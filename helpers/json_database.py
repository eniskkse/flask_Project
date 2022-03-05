import json

file_books = open("../data/books.json", encoding="utf-8").read()
file_pages = open("../data/pages.json", encoding="utf-8").read()

data_books = json.loads(file_books)
data_pages = json.loads(file_pages)

# Tüm ayrı sayfaları, tek kitap ismi başlığında birleşiyor.
pages = {}
for page in data_pages:
	try:
		pages[page["book_name"]].append({
			"page": page["page"],
			"content": page["content"],
		})
	except:
		pages[page["book_name"]] = [{
			"page": page["page"],
			"content": page["content"],
		}]

output_books = []
# Sayfa sıralamaları küçükten büyüğe sortlanıyor
for page in pages:
	_page = sorted(pages[page], key=lambda k: k["page"], reverse=False)

	# Sayfalara ait olan kitap bilgileri alınıyor.
	book = [x for x in data_books if x["book_name"] == page][0]
	# Sayfalar kitaba ekleniyor.
	book["pages"] = _page
	# Kitap global diziye atılıyor.
	output_books.append(book)

# Json save
with open("../data/database.json", "w", encoding="utf-8") as f:
	json.dump(output_books, f, ensure_ascii=False)
