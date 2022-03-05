from flask import Flask, jsonify, request
import json
from models import Book

data = json.loads(open("data/database.json", encoding="utf-8").read())

app = Flask(__name__)
app.config["DEBUG"] = True

book = Book(data=data)


@app.route("/", methods=["POST"])
def home():
	return jsonify(book.get_all_books())


@app.route("/book", methods=["POST"])
def book_detail():
	book_name = request.args.get("book_name")
	return jsonify(book.get_book(book_name=book_name))


if __name__ == '__main__':
	app.run()
