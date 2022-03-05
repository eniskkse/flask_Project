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
	# Edit (KT): Aşağıda start_requests method'unu kullandığın zaman; start_urls dizisine ihtiyaç yok.
	# start_urls = ['https://english-e-reader.net/login']
	api_headers = {
		'Connection': 'keep-alive',
		'Pragma': 'no-cache',
		'Cache-Control': 'no-cache',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
		'Accept': '*/*',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'sec-ch-ua-mobile': '?0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
		'sec-ch-ua-platform': '"Windows"',
		'Origin': 'https://english-e-reader.net',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Referer': 'https://english-e-reader.net/onlinereader/fever-dream-ray-bradbury',
		'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
		'Cookie': 'theme=%7B%22theme-name%22%3A%22default%22%2C%22theme-opts%22%3A%7B%22color%22%3A%22%23000%22%2C%22backgroundColor%22%3A%22%23fff%22%2C%22backgroundImage%22%3A%22%22%2C%22fontFamily%22%3A%22Arial%22%2C%22fontSize%22%3A16%2C%22fontStyle%22%3A%22normal%22%2C%22textAlign%22%3A%22start%22%2C%22textIndent%22%3A0%2C%22textPadding%22%3A0%7D%7D; _ga=GA1.2.859758483.1646470977; _gid=GA1.2.1534369056.1646470977; JSESSIONID=D3E8E20402350871AAC3E329655C4EB5; session=4c4e9931-a7c0-4639-a8be-7854ed96d94c-c232ce58-b624-4c75-ba2f-e48c0e39cf7a; _gat_gtag_UA_108090877_1=1'
	}

	books = []
	pages = []

	def start_requests(self):
		# login olarak başlatıyorum.
		# Edit (KT): Return yerine yield kullandım.
		# Edit (KT): Sitenin form kısmını incelediğimde POST ile çalıştığını gördüm. Method'u bu şekilde güncelledim.
		# Edit (KT): Form alanları isimlerini user ve pass olarak girmişsin. Web sitesinde o şekilde kullanılmıyordu.
		# Edit (KT): Ayrıca form içerisinde bir de "referer" alanı bulunuyordu. Koda ekledim.
		yield FormRequest("https://english-e-reader.net/login",
						  formdata={"email": "eniskucukkose@gmail.com",
									"password": "EXGSOS",
									"referer": "https://english-e-reader.net/"},
						  callback=self.parse,
						  method="POST")

	def parse(self, response):
		# library'den seviyelere ulaştığım method.
		library = response.css(".dropdown-menu li a::attr(href)").getall()
		for lib in library:
			# Edit (KT): Regex kullanmak işi biraz uzatmış ve yavaşlatma ihtimali var.
			# Bunun yerine "level" in lib.get() şeklinde düzeltebiliriz.
			if 'level' in lib:
				geturl = f"https://english-e-reader.net{lib}"
				yield scrapy.Request(geturl, callback=self.category)

	def category(self, response):
		# Kitapların linklerine teker teker götüren method.
		books = response.xpath("//div[@class='col-md-2 col-sm-4 col-xs-6']")
		for book in books:
			book_link = book.css(".book-container a::attr(href)").get()
			if book_link:
				geturl = f"https://english-e-reader.net{book_link}"
				yield scrapy.Request(geturl, callback=self.books_detail)

	def books_detail(self, response):
		# Kitap Attribute'lerinin alındığı method.
		author_name = response.css(".col-md-10 h4::text").get()
		book_name = response.css("meta[property='og:title']::attr(content)").get()
		genre = response.css(".list-group-item::text").get()
		level = response.css(".col-md-3.col-sm-12.hidden-sm.hidden-xs a::text").get()
		desc = response.css(".col-sm-12 .text-justify::text").get()
		tags = [x.strip() for x in response.css(".label.label-default::text").getall()]
		analyze = response.css("#hard-words .panel-heading .panel-title::text").getall()[-1].strip()
		analyze = analyze.replace('\r', '').replace('\n', '').replace('  ', '').strip()

		page_count = response.css(".col-lg-10.col-md-9.col-sm-12.col-xs-12 .row")[2]
		page_count = page_count.css(".text-center::text")[-2].get().strip()

		pages_link = response.css(".col-sm-3.col-xs-12.text-center.form-group button::attr(onclick)")[0].get()
		pages_link = pages_link.replace("location.href = '", "").rstrip("';'")
		pages_link = "https://english-e-reader.net" + pages_link

		item = {
			"book_name": book_name,
			"book_genre": genre,
			"author": author_name,
			"level": level,
			"description": desc,
			"tags": tags,
			"page_count": int(page_count),
			"analyze": analyze,
			"pages": []
		}

		self.books.append(item)

		for i in range(1, int(page_count) + 1):
			req = scrapy.Request(pages_link,
								 callback=self.page,
								 headers=self.api_headers,
								 body=f"page={str(i)}",
								 method="POST")
			req.cb_kwargs["page"] = i
			req.cb_kwargs["book_name"] = book_name
			yield req

	def page(self, response, **kwargs):
		pn = kwargs["page"]
		book_name = kwargs["book_name"]
		content = response.text
		self.pages.append({
			"book_name": book_name,
			"page": pn,
			"content": content
		})

	def close(self, spider, reason):

		with open("../data/books.json", "w", encoding="utf-8") as f:
			json.dump(self.books, f, ensure_ascii=False)

		with open("../data/pages.json", "w", encoding="utf-8") as f:
			json.dump(self.pages, f, ensure_ascii=False)


process = CrawlerProcess()
process.crawl(EnglishSpider)
process.start()
