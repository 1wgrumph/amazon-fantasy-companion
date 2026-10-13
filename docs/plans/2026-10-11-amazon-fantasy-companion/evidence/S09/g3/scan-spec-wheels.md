verdict: PASS
Date: 2026-10-12T06:57:40.636150+00:00
Origin: https://pypi.org
Intended use: S06 vendoring and offline verification, after this receipt.
CREDENTIAL FINDINGS: none; gitleaks redacted scans exit 0.
pytest 9.0.3, PyYAML 6.0.3, iniconfig 2.3.1, packaging 26.3, pluggy 1.6.0, pygments 2.21.0; all wheel SHA256 values matched official PyPI JSON, no reported vulnerabilities. Archive paths checked before extraction. Native PyYAML readelf imports libc and libpthread; no RPATH. Wheels have no build/install hooks.
ClamAV 1.5.4, database 28150 (2026-10-11): 568 files, zero infected, exit 0.
No dynamic analysis performed. Residual risk: scanners cannot prove absence of unknown defects.
SHA256:
9121e2c1fdb355232495be3194c8dfe87ccc2d5dee45947b78e68f499790d7a7  iniconfig-2.3.1-py3-none-any.whl
d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c  packaging-26.3-py3-none-any.whl
e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746  pluggy-1.6.0-py3-none-any.whl
2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9  pygments-2.21.0-py3-none-any.whl
2c5efc453d45394fdd706ade797c0a81091eccd1d6e4bccfcd476e2b8e0ab5d9  pytest-9.0.3-py3-none-any.whl
c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5  pyyaml-6.0.3-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl

Reused after SHA256 verification 2026-10-12T11:48:39.999869+00:00 before g3 use. Intended command: uv run --script tools/spec/*.py; UV_OFFLINE=1 UV_NO_CACHE=1 UV_FIND_LINKS points at this wheel directory, UV_PYTHON=host python3.
