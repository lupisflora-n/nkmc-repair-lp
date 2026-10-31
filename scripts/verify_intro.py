#!/usr/bin/env python3
"""Verify CSS intro and native replay, including with page JavaScript disabled."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'design/preview.html').read_text()
report = {}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage'])
    try:
        for scripts in [True, False]:
            context = browser.new_context(java_script_enabled=scripts, viewport={'width':390,'height':844})
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.set_content(html, wait_until='load')
            # Freeze CSS animations at explicit points to check the actual markup deterministically.
            page.evaluate("""() => document.querySelector('.intro-screen').getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=900})""")
            assert page.locator('.intro-screen').is_visible()
            transforms = page.locator('.intro-screen [data-part]').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).transform)')
            assert len(transforms) == 5 and all(t != 'none' for t in transforms), transforms
            page.evaluate("""() => document.querySelector('.intro-screen').getAnimations({subtree:true}).forEach(a=>{a.currentTime=2200})""")
            opacity = float(page.locator('.intro-screen').evaluate('(e)=>getComputedStyle(e).opacity'))
            assert 0 < opacity < 1, opacity
            transforms = page.locator('.intro-screen [data-part]').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).transform)')
            assert all(t in ('none', 'matrix(1, 0, 0, 1, 0, 0)') for t in transforms), transforms
            page.evaluate("""() => document.querySelector('.intro-screen').getAnimations({subtree:true}).forEach(a=>{a.currentTime=2400})""")
            assert not page.locator('.intro-screen').is_visible()
            assert page.locator('h1').is_visible()
            page.locator('.intro-review summary').click()
            page.wait_for_timeout(100)
            assert page.locator('.intro-replay-screen').is_visible()
            page.wait_for_timeout(2450)
            assert not page.locator('.intro-replay-screen').is_visible()
            if not scripts:
                page.locator('.intro-review summary').click()  # close native details
                page.wait_for_timeout(50)
            page.locator('.intro-review summary').click()
            page.wait_for_timeout(100)
            assert page.locator('.intro-replay-screen').is_visible(), {'scripts':scripts,'open':page.locator('.intro-review').get_attribute('open'),'style':page.locator('.intro-replay-screen').evaluate('(e)=>({opacity:getComputedStyle(e).opacity,animation:getComputedStyle(e).animationName})')}
            assert not errors, errors
            report['cssIntroAndRepeatReplayWithJavaScript' if scripts else 'cssIntroAndRepeatReplayWithoutJavaScript'] = True
            context.close()
        context = browser.new_context(reduced_motion='reduce')
        page = context.new_page(); page.set_content(html,wait_until='load')
        assert not page.locator('.intro-screen').is_visible()
        assert not page.locator('.intro-review').is_visible()
        assert page.locator('.intro-reduced-note').is_visible()
        report['reducedMotionSkipsAndExplains'] = True
        context.close()
        page = browser.new_page();page.set_content(html,wait_until='load')
        page.keyboard.press('Tab')
        assert page.locator('.intro-screen').count() == 0
        report['keyboardSkip'] = True
        page.close()
        page = browser.new_page();page.set_content(html,wait_until='load')
        page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
        assert page.locator('.intro-screen').count() == 0
        report['backForwardRestoreClearsOverlay'] = True
    finally:
        browser.close()
(ROOT / 'qa/intro-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
