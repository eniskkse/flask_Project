import json


class Book_attributes():

    @staticmethod
    def ids(eng_json):
        # id
        # Book_name
        # book_author
        # level
        books = []
        for book in eng_json:
            book_name = book["Book Name"]
            book_author = book["Author"]
            level = book["Book English Level"]
            books_dict = {
                "Kitap İsmi": book_name,
                "Kitap Yazarı": book_author,
                "Kitap Seviyesi": level
            }
            books.append(books_dict)
        return books
    @staticmethod
    def detail(eng_json,name):
        book_details = []
        control = False
        for i in eng_json:
            if name in i["Book Name"]:
                control = True
                desc = i["Book Description"]
                page_number = i["Book Pages Count"]
                book_detail = {
                    "Name": name,
                    "Book Description" : desc,
                    "Book Pages Count" : page_number,
                }
                book_details.append(book_detail)
            else:
                pass
        if control:
            return book_details
        else:
            return "Aradığınız kitap bulunamadı!"





if __name__ == "__main__":
    Book_attributes()