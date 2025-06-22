import os
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

URL = "https://www.baseball-almanac.com/family/fam1.shtml"
OUTPUT_CSV = "data/raw/baseball_brothers_sets.csv"

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

logger.info(f"Navigating to {URL}")
driver.get(URL)
time.sleep(2)

try:
    table = driver.find_element(By.CSS_SELECTOR, "table.boxed")
    tds = table.find_elements(By.TAG_NAME, "td")

    data = []
    current_set = None
    current_names = []

    for td in tds:
        class_name = td.get_attribute("class").strip()
        text = td.text.strip()

        if "datacolBlueR" in class_name and text.strip(".").isdigit():
            if current_set and current_names:
                data.append({
                    "set_number": current_set,
                    "brothers_count": len(current_names),
                    "brothers_names": ";".join(current_names),
                    "source_url": URL,
                    "extraction_date": pd.Timestamp.now().isoformat()
                })
            current_set = int(text.strip("."))
            current_names = []

        elif "datacolBox" in class_name and text:
            current_names.append(text)

    if current_set and current_names:
        data.append({
            "set_number": current_set,
            "brothers_count": len(current_names),
            "brothers_names": ";".join(current_names),
            "source_url": URL,
            "extraction_date": pd.Timestamp.now().isoformat()
        })

    driver.quit()

    if data:
        df = pd.DataFrame(data)
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"✅ Extracted {len(df)} records to {OUTPUT_CSV}")
    else:
        logger.warning("⚠️ No records extracted.")

except Exception as e:
    logger.error(f"Error during scraping: {e}")
    driver.quit()
