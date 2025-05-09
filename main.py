import json
import time
from parser import collect_all_final_pages

def main():
    brand = input("🔤 Введите название бренда (например: Sidi, Furygan): ").strip()
    start_url = f"https://www.jopa.nl/en/{brand.lower()}"

    print(f"\n🔍 Сбор конечных страниц для бренда: {brand}")
    start_time = time.time()

    final_pages = collect_all_final_pages(start_url, brand)
    print(f"📄 Найдено конечных страниц: {len(final_pages)}")

    filename = f"{brand.lower()}_final_pages.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_pages, f, ensure_ascii=False, indent=2)

    print(f"✅ Ссылки сохранены в {filename} за {time.time() - start_time:.2f} сек.")

# def collect_product_info():

if __name__ == "__main__":
    main()
