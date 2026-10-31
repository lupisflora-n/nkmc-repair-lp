#!/usr/bin/env python3
"""Build the review or release site without changing supplied image bytes."""
import argparse
import base64
import hashlib
import html
import json
import mimetypes
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


def lines(value):
    return '<br>'.join(esc(value).split('\n'))


def asset_path(value):
    if not isinstance(value, str) or not value.startswith('assets/'):
        raise ValueError('画像はsite/assets/以下の元ファイルを指定してください。')
    path = (SITE / value).resolve()
    if not path.is_relative_to((SITE / 'assets').resolve()) or not path.is_file():
        raise ValueError(f'画像ファイルが見つかりません: {value}')
    if path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif', '.svg'}:
        raise ValueError(f'ブラウザ表示に適した元ファイルが必要です（変換は行いません）: {value}')
    return path


def web_url(value):
    parsed = urlparse(value or '')
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ValueError('リンクには確認したHTTPS URLを指定してください。')
    return value



def canonical_url(data):
    value = data.get('publication', {}).get('siteUrl')
    if not value:
        return None
    parsed = urlparse(web_url(value))
    if parsed.query or parsed.fragment:
        raise ValueError('公開URLに共有パラメータやページ内位置を含めないでください。')
    return value if parsed.path.endswith('/') or Path(parsed.path).suffix else value + '/'


def seo_head(data, review):
    seo = data['seo']
    url = canonical_url(data) if not review else None
    business = {'@context': 'https://schema.org', '@type': seo['businessType'],
                'name': data['brand']['nameJa'], 'alternateName': data['brand']['nameEn'],
                'description': seo['description'],
                'areaServed': [{'@type': 'Place', 'name': name} for name in ['千葉県', '関東地方']],
                'sameAs': [web_url(data['contact']['profileUrl'])]}
    tags = [f'<meta property="og:site_name" content="{esc(data["brand"]["nameJa"])} LIBRIGHT">',
            '<meta name="twitter:card" content="summary">',
            f'<meta name="twitter:title" content="{esc(seo["title"])}">',
            f'<meta name="twitter:description" content="{esc(seo["description"])}">']
    if url:
        business.update({'url': url, '@id': url + '#business',
                         'logo': urljoin(url, data['brand']['assets']['horizontal'])})
        tags += [f'<link rel="canonical" href="{esc(url)}">', f'<meta property="og:url" content="{esc(url)}">']
    payload = json.dumps(business, ensure_ascii=False).replace('<', chr(92) + 'u003c')
    tags.append('<script type="application/ld+json">' + payload + '</script>')
    return '\n  '.join(tags)


