import requests
import xml.etree.ElementTree as ET
import os
import telebot
from dotenv import load_dotenv

F1NEWS_XML_URL = 'https://www.f1news.ru/export/news.xml'
TEMP_FOLDER = f'{os.getcwd()}/tmp/'
LOCAL_XML_FILE = f'{TEMP_FOLDER}/news.xml'
ELEMENTS = ('link', 'pubDate')


class Bot:
    def __init__(self) -> None:
        self.bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

    def public_article(self, article: dict) -> None:
        self.bot.send_message(os.getenv('CHANNEL_ID'), f"{article['pubDate']}\n{article['link']}")
    

def create_tmp_folder() -> None:
    if not os.path.isdir(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER, mode=0o755)


def parse_xml(xml: str) -> dict:
    articles = []

    root = ET.fromstring(xml)
    
    for item in root.iter('item'):
        article = {}

        for el in ELEMENTS:
            if el == 'pubDate':
                article[el] = item.find(el).text.split(' +')[0]
            else:
                article[el] = item.find(el).text
            
        articles.append(article)

    return articles


def get_f1news_xml() -> str:
    return requests.get(F1NEWS_XML_URL).text


def read_local_xml() -> str:
    if not os.path.exists(LOCAL_XML_FILE):
        return ''
    
    f = open(LOCAL_XML_FILE, 'r')

    return f.read()


def articles_diff(f1news_articles: dict, local_articles: dict) -> dict:
    new_articles = []

    for f1news_article in f1news_articles:
        new = True

        for local_article in local_articles:
            if f1news_article['link'] == local_article['link']:
                new = False

        if new:
            new_articles.append(f1news_article)

    return new_articles


def save_xml(xml: str) -> None:
    f = open(LOCAL_XML_FILE, 'w')
    f.write(xml)
    f.close()


def run() -> None:
    bot = Bot()

    create_tmp_folder()
    
    f1news_xml = get_f1news_xml()
    local_xml = read_local_xml()

    if local_xml != '':
        f1news_articles = parse_xml(f1news_xml)
        local_articles = parse_xml(local_xml)
        
        new_articles = articles_diff(f1news_articles, local_articles)
        
        for new_article in new_articles:
            bot.public_article(new_article)

    save_xml(f1news_xml)
    


load_dotenv()
run()