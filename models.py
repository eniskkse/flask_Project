import json


class JsonClassMain():

	def __init__(self, data):
		self.data = data


class Book(JsonClassMain):

	def get_all_books(self):
		return [x["book_name"] for x in self.data]

	def get_book(self, book_name):
		return [x for x in self.data if x["book_name"] == book_name]