import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cmbchina.items import Article


class cmbchinaSpider(scrapy.Spider):
    name = 'cmbchina'
    start_urls = ['http://english.cmbchina.com/CmbInfo/News/']

    def parse(self, response):
        articles = response.xpath('//div[@class="itemlist"]/ul/li')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('./span[@class="right"]/text()').get()
            if date:
                date = " ".join(date.split())[1:-1]

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//div[@class="pager"]//a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="conheader"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="artbody"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
