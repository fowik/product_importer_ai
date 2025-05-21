import os
import sys
import json
import time

from parser import collect_all_final_pages, get_product_details
from uploader import start_upload


OUTPUT_DIR = "output"
DETAILS_DIR = "product_details"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_pages_flow():
    brand = input("🔤 Введите название бренда (например: Sidi, Furygan): ").strip()
    start_url = f"https://www.jopa.nl/en/{brand.lower()}"

    print(f"\n🔍 Сбор конечных страниц для бренда: {brand}")
    t0 = time.time()

    pages = collect_all_final_pages(start_url, brand)
    print(f"📄 Найдено {len(pages)} страниц за {time.time() - t0:.2f} сек.")

    ensure_dir(OUTPUT_DIR)
    out_path = os.path.join(OUTPUT_DIR, f"{brand.lower()}_final_pages.json")
    save_json(pages, out_path)

    print(f"✅ Ссылки сохранены в {out_path}")


def get_products_flow():
    brand = input("🔤 Введите название бренда: ").strip().lower()
    pages_file = os.path.join(OUTPUT_DIR, f"{brand}_final_pages.json")

    if not os.path.exists(pages_file):
        print(f"❌ Файл {pages_file} не найден.")
        sys.exit(1)

    with open(pages_file, "r", encoding="utf-8") as f:
        pages = json.load(f)

    print(f"📄 Обрабатываем {len(pages)} страниц...")
    products = []
    for i, url in enumerate(pages, 1):
        print(f"  {i}/{len(pages)}: {url}")
        products.append(get_product_details(brand, url))

    ensure_dir(DETAILS_DIR)
    out_path = os.path.join(DETAILS_DIR, f"{brand}_products.json")
    save_json(products, out_path)
    print(f"✅ Данные сохранены в {out_path}")


def upload_flow():
    brand = input("🔤 Введите название бренда: ").strip().lower()
    brand = brand.replace(" ", "-")
    details_file = os.path.join(DETAILS_DIR, f"{brand}_products.json")

    if not os.path.exists(details_file):
        print(f"❌ Файл {details_file} не найден.")
        sys.exit(1)

    print(f"🚀 Запуск загрузки из {details_file}...")
    start_upload(details_file, brand.replace("-", " ").upper())
    print("✅ Загрузка завершена")


def main():
    actions = {
        "1": ("Собрать ссылки на страницы", collect_pages_flow),
        "2": ("Получить JSON продуктов", get_products_flow),
        "3": ("Загрузить на сайт", upload_flow),
    }

    print("Выберите действие:")
    for key, (descr, _) in actions.items():
        print(f"  {key}. {descr}")

    choice = input("Введите номер действия: ").strip()
    action = actions.get(choice)
    if not action:
        print("❌ Неверный выбор.")
        sys.exit(1)

    _, func = action
    func()


if __name__ == "__main__":
    main()
