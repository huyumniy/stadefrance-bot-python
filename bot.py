import time
from selenium.webdriver.common.by import By
from random import choice, randint, sample
from selenium.webdriver.support.ui import Select
import soundfile as sf
import sounddevice as sd
from helpers import find_category_value, ua, parse_seat_info, match_seat_info
from selenium_helpers import loginorfindx, check_for_element, \
 check_for_elements, ensure_check_elem, init_selenium_driver, \
 get_indexeddb_data, handle_captcha_solve, wait_for_element, \
 add_proxy_switcher
from data_processing import genselx
import eel
import socket
import threading
from collections import defaultdict


class TicketManager:
    def __init__(self, driver, main_match, categories, time_to_wait):
        self.driver = driver
        self.main_match = main_match
        self.categories = categories
        self.time_to_wait = time_to_wait

    def filter(self):
        raise NotImplementedError

    def select(self):
        raise NotImplementedError

    def add_to_cart(self):
        raise NotImplementedError

    def sort(self):
        raise NotImplementedError


class ResaleTicketManager(TicketManager):
    def filter(self):
        seat_categories = check_for_elements(self.driver, 
            '//div[@id="seat_categories_table"]//label/span', xpath=True)
        if not seat_categories:
            return False
        valid_categories = [cat.text for cat in seat_categories if cat.text in self.categories]

        if not valid_categories:
            print('No valid resale categories found.')
            time.sleep(self.time_to_wait)
            return []

        for category in seat_categories:
            if category.text in valid_categories:
                category.click()
                time.sleep(1)
        return valid_categories

    def collect(self, valid_categories):
        seats_obj = []

        categ_sels = [
            f'//tr[.//td[contains(., "{cat}")]]' for cat in valid_categories
        ] if valid_categories else ['//tr[@class="resale-row"]']

        while True:
            for itm in self.driver.find_elements(By.XPATH, "|".join(categ_sels)):
                category_info_raw = check_for_element(itm, './/td[@class="resale-item-seatCat category"]/div/span[2]', xpath=True)
                category_info = category_info_raw.text if category_info_raw else None

                current_pagination = check_for_element(self.driver, '//span[@class="page current"]/a', xpath=True)
                current_pagination = current_pagination.text if current_pagination else None

                seat_info_raw = check_for_element(itm, './/td[@class="resale-item-seatPath seatPath"]', xpath=True)
                seat_info = match_seat_info(seat_info_raw.text)
                seats_obj.append({  'category': category_info,
                                    'seat_info': seat_info,
                                    'name': seat_info_raw.text,
                                    'pagination_level': current_pagination})

            pagination_next = check_for_element(self.driver, '//span[@class="page next"]', xpath=True, click=True)
            if not pagination_next:
                while True:
                    pagination_first = check_for_element(self.driver, '//span[@class="page previous"]/a', xpath=True, click=True)
                    if not pagination_first:
                        break
                break
        
        return seats_obj

    
    def select(self, data, requests):
        """
        data: list of dicts, some of which may have 'seat_info': None
        requests: as before
        """
        MAX_SEATS = 6
        output = {}

        for req in requests:
            temp = {}
            for cat in req['categories']:
                name, min_req = cat['name'], cat['value']

                # bucket all entries of this category
                bucket = [e for e in data if e.get('category','').lower() == name.lower()]
                # split out those missing seat_info
                unknown = [e for e in bucket if not e.get('seat_info')]
                known   = [e for e in bucket if e.get('seat_info')]

                # if we have at least min_req unknown seats, just pick those
                if len(unknown) >= min_req:
                    temp[name] = sample(unknown, min_req)
                    continue

                # otherwise, proceed with contiguous-seat logic on 'known' only
                groups = defaultdict(list)
                for e in known:
                    sec, blk, row, num = parse_seat_info(e['seat_info'])
                    groups[(sec, blk, row)].append((num, e))

                segments = []
                for seq in groups.values():
                    seq.sort(key=lambda x: x[0])
                    cur = [seq[0]]
                    for prev, curr in zip(seq, seq[1:]):
                        if curr[0] == prev[0] + 1:
                            cur.append(curr)
                        else:
                            segments.append(cur)
                            cur = [curr]
                    segments.append(cur)

                # now build candidate runs (respecting MAX_SEATS)
                candidates = []
                for seg in segments:
                    rows = [e for _, e in seg]
                    L = len(rows)
                    if L < min_req:
                        continue
                    if L > MAX_SEATS:
                        for i in range(L - MAX_SEATS + 1):
                            candidates.append(rows[i : i + MAX_SEATS])
                    else:
                        candidates.append(rows)

                # pick best contiguous run if any
                if candidates:
                    best_len = max(len(c) for c in candidates)
                    top_runs = [c for c in candidates if len(c) == best_len]
                    temp[name] = choice(top_runs)
                else:
                    temp[name] = None

            # of all categories for this match, keep only those with the global max length
            runs = [r for r in temp.values() if r]
            if runs:
                max_len = max(len(r) for r in runs)
                output[req['match']] = {
                    cat: run
                    for cat, run in temp.items()
                    if run and len(run) >= max_len
                }
            else:
                output[req['match']] = {}

        return output


    def add_to_cart(self, seats):
        for seat in seats:
            if seat.get('pagination_level') is not None:
                check_for_element(self.driver, \
                f"//span[@class='page ']/a[contains(text(),'{seat['pagination_level']}')]", xpath=True, click=True)
            check_for_element(self.driver, f".//td[@class='resale-item-seatPath seatPath'][contains(normalize-space(text()), '{seat['name']}')]", xpath=True, click=True, debug=True)


