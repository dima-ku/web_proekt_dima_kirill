from logging import debug
from flask import Flask, request, redirect
from flask.templating import render_template
import json
import meilisearch

client = meilisearch.Client('http://127.0.0.1:8080')

json_file = open('db/books.json')
books = json.load(json_file)
client.index('books').add_documents(books)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
    


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        search_request = request.form['search_bar']
        return redirect(f'/{search_request}')
    param = {}
    param['title'] = 'Лучший сайт по поиску книг'
    return render_template('base.html')


@app.route('/<search_request>')
def search_result(search_request):
    param = {}
    param['title'] = search_request
    param['books'] = client.index('books').search(search_request)['hits']
    return render_template('search_result.html', param=param)


app.run(debug=True)
