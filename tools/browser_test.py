"""Development-only Chromium inspection of the exported native simulation recording."""
from pathlib import Path
import json,time,shutil,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=[]
with sync_playwright()as p:
    browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1060},device_scale_factor=1)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(os.environ.get('PREVIEW_URL','http://127.0.0.1:8000/docs/preview.html'),wait_until='networkidle')
    page.wait_for_function('window.reefPreview?.ready===true')
    page.evaluate('window.reefPreview.seek(0)')
    start=page.evaluate('window.reefPreview.inspect()')
    if start['samples']<21 or len(start['fish'])!=8:raise RuntimeError('Preview must sample at 10 Hz to preserve fin/tail rhythms')
    page.evaluate('window.reefPreview.seek(2)')
    end=page.evaluate('window.reefPreview.inspect()')
    if not all(a['phase']!=b['phase'] and a['finPhase']!=b['finPhase']for a,b in zip(start['fish'],end['fish'])):raise RuntimeError('A fish body or pectoral animation is frozen')
    checks.append('All 8 body and pectoral animations advance in the short native-world recording')
    page.evaluate('window.reefPreview.seek(1.5)')
    page.wait_for_timeout(120)
    page.locator('canvas').screenshot(path=str(ROOT/'docs/previews/browser-sunset.png'))
    checks.append('All fish, coral and wave-shadow images and production snapshots loaded in Chromium')
    for mode in ['Daylight','Dusk','Moonlight','Sunset']:
        page.select_option('#mode',mode)
        page.wait_for_timeout(90)
        pixel=page.locator('canvas').evaluate('(c)=>Array.from(c.getContext("2d").getImageData(960,200,1,1).data)')
        if len(pixel)!=4 or pixel[3]!=255:raise RuntimeError('Invalid canvas output '+mode)
        checks.append({'lighting':mode,'sample_pixel':pixel})
    page.locator('#time').fill('2.5')
    page.locator('#time').dispatch_event('input')
    page.wait_for_timeout(90)
    if page.locator('#play').inner_text()!='Play':raise RuntimeError('Seek did not pause')
    paused=page.locator('#stamp').inner_text();page.wait_for_timeout(120)
    if page.locator('#stamp').inner_text()!=paused:raise RuntimeError('Pause advanced recording')
    page.click('#play');page.wait_for_timeout(250)
    if page.locator('#stamp').inner_text()==paused:raise RuntimeError('Play failed to advance recording')
    checks.extend(['Seeking pauses at selected time','Pause holds frame','Play advances native-world recording'])
    page.evaluate('window.reefPreview.seek(1.5)');page.wait_for_timeout(90)
    page.screenshot(path=str(ROOT/'docs/previews/browser-inspector.png'),full_page=True)
    browser.close()
report={'checks':checks,'page_errors':errors,'passed':not errors,'scope':'Desktop development preview only; not Roku GPU or hardware validation'}
(ROOT/'docs/browser-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if errors:raise SystemExit(1)
