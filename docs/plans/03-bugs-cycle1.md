# 03 — Bugs (Cycle 1)

Tester report after first Playwright run.

## Summary
- Passes: 11 / 15
- Fails: 4 / 15

## Failures

### B1 (test infra) — `window.speechSynthesis` stub not applied
`window.speechSynthesis` is a read-only WebIDL property on Window in Chromium. Direct assignment via `add_init_script` silently fails in strict-mode page contexts, so all 4 utterance-counting tests time out.

**Affected tests**:
- hero input → speak utterance
- card Play button speaks
- speed slider affects utterance rate
- Space on focused card speaks

**This is a test problem, not a product bug** (app code is fine — it correctly calls `window.speechSynthesis.speak(...)`).

**Fix**: use `Object.defineProperty` to redefine the property as configurable in the init script.
