#!/usr/bin/env python3
"""Check scroll reveals without changing or sending original construction photos."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'design/release-preview.html').read_text()
report = {}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage'])
    try:
        page = browser.new_page(viewport={'width':390, 'height':740})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(HTML, wait_until='load')
        frames = page.locator('.photo-pair figure')
        assert frames.count() == 6
        assert frames.first.get_attribute('data-scroll-reveal') == 'pending'
        page.wait_for_function("document.documentElement.dataset.introState==='complete'")
        assert frames.first.get_attribute('data-scroll-reveal') == 'pending'
        pair = page.locator('.photo-pair').first
        pair.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-140,behavior:'instant'})")
        page.wait_for_function("[...document.querySelector('.photo-pair').children].every(e=>e.dataset.scrollReveal==='visible')")
        # Freeze actual CSS transitions at the same time to compare before/after stagger.
        pair.evaluate("e=>[...e.children].forEach(f=>f.getAnimations().forEach(a=>{a.pause();a.currentTime=200}))")
        opacity = pair.locator('figure').evaluate_all('(es)=>es.map(e=>Number(getComputedStyle(e).opacity))')
        assert 0 < opacity[0] < 1 and 0 <= opacity[1] < opacity[0], opacity
        pair.evaluate("e=>[...e.children].forEach(f=>f.getAnimations().forEach(a=>{a.currentTime=1200}))")
        assert pair.locator('figure').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
        for photo in page.locator('.original-photo').all():
            assert photo.evaluate('(e)=>getComputedStyle(e).transform') == 'none'
            assert photo.evaluate('(e)=>getComputedStyle(e).filter') == 'none'
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.wait_for_timeout(100)
        assert frames.first.get_attribute('data-scroll-reveal') == 'visible'
        report['photoStaggerAndOneTimeReveal'] = True
        page.evaluate("location.hash='works'")
        page.wait_for_timeout(150)
        report['worksAnchorKeepsLaterPhotosForScroll'] = True
        assert frames.nth(4).get_attribute('data-scroll-reveal') == 'pending'
        frames.nth(4).locator('button').focus()
        assert frames.nth(4).get_attribute('data-reveal-instant') is not None
        assert frames.nth(4).evaluate('(e)=>getComputedStyle(e).opacity') == '1'
        report['keyboardFocusIsImmediatelyVisible'] = True
        page.evaluate("location.hash='contact'")
        page.wait_for_function("[...document.querySelectorAll('#contact [data-scroll-reveal]')].every(e=>e.dataset.scrollReveal==='visible')")
        assert page.locator('#message-template').is_visible()
        report['contactAnchorImmediatelyVisible'] = True
        page.emulate_media(media='print')
        assert page.locator('[data-scroll-reveal]').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
        report['printShowsAllContent'] = True
        assert not errors, errors
        page.close()
        reduced = browser.new_context(reduced_motion='reduce')
        page = reduced.new_page();page.set_content(HTML, wait_until='load')
        assert page.locator('[data-scroll-reveal="pending"]').count() == 0
        assert page.locator('.photo-pair figure').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
        reduced.close();report['reducedMotionShowsContentWithoutAnimation'] = True
        nojs = browser.new_context(java_script_enabled=False)
        page = nojs.new_page();page.set_content(HTML, wait_until='load')
        assert page.locator('[data-scroll-reveal]').count() == 0
        assert page.locator('.photo-pair figure').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
        nojs.close();report['noJavaScriptContentVisible'] = True
        for broken in [False, True]:
            page = browser.new_page()
            page.evaluate('() => { window.IntersectionObserver=class {constructor(){throw new Error("unavailable")}}; }' if broken else 'delete window.IntersectionObserver')
            page.set_content(HTML, wait_until='load')
            assert page.locator('.photo-pair figure').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
            page.close()
        report['missingOrFailedObserverKeepsContentVisible'] = True
    finally:
        browser.close()
(ROOT / 'qa/scroll-reveal-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
