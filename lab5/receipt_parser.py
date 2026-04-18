import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()


# --------------------
# PRICES
# --------------------

price_pattern = r"\d[\d ]*,\d{2}"
prices = re.findall(price_pattern, text)

prices_clean = []

for p in prices:
    value = float(p.replace(" ", "").replace(",", "."))
    prices_clean.append(value)
# convert to float
prices_clean = []
for p in prices:
    value = float(p.replace(" ", "").replace(",", "."))
    prices_clean.append(value)


# --------------------
# PRODUCT NAMES
# --------------------

product_pattern = r"\d+\.\n([^\n]+)"
products = re.findall(product_pattern, text)


# --------------------
# DATE AND TIME
# --------------------

datetime_pattern = r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s*(\d{2}:\d{2}:\d{2})"
dt_match = re.search(datetime_pattern, text)

date = dt_match.group(1) if dt_match else None
time = dt_match.group(2) if dt_match else None


# --------------------
# PAYMENT METHOD
# --------------------

payment_pattern = r"(Банковская карта|Наличные)"
payment = re.search(payment_pattern, text)

payment_method = payment.group(1) if payment else None


# --------------------
# TOTAL
# --------------------

total_pattern = r"ИТОГО:\n([\d\s]+,\d{2})"
total_match = re.search(total_pattern, text)

total = None
if total_match:
    total = float(total_match.group(1).replace(" ", "").replace(",", "."))


# --------------------
# STRUCTURED OUTPUT
# --------------------

data = {
    "products": products,
    "prices_found": prices_clean,
    "total_calculated": sum(prices_clean),
    "total_from_receipt": total,
    "date": date,
    "time": time,
    "payment_method": payment_method
}


print(json.dumps(data, indent=4, ensure_ascii=False))