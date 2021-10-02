from bs4 import BeautifulSoup
import requests
import json
import requests
import os

BASE_URL = 'https://www.iiscastelli.edu.it/'
LINK = BASE_URL+'pager.aspx?page=circolari'
WEBHOOK_URL = "https://discord.com/api/webhooks/..."


class Circolare:
    def __init__(self, data):
        self.name = data.a.string
        self.url = BASE_URL+data.a.get('href')

    @property
    def discord_payload(self):
        return {
            "embeds": [{
                "title": 'Nuova circolare pubblicata',
                "description": f"[{self.name}]({self.url})"
            }]
        }


def send_webhook(circolare):
    headers = {'Content-Type': 'application/json'}
    requests.post(WEBHOOK_URL, headers=headers, data=circolare.discord_payload)
    print(f'Posted {circolare.name} to Discord')


if __name__ == '__main__':
    html = requests.get(LINK).text
    soup = BeautifulSoup(html, 'html.parser')
    circolari = set()
    if not os.path.exists('already_sent.json'):
        already_sent = []
    else:
        already_sent = json.load(open('already_sent.json'))
    table = soup.find('tbody')
    for x in table.contents:
        c = Circolare(x)
        if c.url not in already_sent:
            circolari.add(c.url)
            send_webhook(c)
    data = list(circolari.union(already_sent))
    data.sort()

    json.dump(data, open('already_sent.json', 'w'))
