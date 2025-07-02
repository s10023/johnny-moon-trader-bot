# 🚀 Johnny Moon Trader Bot

A tactical crypto trading bot designed for fast, risk-managed, and confident entries — with live position and price monitoring. Built for degens who trade smart. LFG. 🌕

## 🧠 Features

### ✅ Core Tools
- **Manual Multi-Trade Entry Script**  
  Open multiple trades (BTC, ETH, alts) in one go, using USD-based sizing with automatic SL & leverage rules.

- **Live Price + PnL Monitor**  
  Tracks open positions, wallet balance, unrealized PnL, and risk exposure.

- **15-Min Telegram Position Alerts** *(Optional)*  
  Sends live updates to your Telegram bot with PnL per trade, wallet value, and risk summary.

---

## 🔒 Risk Rules (Preconfigured)

| Asset Type  | Leverage | Stop Loss |
|-------------|----------|-----------|
| BTC         | 25x      | 2.0%      |
| ETH         | 20x      | 2.5%      |
| Altcoins    | 20x      | 3.5%      |

Includes max USD per trade cap and total wallet risk protection.

---

## 📦 Directory Structure

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


---

## ⚙️ Setup

### 1. Clone this repo

```bash
git clone https://github.com/yourname/johnny-moon-trader-bot.git
cd johnny-moon-trader-bot

```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your .env file

```env
# .env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

TELEGRAM_BOT_TOKEN=bot_token
TELEGRAM_CHAT_ID=your_chat_id
```
### 4. Configure your coins

Edit config/coins.json to define each symbol’s leverage and stop-loss percent.

## 🛠️ Usage

### 🧾 Open Multiple Trades (manually)

```bash
python trade/open_trades.py
```

You'll be prompted to enter:

- Direction (LONG/SHORT)

- USD per trade (with default)

- Confirmation before executing

### 📡 Monitor Prices & Positions

```bash
python monitor/price_monitor.py
```

Prints wallet value, unrealized PnL, risk per trade.

### 🕐 Automated 15min PnL Telegram Alerts (optional)

Set up GitHub Actions using the included .github/workflows/monitor.yml to run position_monitor.py every 15 minutes and send Telegram updates.