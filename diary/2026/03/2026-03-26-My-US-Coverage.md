# 專案實作紀錄：My-US-Coverage
* **📅 日期**：2026-03-26
* **🏷️ 標籤**：`#Project` `#DevLog` `#US-Stock`

---

> 🎯 **本次進度摘要**
> 成功建立「My-US-Coverage」美股研究數據庫，平移並優化了台股專案的自動化工具鏈，支援 6,500+ 美股標的與美元財務報表。

### 🛠️ 執行細節與變更
* **新專案初始化**：
  - 建立 `Pilot_Reports/`, `scripts/`, `themes/`, `network/` 目錄結構。
  - 抓取並整併 NASDAQ、NYSE、AMEX 交易所的上市清單，產生 `tickers_us.csv` (6,500+ 標的)。
* **核心工具鏈平移 (US Adaptation)**：
  - 📄 `scripts/utils.py`：適應美股代號（無後綴）、美元貨幣單位與英文 Wiki 標籤。
  - 📄 `scripts/update_financials.py` & `add_ticker.py`：實現自動抓取美股 3 年年報與 4 季季報。
  - 📄 `scripts/build_themes.py`：定義美股專屬主題 (Magnificent 7, Semi CapEx, AI Cloud)。
  - 📄 `scripts/audit_batch.py`：建立美股高品質報告審核機制。
* **試點報告生成**：
  - 完成 `AAPL (Apple)` 與 `NVDA (NVIDIA)` 報告，確認財務單位為 Million USD。

### 🚨 問題與解法 (Troubleshooting)
> 🐛 **遇到困難**：美股代號不帶 `.TW` 後綴，初版腳本在正則表達式解析時會混淆。
> 💡 **解決方案**：重寫 `utils.py` 中的 `find_ticker_files` 與 `RE` 邏輯，僅匹配 `[A-Z0-9\.]+` 格式的代號。

### ⏭️ 下一步計畫 (Next Steps)
- [ ] 完成 Batch 1 剩餘 8 隻標的 (MSFT, GOOGL, AMZN, META, TSLA, ASML, TSM, AVGO)。
- [ ] 執行 `update_enrichment.py` 補充繁體中文業務說明。
- [ ] 運行 `build_network.py` 產生美股供應鏈關係圖。
- [ ] 同步至 GitHub 以確保資料安全。
