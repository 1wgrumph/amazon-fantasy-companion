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

    def test_r3_rejects_malformed_scoring_modifiers_and_allows_zero(self):
        zero_raw = {"stat_modifiers": {"stats": [
            {"stat": {"stat_id": "4", "value": "0"}},
            {"stat": {"stat_id": 5, "value": 0}},
        ]}}
        self.assertEqual(
            y.normalize_settings(zero_raw, "461.l.123")["stat_modifiers"],
            {"4": 0.0, "5": 0.0},
        )
        for bad_stat in (
            {"stat_id": "4", "value": "invalid"},
            {"stat_id": "4", "value": None},
            {"stat_id": "4"},
            {"stat_id": "4", "value": "nan"},
            {"stat_id": "4", "value": "inf"},
            {"stat_id": "4", "value": "-inf"},
            {"stat_id": "4", "value": True},
        ):
            raw = {"stat_modifiers": {"stats": [{"stat": bad_stat}]}}
            with self.subTest(bad_stat=bad_stat):
                with self.assertRaises(ValueError):
                    y.normalize_settings(raw, "461.l.123")
                with self.assertRaises(ValueError):
                    y.YahooTransport._normalize("https://example/league/461.l.123/settings", raw)


class CallbackStateBindingTests(unittest.TestCase):
    @staticmethod
    def _run_capture_with_paths(paths_fn):
        import contextlib
        import io
        from unittest.mock import MagicMock, patch

        out = io.StringIO()
        err = io.StringIO()
        statuses = []
        bound_addresses = []

        class FakeServer:
            def __init__(self, address, handler):
                bound_addresses.append(address)
                self.handler = handler
                self.socket = object()
                self._paths = None

            def handle_request(self):
                if self._paths is None:
                    self._paths = list(paths_fn(out.getvalue()))
                if not self._paths:
                    raise RuntimeError("capture loop did not terminate on expected callback")
                path = self._paths.pop(0)
                request = object.__new__(self.handler)
                request.path = path
                request.send_response = statuses.append
                request.send_header = lambda *_: None
                request.end_headers = lambda: None
                request.wfile = io.BytesIO()
                request.do_GET()

            def server_close(self):
                pass

        with patch("tempfile.TemporaryDirectory") as td, \
             patch("subprocess.run"), \
             patch("ssl.SSLContext", return_value=MagicMock()), \
             patch("http.server.HTTPServer", FakeServer), \
             patch.object(y, "ssm_get", return_value="public-client-id"), \
             patch.object(y, "_exchange_and_store", return_value=0) as exchange, \
             contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            td.return_value.__enter__.return_value = "/unused"
            rc = y.cmd_capture()
        return rc, exchange, out.getvalue(), statuses, bound_addresses

    @staticmethod
    def _extract_state(stdout_text):
        for line in stdout_text.splitlines():
            if line.startswith("https://"):
                query = urllib.parse.parse_qs(urllib.parse.urlparse(line).query)
                return (query.get("state") or [""])[0]
        return ""

    def test_r1_rejects_unbound_callbacks(self):
        def make_paths(stdout_text):
            state = self._extract_state(stdout_text)
            return [
                "/link?code=foreign-code&state=wrong-state",
                "/link?code=missing-state-code",
                f"/wrong-path?code=wrong-path-code&state={state}",
                f"/link?error=access_denied&state={state}",
            ]

        rc, exchange, _, statuses, _ = self._run_capture_with_paths(make_paths)
        self.assertEqual(exchange.call_count, 0)
        self.assertEqual(rc, 2)
        self.assertEqual(statuses, [400, 400, 400, 200])

    def test_r1_accepts_matching_state_after_rejecting_invalid_callbacks(self):
        seen_states = []

        def make_paths(stdout_text):
            state = self._extract_state(stdout_text)
            seen_states.append(state)
            return [
                "/link?code=foreign-code&state=wrong-state",
                f"/other?code=foreign-code&state={state}",
                f"/link?code=valid-code&state={state}",
            ]

        rc1, exchange1, _, statuses1, addrs1 = self._run_capture_with_paths(make_paths)
        rc2, exchange2, _, _, _ = self._run_capture_with_paths(make_paths)
        self.assertTrue(seen_states[0])
        self.assertNotEqual(seen_states[0], seen_states[1])
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 0)
        self.assertEqual(statuses1, [400, 400, 200])
        self.assertEqual(addrs1, [("localhost", y.CAPTURE_PORT)])
        exchange1.assert_called_once_with("valid-code", y.CAPTURE_REDIRECT_URI)
        exchange2.assert_called_once_with("valid-code", y.CAPTURE_REDIRECT_URI)


class RefreshTokenRotationTests(unittest.TestCase):
    def test_r2_preserves_rotated_refresh_token_and_carries_forward(self):
        import contextlib
        import io
        import tempfile
        from unittest.mock import patch

        with patch.object(y, "_token_post", return_value=(200, {
            "access_token": "access-1", "refresh_token": "new-refresh"
        })), patch.object(y, "ssm_put_token") as store:
            y._access_token("client", "secret", "old-refresh")
            store.assert_called_once_with("new-refresh")

        # Rotation followed by Fantasy API 403 still saves the rotated refresh token.
        with patch.object(y, "ssm_get", side_effect=["cid", "csec", "old-refresh"]), \
             patch.object(y, "_token_post", return_value=(200, {
                 "access_token": "access-1", "refresh_token": "rotated-before-403"
             })), \
             patch.object(y, "ssm_put_token") as store_403, \
             patch.object(y, "_read_once", side_effect=y.HttpError(403, "Yahoo Fantasy API")):
            with self.assertRaises(y.HttpError):
                y.cmd_read()
            store_403.assert_called_once_with("rotated-before-403")

        # Rotation followed by 401 retry uses the rotated refresh token in memory
        # and preserves it when the second refresh supplies no replacement.
        token_calls = []

        def fake_token_post(client_id, client_secret, fields, what):
            token_calls.append(dict(fields))
            if len(token_calls) == 1:
                return 200, {"access_token": "access-1", "refresh_token": "rotated-refresh"}
            return 200, {"access_token": "access-2"}

        read_calls = []

        def fake_read_once(access):
            read_calls.append(access)
            if len(read_calls) == 1:
                raise y.HttpError(401, "Yahoo Fantasy API")
            return None, {
                "http_statuses": [200],
                "week": 7,
                "starter_count": 1,
                "bench_count": 1,
            }

        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = f"{tmp}/read-result.json"
            with patch.object(y, "EVIDENCE_PATH", evidence_path), \
                 patch.object(y, "ssm_get", side_effect=["cid", "csec", "initial-refresh"]), \
                 patch.object(y, "_token_post", side_effect=fake_token_post), \
                 patch.object(y, "ssm_put_token") as store_retry, \
                 patch.object(y, "_read_once", side_effect=fake_read_once), \
                 contextlib.redirect_stdout(io.StringIO()):
                rc = y.cmd_read()
        self.assertEqual(rc, 0)
        self.assertEqual([c["refresh_token"] for c in token_calls],
                         ["initial-refresh", "rotated-refresh"])
        store_retry.assert_called_once_with("rotated-refresh")

        # Invalid replacement refresh_token is rejected.
        with patch.object(y, "_token_post", return_value=(200, {
            "access_token": "access-1", "refresh_token": ""
        })), patch.object(y, "ssm_put_token") as store_bad:
            with self.assertRaises(ValueError):
                y._access_token("client", "secret", "old-refresh")
            store_bad.assert_not_called()


if __name__ == "__main__":
    unittest.main()
