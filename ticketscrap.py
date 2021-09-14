import argparse
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

TICKET_PATH = "https://www.ticketswap.fr/event/macki-music-festival-2021/pass-samedi-late-bird/e01728a8-7038-4663-9f97-833e4c60faa7/1685200"
FB_EMAIL = os.environ.get('FB_EMAIL')
FB_PASS = os.environ.get('FB_PASS')


def click_button(soup, button_text, driver, by_class=True):
    for button in soup.find_all('button'):
        if button.text == button_text:
            if by_class:
                button_class = button['class'][0]
                driver.find_element_by_class_name(button_class).click()
            else:
                button_id = button['id']
                driver.find_element_by_id(button_id).click()
            break
    return driver


def main(ticket_path=TICKET_PATH, sleep_time=0.1, fb_email=FB_EMAIL, fb_pass=FB_PASS):
    while True:
        r = requests.get(ticket_path)
        soup = BeautifulSoup(r.content, 'html.parser')
        if len(soup.find_all('h5')) > 0:
            for a in soup.find_all('a', href=True):
                if a['href'].startswith('https://www.ticketswap.fr/listing'):
                    print('Ticket in sale')
                    r_ticket = (
                        requests.get(a['href'])
                    )
                    soup_ticket = BeautifulSoup(r_ticket.content, 'html.parser')
                    driver = webdriver.Chrome()
                    driver.get(a['href'])
                    driver = click_button(soup_ticket, 'Acheter un billet', driver)
                    time.sleep(1)
                    connexion_soup = BeautifulSoup(driver.page_source)
                    driver = click_button(connexion_soup, 'Se connecter avec Facebook', driver)
                    main_window_handle = driver.current_window_handle

                    signin_window_handle = None
                    while not signin_window_handle:
                        for handle in driver.window_handles:
                            if handle != main_window_handle:
                                signin_window_handle = handle
                                break

                    driver.switch_to.window(signin_window_handle)
                    second_connexion_soup = BeautifulSoup(driver.page_source)
                    driver = click_button(second_connexion_soup, 'Tout accepter', driver, False)
                    driver.find_element_by_id('email').send_keys(fb_email)
                    driver.find_element_by_id('pass').send_keys(fb_pass)
                    for button in second_connexion_soup.find_all('input'):
                        if button.get('value') == 'Se connecter':
                            button_id = button['id']
                    driver.find_element_by_id(button_id).click()
                    time.sleep(600)
                    break
        print('No Ticket')
        time.sleep(sleep_time)
    print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default=TICKET_PATH)
    parser.add_argument("--fb-email", type=str, default=FB_EMAIL)
    parser.add_argument("--fb-pass", type=str, default=FB_PASS)
    parser.add_argument('--sleep-time', type=float, default=0.1)
    args = vars(parser.parse_args())
    sleep_time_, ticket_path_, fb_email_, fb_pass_ = (
        args.get('sleep_time'), args["path"], args['fb_email'], args['fb_pass']
    )
    main(ticket_path_, sleep_time_)
