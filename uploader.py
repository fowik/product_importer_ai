import json
import os
import time
import tempfile
import traceback
import requests
from dotenv import load_dotenv

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

    # Находим первый видимый input или textarea
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


def create_product(driver, wait, prod, brand_name):
    driver.get('https://www.motobuzz.lv/admin/kategorie-1929')
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sidebar')))

    # 1) Create new product
    add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.pridat.btn.btn-xs.btn-success')))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.ID, 'nazev'))).send_keys(prod['name'])
    driver.find_element(By.ID, 'cena').send_keys(prod['price'].replace(',', '.'))
    driver.find_element(By.CSS_SELECTOR, '.modal-footer button[type=submit]').click()
    wait.until(EC.url_contains('/admin/kategorie-1929/zbozi-'))

    # 2) Edit product details
    inline_edit_text(driver, wait, 'CPolozka.ean', prod['ean'])
    inline_edit_text(driver, wait, 'CZbozi.dodavatelurl', 'https://jopa.nl/en/')
    inline_edit_brand_js(driver, wait, 'CZbozi.vyrobce_id', brand_name)

    # 3) Fill descriptions
    fill_tinymce(driver, wait, 'zbozi.popis', prod['short-description'])
    fill_tinymce(driver, wait, 'zbozi.popis2', prod['long-description'])

    # 4) Upload images and variants
    upload_images(driver, wait, prod['images'])
    upload_variants(driver, wait, prod['sizes'])

    print(f"✔ Готово: {prod['name']}")


def start_upload(file_path, brand_name):
    load_dotenv()  
    username = os.getenv("MOTOBUZZ_USERNAME")
    password = os.getenv("MOTOBUZZ_PASSWORD")
    if not username or not password:
        raise RuntimeError("Не найдены MOTOBUZZ_USERNAME или MOTOBUZZ_PASSWORD в .env")

    products = load_products(file_path)
    driver, wait = init_driver()
    login(driver, wait, 'https://www.motobuzz.lv/admin/', username, password)

    for prod in products:
        try:
            create_product(driver, wait, prod, brand_name)
            time.sleep(2)
        except Exception:
            traceback.print_exc()
            print(f"✘ Ошибка при создании {prod['name']}")

    driver.quit()