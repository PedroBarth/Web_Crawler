import scrapy
from bs4 import BeautifulSoup
import search_tjal


class TJAL_Spider(scrapy.Spider):

    name = "tjal"
    allowed_domains = "tjal.jus.br"

    def _init_(self, process=None, *args, **kwargs):
        super(TJAL_Spider, self)._init_(*args, **kwargs)

    def start_requests(self):
        input = '0731425-82.2014.8.02.0001'
        url = search_tjal.build_url(input)

        yield scrapy.Request(url=url, callback=search_tjal.crawler, headers=search_tjal.build_headers)
