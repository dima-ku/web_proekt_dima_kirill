from flask.signals import message_flashed
from flask_restful import Resource
from flask import jsonify
from flask import abort

import meilisearch
import json

client = meilisearch.Client('http://127.0.0.1:8080')

class BookResource(Resource):
    def get(self, request):
        res = client.index('books').search(request)['hits']
        if res:
            return jsonify({'books': res})
        abort(404, message=f'Book {request} not found')

class BookListResource(Resource):
    def get(self):
        with open('./db/books.json') as f:
            data = json.load(f)
            return jsonify(data)

class BookIdResource(Resource):
    def get(self, book_id):
        with open('./db/books.json') as f:
            data = json.load(f)
            for book in data:
                if book['id'] == book_id:
                    return jsonify(book)
        abort(404, message=f'Book {book_id} not found')