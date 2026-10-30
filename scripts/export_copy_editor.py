#!/usr/bin/env python3
"""Export the current LP wording as one editable request document, without changing the LP."""
from pathlib import Path
from html import escape
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'site/content.json').read_text(encoding='utf-8'))
records = []
group = ''
counter = 0


def section(code, title):
    global group, counter
    group, counter = code, 0
    records.append({'section': code + '｜' + title})


def field(label, path=None, value=None, source=None):
    global counter
    counter += 1
    if path:
        value = data
        for part in path.split('.'):
            value = value[int(part)] if isinstance(value, list) else value[part]
        source = 'site/content.json:' + path
    else:
        assert value in (ROOT / source).read_text(encoding='utf-8'), (label, value)
    assert isinstance(value, str)
    records.append({'id': f'{group}{counter:02}', 'label': label, 'text': value, 'source': source})


section('A', '冒頭')
field('対象のお客様（削除済み）', 'copy.heroEyebrow')
for label,key in [('主見出し','heroHeadline'),('説明文','heroDescription'),('ブランドの一文','brandPromise'),('相談ボタン','primaryCta'),('相談ボタン下の補足','heroSubnote')]: field(label,'copy.'+key)
field('施工写真へのリンク', value='施工前後の写真を見る ↓',source='scripts/build.py')
field('旧マーク横の短い言葉（削除済み・E01が冒頭に移動）',value='',source='scripts/build.py')
field('旧マーク横の補足（削除済み・E04が冒頭に移動）',value='',source='scripts/build.py')
section('B','対応地域・部材の帯（部材名は地域欄にも共通）')
field('地域の要約','area.summary')
for i in range(len(data['services']['materials'])):field(f'対応部材{i+1}','services.materials.'+str(i))
field('業務の短い説明',value='住宅リペア・キズ補修',source='site/template.html')
section('C','施工前後の写真・説明')
for label,key in [('見出し','worksHeadline'),('導入文','worksDescription')]:field(label,'copy.'+key)
for i,case in enumerate(data['cases']['items']):
    field(f'事例{i+1}の見出し',f'cases.items.{i}.title')
    field(f'事例{i+1}の説明',f'cases.items.{i}.description')
for text in ('補修前','補修後'):field('写真外の共通ラベル',value=text,source='scripts/build.py')
field('撮影条件・拡大の注記','copy.worksNote')
section('D','対応内容')
field('見出し','copy.servicesHeadline')
for i in range(len(data['services']['titles'])):
    field(f'対応内容{i+1}の小見出し',f'services.titles.{i}')
    field(f'対応内容{i+1}の説明',f'services.descriptions.{i}')
section('E','原点の物語・ブランドの思い（開閉内の文章を含む）')
for label,key in [('ブランド見出し','aboutHeadline'),('工務店向けの接続文','contractorBridge'),('物語の小見出し','storyHeadline'),('物語の本文','storyText')]:field(label,'copy.'+key)
field('詳細を開く文',value='リブライトが大切にしていること',source='scripts/build.py')
field('コンセプト本文','copy.aboutText')
field('名前の由来の小見出し',value='LIBRIGHTの名前に重ねる思い',source='scripts/build.py')
field('名前の由来の本文','copy.brandOriginText')
section('F','現在の実務・TRC／RBS紹介')
for label,key in [('Nさんの実務の見出し','headline'),('学びと現場協力の説明','relationship'),('現在の取り組みの補足','approach'),('TRC紹介の小見出し','companyHeadline'),('TRC・RBS紹介の本文','description')]:field(label,'partnerIntroduction.reviewDraft.'+key)
for i in range(len(data['partnerIntroduction']['reviewDraft']['links'])):field(f'案内リンク{i+1}の表示文',f'partnerIntroduction.reviewDraft.links.{i}.label')
section('G','現場で大切にすること')
field('見出し','copy.practiceHeadline')
for i in range(len(data['copy']['practiceItems'])):
    field(f'項目{i+1}の小見出し',f'copy.practiceItems.{i}.title')
    field(f'項目{i+1}の説明',f'copy.practiceItems.{i}.text')
section('H','対応地域')
field('見出し','copy.areaHeadline');field('説明','copy.areaDescription')
section('I','相談から施工まで')
field('見出し','copy.processHeadline')
for i in range(len(data['copy']['processSteps'])):
    field(f'手順{i+1}の小見出し',f'copy.processSteps.{i}.title')
    field(f'手順{i+1}の説明',f'copy.processSteps.{i}.text')
section('J','よくある質問')
field('見出し','copy.faqHeadline')
for i in range(len(data['copy']['faq'])):
    field(f'質問{i+1}',f'copy.faq.{i}.question');field(f'回答{i+1}',f'copy.faq.{i}.answer')
