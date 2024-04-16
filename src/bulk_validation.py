import logging
import os
import random
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

def upload_and_scrape_chrome(xml_file_path, rule_set_value):
    url = "https://peppol-tools.ademico-software.com/ui/document-validator"

    logging.info("at the top of webscraping")
    # Set up Chrome WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--headless")
    ua = UserAgent(browsers=['chrome'])
    chrome_options.add_argument(f"user-agent={random.choice(ua.random)}")

    logging.info("user-options")
    # Initialize Chrome WebDriver using WebDriver Manager
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
        driver.get(url)

        logging.info("get-url")
        # Locate and interact with the file input element to upload the XML file
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "customFile")))
        absolute_path = os.path.abspath(xml_file_path)
        file_input.send_keys(absolute_path)

        logging.info("file_input")
        # Locate and click the desired option within the rule set select
        desired_option = driver.find_element(
            By.XPATH, f"//option[text()='{rule_set_value}']")
        desired_option.click()
        logging.info("rule_set_value")
        # Wait for validation result
        time.sleep(random.uniform(5, 10))

        validate_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
        # driver.execute_script("arguments[0].scrollIntoView();", validate_button)

        # Wait for a moment to ensure everything is ready
        time.sleep(1)

        # Click the validate button
        validate_button.click()
        logging.info("validate_button")
        # Define regex patterns for HTML cleanup
        pattern = re.compile(r'(.*?XML document)', re.DOTALL)
        pattern2 = re.compile(
            r'<div class="container h-100">\s*<!--\s*<span'
            r'th:if="\${report != null}" th:text="\${report.globalStatus}"></span>\s*-->')
        pattern3 = re.compile(r'<head>[\s\S]*?</head>')
        pattern4 = re.compile(r' class="[^"]*"[^>]*>', re.IGNORECASE)
        pattern5 = re.compile(r'</html>[\s\S]*$', re.IGNORECASE)

        match = re.search(pattern, driver.page_source)
        logging.info("patterns")
        with open('validation.html', 'w+') as file:
            result = re.sub(pattern2, '', match.group(1))
            lines = result.split('\n')
            modified_result = '\n'.join(lines[:-5])
            modified_result2 = re.sub(pattern, '', modified_result)
            modified_result3 = re.sub(pattern3, '', modified_result2)
            modified_result4 = re.sub(pattern4, '>', modified_result3)
            modified_result5 = re.sub(pattern5, '', modified_result4)
            soup = BeautifulSoup(modified_result5, 'html.parser')
            file.seek(0)
            file.truncate()
            file.write(f"{soup.prettify()}")
