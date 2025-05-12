import requests
from bs4 import BeautifulSoup
from collections import deque
import re
from ai_description import generate_description

BASE_URL = "https://www.jopa.nl"

def safe_request(url):
    """
    Функция для безопасного отправления запроса.
    """
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Ошибка запроса: {e}")
        return None

def collect_all_final_pages(start_url, brand):
    """
    Функция для сбора всех финальных страниц с товарами по бренду.
    Возвращает список URL страниц, на которых находится блок <div class="artikel">.
    """
    visited = set()
    queue = deque([start_url])
    final_pages = []

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        response = safe_request(url)
        if not response:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Если на странице есть товарный блок — считаем её «финальной»
        if soup.select("div.artikel"):
            final_pages.append(url)

        # Добавляем в очередь все ссылки вида /en/{brand}/… для дальнейшего обхода
        for a in soup.select(f"a[href*='/en/{brand.lower()}/']"):
            href = a.get("href")
            if href:
                full_url = href if href.startswith("http") else BASE_URL + href
                if full_url not in visited:
                    queue.append(full_url)

    return final_pages

def get_product_details(category_url):
    resp = safe_request(category_url)
    if not resp:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    tegel = soup.select_one("div.shopTegel a.link")
    if not tegel:
        return None
    href = tegel["href"]
    product_url = href if href.startswith("http") else BASE_URL + href

    resp2 = safe_request(product_url)
    if not resp2:
        return None
    soup2 = BeautifulSoup(resp2.text, "html.parser")

    # Name
    name_tag = soup2.select_one("div.omschrijving h1")
    name = name_tag.text.strip() if name_tag else "No name"
    name = re.sub(r"\s\d+$", "", name)

    # Images
    imgs = soup2.select("div.carousel-cell-groot img")
    images = [img["src"] for img in imgs] if imgs else ["No image"]

    # EAN
    ean_tag = soup2.select_one("div.EANnummer span:nth-of-type(2)")
    ean = ean_tag.text.strip() if ean_tag else "Not found"

    # Price
    price_tag = soup2.select_one("span.displayprijs")
    texts = price_tag.find_all(string=True, recursive=False)
    price = texts[0].strip() if texts else "Not found"

    # Размеры и артикулы
    sizes = []
    link_tags = soup.select("div.shopTegel a.link")
    # links = [tag["href"] for tag in link_tags if "href" in tag.attrs]

    for tag in link_tags:
        nummer_span = tag.find_next("span", class_="nummer")
        if nummer_span:
            text = nummer_span.get_text(strip=True)
            parts = text.split("-")
            if len(parts) > 1:
                size = parts[1]  # Получаем значение между дефисами
                sizes.append(size)      
        
    # Уникализируем и отсортируем
    sizes = sorted(set(sizes))

    # Описание
    description = generate_description(name, "Sidi")
    short_description = ""
    long_description = ""

    if "Īss apraksts" in description:
        # Извлекаем короткое описание
        short_start = description.find("Īss apraksts") + len("Īss apraksts")
        short_end = description.find("Detalizēts apraksts")
        short_description = description[short_start:short_end].strip()

    if "Detalizēts apraksts" in description:
        # Извлекаем длинное описание
        long_start = description.find("Detalizēts apraksts ar galvenajām īpašībām") + len("Detalizēts apraksts ar galvenajām īpašībām")
        long_description = description[long_start:].strip()

    # Удаляем лишние символы, если нужно
    short_description = short_description.lstrip(":-").strip()
    long_description = long_description.lstrip(":-").strip()

    # print("Short description:", short_description)
    # print("Long description:", long_description)
    
    product = {
        "category_url": category_url,
        "product_url":   product_url,
        "name":          name,
        "images":        images,
        "price":         price,
        "ean":           ean,
        "sizes":         sizes,
        "short-description": short_description,
        "long-description":   long_description
    }

    print(product)
    return product


