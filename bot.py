print("🚀 Crypto Sentinel Bot is starting...")
import requests
import json
import time

# DexScreener API URL
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/search/?q=ETH"

# Load Config File
with open("config.json") as config_file:
    CONFIG = json.load(config_file)

# API Endpoints
POCKET_UNIVERSE_API_URL = "https://api.pocketuniverse.app/fake-volume"
RUGCHECK_API_URL = "https://rugcheck.xyz/api/check"
TOXISOL_API_URL = "https://api.toxisol.com/trade"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{CONFIG['telegram']['bot_token']}/sendMessage"

# Function to Fetch Data from DexScreener
def fetch_data():
    try:
        response = requests.get(DEXSCREENER_URL, timeout=10)
        if response.status_code == 200:
            return response.json().get("pairs", [])
        else:
            return {"error": f"Failed to fetch data: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Function to Check Fake Volume
def detect_fake_volume(token_address):
    headers = {"Authorization": f"Bearer {CONFIG['pocket_universe_api_key']}"}
    try:
        response = requests.post(POCKET_UNIVERSE_API_URL, json={"token": token_address}, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else {"error": "API call failed"}
    except Exception as e:
        return {"error": str(e)}

# Function to Check RugCheck
def check_rugcheck(token_address):
    headers = {"Authorization": f"Bearer {CONFIG['rugcheck_api_key']}"}
    try:
        response = requests.get(f"{RUGCHECK_API_URL}/{token_address}", headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else {"error": "API call failed"}
    except Exception as e:
        return {"error": str(e)}

# Function to Send Telegram Message
def send_telegram_message(message):
    data = {"chat_id": CONFIG["telegram"]["chat_id"], "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(TELEGRAM_API_URL, json=data, timeout=10)
        return response.json() if response.status_code == 200 else {"error": "Telegram API call failed"}
    except Exception as e:
        return {"error": str(e)}

# Function to Execute Trade
def execute_trade(token, action):
    headers = {"Authorization": f"Bearer {CONFIG['toxisol_api_key']}"}
    payload = {
        "token_address": token["baseToken"]["address"],
        "pair_address": token["pairAddress"],
        "action": action
    }
    try:
        response = requests.post(TOXISOL_API_URL, json=payload, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else {"error": "Trade execution failed"}
    except Exception as e:
        return {"error": str(e)}

# Main Trading Bot Loop
def trading_bot():
    print("🔄 Trading bot loop has started!")
    send_telegram_message("🚀 Crypto Sentinel Bot Started!")  # ✅ Moved to the correct place

    while True:
        tokens = fetch_data()
        print("Fetched tokens:", tokens)  # Debugging output

        if "error" in tokens:
            print("Error fetching data:", tokens["error"])
        else:
            for token in tokens[:5]:  # ✅ Only process first 5 tokens
                token_address = token["baseToken"]["address"]
                print(f"🔍 Checking token: {token_address} ({token['baseToken']['symbol']})")

                # Check if the token is safe
                rugcheck_result = check_rugcheck(token_address)
                print(f"🛡️ RugCheck Result: {rugcheck_result}")

                fake_volume_result = detect_fake_volume(token_address)
                print(f"📉 Fake Volume Check: {fake_volume_result}")

                if rugcheck_result.get("status") == "Good" and not fake_volume_result.get("is_fake"):
                    print(f"✅ Safe Token Found: {token['baseToken']['symbol']} at {token['priceUsd']}")

                    send_telegram_message(f"✅ Safe Token Found: {token_address}\nPrice: {token['priceUsd']}")

                    # Execute trade
                    trade_result = execute_trade(token, "buy")
                    print(f"🛒 Trade Executed: {trade_result}")
                    send_telegram_message(f"🛒 Trade Executed: {trade_result}")
                else:
                    print(f"❌ Token filtered out: {token['baseToken']['symbol']}")

        time.sleep(CONFIG['trading']['update_interval'])  # ✅ Ensures loop waits before next run

# ✅ FIXED: Corrected placement of `if __name__ == "__main__":`
if __name__ == "__main__":
    trading_bot()
