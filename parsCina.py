import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import telebot
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess  # ✅ добавил для ollama
import random

# 🔹 Настройки бота
BOT_TOKEN = "7886381245:AAFzIJWxLoC5iZQtysuiSvTOcSZQe18cPqU"
CHANNEL_ID = "@SunYurui"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔹 Шрифты
# 🔹 Папка со шрифтами
font_dir = "/home/orlan/yolo/Orlan-24/Fonts"

# 🔹 Шрифты
font_text = ImageFont.truetype(os.path.join(font_dir, "arial.ttf"), 35)   # основной текст
font_symbols = ImageFont.truetype(os.path.join(font_dir, "seguisym.ttf"), 35)  # символы

emoji_font_path = os.path.join(font_dir, "NotoColorEmoji.ttf")
if not os.path.exists(emoji_font_path):
    emoji_font_path = os.path.join(font_dir, "seguisym.ttf")
font_emoji = ImageFont.truetype(emoji_font_path, 35)

font_date = ImageFont.truetype(os.path.join(font_dir, "arial.ttf"), 48)   # увеличенный размер для даты

# 🔹 Настройки картинки
width, height = 1500, 2250
line_spacing = 10
x_margin = 100
y_start = 600  # смещение от верхнего края

# 🔹 Цвета
COLOR_HIGHLIGHT = (226, 151, 29)  # для ★, даты и заголовков
COLOR_TEXT = (255, 255, 255)      # для остального текста

# 🔹 Словарь знаков с эмодзи и иконками
zodiac_translate = {
    "牡羊座": ("Овен ♈🐏", "/home/orlan/yolo/Orlan-24/icons/0.png"),
    "金牛座": ("Телец ♉🐂", "/home/orlan/yolo/Orlan-24/icons/1.png"),
    "雙子座": ("Близнецы ♊👯", "/home/orlan/yolo/Orlan-24/icons/2.png"),
    "巨蟹座": ("Рак ♋🦀", "/home/orlan/yolo/Orlan-24/icons/3.png"),
    "獅子座": ("Лев ♌🦁", "/home/orlan/yolo/Orlan-24/icons/4.png"),
    "處女座": ("Дева ♍👩‍🌾", "/home/orlan/yolo/Orlan-24/icons/5.png"),
    "天秤座": ("Весы ♎⚖️", "/home/orlan/yolo/Orlan-24/icons/6.png"),
    "天蠍座": ("Скорпион ♏🦂", "/home/orlan/yolo/Orlan-24/icons/7.png"),
    "射手座": ("Стрелец ♐🏹", "/home/orlan/yolo/Orlan-24/icons/8.png"),
    "摩羯座": ("Козерог ♑🐐", "/home/orlan/yolo/Orlan-24/icons/9.png"),
    "水瓶座": ("Водолей ♒💧", "/home/orlan/yolo/Orlan-24/icons/10.png"),
    "雙魚座": ("Рыбы ♓🐟", "/home/orlan/yolo/Orlan-24/icons/11.png")
}

months = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

today = datetime.now()
date_text = f"Гороскоп на сегодня: {today.day} {months[today.month]} {today.year} \n\n"

headers = {"User-Agent": "Mozilla/5.0"}
fortune_map = {
    "txt_green": "🌟 Общий прогноз",
    "txt_pink": "💖 Любовь",
    "txt_blue": "💼 Карьера",
    "txt_orange": "💰 Деньги"
}
lucky_labels = ["Число удачи", "Цвет удачи", "Удачное направление", "Время удачи", "Удачный зодиак"]

