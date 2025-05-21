import json
import os
import time
import tempfile
import traceback
import requests
from dotenv import load_dotenv
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def load_products(json_path):
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


def init_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 15)
    return driver, wait


def login(driver, wait, url, username, password):
    driver.get(url)
    wait.until(EC.visibility_of_element_located((By.NAME, '_username'))).send_keys(username)
    driver.find_element(By.NAME, '_password').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sidebar')))


def inline_edit_text(driver, wait, data_name, value):
    anchor = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a.inlineedit[data-name='{data_name}']")))
    anchor.click()
    form = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form.editableform")))
    
    field = None
    for tag in ('input', 'textarea'):
        for el in form.find_elements(By.TAG_NAME, tag):
            if el.is_displayed():
                field = el
                break
        if field:
            break

    field.clear()
    field.send_keys(value)
    form.find_element(By.CSS_SELECTOR, "button.editable-submit").click()
    wait.until(EC.staleness_of(form))


def inline_edit_brand_js(driver, wait, data_name, brand_name):
    anchor = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a.inlineedit[data-name='{data_name}']")))
    anchor.click()
    form = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form.editableform")))

    sel = form.find_element(By.TAG_NAME, 'select')
    option_value = None
    for opt in sel.find_elements(By.TAG_NAME, 'option'):
        if opt.text.strip() == brand_name:
            option_value = opt.get_attribute('value')
            break

    if not option_value:
        raise RuntimeError(f"Brand '{brand_name}' not found in dropdown")

    driver.execute_script(
        """
        var select = arguments[0], val = arguments[1];
        select.value = val;
        var evt = new Event('change', { bubbles: true });
        select.dispatchEvent(evt);
        """,
        sel, option_value
    )

    wait.until(EC.staleness_of(form))


def fill_tinymce(driver, wait, data_name, text):
    try:
        header = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"h4[data-for^='{data_name}']")))
        header.click()

        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id^='mce_']")))
        driver.switch_to.frame(iframe)

        body = wait.until(EC.presence_of_element_located((By.ID, 'tinymce')))
        body.clear()
        body.send_keys(Keys.CONTROL + 'a', Keys.DELETE)
        body.send_keys(text)

        driver.switch_to.default_content()
        save_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-mce-name='save']")))
        save_btn.click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-mce-name='savedone']")))

        driver.refresh()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sidebar')))

    except Exception as e:
        print(f"Ошибка при заполнении TinyMCE для {data_name}: {e}")


def upload_images(driver, wait, image_urls):
    try:
        tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-presenter='img_galerie']")))
        tab.click()
        gallery = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.galerie_container")))
        file_input = gallery.find_element(By.CSS_SELECTOR, "input[name='upload[]']")
        driver.execute_script("arguments[0].classList.remove('hidden')", file_input)

        temp_dir = tempfile.mkdtemp()
        paths = []
        for idx, url in enumerate(image_urls):
            resp = requests.get(url, timeout=15)
            local = os.path.join(temp_dir, f"img_{idx}.jpg")
            with open(local, 'wb') as f:
                f.write(resp.content)
            paths.append(local)

        file_input.send_keys("\n".join(paths))
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.galerie_upload .galerie_telo")))

        for p in paths:
            os.remove(p)
        os.rmdir(temp_dir)

        print("✔ Изображения успешно загружены")

    except Exception as e:
        print(f"✘ Ошибка при загрузке изображений: {e}")
        traceback.print_exc()


def upload_variants(driver, wait, variants):
    try:
        tab = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[data-presenter='zbozi_varianty']")))
        tab.click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sidebar")))

        for name in variants:
            add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pridat.btn.btn-xs.btn-success")))
            add_btn.click()
            form = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form.modal.in.ui-draggable")))

            form.find_element(By.ID, 'nazev').send_keys(name)
            form.find_element(By.CSS_SELECTOR, "div.modal-footer button[type=submit]").click()
            wait.until(EC.staleness_of(form))

            wait.until(EC.visibility_of_element_located((
                By.XPATH,
                f"//a[@class='inlineedit editable editable-click' and text()='{name}']"
            )))


        print("✔ Варианты успешно добавлены")

    except Exception as e:
        print(f"✘ Ошибка при добавлении вариантов: {e}")
        traceback.print_exc()

