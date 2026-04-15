import schedule
import time
import subprocess

file_path = r"/home/orlan/yolo/Orlan-24/parsKorea.py"

def job():
    print("🚀 Запуск скрипта!")
    subprocess.Popen(["python", file_path])

# каждый день в 07:00
schedule.every().day.at("07:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
