"""Conservative source-only DynamoDB inventory; never import application code.

Analyze every entry-module function (including API dispatch callbacks), then
follow local imports, calls, arguments, returns and assignment aliases. Branches
are unioned; dynamic table names and unsupported table receivers fail closed.
"""

import ast

from botocore import xform_name
from botocore.loaders import Loader

UNKNOWN = frozenset({("unknown",)})
OPERATIONS = {xform_name(name): name for name in
              Loader().load_service_model("dynamodb", "service-2")["operations"]}


def required_actions(root, handler, environment):
    modules = {}
    for path in root.rglob("*.py"):
        parts = path.relative_to(root).with_suffix("").parts
        name = ".".join(parts[:-1] if parts[-1] == "__init__" else parts)
        modules[name] = ast.parse(path.read_text(), filename=str(path))
    required, cache, active, loaded = {}, {}, set(), set()

    def one(*value):
        return frozenset({value})

    def union(values):
        return frozenset().union(*values) if values else UNKNOWN

    def bindings(body):
        result = {}
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                result[node.name] = [node]
                continue
            for item in ast.walk(node):
                if isinstance(item, ast.Import):
                    for alias in item.names:
                        name = alias.name if alias.asname else alias.name.split(".")[0]
                        result[alias.asname or name] = [("module", name)]
                elif isinstance(item, ast.ImportFrom):
                    assert not item.level, "Relative imports need explicit IAM resolution"
                    for alias in item.names:
                        result[alias.asname or alias.name] = [("import", item.module, alias.name)]
                elif isinstance(item, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and item.value is not None:
                            result.setdefault(target.id, []).append(item.value)
                elif isinstance(item, ast.withitem) and isinstance(item.optional_vars, ast.Name):
                    result.setdefault(item.optional_vars.id, []).append(item.context_expr)
        return result

    globals_ = {name: bindings(tree.body) for name, tree in modules.items()}

    def symbol(module, name, scope, resolving):
        key = (module, name)
        assert key not in resolving, f"Cyclic IAM binding: {key}"
        if name in scope:
            return scope[name]
        values = []
        for value in globals_[module].get(name, []):
            if isinstance(value, tuple):
                if value[0] == "module":
                    values.append(one(*value))
                else:
                    values.append(member(value[1], value[2], resolving | {key}))
            elif isinstance(value, (ast.FunctionDef, ast.AsyncFunctionDef)):
                values.append(one("function", module, name))
            elif not isinstance(value, ast.ClassDef):
                values.append(evaluate(value, module, {}, resolving | {key}))
        return union(values)

    def load(module):
        if module not in modules or module in loaded:
            return
        loaded.add(module)
        for node in modules[module].body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    load(alias.name)
            elif isinstance(node, ast.ImportFrom):
                load(node.module)
                for alias in node.names:
                    load(node.module + "." + alias.name)
            elif not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for call in ast.walk(node):
                    if isinstance(call, ast.Call):
                        evaluate(call, module, {}, set())

    def member(module, name, resolving):
        load(module)
        if module in modules and name in globals_[module]:
            return symbol(module, name, {}, resolving)
        if module + "." + name in modules:
            return one("module", module + "." + name)
        return UNKNOWN

    def invoke(module, name, arguments, keywords):
        key = (module, name, tuple(arguments), tuple(sorted(keywords.items())))
        if key in cache:
            return cache[key]
        assert key not in active, f"Recursive IAM call needs explicit resolution: {module}.{name}"
        active.add(key)
        [function] = globals_[module][name]
        parameters = function.args.posonlyargs + function.args.args
        scope = {p.arg: UNKNOWN for p in parameters + function.args.kwonlyargs}
        for p, value in zip(parameters, arguments):
            scope[p.arg] = value
        scope.update(keywords)
        defaults = dict(zip([p.arg for p in parameters][-len(function.args.defaults):],
                            function.args.defaults)) if function.args.defaults else {}
        for parameter, value in defaults.items():
            if parameter not in keywords and parameter not in [p.arg for p in parameters[:len(arguments)]]:
                scope[parameter] = evaluate(value, module, {}, set())
        local = bindings(function.body)
        resolving_local = set()

        def local_symbol(identifier):
            if identifier in resolving_local:
                return scope.get(identifier, UNKNOWN)
            if identifier in local:
                resolving_local.add(identifier)
                value = union([evaluate(n, module, scope, set(), local_symbol)
                               for n in local[identifier]])
                resolving_local.remove(identifier)
                return value
            return symbol(module, identifier, scope, set())

        returns = []
        for node in ast.walk(function):
            if isinstance(node, ast.Call):
                evaluate(node, module, scope, set(), local_symbol)
            elif isinstance(node, ast.Attribute) and node.attr in OPERATIONS:
                evaluate(node, module, scope, set(), local_symbol)
            elif isinstance(node, ast.Return) and node.value:
                returns.append(evaluate(node.value, module, scope, set(), local_symbol))
        result = union(returns)
        active.remove(key)
        cache[key] = result
        return result

    def evaluate(node, module, scope, resolving, lookup=None):
        if isinstance(node, tuple):
            return one(*node) if node[0] == "module" else member(node[1], node[2], resolving)
        assert not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)), \
            "Nested IAM helper needs explicit resolution"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return one("string", node.value)
        if isinstance(node, ast.Name):
            return lookup(node.id) if lookup else symbol(module, node.id, scope, resolving)
        if isinstance(node, ast.Attribute):
            receivers = evaluate(node.value, module, scope, resolving, lookup)
            if node.attr in OPERATIONS:
                assert all(r[0] in {"table", "batch"} for r in receivers), \
                    f"Unknown DynamoDB table resolution: {module}: {ast.unparse(node)}"
            values = []
            for receiver in receivers:
                if receiver[0] == "module":
                    values.append(member(receiver[1], node.attr, resolving))
                elif receiver[0] in {"table", "batch"}:
                    assert node.attr in OPERATIONS or node.attr == "batch_writer", \
                        f"Unknown DynamoDB table method: {node.attr}"
                    if node.attr in OPERATIONS:
                        action = "BatchWriteItem" if receiver[0] == "batch" else OPERATIONS[node.attr]
                        required.setdefault(receiver[1], set()).add(action)
                    values.append(one("method", receiver[1], node.attr, receiver[0]))
            return union(values)
        if isinstance(node, ast.Call):
            arguments = [evaluate(n, module, scope, resolving, lookup) for n in node.args]
            keywords = {n.arg: evaluate(n.value, module, scope, resolving, lookup)
                        for n in node.keywords if n.arg}
            if isinstance(node.func, ast.Attribute) and node.func.attr == "Table":
                assert arguments, "Unknown DynamoDB table resolution: no Table argument"
                tables = set()
                for value in arguments[0]:
                    assert value[0] == "environment" and value[1] in environment, \
                        f"Unknown DynamoDB table resolution: {ast.unparse(node)}"
                    ref = environment[value[1]]
                    assert set(ref) == {"Ref"}, f"Unknown DynamoDB table reference: {ref}"
                    tables.add(("table", ref["Ref"]))
                return frozenset(tables)
            callees = evaluate(node.func, module, scope, resolving, lookup)
            if (isinstance(node.func, ast.Attribute) and node.func.attr in OPERATIONS):
                assert all(c[0] == "method" for c in callees), \
                    f"Unknown DynamoDB table resolution: {module}: {ast.unparse(node)}"
            # External higher-order calls may invoke supplied local callbacks.
            if ("unknown",) in callees:
                for value in arguments + list(keywords.values()):
                    for callback in value:
                        if callback[0] == "function":
                            invoke(callback[1], callback[2], [], {})
            values = []
            for callee in callees:
                if callee[0] == "function":
                    values.append(invoke(callee[1], callee[2], arguments, keywords))
                elif callee[0] == "method":
                    _, table, method, kind = callee
                    if method == "batch_writer":
                        values.append(one("batch", table))
            return union(values)
        if isinstance(node, ast.Subscript) and ast.unparse(node.value) == "os.environ":
            return union([one("environment", v[1]) if v[0] == "string" else UNKNOWN
                          for v in evaluate(node.slice, module, scope, resolving, lookup)])
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return union([evaluate(n, module, scope, resolving, lookup) for n in node.elts])
        if isinstance(node, ast.Dict):
            return union([evaluate(n, module, scope, resolving, lookup) for n in node.values])
        # shortcut: reflection and computed dispatch are outside this static
        # inventory; extend resolution before introducing them for persistence.
        if isinstance(node, ast.IfExp):
            return union([evaluate(n, module, scope, resolving, lookup)
                          for n in (node.body, node.orelse)])
        return UNKNOWN

    entry, _ = handler.rsplit(".", 1)
    assert entry in modules, f"Unknown handler module: {entry}"
    load(entry)
    for node in modules[entry].body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            invoke(entry, node.name, [], {})
    return required
