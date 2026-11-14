import json,csv,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/scholarships.json').read_text(encoding='utf-8'))
page=(ROOT/'templates/page.html').read_text(encoding='utf-8')
for k,v in [('__CSS__',(ROOT/'assets/style.css').read_text(encoding='utf-8')),('__DATA__',json.dumps(d,ensure_ascii=False).replace(chr(60),chr(92)+'u003c')),('__JS__',(ROOT/'assets/app.js').read_text(encoding='utf-8'))]:page=page.replace(k,v)
(ROOT/'index.html').write_text(page,encoding='utf-8')
b=io.StringIO();w=csv.writer(b);w.writerow(['編號','ID','名稱','主辦','期別','金額','主辦截止','參考校內日','適用學校','來源單位','來源網址','核對層級'])
for i,x in enumerate(d['records'],1):
 for s in x['sources']:w.writerow([i,x['id'],x['name'],x['organization'],x['period'],x['amount'],x['deadline'],x['schoolDeadline'],x['referenceSchool'],s['publisher'],s['url'],x['reviewStatus']])
(ROOT/'data/sources.csv').write_text('\ufeff'+b.getvalue(),encoding='utf-8')
print('已實際內嵌',len(d['records']),'筆資料至index.html')
