"""
Playwright e2e for EnglishBoard.

Headless chromium has no real TTS voices, so we stub speechSynthesis
on every page to capture utterances rather than actually play them.
That lets us verify: input → speak path, card play, favorite toggle,
favorites tab, recent tab, speed slider, print path, accessibility.
"""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

PORT = os.environ.get("TEST_PORT", "5180")
URL = f"http://127.0.0.1:{PORT}/index.html"
OUT = Path(os.environ.get("TEST_OUT", str(Path(__file__).parent / "screenshots")))
OUT.mkdir(parents=True, exist_ok=True)

# Capture every utterance the page tries to speak.
STUB = r"""
window.__utterances = [];
const fakeVoice = { name: 'StubEnUS', lang: 'en-US', default: true };
const stub = {
  _voices: [fakeVoice],
  getVoices() { return this._voices; },
  speak(u) {
    window.__utterances.push({ text: u.text, lang: u.lang, rate: u.rate });
    setTimeout(() => { if (u.onend) u.onend(); }, 30);
  },
  cancel() {},
  addEventListener() {},
  onvoiceschanged: null,
};
// speechSynthesis is read-only on Window — override via defineProperty.
try {
  Object.defineProperty(window, 'speechSynthesis', { value: stub, configurable: true, writable: true });
} catch (e) {
  window.speechSynthesis = stub;
}
function StubUtterance(text) {
  this.text = text;
  this.lang = 'en-US';
  this.rate = 1.0;
  this.pitch = 1.0;
  this.volume = 1.0;
  this.onend = null;
  this.onerror = null;
}
try {
  Object.defineProperty(window, 'SpeechSynthesisUtterance', { value: StubUtterance, configurable: true, writable: true });
} catch (e) {
  window.SpeechSynthesisUtterance = StubUtterance;
}
"""

FAILS = []
SKIPPED = []