def set_price_source_to_product(driver, wait):
    driver.get(driver.current_url)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sidebar")))

    driver.find_element(By.CSS_SELECTOR, "a[data-presenter='zbozi_detail']").click()

    price_source_link = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a.inlineedit[data-name='CZbozi.zdrojceny']")))
    price_source_link.click()

    form = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form.editableform")))

    select = form.find_element(By.TAG_NAME, "select")
    for option in select.find_elements(By.TAG_NAME, "option"):
        if option.text.strip() == "cenu určuje zboží":
            option.click()
            break

    submit_btn = form.find_element(By.CSS_SELECTOR, "button.editable-submit")
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    driver.execute_script("arguments[0].click();", submit_btn)

    wait.until(EC.staleness_of(form))

    driver.refresh()

def set_accessability(driver, wait):
    btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        'a.dostupnost.btn.btn-xs.btn-info'
    )))
    btn.click()

    select_elem = wait.until(EC.element_to_be_clickable((By.ID, "dostupnost")))
    select = Select(select_elem)
    select.select_by_value("1") 

    time.sleep(0.5)

    nastavit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nastavit.btn.btn-xs.btn-success")))
    nastavit_btn.click()


def group_products_by_subcategory(products, brand_name=None):
    grouped = defaultdict(list)
    for prod in products:
        url = prod.get("category_url", "")
        if brand_name:
            after_brand = url.split(f"/{brand_name}/", 1)[-1]
            parts = after_brand.strip("/").split("/")
            if len(parts) > 1:
                subcategory = "/".join(parts[:-1])
            else:
                subcategory = "" 
        else:
            subcategory = url.split("/")[-2]
        grouped[subcategory].append(prod)
    return grouped



def pretty_print_grouped_products(grouped_products):
    for category, products in grouped_products.items():
        print(f"{category}")
        for prod in products:
            sizes = ", ".join(prod.get('sizes', [])) or "-"
            name = prod.get('name', 'Без названия')
            print(f" - {name} Sizes: [{sizes}]")
        print()


def extract_external_id(url):
    return url.rstrip('/').split('-')[-1]

def create_product(driver, wait, prod, brand_name):
    driver.get('https://www.motobuzz.lv/admin/kategorie-1929')
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sidebar')))

    add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.pridat.btn.btn-xs.btn-success')))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.ID, 'nazev'))).send_keys(prod['name'])
    driver.find_element(By.ID, 'cena').send_keys(prod['price'].replace(',', '.'))
    driver.find_element(By.CSS_SELECTOR, '.modal-footer button[type=submit]').click()
    wait.until(EC.url_contains('/admin/kategorie-1929/zbozi-'))

    current_url = driver.current_url
    external_id = extract_external_id(current_url)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.inlineedit[data-name="CPolozka.code"]')))
    code_elem = driver.find_element(By.CSS_SELECTOR, 'a.inlineedit[data-name="CPolozka.code"]')
    internal_id = "P" + code_elem.get_attribute("data-pk")

    inline_edit_text(driver, wait, 'CPolozka.ean', prod['ean'])
    inline_edit_text(driver, wait, 'CZbozi.dodavatelurl', 'https://jopa.nl/en/')
    inline_edit_brand_js(driver, wait, 'CZbozi.vyrobce_id', brand_name)

    fill_tinymce(driver, wait, 'zbozi.popis', prod['short-description'])
    fill_tinymce(driver, wait, 'zbozi.popis2', prod['long-description'])

    upload_images(driver, wait, prod['images'])
    upload_variants(driver, wait, prod['sizes'])

    set_price_source_to_product(driver, wait)
    set_accessability(driver, wait)

    print(f"✔ Готово: {prod['name']} (internal PK: {internal_id}, external ID: {external_id}) URL: {current_url}")
    return {
        "product_url": current_url,
        "product_pk": internal_id,
        "external_id": external_id,
        "original_url": prod.get('product_url')
    }

