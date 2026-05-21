import os
import psycopg2

from flask import Flask, session, jsonify, abort, request, redirect, url_for
from flask_session import Session

# Create the flask app
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Conversion functions for each type


def get_objects(cursor):
    def to_object(row):
        obj = {}
        for i, col in enumerate(cursor.description):
            obj[col.name] = row[i]

        return obj

    return [to_object(row) for row in cursor.fetchall()]


# Connect to database
with psycopg2.connect(
    database='books', user='postgres',
    password='246432', host='localhost', port='5432'
) as conn:

    # Define view functions
    def view_logged_in_nav(search=''):
        return f"""
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">Books</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                    <form class="navbar-nav me-auto">
                        <input class="form-control me-2" value="{search}" type="search" name="search" placeholder="Search" aria-label="Search">
                        <button class="btn btn-outline-success" type="submit">Search</button>
                    </form>
                    <form class="d-flex" action="/logout" onsubmit="return confirm('Are you sure?');">
                        <button class="btn btn-outline-secondary" type="submit">Logout</button>
                    </form>
                </div>
            </div>
        </nav>
        """
    
    def view_basic_nav():
        return f"""
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">Books</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <!--div class="collapse navbar-collapse" id="navbarSupportedContent">
                    <form class="navbar-nav me-auto">
                        <input class="form-control me-2" type="search" name="search" placeholder="Search" aria-label="Search">
                        <button class="btn btn-outline-success" type="submit">Search</button>
                    </form>
                </div-->
            </div>
        </nav>
        """

    def view_page(title, header, body):
        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{title}</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
            </head>
            <body>
                <header>{header}</header>
                <div class="container">
                {body}
                </div>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
            </body>
        </html>
        """
    
    def view_err_msg(msg = None):
        if msg is None: 
            return "" 
        
        return f"""
        <div class="alert alert-danger" role="alert">{msg}</div>
        """

    def view_login(msg=None):
        return f"""
            <form method="POST" class="row">
                <div class="mb-3">
                    <h1>Login</h1>
                </div>

                {view_err_msg(msg)}

                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" required class="form-control" name="username"/>
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" required class="form-control" name="password"/>
                </div>

                <div class="mb-3">
                    <input type="submit" name="action" class="btn btn-primary" value="Login"/>
                    <input type="submit" name="action" class="btn btn-secondary" value="Register"/>
                </div>
            </form>
            """

    def view_register(msg=None):
        return f"""
            <form method="POST" class="row">
                <div class="mb-3">
                    <h1>Register</h1>
                </div>
            
                {view_err_msg(msg)}

                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" required name="username" class="form-control"/>
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" required name="password" class="form-control"/>
                </div>

                <div class="mb-3">
                    <label for="confirm_password" class="form-label">Confirm Password</label>
                    <input type="password" name="confirm_password" class="form-control"/>
                </div>

                <div class="mb-3">
                    <input type="submit" name="action" value="Register" class="btn btn-primary"/>
                </div>
            </form>
            """

    def view_reviews(reviews):
        if len(reviews) == 0:
            return "No reviews"

        out = '<ul class="list-group">'

        for review in reviews:
            out += f"""<li class="list-group-item">
                <h5>{review['username']}</h5>
                <p><b>Score:</b> {review['score']}</p>
                <p>{review['review']}</p>
            </li>"""

        out += "</ul>"

        return out
    
    def view_review_form(has_review):
        if has_review:
            return ""
        
        return f"""
        <div class="mb-3 container">
            <form method="POST">
                <div class="row mb-3">
                    <label for="score" class="form-label">Score</label>
                    <select name="score" required class="form-control">
                        <option></option>
                        <option>1</option>
                        <option>2</option>
                        <option>3</option>
                        <option>4</option>
                        <option>5</option>
                    </select>
                </div>
                <div class="row mb-3">
                    <label for="review" class="form-label">Review</label>
                    <textarea name="review" required class="form-control"></textarea>
                </div>
                <div class="row mb-3">
                    <input type="submit" rows="5" class="btn btn-primary" value="Post Review"/>
                </div>
            </form>
        </div>
        """

    def view_book(book, reviews, has_review):
        return f"""
        <div class="mb-3">
            <h2>{book['title']}</h2>
        </div>
        
        <div class="mb-3">
            <ul class="list-group">
                <li class="list-group-item">
                    <b>Author:</b>
                    <span>{book['author']}</span>
                </li>
                
                <li class="list-group-item">
                    <b>Year:</b>
                    <span>{book['year']}</span>
                </li>

                <li class="list-group-item">
                    <b>ISBN:</b>
                    <span>{book['isbn']}</span>
                </li>

                <li class="list-group-item">
                    <b>Average Rating:</b>
                    <span>{book['averageRating']}</span>
                </li>

                <li class="list-group-item">
                    <b>Ratings Count:</b>
                    <span>{book['ratingsCount']}</span>
                </li>
            </ul>
        </div>

        <div class="mb-3">
            <h4>Reviews</h4>
        </div>

        {view_review_form(has_review)}

        <div class="mb-3">
            {view_reviews(reviews)}
        </div>
        """

    def view_book_item(book):
        return f"""
        <li class="list-group-item">
            <a href="{'/book/' + book['isbn']}">{book['title']}</a>
            <span>by {book['author']}</span>
        </li>
        """

    def view_books(books):
        return f"""
        <ul class="list-group">
            {''.join([view_book_item(book) for book in books])}
        </ul>
        """

    def view_index(search='', books=None):
        return f"""
        <div class="mb-3">
            <h1>{'Book Database' if search == '' else f'Search results: "{search}"'}</h1>
        </div>
        {'<div class="mb-3">No results found</div>' if books is None or len(books) == 0 else view_books(books)}
        """ 

    def is_logged_in():
        return 'current_user' in session

    # Page routes here
    @app.route("/")
    def index():
        if not is_logged_in():
            return redirect(url_for('login'))

        # Find the books that match the search criteria
        if 'search' in request.args:
            with conn.cursor() as cursor:
                search_match = '%' + request.args['search'].lower() + '%'
                cursor.execute("SELECT * FROM books WHERE LOWER(title) LIKE %s OR LOWER(author) LIKE %s OR LOWER(isbn) LIKE %s",
                               (search_match, search_match, search_match))
                return view_page('Books', view_logged_in_nav(request.args['search']), view_index(request.args['search'], get_objects(cursor)))
        else:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM books")
                return view_page('Books', view_logged_in_nav(), view_index(books=get_objects(cursor)))

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # Check if password confirmation is correct
            if request.form['password'] != request.form['confirm_password']:
                return view_page('Register', view_basic_nav(), view_register('Password confirmation does not match'))

            # Create user and register to database
            with conn.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO users (username, password, created) VALUES (%s, %s, NOW());", (
                        request.form['username'], request.form['password']))
                    conn.commit()
                    return redirect(url_for('login'))
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    return view_page('Register', view_basic_nav(), view_register('Username is already taken'))
                

        return view_page('Register', view_basic_nav(), view_register())

    @app.route("/logout")
    def logout():
        session.pop('current_user')
        return redirect(url_for('login'))

    @app.route("/book/<isbn>", methods=['GET', 'POST'])
    def book(isbn):
        if not is_logged_in():
            return redirect(url_for('login'))

        # Get book
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books WHERE ISBN = %s;", (isbn,))
            bks = get_objects(cursor)

            if len(bks) == 0:
                abort(404)

            # Insert the review 
            if request.method == 'POST':
                # Insert the new review 
                cursor.execute("INSERT INTO reviews (postedby, reviewof, review, score, created) VALUES (%s, %s, %s, %s, NOW());",
                               (session['current_user']['userid'], bks[0]['bookid'], request.form['review'], request.form['score']))
                conn.commit()

            # Check if review is present 
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE postedby = %s AND reviewof = %s;", 
                            (session['current_user']['userid'], bks[0]['bookid']))
            
            has_review = cursor.fetchall()[0][0] > 0

            # Get the reviews
            cursor.execute(
                "SELECT * FROM reviews r LEFT JOIN users u ON r.postedby = u.userid WHERE reviewof = %s", (bks[0]['bookid'],))

            # Get Google Books data
            import requests

            url = "https://www.googleapis.com/books/v1/volumes?"

            # query to search using isbn
            res = requests.get(url, params={ "q": {f"isbn:{isbn}"} })

            data = res.json()

            if len(data['items']) > 0:
                bks[0]['averageRating'] = data['items'][0]['volumeInfo']['averageRating']
                bks[0]['ratingsCount'] = data['items'][0]['volumeInfo']['ratingsCount']
            else:
                bks[0]['averageRating'] = 'N/A'
                bks[0]['ratingsCount'] = 'N/A'

            return view_page('Book', view_logged_in_nav(), view_book(bks[0], get_objects(cursor), has_review))

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if is_logged_in():
            return redirect(url_for('index'))

        if request.method == 'POST':
            # If action is user, redirect to register
            if request.form['action'] == 'Register':
                return redirect(url_for('register'))

            # Authenticate user details
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                               (request.form['username'], request.form['password']))

                users = get_objects(cursor)

                if len(users) == 0:
                    return view_page('Login', view_basic_nav(), view_login("Invalid username or password"))
                else:
                    # Redirect
                    session['current_user'] = users[0]
                    return redirect(url_for('index'))
        else:
            return view_page('Login', view_basic_nav(), view_login())

    # Define API routes here
    @app.route("/api/<isbn>", methods=['GET', 'POST'])
    def get_book(isbn):
        with conn.cursor() as cursor:
            cursor.execute("SELECT title, author, year, isbn, COUNT(reviewid) as review_count, AVG(score) as average_score FROM Books b LEFT JOIN Reviews r ON b.bookid = r.reviewof WHERE isbn = %s GROUP BY title, year, author, isbn;", (isbn))
            books = get_objects(cursor)

            if len(books) == 0:
                abort(404)

            return jsonify(books[0])

    app.run(debug=True)
