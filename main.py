from bs4 import BeautifulSoup
import requests
import json
import requests
import os
import time
import sys
import config

BASE_URL = 'https://www.iiscastelli.edu.it/'
LINK = BASE_URL+'pager.aspx?page=circolari'
WEBHOOK_URL = config.webhook


class Circolare:
    def __init__(self, data):
        self.name = data.a.string
        self.url = BASE_URL+data.a.get('href').replace(' ', '%20').replace(
            '(','%28').replace(')','%29')

    @property
    def discord_payload(self):
        return json.dumps({
            "embeds": [{
                "title": 'Nuova circolare pubblicata',
                "description": f"{self.name}\n\n[Apri]({self.url})"
            }]
        })

def req(payload):
    headers = {'Content-Type': 'application/json'}
    r = requests.post(WEBHOOK_URL, headers=headers,
                      data=payload)
    return r

def send_webhook(circolare):
    r = req(circolare.discord_payload)
    print(
        f'Posted {circolare.name} to Discord with status code {r.status_code}')

    if r.status_code == 429:
        print('Got 429, retrying')
        time.sleep(int(r.json()['retry_after'])/1000)
        r = req(circolare.discord_payload)
        print(f'Retried {circolare.name}, status code {r.status_code}')

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
            time.sleep(1)
            send_webhook(c)
    data = list(circolari.union(already_sent))
    data.sort()

json.dump(data, open('already_sent.json', 'w'))
