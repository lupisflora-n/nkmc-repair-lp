#!/usr/bin/env python3
"""Create 1.2-second mark-assembly demos and chat-friendly GIF/storyboards."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, re, subprocess, tempfile, shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design/previews/mark-effects-12s'
OUT.mkdir(parents=True,exist_ok=True)
svg=(ROOT/'site/assets/brand/libright/logos/svg/symbol-color.svg').read_text()
svg=re.sub(r'<\?xml.*?\?>','',svg).replace('width="530" height="445"','class="mark-svg"')
NAMES=['５つのパーツが合体','割れた形が元に戻る','筆が色を仕上げる','折りたたみから立体へ','回転してぴたりと整列','線画からマークへ','色を取り戻す','四角い素材から変身','筆と補修面が組み上がる','小さな欠片から完成']
DESCS=['黒・黄・赤の部品が四方から集まる。','離れた部品が継ぎ目を合わせて復元する。','補修面に黄色が広がり、筆が最後に収まる。','細く畳まれた面が開き、マークになる。','少し回転した部品が向きをそろえて合体。','マーク自身の輪郭線が描かれ、色が入る。','無彩色のマークが、本来の色へ変わる。','四角い素材が伸び、正式マークの形へ変わる。','筆先と軸が先に合体し、補修面が続く。','小さく散った欠片が集まり、完成形へ育つ。']
css='''*{box-sizing:border-box}body{margin:0;color:#151515;background:#fff;font:14px/1.6 sans-serif}header{padding:12px 16px}header h1{font-size:20px;margin:0}header p{font-size:12px;margin:3px 0}main{padding:0 12px 12px;display:grid;gap:8px}.card{padding:8px;border:1px solid #ddd;background:white}.card h2{font-size:16px;margin:0 0 4px}.card>p{font-size:12px;color:#666;margin:4px 0}.stage{height:180px;position:relative;overflow:hidden;border:1px solid #e8e7e1}.sample-page{position:absolute;inset:0;padding:14px 18px;background:#fff}.sample-page small{font-weight:800}.sample-page strong{display:block;font-size:17px;margin-top:15px}.sample-page p{font-size:10px}.sample-page b{font-size:10px;background:#f3c63a;padding:7px 13px}.intro{position:absolute;inset:0;background:#fff;display:flex;align-items:center;justify-content:center}.mark-svg{width:180px;height:auto;overflow:visible}button{font:inherit;min-height:44px;padding:8px 16px;background:#151515;color:white;border:0;cursor:pointer;margin-top:8px}.outline path{fill:none!important;stroke:#151515;stroke-width:3}.board main{display:block}.board .row{padding:8px 0;border-top:1px solid #ddd}.board .row>h2{font-size:18px;margin:0 0 5px}.board .frames{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.board .stage{height:155px}.board .mark-svg{width:145px}.board .sample-page{padding:10px}.board .sample-page strong{font-size:12px;margin-top:12px}.board .sample-page small,.board .sample-page p,.board .sample-page b{font-size:8px}.board .time{display:block;font-size:12px;color:#666}.playing-note{font-size:12px;color:#555}'''
script=r'''
const originals=new Map();
const clamp=(v)=>Math.min(1,Math.max(0,v));
const ease=(v)=>{v=clamp(v);return 1-Math.pow(1-v,3);};
function init(stage){
 const svg=stage.querySelector('svg');
 const group=svg.querySelector('g');
 const paths=[...group.querySelectorAll('path')];
 originals.set(stage,paths.map(path=>({d:path.getAttribute('d'),box:path.getBBox(),fill:path.getAttribute('fill')})));
 const outline=group.cloneNode(true);outline.classList.add('outline');outline.querySelectorAll('path').forEach(path=>{path.removeAttribute('data-part');path.removeAttribute('transform');});svg.appendChild(outline);stage.outline=outline;
}
function show(stage,time){
 const mode=Number(stage.dataset.mode), p=ease(time/.8), fade=time>=1.2?1:clamp((time-.9)/.3);
 const paths=[...stage.querySelector('svg>g:not(.outline)').querySelectorAll('path')];
 const old=originals.get(stage);
 stage.querySelector('.intro').style.opacity=1-fade;
 stage.querySelector('.sample-page').style.opacity=fade;
 stage.outline.style.opacity=0;
 paths.forEach((path,i)=>{
  const box=old[i].box,cx=box.x+box.width/2,cy=box.y+box.height/2;
  let q=p,dx=0,dy=0,sx=1,sy=1,rot=0,opacity=1;
  path.setAttribute('d',old[i].d);path.style.fill=old[i].fill;path.style.filter='none';
  const offsets=[[-155,15],[95,-130],[35,110],[-100,-80],[120,-90]];
  if(mode===1){dx=offsets[i][0]*(1-p);dy=offsets[i][1]*(1-p);}
  if(mode===2){dx=[-40,35,20,-25,25][i]*(1-p);dy=[35,-30,35,-35,-35][i]*(1-p);rot=[-5,5,-3,9,-9][i]*(1-p);}
  if(mode===3){q=ease((time-[0,.18,.3,.38,.38][i])/.36);if(i===1)sy=q;if(i===2)sx=q;if(i>=3){dx=-120*(1-q);dy=40*(1-q);}opacity=i<3?1:q;}
  if(mode===4){q=ease((time-i*.025)/.55);sx=i===1?.03+.97*q:1;sy=i===2?.03+.97*q:1;if(i===0)sy=.1+.9*q;if(i>=3){rot=-55*(1-q);opacity=q;}}
  if(mode===5){dx=offsets[i][0]*(1-p)*.6;dy=offsets[i][1]*(1-p)*.6;rot=[-70,70,-60,85,85][i]*(1-p);}
  if(mode===6){stage.outline.style.opacity=1-ease((time-.45)/.3);const length=stage.outline.querySelectorAll('path')[i].getTotalLength();const line=stage.outline.querySelectorAll('path')[i];line.style.strokeDasharray=length;line.style.strokeDashoffset=length*(1-ease(time/.5));opacity=ease((time-.4)/.4);}
  if(mode===7){path.style.filter=`grayscale(${1-p})`;sx=sy=.9+.1*p;}
  if(mode===8){let n=0;const coords=[...old[i].d.matchAll(/[0-9.-]+/g)].map(x=>Number(x[0]));path.setAttribute('d',old[i].d.replace(/[0-9.-]+/g,()=>{const j=n++, k=Math.floor(j/2)%4, start=j%2?[158,158,202,202][k]:[208,252,252,208][k];return start+(coords[j]-start)*p;}));}
  if(mode===9){q=ease((time-(i>=3?0:.15+i*.08))/.42);dx=(i>=3?60:-90)*(1-q);dy=(i>=3?-65:60)*(1-q);opacity=q;}
  if(mode===10){dx=offsets[i][0]*(1-p);dy=offsets[i][1]*(1-p);sx=sy=.04+.96*p;rot=[-90,60,-80,130,-100][i]*(1-p);}
  if(time>=.8){path.removeAttribute('transform');path.setAttribute('d',old[i].d);path.style.opacity=1;path.style.fill=old[i].fill;path.style.filter='none';}
  else{path.setAttribute('transform',`translate(${dx} ${dy}) translate(${cx} ${cy}) rotate(${rot}) scale(${sx} ${sy}) translate(${-cx} ${-cy})`);path.style.opacity=opacity;}
 });
}
window.effectShow=show;window.effectInit=init;
document.querySelectorAll('.stage').forEach(stage=>{init(stage);show(stage,0);});
document.querySelectorAll('[data-play]').forEach(button=>button.onclick=()=>{const stage=document.getElementById(button.dataset.play);const start=performance.now();function tick(now){const t=Math.min(1.2,(now-start)/1000);show(stage,t);if(t<1.2)requestAnimationFrame(tick);}requestAnimationFrame(tick);});
'''
def stage(i,ident):
 return f'<div class="stage" data-mode="{i}" id="{ident}"><div class="sample-page"><small>LIBRIGHT　リブライト</small><strong>引渡し前のキズ補修から、<br>急な依頼のご相談まで。</strong><p>千葉県を中心に関東エリア対応</p><b>現場の補修を相談する</b></div><div class="intro">{svg}</div></div>'
def page(body,title,klass=''):
 return '<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+title+'</title><style>'+css+'</style></head><body class="'+klass+'"><header><h1>'+title+'</h1><p>0〜0.8秒：マークの組立・変化　0.8〜0.9秒：完成　0.9〜1.2秒：ページへ</p></header><main>'+body+'</main><script>'+script+'</script></body></html>'
cards=''.join(f'<article class="card" data-item="{i}"><h2>{i}. {name}</h2><p>{DESCS[i-1]}</p>'+stage(i,f'stage-{i}')+f'<button type="button" data-play="stage-{i}">1.2秒で再生</button></article>' for i,name in enumerate(NAMES,1))
html=page(cards,'LIBRIGHT｜マークが変化する演出10案（新版）')
(ROOT/'design/mark-effect-options.html').write_text(html,encoding='utf-8')
report=[]
with tempfile.TemporaryDirectory(prefix='libright-mark-motion-') as folder:
 tmp=Path(folder)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  try:
   for start,end in [(1,5),(6,10)]:
    label=f'{start:02}-{end:02}'
    web=browser.new_page(viewport={'width':480,'height':1300},device_scale_factor=1)
    web.set_content(html,wait_until='load')
    web.add_style_tag(content='.card>p,.card>button{display:none!important}')
    web.evaluate('''({start,end})=>{document.querySelectorAll('.card').forEach(card=>{const i=Number(card.dataset.item);if(i<start||i>end)card.remove();});document.querySelector('h1').textContent=`新版｜候補 ${start}〜${end}・1.2秒`;}''',{'start':start,'end':end})
    height=web.evaluate('document.documentElement.scrollHeight');height+=height%2
    web.set_viewport_size({'width':480,'height':height})
    frames=tmp/label;frames.mkdir()
    for frame in range(36):
     t=min(frame/20,1.2)
     web.evaluate('(t)=>document.querySelectorAll(".stage").forEach(stage=>effectShow(stage,t))',t)
     web.screenshot(path=str(frames/f'{frame:03}.png'))
    assert web.locator('.intro').first.evaluate('(e)=>getComputedStyle(e).opacity')=='0'
    # Every original path is exactly restored before the page fade.
    web.evaluate('document.querySelectorAll(".stage").forEach(stage=>effectShow(stage,.8))')
    assert web.locator('svg>g:not(.outline) path[transform]').count()==0
    web.close()
    gif=OUT/f'LIBRIGHT-mark-12s-{label}.gif'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','20','-i',str(frames/'%03d.png'),'-filter_complex','split[a][b];[a]palettegen=max_colors=112[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',str(gif)],check=True)
    shutil.copy2(gif,Path('/workspace')/gif.name)
    # Four exact stages for users whose chat client displays GIFs as a still image.
    rows=''
    for i in range(start,end+1):
     row=''.join('<div><span class="time">'+f'{t:.1f}秒</span>'+stage(i,f'board-{i}-{j}')+'</div>' for j,t in enumerate([0,.4,.8,1.2]))
     rows+=f'<section class="row"><h2>{i}. {NAMES[i-1]}</h2><div class="frames">'+row+'</div></section>'
    board=browser.new_page(viewport={'width':960,'height':1200},device_scale_factor=1)
    board.set_content(page(rows,f'新版｜候補 {start}〜{end} コマ送り','board'),wait_until='load')
    board.evaluate('document.querySelectorAll(".row").forEach(row=>row.querySelectorAll(".stage").forEach((stage,i)=>effectShow(stage,[0,.4,.8,1.2][i])))')
    poster=OUT/f'LIBRIGHT-mark-12s-{label}-storyboard.png'
    board.screenshot(path=str(poster),full_page=True);board.close()
    shutil.copy2(poster,Path('/workspace')/poster.name)
    report.append({'options':label,'gif':gif.name,'bytes':gif.stat().st_size,'storyboard':poster.name,'transitionSeconds':1.2,'gifLoopSeconds':1.8})
    print(json.dumps(report[-1],ensure_ascii=False),flush=True)
  finally:browser.close()
(OUT/'media-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'docs/EFFECT_OPTIONS_V2.txt').write_text('新版：マークそのものが変化する演出10案\n全体1.2秒。0-.8秒：組立や変化、.8-.9秒：完成、.9-1.2秒：ページへフェード。\nユーザー指示により演出中のパーツ分解・移動・形状変化を許容。完成時は正式SVGの形と配色に戻す。元SVGと施工写真は変更しない。\n旧0.7秒案に代わる選択用の新版。実LPはまだ選択待ち。\n\n'+'\n'.join(f'{i}. {name}：{DESCS[i-1]}' for i,name in enumerate(NAMES,1))+'\n',encoding='utf-8')
