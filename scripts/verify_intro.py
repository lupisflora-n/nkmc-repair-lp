#!/usr/bin/env python3
"""Check the selected intro in the actual self-contained LP with a controlled clock."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'design/preview.html').read_text()
report={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 try:
  page=browser.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.clock.install(time=0);page.clock.pause_at(1000)
  page.set_content(html,wait_until='load')
  assert page.locator('html').get_attribute('data-intro-state')=='playing'
  assert page.locator('.intro-screen').get_attribute('data-intro-effect')=='2'
  assert page.locator('.intro-screen [data-part][transform]').count()==5
  page.clock.run_for(400)
  assert page.locator('.intro-screen [data-part][transform]').count()==5
  page.screenshot(path=str(ROOT/'qa/intro-400ms.png'))
  page.clock.run_for(420)
  assert page.locator('.intro-screen [data-part][transform]').count()==0
  page.clock.run_for(130)
  opacity=float(page.locator('.intro-screen').evaluate('(e)=>getComputedStyle(e).opacity'))
  assert 0<opacity<1,opacity
  page.clock.run_for(250)
  assert page.locator('html').get_attribute('data-intro-state')=='complete'
  assert page.locator('.intro-screen').count()==0
  assert 'intro-pending' not in (page.locator('html').get_attribute('class') or '')
  assert page.locator('h1').is_visible()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  assert not errors,errors
  report['restorationFadeAndExact1200msCompletion']=True
  page.close()
  reduced=browser.new_context(reduced_motion='reduce')
  page=reduced.new_page();page.set_content(html,wait_until='load')
  assert page.locator('html').get_attribute('data-intro-state')=='reduced-motion'
  assert page.locator('.intro-screen').count()==0
  assert page.locator('h1').is_visible();reduced.close()
  report['reducedMotionSkipsIntro']=True
  nojs=browser.new_context(java_script_enabled=False)
  page=nojs.new_page();page.set_content(html,wait_until='load')
  assert not page.locator('.intro-screen').is_visible()
  assert page.locator('h1').is_visible();nojs.close()
  report['noJavaScriptStillShowsPage']=True
  page=browser.new_page();page.set_content(html,wait_until='load')
  page.keyboard.press('Tab')
  assert page.locator('html').get_attribute('data-intro-state')=='skipped'
  assert page.locator('.intro-screen').count()==0;page.close()
  report['keyboardCanSkipWithoutBlockingPage']=True
  page=browser.new_page();page.clock.install(time=0);page.clock.pause_at(1000);page.set_content(html,wait_until='load')
  page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:false}));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}));")
  assert page.locator('html').get_attribute('data-intro-state')=='restored'
  assert page.locator('.intro-screen').count()==0;page.close()
  report['backForwardRestoreCannotKeepOverlay']=True
 finally:browser.close()
(ROOT/'qa/intro-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
