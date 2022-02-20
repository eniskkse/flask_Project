import scrapy
from datetime import datetime
import json
from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest
import re


# EXGSOS

class EnglishSpider(scrapy.Spider):
    name = 'englishereader'
    output = []
    today = datetime.now().strftime("%Y-%m-%d")
    start_urls = ['https://english-e-reader.net/login']

    def start_requests(self):
        pass
        # login olarak başlatıyorum.
        # return [
        #     FormRequest("https://english-e-reader.net/login", formdata={"user": "eniskucukkose@gmail.com",
        #                                                                 "pass": "EXGSOS"}, callback=self.parse)]

    def parse(self, response):
        # library'den seviyelere ulaştığım method.
        library = response.xpath("//ul[@class='dropdown-menu']/li")
        for lib in library:

            if bool(re.search("/level/", lib.get())):
                # Seçtiğim classta seviyeleri vermeyen başka classlarda var.
                # Onları bu if içinde elekten geçiriyorum.
                level_url = lib.css("a").attrib['href']
                # Css selector ile link kuyruğunu çekiyorum.
                geturl = f"https://english-e-reader.net{level_url}"
                yield scrapy.Request(geturl, callback=self.books)

            else:
                pass

    def books(self, response):
        # Kitapların linklerine teker teker götüren method.
        books = response.xpath("//div[@class='col-md-2 col-sm-4 col-xs-6']")
        for book in books:
            book_link = book.css(".book-container a::attr(href)").get()
            geturl = f"https://english-e-reader.net{book_link}"
            yield scrapy.Request(geturl, callback=self.books_attr)

    def books_attr(self, response):
        # Kitap Attribute'lerinin alındığı method.
        author = response.xpath("//div[@class='col-md-10']/h4").get()
        author_name = re.findall('></i>(.*?)</h4>', author)
        book_name = response.xpath("//div[@class='col-md-9']/h1").get().replace(" ", "")
        book_name = book_name[re.search('lagicon">', book_name).span()[1]:re.search('</h1>', book_name).span()[0]].strip()
        genres = response.xpath("//a[@class='list-group-item']").get()
        genres = genres[re.search("/genre/", genres).span()[1]:re.search('">', genres).span()[0]]
        # genres'in "/genre/"yi bulduğu yerden "">" yere kadar al
        elevel = response.xpath("//p[@class='text-center bg-success']").get()
        try:
            elevel = elevel[re.search("/level/", elevel).span()[1]:re.search("</a></p>", elevel).span()[0]]
        except:
            pass
        desc = response.xpath("//p[@class='text-justify']").get()
        desc = desc[re.search('text-justify">', desc).span()[1]:re.search('</p>', desc).span()[0]]
        tags = response.xpath('//div[@class="row"]/p/a[@href]').get()

        if tags:
            tags = tags[re.search("/tag/", tags).span()[1]:re.search('"><span', tags).span()[0]]
        numbers = response.xpath("//div[@class='row']/p").get().strip()
        down = numbers[re.search('download"></i></a>', numbers).span()[1]:re.search('<a title="Reading">', numbers).span()[0]].strip()
        reading = numbers[re.search('warning"></i></a>', numbers).span()[1]:re.search('<a title="Read">', numbers).span()[0]].strip()
        read = numbers[re.search('text-success"></i></a>', numbers).span()[1]:re.search('<a title="Favourite">', numbers).span()[0]].strip()
        fav = numbers[re.search('text-danger"></i></a>', numbers).span()[1]:re.search('<a title="Pages">', numbers).span()[0]].strip()
        # book_pages = numbers[re.search('large text-warning"></i></a>', numbers).span()[1]:re.search('<a title="Audio duration', numbers).span()[0]].strip()
        a_durat = numbers[re.search('text-info"></i></a>', numbers).span()[1]:re.search('</p>', numbers).span()[0]]
        uni_total = response.xpath('//h3[@class="panel-title"]').get()
        uni = uni_total[re.search('Unique words:', uni_total).span()[1]:re.search('Total', uni_total).span()[0]].strip()
        total = uni_total[re.search('  words:', uni_total).span()[1]:re.search('</h3>', uni_total).span()[0]].strip().replace(" ", "")
        hardwords = response.xpath("//div[@class='panel-body']/p/text()").get()
        pages_link = response.css(".col-sm-3.col-xs-12.text-center.form-group button::attr(onclick)")[0].get().replace("location.href = '","").rstrip("';'")
        pages_link = "https://english-e-reader.net" + pages_link
        # req = scrapy.Request(pages_link, callback=self.book_pageses,dont_filter=True)
        # return FormRequest("https://english-e-reader.net/login", formdata={"user": "eniskucukkose@gmail.com",
        #                                                                 "pass": "EXGSOS"}, callback=self.book_pageses)

        # https://english-e-reader.net/book/cooking-the-books-christopher-fowler
        # location.href = '/onlinereader/cooking-the-books-christopher-fowler';
        # https://english-e-reader.net/onlinereader/cooking-the-books-christopher-fowler

        # self.output.append({
        #     "Book Name": book_name,
        #     "Book Genre": genres,
        #     "Author": author_name,
        #     "Book English Level": elevel,
        #     "Book Description": desc,
        #     "Tags": tags,
        #     "Download Count": down,
        #     "Reading Count": reading,
        #     "Read Count": read,
        #     "Favourite Count": fav,
        #     # "Book Pages Count": book_pages,
        #     "Audio Duration Time": a_durat,
        #     "Unique Words Count": uni,
        #     "Total Words Count": total,
        #     "Hard Words": hardwords,
        # })
    def book_pageses(self,response):

        pages = response.css("//div[@class='inner']/div")
        for page in pages:
            paragrafs = page.css(".p").getall()
    # def close(self, spider, reason):
    #     with open(f"English_reader.json", "w", encoding="utf-8") as f:
    #         json.dump(self.output, f, ensure_ascii=False)


process = CrawlerProcess()
process.crawl(EnglishSpider)
process.start()
