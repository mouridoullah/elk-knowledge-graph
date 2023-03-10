import requests
from bs4 import BeautifulSoup

def crawl_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    print("Page Title:", soup.title.string)
    print("Links:")
    for link in soup.find_all("a"):
        print("-", link.get("href"))

crawl_webpage("https://www.lefigaro.fr/")