# 🔹 Функция Ollama
def improve_with_ollama(text, model="llama3"):
    try:
        prompt = (
            f"Напиши текст на русском языке исползуя кириллицу."
            f"Не допускай английских слов, латиницы, транслита, аббревиатур, имён и терминов на иностранных языках. "
            f"Если встречаются иностранные слова — переформулируй их естественно по-русски. "
            f"Сократи и переработай его в поэтичный, выразительный гороскоп."
            f"Сохрани только суть и ключевые идеи, отбрось второстепенное."
            f"Объём: 2 плавных, связных предложения. "
            f"Стиль — гармоничный, вдохновляющий, естественный для носителя языка. "
            f"Обращайся к читателю только на 'вы'. Не используй местоимения 'я', 'мы', 'мне'. "
            f"Не допускай английских слов, латиницы, транслита или иностранных символов — при необходимости переформулируй. "
            f"Следи за грамотностью, правильными склонениями и естественным ритмом фраз. "
            f"Формат вывода — один абзац без кавычек, пояснений и служебных фраз. "
            f"Пример стиля (не копируй буквально): 'Сегодня вы ощутите прилив энергии и вдохновения, смело принимайте важные решения и доверяйте интуиции.' "
            f"Ни в начале, ни в конце не добавляй служебных фраз вроде 'вот ваш текст', 'результат', 'готово'. "
            f"В результате у тебя должен быть текст полностью на русском языке, без использования английских слов, латиницы, транслита или иностранных символов. "
            f"Вот текст для преобразования:\n{text}"
        )


        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )
        response = result.stdout.decode("utf-8").strip()
        return response if response else text
    except Exception as e:
        print("⚠️ Ошибка Ollama:", e)
        return text

# 🔹 Перевод
def safe_translate(text, src="zh-TW", tgt="ru", chunk_size=30, retries=3, delay=2):
    if not text:
        return ""
    translated = ""
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        for attempt in range(retries):
            try:
                translated_chunk = GoogleTranslator(source=src, target=tgt, timeout=15).translate(chunk)
                translated += translated_chunk
                time.sleep(1)
                break
            except Exception as e:
                print(f"⚠️ Ошибка перевода части текста (попытка {attempt+1}/{retries}): {e}")
                time.sleep(delay)
        else:
            translated += chunk
    return translated

def clean_time(text):
    text = text.replace(" :", ":").replace(": ", ":").replace(" ", "")
    if text.count(":") > 2:
        parts = text.split(":")
        text = ":".join(parts[:3])
    return text

def get_soup(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = "utf-8"
            return BeautifulSoup(response.text, "html.parser")
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"⚠️ Ошибка запроса: {e}. Попытка {attempt + 1}/{retries}")
            time.sleep(delay)
    return None

# 🔹 Выбор шрифта
def choose_font(char):
    if char in "★☆🍀":
        return font_symbols
    if ord(char) > 0x2300:
        return font_emoji
    return font_text

# 🔹 Рисуем текст с подсветкой
def draw_wrapped_text_colored(draw, text, x, y, max_width, line_spacing):
    for paragraph in text.split("\n"):
        # Определяем цвет для заголовков
        fill_color = COLOR_HIGHLIGHT if paragraph.startswith("Гороскоп на сегодня") or any(paragraph.startswith(h) for h in fortune_map.values()) else COLOR_TEXT
        
        # Если это дата, используем увеличенный шрифт
        font_for_paragraph = font_date if paragraph.startswith("Гороскоп на сегодня") else None

        words = paragraph.split(" ")
        line = ""
        for word in words:
            test_line = (line + " " + word).strip()
            width_line = sum(draw.textlength(c, font=font_for_paragraph if font_for_paragraph else choose_font(c)) for c in test_line)
            if width_line > max_width and line:
                x_line = x
                for c in line:
                    c_color = COLOR_HIGHLIGHT if c in "★⭐🍀" else fill_color
                    draw.text((x_line, y), c, font=font_for_paragraph if font_for_paragraph else choose_font(c), fill=c_color)
                    x_line += draw.textlength(c, font=font_for_paragraph if font_for_paragraph else choose_font(c))
                y += (42 if font_for_paragraph else 28) + line_spacing
                line = word
            else:
                line = test_line
        x_line = x
        for c in line:
            c_color = COLOR_HIGHLIGHT if c in "★⭐🍀" else fill_color
            draw.text((x_line, y), c, font=font_for_paragraph if font_for_paragraph else choose_font(c), fill=c_color)
            x_line += draw.textlength(c, font=font_for_paragraph if font_for_paragraph else choose_font(c))
        y += (42 if font_for_paragraph else 28) + line_spacing
    return y


