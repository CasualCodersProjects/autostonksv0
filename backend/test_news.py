import os
from newsapi import NewsApiClient
from dotenv import load_dotenv
load_dotenv()
news_api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))


def test_get_news():
    """
    Test the get_news function
    """
    # get the top headlines for the US
    top_headlines = news_api.get_everything(q="Jim Cramer")
    # get the top headlines for the US and Canada
    print(top_headlines)
    assert top_headlines is not None


if __name__ == "__main__":
    test_get_news()
