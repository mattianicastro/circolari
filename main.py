import json
import os
import sys
import time
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

import config

BASE_URL = 'https://www.iiscastelli.edu.it/'
LINK = BASE_URL+'pager.aspx?page=circolari'
DISCORD_WEBHOOK_URL = config.discord_webhook
TELEGRAM_URL = f"https://api.telegram.org/bot{config.telegram_token}/sendMessage"


class Circolare:
    def __init__(self, data):
        self.name = data.a.string
        self.url = BASE_URL+quote(data.a.get('href'))

    @property
    def discord_payload(self):
        return json.dumps({
            "embeds": [{
                "title": "Nuova circolare pubblicata",
                "description": f"{self.name}\n\n[Apri]({self.url})"
            }]
        })

    @property
    def telegram_payload(self):
        return json.dumps({
            "chat_id": config.telegram_chat_id,
            "parse_mode": "HTML",
            "text": f"""<b>Nuova circolare pubblicata</b>

<code>{self.name}</code>

<a href="{self.url}">Apri</a>
"""
        })

    def post(self):
        headers = {"Content-Type": "application/json"}
        print(f"Posting {self.name}...")
        r = requests.post(DISCORD_WEBHOOK_URL, headers=headers,
                          data=self.discord_payload)
        print(f"[DISCORD] {r.status_code}")
        r = requests.post(TELEGRAM_URL, headers=headers,
                          data=self.telegram_payload)
        print(f"[TELEGRAM] {r.status_code}")
        if r.status_code == 429:
            print(f"[TELEGRAM] Retrying 429...")
            time.sleep(int(r.json()["parameters"]["retry_after"]))
            r = requests.post(TELEGRAM_URL, headers=headers,
                              data=self.telegram_payload)
            print(f"[TELEGRAM] {r.status_code}")


if __name__ == '__main__':
    html = requests.get(LINK).text
    soup = BeautifulSoup(html, 'html.parser')
    circolari = set()
    if not os.path.exists('already_sent.json'):
        already_sent = []
    else:
        already_sent = json.load(open('already_sent.json'))
    table = soup.find('tbody')
    table.contents.reverse()
    if "cache" in sys.argv:
        urls = list(map(lambda x: Circolare(x).url, table.contents))
        urls.sort()
        json.dump(urls, open('already_sent.json', 'w'))
        exit()
    for x in table.contents:
        c = Circolare(x)
        if c.url not in already_sent:
            circolari.add(c.url)
            c.post()
            time.sleep(2)
    data = list(circolari.union(already_sent))
    data.sort()

    json.dump(data, open('already_sent.json', 'w'))
