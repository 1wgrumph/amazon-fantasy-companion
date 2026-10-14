"""DES-AFC-P2-PANELSVC PanelState per profile and team/league.

AFC-STUB module: P2-B07 replaces each body; the signatures are final.
"""


def _pending():
    return "AFC-STUB: panel is implemented by P2-B07"


def project(game_event, matches):
    """AFC-STUB (P2-B07): Recompute and store PanelState for each matched profile's team/league."""
    raise NotImplementedError(_pending())


def snapshot(profile_id, team_league):
    """AFC-STUB (P2-B07): GET /v1/panel body: enveloped PanelState with scoring basis."""
    raise NotImplementedError(_pending())
