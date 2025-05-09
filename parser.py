import requests
from bs4 import BeautifulSoup
from collections import deque

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
