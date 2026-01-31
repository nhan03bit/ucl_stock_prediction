import os
import random
import time

import pandas as pd

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

MAX_PAGES = 3  # Limit to 3 pages per stock

def get_webdriver():
    random_user_agent = random.choice(user_agents)
    options = Options()
    
    # Set user agent
    options.add_argument(f"user-agent={random_user_agent}")
    
    # Anti-detection settings
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Additional stealth settings
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--start-maximized')
    
    # Performance settings
    prefs = {
        "profile.managed_default_content_settings.images": 1,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.cookies": 1,
        "profile.managed_default_content_settings.javascript": 1,
    }
    options.add_experimental_option("prefs", prefs)
    
    # Set page load strategy
    options.page_load_strategy = 'normal'
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    # Execute CDP commands to hide webdriver
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": random_user_agent,
        "platform": "Win32",
        "userAgentMetadata": {
            "brands": [{"brand": "Google Chrome", "version": "122"}, {"brand": "Not_A Brand", "version": "8"}, {"brand": "Chromium", "version": "122"}],
            "fullVersion": "122.0.6261.69",
            "platform": "Windows",
            "platformVersion": "10.0.0",
            "architecture": "x86",
            "model": "",
            "mobile": False
        }
    })
    
    # Override navigator properties
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        window.chrome = {runtime: {}};
    """)
    
    return driver


def accept_cookies(driver):
    """Automatically accept cookies if consent banner appears."""
    try:
        # Common cookie button selectors for Nasdaq and similar sites
        cookie_button_selectors = [
            (By.ID, 'onetrust-accept-btn-handler'),
            (By.CLASS_NAME, 'accept-cookies'),
            (By.CLASS_NAME, 'cookie-accept'),
            (By.XPATH, "//button[contains(text(), 'Accept')]"),
            (By.XPATH, "//button[contains(text(), 'accept')]"),
            (By.XPATH, "//button[contains(text(), 'ACCEPT')]"),
            (By.XPATH, "//button[contains(@class, 'cookie') and contains(@class, 'accept')]"),
            (By.CSS_SELECTOR, "button[id*='accept']"),
            (By.CSS_SELECTOR, "button[class*='accept']"),
        ]
        
        for by, selector in cookie_button_selectors:
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                cookie_button.click()
                print("Cookies accepted")
                time.sleep(1)
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        
        return False
    except Exception as e:
        return False


def safe_find_element(driver, by, value):
    """Safely find element, handle possible StaleElementReferenceException."""
    try:
        content = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, value)))
        return content
    except StaleElementReferenceException:
        time.sleep(2)
        content = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, value)))
        return content


def safe_find_elements(driver, by, value):
    """Safely find elements, handle possible StaleElementReferenceException."""
    try:
        content = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((by, value)))
        return content
    except StaleElementReferenceException:
        time.sleep(2)
        content = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((by, value)))
        return content


def find_headlines(stock_name, driver, headline_file_path, headline_url, desired_page, list_df, index):
    # 'aapl'
    
    # Create headlines directory if it doesn't exist
    os.makedirs('headlines', exist_ok=True)

    driver.delete_all_cookies()
    
    # Add random delay to mimic human behavior
    time.sleep(random.uniform(1, 3))
    
    # driver.minimize_window()
    now_retry = 0
    max_retries = 3
    headlines = []
    while True:
        if now_retry == max_retries:
            return desired_page
        try:
            driver.get(headline_url)
            
            # Accept cookies if banner appears
            accept_cookies(driver)
            
            # Random delay to simulate human reading
            time.sleep(random.uniform(2, 4))
            
            # Debug: print page title and check if we're blocked
            print(f"Page title: {driver.title}")
            page_source_snippet = driver.page_source[:500] if driver.page_source else "No source"
            if "Access Denied" in page_source_snippet or "blocked" in page_source_snippet.lower():
                print("WARNING: Possible access denied or blocked page")
            
            # driver.minimize_window()

            attempts = 0

            while attempts < 2:
                try:
                    # Try multiple ways to confirm page loaded
                    try:
                        flag_loaded = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'nsdq-logo--default'))
                        )
                        print("Loaded Logo")
                        break
                    except TimeoutException:
                        # Try alternative element that might load first
                        flag_loaded = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'body'))
                        )
                        print("Loaded body (logo not found)")
                        break
                except NoSuchElementException:
                    attempts += 1
                    print(attempts, "times meet NoSuchElementException, Maybe meet Special Page")
            current_page = 0
            while True:
                headlines = []
                next_pages = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagination__page')))
                exist_next = len(next_pages) > 1
                if desired_page == 9999:
                    print("This stock has been done")
                    break
                if current_page < desired_page:
                    next_page = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'pagination__next')))
                    driver.execute_script("arguments[0].click();", next_page)
                    current_page += 1
                    if next_page.get_attribute("disabled") == "true":
                        print("Last page reached.")
                        break
                    continue
                else:
                    time.sleep(2)

                #headlines
                # headlines = WebDriverWait(driver, 20).until(
                #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'quote-news-headlines__item')))
                # Get article list items - find by LI tag with article class
                headlines = safe_find_elements(driver, By.TAG_NAME, 'li')
                
                # Filter to only article items
                article_items = []
                for item in headlines:
                    try:
                        item_class = item.get_attribute('class')
                        if 'jupiter22-c-article-list__item' in item_class:
                            article_items.append(item)
                    except:
                        continue
                
                headlines = article_items

                active_page_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pagination__page--active')))
                current_page = int(active_page_element.text)
                
                # Check if we've reached the page limit
                if current_page >= MAX_PAGES:
                    print(f"Reached page limit ({MAX_PAGES} pages). Marking as done.")
                    desired_page = 9999
                    break
                
                print(f"Page {current_page}: Found {len(headlines)} article items")

                for idx, headline in enumerate(headlines):
                    try:
                        # Debug: print what we're looking for
                        print(f"  Item {idx}: Trying to extract...")
                        
                        # Find the anchor tag with title wrapper class
                        try:
                            headline_link = headline.find_element(By.CLASS_NAME, 'jupiter22-c-article-list__item_title_wrapper')
                            print(f"    ✓ Found link element")
                        except NoSuchElementException as e:
                            print(f"    ✗ No link element found: {e}")
                            continue
                        
                        # Get the span with the actual headline text
                        try:
                            headline_title = headline_link.find_element(By.CLASS_NAME, 'jupiter22-c-article-list__item_title')
                            print(f"    ✓ Found title element")
                        except NoSuchElementException as e:
                            print(f"    ✗ No title element found: {e}")
                            continue
                        
                        headline_text = headline_title.text.strip()
                        headline_url = headline_link.get_attribute('href')
                        
                        print(f"    ✓ Text: {headline_text[:50]}...")
                        print(f"    ✓ URL: {headline_url}")
                        
                        # Make absolute URL if it's relative
                        if headline_url and not headline_url.startswith('http'):
                            headline_url = 'https://www.nasdaq.com' + headline_url
                        
                        # Try to get date/time from stamps div
                        try:
                            headline_stamps = headline.find_element(By.CLASS_NAME, 'jupiter22-c-article-list__item_stamps')
                            date_text = headline_stamps.text.strip() if headline_stamps.text else "N/A"
                        except NoSuchElementException:
                            date_text = "N/A"
                        
                        # Clean up special characters
                        headline_text_cleaned = headline_text.replace(u"\u2018", "'").replace(u"\u2019", "'")
                        
                        data = {
                            'Date': [date_text],
                            'Headline': [headline_text_cleaned],
                            'URL': [headline_url]
                        }
                        
                        # Create a DataFrame
                        df = pd.DataFrame(data)
                        # Check if file exists and is not empty
                        file_exists = os.path.isfile(headline_file_path) and os.path.getsize(headline_file_path) > 0
                        # Decide whether to write column names based on file existence
                        df.to_csv(headline_file_path, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')
                        list_df.at[index, 'Desired_page'] = desired_page
                        list_df.to_csv(list_file_path, index=False)
                        print(f"  ✓ Saved: {headline_text_cleaned[:60]}...")
                    except Exception as e:
                        print(f"  ✗ Error extracting headline: {str(e)[:80]}")
                        continue
                # Next page button
                next_page = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pagination__next')))
                # next_page = next_pages[0]
                # Only one page
                if not exist_next:
                    print("Only one page")
                    desired_page = 9999
                    break
                if next_page.get_attribute("disabled") == "true":
                    print("Last page reached.")
                    desired_page = 9999
                    break
                print("current_page:", current_page)
                desired_page = current_page

                # Click the next page button
                driver.execute_script("arguments[0].click();", next_page)
            return desired_page
        except TimeoutException:
            # Debug: print what we can see on the page
            print(f"Timeout for {stock_name}. Page title: {driver.title}")
            print(f"Current URL: {driver.current_url}")
            
            try:
                # Find <h1> tag in page to check if it's a special case
                h2_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'alert__heading')))
                # Exit loop after finding match
                for h2 in h2_elements:
                    if h2.text.find("trading") != -1:
                        print("time out, finding alerts")
                        print("Alert found")
                        desired_page = 9999
                        return desired_page
            except TimeoutException:
                # Check if we can at least see the page content
                try:
                    body = driver.find_element(By.TAG_NAME, 'body')
                    body_text = body.text[:200] if body.text else "Empty body"
                    print(f"Body text preview: {body_text}")
                except:
                    print("Cannot access body element")
                
                print(f"Time out or wrong url for {stock_name} - marking as done (9999)")
                desired_page = 9999
                return desired_page
        except ElementClickInterceptedException:
            print("button missed, desired_page:", desired_page)
            return desired_page
        except NoSuchWindowException:
            print("closed window manually, desired_page:", desired_page)
            print("5 sec later, driver will restart, if you want to TERMINATE this process please be quick")
            time.sleep(15)
            driver = get_webdriver()
            return desired_page
        except StaleElementReferenceException:
            now_retry += 1
            print("maybe too fast, elements weren't ready, desired_page:", desired_page)
            try:
                WebDriverWait(driver, 20).until(
                    EC.staleness_of(headlines[0])
                )
            except Exception:
                pass
            continue
            # return desired_page


def start_find(list_df):
    for index, row in list_df.iloc[start_row_index:].iterrows():
        print("start: ", row["Stock_name"], "from:", row["Desired_page"])
        if row["Desired_page"] == 9999:
            print("This stock Has been done")
            continue
        driver = get_webdriver()
        # print("index: ", index)
        stock_name = str(row['Stock_name'])
        headline_file_path = "headlines/" + stock_name + ".csv"
        headlines_url = "https://www.nasdaq.com/market-activity/stocks/" + stock_name + "/news-headlines"
        Desired_page = find_headlines(stock_name, driver, headline_file_path, headlines_url, row['Desired_page'], list_df, index)
        try:
            driver.close()
        except:
            pass  # Driver already closed
        list_df.at[index, 'Desired_page'] = Desired_page
        print("now desired_page: ", list_df.loc[row.name, 'Desired_page'])
        list_df.to_csv(list_file_path, index=False)
        print(list_df)
    return list_df


if __name__ == "__main__":
    # find_headlines("aapl")
    inits = input("from which list:")
    start_row_index = 0
    for init in inits:
        list_file_path = 'lists/list_' + init + '.csv'
        if not os.path.isfile(list_file_path):
            print("!!! Wrong list_name !!!")
        else:
            list_df = pd.read_csv(list_file_path, encoding="utf-8")
            while not list_df['Desired_page'].isin([9999]).all():
                print("need find")
                list_df = start_find(list_df)
            print("list_", init, "completed")

    # Parameter is the stock symbol