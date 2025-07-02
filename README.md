# 🚀 Johnny Moon Trader Bot

A tactical crypto trading bot designed for fast, risk-managed, and confident entries — with live price monitoring and position tracking. Built for degens who trade smart. LFG. 🌕

---

## 🧠 Features

### ✅ Core Tools
- **Manual Multi-Trade Entry Script**  
  Open multiple trades (BTC, ETH, alts) in one go, using USD-based sizing with automatic SL & leverage.

- **Live Price Monitor**  
  See real-time prices, 24h change, and volume for top coins.

- **Live Position Tracker**  
  Track open positions, wallet value, unrealized PnL, and risk exposure per trade.

- **15-Min Telegram Updates** *(optional)*  
  Get regular position snapshots via Telegram bot.

---

## 🔒 Risk Rules (Preconfigured)

| Asset Type  | Leverage | Stop Loss |
|-------------|----------|-----------|
| BTC         | 25x      | 2.0%      |
| ETH         | 20x      | 2.5%      |
| Altcoins    | 20x      | 3.5%      |

Includes max USD-per-trade cap and wallet-level risk protection.

---

## 📦 Directory Structure

```
johnny-moon-trader-bot/
├── trade/
│ └── open_trades.py # Open multiple trades via Binance
├── monitor/
│ ├── price_monitor.py # Live price, PnL, risk tracker
│ └── position_monitor.py # Telegram PnL updates every 15min
├── config/
│ └── coins.json # Coin list, SL%, leverage per symbol
├── .github/
│ └── workflows/
│ └── monitor.yml # GitHub Actions for automated Telegram updates
├── .env.example # Sample config (Telegram + Binance keys)
├── requirements.txt # Python dependencies
└── README.md
```

---

## ⚙️ Setup

### 1. Clone this repo

```bash
git clone https://github.com/yourname/johnny-moon-trader-bot.git
cd johnny-moon-trader-bot

```

### 2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

🔁 To update later:
pip freeze > requirements.txt

### 4. Add Your API Keys

Create a `.env` file based on .env.example:

```
# .env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

TELEGRAM_BOT_TOKEN=bot_token
TELEGRAM_CHAT_ID=your_chat_id
```
### 4. Configure your coins

Edit `config/coins.json` to define each symbol’s leverage and stop-loss percent.

```json
{
  "BTCUSDT": { "leverage": 25, "sl_percent": 2.0 },
  "ETHUSDT": { "leverage": 20, "sl_percent": 2.5 },
  "SOLUSDT": { "leverage": 20, "sl_percent": 3.5 }
}
```

## 🛠️ Usage

### 🧾 Open Multiple Trades (manually)

```bash
python trade/open_trades.py
```

You'll be prompted to enter:

- Direction (LONG/SHORT)

- USD per trade (with default)

- Confirmation before executing

### 📈 Monitor Prices

```bash
python monitor/price_monitor.py
```

### 📊 Monitor Positions & PnL

```bash
python monitor/position_monitor.py
```

### ☁️ GitHub Actions (Optional)

The `.github/workflows/monitor.yaml` file can be configured to:

- Run position_monitor.py every 15 minutes

- Send live updates to Telegram