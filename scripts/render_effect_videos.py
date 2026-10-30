#!/usr/bin/env python3
"""Render the existing effect demos to mobile-friendly media without changing LP assets."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'design/previews/effects'
OUT.mkdir(parents=True, exist_ok=True)
source = (ROOT / 'design/effect-options.html').read_text(encoding='utf-8')
css = '''html,body{width:480px!important;margin:0!important;background:#fff!important}header{padding:12px 16px!important}header h1{font-size:20px!important;margin:0!important}header p{font-size:12px!important;margin:4px 0!important}main.grid{display:grid!important;grid-template-columns:1fr!important;gap:8px!important;padding:0 12px 12px!important}.card{padding:8px!important;border:1px solid #ddd!important}.card h2{font-size:16px!important;margin:0 0 5px!important}.card>p,.card>button{display:none!important}.stage{height:164px!important}.sample-page{padding:10px 20px!important}.sample-page strong{font-size:15px!important;margin-top:12px!important}.sample-page p{margin:5px 0!important}.mark{width:75px!important}'''
report=[]
with tempfile.TemporaryDirectory(prefix='libright-effects-') as temp:
    tmp=Path(temp)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for start,end in [(1,5),(6,10)]:
                label=f'{start:02}-{end:02}'
                page=browser.new_page(viewport={'width':480,'height':1200},device_scale_factor=1,reduced_motion='no-preference')
                page.set_content(source,wait_until='load')
                page.add_style_tag(content=css)
                page.evaluate('''({start,end})=>{document.querySelector('header').innerHTML=`<h1>LIBRIGHT｜演出 ${start}〜${end}</h1><p>各演出は0.7秒。マーク出現 → ページへフェード</p>`;document.querySelectorAll('.card').forEach((card,index)=>{if(index+1<start || index+1>end) card.remove();});document.querySelectorAll('.stage').forEach(stage=>stage.classList.add('run'));window.effectAnimations=document.getAnimations();window.effectAnimations.forEach(animation=>{animation.pause();animation.currentTime=0;});}''',{'start':start,'end':end})
                page.wait_for_function('Array.from(document.querySelectorAll("img")).every(i=>i.complete && i.naturalWidth>0)')
                height=page.evaluate('document.documentElement.scrollHeight')
                height += height % 2
                page.set_viewport_size({'width':480,'height':height})
                frame_dir=tmp/label;frame_dir.mkdir()
                for frame in range(54):
                    milliseconds=min(frame/30,.7)*1000
                    page.evaluate('(time)=>window.effectAnimations.forEach(animation=>animation.currentTime=time)',milliseconds)
                    page.screenshot(path=str(frame_dir/f'{frame:03}.png'),animations='allow')
                assert page.locator('.intro').first.evaluate('(e)=>getComputedStyle(e).opacity')=='0'
                assert page.locator('.sample-page').first.evaluate('(e)=>getComputedStyle(e).opacity')=='1'
                page.close()
                cycle=tmp/f'{label}.mp4'
                common=['ffmpeg','-hide_banner','-loglevel','error','-y']
                subprocess.run(common+['-framerate','30','-i',str(frame_dir/'%03d.png'),'-c:v','libx264','-preset','medium','-crf','20','-profile:v','baseline','-level:v','3.1','-pix_fmt','yuv420p','-movflags','+faststart',str(cycle)],check=True)
                video=OUT/f'LIBRIGHT-effects-{label}.mp4'
                subprocess.run(common+['-stream_loop','2','-i',str(cycle),'-c','copy','-movflags','+faststart',str(video)],check=True)
                gif=OUT/f'LIBRIGHT-effects-{label}.gif'
                subprocess.run(common+['-i',str(cycle),'-filter_complex','fps=20,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',str(gif)],check=True)
                probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
                stream=probe['streams'][0]
                assert stream['codec_name']=='h264' and stream['pix_fmt']=='yuv420p'
                assert abs(float(probe['format']['duration'])-5.4)<.1
                report.append({'effects':label,'video':video.name,'gif':gif.name,'width':stream['width'],'height':stream['height'],'duration':probe['format']['duration'],'videoBytes':video.stat().st_size,'gifBytes':gif.stat().st_size})
                print(json.dumps(report[-1],ensure_ascii=False),flush=True)
        finally:
            browser.close()
(OUT/'media-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
