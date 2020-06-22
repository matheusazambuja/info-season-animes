import requests
import re
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta
from selenium.common.exceptions import ElementNotVisibleException


def format_titles(str_html):
    regex_title_jap = r'<span class="dark_text">' + re.escape('Japanese:') + r'</span>\s(.+)'
    str_title_jap = re.search(regex_title_jap, str_html).group(1).replace('Japanese: ', '')

    regex_title = r'<span class="h1-title"><span itemprop="name">(.+)<br>'
    match_title = re.search(regex_title, str_html)
    if match_title:
        str_title = match_title.group(1).strip()
        str_title_eng = ''
        regex_title_eng = r'<span class="title-english">(.+)</span></span></span>'
        match_title_eng = re.search(regex_title_eng, str_html)
        str_title_eng = match_title_eng.group(1).strip()
    else:
        regex_title = r'<span class="h1-title"><span itemprop="name">(.+)</span></span>'
        match_title = re.search(regex_title, str_html)
        str_title = match_title.group(1).strip()
        regex_title_eng = r'<span class="dark_text">' + re.escape('English:') + r'</span>\s(.+)'
        match_title_eng = re.search(regex_title_eng, str_html)
        if match_title_eng:
            str_title_eng = match_title_eng.group(1).strip()
        else:
            str_title_eng = ''

    return [str_title, str_title_eng, str_title_jap]


def info_dates(str_html, num_eps):
    regex_date = r'<span class="dark_text">' + re.escape('Aired:') + r'</span>\s(.+)'
    str_date = re.search(regex_date, str_html).group(1).strip()
    list_info_date = [date.strip() for date in str_date.split('to')]

    current_episode = None
    date_next_episode = None
    date_first_episode = None
    date_last_episode = None

    if re.match(r'\w{3} \d{1,2}, \d{4}', list_info_date[0]):
        date_first_episode_obj = datetime.strptime(list_info_date[0], "%b %d, %Y")
        date_first_episode_obj += timedelta(days=-1)
        date_first_episode = date_first_episode_obj.strftime("%b %d, %Y")
        if date_first_episode_obj - timedelta(days=1) > datetime.now():
            if num_eps:  # if != None
                for i in range(1, int(num_eps)):
                    date_first_episode_obj += timedelta(days=7)
                    if date_first_episode_obj < datetime.now():
                        date_next_episode = date_first_episode_obj.strftime("%b %d, %Y")
                        current_episode = i
                date_last_episode = date_first_episode_obj.strftime("%b %d, %Y")
            else:
                date_first_episode = date_first_episode_obj.strftime("%b %d, %Y")
        else:
            date_last_episode = date_first_episode_obj.strftime("%b %d, %Y")
    else:
        date_first_episode = list_info_date[0]

    return [current_episode, date_first_episode, date_next_episode,
            date_last_episode]


def get_data(str_html):
    soup = BeautifulSoup(str_html, 'html.parser')

    genres = [g.text for g in soup.find_all('span', attrs={'itemprop': 'genre'})]
    match_description = soup.find('span', attrs={'itemprop': 'description'})
    if match_description:
        str_description = match_description.get_text()
    else:
        str_description = 'No synopsis information has been added to this title.'

    regex_status = r'<span class="dark_text">' + re.escape('Status:') + r'</span>\s(.+)'
    status = re.search(regex_status, str_html).group(1).strip()

    regex_source = r'<span class="dark_text">Source:</span>\s+(.+)'
    match_source = re.search(regex_source, str_html)
    if match_source:
        str_source = match_source.group(1).strip()
    else:
        str_source = 'Unknown'

    regex_episodes = r'<span class="dark_text">' + re.escape('Episodes:') + r'</span>\s+(.+)'
    episodes = re.search(regex_episodes, str_html).group(1)
    if episodes == 'Unknown':
        episodes = None

    # Informations of dates and transmition
    list_dates = info_dates(str_html, episodes)
    if list_dates[2]:
        list_dates[2] = str(list_dates[2])

    list_titles = format_titles(str_html)

    return {
        'title': list_titles[0],
        'title_english': list_titles[1],
        'title_japanese': list_titles[-1],
        'description': str_description,
        'source': str_source,
        'list_genres': genres,
        'status': status,
        'episodes': episodes,
        'current_episode': list_dates[0],
        'date_first_episode': list_dates[1],
        'date_next_episode': list_dates[2],
        'date_last_episode': list_dates[-1]
    }


# THERE ARE INFORMATIONS ONLY ACCESSIBLE VIA LOGIN
# [Official_Site, Wikipedia, and more]

if __name__ == '__main__':
    URL = 'https://myanimelist.net/'
    option = Options()
    option.headless = True
    seasonal_animes = []

    driver = webdriver.Firefox(
                executable_path=r'D:\Program Files\geckodriver\geckodriver.exe', options=option)
    driver.get(URL)
    driver.implicitly_wait(5)  # in seconds

    element_link = driver.find_element_by_css_selector('a[href*="season"]')
    html_link = element_link.get_attribute('outerHTML')

    link_seasonal = BeautifulSoup(html_link, 'html.parser').find('a')['href']

    driver.get(link_seasonal)
    try:
        print('searching animes')
        div_animes = driver.find_element_by_css_selector('div.js-seasonal-anime-list-key-1')
        soup = BeautifulSoup(div_animes.get_attribute('innerHTML'), 'html.parser')
        p_animes = soup.find_all('p', attrs={'class': 'title-text'})
        for anime in p_animes:
            link = anime.find('a')['href']
            r = requests.get(link)

            print(f'getting data of link: {link}')
            seasonal_animes.append(get_data(r.text))
            print(f'finished: {link}')
            print('----------------------------------------------------------------')
    except ElementNotVisibleException:
        print('div_animes not found')

    driver.quit()

    with open('seasonal_animes.json', 'w', encoding='utf-8') as jp:
        js = json.dumps(seasonal_animes, ensure_ascii=False)
        jp.write(js)
