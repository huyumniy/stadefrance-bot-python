import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import os, sys
import requests
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_for_element(driver, selector, click=False, xpath=False, debug=False):
    """
    Finds a single element on a web page using Selenium.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        selector (str): The CSS or XPath selector of the element to find.
        click (bool, optional): Whether to click the element after finding it. Defaults to False.
        xpath (bool, optional): Whether the selector is an XPath expression. Defaults to False.
        debug (bool, optional): Print debug information if an error occurs. Defaults to False.

    Returns:
        WebElement or None: The found element or None if not found.
    """
    try:
        if xpath:
            element = driver.find_element(By.XPATH, selector)
        else:
            element = driver.find_element(By.CSS_SELECTOR, selector)
        if click: 
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
        return element
    except Exception as e: 
        if debug: print("selector: ", selector, "\n", e)
        return None


def check_for_elements(driver, selector, xpath=False, debug=False):
    """
    Finds multiple elements on a web page using Selenium.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        selector (str): The CSS or XPath selector of the elements to find.
        xpath (bool, optional): Whether the selector is an XPath expression. Defaults to False.
        debug (bool, optional): Print debug information if an error occurs. Defaults to False.

    Returns:
        list: A list of found WebElements or an empty list if none are found.
    """
    try:
        if xpath:
            elements = driver.find_elements(By.XPATH, selector)
        else:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
        return elements
    except Exception as e: 
        if debug: print("selector: ", selector, "\n", e)
        return []


def wait_for_element(driver, selector, timeout=10, xpath=False, debug=False):
    try:
        if xpath:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        return element
    except Exception as e:
        if debug: print("selector: ", selector, "\n", e)
        return False


def handle_captcha_solve(driver):
    """
    Handles CAPTCHA solving using the NopeCHA extension.
    """
    time.sleep(5)
    #reload the page button
    check_for_element(driver, '//*[@id="actionButtonSpan"]', xpath=True, click=True)

    #wait for the captcha to be solved
    check_for_element(driver, '//*[@id="submit_button"]', xpath=True, click=True)

    #enter page if there is queue
    check_for_element(driver, '//*[@id="actionButtonSpan"]', xpath=True, click=True)


def ensure_check_elem(driver, selector, methode=By.XPATH, tmt=20, click=False):
    """
    Ensures an element is found within a specified timeout.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        selector (str): The selector of the element to find.
        methode (By, optional): The selection method (e.g., By.XPATH). Defaults to By.XPATH.
        tmt (int, optional): The timeout in seconds. Defaults to 20.
        click (bool, optional): Whether to click the element after finding it. Defaults to False.

    Returns:
        WebElement: The found element.

    Raises:
        Exception: If the element is not found within the timeout.
    """
    var = None
    tmt0 = 0
    while True:
        if tmt0 >= tmt:
            raise Exception('Not Found')
        try:
            var = driver.find_element(methode, selector)
            if click:
                var.click()
            break
        except:
            pass
        tmt0 += 0.5
        time.sleep(0.5)
    return var

# Selenium Authorization
def loginorfindx(driver, link, email, password):
    """
    Logs into a website using Selenium or navigates to a specific page if already logged in.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        email (str): The authorizaion data
        password (str): The authorization data
        link (str): The URL to navigate to after logging in.
        email (str): The email address to use for login.
        password (str): The password associated with the email address.

    Returns:
        None
    """
    while True:
        if "/secure/selection/event/" in driver.current_url or \
           "/secured/selection/resale/" in driver.current_url:
            break

        try:
            eml = ensure_check_elem(driver, '//form[@id="frmLogin"]//input[@name="email"]', tmt=2)
            eml.clear()
            for k in email:
                eml.send_keys(k)
                time.sleep(.1)
            time.sleep(2)
            pwd = ensure_check_elem(driver, '//form[@id="frmLogin"]//input[@name="password"]', tmt=2)
            pwd.clear()
            for k in password:            
                pwd.send_keys(k)
                time.sleep(.1)
            time.sleep(4)
            try:
                driver.find_element(
                    By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
            except:
                pass
            ensure_check_elem(driver, '//button[@type="submit" and @data-skform="frmLogin"]', tmt=2, click=True)
            timer = 15
            while timer > 0:
                if 'auth.fifa.com' not in driver.current_url: 
                    break
                else:
                    timer -= 1
                    time.sleep(1)
            if link and timer > 0: driver.get(link)
        except:
            pass

# Selenium Driver Initialization
def init_selenium_driver(proxyInput):
    """
    Initializes and configures a Selenium Chrome WebDriver instance.

    Returns:
        WebDriver: The configured Selenium WebDriver instance.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--lang=EN')
    cwd= os.getcwd()
    slash = "\\" if sys.platform == "win32" else "/"
    proxy_switcher = os.path.join(cwd, cwd + slash + "BP-Proxy-Switcher-Chrome")
    captcha_solver = os.path.join(os.getcwd(), cwd + slash + "NopeCHA-CAPTCHA-Solver-Chrome")
    if proxyInput: options.add_argument(f"--load-extension={proxy_switcher},{captcha_solver},")


    chromedriver_path = os.path.join(cwd, 'chromedriver.exe')
    service = Service(executable_path=chromedriver_path)

    if os.getlogin() in [
        'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15',
        'S3U1', 'S3U2', 'S3U3', 'S3U4', 'S3U5', 'S3U6', 'S3U7', 'S3U8', 'S3U9', 'S3U10', 'S3U11', 'S3U12', 'S3U13', 'S3U14', 'S3U15', 'S3U16',
        'Admin3'
    ]:
        driver = webdriver.Chrome(
            version_main=129,
            options=options,
            enable_cdp_events=True
        )
    else:
        driver = webdriver.Chrome(
            options=options,
            enable_cdp_events=True
        )

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)


    return driver


def get_indexeddb_data(driver, db_name, store_name):
    script = f"""
    var callback = arguments[arguments.length - 1];  // Last argument is the callback for async script

    var openRequest = indexedDB.open("{db_name}");

    openRequest.onsuccess = function(event) {{
        var db = event.target.result;
        var transaction = db.transaction("{store_name}", "readonly");
        var store = transaction.objectStore("{store_name}");
        var getRequest = store.get(1);  // Assuming the data is stored under key 1, adjust if needed

        getRequest.onsuccess = function(event) {{
            var result = getRequest.result;
            if (result) {{
                callback(JSON.stringify(result.settings));  // Pass the result back to Python
            }} else {{
                callback(null);  // No result found
            }}
        }};

        getRequest.onerror = function(event) {{
            callback(null);  // Error in getting the data
        }};
    }};

    openRequest.onerror = function(event) {{
        callback(null);  // Error in opening the database
    }};
    """
    return driver.execute_async_script(script)