# net_utils.py
import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    """Функция для загрузки страницы по URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching page: {response.status_code}")
        return None

def get_soup(url):
    """Получение объекта BeautifulSoup для парсинга"""
    page_content = fetch_page(url)
    if page_content:
        return BeautifulSoup(page_content, 'html.parser')
    return None
