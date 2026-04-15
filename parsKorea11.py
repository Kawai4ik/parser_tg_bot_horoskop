import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import telebot
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import re
import random
import sys
# ---------------- Настройки бота ----------------
BOT_TOKEN = "8152178417:AAGDb7NUg0-1S0vIljWNTZUlLVbSCrveTgI"
CHANNEL_ID = "@choarakor"
bot = telebot.TeleBot(BOT_TOKEN)

# ---------------- Шрифты и параметры изображения ----------------
width, height = 1500, 2250
line_spacing = 10
x_margin = 98
y_start = 530

# 🔹 Шрифты
# 🔹 Папка со шрифтами
font_dir = "/home/orlan/yolo/Orlan-24/Fonts"

# 🔹 Шрифты
font_text = ImageFont.truetype(os.path.join(font_dir, "arial.ttf"), 43)   # основной текст
font_symbols = ImageFont.truetype(os.path.join(font_dir, "seguisym.ttf"), 45)  # символы

emoji_font_path = os.path.join(font_dir, "NotoColorEmoji.ttf")
if not os.path.exists(emoji_font_path):
    emoji_font_path = os.path.join(font_dir, "seguisym.ttf")
font_emoji = ImageFont.truetype(emoji_font_path, 45)


# ---------------- Дата ----------------
months = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}
today = datetime.now()
date_text = f"✨🌞 Гороскоп на сегодня: {today.day} {months[today.month]} {today.year} 🌞✨\n\n"

# ---------------- Сопоставление корейских названий → русские + иконки ----------------
zodiac_translate = {
    "양자리": ("Овен ♈🐏", "/home/orlan/yolo/Orlan-24/iconss/0.png"),
    "황소자리": ("Телец ♉🐂", "/home/orlan/yolo/Orlan-24/iconss/1.png"),
    "쌍둥이자리": ("Близнецы ♊👯", "/home/orlan/yolo/Orlan-24/iconss/2.png"),
    "게자리": ("Рак ♋🦀", "/home/orlan/yolo/Orlan-24/iconss/3.png"),
    "사자자리": ("Лев ♌🦁", "/home/orlan/yolo/Orlan-24/iconss/4.png"),
    "처녀자리": ("Дева ♍👩‍🌾", "/home/orlan/yolo/Orlan-24/iconss/5.png"),
    "천칭자리": ("Весы ♎⚖️", "/home/orlan/yolo/Orlan-24/iconss/6.png"),
    "전갈자리": ("Скорпион ♏🦂", "/home/orlan/yolo/Orlan-24/iconss/7.png"),
    "사수자리": ("Стрелец ♐🏹", "/home/orlan/yolo/Orlan-24/iconss/8.png"),
    "염소자리": ("Козерог ♑🐐", "/home/orlan/yolo/Orlan-24/iconss/9.png"),
    "물병자리": ("Водолей ♒💧", "/home/orlan/yolo/Orlan-24/iconss/10.png"),
    "물고기자리": ("Рыбы ♓🐟", "/home/orlan/yolo/Orlan-24/iconss/11.png")
}

# ---------------- Ollama — улучшение текста ----------------
def improve_with_ollama(text, model="llama3"):
    try:
        prompt = (
            f"Перевеведи текст и напиши текст на русском языке исползуя кириллицу."
            f"Не используй слова и предложения на англиском языке и языках, которые не относятся к русскому языку."
            f"Сократи и переработай его в поэтичный, выразительный гороскоп."
            f"Сохрани только суть и ключевые идеи, отбрось второстепенное."
            f"Объём: 2 плавных, связных предложения."
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
            timeout=60
        )
        response = result.stdout.decode("utf-8").strip()
        response = re.sub(r"\n\s*\n+", "\n", response)
        response = re.sub(r"^(вот.*гороскоп.*|держи.*|ваш текст.*)[:\-–]?\s*", "", response, flags=re.IGNORECASE)
        return response if response else text
    except Exception as e:
        print("⚠️ Ошибка Ollama:", e)
        return text

# ---------------- Перевод и утилиты ----------------
def safe_translate(text, src="auto", tgt="ru", chunk_size=100, retries=3, delay=0.6):
    if not text:
        return ""
    translated = ""
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        for attempt in range(retries):
            try:
                translated_chunk = GoogleTranslator(source=src, target=tgt, timeout=15).translate(chunk)
                translated += translated_chunk
                time.sleep(0.2)
                break
            except Exception as e:
                print(f"⚠️ Ошибка перевода части (попытка {attempt+1}/{retries}): {e}")
                time.sleep(delay)
        else:
            translated += chunk
    return translated

