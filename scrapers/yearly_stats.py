import os
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

# Constants
URL = "https://www.baseball-almanac.com/me_award.shtml"
OUTPUT_CSV = "data/raw/me_awards_list.csv"

# Setup headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

logger.info(f"🌐 Navigating to {URL}")
driver.get(URL)
time.sleep(3)

# Extract data
try:
    tds = driver.find_elements(By.CSS_SELECTOR, "td.datacolBox")
    logger.info(f"Found {len(tds)} award blocks")

    data = []
    for td in tds:
        try:
            award_elem = td.find_element(By.TAG_NAME, "a")
            award = award_elem.text.strip()
            href = award_elem.get_attribute("href")

            small = td.find_element(By.TAG_NAME, "small")
            years = small.text.strip()

            data.append({
                "award": award,
                "years": years,
                "link": href,
                "source_url": URL,
                "extraction_date": datetime.today().strftime("%Y-%m-%d")
            })
        except Exception as e:
            continue  # silently skip malformed entries

    driver.quit()

    # Save to CSV
    if data:
        df = pd.DataFrame(data)
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"Extracted {len(df)} awards to {OUTPUT_CSV}")
    else:
        logger.warning("No records extracted.")

except Exception as e:
    logger.error(f"Error during scraping: {e}")
    driver.quit()
