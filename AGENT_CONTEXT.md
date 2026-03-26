# 專案上下文 (Agent Context)：My-US-Coverage

> **最後更新時間**：2026-03-26 22:00
> **更新說明**：手動更新以反映 GitHub 同步與結構清理後的狀態

---

## 🎯 1. 專案目標 (Project Goal)
* **核心目的**：建立覆蓋所有美股上市公司的股票研究資料庫（NYSE, NASDAQ, AMEX），架構參考 My-TW-Coverage 專案。
* _完整說明見 [README.md](README.md)_

## 🛠️ 2. 技術棧與環境 (Tech Stack & Environment)
* **語言**: Python 3.x
* **核心依賴**: `yfinance`, `pandas`, `requests`
* **資料來源**: DataHub (NASDAQ/NYSE listings), Yahoo Finance

## 📂 3. 核心目錄結構 (Core Structure)
_(💡 AI 讀取守則：請依據此結構尋找對應檔案，勿盲目猜測路徑)_
```text
My-US-Coverage/
├── AGENT_CONTEXT.md (本文件)
├── README.md (專案說明)
├── CLAUDE.md (IDE 規範)
├── task.md (當前任務追蹤)
├── tickers_us.csv (美股標的主表)
├── Pilot_Reports/ (研究報告存放區，依產業分類)
│   └── Technology/ (如 AAPL_Apple.md)
├── scripts/ (自動化腳本)
│   ├── add_ticker.py (新增標的)
│   ├── fetch_tickers.py (抓取交易所名單)
│   ├── update_financials.py (更新財務數據)
│   ├── update_enrichment.py (AI 業務內容補充)
│   ├── update_valuation.py (更新估值數據)
│   ├── build_network.py (生成供應鏈關係圖)
│   ├── build_themes.py (生成投資主題)
│   ├── build_wikilink_index.py (建立知識圖譜索引)
│   └── utils.py (通用工具函式)
├── diary/ (開發日誌)
├── network/ (視覺化圖表數據)
└── themes/ (主題投資數據)
```

## 🏛️ 4. 架構與設計約定 (Architecture & Conventions)
* **GitHub 同步**: 已完成初始化並連結至 `Allen930311/My-US-Coverage`。
* **命名規範**: 標的文件採用 `[TICKER]_[Name].md` 格式。
* **資料幣別**: 財務數據統一採用 **USD**。

## 🚦 5. 目前進度與待辦 (Current Status & TODO)
_(同步自日記 2026-03-26)_

### ✅ 已完成
- [x] 同步至 GitHub 以確保資料安全。
- [x] 清理冗餘的專案子資料夾。
- [x] 建立並更新 AGENT_CONTEXT.md。

### 🚧 待辦事項
- [ ] 完成 Batch 1 剩餘 8 隻標的 (MSFT, GOOGL, AMZN, META, TSLA, ASML, TSM, AVGO)。
- [ ] 執行 `update_enrichment.py` 補充繁體中文業務說明。
- [ ] 運行 `build_network.py` 產生美股供應鏈關係圖。
- [ ] 運行 `build_themes.py` 建立投資主題。


