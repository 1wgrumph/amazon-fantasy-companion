"""No-network unit tests for yahoo_oauth URL building, redaction, normalization."""
import unittest
import urllib.parse

import yahoo_oauth as y


class UrlTests(unittest.TestCase):
    def test_auth_url(self):
        parsed = urllib.parse.urlparse(y.build_auth_url("cid123"))
        self.assertEqual(parsed.netloc, "api.login.yahoo.com")
        self.assertEqual(parsed.path, "/oauth2/request_auth")
        query = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(query["client_id"], ["cid123"])
        self.assertEqual(query["redirect_uri"], ["https://localhost/link"])
        self.assertEqual(query["response_type"], ["code"])
        self.assertEqual(query["scope"], ["fspt-r"])

    def test_extract_code_from_url_and_bare(self):
        self.assertEqual(y.extract_code("https://localhost/link?code=abc-1"), "abc-1")
        self.assertEqual(y.extract_code(" bare "), "bare")


class RedactTests(unittest.TestCase):
    def test_redact_drops_secret_shaped_keys(self):
        dirty = {"access_token": "x", "client_secret": "y", "code": "z",
                 "Authorization": "Bearer q", "email": "a@b", "keep": 1,
                 "nested": [{"refresh_token": "t", "count": 2}]}
        self.assertEqual(y.redact(dirty), {"keep": 1, "nested": [{"count": 2}]})


RAW_LEAGUES = {"fantasy_content": {"users": {"0": {"user": [
    {"guid": "G"},
    {"games": {"0": {"game": [{"game_key": "461"}, {"leagues": {"0": {"league": [
        {"league_key": "461.l.123", "name": "L", "season": "2026",
         "current_week": "7"}]}}}]}}}]}}}}

RAW_TEAMS = {"fantasy_content": {"league": [{}, {"teams": {"0": {"team": [
    [{"team_key": "461.l.123.t.1"}, {"name": "Mine"},
     {"is_owned_by_current_login": 1}], {}]}}}]}}

RAW_ROSTER = {"fantasy_content": {"team": [{}, {"roster": {"0": {"players": {
    "0": {"player": [
        [{"player_key": "461.p.1"}, {"name": {"full": "Player One"}},
         {"editorial_team_abbr": "KC"},
         {"eligible_positions": [{"position": "QB"}]}],
        {"selected_position": [{"position": "QB"}]}]},
    "1": {"player": [
        [{"player_key": "461.p.2"}, {"name": {"full": "Player Two"}},
         {"editorial_team_abbr": "BUF"},
         {"eligible_positions": [{"position": "RB"}]}],
        {"selected_position": [{"position": "BN"}]}]}}}}}]}}

RAW_SETTINGS = {"fantasy_content": {"league": [{}, {"settings": [{
    "stat_modifiers": {"stats": [{"stat": {"stat_id": 4, "value": "0.04"}}]},
    "roster_positions": [{"roster_position": {"position": "QB", "count": 1}},
                         {"roster_position": {"position": "BN", "count": "6"}}],
}]}]}}


class NormalizeTests(unittest.TestCase):
    def test_leagues_and_week(self):
        self.assertEqual(y.normalize_leagues(RAW_LEAGUES),
                         {"leagues": [{"league_key": "461.l.123", "name": "L",
                                       "season": 2026}]})
        self.assertEqual(y.current_week_from(RAW_LEAGUES), 7)

    def test_teams_and_owned(self):
        self.assertEqual(y.normalize_teams(RAW_TEAMS),
                         {"teams": [{"team_key": "461.l.123.t.1", "name": "Mine"}]})
        self.assertEqual(y.owned_team_key(RAW_TEAMS), "461.l.123.t.1")

    def test_roster(self):
        roster = y.normalize_roster(RAW_ROSTER, "461.l.123.t.1", 7)
        self.assertEqual([p["slot"] for p in roster["players"]], ["QB", "BN"])
        self.assertEqual(roster["players"][0]["positions"], ["QB"])
        self.assertEqual(roster["players"][0]["team"], "KC")

    def test_settings(self):
        settings = y.normalize_settings(RAW_SETTINGS, "461.l.123")
        self.assertEqual(settings["stat_modifiers"], {"4": 0.04})
        self.assertEqual(settings["roster_slots"], ["QB"] + ["BN"] * 6)

    def test_fallback_week_bounds(self):
        from datetime import date
        self.assertEqual(y.fallback_week(date(2026, 9, 7)), 1)
        self.assertTrue(1 <= y.fallback_week(date(2027, 3, 1)) <= 18)


if __name__ == "__main__":
    unittest.main()