def clean_lucky_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text.capitalize()

# ---------------- Сессия ----------------
session = requests.Session()

# ---------------- Выбор шрифта ----------------
def choose_font(char):
    if char in "★☆":
        return font_symbols
    if ord(char) > 0x2300:
        return font_emoji
    return font_text

# ---------------- Рисование текста с переносом ----------------
def draw_wrapped_text(draw, text, x, y, max_width, line_spacing, line_height=None, fill=(143,81,36)):
    if line_height is None:
        line_height = font_text.getbbox("Hg")[3]
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test_line = (line + " " + word).strip()
            width_line = sum(draw.textlength(c, font=choose_font(c)) for c in test_line)
            if width_line > max_width and line:
                x_line = x
                for c in line:
                    draw.text((x_line, y), c, font=choose_font(c), fill=fill)
                    x_line += draw.textlength(c, font=choose_font(c))
                y += line_height + line_spacing
                line = word
            else:
                line = test_line
        x_line = x
        for c in line:
            draw.text((x_line, y), c, font=choose_font(c), fill=fill)
            x_line += draw.textlength(c, font=choose_font(c))
        y += line_height + line_spacing
    return y

# ---------------- Получение HTML из страницы ----------------
def fetch_todaystar(iAstro, retries=3, delay=1.0):
    url = f"https://fortune.nate.com/contents/freeunse/todaystar.nate?iAstro={iAstro}&dateparam=0"
    for attempt in range(1, retries+1):
        try:
            r = session.get(url, timeout=12)
            r.raise_for_status()
            html = r.text
            if "<table" in html:
                return html
            else:
                print(f"⚠️ HTML без таблицы для iAstro={iAstro} (попытка {attempt})")
        except Exception as e:
            print(f"⚠️ Ошибка запроса HTML для iAstro={iAstro} (попытка {attempt}): {e}")
        time.sleep(delay)
    return None

# ---------------- Функция прогресс-бара ----------------
def print_step_progress(current, total, stage=""):
    """
    Выводит прогресс в виде: [██████····]  50% — [1/12] Этап
    """
    bar_length = 30
    filled_len = int(round(bar_length * current / float(total)))
    percents = round(100.0 * current / float(total), 1)
    bar = '█' * filled_len + '·' * (bar_length - filled_len)
    sys.stdout.write(f'\r[{bar}] {percents}% — {stage}')
    sys.stdout.flush()
    if current >= total:
        print()  # переход на новую строку после завершения

