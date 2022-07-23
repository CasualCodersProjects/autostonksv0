import os
import json

import requests
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()


def get_article_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    return response.text


def get_article_data(article_html):
    '''
    Returns a dictionary of the article's data. Tickers are the keys and the intent phrase that needs to be analyzed is the value.
    '''
    soup = BeautifulSoup(article_html, "html.parser")
    links = soup.find_all("a")
    # all links must contain the substring 'cnbc.com/quotes'
    links = [link for link in links if "cnbc.com/quotes" in link.get("href")]
    link_parents = [link.parent for link in links]
    # get all the raw text of each link
    link_texts = [link.text for link in link_parents]
    # get the tickers from the links
    tickers = []
    for link in links:
        href = link.get("href")
        ticker = href.split("/")[-1]
        tickers.append(ticker)

    return dict(zip(tickers, link_texts))


if __name__ == '__main__':
    # newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    # top_headlines = newsapi.get_everything(
    #     q="Cramer's Lightning Round", language='en')

    # output_data = []

    # for headline in top_headlines['articles']:
    #     if headline['source']['name'] == 'CNBC':
    #         output_data.append(headline)

    # with open('output.json', 'w') as f:
    #     json.dump(output_data, f, indent=4)
    url = "https://www.cnbc.com/2022/06/23/cramers-lightning-round-nokia-is-right-to-buy.html"
    article_html = get_article_html(url)

    # this properly gets all the tickers from a CNBC article, however
    # I'm not sure if the tickers are all correct
    # will have to check if they're correct and remove all characters that are not relevant

    print(json.dumps(get_article_data(article_html)))
