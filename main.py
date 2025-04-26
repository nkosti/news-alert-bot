import feedparser
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask
import threading

# --------------- НАЛАШТУВАННЯ -----------------

# Список RSS-стрічок
RSS_FEEDS = [
    "https://www.reutersagency.com/feed/?best-sectors=politics,markets",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "https://www.ft.com/?format=rss",
    "https://www.politico.com/rss/politics08.xml",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.investing.com/rss/news_25.rss"
]

# Ключові слова для фільтрації
KEYWORDS = ["Trump", "NVO", "S&P 500", "stock market", "AMD", "GOOG", "GOOGL", "INTC", "MSFT", "NVO", "PEP", "SMR", "TLT", "U.UN"]

# Дані для надсилання листа
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "ninvestment033@gmail.com"  # Замінити на свою адресу
EMAIL_PASSWORD = "mbuv tszn jvqj whfn"  # Замінити на свій Gmail App Password
RECIPIENT_EMAIL = "ninvestment033@gmail.com"  # Кому надсилати листи

# Пам'ятаємо останні надіслані новини
sent_links = set()

# --------------- СЕРВЕР ДЛЯ ПІДТРИМКИ ЖИТТЯ -----------------

app = Flask('')


@app.route('/')
def home():
    return "Я працюю!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = threading.Thread(target=run)
    t.start()


# --------------- ФУНКЦІЇ ЛОГІКИ -----------------

def send_email(subject, body, link, published_time):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    # Формуємо текст листа
    message_text = f"{body}\n\nДата новини: {published_time}\nДжерело: {link}"

    msg.attach(MIMEText(message_text, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

        print(f"Лист надіслано: {subject}")

        # ----------- ЩОДЕННЕ ЛОГУВАННЯ -----------
        log_filename = f"log_{time.strftime('%Y-%m-%d')}.txt"

        with open(log_filename, "a", encoding="utf-8") as f:
            log_entry = (f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                         f"Надіслано: {subject} | Дата новини: {published_time} | Посилання: {link}\n")
            f.write(log_entry)

    except Exception as e:
        print(f"Помилка при надсиланні листа: {e}")


def check_feeds():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            link = entry.link
            title = entry.title
            summary = entry.get('summary', '')
            published = entry.get('published', 'Дата невідома')

            if link in sent_links:
                continue

            content = f"{title} {summary}".lower()

            if any(keyword.lower() in content for keyword in KEYWORDS):
                send_email(subject=title, body=title, link=link, published_time=published)
                sent_links.add(link)


# --------------- ЗАПУСК -----------------

if __name__ == "__main__":
    keep_alive()  # Запускаємо сервер для UptimeRobot
    print("Скрипт запущено! Перевірка новин кожну 1 хвилину...\n")
    while True:
        check_feeds()
        time.sleep(60)  # Перевірка новин кожну хвилину