section('K','問い合わせ')
for label,key in [('見出し','contactHeadline'),('導入文','contactIntro'),('必要情報の案内','contactPrompt')]:field(label,'copy.'+key)
for i in range(len(data['copy']['contactFields'])):field(f'お知らせいただく内容{i+1}',f'copy.contactFields.{i}')
for label,key in [('Instagramボタン','contactButton'),('DMへの進み方','contactHelp')]:field(label,'copy.'+key)
field('相談文のひな形の見出し',value='相談文のひな形',source='site/template.html')
field('相談文のひな形','contact.suggestedMessage')
field('コピーのボタン',value='相談文をコピーする',source='site/template.html')
field('コピー成功時の案内',value='コピーしました。Instagramの「メッセージ」から、DMに貼り付けてお使いください。',source='site/app.js')
field('手動コピー時の案内',value='文面を選択しました。端末の「コピー」を使い、InstagramのDMに貼り付けてください。',source='site/app.js')
field('一般のお客様への案内','copy.secondaryAudience')
section('L','メニュー・スマホ下部のボタン・写真拡大画面')
for label,text in [('メニュー1','施工事例'),('メニュー2','対応内容'),('メニューの相談ボタン','ご相談'),('スマホ下部の補足','引渡し前の補修・継続取引<br>現場のご相談はこちら'),('スマホ下部のボタン','補修を相談する'),('写真拡大の見出し','施工写真'),('写真拡大を閉じるボタン','閉じる'),('JavaScript無効時の案内','相談文は選択してコピーできます。写真は通常の表示でご確認ください。')]:
    if label == 'スマホ下部の補足':
        field(label,'copy.mobileContactNote')
    else:
        field(label,value=text,source='scripts/build.py' if label == 'メニュー1' else 'site/template.html')
        records[-1]['text']=text.replace('<br>','\n')
section('M','写真の代替説明（通常は画像が表示できない場合等に使う文章）')
for i in range(len(data['cases']['items'])):
    field(f'事例{i+1}・補修前の説明',f'cases.items.{i}.altBefore')
    field(f'事例{i+1}・補修後の説明',f'cases.items.{i}.altAfter')

intro = '''LIBRIGHT｜掲載文 一括編集用原稿
基準版：v0.4／2026-10-31

使い方
・【A01｜…】などの項目番号と項目名は残し、その下の文章を直接書き換えてください。
・変更しない文章は、そのまま残して大丈夫です。
・削除したい項目の本文には「【削除】」と書いてください。
・改行も編集できます。注釈を付けたい場合は末尾の「追加指示」へ記入してください。
・編集したファイル全体をこのチャットへ添付するか、全文を貼り付けて「この原稿に差し替え」と送ってください。
・編集だけではLPは変わりません。受け取り後に差分を確認し、LPとプレビューへ反映します。

配置：E01とE04は冒頭のマーク欄へ移動済みです。空欄・削除済みの項目を再掲載したい場合は追加指示へ記入してください。
対象：現在の確認版の日本語の見出し・本文・ボタン等。TRC紹介、FAQ、開閉内の本文も含みます。
ロゴ内の文字、写真自体、装飾の英字・番号、制作確認用の注意表示、未掲載の料金欄は対象外です。
同じ意味の文章が別項目にもある場合は、各項目を編集してください。Bの部材名だけは同じデータを複数箇所で共用しています。

==================== 原稿ここから ====================
'''
parts=[intro]
for record in records:
    if 'section' in record:parts.append('\n──────── '+record['section']+' ────────\n')
    else:parts.append('\n【'+record['id']+'｜'+record['label']+'】\n'+(record['text'] or '【削除】')+'\n')
parts.append('\n==================== 原稿ここまで ====================\n\n【追加指示】\n（必要があれば記入してください）\n')
text='\n'.join(parts)
(ROOT/'docs/COPY_EDIT.txt').write_text(text,encoding='utf-8')
(ROOT/'design/copy-edit-map.json').write_text(json.dumps({'baseline':'v0.4','sourceSha256':hashlib.sha256((ROOT/'site/content.json').read_bytes()).hexdigest(),'fields':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
style='*{box-sizing:border-box}body{margin:0;background:#f8f7f3;color:#151515;font:16px/1.8 sans-serif}main{max-width:1000px;margin:auto;padding:28px 20px}h1{font-size:24px}p{margin:12px 0}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}button{font:inherit;padding:12px 18px;border:1px solid #151515;background:#f3c63a;color:#151515;cursor:pointer}textarea{width:100%;height:65vh;min-height:360px;padding:18px;border:1px solid #888;border-radius:0;font:16px/1.9 sans-serif;resize:vertical;background:white;color:#151515}label{display:block;font-weight:bold;margin:16px 0 8px}#status{min-height:2em}a,button,textarea{outline-offset:3px}'
js='''const editor=document.querySelector('#editor');const status=document.querySelector('#status');
document.querySelector('#save').addEventListener('click',()=>{const blob=new Blob([editor.value],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='LIBRIGHT-掲載文-編集済み.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='保存したファイルを、このチャットへ添付してください。';});
document.querySelector('#copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(editor.value);status.textContent='全文をコピーしました。このチャットへ貼り付けて送ってください。';}catch{editor.focus();editor.select();status.textContent='全文を選択しました。端末のコピー操作を使ってください。';}});'''
page='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>LIBRIGHT｜掲載文の一括編集</title><style>'+style+'</style></head><body><main><h1>LIBRIGHT｜掲載文の一括編集</h1><p>原文を直接書き換えて、編集済みの全文をまとめて送れます。項目番号は残してください。変更しない文章はそのままで大丈夫です。</p><p>編集後は「編集済み原稿を保存」を押し、そのファイルをチャットへ添付してください。自動保存・LPへの自動反映はありません。</p><div class="actions"><button id="save" type="button">編集済み原稿を保存</button><button id="copy" type="button">全文をコピー</button></div><p id="status" role="status" aria-live="polite"></p><label for="editor">掲載文の原稿（全項目を一括編集できます）</label><textarea id="editor" spellcheck="false">'+escape(text)+'</textarea></main><script>'+js+'</script></body></html>'
(ROOT/'design/copy-editor.html').write_text(page,encoding='utf-8')
print(str(sum('id' in r for r in records))+'項目の原文をTXTと一括編集HTMLへ出力しました。LPの本文は変更していません。')
