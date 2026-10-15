"""Which games to monitor, each decision with its basis label (AFC-PR-008, AFC-PR-011)."""


def _bases():
    return ("observed-playback", "profile-assumption")


def monitored_decisions(games, selected_player_ids, favorite_team_ids, enabled, basis):
    """One {gameId, monitored, basis} per game, in input order.

    A game is monitored only in an enabled period and only when it holds a selected
    player or a favorite team.
    """
    if basis not in _bases():
        raise ValueError(f"Monitoring basis must be one of {_bases()}, not {basis!r}")
    players, teams = set(selected_player_ids), set(favorite_team_ids)
    return [{"gameId": game["gameId"], "basis": basis,
             "monitored": bool(enabled) and bool(players & set(game["playerIds"])
                                                 or teams & set(game["teamIds"]))}
            for game in games]
