import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tqdm import tqdm

# Load JSON exhibitor IDs
with open('hits.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

exhibitors = data['DATA']['results']['exhibitor']['hit']
exhids = [exh['fields']['exhid_l'] for exh in exhibitors]

# Configure Selenium (headless Chrome)
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')

driver = webdriver.Chrome(options=options)


# def get_exhibitor_data(exhid):
#     url = f"https://sff2025.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid={exhid}"
#     driver.get(url)
#     time.sleep(3)

#     def safe_find(selector):
#         try:
#             return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
#         except:
#             return ""

#     return {
#         'name': safe_find("h1"),
#         'address': safe_find(".contact-info"),  # <--- likely class for address
#         "contact": safe_find(".address.column.address p"),  # Adjust based on actual HTML structure
#     }


def get_exhibitor_data(exhid):
    url = f"https://sff2025.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid={exhid}"
    driver.get(url)
    time.sleep(3)  # wait for JS to render

    def safe_text(by, selector, multiple=False):
        try:
            if multiple:
                return [e.text.strip() for e in driver.find_elements(by, selector)]
            return driver.find_element(by, selector).text.strip()
        except:
            return "" if not multiple else []

    # Extract fields
    name = safe_text(By.CSS_SELECTOR, 'h1')
    website = safe_text(By.CSS_SELECTOR, '.contact-info')
    booth = safe_text(By.CSS_SELECTOR, 'a#newfloorplanlink')
    address_parts = safe_text(By.CSS_SELECTOR, 'address.column.address p', multiple=True)
    address = ""
    if address_parts:
        if len(address_parts) >= 1:
            address += address_parts[0] + ", "
        if len(address_parts) >= 2:
            address += address_parts[1] + ", "
        if len(address_parts) >= 3:
            address += address_parts[2]


    return {
        'name': name,
        'address': address,
        'website': website,
        'booth': booth
    }


# Scrape all
results = []
for exhid in tqdm(exhids[:5]):  # Use [:10] to test first; remove slice for full run
    data = get_exhibitor_data(exhid)
    results.append(data)

driver.quit()

# Save to CSV
df = pd.DataFrame(results)
df.to_csv('exhibitor_details.csv', index=False)
