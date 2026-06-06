# 04 — Fixes (Cycle 1 → Cycle 2)

## B1 fix: speechSynthesis stub via `Object.defineProperty`
`window.speechSynthesis` is a read-only WebIDL property. Setting `window.speechSynthesis = stub` silently no-ops, so `add_init_script` didn't actually swap in the test double. Replaced both `speechSynthesis` and `SpeechSynthesisUtterance` assignments with `Object.defineProperty(..., { configurable: true, writable: true })`.

Test infrastructure only — no product code change.

## Cycle 2 result
- 15 / 15 pass
- 0 console errors
- 0 page errors
- No P0 / P1 bugs

Termination condition met. Proceeding to deployment.

## Note on `with_server.py`
The helper script reported "Server ready on port 5180" but Playwright's `page.goto` immediately got `ERR_EMPTY_RESPONSE`. A standalone `python3 -m http.server` followed by a `curl` request on the same port returned 200. Switching to a manually backgrounded static server unblocked the loop. Filed under environment-noise; not a product issue.
