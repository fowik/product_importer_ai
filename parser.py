# parser.py
from net_utils import get_soup

def extract_product_links(soup, brand, category):
    """Извлечение ссылок на модели товаров из страницы категории"""
    links = set()  # Используем set, чтобы избежать дубликатов
    # Ищем все теги <a> с атрибутом href, которые ведут на страницы моделей
    product_elements = soup.find_all('a', href=True)
    
    for product_element in product_elements:
        link = product_element['href']
        # Фильтруем ссылки, чтобы они были связаны с моделью (по ключевым словам)
        if f"/{brand}/{category}/" in link:  # Пример фильтрации по категории
            # Преобразуем относительные ссылки в абсолютные
            if not link.startswith("http"):
                link = f"https://www.jopa.nl{link}"
            links.add(link)  # Добавляем ссылку в set (автоматически удаляет дубликаты)
    
    return list(links)  # Преобразуем set обратно в list

def parse_category_page(url, brand, category):
    """Парсинг страницы категории товара для извлечения ссылок на модели"""
    soup = get_soup(url)
    if soup:
        model_links = extract_product_links(soup, brand, category)
        return model_links
    return []