def check(label, fn):
    try:
        fn()
        print(f"  PASS  {label}")
    except Exception as e:
        FAILS.append((label, str(e)))
        print(f"  FAIL  {label}: {e}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script(STUB)

        console = []
        pageerrors = []
        page = ctx.new_page()
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: pageerrors.append(str(e)))

        page.goto(URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("#tabs .tab", timeout=5000)
        page.screenshot(path=str(OUT / "01-load.png"), full_page=True)

        # 1. Hero text appears.
        def t1():
            expect(page.locator("#hero-title")).to_have_text("Listen, repeat, learn.")
        check("hero title visible", t1)

        # 2. Default tab is Greeting and shows 6 seeded cards.
        def t2():
            page.wait_for_selector(".card", timeout=3000)
            cards = page.locator(".card")
            assert cards.count() == 6, f"expected 6 greeting cards, got {cards.count()}"
        check("greeting tab seeds 6 cards", t2)

        # 3. Type input and submit → utterance recorded, status toast shows.
        def t3():
            page.fill("#word-input", "Where is the library?")
            page.click("#speak-btn")
            page.wait_for_function("window.__utterances.length >= 1", timeout=3000)
            u = page.evaluate("window.__utterances[window.__utterances.length-1]")
            assert u["text"] == "Where is the library?", u
            expect(page.locator("#status")).to_contain_text("Where is the library?")
        check("hero input → speak utterance", t3)
        page.screenshot(path=str(OUT / "02-spoken.png"), full_page=True)

        # 4. Recent tab now has that phrase as a card.
        def t4():
            page.click('button.tab[data-tab="recent"]')
            page.wait_for_selector(".card", timeout=3000)
            texts = page.locator(".card .card-text").all_inner_texts()
            assert "Where is the library?" in texts, texts
        check("recent tab includes typed phrase", t4)
        page.screenshot(path=str(OUT / "03-recent.png"), full_page=True)

        # 5. Click a recent card → speaks again, utterance count grows.
        def t5():
            before = page.evaluate("window.__utterances.length")
            page.click('.card .card-play', force=False)  # first card play btn
            page.wait_for_function(f"window.__utterances.length > {before}", timeout=3000)
        check("card Play button speaks", t5)

        # 6. Favorite toggle persists across tab switch + reload.
        def t6():
            page.click('button.tab[data-tab="animals"]')
            page.wait_for_selector(".card", timeout=3000)
            # star first card
            first = page.locator(".card").first
            label_before = first.locator(".card-text").inner_text()
            first.locator(".card-fav").click()
            # switch to favorites
            page.click('button.tab[data-tab="favorites"]')
            texts = page.locator(".card .card-text").all_inner_texts()
            assert label_before in texts, f"expected {label_before} in {texts}"
            # reload, confirm still there
            page.reload()
            page.wait_for_load_state("networkidle")
            page.click('button.tab[data-tab="favorites"]')
            texts = page.locator(".card .card-text").all_inner_texts()
            assert label_before in texts, "favorite not persisted"
        check("favorite toggle persists across reload", t6)
        page.screenshot(path=str(OUT / "04-favorites.png"), full_page=True)

        # 7. Speed slider changes utterance.rate.
        def t7():
            page.evaluate("document.getElementById('speed').value = '0.7'; document.getElementById('speed').dispatchEvent(new Event('input'))")
            txt = page.locator("#speed-value").inner_text()
            assert "0.70" in txt or "0.7" in txt, txt
            page.fill("#word-input", "slow test")
            page.click("#speak-btn")
            page.wait_for_function("window.__utterances.length >= 1", timeout=3000)
            last = page.evaluate("window.__utterances[window.__utterances.length-1]")
            assert abs(last["rate"] - 0.7) < 0.05, last
        check("speed slider affects utterance rate", t7)

        # 8. Tabs are keyboard-focusable and have aria-selected.
        def t8():
            tab = page.locator('button.tab[data-tab="greeting"]')
            assert tab.get_attribute("role") == "tab"
            page.click('button.tab[data-tab="greeting"]')
            assert tab.get_attribute("aria-selected") == "true"
        check("tab has role=tab and aria-selected updates", t8)

        # 9. Empty favorites print attempt → error toast (set up fresh).
        def t9():
            page.evaluate("localStorage.removeItem('englishboard.favs.v1'); localStorage.removeItem('englishboard.recent.v1')")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_selector("#print-btn")
            page.click("#print-btn")
            expect(page.locator("#status")).to_contain_text("Star at least one card")
        check("print without favorites shows error", t9)

        # 10. Card aria-label includes word.
        def t10():
            page.click('button.tab[data-tab="greeting"]')
            page.wait_for_selector(".card", timeout=3000)
            play = page.locator(".card .card-play").first
            label = play.get_attribute("aria-label") or ""
            assert label.startswith("Play "), label
        check("card play button aria-label", t10)

        # 11. Print stylesheet hides nav (we just check CSS rule via DOM).
        def t11():
            # quick proxy: ensure @media print exists in stylesheet
            css = page.evaluate("Array.from(document.styleSheets).map(s => { try { return Array.from(s.cssRules).map(r => r.cssText).join('\\n'); } catch(e) { return ''; }}).join('\\n')")
            assert "@media print" in css, "missing print stylesheet"
        check("print stylesheet present", t11)

        # 12. Space on focused card triggers speak.
        def t12():
            page.click('button.tab[data-tab="colors"]')
            page.wait_for_selector(".card", timeout=3000)
            before = page.evaluate("window.__utterances.length")
            card = page.locator(".card").first
            card.focus()
            page.keyboard.press("Space")
            page.wait_for_function(f"window.__utterances.length > {before}", timeout=3000)
        check("Space on focused card speaks", t12)

        # 13. F on focused card toggles favorite.
        def t13():
            page.click('button.tab[data-tab="colors"]')
            page.wait_for_selector(".card", timeout=3000)
            card = page.locator(".card").first
            word = card.locator(".card-text").inner_text()
            card.focus()
            page.keyboard.press("f")
            page.click('button.tab[data-tab="favorites"]')
            texts = page.locator(".card .card-text").all_inner_texts()
            assert word in texts
        check("F on focused card toggles favorite", t13)

        # 14. No uncaught page errors. (Console warnings about CDN noise are OK
        # — but we don't load any CDN, so the bar is "no errors".)
        def t14():
            errs = [c for c in console if c["type"] == "error"]
            # Web Speech "interrupted" event is handled; no other errors expected.
            unexpected = [c for c in errs if "interrupted" not in c["text"].lower()]
            assert not unexpected, f"console errors: {unexpected}"
            assert not pageerrors, f"page errors: {pageerrors}"
        check("no unexpected console / page errors", t14)

        # 15. Final screenshot of favorites tab with one item.
        page.click('button.tab[data-tab="favorites"]')
        page.screenshot(path=str(OUT / "05-final.png"), full_page=True)

        browser.close()

    summary = {"fails": FAILS, "skipped": SKIPPED, "screenshots": [p.name for p in OUT.glob("*.png")]}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print()
    print(f"Passes: {15 - len(FAILS)}")
    print(f"Fails:  {len(FAILS)}")
    for label, err in FAILS:
        print(f"  - {label}: {err}")
    print(f"Screenshots in {OUT}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(run())
