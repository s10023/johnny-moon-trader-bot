# 🚀 Buibui Moon Trader Bot

A tactical crypto trading bot designed for fast, risk-managed, and confident entries — with live price monitoring and position tracking. Built for degens who trade smart. LFG. 🌕

---

## 🧠 Features

### ✅ Core Tools

- **Manual Multi-Trade Entry Script**  
  Open multiple trades (BTC, ETH, alts) in one go, using USD-based sizing with automatic SL & leverage.

- **Live Price Monitor**  
  See real-time prices, 15m / 1h / 24h % changes, and intraday % change since Asia open (8AM GMT+8).  
  Color-coded for clarity.

- **Live Position Tracker**  
  Track open positions with wallet balance, used margin, PnL, %PnL, and risk exposure per trade.  
  Table auto-sorted by your config list.

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

```bash
buibui-moon-trader-bot/
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
git clone https://github.com/yourname/buibui-moon-trader-bot.git
cd buibui-moon-trader-bot

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

```bash
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

This will loop and update every 5 seconds by default.
To run once and exit:

```bash
python monitor/price_monitor.py --once
```

It shows:

- Live price
- 15-minute %, 1-hour %, Asia session %, and 24h %

### 📊 Monitor Positions & PnL

```bash
python monitor/position_monitor.py
```

Shows:

- Wallet balance

- Total unrealized PnL

- Colorized risk table with per-trade metrics

- Only open positions are shown. Auto-sorted by your coins.json order.

Example Output:

```yaml
💰 Wallet Balance: $1,123.15
📊 Total Unrealized PnL: +290.29

╒══════════════╤════════╤═══════════╤═══════════╤═════════════════════╤═══════════════════════╤════════╤════════╤═════════╕
│ Symbol       │ Side   │     Entry │      Mark │   Used Margin (USD) │   Position Size (USD) │    PnL │ PnL%   │ Risk%   │
╞══════════════╪════════╪═══════════╪═══════════╪═════════════════════╪═══════════════════════╪════════╪════════╪═════════╡
│ BTCUSDT      │ SHORT  │ 110032    │ 109265    │              598.77 │              14969.3  │ 105.08 │ +0.70% │ 53.31%  │
│ ETHUSDT      │ SHORT  │   2616.17 │   2580.28 │              598.11 │              11962.2  │ 166.2  │ +1.37% │ 53.25%  │
│ ...          │ ...    │    ...    │    ...    │               ...    │                 ...    │ ...    │  ...   │  ...    │
╘══════════════╧════════╧═══════════╧═══════════╧═════════════════════╧═══════════════════════╧════════╧════════╧═════════╛

```

### ☁️ GitHub Actions (Optional)

The `.github/workflows/monitor.yaml` file can be configured to:

- Run position_monitor.py every 15 minutes

- Send live updates to Telegram

### 📌 Coming Soon / Ideas

- Trade signal engine (support/resistance + volume traps)

- Auto-close on global SL or high-risk warning

- Visual dashboard (web UI or terminal rich)

- Funding rate monitor + reversal detector
