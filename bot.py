import time
from selenium.webdriver.common.by import By
from random import choice, randint
from selenium.webdriver.support.ui import Select
import soundfile as sf
import sounddevice as sd
from helpers import find_category_value, ua
from selenium_helpers import loginorfindx, check_for_element, \
 check_for_elements, ensure_check_elem, init_selenium_driver, \
 get_indexeddb_data, handle_captcha_solve, wait_for_element
from data_processing import genselx
import eel
import socket
import threading


INPUT='input.xlsx'
isInitialRun = True

def run(thread, link, time_to_wait, browsersAmount, proxyInput):
    global isInitialRun
    selxs_static=genselx(xlsx_name=INPUT)

    driver = init_selenium_driver(proxyInput)
    driver.get(link)
    if proxyInput != '':
        driver.get('chrome://extensions/')
        time.sleep(1)

        # Example script to retrieve extensions
        script_array = """
                    const callback = arguments[0];
                    chrome.management.getAll((extensions) => {
                        callback(extensions);
                    });
                """

        # Execute the JavaScript and get the result
        extensions = driver.execute_async_script(script_array)
        filtered_extensions = [extension for extension in extensions if "BP Proxy Switcher" in extension['name']]

        extension_id = [extension['id'] for extension in filtered_extensions if 'id' in extension][0]
        extension_url = f'chrome-extension://{extension_id}/popup.html'
        driver.get(extension_url)
        # proxies = parse_data_from_file('proxies.txt')
        delete_tab = driver.find_element(By.XPATH, '//*[@id="deleteOptions"]')
        driver.execute_script("arguments[0].scrollIntoView();", delete_tab)
        delete_tab.click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="privacy"]/div[1]/input').click()
        driver.find_element(By.XPATH, '//*[@id="privacy"]/div[2]/input').click()
        driver.find_element(By.XPATH, '//*[@id="privacy"]/div[4]/input').click()
        driver.find_element(By.XPATH, '//*[@id="privacy"]/div[7]/input').click()
        optionsOK = driver.find_element(By.XPATH, '//*[@id="optionsOK"]')
        driver.execute_script("arguments[0].scrollIntoView();", optionsOK)
        optionsOK.click()
        time.sleep(1)
        edit = driver.find_element(By.XPATH, '//*[@id="editProxyList"]/small/b')
        driver.execute_script("arguments[0].scrollIntoView();", edit)
        edit.click()
        time.sleep(1)
        text_area = driver.find_element(By.XPATH, '//*[@id="proxiesTextArea"]')
        text_area.send_keys(proxyInput)
        time.sleep(1)
        ok_button = driver.find_element(By.XPATH, '//*[@id="addProxyOK"]')
        driver.execute_script("arguments[0].scrollIntoView();", ok_button)
        ok_button.click()
        time.sleep(3)
        proxy_switch_list = driver.find_elements(By.CSS_SELECTOR, '#proxySelectDiv > div > div > ul > li')
        if len(proxy_switch_list) == 3: proxy_switch_list[2].click()
        else: proxy_switch_list[randint(2, len(proxy_switch_list))-1].click()
        time.sleep(5)
        proxy_auto_reload_checkbox = driver.find_element(By.XPATH, '//*[@id="autoReload"]')
        driver.execute_script("arguments[0].scrollIntoView();", proxy_auto_reload_checkbox)
        proxy_auto_reload_checkbox.click()
        time.sleep(2)

    driver.get('https://nopecha.com/setup#awscaptcha_auto_open=false|awscaptcha_auto_solve=true|awscaptcha_solve_delay=true|awscaptcha_solve_delay_time=1000|disabled_hosts=|enabled=true|funcaptcha_auto_open=false|funcaptcha_auto_solve=false|funcaptcha_solve_delay=true|funcaptcha_solve_delay_time=1000|geetest_auto_open=false|geetest_auto_solve=true|geetest_solve_delay=true|geetest_solve_delay_time=1000|hcaptcha_auto_open=true|hcaptcha_auto_solve=true|hcaptcha_solve_delay=true|hcaptcha_solve_delay_time=3000|sub_1QsSuQCRwBwvt6ptjP0yralq|keys=|lemincaptcha_auto_open=false|lemincaptcha_auto_solve=true|lemincaptcha_solve_delay=true|lemincaptcha_solve_delay_time=1000|perimeterx_auto_solve=false|perimeterx_solve_delay=true|perimeterx_solve_delay_time=1000|recaptcha_auto_open=false|recaptcha_auto_solve=false|recaptcha_solve_delay=true|recaptcha_solve_delay_time=2000|textcaptcha_auto_solve=true|textcaptcha_image_selector=#img_captcha|textcaptcha_input_selector=#secret|textcaptcha_solve_delay=true|textcaptcha_solve_delay_time=100|turnstile_auto_solve=false|turnstile_solve_delay=true|turnstile_solve_delay_time=1000')

    while True:
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {"userAgent": ua()})
        time.sleep(2)
        driver.execute_script(f"window.open('{link}/','_self')")
        check_for_element(driver, '//*[@id="onetrust-accept-btn-handler"]', xpath=True, click=True)

        if isInitialRun and 'peak35' not in driver.current_url:
            print('initialRun')
            cookie_button = wait_for_element(driver, '//*[@id="didomi-notice-agree-button"]', timeout=30, xpath=True, debug=True)
            print(cookie_button, 'cookie_button')
            if cookie_button:
                time.sleep(5)
                print('trying to click')
                check_for_element(driver, '//*[@id="didomi-notice-agree-button"]', xpath=True, click=True, debug=True)
                isInitialRun = False

        if 'peak35' in driver.current_url: handle_captcha_solve(driver)
        bskt=0
        time.sleep(.5)
        categ_sels=[]
        selected_category = None
        
        title_raw = check_for_element(driver, '.product_title_container > p')
        title = title_raw.text if title_raw else None

        if title is None:
            print('Не вдалось знайти назву матчу')
            time.sleep(time_to_wait)
            continue
        main_match = [i for i in selxs_static if i.get('match') == title]
        if not main_match: 
            print('Такого матчу не існує в таблиці.')
            time.sleep(time_to_wait)
            continue
        
        if check_for_element(driver, 'section[style="display: block;"][id="no_ticket_on_sale"]'):
            print('No tickets on sale.')
            time.sleep(time_to_wait)
            continue

        all_category_names = sorted({category['name'] for category in \
         main_match[0]['categories'] if category['value'] != 0})
        if len(all_category_names) == 0:
            print('Немає даних на цю подію в таблиці.')
            time.sleep(time_to_wait)
            continue
        
        # RESALE
        if 'resale' in driver.current_url:
            start_over = False
            no_filtration = False

            seat_categories_table_raw = check_for_elements(driver, \
            '//div[@id="seat_categories_table"]//label/span', xpath=True, debug=True)
            seat_categories_table =\
            [seat_category.text for seat_category in seat_categories_table_raw]
            
            if seat_categories_table_raw:
                for seat_category in seat_categories_table_raw:
                    if seat_category.text in all_category_names:
                        categ_sels.append(\
                        f'//tr[.//td[contains(., "{seat_category.text}")]]')
                        time.sleep(1)
                        seat_category.click()
            else:
                categ_sels.append(\
                        f'//tr[.//td[contains(., " ")]]')
                no_filtration = True
            if start_over or categ_sels == []:
                print('Немає необхідних категорій')
                time.sleep(time_to_wait)
                continue
            # input('continue?')
            # data = get_indexeddb_data(driver, 'TicketBotDB', 'settings')
            # print(data)
            # ADD TICKET
            seats = []
            seats_obj = []
            last_added_seat_number = None
            last_added_block_row = None
            previous_category = None
            temp_cat_obj = {}
            filled_cat_obj = False
            while True:
                for itm in driver.find_elements(By.XPATH, "|".join(categ_sels)):
                    category_info_raw = None
                    category_info = None
                    category_info_raw = check_for_element(itm, 
                        './/td[@class="resale-item-seatCat category"]/div/span[2]', xpath=True)
                    if category_info_raw: category_info = category_info_raw.text
                    if len(seats) >= 6 or filled_cat_obj:
                        break

                    
                    current_pagination = check_for_element(driver, '//span[@class="page current"]/a', xpath=True)
                    current_pagination = current_pagination.text if current_pagination else None

                    
                    try:
                        seat_info_raw = check_for_element(itm, \
                        './/td[@class="resale-item-seatPath seatPath"]', xpath=True)

                        seat_info = seat_info_raw.text

                        parts = seat_info.split(" - ")
                        print(parts, 'parts')
                        block, row, seat = parts[-3], parts[-2], parts[-1]

                        seat_number = int(seat)
                        current_block_row = block + " " + row
                        
                        if not no_filtration:
                            if last_added_block_row != current_block_row or \
                            (last_added_seat_number is not None and \
                            abs(seat_number - last_added_seat_number) not in (1, 2)):
                                seats.clear()
                                seats_obj.clear()
                                temp_cat_obj = {}
                        elif no_filtration:
                            if category_info not in all_category_names or \
                            last_added_block_row != current_block_row or \
                            (last_added_seat_number is not None and \
                            abs(seat_number - last_added_seat_number) not in (1, 2)):
                                seats.clear()
                                seats_obj.clear()
                                temp_cat_obj = {}
                        if not temp_cat_obj.get(category_info):
                            temp_cat_obj[category_info] = 0
                        if temp_cat_obj.get(category_info) or temp_cat_obj.get(category_info) == 0:
                            if temp_cat_obj[category_info] < find_category_value(main_match[0]['categories'], category_info):
                                seats.append(seat_info)
                                seats_obj.append({'selenium_obj':itm,\
                                'seat_info':seat_info, 'pagination_level': current_pagination})
                                temp_cat_obj[category_info] += 1
                            elif temp_cat_obj[category_info] >= find_category_value(main_match[0]['categories'], category_info):
                                filled_cat_obj = True
                        last_added_block_row = current_block_row
                        last_added_seat_number = seat_number
                    except Exception as e:
                        print(e)
                        pass
                if start_over: break
                pagination_next = check_for_element(driver, \
                '//span[@class="page next"]', xpath=True, click=True)
                
                if not pagination_next:
                    while True:
                        pagination_first = check_for_element(driver, \
                        '//span[@class="page previous"]/a',\
                        xpath=True, click=True)
                        if not pagination_first: break
                    break
            if start_over: 
                print('No tickets')
                time.sleep(time_to_wait)
                continue
            if filled_cat_obj == False: 
                print('Недостатньо квитків було знайдено')
                time.sleep(time_to_wait)
                continue
            else:
                time.sleep(1)
                for seat_obj in seats_obj:
                    print(seat_obj)
                    if seat_obj.get('pagination_level') is not None:
                        check_for_element(driver, \
                        f"//span[@class='page ']/a[contains(text(),'{seat_obj['pagination_level']}')]", xpath=True, click=True)
                    
                    check_for_element(driver, f".//td[@class='resale-item-seatPath seatPath'][contains(normalize-space(text()), '{seat_obj['seat_info']}')]", xpath=True, click=True, debug=True)
        # OFFICIAL
        elif 'fcfs' in driver.current_url:   
            
            selected_category = choice(all_category_names)
            categ_sels.append(f'//tr[.//th[contains(., "{selected_category}")]]//select[@aria-label="Quantity"]')

            for itm in range(len(driver.find_elements(By.XPATH, "|".join(categ_sels)))):
                if bskt>=6:
                    break
                try:
                    selected_value = find_category_value(main_match[0]['categories'], selected_category) 
                    elem = ensure_check_elem(driver, "|".join(categ_sels),click=True,tmt=1)
                    dropdown = Select(elem)
                    
                    dropdown.select_by_value(str(selected_value))
                    bskt+=1
                except Exception as e:
                    print(e)
                    pass

        while True:
            try:
                itms = driver.find_elements(By.XPATH, "|".join(categ_sels))
                break
            except:
                try:
                    dlk = driver.find_element(
                        By.XPATH, '//*[contains(text(),"There are currently no available tickets to resell, please visit us frequently to check availability")]')
                    itms = []
                    break
                except:
                    pass

        if len(itms) != 0:
            ensure_check_elem(driver, '//*[@id="book"]', click=True)
            try:
                ensure_check_elem(driver, '//*[@id="restart"]', click=True, tmt=2)
            except Exception as dd:
                try:
                    ensure_check_elem(driver, '//*[@id="addOtherProducts"]', tmt=2)
                    data_play, fs = sf.read('noti.wav', dtype='float32')  
                    sd.play(data_play, fs)
                    status = sd.wait()
                    input('TAP ENTER TO FIND OTHER TIKETS')
                except:
                    pass
        time.sleep(time_to_wait)   


@eel.expose
def main(initialUrl, updateInterval, browsersAmount, proxyInput):
    print(initialUrl, updateInterval, browsersAmount, proxyInput)
    # eel.spawn(run(initialUrl, isSlack, browserAmount, proxyList))
    threads = []
    if browsersAmount != '' and browsersAmount != '0':
        for idx in range(1, int(browsersAmount)+1):
            if idx!= 1: time.sleep(idx*30)
            thread = threading.Thread(
                target=run,
                args=(
                    idx,
                    initialUrl,
                    int(updateInterval),
                    browsersAmount,
                    proxyInput,
                )
            )
            threads.append(thread)
            thread.start()
        

    for thread in threads:
        thread.join()


def is_port_open(host, port):
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect((host, port))
    return True
  except (socket.timeout, ConnectionRefusedError):
    return False
  finally:
    sock.close()


if __name__ == "__main__":
    eel.init('gui')

    port = 8000
    while True:
        try:
            if not is_port_open('localhost', port):
                eel.start('main.html', size=(600, 800), port=port)
                break
            else:
                port += 1
        except OSError as e:
            print(e)
    # main()