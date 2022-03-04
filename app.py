from flask import Flask, jsonify
import json
import pull_att as pa
app = Flask(__name__)


eng_json = json.loads(
            open("English_reader.json", encoding="utf-8").read())
kitaps = str(pa.Book_attributes.ids(eng_json))
selected_book = input("Kitap ismi giriniz.\n")
book_details = pa.Book_attributes.detail(eng_json,selected_book)
book_details = str(book_details)

@app.route("/")
def start_api():
    project_name = "English Reader"
    return project_name

@app.route("/Enis.dev/Books")
def public():
    # id
    # Book_name
    # book_author
    # level
    return kitaps


@app.route(f"/Enis.dev/Books/{selected_book}")
def book_detail():
    return book_details
    # id
    # name
    # description
    # page_number
    # other_details

@app.route("/Enis.dev/Books/Details/Pages")
def book_pages():
    pass



if __name__ == '__main__':
    app.run()
