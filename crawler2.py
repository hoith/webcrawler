import requests
import sys
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
 
def get_tags(page):
    #page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = title = soup.find("meta",  property="og:title")
    descrption = soup.find("meta",  property="og:description")
    url_og= soup.find("meta",  property="og:url")
    image=soup.find("meta",  property="og:image")
    video = soup.find("meta",  property="og:video")
    print("checking tags")
    #print(title["content"] if title else "No meta title given")
    #print(descrption["content"] if descrption else "No description given")
    #print(url_og["content"] if url_og else "No meta url given")
    #print(image["content"] if image else "No image given")
    #print(video["content"] if video else "No video given")

class MultiThreadScraper:
 
    def __init__(self, base_url):
 
        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        #self.pool.daemon = True
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.pool.daemon = True
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.is_article = set([])
        self.to_crawl.put(self.base_url)
 
    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        #print(soup)
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            #if soup.find("meta",  property="og:title") != None and soup.find("meta",  property="og:description") != None and soup.find("meta",  property="og:url") != None:
             #   print("this is an article page")
                        #title = title = soup.find("meta",  property="og:title")
            #descrption = soup.find("meta",  property="og:description")
            #url_og= soup.find("meta",  property="og:url")
            #image=soup.find("meta",  property="og:image")
            #video = soup.find("meta",  property="og:video")
            #print("checking tags")
            if url.startswith('/news/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scraped_pages:
                    self.to_crawl.put(url)
 
    def scrape_info(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        url = soup.find("meta",  property="og:url")
        title = soup.find("meta",  property="og:title")
        descrption = soup.find("meta",  property="og:description")
        #test2 = test["content"]
        if title != None and descrption != None and url != None:
            test2 = url["content"]
            self.is_article.add(test2)
        return 
 
    def post_scrape_callback(self, res ):
        
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)
            self.scrape_info(result.text)
            return 
 
    def scrape_page(self, url):
        try:
            res = requests.get(url, timeout=(3, 30))
            return res
        except requests.RequestException:
            return
 
    def run_scraper(self):
        #while True:
        count =0
        while True:
            try:
                target_url = self.to_crawl.get(timeout=60)
                if target_url not in self.scraped_pages:
                    print("Scraping URL: {}".format(target_url))
                    self.scraped_pages.add(target_url)
                    job = self.pool.submit(self.scrape_page, target_url)
                    #get_tags(job.result())
                    job.add_done_callback(self.post_scrape_callback)
                    count= count +1
                    print(count)
                    #print(self.is_article)
            except KeyboardInterrupt:
                sys.exit(1)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue
if __name__ == '__main__':
    s = MultiThreadScraper("https://www.bbc.com/news/")
    s.run_scraper()