class OfficialTicketManager(TicketManager):
    def filter(self):
        selected_category = choice(self.categories)
        return [selected_category]

    def select(self, valid_categories):
        seats = []
        for category in valid_categories:
            elements = self.driver.find_elements(By.XPATH, 
                f'//tr[.//th[contains(., "{category}")]]//select[@aria-label="Quantity"]')
            for elem in elements:
                seats.append(elem)
        return seats

    def add_to_cart(self, seats):
        for seat in seats:
            dropdown = Select(seat)
            dropdown.select_by_value("1")
            time.sleep(1)


def run(thread, link, time_to_wait, browsersAmount, proxyInput):
    INPUT = 'input.xlsx'
    selxs_static = genselx(xlsx_name=INPUT)
    
    driver = init_selenium_driver(proxyInput)

    if proxyInput != '': add_proxy_switcher(driver, proxyInput)
    driver.get('https://nopecha.com/setup#awscaptcha_auto_open=false|awscaptcha_auto_solve=true|awscaptcha_solve_delay=true|awscaptcha_solve_delay_time=1000|disabled_hosts=|enabled=true|funcaptcha_auto_open=false|funcaptcha_auto_solve=false|funcaptcha_solve_delay=true|funcaptcha_solve_delay_time=1000|geetest_auto_open=false|geetest_auto_solve=true|geetest_solve_delay=true|geetest_solve_delay_time=1000|hcaptcha_auto_open=true|hcaptcha_auto_solve=true|hcaptcha_solve_delay=true|hcaptcha_solve_delay_time=3000|sub_1QsSuQCRwBwvt6ptjP0yralq|keys=|lemincaptcha_auto_open=false|lemincaptcha_auto_solve=true|lemincaptcha_solve_delay=true|lemincaptcha_solve_delay_time=1000|perimeterx_auto_solve=false|perimeterx_solve_delay=true|perimeterx_solve_delay_time=1000|recaptcha_auto_open=false|recaptcha_auto_solve=false|recaptcha_solve_delay=true|recaptcha_solve_delay_time=2000|textcaptcha_auto_solve=true|textcaptcha_image_selector=#img_captcha|textcaptcha_input_selector=#secret|textcaptcha_solve_delay=true|textcaptcha_solve_delay_time=100|turnstile_auto_solve=false|turnstile_solve_delay=true|turnstile_solve_delay_time=1000')
    driver.get(link)

    try:
        driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
    except:
        pass

    while True:
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {"userAgent": ua()})
        time.sleep(2)
        driver.execute_script(f"window.open('{link}/','_self')")
        check_for_element(driver, '//*[@id="onetrust-accept-btn-handler"]', xpath=True, click=True)

        if 'peak35' not in driver.current_url:
            cookie_button = wait_for_element(driver, '//*[@id="didomi-notice-agree-button"]', timeout=5, xpath=True)
            if cookie_button:
                time.sleep(2)
                check_for_element(driver, '//*[@id="didomi-notice-agree-button"]', xpath=True, click=True)

        if 'peak35' in driver.current_url: handle_captcha_solve(driver)
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

        all_category_names = sorted({cat['name'] for cat in main_match[0]['categories'] if cat['value'] != 0})
        if not all_category_names:
            print('No category data available for this event.')
            time.sleep(time_to_wait)
            continue


        if 'resale' in driver.current_url:
            manager = ResaleTicketManager(driver, main_match, all_category_names, time_to_wait)
        else:
            manager = OfficialTicketManager(driver, main_match, all_category_names, time_to_wait)

        valid_categories = manager.filter()
        desired_seats = manager.collect(valid_categories)

        if not desired_seats:
            print('No tickets found.')
            time.sleep(time_to_wait)
            continue

        tickets = manager.select(desired_seats, main_match)
        
        match_tickets = list(tickets[title].values())
        if not match_tickets:
            print(f"No tickets available for {title!r}")
            time.sleep(time_to_wait)
            continue

        manager.add_to_cart(choice(list(tickets[title].values())))
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
