import json
import string
import requests
import re
import time
from bs4 import BeautifulSoup
from random import choices, randint
from datetime import timedelta, date
from telebot import apihelper, types, TeleBot

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

with open('credentials_for_bot.json', 'r', encoding='utf-8') as bot_file, \
        open('email.json', 'r', encoding='utf-8') as email_file, \
        open('comment.json', 'r', encoding='utf-8') as comment_file, \
        open('headers.json', 'r', encoding='utf-8') as headers_file, \
        open('proxies.txt', 'r', encoding='utf-8') as proxies_file:
    credentials_bot = json.load(bot_file)
    list_emails = json.load(email_file)["email"]
    comment = json.load(comment_file)
    headers = json.load(headers_file)
    proxies_arr = proxies_file.read().split(',\n')

bot = TeleBot(credentials_bot["telegram"]["api_token"], skip_pending=True)


def change_proxy(mode=0):
    if mode == 1:
        ip = proxies_arr[randint(0, len(proxies_arr) - 1)]
        return ip
    else:
        ip = proxies_arr[randint(0, len(proxies_arr) - 1)]
        proxies = {
            "http": ip,
            "https": ip}
        return proxies


def data_olx(id_ad, choice_reason, text):
    data = {
        "ad_id": f"{id_ad}",
        "reason": f"{choice_reason}",
        "text": f"{text}"
    }
    return data


def ban_olx(message, url, choice_reason):
    proxy = change_proxy()
    try:
        r = requests.get(url,
                         timeout=30,
                         headers={"user-agent": headers["user-agent"][0]},
                         proxies=proxy,
                         verify=False
                         )
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            banned = soup.find("p", {"class": "css-1ufumz9-Text eu5v0x0"}).getText()
            if banned:
                return -1
        except:
            try:
                if re.findall(".*from404", r.url)[0]:
                    return -1
            except:
                pass
        try:
            data_soup = soup.find("span", {"class": "css-7oa68k-Text eu5v0x0"}).getText()
        except:
            data_soup = soup.find("ul", {"class": "offer-bottombar__items"}).getText()
        if data_soup:
            id_ad = re.findall(r"\d{9}", data_soup)[0]
            reason = comment[choice_reason]
            text = reason[randint(0, len(reason) - 1)]
            time.sleep(randint(5, 15))
            response = requests.post('https://www.olx.ua/api/v1/moderation/abuse/',
                                     timeout=15,
                                     headers={
                                         "user-agent": headers["user-agent"][
                                             randint(0, len(headers["user-agent"]) - 1)]},
                                     data=data_olx(id_ad, choice_reason, text),
                                     proxies=proxy,
                                     verify=False)

            data = response.json()
            if response.status_code == 200:
                return 1
            else:
                bot.send_message(id_user, 'Щось пішло не так')
    except Exception as e:
        print(e)
        return 0


def ban_flatfy(message, url, choice_reason):
    email = list_emails[randint(0, len(list_emails) - 1)]
    reason = comment[choice_reason]
    text = reason[randint(0, len(reason) - 1)]
    result = flatfy_driver(url, email, choice_reason, text)
    return result


def flatfy_driver(url, email, choice_reason, text):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--proxy-server=%s' % change_proxy(1))
    options.add_argument(f'user-agent={headers["user-agent"][randint(0, len(headers["user-agent"]) - 1)]}')
    driver = webdriver.Chrome(ChromeDriverManager(path='C:\\Users\\bmi\\.wdm\\').install(), chrome_options=options)
    driver.set_page_load_timeout(25)
    try:
        driver.set_window_size(1400, 1000)
        driver.get(url)
        time.sleep(randint(5, 15))
        arrows_left = driver.find_elements_by_xpath('//button[@class="image-gallery-left-nav"]')
        arrows_right = driver.find_elements_by_xpath('//button[@class="image-gallery-right-nav"]')
        for i in range(randint(1, 7)):
            arrows_right[0].click()
            time.sleep(3)
        for i in range(randint(1, 6)):
            arrows_left[0].click()
            time.sleep(4)
        time.sleep(2)
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(randint(3, 7))
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.PAGE_UP)
        time.sleep(2)
        dots = driver.find_element_by_xpath('//div[@class="realty-page-main-content__gallery-actions-item"]'
                                            '/div[@class="realty-menu"]'
                                            '/button[@class="button-base icon-button realty-menu__button"]')
        dots.click()
        time.sleep(2)
        try:
            driver.find_element_by_xpath('//*[text()="Поскаржитися"]').click()
        except:
            driver.find_element_by_xpath('//*[text()="Пожаловаться"]').click()
        time.sleep(2)
        html = driver.find_element_by_tag_name('html')
        time.sleep(1)
        html.send_keys(Keys.PAGE_DOWN)
        category = driver.find_element_by_xpath(f'//div[@data-event-label="{choice_reason}"]')
        time.sleep(1)
        category.click()
        category.click()
        time.sleep(2)
        input_email = driver.find_element_by_xpath("//input[@name='email']")
        time.sleep(1)
        input_email.send_keys(email)
        time.sleep(10)
        input_comment = driver.find_element_by_xpath("//input[@name='text']")
        input_comment.send_keys(text)
        time.sleep(4)
        driver.find_element_by_xpath(
            "//button[@class='button button_primary button_rounded contacts-form__send-action']").click()
        time.sleep(20)
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.PAGE_UP)
        time.sleep(2)

    except Exception as e:
        print(e)
        return 0
    finally:
        driver.close()
    return 1