# 🔹 Парсим и создаём картинки
images = []
for i in range(12):
    print(f"\n🔎 Обработка знака {i}...")
    url = f"https://astro.click108.com.tw/daily_{i}.php?iAstro={i}"
    soup = get_soup(url)
    if not soup:
        print(f"❌ Не удалось получить данные для знака {i}")
        continue

    h3 = soup.select_one(".TODAY_CONTENT h3")
    raw_name = h3.text.strip().replace("今日","").replace("解析","") if h3 else f"Знак {i}"
    translated_name, icon_path = zodiac_translate.get(raw_name, (raw_name, "default.png"))
    print(f"✔️ Знак: {raw_name} → {translated_name}")

    fortunes = []
    for span in soup.select(".TODAY_CONTENT span"):
        cls = span.get("class", [""])[0]
        if cls in fortune_map:
            title = fortune_map[cls]
            rating = span.text.strip()[-6:].replace("：", "")
            next_p = span.find_parent("p").find_next_sibling("p")
            text_block = next_p.text.strip() if next_p else ""
            translated_text = safe_translate(text_block)
            improved_text = improve_with_ollama(translated_text)
            fortunes.append(f"{title} {rating}:\n{improved_text}")

    fortune_text = "\n\n".join(fortunes)

    lucky_elements = soup.select(".TODAY_LUCKY .LUCKY h4")
    lucky_text = ""
    if not lucky_elements:
        print("⚠️ Элементы удачи не найдены!")
    for idx, el in enumerate(lucky_elements):
        raw_value = el.text.strip()
        value = safe_translate(raw_value)
        label = lucky_labels[idx] if idx < len(lucky_labels) else f"Элемент {idx+1}"
        if label == "Время удачи":
            value = clean_time(value)
        lucky_text += f"🍀 {label}: {value}\n"

    full_text = f"{date_text}{fortune_text}\n\n⭐ Элементы Удачи:\n{lucky_text}"

    # 🔹 Создаём изображение с прозрачным фоном
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 🔹 Вставка иконки зодиака
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((width, height))
        icon.putalpha(255)
        image.paste(icon, (0, 0), icon)

    # 🔹 Рисуем текст с подсветкой
    draw_wrapped_text_colored(draw, full_text, x_margin, y_start, width - 2*x_margin, line_spacing)

    img_name = f"horoscope_{i}.png"
    image.save(img_name)
    images.append(img_name)
    print(f"✅ Картинка сохранена: {img_name}")

# 🔹 Реакции на Telegram
REACTIONS = ["👍", "🔥", "❤️", "😂", "👏", "🌟", "🙏", "💯"]

def set_random_reaction(bot_token, chat_id, message_id):
    reaction = random.choice(REACTIONS)
    url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": reaction}],
        "is_big": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"➡️ Реакция {reaction} установлена для {message_id}: {r.json()}")
    except Exception as e:
        print("⚠️ Ошибка при установке реакции:", e)

# 🔹 Отправка батчами
for j in range(0, len(images), 6):
    batch = images[j:j+6]
    media = [telebot.types.InputMediaPhoto(open(f, "rb")) for f in batch]
    sent = False
    sent_messages = None
    while not sent:
        try:
            sent_messages = bot.send_media_group(CHANNEL_ID, media)
            sent = True
        except telebot.apihelper.ApiTelegramException as e:
            desc = e.result_json.get("description", "")
            if "retry after" in desc:
                wait = int(desc.split("retry after")[1].split()[0])
                time.sleep(wait + 1)
            else:
                time.sleep(5)

    if sent_messages:
        for msg in sent_messages:
            set_random_reaction(BOT_TOKEN, msg.chat.id, msg.message_id)
            time.sleep(2)
    time.sleep(6)
    # Удаляем все созданные изображения с сервера
for img_file in images:
    try:
        os.remove(img_file)
        print(f"🗑 Файл удалён: {img_file}")
    except Exception as e:
        print(f"⚠️ Ошибка удаления файла {img_file}: {e}")

print("\n✅ Все гороскопы созданы, отправлены и с реакциями!")
