import re
from collections import deque
from typing import List, Optional, Dict, Any

from bs4 import BeautifulSoup

from net_utils import safe_request
from ai_description import generate_description

BASE_URL = "https://www.jopa.nl"


def collect_all_final_pages(start_url: str, brand: str) -> List[str]:
    visited, queue, final_pages = set(), deque([start_url]), []
    brand_pattern = f"/en/{brand.lower()}/"

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        resp = safe_request(url)
        if not resp:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        if soup.select_one("div.artikel"):
            final_pages.append(url)

        for a in soup.select(f"a[href*='{brand_pattern}']"):
            href = a.get("href")
            if href:
                full = href if href.startswith("http") else BASE_URL + href
                if full not in visited:
                    queue.append(full)

    return final_pages


def parse_product_page(url: str) -> Optional[Dict[str, Any]]:
    resp = safe_request(url)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    tegel = soup.select_one("div.shopTegel a.link")
    if not tegel or "href" not in tegel.attrs:
        return None

    href = tegel["href"]
    product_url = href if href.startswith("http") else BASE_URL + href

    resp2 = safe_request(product_url)
    if not resp2:
        return None

    soup2 = BeautifulSoup(resp2.text, "html.parser")
    return {
        "category_url": url,
        "product_url":  product_url,
        "name":         extract_name(soup2),
        "images":       extract_images(soup2),
        "price":        extract_price(soup2),
        "ean":          extract_ean(soup2),
        "sizes":        extract_sizes(soup),
        **extract_descriptions(soup2)
    }

def extract_name(soup: BeautifulSoup) -> str:
    tag = soup.select_one("div.omschrijving h1")
    name = tag.get_text(strip=True) if tag else "No name"
    return re.sub(r"\s\d+$", "", name)


def extract_images(soup: BeautifulSoup) -> List[str]:
    return [img["src"] for img in soup.select("div.carousel-cell-groot img") if img.get("src")]


def extract_price(soup: BeautifulSoup) -> str:
    tag = soup.select_one("span.displayprijs")
    if not tag:
        return "Not found"
    texts = tag.find_all(string=True, recursive=False)
    return texts[0].strip() if texts else "Not found"


def extract_ean(soup: BeautifulSoup) -> str:
    tag = soup.select_one("div.EANnummer span:nth-of-type(2)")
    return tag.get_text(strip=True) if tag else "Not found"


def extract_sizes(soup: BeautifulSoup) -> List[str]:
    sizes = []
    for tegel in soup.select("div.shopTegel a.link"):
        nummer = tegel.find_next("span", class_="nummer")
        if nummer:
            parts = nummer.get_text(strip=True).split("-")
            if len(parts) > 1:
                sizes.append(parts[1])
    return sorted(set(sizes))

def extract_descriptions(soup):
    name = extract_name(soup)
    raw = generate_description(name, "Sidi")

    short, long = "", ""
    m = re.search(r"1\.\s*Īsais:\s*(.+?)\s*2\.\s*Garais:\s*(.+)", raw, re.S)
    if m:
        short = m.group(1).strip()
        long = m.group(2).strip()

    return {"short-description": short, "long-description": long}



def get_product_details(category_url: str) -> Optional[Dict[str, Any]]:
    try:
        data = parse_product_page(category_url)
        if data:
            print(f"✔ Parsed: {data['name']}")
        return data
    except Exception as e:
        print(f"✘ Ошибка парсинга {category_url}: {e}")
        return None
