import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime


# THERE ARE INFORMATIONS ONLY ACCESSIBLE VIA LOGIN
# [Official_Site, Wikipedia, and more]

if __name__ == '__main__':
    URL = 'https://myanimelist.net/anime/season'
    seasonal_animes = []

    r = requests.get(URL)

    soup = BeautifulSoup(r.text, 'html.parser')
    season_anime = soup.find('div', attrs={
        'class': 'seasonal-anime-list js-seasonal-anime-list js-seasonal-anime-list-key-1 clearfix'})
    animes = season_anime.find_all('div', attrs={
        'class': 'seasonal-anime js-seasonal-anime'})

    for anime in animes:
        dict_anime = {}
        dict_anime['title'] = anime.find('a', attrs={'class': 'link-title'}).get_text()
        dict_anime['episodes'] = anime.find('div', attrs={'class': 'eps'}).get_text().strip()
        if '?' in dict_anime['episodes']:
            dict_anime['episodes'] = 'Unknown'
        dict_anime['source'] = anime.find('span', attrs={'class': 'source'}).get_text().strip()

        div_genres = anime.find('div', attrs={'class': 'genres js-genre'})
        dict_anime['genres'] = [div.get_text()
                                for div in div_genres.find_all('a')]
        dict_anime['description'] = anime.find('div', attrs='synopsis js-synopsis').get_text().strip()

        anime_link = anime.find('a', attrs={'class': 'link-title'})['href']
        r_anime = requests.get(anime_link)
        html_anime = r_anime.text

        title_jap = re.search(
            r'<span class="dark_text">Japanese:</span>\s(.+)',
            html_anime)
        if title_jap:
            dict_anime['title_jap'] = title_jap.group(1)
        else:
            dict_anime['title_jap'] = 'Unknown'

        season = re.search(
            r'<span class="dark_text">Premiered:</span>\s(.+)>(.+)</a>',
            html_anime)
        if season:
            dict_anime['season'] = season.group(2)
        else:
            dict_anime['season'] = 'Unknown'

        status = re.search(
            r'<span class="dark_text">Status:</span>\s(.+)',
            html_anime)
        if status:
            dict_anime['status'] = status.group(1)
        else:
            dict_anime['status'] = 'Unknown'

        bcast = re.search(
            r'<span class="dark_text">Broadcast:</span>\s(.+)',
            html_anime
        )
        if bcast and bcast != 'Unknown':
            list_bcast = bcast.group(1).strip().split(' ')
            day = list(list_bcast[0])
            day[-1] = ''
            list_bcast[0] = ''.join(day)
            dict_anime['broadcast'] = ' '.join(list_bcast)
        else:
            dict_anime['broadcast'] = 'Unknown'

        str_date = re.search(
            r'<span class="dark_text">Aired:</span>\s(.+)',
            html_anime)
        if str_date:
            list_info_date = [date.strip() for date in str_date.group(1).strip().split('to')]

            date_start = None
            date_finished = None

            if re.match(r'\w{3} \d{1,2}, \d{4}', list_info_date[0]):
                date_start_obj = datetime.strptime(
                    list_info_date[0],
                    "%b %d, %Y")
                date_start = date_start_obj.strftime("%b %d, %Y")

                if list_info_date[1] != '?':
                    date_finished = list_info_date[1].strftime("%b %d, %Y")

            dict_anime['date_start'] = date_start
            dict_anime['date_finished'] = date_finished
        else:
            dict_anime['date_start'] = None
            dict_anime['date_finished'] = None

        seasonal_animes.append(dict_anime)

    with open('seasonal_animes.json', 'w', encoding='utf-8') as jp:
        js = json.dumps(seasonal_animes, ensure_ascii=False)
        jp.write(js)
