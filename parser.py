# parser.py
from net_utils import get_soup

def extract_product_links(soup, brand, category):
    """Извлечение ссылок на модели товаров из страницы категории"""
    links = []
    # Ищем все теги <a> с атрибутом href, которые ведут на страницы моделей
    product_elements = soup.find_all('a', href=True)
    
    for product_element in product_elements:
        link = product_element['href']
        # Фильтруем ссылки, чтобы они были связаны с моделью (по ключевым словам)
        if f"/{brand}/{category}/" in link:  # Пример фильтрации по категории
            links.append(link)
    
    return links

def parse_category_page(url, brand, category):
    """Парсинг страницы категории товара для извлечения ссылок на модели"""
    soup = get_soup(url)
    if soup:
        model_links = extract_product_links(soup, brand, category)
        return model_links
    return []