# ---------------- Основной цикл с прогрессом ----------------
images = []
for i in range(12):
    print(f"\n🔎 Обработка знака {i}...")

    # ---- шаги главного прогресса ----
    total_steps = 5
    step = 0

    # ==== 1. Получение HTML ====
    step += 1
    print_step_progress(step, total_steps, f"[{i+1}/12] Получение HTML")
    html = fetch_todaystar(i)
    if not html:
        print(f"\n❌ Не удалось получить контент для знака {i}, пропускаю.")
        continue
    soup = BeautifulSoup(html, "html.parser")

    # ==== 2. Извлечение текста ====
    step += 1
    print_step_progress(step, total_steps, f"[{i+1}/12] Извлечение текста")

    raw_name = None
    try:
        b = soup.select_one("#con_box b")
        if b:
            raw_name = b.get_text(strip=True).split("(")[0].strip()
    except Exception as e:
        print("\n⚠️ Ошибка чтения имени знака:", e)

    if not raw_name:
        h3 = soup.find("h3")
        raw_name = h3.get_text(strip=True).split("(")[0].strip() if h3 else f"Знак {i}"
    print(f"\n  ✅ Найдено имя знака: {raw_name}")

    content = "❌ нет текста"
    try:
        con_txt = soup.select_one("#con_txt")
        if con_txt:
            content = con_txt.get_text("\n", strip=True) or content
    except Exception as e:
        print("\n⚠️ Ошибка извлечения основного текста:", e)
    print(f"  📄 Длина текста: {len(content)}")

    # ==== 2a. Элементы удачи с прогрессом ====
    lucky_translate = {
        "행운의시간": "Удачное время",
        "행운의물건": "Счастливый предмет",
        "행운의장소": "Счастливое место",
        "행운의색상": "Счастливый цвет"
    }
    lucky_text_list = []

    try:
        table = soup.select_one("#con_box2 table")
        if table:
            ths = table.find_all("th")
            ems = table.find_all("em")
            total_lucky = len(ths)
            for idx, (th, em) in enumerate(zip(ths, ems), 1):
                title = (th.get("title") or th.get_text(strip=True) or "").strip()
                value = (em.get_text(strip=True) or "").strip()
                if not title or not value:
                    continue
                # Перевод
                translated_value = safe_translate(value, src="auto", tgt="ru")
                translated_value = clean_lucky_text(translated_value)
                lucky_text_list.append(f"🍀 {lucky_translate.get(title, title)}: {translated_value}")

                # Прогресс элементов удачи
                print_step_progress(idx, total_lucky, f"[{i+1}/12] Перевод элементов удачи")
        else:
            print("  ⚠️ Таблица элементов удачи не найдена")
    except Exception as e:
        print("⚠️ Ошибка парсинга элементов удачи:", e)

    lucky_text = "\n".join(lucky_text_list) if lucky_text_list else "🍀 Элементы удачи временно недоступны"

    # ==== 3. Перевод основного текста ====
    step += 1
    print_step_progress(step, total_steps, f"[{i+1}/12] Перевод текста")
    try:
        translated_content = safe_translate(content, src="auto", tgt="ru")
    except Exception as e:
        print("\n⚠️ Ошибка перевода:", e)
        translated_content = content

    # ==== 4. Улучшение текста ====
    step += 1
    print_step_progress(step, total_steps, f"[{i+1}/12] Улучшение текста (Ollama)")
    try:
        translated_content = improve_with_ollama(translated_content)
    except Exception as e:
        print("\n⚠️ Ошибка улучшения:", e)

    # ==== 5. Создание изображения ====
    step += 1
    print_step_progress(step, total_steps, f"[{i+1}/12] Создание изображения")

    translated_name, icon_path = zodiac_translate.get(raw_name, (raw_name, "icons/default.png"))
    full_text = f"{date_text}{translated_name}\n\n{translated_content}\n\n✨ Элементы Удачи:\n{lucky_text}"

    image = Image.new("RGBA", (width, height), (255, 248, 220, 255))
    draw = ImageDraw.Draw(image)
    if os.path.exists(icon_path):
        try:
            icon = Image.open(icon_path).convert("RGBA").resize((width, height))
            icon.putalpha(255)
            image.paste(icon, (0, 0), icon)
        except Exception as e:
            print("\n⚠️ Ошибка загрузки иконки:", e)

    draw_wrapped_text(draw, full_text, x_margin, y_start, width - 2 * x_margin, line_spacing)
    img_name = f"horoscope_kr_{i}.png"
    image.save(img_name)
    images.append(img_name)

    # Финальный прогресс
    print_step_progress(total_steps, total_steps, f"[{i+1}/12] Готово!")
    print("\n")
    time.sleep(0.6)

# ---------------- Отправка в Telegram (батчами по 6) ----------------
REACTIONS = ["👍", "🔥", "❤️", "👏", "🙏", "💯"]

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

for j in range(0, len(images), 6):
    batch = images[j:j+6]
    print(f"\n📤 Отправка батча {j//6 + 1}: {batch}")
    media = []
    for f in batch:
        media.append(telebot.types.InputMediaPhoto(open(f, "rb")))
    sent = False
    sent_messages = None
    while not sent:
        try:
            sent_messages = bot.send_media_group(CHANNEL_ID, media)
            sent = True
            print("✔️ Отправлено!")
        except telebot.apihelper.ApiTelegramException as e:
            desc = e.result_json.get("description", "")
            if "retry after" in desc:
                wait = int(re.search(r"(\d+)", desc).group(1))
                print(f"⚠️ Too Many Requests. Ждём {wait} секунд...")
                time.sleep(wait + 1)
            else:
                print(f"❌ Ошибка Telegram: {e}. Пробуем снова через 5 секунд...")
                time.sleep(5)

    if sent_messages:
        for msg in sent_messages:
            try:
                set_random_reaction(BOT_TOKEN, msg.chat.id, msg.message_id)
            except Exception as e:
                print("⚠️ Ошибка установки реакции:", e)
            time.sleep(1.5)

    # закрываем файлы из media
    for m in media:
        try:
            m.media.close()
        except Exception:
            pass

    time.sleep(6)

# Удаляем все созданные изображения с сервера
for img_file in images:
    try:
        os.remove(img_file)
        print(f"🗑 Файл удалён: {img_file}")
    except Exception as e:
        print(f"⚠️ Ошибка удаления файла {img_file}: {e}")

print("\n✅ Все гороскопы созданы и отправлены!")
