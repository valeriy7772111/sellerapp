import os, requests
from dotenv import load_dotenv

load_dotenv("/root/sellerapp/.env")

headers = {
    "Client-Id": os.getenv("OZON_CLIENT_ID"),
    "Api-Key": os.getenv("OZON_API_KEY"),
    "Content-Type": "application/json"
}

# Новый рабочий эндпоинт Ozon — проверяем цены/информацию о товарах
data = {"page_size": 10, "page": 1}

response = requests.post(
    "https://api-seller.ozon.ru/v4/product/info/prices",
    json=data,
    headers=headers
)

print("✅ Ответ от Ozon (обновлённый API):")
print(response.text)