def write_indexing_files(out, data):
    url = canonical_url(data)
    if not url:
        raise ValueError('公開URLを確定してから検索エンジン向けファイルを生成してください。')
    tree = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    ET.SubElement(ET.SubElement(tree, 'url'), 'loc').text = url
    ET.ElementTree(tree).write(out / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    # robots.txt is read at the origin root; the deployment checklist covers subdirectory hosting.
    (out / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + urljoin(url, 'sitemap.xml') + '\n', encoding='utf-8')


def raster_dimensions(path):
    raw = path.read_bytes()
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        return int.from_bytes(raw[16:20], 'big'), int.from_bytes(raw[20:24], 'big')
    if raw[:2] == b'\xff\xd8':
        pos = 2
        while pos + 9 < len(raw):
            if raw[pos] != 255:
                break
            while raw[pos] == 255:
                pos += 1
            marker = raw[pos]
            pos += 1
            if marker in {1, 216, 217} or 208 <= marker <= 215:
                continue
            length = int.from_bytes(raw[pos:pos + 2], 'big')
            if marker in {192, 193, 194, 195, 197, 198, 199, 201, 202, 203, 205, 206, 207}:
                return int.from_bytes(raw[pos + 5:pos + 7], 'big'), int.from_bytes(raw[pos + 3:pos + 5], 'big')
            if length < 2:
                break
            pos += length
    return None



def intro_markup(data):
    settings = data.get('intro', {})
    if not settings.get('enabled'):
        return '', ''
    if settings.get('effect') != 2 or settings.get('durationMs') != 1200:
        raise ValueError('選択済みの初回演出は2番・1200msです。')
    original = ET.fromstring(asset_path(data['brand']['assets']['symbol']).read_text(encoding='utf-8'))
    original.attrib.pop('width', None)
    original.attrib.pop('height', None)
    original.set('class', 'intro-mark')
    original.set('aria-hidden', 'true')
    original.set('focusable', 'false')
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg = ET.tostring(original, encoding='unicode')
    overlay = '<div class="intro-screen" data-intro-effect="2" data-intro-duration="1200" aria-hidden="true">' + svg + '</div>'
    return overlay, ''



def check_image_policy(data):
    policy = data['cases']['imagePolicy']
    required = {'useOriginalFiles': True, 'allowEditing': False, 'allowCompression': False,
                'allowFormatConversion': False, 'allowCropping': False,
                'preserveAspectRatio': True, 'showWholeImage': True, 'labelsOutsideImage': True}
    if any(policy.get(key) is not value for key, value in required.items()):
        raise ValueError('施工写真の無加工・全体表示ルールを維持してください。')


def verify_photos(data):
    for case in data['cases']['items']:
        for side in ('before', 'after'):
            if not case.get(side):
                continue
            path = asset_path(case[side])
            if path.suffix.lower() == '.svg':
                raise ValueError('施工写真は受領した元の写真ファイルを指定してください。')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != case.get(side + 'Sha256'):
                raise ValueError(f'{case["id"]} {side}: 元写真のSHA-256と一致しません。')


def ready(case):
    return all(case.get(key) for key in ('before', 'after', 'confirmed', 'publicationCleared'))


def release_issues(data):
    issues = []
    if not canonical_url(data):
        issues.append('正式な公開URLを設定する')
    if not data['cases'].get('publish') or not all(ready(case) for case in data['cases']['items']):
        issues.append('施工写真3組の元ファイル・内容・掲載条件を確認する')
    if not data['contact'].get('linkVerified'):
        issues.append('Instagramの実際の遷移とDMまでの経路を確認する')
    if not data['contact'].get('channelConfirmedForLp'):
        issues.append('LPの問い合わせ窓口を確定する')
    if not data['brand'].get('assetsReady') or not data['brand']['assets'].get('horizontal'):
        issues.append('正式ロゴを受領して組み込む')
    if not data.get('publication', {}).get('hostingConditionsChecked'):
        issues.append('公開先の利用条件と設定を確認する')
    return issues


def render(data, review):
    used_assets = set()
    intro_screen, intro_boot = intro_markup(data)
    intro_replay = ''
    if review and intro_screen:
        replay_screen = intro_screen.replace('class="intro-screen"', 'class="intro-replay-screen"')
        intro_replay = '<details class="intro-review"><summary><span class="intro-open-label">2番の演出を再生（1.2秒）</span><span class="intro-close-label">閉じて、もう一度再生する</span></summary></details>' + replay_screen + '<span class="intro-reduced-note">端末の「動きを減らす」設定により演出を省略しています。</span>'
    copy = data['copy']
    cases = data['cases']['items']
    visible_cases = cases if review else [case for case in cases if data['cases'].get('publish') and ready(case)]

    def photo(case, side, placeholder=False):
        value = case.get(side)
        side_ja = '補修前' if side == 'before' else '補修後'
        if value:
            asset_path(value)
            used_assets.add(value)
            dimensions = raster_dimensions(asset_path(value))
            size = f' width="{dimensions[0]}" height="{dimensions[1]}"' if dimensions else ''
            alt = case.get('altBefore' if side == 'before' else 'altAfter') or f'{case["title"]} {side_ja}'
            caption = f'{case["title"]}｜{side_ja}'
            return f'<button class="photo-button" type="button" aria-label="{esc(caption)}の写真全体を拡大" data-photo-src="{esc(value)}" data-photo-alt="{esc(alt)}" data-photo-caption="{esc(caption)}"><img class="original-photo" src="{esc(value)}" alt="{esc(alt)}"{size} loading="lazy" decoding="async"></button>'
        if placeholder:
            ratio = '4/3' if case['id'] == 'case-03' and side == 'before' else '3/4'
            return f'<div class="photo-placeholder" style="--ratio:{ratio}"><span>{esc(case["id"].upper())} / {side.upper()}</span>元写真の差し込み位置</div>'
        return ''

    cards = []
    for index, case in enumerate(visible_cases, 1):
        pair = ''.join(f'<figure>{photo(case, side, review)}<figcaption>{label}<span>{side.upper()}</span></figcaption></figure>' for side, label in [('before', '補修前'), ('after', '補修後')])
        cards.append(f'<article class="case"><div class="case-heading"><span>CASE {index:02}</span><h3>{esc(case.get("title"))}</h3></div><div class="photo-pair">{pair}</div><p class="case-description">{esc(case.get("description"))}</p></article>')
    works = ''
    if cards:
        works = '<section class="wrap" id="works"><div class="section-heading"><div><span class="section-label">REPAIR WORKS</span><h2>' + lines(copy['worksHeadline']) + '</h2></div><p>' + esc(copy['worksDescription']) + '</p></div><div class="case-list">' + ''.join(cards) + '</div><p class="photo-note">' + esc(copy['worksNote']) + '</p></section>'
    hero = '<div class="hero-text-panel"><p>木部・フローリング・<br>アルミサッシのキズ補修</p><small>引渡し前のまとめ補修・緊急補修のご相談</small></div>'
    if visible_cases:
        hero = '<figure class="hero-visual">' + photo(visible_cases[0], 'after', review) + '<figcaption>施工事例01｜縦枠の欠け補修・補修後</figcaption></figure>'
    assets = data['brand']['assets']
    if data['brand'].get('assetsReady') and assets.get('horizontal'):
        asset_path(assets['horizontal'])
        used_assets.add(assets['horizontal'])
        brand = f'<img class="brand-image" src="{esc(assets["horizontal"])}" alt="{esc(data["brand"]["nameEn"])} {esc(data["brand"]["nameJa"])}">'
    else:
        brand = f'<span class="brand-name">{esc(data["brand"]["nameEn"])}</span><small>{esc(data["brand"]["nameJa"])}｜住宅リペア・キズ補修</small>'

    def brand_image(key, class_name, alt):
        value = assets.get(key)
        if not data['brand'].get('assetsReady') or not value:
            return ''
        asset_path(value)
        used_assets.add(value)
        return f'<img class="{class_name}" src="{esc(value)}" alt="{esc(alt)}" decoding="async">'

    footer_brand = brand_image('horizontalWhite', 'footer-logo', 'LIBRIGHT リブライト') or brand
    symbol = brand_image('symbol', 'hero-symbol', '')
    if symbol:
        if copy.get('storyPlacement') == 'hero':
            caption = '<h2>' + lines(copy['aboutHeadline']) + '</h2>' if review or copy.get('aboutConfirmed') else ''
            if review or copy.get('storyConfirmed'):
                caption += ''.join(f'<p>{lines(paragraph)}</p>' for paragraph in copy['storyText'].split('\n\n'))
            hero = '<div class="hero-emblem hero-story"><span class="emblem-index">LIBRIGHT / HOUSING REPAIR</span>' + symbol + '<div class="emblem-caption">' + caption + '</div></div>'
        else:
            hero = '<div class="hero-emblem"><span class="emblem-index">LIBRIGHT / HOUSING REPAIR</span>' + symbol + '<div class="emblem-caption"><span>仕上げの一筆。</span><p>その先の、晴れやかな暮らしへ。</p></div></div>'
    favicon = ''
    for key, mime, sizes in [('favicon', 'image/svg+xml', 'any'), ('faviconPng', 'image/png', '32x32')]:
        if data['brand'].get('assetsReady') and assets.get(key):
            asset_path(assets[key])
            used_assets.add(assets[key])
            favicon += f'<link rel="icon" type="{mime}" sizes="{sizes}" href="{esc(assets[key])}">'

    about = ''
    if copy.get('showAboutSection', True) and copy.get('aboutText') and (review or copy.get('aboutConfirmed')):
        paragraphs = ''.join(f'<p>{lines(p)}</p>' for p in copy['aboutText'].split('\n\n'))
        bridge = f'<p class="contractor-bridge">{esc(copy["contractorBridge"])}</p>' if copy.get('contractorBridge') else ''
        origin = f'<div class="brand-origin"><h3>LIBRIGHTの名前に重ねる思い</h3><p>{esc(copy["brandOriginText"])}</p></div>' if copy.get('brandOriginText') else ''
        narrative = paragraphs + origin
        if copy.get('storyText') and (review or copy.get('storyConfirmed')):
            story = ''.join(f'<p>{lines(p)}</p>' for p in copy['storyText'].split('\n\n'))
            narrative = '<h3 class="story-heading">' + lines(copy['storyHeadline']) + '</h3>' + story + '<details class="concept-details"><summary>リブライトが大切にしていること</summary><div>' + paragraphs + origin + '</div></details>'
        about_title = copy['aboutHeadline']
        if copy.get('storyPlacement') == 'hero':
            about_title = copy['storyHeadline']
            narrative = '<details class="concept-details"><summary>リブライトが大切にしていること</summary><div>' + paragraphs + origin + '</div></details>'
        about = '<section class="wrap about-grid" id="brand-concept"><div><span class="section-label">OUR STORY</span><h2>' + lines(about_title) + '</h2>' + bridge + '</div><div class="about-text">' + narrative + '</div></section>'
    practice = ''
    if copy.get('practiceItems') and (review or copy.get('practiceConfirmed')):
        items = ''.join(f'<li><span class="practice-number">{i:02}</span><h3>{esc(item["title"])}</h3><p>{esc(item["text"])}</p></li>' for i, item in enumerate(copy['practiceItems'], 1))
        practice = '<section class="practice-section" id="approach"><div class="wrap"><span class="section-label">OUR APPROACH</span><h2>' + lines(copy['practiceHeadline']) + '</h2><ol class="practice-list">' + items + '</ol></div></section>'
    service_rows = '<div class="service-grid">' + ''.join(f'<div class="service-row"><span class="service-number">{i:02}</span><h3>{esc(name)}</h3><p>{esc(text)}</p></div>' for i, (name, text) in enumerate(zip(data['services'].get('titles', data['services']['requests']), data['services']['descriptions']), 1)) + '</div>'
    steps = ''
    if copy.get('processSteps') and (review or copy.get('processConfirmed')):
        steps = '<section class="wrap" id="process"><span class="section-label">HOW TO REQUEST</span><h2>' + lines(copy['processHeadline']) + '</h2><ol class="steps">' + ''.join(f'<li><h3>{esc(step["title"])}</h3><p>{esc(step["text"])}</p></li>' for step in copy['processSteps']) + '</ol></section>'
    faq = [item for item in copy.get('faq') or [] if review or item.get('confirmed')]
    faq_section = ''
    if faq:
        faq_section = '<section class="faq-section"><div class="wrap"><span class="section-label">QUESTIONS</span><h2>' + lines(copy['faqHeadline']) + '</h2><div class="faq-list">' + ''.join(f'<details class="faq-item"><summary>{esc(item["question"])}</summary><p>{esc(item["answer"])}</p></details>' for item in faq) + '</div></div></section>'
    pricing = ''
    price = data['pricing']
    if price.get('publish'):
        if not price.get('confirmed'):
            raise ValueError('料金は確認済みになってから公開してください。')
        labels = [('minimum', '最低料金'), ('travelFee', '出張費'), ('taxNote', '税の表示'), ('estimateFee', '見積もり費用'), ('estimateConditions', '見積もり条件'), ('paymentConditions', 'お支払い')]
        rows = ''.join(f'<tr><th scope="row">{esc(label)}</th><td>{esc(price[key])}</td></tr>' for key, label in labels if price.get(key) is not None)
        if not rows:
            raise ValueError('公開する料金情報が空です。')
        pricing = '<section class="wrap" id="pricing"><span class="section-label">PRICING</span><h2>料金・お見積もりについて。</h2><table class="price-table"><tbody>' + rows + '</tbody></table></section>'
    partner = ''
    p = data['partnerIntroduction']
    if p.get('publish'):
        if not all(p.get(key) for key in ['name', 'relationship', 'description', 'officialUrl', 'confirmed', 'publicationCleared']):
            raise ValueError('協力先紹介は、関係・紹介文・公式案内先・掲載条件を確認してから公開してください。')
        partner = f'<section class="partner-section" id="partner"><div class="wrap"><span class="section-label">PARTNER</span><h2>{esc(p["name"])}</h2><p>{esc(p["relationship"])}</p><p>{esc(p["description"])}</p><a href="{esc(web_url(p["officialUrl"]))}" target="_blank" rel="noopener noreferrer">{esc(p["name"])}の公式サイトを見る</a></div></section>'
    elif review and p.get('reviewDraft', {}).get('show'):
        draft = p['reviewDraft']
        draft_links = '<nav class="partner-links" aria-label="TRC・RBSのご紹介">' + ''.join(f'<a href="{esc(web_url(link["url"]))}" target="_blank" rel="noopener noreferrer">{esc(link["label"])}</a>' for link in draft.get('links', []) if link.get('label')) + '</nav>' if draft.get('links') else ''
        partner = '<section class="partner-section" id="partner"><div class="wrap partner-grid"><div><span class="section-label">FIELD WORK</span><h2>' + lines(draft['headline']) + '</h2><p class="partner-draft-note">紹介文案｜関係・紹介内容・掲載条件は最終確認前です。</p></div><div><p>' + esc(draft['relationship']) + '</p>' + (('<p>' + esc(draft['approach']) + '</p>') if draft.get('approach') else '') + '</div><aside class="partner-company" aria-labelledby="partner-company-title"><div><h3 id="partner-company-title">' + esc(draft['companyHeadline']) + '</h3><p>' + lines(draft['description']) + '</p></div>' + draft_links + '</aside></div></section>'
    business = data['business']
    business_html = ''
    if business.get('publishDetails'):
        business_html = '<div class="business-details">' + '<br>'.join(esc(business[key]) for key in ['publicRepresentativeName', 'publicAddress'] if business.get(key)) + '</div>'
    review_bar = '<div class="review-bar"><span>DESIGN PREVIEW</span> 制作確認版・未公開｜掲載内容は最終確認前です。' + intro_replay + '</div>' if review else ''
    values = {
        'INTRO_SCREEN': intro_screen, 'INTRO_BOOT': intro_boot,
        'ROBOTS': 'noindex,nofollow' if review else 'index,follow',
        'TITLE': esc(data['seo']['title']),
        'SEO_HEAD': seo_head(data, review),
        'META_DESCRIPTION': esc(data['seo']['description']),
        'REVIEW_BAR': review_bar, 'BRAND': brand,
        'FOOTER_BRAND': footer_brand, 'FAVICONS': favicon or '<link rel="icon" href="data:,">',
        'BRAND_NAME': esc(data['brand']['nameEn']), 'BRAND_NAME_JA': esc(data['brand']['nameJa']),
        'WORKS_NAV': '<a class="nav-detail" href="#works">施工事例</a>' if cards else '',
        'WORKS_LINK': '<a class="text-link" href="#works">施工前後の写真を見る ↓</a>' if cards else '',
        'HERO_HEADLINE': lines(copy['heroHeadline']), 'HERO_DESCRIPTION': lines(copy['heroDescription']),
        'BRAND_PROMISE': f'<p class="brand-promise">{esc(copy["brandPromise"])}</p>' if copy.get('brandPromise') else '',
        'PRIMARY_CTA': esc(copy['primaryCta']), 'HERO_VISUAL': hero,
        'AREA_SUMMARY': esc(data['area']['summary']),
        'HERO_EYEBROW': ('<p class="eyebrow">' + esc(copy['heroEyebrow']) + '</p>') if copy.get('heroEyebrow') else '',
        'MOBILE_CONTACT_NOTE': lines(copy['mobileContactNote']),
        'PRACTICE_SECTION': practice,
        **{key: lines(copy[name]) for key, name in [('HERO_SUBNOTE', 'heroSubnote'), ('SERVICES_HEADLINE', 'servicesHeadline'), ('AREA_HEADLINE', 'areaHeadline'), ('AREA_DESCRIPTION', 'areaDescription'), ('CONTACT_HEADLINE', 'contactHeadline'), ('CONTACT_PROMPT', 'contactPrompt'), ('CONTACT_BUTTON', 'contactButton'), ('CONTACT_HELP', 'contactHelp'), ('SECONDARY_AUDIENCE', 'secondaryAudience')]},
        'CONTACT_INTRO': ('<p>' + lines(copy['contactIntro']) + '</p>') if copy.get('contactIntro') else '',
        'CONTACT_FIELDS': ''.join(f'<li>{esc(field)}</li>' for field in copy['contactFields']),
        'MATERIALS_LINE': ''.join(f'<span>{esc(value)}</span>' for value in data['services']['materials']),
        'WORKS_SECTION': works, 'SERVICE_ROWS': service_rows, 'ABOUT_SECTION': about,
        'PRICING_SECTION': pricing, 'PROCESS_SECTION': steps, 'FAQ_SECTION': faq_section,
        'PARTNER_SECTION': partner, 'BUSINESS_DETAILS': business_html,
        'INSTAGRAM_URL': esc(web_url(data['contact']['profileUrl'])),
        'MESSAGE_TEMPLATE': esc(data['contact']['suggestedMessage'])
    }
    return values, used_assets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['review', 'release'], default='review')
    args = parser.parse_args()
    data = json.loads((SITE / 'content.json').read_text(encoding='utf-8'))
    check_image_policy(data)
    verify_photos(data)
    issues = release_issues(data)
    if args.mode == 'release' and issues:
        raise SystemExit('公開版は未作成です。残る項目:\n- ' + '\n- '.join(issues))
    values, assets = render(data, review=args.mode == 'review')
    template = (SITE / 'template.html').read_text(encoding='utf-8')
    css = (SITE / 'styles.css').read_text(encoding='utf-8')
    js = (SITE / 'app.js').read_text(encoding='utf-8')

    def compile_page(standalone):
        v = dict(values)
        v['STYLE'] = '<style>\n' + css + '\n</style>' if standalone else '<link rel="stylesheet" href="styles.css">'
        v['SCRIPT'] = '<script>\n' + js + '\n</script>' if standalone else '<script src="app.js" defer></script>'
        result = re.sub(r'\{\{([A-Z_]+)\}\}', lambda match: v[match.group(1)], template)
        if standalone:
            # Single-file preview: reversible data URIs preserve every supplied asset byte.
            for value in sorted(assets):
                mime = mimetypes.guess_type(value)[0] or 'application/octet-stream'
                encoded = base64.b64encode(asset_path(value).read_bytes()).decode('ascii')
                result = result.replace('"' + esc(value) + '"', '"data:' + mime + ';base64,' + encoded + '"')
        return '\n'.join(line.rstrip() for line in result.split('\n'))

    out = ROOT / ('dist-review' if args.mode == 'review' else 'dist')
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    (out / 'index.html').write_text(compile_page(False), encoding='utf-8')
    shutil.copyfile(SITE / 'styles.css', out / 'styles.css')
    shutil.copyfile(SITE / 'app.js', out / 'app.js')
    (out / '.nojekyll').write_text('', encoding='utf-8')
    for value in assets:
        source = asset_path(value)
        target = out / value
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(target.read_bytes()).digest():
            raise ValueError(f'元画像と配信ファイルが一致しません: {value}')
    if args.mode == 'release':
        write_indexing_files(out, data)
    if args.mode == 'review':
        preview = ROOT / 'design' / 'preview.html'
        preview.parent.mkdir(exist_ok=True)
        preview.write_text(compile_page(True), encoding='utf-8')
        for value in assets:
            if value.startswith('assets/brand/'):
                continue
            target = preview.parent / value
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset_path(value), target)
        print('確認版: design/preview.html / dist-review/index.html')
    print('公開までの確認項目:', len(issues))
    for issue in issues:
        print('- ' + issue)


if __name__ == '__main__':
    main()
