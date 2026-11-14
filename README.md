# 助學小本本｜20筆實際預載版

## 直接開始
- 本機：解壓縮後雙擊index.html，首頁即顯示20筆，無需啟動Python或另上傳資料。
- Colab：本次.ipynb已內嵌整個專案，依序跑展開、檢查、預覽即可，不用舊ZIP。
- 可以直接另下載本次單獨index.html看網站，但正式GitHub請上傳完整專案，讓AGENTS.md及來源可讀。

## 這次怎麼算20筆
20項不同獎學金/助學金，不含急難轉介，不以同獎換年度湊數。鄭豐喜本人與家庭子女是兩個不同資格的方案。包含校內生活助學及政府勵學，亦包含台泥2025歷年；不代表現在都在受理。
每筆有資格、文件、金額、方法、主辦背景、建議、來源與日期說明。source-reviewed是AI依官方/學校來源整理，不冒充人工確認。申請表從真實來源入口取得，不造20個下載附件。
資料總數=JSON records長度=index內嵌records長度=首頁未篩選卡片數，由驗證及瀏覽器檢查實測。來源索引在data/sources.csv。

## 功能
列表搜尋/類型/歷年/常設/參考校日/收藏，資料詳情、文件進度、列印、問題帶入筆記、新增編輯刪除、JSON備份預覽與還原。五個共用視圖由單一頁面路由，不複製20份HTML。
主辦截止和參考校內截止分開，後者只適用標示學校。常設週期、核發期間不算受理期。台泥2025明標歷年。林熊徵採主辦115新規不需推薦函；金融總會不同轉知日期有差異，保留提示不亂定全台期限。

## 新增第21筆
先讀AGENTS.md與templates/scholarship.json。只改data/scholarships.json，再執行：
```
python scripts/build.py
python scripts/validate.py
```
index.html與sources.csv是生成成果，不直接修改。沒有Python的使用者可請AI重建完整檔案。
要跑瀏覽器測試需安裝playwright及chromium後執行scripts/browser-test.py；一般瀏覽不需安裝。

## 隱私及限制
筆記/收藏/文件勾選僅localStorage，不加密、不同步、不上傳。不同本機路徑/Colab/正式網址可能分開儲存，請先匯出。不要填證號帳戶收入或上傳證件。備份不要放GitHub。
資料核對日2026-11-14。未逐份下載全部空白表格，亦未由使用者確認個人資格。程式測試不表示公告獲官方認證。

## GitHub Pages
1. 建立Public Repository。
2. 上傳本專案內檔案至根目錄，不是ZIP，也不要多包一層。
3. 確認根目錄有index.html與AGENTS.md。
4. Settings → Pages → Deploy from a branch → main → /(root) → Save。
5. 用GitHub實際給的網址無痕測試，再填docs/submission.md。
Colab是暫時預覽，還不算正式發布。不要提供GitHub密碼/驗證碼/權杖。

## 原創及AI揭露
需求與設計取捨來自提案人，AI協助規則、程式、公開資料整理與測試；不編造申請成功或人工審核。真實測試見docs/test-report.md。GitHub及公開網址尚待使用者操作。
