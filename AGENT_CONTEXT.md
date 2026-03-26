# 專案上下文 (Agent Context)：My-US-Coverage

> **最後更新時間**：2026-03-26 21:50
> **自動生成**：由 `prepare_context.py` 產生，供 AI Agent 快速掌握專案全局

---

## 🎯 1. 專案目標 (Project Goal)
* **核心目的**：An equity research database for all US-listed companies (NYSE, NASDAQ, AMEX), modeled after the My-TW-Coverage project.
* _完整說明見 [README.md](README.md)_

## 🛠️ 2. 技術棧與環境 (Tech Stack & Environment)
* _（未偵測到 package.json / pyproject.toml / requirements.txt）_

## 📂 3. 核心目錄結構 (Core Structure)
_(💡 AI 讀取守則：請依據此結構尋找對應檔案，勿盲目猜測路徑)_
```text
My-US-Coverage/
├── AGENT_CONTEXT.md
├── CLAUDE.md
├── My-US-Coverage
│   ├── Pilot_Reports
│   ├── network
│   ├── scripts
│   │   └── fetch_tickers.py
│   └── themes
├── Pilot_Reports
│   └── Technology
│       ├── AAPL_Apple.md
│       └── NVDA_NVIDIA.md
├── README.md
├── diary
│   └── 2026
│       └── 03
├── network
├── scripts
│   ├── add_ticker.py
│   ├── audit_batch.py
│   ├── fetch_tickers.py
│   ├── update_enrichment.py
│   ├── update_financials.py
│   ├── update_valuation.py
│   └── utils.py
├── task.md
├── themes
└── tickers_us.csv
```

## 🏛️ 4. 架構與設計約定 (Architecture & Conventions)
* _（尚無 `.auto-skill-local.md`，專案踩坑經驗將在開發過程中自動累積）_

## 🚦 5. 目前進度與待辦 (Current Status & TODO)
_(自動提取自最近日記 2026-03-26)_

### 🚧 待辦事項
- [ ] 完成 Batch 1 剩餘 8 隻標的 (MSFT, GOOGL, AMZN, META, TSLA, ASML, TSM, AVGO)。
- [ ] 執行 `update_enrichment.py` 補充繁體中文業務說明。
- [ ] 運行 `build_network.py` 產生美股供應鏈關係圖。
- [ ] 同步至 GitHub 以確保資料安全。

