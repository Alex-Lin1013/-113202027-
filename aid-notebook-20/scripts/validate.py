import json,re,datetime,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];errors=[]
def ck(ok,msg):
 if not ok:errors.append(msg)
def date(v,msg):
 if v is not None:
  try:datetime.date.fromisoformat(v)
  except (ValueError,TypeError):errors.append('日期錯誤 '+msg)
def main():
 d=json.loads((ROOT/'data/scholarships.json').read_text(encoding='utf-8'));seen=set();fields=set(json.loads((ROOT/'templates/scholarship.json').read_text(encoding='utf-8')))
 ck(len(d['records'])>=20,'未達20筆')
 for x in d['records']:
  k=x['id'];ck(bool(re.fullmatch('[a-z0-9-]+',k)) and k not in seen,'ID無效/重複 '+k);seen.add(k);ck(fields<=set(x),'缺欄位 '+k)
  ck('急難濟助' not in x['name'] and '轉介' not in x['name'],'不以急難轉介湊數 '+k)
  ck(x['reviewStatus'] in ['source-reviewed','verified'],'公開資料不能是未整理草稿 '+k)
  if x['reviewStatus']=='verified':ck(bool(x['verifiedBy']) and bool(x['verifiedAt']),'未人工確認 '+k)
  for key in ['name','organization','period','amount','method']:ck(bool(x[key]),'空欄位 '+key+k)
  ck(bool(x['eligibility']) and bool(x['documents']) and bool(x['sources']),'缺主要內容 '+k)
  ck(len({z['id'] for z in x['documents']})==len(x['documents']),'文件ID重複 '+k)
  for s in x['sources']:
   u=urlparse(s['url']);ck(u.scheme in ['http','https'] and bool(u.netloc),'來源URL錯誤 '+k);date(s['readDate'],k)
  for key in ['deadline','schoolDeadline','verifiedAt']:date(x[key],k)
  ck(not x['schoolDeadline'] or bool(x['referenceSchool']),'校內期限缺學校 '+k)
 html=(ROOT/'index.html').read_text(encoding='utf-8')
 class P(HTMLParser):
  inside=False;content=''
  def handle_starttag(self,t,attrs):
   a=dict(attrs)
   if t=='script' and a.get('id')=='catalog':self.inside=True
  def handle_data(self,data):
   if self.inside:self.content+=data
  def handle_endtag(self,t):
   if t=='script':self.inside=False
 p=P();p.feed(html);embedded=json.loads(p.content);ck(embedded==d,'index內嵌資料與JSON不同步，請先build.py')
 for f in ['AGENTS.md','README.md','data/sources.csv','assets/app.js','assets/style.css','templates/page.html']:ck((ROOT/f).is_file(),'缺檔案 '+f)
 print(f"JSON={len(d['records'])}筆；index內嵌={len(embedded['records'])}筆；錯誤={len(errors)}項")
 for e in errors:print('ERROR:',e)
 return bool(errors)
try:sys.exit(main())
except (KeyError,ValueError,TypeError,OSError) as e:print('ERROR:',e);sys.exit(1)
