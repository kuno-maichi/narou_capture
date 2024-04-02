import time
import jsonc
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw
from io import BytesIO
import os
import platform
import datetime
import re

# ラベルとURLのペア
with open('config.json', 'r', encoding='utf-8') as f:
    config = jsonc.load(f)

items = config['items']
texts = config['texts']
keywords = config['keywords']

# ChromeDriverを起動
options = Options()
options.add_argument('--window-size=800,600')
options.add_argument('--headless')
options.add_argument('log-level=3')
browser = webdriver.Chrome(options)

browser.execute_script("document.body.style.overflow = 'hidden';")

def sanitize(filename, os_name=None):
    if os_name is None:
        os_name = platform.system()

    if os_name == 'Windows':
        invalid_chars = r'[<>:"/\\|?*]'
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
                          'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5',
                          'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if filename.upper() in reserved_names:
            filename = '_' + filename
    else:  # Assume Unix/Linux
        invalid_chars = r'[/]'

    sanitized_filename = re.sub(invalid_chars, '_', filename)
    return sanitized_filename

def save_screenshots(driver, directory_path, texts, keywords):
    base_elements  = driver.find_elements(By.XPATH, f"//div[contains(@class, 'c-card') and contains(@class, 'p-ranklist-item')]")
    for i, base_element in enumerate(base_elements):
        found = False
        for text in texts:
            text_elements = base_element.find_elements(By.XPATH, f".//div[contains(text(), '{text}')]")
            if len(text_elements) > 0:
                found = True
                break
        for keyword in keywords:
            keyword_elements = base_element.find_elements(
                By.XPATH, 
                f".//div[@class='p-ranklist-item__keyword']//*[contains(text(), '{keyword}')]"
            )
            if len(keyword_elements) > 0:
                found = True
                break
        if found:
            rank = base_element.find_element(By.XPATH, f".//div[contains(@class, 'p-ranklist-item__place')]/span")
            author = base_element.find_element(By.XPATH, f".//div[contains(@class, 'p-ranklist-item__author')]/a")
            print("ランキング: " + rank.text + "位")
            print("作者: " + author.text)
            element_screenshot = base_element.screenshot_as_png
            image = Image.open(BytesIO(element_screenshot))

            # 作品枠全体に太い赤線の枠を描画
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, image.width, image.height), outline='red', width=3)

            now = datetime.datetime.now()
            now_text = now.strftime('%Y-%m-%d-%H%M')

            path = f"{directory_path}/{rank.text}位_作者-{sanitize(author.text)}_{now_text}.png"
            image.save(path)
            print(f"スクリーンショット {path} をキャプチャしました")
            continue
    pass

def capture(label, url):
    browser.get(url)
    browser.refresh()

    if not label:
        label = browser.find_element(By.XPATH, "//h2[@class='c-page-title__text']").text
    print(label)

    out_dir = f"out/{label}"
    os.makedirs(out_dir, exist_ok=True)

    save_screenshots(
        browser, f"{out_dir}", texts, keywords
    )

print("キャプチャ開始：")
for item in items:
    if isinstance(item, dict):
        label = item['label']
        url = item['url']
    else:
        label = None
        url = item
    capture(label, url)
print("キャプチャ終了：")
