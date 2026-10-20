---
type: evidence
title: P2-L02 2026-10-18 recovery deploy projection
okf_status: draft
tags: [afc, p2-l02, evidence]
---

# Projection of P2-L02 recovery-2026-10-18 evidence (#29)

Observer: Light Implementer (Claude Code / Claude Sonnet 5.5 / medium), 2026-10-19. Not an independent review.

## Rules applied (only these)

1. the recovery worktree root path (absolute, with trailing slash) -> `<repo>/`
2. the user-local `afc-tools` install root path (absolute, with trailing slash) -> `<tools>/`
3. any other absolute user-home prefix -> `<home>/` (0 occurrences)
4. raw 12-digit AWS account ID -> `<acct>` (0 occurrences; existing `<ACCT>` placeholders kept)
5. strip trailing spaces and tabs at end of line, and reduce trailing blank lines at end of file to a single newline, as the hygiene gate requires (existing practice: main commit cce9489; landed P2-L02 evidence has none). Nothing else.

API Gateway hostname, region, stack, resource, change-set and SSM names are unchanged. No other bytes changed.

Rule 5 counts: `deploy-stage-output.txt` 27 lines (lines 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60); plus 1 extra blank line removed at EOF in the same file (source ended `\n\n`); every other file 0.

## Files

| File | Source sha256 | Projected sha256 | `<repo>/` | `<tools>/` | `<home>/` | `<acct>` | rule 5 lines |
|---|---|---|---|---|---|---|---|
| `change-set-describe.json` | `4681f76527d2c02c963023f6c01bb2c0413e83c0cc1ee347e194299eff10eeca` | `4681f76527d2c02c963023f6c01bb2c0413e83c0cc1ee347e194299eff10eeca` | 0 | 0 | 0 | 0 | 0 |
| `deploy-execute-output.txt` | `294b535d4b6686d2740a344a059be894346d1c8bf9bcb82b459221c932efb595` | `294b535d4b6686d2740a344a059be894346d1c8bf9bcb82b459221c932efb595` | 0 | 0 | 0 | 0 | 0 |
| `deploy-execution-receipt.json` | `ba9ae1974c56518afa344d55a97764f32329dda097838fcc2ca5be5d0e99b6e8` | `ba9ae1974c56518afa344d55a97764f32329dda097838fcc2ca5be5d0e99b6e8` | 0 | 0 | 0 | 0 | 0 |
| `deploy-stage-output.txt` | `1b31290cd0e4841c9756bc819668fe37102635af7ef31e4ee33482198269807c` | `804345d93967c20de1ef96c56d870726d607baf8abb80a5c7b96180698ad18b0` | 0 | 0 | 0 | 0 | 27 |
| `deploy-stage-receipt.json` | `32e47536529e8f9575c23b87897da1eeb79b2def1602ea73935bc8cb4d1e2031` | `32e47536529e8f9575c23b87897da1eeb79b2def1602ea73935bc8cb4d1e2031` | 0 | 0 | 0 | 0 | 0 |
| `deploy.last_green.json` | `ceb47f3d486f822f2195c7946f5a54391e1f8ef008ae9b68fcd8944d1675ba83` | `ceb47f3d486f822f2195c7946f5a54391e1f8ef008ae9b68fcd8944d1675ba83` | 0 | 0 | 0 | 0 | 0 |
| `deployed-output.txt` | `e60d8c83302c7f142a19c82fa1a9d7ca4e895fd13adf37fe647d01c4f539ff3d` | `afe18c0987e2703104304d3142786528894f523e224f07827b057eb31a9216a9` | 2 | 1 | 0 | 0 | 0 |
| `deployed-smoke-output.txt` | `92dcccb70e4a4676707ace3ac7d19b8d98fc10441bc7d8f3efc8d951084f4302` | `40329692ad78737956dcacba8a70bb6e6c95a97135ec26b618a810edc90d07d3` | 2 | 1 | 0 | 0 | 0 |
| `deployed-smoke.xml` | `5eeada08a3ab4272b8e1de1061e7c7ea3bc8edda8311f1d7e2bfac523d6b3244` | `5eeada08a3ab4272b8e1de1061e7c7ea3bc8edda8311f1d7e2bfac523d6b3244` | 0 | 0 | 0 | 0 | 0 |
| `deployed.xml` | `cee9f523c386be4b86c6becb151ed48704114577887604abcaf7126d48fb0a4b` | `cee9f523c386be4b86c6becb151ed48704114577887604abcaf7126d48fb0a4b` | 0 | 0 | 0 | 0 | 0 |

## Leak check

Command, run in the projected directory over the 10 projected files (excluding this file, whose pattern text matches itself):

```
grep -nE '/home/|AKIA[0-9A-Z]{16}|aws_secret|refresh_token|Bearer [A-Za-z0-9]|(^|[^0-9a-f])[0-9]{12}([^0-9a-f]|$)' <10 projected files>
```

Output: no hits (no lines to justify).

Parse checks: `python3 -m json.tool` passed on all 4 `.json` files; `xml.dom.minidom.parse` passed on both `.xml` files.
