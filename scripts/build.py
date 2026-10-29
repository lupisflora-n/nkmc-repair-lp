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
from urllib.parse import urlparse

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
    cases = data['cases']['items']
    visible_cases = cases if review else [case for case in cases if data['cases'].get('publish') and ready(case)]

    def photo(case, side, placeholder=False):
        value = case.get(side)
        side_ja = '補修前' if side == 'before' else '補修後'
        if value:
            asset_path(value)
            used_assets.add(value)
            alt = case.get('altBefore' if side == 'before' else 'altAfter') or f'{case["title"]} {side_ja}'
            caption = f'{case["title"]}｜{side_ja}'
            return f'<button class="photo-button" type="button" aria-label="{esc(caption)}の写真全体を拡大" data-photo-src="{esc(value)}" data-photo-alt="{esc(alt)}" data-photo-caption="{esc(caption)}"><img class="original-photo" src="{esc(value)}" alt="{esc(alt)}" loading="lazy" decoding="async"></button>'
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
        works = '<section class="wrap" id="works"><div class="section-heading"><div><span class="section-label">REPAIR WORKS</span><h2>補修前と補修後を、<br>写真でご覧ください。</h2></div><p>部材やキズの状態とあわせて、補修前後の変化をご紹介します。</p></div><div class="case-list">' + ''.join(cards) + '</div><p class="photo-note">※補修前後で、撮影位置・距離・光の条件が異なります。</p></section>'
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
        hero = '<div class="hero-emblem"><span class="emblem-index">LIBRIGHT / HOUSING REPAIR</span>' + symbol + '<div class="emblem-caption"><span>仕上げの一筆。</span><p>その先の、晴れやかな暮らしへ。</p></div></div>'
    favicon = ''
    for key, mime, sizes in [('favicon', 'image/svg+xml', 'any'), ('faviconPng', 'image/png', '32x32')]:
        if data['brand'].get('assetsReady') and assets.get(key):
            asset_path(assets[key])
            used_assets.add(assets[key])
            favicon += f'<link rel="icon" type="{mime}" sizes="{sizes}" href="{esc(assets[key])}">'

    copy = data['copy']
    about = ''
    if copy.get('aboutText') and (review or copy.get('aboutConfirmed')):
        paragraphs = ''.join(f'<p>{lines(p)}</p>' for p in copy['aboutText'].split('\n\n'))
        bridge = f'<p class="contractor-bridge">{esc(copy["contractorBridge"])}</p>' if copy.get('contractorBridge') else ''
        origin = f'<div class="brand-origin"><h3>LIBRIGHTの名前に重ねる思い</h3><p>{esc(copy["brandOriginText"])}</p></div>' if copy.get('brandOriginText') else ''
        about = '<section class="wrap about-grid" id="brand-concept"><div><span class="section-label">ABOUT LIBRIGHT</span><h2>' + lines(copy['aboutHeadline']) + '</h2>' + bridge + '</div><div class="about-text">' + paragraphs + origin + '</div></section>'
    service_rows = '<div class="service-grid">' + ''.join(f'<div class="service-row"><span class="service-number">{i:02}</span><h3>{esc(name)}</h3><p>{esc(text)}</p></div>' for i, (name, text) in enumerate(zip(data['services'].get('titles', data['services']['requests']), data['services']['descriptions']), 1)) + '</div>'
    steps = ''
    if copy.get('processSteps') and (review or copy.get('processConfirmed')):
        steps = '<section class="wrap" id="process"><span class="section-label">HOW TO REQUEST</span><h2>ご相談から施工まで。</h2><ol class="steps">' + ''.join(f'<li><h3>{esc(step["title"])}</h3><p>{esc(step["text"])}</p></li>' for step in copy['processSteps']) + '</ol></section>'
    faq = [item for item in copy.get('faq') or [] if review or item.get('confirmed')]
    faq_section = ''
    if faq:
        faq_section = '<section class="faq-section"><div class="wrap"><span class="section-label">QUESTIONS</span><h2>ご相談の前に。</h2><div class="faq-list">' + ''.join(f'<details class="faq-item"><summary>{esc(item["question"])}</summary><p>{esc(item["answer"])}</p></details>' for item in faq) + '</div></div></section>'
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
        partner = f'<section class="partner-section"><div class="wrap"><span class="section-label">PARTNER</span><h2>{esc(p["name"])}</h2><p>{esc(p["relationship"])}</p><p>{esc(p["description"])}</p><a href="{esc(web_url(p["officialUrl"]))}" target="_blank" rel="noopener noreferrer">{esc(p["name"])}の公式サイトを見る</a></div></section>'
    business = data['business']
    business_html = ''
    if business.get('publishDetails'):
        business_html = '<div class="business-details">' + '<br>'.join(esc(business[key]) for key in ['publicRepresentativeName', 'publicAddress'] if business.get(key)) + '</div>'
    review_bar = '<div class="review-bar"><span>DESIGN PREVIEW</span> 制作確認版・未公開｜施工写真は配置枠です。</div>' if review else ''
    values = {
        'ROBOTS': 'noindex,nofollow' if review else 'index,follow',
        'TITLE': esc('工務店・建築会社向け住宅リペア｜千葉・関東｜LIBRIGHT'),
        'META_DESCRIPTION': esc('リブライトは千葉県を中心に関東エリアの住宅のキズ補修に対応。木部・フローリング・アルミサッシ、引渡し前のまとめ補修や緊急補修、継続的なお取引をご相談いただけます。'),
        'REVIEW_BAR': review_bar, 'BRAND': brand,
        'FOOTER_BRAND': footer_brand, 'FAVICONS': favicon or '<link rel="icon" href="data:,">',
        'BRAND_NAME': esc(data['brand']['nameEn']), 'BRAND_NAME_JA': esc(data['brand']['nameJa']),
        'WORKS_NAV': '<a class="nav-detail" href="#works">施工事例</a>' if cards else '',
        'WORKS_LINK': '<a class="text-link" href="#works">施工前後の写真を見る ↓</a>' if cards else '',
        'HERO_HEADLINE': lines(copy['heroHeadline']), 'HERO_DESCRIPTION': lines(copy['heroDescription']),
        'BRAND_PROMISE': f'<p class="brand-promise">{esc(copy["brandPromise"])}</p>' if copy.get('brandPromise') else '',
        'PRIMARY_CTA': esc(copy['primaryCta']), 'HERO_VISUAL': hero,
        'AREA_SUMMARY': esc(data['area']['summary']),
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
            # Brand assets only: lossless data URIs. Construction photos stay original files.
            for value in sorted(assets):
                if not value.startswith('assets/brand/'):
                    continue
                mime = mimetypes.guess_type(value)[0] or 'application/octet-stream'
                encoded = base64.b64encode(asset_path(value).read_bytes()).decode('ascii')
                result = result.replace('"' + esc(value) + '"', '"data:' + mime + ';base64,' + encoded + '"')
        return result

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
