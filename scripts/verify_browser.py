#!/usr/bin/env python3
"""Verify the built LP locally; never send an Instagram DM or publish a site."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'
QA.mkdir(exist_ok=True)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT / 'dist-review')))
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
origin = f'http://127.0.0.1:{server.server_port}'
report = {'pageErrors': [], 'failedRequests': [], 'viewports': [], 'checks': {}, 'limits': [
    '元写真ファイルが未取得のため、実写真の表示・ハッシュ検証・拡大表示の実動作は未検証。',
    'Instagramの外部通信はテストで代替し、遷移先URLを確認した。実アカウントの表示、DM画面と送受信は未検証。',
    'ローカルの確認版を検証。GitHubや他ホスティングへは未公開。',
    'file://の直接起動は実行環境の管理ポリシーで遮断されるため、単体HTMLの内容をブラウザへ読み込んで確認。'
]}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        try:
            context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()
            page.on('pageerror', lambda error: report['pageErrors'].append(str(error)))
            page.on('requestfailed', lambda request: report['failedRequests'].append(request.url))
            for width, height in [(390, 844), (320, 740), (768, 1024), (1440, 1000)]:
                page.set_viewport_size({'width': width, 'height': height})
                response = page.goto(origin + '/', wait_until='networkidle')
                assert response.status == 200
                assert page.locator('h1').count() == 1
                assert page.locator('.case').count() == 3
                assert page.locator('.photo-placeholder').count() == 6
                page.wait_for_function('Array.from(document.querySelectorAll("img[src]")).every(img => img.complete && img.naturalWidth > 0)')
                for selector in ['.brand-image', '.footer-logo']:
                    dimensions = page.locator(selector).evaluate('(img) => ({width: img.getBoundingClientRect().width, height: img.getBoundingClientRect().height, ratio: img.naturalWidth / img.naturalHeight})')
                    assert dimensions['width'] >= 220, (selector, width, dimensions)
                    assert abs(dimensions['width'] / dimensions['height'] - dimensions['ratio']) < .02
                assert page.locator('.hero-symbol').count() == 1
                overflow = page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
                assert not overflow, f'horizontal overflow at {width}px'
                assert page.locator('#pricing').count() == 0
                assert page.locator('.partner-section').count() == 0
                assert page.locator('.original-photo').count() == 0
                if width in (390, 1440):
                    page.screenshot(path=str(QA / f'preview-{width}.png'), full_page=True)
                    page.screenshot(path=str(QA / f'preview-top-{width}.png'))
                report['viewports'].append({'width': width, 'height': height, 'http': response.status, 'horizontalOverflow': overflow})
            page.set_viewport_size({'width': 390, 'height': 844})
            page.goto(origin + '/', wait_until='networkidle')
            page.locator('.hero .button').click()
            assert page.evaluate('location.hash') == '#contact'
            report['checks']['heroToContact'] = True
            page.locator('[data-copy-message]').click()
            page.wait_for_function('document.querySelector("[data-copy-message]").dataset.copyState !== undefined')
            assert page.locator('[data-copy-message]').get_attribute('data-copy-state') == 'copied', page.locator('#copy-status').inner_text()
            clipboard = page.evaluate('navigator.clipboard.readText()')
            assert clipboard == page.locator('#message-template').input_value()
            report['checks']['actualClipboardCopy'] = True
            page.locator('.faq-item').first.locator('summary').click()
            assert page.locator('.faq-item').first.get_attribute('open') is not None
            report['checks']['faqExpanded'] = True
            context.route('https://www.instagram.com/**', lambda route: route.fulfill(status=200, content_type='text/html', body='<title>External navigation check</title>'))
            with page.expect_popup() as popup_info:
                page.locator('.instagram-link').click()
            popup = popup_info.value
            popup.wait_for_load_state()
            assert popup.url == 'https://www.instagram.com/libright_chiba/'
            report['checks']['instagramProfileDestination'] = popup.url
            popup.close()
            for link in page.locator('a[href^="#"]').all():
                target = link.get_attribute('href')[1:]
                assert page.locator('[id="' + target + '"]').count() == 1
            report['checks']['allInternalAnchors'] = True
            report['checks']['brandAssetsLoadedAndProportionsPreserved'] = True
            fallback = browser.new_context(viewport={'width': 390, 'height': 844})
            fallback.add_init_script('Object.defineProperty(navigator, "clipboard", {get: () => undefined});')
            fallback_page = fallback.new_page()
            fallback_page.goto(origin + '/', wait_until='networkidle')
            fallback_page.locator('[data-copy-message]').click()
            assert fallback_page.locator('[data-copy-message]').get_attribute('data-copy-state') == 'selected'
            assert fallback_page.locator('#message-template').evaluate('(el) => el.selectionEnd - el.selectionStart === el.value.length')
            report['checks']['manualCopyFallback'] = True
            fallback.close()
            offline = browser.new_context(java_script_enabled=False)
            offline_page = offline.new_page()
            offline_page.set_content((ROOT / 'design/preview.html').read_text(encoding='utf-8'), wait_until='load')
            assert offline_page.locator('h1').is_visible()
            assert offline_page.locator('.instagram-link').get_attribute('href') == 'https://www.instagram.com/libright_chiba/'
            assert offline_page.locator('#message-template').input_value()
            offline_page.wait_for_function('Array.from(document.querySelectorAll("img[src]")).every(img => img.complete && img.naturalWidth > 0)')
            assert offline_page.locator('.brand-image').get_attribute('src').startswith('data:image/svg+xml;base64,')
            offline.close()
            report['checks']['standaloneHtmlAndNoJsContent'] = True
            assert not report['pageErrors'], report['pageErrors']
            assert not report['failedRequests'], report['failedRequests']
        finally:
            browser.close()
finally:
    server.shutdown()
    server.server_close()
    (QA / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
