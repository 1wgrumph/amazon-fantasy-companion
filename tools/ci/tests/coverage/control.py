"""Native Python coverage corpus; both returns must appear in Cobertura XML."""


def verdict(ok):
    if ok:
        return 'covered'
    return 'uncovered'
