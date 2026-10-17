"""The tvapp gate runs unit tests, lint and assemble in one Gradle daemon.

With no tv-app/gradle.properties the daemon used Gradle's 384 MiB metaspace
default; a clean gate run peaks at roughly 260-288 MiB, so on a loaded
machine it intermittently died with OutOfMemoryError: Metaspace in
:app:testDebugUnitTest and :app:lintAnalyzeDebug after every test passed.
Pin the daemon memory so the configuration cannot silently regress.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROPERTIES = REPO / 'tv-app' / 'gradle.properties'
MIN_METASPACE_MIB = 512
MIN_HEAP_MIB = 1024

_SUFFIX_MIB = {'k': 1 / 1024, 'm': 1.0, 'g': 1024.0, 't': 1024.0 ** 2}
_ESCAPES = {'t': '\t', 'n': '\n', 'r': '\r', 'f': '\f'}


def _to_mib(value, suffix):
    if suffix:
        return float(value) * _SUFFIX_MIB[suffix.lower()]
    return float(value) / (1024 * 1024)


def _unescape(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == '\\' and i + 1 < len(text):
            n = text[i + 1]
            if n == 'u' and re.fullmatch(r'[0-9a-fA-F]{4}', text[i + 2:i + 6]):
                out.append(chr(int(text[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append(_ESCAPES.get(n, n))
            i += 2
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def _load_properties(text):
    """Parse text the way java.util.Properties.load does; the last key wins."""
    props, lines, i = {}, text.splitlines(), 0
    while i < len(lines):
        line = lines[i].lstrip(' \t\f')
        i += 1
        if not line or line[0] in '#!':
            continue
        # An odd run of trailing backslashes continues the logical line.
        while (len(line) - len(line.rstrip('\\'))) % 2 == 1:
            line = line[:-1]
            if i >= len(lines):
                break
            line += lines[i].lstrip(' \t\f')
            i += 1
        k = 0
        while k < len(line) and line[k] not in '=: \t\f':
            k += 2 if line[k] == '\\' else 1
        key, rest = line[:k], line[k:].lstrip(' \t\f')
        if rest[:1] in ('=', ':'):
            rest = rest[1:].lstrip(' \t\f')
        props[_unescape(key)] = _unescape(rest)
    return props


def _require(ok, message):
    if not ok:
        raise AssertionError(message)


def _last_size_mib(jvmargs, flag_pattern, name):
    values = re.findall(r'(?:^|\s)(?:' + flag_pattern + r')(\S*)', jvmargs)
    _require(values, f'org.gradle.jvmargs sets no {name}: {jvmargs}')
    # HotSpot applies the last occurrence of a repeated flag.
    size = re.fullmatch(r'([0-9]+)([kKmMgGtT]?)', values[-1])
    _require(size, f'{name} value {values[-1]!r} is not a JVM size')
    return _to_mib(*size.groups())


def _validate(text):
    """Return the effective (metaspace, heap) MiB, asserting both floors."""
    jvmargs = _load_properties(text).get('org.gradle.jvmargs')
    _require(jvmargs is not None,
             'org.gradle.jvmargs is not set in tv-app/gradle.properties')
    meta = _last_size_mib(jvmargs, r'-XX:MaxMetaspaceSize=',
                          '-XX:MaxMetaspaceSize')
    _require(meta >= MIN_METASPACE_MIB,
             f'MaxMetaspaceSize is {meta:g} MiB, below the '
             f'{MIN_METASPACE_MIB} MiB floor (measured clean-gate peak is '
             'roughly 260-288 MiB)')
    heap = _last_size_mib(jvmargs, r'-Xmx|-XX:MaxHeapSize=', '-Xmx')
    _require(heap >= MIN_HEAP_MIB,
             f'max heap is {heap:g} MiB, below the {MIN_HEAP_MIB} MiB floor')
    return meta, heap


class TvappGradleMemory(unittest.TestCase):
    def test_gradle_properties_pins_metaspace_at_or_above_floor(self):
        self.assertTrue(PROPERTIES.is_file(),
                        'tv-app/gradle.properties is missing; the Gradle '
                        'daemon falls back to the 384 MiB metaspace default')
        _validate(PROPERTIES.read_text(encoding='utf-8'))

    def test_mistyped_key_fails(self):
        for text in (
            'org.gradle.jvmargsX=-Xmx2g -XX:MaxMetaspaceSize=1g\n',
            'org.gradle.jvmargs.extra=-Xmx2g -XX:MaxMetaspaceSize=1g\n',
        ):
            with self.assertRaises(AssertionError):
                _validate(text)

    def test_last_metaspace_flag_is_the_effective_one(self):
        with self.assertRaises(AssertionError):
            _validate('org.gradle.jvmargs=-Xmx2g '
                      '-XX:MaxMetaspaceSize=1g -XX:MaxMetaspaceSize=256m\n')
        meta, _heap = _validate(
            'org.gradle.jvmargs=-Xmx2g '
            '-XX:MaxMetaspaceSize=256m -XX:MaxMetaspaceSize=1g\n')
        self.assertGreaterEqual(meta, MIN_METASPACE_MIB)

    def test_heap_below_floor_fails(self):
        with self.assertRaises(AssertionError):
            _validate('org.gradle.jvmargs=-Xmx256m '
                      '-XX:MaxMetaspaceSize=1g\n')
        with self.assertRaises(AssertionError):
            _validate('org.gradle.jvmargs=-Xmx2g -Xmx256m '
                      '-XX:MaxMetaspaceSize=1g\n')

    def test_valid_properties_syntax_is_accepted(self):
        for text in (
            'org.gradle.jvmargs:-Xmx2g -XX:MaxMetaspaceSize=1g\n',
            'org.gradle.jvmargs -Xmx2g -XX:MaxMetaspaceSize=1g\n',
            'org.gradle.jvmargs = -Xmx2g -XX:MaxMetaspaceSize=1g\n',
            '# comment\n! comment\n'
            'org.gradle.jvmargs=-Xmx2g \\\n  -XX:MaxMetaspaceSize=1g\n',
            '#org.gradle.jvmargs=-Xmx256m -XX:MaxMetaspaceSize=256m\n'
            'org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=1g\n',
        ):
            meta, heap = _validate(text)
            self.assertGreaterEqual(meta, MIN_METASPACE_MIB)
            self.assertGreaterEqual(heap, MIN_HEAP_MIB)


if __name__ == '__main__':
    unittest.main()
