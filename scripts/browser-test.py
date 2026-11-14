import asyncio,json,threading,functools,http.server,tempfile,sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
async def main():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT.parent)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/{ROOT.name}/index.html'
 results=[];errors=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,args=['--no-sandbox']);context=await browser.new_context(viewport={'width':1365,'height':1000},accept_downloads=True);page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  async def ck(name,condition):
   assert condition,name
   results.append(name)
  await page.goto(url);await ck('首頁實際20張卡片',await page.locator('.card').count()==20)
  await ck('JSON內嵌及DOM數量一致',await page.evaluate('AID_TEST.count()')==20 and await page.locator('#loaded').inner_text()=='20' and await page.locator('#shown').inner_text()=='20')
  await page.locator('#search').fill('中低收');await ck('資格全文搜尋',0<await page.locator('.card').count()<20)
  await page.locator('#search').fill('不可能存在xyz');await ck('無結果提示',await page.locator('.empty').count()==1)
  await page.locator('#search').fill('');await page.select_option('#category','企業培育');await ck('企業分類2筆',await page.locator('.card').count()==2)
  await page.select_option('#category','all');await page.select_option('#scope','standing');await ck('常設4筆',await page.locator('.card').count()==4)
  await page.select_option('#scope','all');await page.locator('.card').first.get_by_role('button',name='收藏',exact=True).click();await page.reload();await page.select_option('#scope','saved');await ck('收藏持續',await page.locator('.card').count()==1)
  await page.locator('.card').first.get_by_role('link',name='看資格與文件 →').click();await page.locator('.check input').first.check();await page.reload();await ck('勾選持續',await page.locator('.check input').first.is_checked())
  await page.get_by_role('button',name='記下要問的問題').click();await page.locator('#note-form').wait_for();await ck('問題帶入筆記',len(await page.locator('#text').input_value())>0)
  await page.locator('#title').fill('測試筆記');await page.locator('#text').fill('<img src=x onerror=alert(1)>文字');await page.get_by_role('button',name='存進小本本').click();await page.reload();await ck('筆記持續',await page.locator('.note').count()==1);await ck('文字不作HTML',await page.locator('.note img').count()==0 and '<img' in await page.locator('.note-body').inner_text())
  await page.get_by_role('button',name='編輯',exact=True).click();await page.locator('#text').fill('編輯後');await page.get_by_role('button',name='存進小本本').click();await ck('編輯不新增',await page.locator('.note').count()==1 and await page.locator('.note-body').inner_text()=='編輯後')
  async with page.expect_download() as info:await page.locator('#export').click()
  download=await info.value
  with tempfile.TemporaryDirectory() as temp:
   f=Path(temp)/'backup.json';await download.save_as(f);backup=f.read_bytes();v=json.loads(backup);await ck('完整備份',len(v['notes'])==1 and len(v['saved'])==1 and len(v['checks'])==1)
   await page.locator('#file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{bad'});await ck('錯誤匯入不刪資料','未執行' in await page.locator('#status').inner_text() and await page.locator('.note').count()==1)
   await page.locator('#file').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':backup});await ck('匯入先預覽',await page.locator('#preview').is_visible());await page.locator('#cancel-import').click();await ck('取消不覆蓋',not await page.locator('#preview').is_visible() and await page.locator('.note').count()==1)
   page.once('dialog',lambda d:d.accept());await page.get_by_role('button',name='刪除此筆').click();await ck('刪除單筆',await page.locator('.note').count()==0)
   await page.locator('#file').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':backup});page.once('dialog',lambda d:d.accept());await page.locator('#restore').click();await ck('還原備份',await page.locator('.note').count()==1)
  data=json.loads((ROOT/'data/scholarships.json').read_text(encoding='utf-8'))
  for d in data['records']:
   await page.goto(url+'#detail/'+d['id']);await page.locator('.check').first.wait_for();await ck('詳情與文件 '+d['id'],await page.locator('h1').inner_text()==d['name'] and await page.locator('.check').count()==len(d['documents']))
  await page.goto(url+'#detail/no-such-id');await ck('未知ID提示','找不到' in await page.locator('#app').inner_text())
  for view in ['guide','about','notes','list']:
   await page.goto(url+'#'+view);await ck('視圖 '+view,await page.locator('h1').count()==1)
  for width in [320,390]:
   await page.set_viewport_size({'width':width,'height':844})
   for view in ['list','detail/nccu-living','notes','about','guide']:
    await page.goto(url+'#'+view);await ck(str(width)+'px無溢出 '+view,await page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  await page.goto(url);await page.keyboard.press('Tab');await ck('鍵盤主內容入口',await page.evaluate("document.activeElement.classList.contains('skip')"))
  fail=await context.new_page();await fail.add_init_script("Storage.prototype.setItem=function(){throw Error('test quota')}");await fail.goto(url+'#notes');await fail.locator('#title').fill('不清空');await fail.locator('#text').fill('失敗保留');await fail.get_by_role('button',name='存進小本本').click();await ck('失敗保留輸入','沒有存成功' in await fail.locator('#status').inner_text() and await fail.locator('#title').input_value()=='不清空');await fail.close()
  offline=await context.new_page();await offline.goto((ROOT/'index.html').as_uri());await ck('雙擊離線20筆',await offline.locator('.card').count()==20)
  logic=await page.evaluate('''() => {const A=AID_TEST;return [A.state({deadline:'2026-09-30'},'2026-11-14').key==='archive',A.state({deadline:'2026-09-30'},'2026-09-30').label==='今日截止・確認時刻',A.state({schoolDeadline:'2026-10-05'},'2026-11-14').key==='reference',A.state({},'2026-11-14').key==='standing',A.valid(A.blank()),!A.valid({version:2,notes:[{id:'x'}],checks:{}}),A.valid({version:2,notes:[],checks:{}})]}''')
  for i,condition in enumerate(logic,1):await ck('邏輯檢查 '+str(i),condition)
  await ck('沒有未捕捉JS錯誤',not errors)
  report='# 實際測試報告\n\n2026-11-14；Playwright Chromium '+browser.version+'；HTTP子路徑與file離線。\n\n'+'\n'.join('- 通過：'+x for x in results)+f'\n\n共{len(results)}項檢查通過。驗收：JSON20、內嵌20、首頁卡片20，不計急難轉介。\n\n未測真實Colab代理、GitHub Pages、實體手機、Safari/Firefox；未人工確認個人資格、未逐份下載全部表格。程式通過不代表官方認證。\n'
  (ROOT/'docs/test-report.md').write_text(report,encoding='utf-8')
  if '--screenshots' in sys.argv:
   out=ROOT.parent.parent/'output';out.mkdir(exist_ok=True);await page.set_viewport_size({'width':1365,'height':1000});await page.goto(url);await page.screenshot(path=str(out/'20筆版_實際首頁.png'))
   await page.set_viewport_size({'width':390,'height':844});await page.goto(url+'#detail/tfsr-115');await page.screenshot(path=str(out/'20筆版_手機詳情.png'))
  print(json.dumps({'checks':len(results),'actual_cards':20,'errors':errors},ensure_ascii=False));await browser.close()
 server.shutdown()
if __name__=='__main__':asyncio.run(main())
