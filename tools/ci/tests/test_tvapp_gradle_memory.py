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

_SUFFIX_MIB = {'k': 1 / 1024, 'm': 1.0, 'g': 1024.0}


def _to_mib(value, suffix):
    if suffix:
        return float(value) * _SUFFIX_MIB[suffix.lower()]
    return float(value) / (1024 * 1024)


class TvappGradleMemory(unittest.TestCase):
    def test_gradle_properties_pins_metaspace_at_or_above_floor(self):
        self.assertTrue(PROPERTIES.is_file(),
                        'tv-app/gradle.properties is missing; the Gradle '
                        'daemon falls back to the 384 MiB metaspace default')
        jvmargs = None
        for line in PROPERTIES.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line.startswith('org.gradle.jvmargs'):
                jvmargs = line.partition('=')[2]
        self.assertIsNotNone(jvmargs,
                             'org.gradle.jvmargs is not set in '
                             'tv-app/gradle.properties')
        match = re.search(r'-XX:MaxMetaspaceSize=([0-9]+)([kKmMgG]?)', jvmargs)
        self.assertIsNotNone(match,
                             'org.gradle.jvmargs sets no -XX:MaxMetaspaceSize: '
                             + jvmargs)
        mib = _to_mib(match.group(1), match.group(2))
        self.assertGreaterEqual(
            mib, MIN_METASPACE_MIB,
            f'MaxMetaspaceSize is {mib:g} MiB, below the {MIN_METASPACE_MIB} '
            'MiB floor (measured clean-gate peak is roughly 260-288 MiB)')


if __name__ == '__main__':
    unittest.main()