def add_podobne_products(driver, wait, base_external_id, podobne_internal_ids):
    base_url = f"https://www.motobuzz.lv/admin/kategorie-1929/zbozi-{base_external_id}"
    driver.get(base_url)
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sidebar')))
        
    except:
        return

    podobne_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-presenter='zbozi_podobne']")))
    podobne_tab.click()

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.widget-main")))

    for pid in podobne_internal_ids:
        if pid == base_external_id:
            continue

        modal = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.widget-main.padding-8")))

        radio_label = modal.find_element(
            By.XPATH,
            ".//span[contains(@class, 'lbl') and contains(text(), 'vybrat přes filtr')]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", radio_label)
        driver.execute_script("arguments[0].click();", radio_label)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form.filtr")))
        
        search_input = modal.find_element(By.CSS_SELECTOR, "input#hledat")
        search_input.clear()
        search_input.send_keys(pid)

        filter_btn = modal.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.filtrovat")
        filter_btn.click()

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.produkty")))

        checkbox = modal.find_element(By.CSS_SELECTOR, "input[type='checkbox'].ace.zatrhnout")
        label = checkbox.find_element(By.XPATH, "./following-sibling::span[contains(@class, 'lbl')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", label)
        driver.execute_script("arguments[0].click();", label)

        select_btn = modal.find_element(By.CSS_SELECTOR, "div.table-footer a.vyber.btn.btn-xs.btn-success")
        select_btn.click()
        print(f"✔ Добавлен podobny товар с id {pid} к товару {base_external_id}")



    driver.refresh()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sidebar')))



def start_upload(file_path, brand_name):
    load_dotenv()  
    username = os.getenv("MOTOBUZZ_USERNAME")
    password = os.getenv("MOTOBUZZ_PASSWORD")
    if not username or not password:
        raise RuntimeError("Не найдены MOTOBUZZ_USERNAME или MOTOBUZZ_PASSWORD в .env")

    products = load_products(file_path)

    grouped = group_products_by_subcategory(products, brand_name)
    pretty_print_grouped_products(grouped) 

    driver, wait = init_driver()
    login(driver, wait, 'https://www.motobuzz.lv/admin/', username, password)

    created_products = [] 

    for prod in products:
        try:
            created = create_product(driver, wait, prod, brand_name)
            created_products.append(created)
            time.sleep(2)
        except Exception:
            traceback.print_exc()
            print(f"✘ Ошибка при создании {prod['name']}")

    # Создаём словари для поиска
    url_to_internal_pk = {p["original_url"]: p["product_pk"] for p in created_products}
    url_to_external_id = {p["original_url"]: p["external_id"] for p in created_products}

    print(f"Создано {len(created_products)} товаров")
    print(f"Создано {len(url_to_internal_pk)} товаров с внутренними ID")

    # Добавляем podobne для товаров из каждой подкатегории
    for subcat, prods in grouped.items():
        internal_pks = [url_to_internal_pk.get(prod['product_url']) for prod in prods if prod['product_url'] in url_to_internal_pk]

        for prod in prods:
            base_external_id = url_to_external_id.get(prod['product_url'])
            base_internal_id = url_to_internal_pk.get(prod['product_url'])

            if not base_external_id or not base_internal_id:
                continue

            podobne_internal_pks = [pk for pk in internal_pks if pk != base_internal_id]
            print(f"DEBUG: podobne_internal_pks: {podobne_internal_pks}")

            print(f"Добавляем похожие для товара с external_id={base_external_id} и internal_id={base_internal_id}")
            add_podobne_products(driver, wait, base_external_id, podobne_internal_pks)


    driver.quit()
    print("✔ Все товары загружены и связаны как подобные")