# Projekta pārskats

Šī Python programma veic trīs galvenās darbības:

1. **Datu vākšana**  
   No e-veikala `jopa.nl` tiek savāktas gala preču lapas (URL), izmantojot `requests` un `BeautifulSoup`.
2. **Aprakstu ģenerēšana**  
   Katram produktam izmantojot OpenAI (caur `openrouter.ai`) ģenerējam:
   - īsu aprakstu (1 teikums, līdz 10 vārdiem)
   - detalizētu punktu aprakstu
3. **Datu augšupielāde**  
   Visu produktu informāciju (nosaukums, cena, EAN, izmēri, attēli, apraksti) automātiski augšupielādējam citas platformas administrācijas panelī (`motobuzz.lv`) ar `selenium`.

---

## Projekta uzdevums

- **Uzdevums**: no konkrēta e-veikala **jopa.nl** izvelēties visus preču nosaukumus un saistītās detaļas, ģenerēt latviešu valodā reklamtekstus un šos datus automātiski pārsūtīt uz cita e-veikala administratora interfeisu.
- **Mērķis**: pilnībā automatizēt produktu importu un aprakstu izveidi, samazinot manuālo darbu un kļūdu iespējamību.

---

## Lietotās Python bibliotēkas

| Bibliotēka            | Versija  | Lietojums                                                           |
| --------------------- | -------- | ------------------------------------------------------------------- |
| `requests`            | >=2.28.0 | HTTP pieprasījumi — lapu saturs, attēlu lejupielāde                 |
| `beautifulsoup4`      | >=4.11.0 | HTML parsēšana — elementi pēc CSS selektoriem                       |
| `selenium`            | >=4.4.0  | Automātiska pārlūkprogrammas vadība produktu augšupielādei          |
| `webdriver-manager`   | >=3.8.5  | Chromedriver automātiska pārvaldība (versiju saskaņošana)           |
| `openai`              | >=0.27.0 | API zvani uz GPT modeli aprakstu ģenerēšanai (caur `openrouter.ai`) |
| `python-dotenv`       | >=0.21.0 | .env faila ielāde — API atslēgu glabāšana drošā veidā               |
| `collections` (deque) | —        | FIFO rinda BFS (plašuma pirmā meklēšana) preču lapu vākšanai        |
| `re`                  | —        | Regulārie izteiksmes — aprakstu teksta izvilkšanai                  |
| `json`                | —        | Datu struktūru saglabāšana un ielāde `.json` formātā                |

**Kāpēc šīs bibliotēkas?**

- Viegls un uzticams HTTP ar `requests`.
- Elastīga HTML parsēšana ar `BeautifulSoup`.
- Web UI automatizācija ar `selenium` ļauj atdarināt cilvēka darbības.
- `webdriver-manager` atbrīvo no manuālas Chromedriver uzstādīšanas.
- GPT-ģenerēti apraksti ar OpenAI, izmantojot bezmaksas `openrouter.ai` modeli.

---

## Izmantotās datu struktūras

- **List (`list`)**
  - Produktu sarakstam, attēlu URL — dinamiski mainīga izmēra un ātra indeksa piekļuve.
- **Dictionary (`dict`)**
  - Katram produktam atslēga→vērtība pāriem (`name`, `price`, `ean`, `images`, `sizes`, `short-description`, `long-description`) — ērta piekļuve pēc nosaukuma.
- **Deque (`collections.deque`)**
  - FIFO rinda BFS algoritmam preču lapu vākšanai — O(1) pievienošana/izņemšana abu galā.
- **JSON**
  - Projektā saglabājam starpfailus (`*_final_pages.json`, `*_products.json`) — universāls, viegli lasāms un portējams formāts.

---

## Programmatūras izmantošanas metodes

1. **Instalēšana**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   pip install -r requirements.txt
   ```

2. **Jāpievieno .env**

   ```bash
    OPENROUTER_API_KEY="sk-or-jūsu-api-atslēga"
   ```
