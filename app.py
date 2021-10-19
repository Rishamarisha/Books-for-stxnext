from flask import Flask, jsonify, request
import urllib.request, json

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello. My name is Marina Kalaur. Welcome to my backend application about books.</p>"

def book_pattern(book):
    new_book = {
        "title": book["volumeInfo"]["title"],
        "authors": book["volumeInfo"]["authors"],
        "published_date": book["volumeInfo"]["publishedDate"],
        "id": book["id"],
    }   
    if "averageRating" in book["volumeInfo"]:
        new_book["average_rating"] = book["volumeInfo"]["averageRating"]
    
    if "ratingsCount" in book["volumeInfo"]:
        new_book["ratings_count"] = book["volumeInfo"]["ratingsCount"]

    if "categories" in book["volumeInfo"]:
        new_book["categories"] = book["volumeInfo"]["categories"]

    if "imageLinks" in book["volumeInfo"]:
        new_book["thumbnail"] = book["volumeInfo"]["imageLinks"]["thumbnail"]
    return new_book

with urllib.request.urlopen('https://www.googleapis.com/books/v1/volumes?q=Hobbit') as response:
    data = json.loads(response.read().decode()) 
    all_books = []
    for book in data["items"]:
        all_books.append(book_pattern(book))


@app.route("/books")
def get_books():
    sorted_by = request.args.get('sort')
    if sorted_by == "-published_date":
        sorted_books = sorted(all_books, key=lambda book: book["published_date"], reverse=True)
    elif sorted_by == "published_date":
        sorted_books = sorted(all_books, key=lambda book: book["published_date"])
    else:
        sorted_books = all_books
    
    authors = request.args.getlist('author')
    
    if authors:
        books_filtered_by_author = authors_books(sorted_books)
    else:
        books_filtered_by_author = sorted_books

    pub_date = request.args.get('published_date')

    if pub_date:
        books_filtered_by_date = published_date(books_filtered_by_author)
    else:
        books_filtered_by_date = books_filtered_by_author

    return jsonify(books_filtered_by_date)

# Making a list of authors in data with quotes to match a task
def authors_with_quotes(authors_list):
    list_of_authors = []
    for author in authors_list:
        list_of_authors.append('\"' + author + '\"')
    return list_of_authors


def authors_books(books_lst):
    authors = request.args.getlist('author')
    filtered_books = []
    for book in books_lst:
        for author in authors:
            if author in authors_with_quotes(book['authors']):
                filtered_books.append(book)
    return filtered_books

def published_date(books_lst):
    pub_date = request.args.get('published_date')
    filtered_books = []
    for book in books_lst:
        if pub_date in book["published_date"]:
            filtered_books.append(book)
    return filtered_books

@app.route("/books/<id>")
def get_book(id):
    for book in all_books:
        if book["id"] == id:
            return book

@app.route("/db", methods=['POST']) 
def add_books():
    request_data = request.get_json()
    with urllib.request.urlopen('https://www.googleapis.com/books/v1/volumes?q=' + request_data["q"]) as response:
        data = json.loads(response.read().decode())
        new_list = []
        for book in data["items"]:
            new_book = book_pattern(book)
            new_list.append(new_book)
            all_books.append(new_book)
    return jsonify(new_list)