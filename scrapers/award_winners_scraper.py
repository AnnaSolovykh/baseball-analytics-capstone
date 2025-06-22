import os
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

URL = "https://www.baseball-almanac.com/awards/aw_mvpa.shtml"
OUTPUT_CSV = "data/raw/mvp_awards.csv"

# Set up headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    logger.info(f"Navigating to {URL}")
    driver.get(URL)

    table = driver.find_element(By.CSS_SELECTOR, "table.boxed")
    rows = table.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows[1:]:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 5:
            year = cols[0].text.strip()
            player = cols[1].text.strip()
            league = cols[2].text.strip()
            team = cols[3].text.strip()
            position = cols[4].text.strip()

            data.append({
                "year": year,
                "player_name": player,
                "league": league,
                "team": team,
                "position": position,
                "source_url": URL,
                "extraction_date": datetime.today().strftime("%Y-%m-%d")
            })

    driver.quit()

    if data:
        df = pd.DataFrame(data)
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"Extracted {len(df)} records to {OUTPUT_CSV}")
    else:
        logger.warning("No records extracted.")

except Exception as e:
    logger.error(f"Error during scraping: {e}")
    driver.quit()
