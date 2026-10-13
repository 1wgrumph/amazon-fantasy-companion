verdict: PASS
CREDENTIAL FINDINGS: none; gitleaks redacted scan exit 0.
Date: 2026-10-12T11:57:30.962472+00:00
Artifact: /tmp/afc-s09-g3-metrics-wheels-4onmfgui; inert wheels and mutmut/glob2 source archives; intended use: CMD-COVERAGE-CI: uv run --no-project --with 'coverage>=7,<8' --with 'diff-cover>=9,<10'.
Origin: official PyPI HTTPS JSON and distribution URLs; downloaded packages were not executed or installed before this receipt. Exact package/version/digest/URL inventory: metrics-inventory.json and mutation-sdist-inventory.json.
Integrity: every SHA256 matched official version JSON, no vulnerabilities listed for these exact versions. Wheel/tar members listed before extraction; no absolute/traversal, links, device or special entries.
Static checks: clamscan --recursive --no-summary --infected on the entire extracted closure, exit 0, no infected files; ClamAV 1.5.4 / DB 28150 dated 2026-10-11. gitleaks dir --redact exit 0, no findings. Native wheel objects readelf -d: libc/libpthread dependencies, no RPATH/RUNPATH.
Source inspection: coverage entrypoint executes the specified local runner and writes local measurement/report files; diff-cover invokes git with argument lists and reads coverage XML. Their dependencies provide local parsing, templates, character decoding and plugin management; no default outbound transport or telemetry. coverage a1_coverage.pth starts measurement only on COVERAGE_PROCESS_START/CONFIG; setuptools distutils-precedence.pth installs the documented local import shim. Neither fetches data.
Mutation/build inspection: mutmut runs only the configured runner (shell=True is necessary for its command string), temporarily edits only declared Python targets, restores them and writes SQLite .mutmut-cache. No custom pre/post hooks configured. Pony SQLite path used, no remote DB bound. mutmut setup.py reads local metadata; tag/release_check commands are declared but not invoked by wheel builds. glob2 setup.py eval is restricted by regex to the shipped literal version tuple (0, 7). setuptools/wheel build hooks inspected as package tooling; no project-specific downloader, persistence or upload. Dynamic analysis unnecessary for admission; mutation verification must check restoration after use.
Unavailable checks/residual risk: no independent signature or attestation; PyPI hashes anchor identity. PyPI-reported advisories are not exhaustive vulnerability analysis; no current local advisory database scan claimed. Static scans cannot prove absence of unknown defects. All use is offline with no cache from the scanned wheel directory; no unscanned cache artifact can satisfy resolution.
SHA256 manifest:
cedbc584789eb2edfde20fd03669972a833ce6019e60014ae613f9bfc440e8e3  chardet-7.6.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
35f37886699cb9abd29958247d718628d5bc6f39e623dff66a09e546c42a7e03  coverage-7.16.2-cp314-cp314-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl
cd6498620c747c2493a6c83c14362c32868bfd91cd8d0dd093f136070ec4ffc5  diff_cover-9.7.2-py3-none-any.whl
85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67  jinja2-3.1.6-py3-none-any.whl
a8e9f292fcda89b324f2f5c91d13f1424a153e40fc2756f38ee23b15835ff300  markupsafe-3.0.4-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl
e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746  pluggy-1.6.0-py3-none-any.whl
2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9  pygments-2.21.0-py3-none-any.whl
255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360  click-8.5.0-py3-none-any.whl
ec5ca1a55aefdd76d28fcc0b135251d156c7106fa979686a4b48d62b761b4732  junit_xml-1.9-py2.py3-none-any.whl
d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c  packaging-26.3-py3-none-any.whl
a8926eb2a1b915486941fdbd31e86a4baf88fe8c210f25f2f35ecec5b574ca1c  parso-0.8.7-py2.py3-none-any.whl
88eb65c940c6efebdc56d2181dc4e5c89650f993f0b27037bbfb3e07b60696ba  pony-0.7.20-py3-none-any.whl
51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670  setuptools-84.0.0-py3-none-any.whl
4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274  six-1.17.0-py2.py3-none-any.whl
806143ae5bfb6a3c6e736a764057db0e6a0e05e338b5630894a5f779cabb4f9b  toml-0.10.2-py2.py3-none-any.whl
3217dcc807155e45db462d7ef2431f5ddda0d7273b700d05a67b271ceb1287ab  wheel-0.48.0-py3-none-any.whl
d8fea2538805277f6290922e88881ad045002fc284d5a53c2b3915298b77f79d  mutmut-2.5.1.tar.gz
85c3dbd07c8aa26d63d7aacee34fa86e9a91a3873bc30bf62ec46e531f92ab8c  glob2-0.7.tar.gz
