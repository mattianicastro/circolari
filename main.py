from bs4 import BeautifulSoup
import requests
import json

BASE_URL= 'https://www.iiscastelli.edu.it/'
LINK = BASE_URL+'pager.aspx?page=circolari'

class Circolare:
    def __init__(self, data):
        self.name = data.a.string
        self.url = BASE_URL+data.a.get('href')

    def to_dict(self):
        return {'name':self.name,'url':self.url}

if __name__ == '__main__':
    html = requests.get(LINK).text
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('tbody')
    for x in table.contents:
        circolare = Circolare(x)
