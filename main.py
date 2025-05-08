# main.py
from parser import parse_category_page

def main():
    # Ввод пользователем бренда и категории
    brand = input("Enter brand: ")
    category = input("Enter category: ")

    # Формируем URL для поиска товаров по категории
    url = f"https://www.jopa.nl/en/{brand}/{category}/"  # URL для категории
    print(f"Fetching models from {url}")
    
    # Парсим страницу категории и извлекаем ссылки на модели
    model_links = parse_category_page(url, brand, category)
    
    # Выводим все найденные ссылки на модели
    for link in model_links:
        print(link)

if __name__ == "__main__":
    main()
