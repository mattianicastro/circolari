from bs4 import BeautifulSoup
import requests
import json
import requests
import os
import sys
import config

BASE_URL = 'https://www.iiscastelli.edu.it/'
LINK = BASE_URL+'pager.aspx?page=circolari'
WEBHOOK_URL = config.webhook


class Circolare:
    def __init__(self, data):
        self.name = data.a.string
        self.url = BASE_URL+data.a.get('href').replace(' ', '%20')

    @property
    def discord_payload(self):
        return json.dumps({
            "embeds": [{
                "title": 'Nuova circolare pubblicata',
                "description": f"[{self.name}]({self.url})"
            }]
        })


def send_webhook(circolare):
    headers = {'Content-Type': 'application/json'}
    r = requests.post(WEBHOOK_URL, headers=headers,
                      data=circolare.discord_payload)
    print(
        f'Posted {circolare.name} to Discord with status code {r.status_code}')


if __name__ == '__main__':
    html = requests.get(LINK).text
    soup = BeautifulSoup(html, 'html.parser')
    circolari = set()
    if not os.path.exists('already_sent.json'):
        already_sent = []
    else:
        already_sent = json.load(open('already_sent.json'))
    table = soup.find('tbody')
    if "cache" in sys.argv:
        urls = list(map(lambda x: Circolare(x).url, table.contents))
        urls.sort()
        json.dump(urls, open('already_sent.json', 'w'))
        exit()
    for x in table.contents:
        c = Circolare(x)
        if c.url not in already_sent:
            circolari.add(c.url)
            send_webhook(c)
    data = list(circolari.union(already_sent))
    data.sort()

json.dump(data, open('already_sent.json', 'w'))
