import requests
from bs4 import BeautifulSoup

URL = "https://www.tv-asahi.co.jp/goodmorning/uranai/#ranking"
response = requests.get(URL)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "html.parser")

horoscope_data = {}

# Каждый знак зодиака в своем div.seiza-box
for box in soup.select("div.seiza-box"):
    # Название знака
    try:
        sign_name = box.select_one(".seiza-txt").get_text(strip=True)
    except:
        sign_name = "❌ нет названия"

    # Основной текст
    try:
        content = box.select_one(".read-area p.read").get_text(" ", strip=True)
    except:
        content = "❌ нет текста"

    # Счастливый цвет
    lucky_color = "❌ нет цвета"
    color_span = box.find("span", class_="lucky-color-txt")
    if color_span and color_span.next_sibling:
        lucky_color = color_span.next_sibling.strip(" ：:\n")

    # Счастливый ключ
    lucky_key = "❌ нет ключа"
    key_span = box.find("span", class_="key-txt")
    if key_span and key_span.next_sibling:
        lucky_key = key_span.next_sibling.strip(" ：:\n")

    # 🍁🍂 Уровень удачи
    lucky_blocks = box.select("li.lucky-cell")
    lucky_texts = []
    for block in lucky_blocks:
        # Определяем категорию по классу
        if "lucky-money" in block.get("class", []):
            category = "💰"
        elif "lucky-love" in block.get("class", []):
            category = "❤️"
        elif "lucky-work" in block.get("class", []):
            category = "💼"
        elif "lucky-health" in block.get("class", []):
            category = "💊"
        else:
            category = "✨ Удача"

        # Считаем количество иконок
        icons = block.select("p.lucky-box img")
        count = len(icons)

        # Листочки 🍁🍂
        if count >= 3:
            rating = "🍁" * count
        else:
            rating = "🍂" * count

        lucky_texts.append(f"{category}: {rating}")

    lucky_summary = "\n".join(lucky_texts) if lucky_texts else "❌ нет данных по удаче"

    # Собираем текст (сначала цвет и ключ, потом уровни)
    horoscope_data[sign_name] = f"""{content}

Счастливый цвет: {lucky_color}
Ключ к удаче: {lucky_key}
{lucky_summary}"""

# Сохраняем в файл
with open("horoscope_tv_asahi.txt", "w", encoding="utf-8") as f:
    for sign, text in horoscope_data.items():
        f.write(f"==== {sign} ====\n")
        f.write(text + "\n\n")

print("✅ Готово! Данные сохранены в horoscope_tv_asahi.txt")
