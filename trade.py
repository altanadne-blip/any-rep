import cloudscraper
import requests

SAFE_URL = "https://safe.trade/api/v2"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

def get_binance_price():
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        r.raise_for_status()
        return float(r.json()["price"])
    except Exception as e:
        print("Помилка Binance:", e)
        return None

def get_safe_bids(market_id="btcusdt"):
    scraper = cloudscraper.create_scraper()
    url = f"{SAFE_URL}/trade/public/markets/{market_id}/depth"
    try:
        r = scraper.get(url, timeout=10)
        r.raise_for_status()
        depth = r.json()
        return depth.get("bids", [])
    except Exception as e:
        print("Помилка SafeTrade:", e)
        return []

def find_best_order():
    binance_price = get_binance_price()
    if not binance_price:
        return
    
    print(f"Ціна Binance: {binance_price}")
    bids = get_safe_bids()

    candidates = []
    for price, amount in bids:
        price = float(price)
        amount = float(amount)
        if amount >= 0.001 and price < binance_price:
            # Відстань > 1% від ціни Binance
            if (binance_price - price) / binance_price > 0.01:
                candidates.append((price, amount))
    
    if not candidates:
        print("Немає підходящих ордерів для виставлення")
        return
    
    # вибираємо найвищу ціну серед кандидатів
    best_price, best_amount = max(candidates, key=lambda x: x[0])
    my_order_price = round(best_price + 0.1, 2)

    print(f"Найкращий ордер у стакані: {best_price} (обсяг {best_amount})")
    print(f"Рекомендована ціна для виставлення ордера: {my_order_price}")

if __name__ == "__main__":
    find_best_order()
