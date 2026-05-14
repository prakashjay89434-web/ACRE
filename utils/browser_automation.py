from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_driver():
    """Create and return a Chrome driver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def search_youtube(query: str) -> dict:
    """Open YouTube and search for a query."""
    try:
        driver = get_driver()
        driver.get("https://www.youtube.com")
        time.sleep(2)

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        return {"success": True, "message": f"Searched '{query}' on YouTube"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def send_whatsapp_message(contact: str, message: str) -> dict:
    """Open WhatsApp Web and send a message."""
    try:
        driver = get_driver()
        driver.get("https://web.whatsapp.com")

        print("Please scan WhatsApp QR code... waiting 15 seconds")
        time.sleep(15)

        # Search for contact
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            )
        )
        search_box.click()
        search_box.send_keys(contact)
        time.sleep(2)

        # Click first result
        first_contact = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//span[@title="{contact}"]')
            )
        )
        first_contact.click()
        time.sleep(1)

        # Type and send message
        msg_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            )
        )
        msg_box.click()
        msg_box.send_keys(message)
        msg_box.send_keys(Keys.RETURN)
        time.sleep(1)

        return {"success": True, "message": f"Message sent to {contact}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def send_gmail(to: str, subject: str, body: str) -> dict:
    """Open Gmail and compose an email."""
    try:
        driver = get_driver()
        driver.get("https://gmail.com")
        time.sleep(3)

        # Click Compose
        compose = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[text()="Compose"]')
            )
        )
        compose.click()
        time.sleep(1)

        # To field
        to_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "to"))
        )
        to_field.send_keys(to)
        to_field.send_keys(Keys.TAB)

        # Subject
        subject_field = driver.find_element(By.NAME, "subjectbox")
        subject_field.send_keys(subject)

        # Body
        body_field = driver.find_element(
            By.XPATH, '//div[@aria-label="Message Body"]'
        )
        body_field.send_keys(body)

        return {"success": True, "message": f"Email composed to {to}. Please review and send."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def open_url(url: str) -> dict:
    """Open any URL in Chrome."""
    try:
        driver = get_driver()
        if not url.startswith("http"):
            url = "https://" + url
        driver.get(url)
        return {"success": True, "message": f"Opened {url}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def google_search(query: str) -> dict:
    """Search on Google."""
    try:
        driver = get_driver()
        driver.get("https://www.google.com")
        time.sleep(1)

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        return {"success": True, "message": f"Searched '{query}' on Google"}
    except Exception as e:
        return {"success": False, "message": str(e)}