#!/usr/bin/env python3
"""Create a text review companion from the actual rendered preview, without images."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


class MainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.output = []
        self.markdown = []
        self.stack = []
        self.allowed = {'section', 'div', 'h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'summary', 'figcaption', 'span', 'strong'}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'main':
            self.active = True
            return
        if not self.active:
            return
        if tag == 'br':
            self.output.append('<br>')
            self.markdown.append('\n')
        elif tag == 'textarea':
            self.output.append('<pre>')
        elif tag in self.allowed:
            identifier = ' id="' + escape(attrs['id'], quote=True) + '"' if attrs.get('id') else ''
            self.output.append('<' + tag + identifier + '>')
            if tag in ('h1', 'h2', 'h3'):
                self.markdown.append('\n\n' + '#' * (int(tag[1]) + 1) + ' ')
            elif tag == 'li':
                self.markdown.append('\n- ')
            elif tag == 'summary':
                self.markdown.append('\n\n**')
            elif tag == 'textarea':
                self.markdown.append('\n\n')
            elif tag == 'p':
                self.markdown.append('\n\n')
        elif tag in ('a', 'button'):
            self.output.append('<p class="action">')
            self.markdown.append('\n\n【ボタン・リンク】')
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'main':
            self.active = False
            return
        if not self.active:
            return
        if tag == 'textarea':
            self.output.append('</pre>')
        elif tag in self.allowed:
            self.output.append('</' + tag + '>')
        elif tag in ('a', 'button'):
            self.output.append('</p>')
        if tag == 'summary':
            self.markdown.append('**')
        if tag in ('section', 'summary', 'figcaption', 'h1', 'h2', 'h3', 'div', 'li', 'a', 'button', 'textarea', 'span', 'strong', 'p'):
            self.markdown.append('\n\n')

    def handle_data(self, text):
        if self.active and text.strip():
            self.output.append(escape(text))
            self.markdown.append(text)


parser = MainText()
parser.feed((ROOT / 'design/preview.html').read_text(encoding='utf-8'))
body = re.sub(r'<p class="action"></p>', '', ''.join(parser.output))
md = ''.join(parser.markdown)
md = re.sub(r'【ボタン・リンク】\s*(?=補修[前後])', '', md)
md = re.sub(r'\n- \s*\n', '\n', md)
md = re.sub(r'\n{3,}', '\n\n', md)
intro = '文章確認版 v0.2｜2026-10-30。LP本体から本文を抽出。写真は省略し、折りたたみ内の文章もすべて表示しています。掲載順に読み進められます。'
notes = '新しい原点の物語・現場での姿勢・施工の流れはnさんの確認前の案です。TRC紹介は、関係・紹介文・公式リンク・掲載条件の確認後に「現場で大切にすること」の次へ追加します。現在のLPには表示していません。料金も確認後に差し込みます。'
style = 'body{margin:0;background:#f8f7f3;color:#151515;font:16px/2 sans-serif}header,main,footer{max-width:820px;margin:auto;padding:28px 24px}header{border-bottom:5px solid #f3c63a}section{padding:28px 0;border-top:1px solid #ddd}h1{font-size:26px}h2{font-size:23px}h3{font-size:19px}summary{font-weight:bold;margin-top:20px}p{margin:14px 0}pre{white-space:pre-wrap;background:white;padding:20px;font:inherit}.action{border-left:4px solid #f3c63a;padding-left:12px}footer{border-top:1px solid #ddd;font-size:14px}section{counter-increment:section}section>div:first-child:before,section>span:first-child:before{content:counter(section,decimal-leading-zero) " / ";font-weight:bold;color:#c54136}div{overflow-wrap:anywhere}@media print{body{background:white}section{break-inside:avoid}}'
page = '<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>LIBRIGHT 文章確認版 v0.2</title><style>' + style + '</style></head><body><header><h1>LIBRIGHT｜LPの文章確認版</h1><p>' + intro + '</p></header><main>' + body + '</main><footer><h2>制作上の確認事項</h2><p>' + notes + '</p></footer></body></html>'
(ROOT / 'design/copy-review.html').write_text(page, encoding='utf-8')
(ROOT / 'docs/COPY_DRAFT.md').write_text('# LIBRIGHT LP 文章確認版 v0.2\n\n' + intro + '\n\n' + md + '\n\n## 制作上の確認事項\n\n' + notes + '\n', encoding='utf-8')
print('文章確認版: design/copy-review.html / docs/COPY_DRAFT.md')
