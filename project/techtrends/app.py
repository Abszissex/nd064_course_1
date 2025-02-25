import sqlite3
import logging
import sys
from flask import Flask, json, render_template, request, url_for, redirect, flash

# To be honest I am not sure if this was the idea behind it
# but since we don't keep multiple open connections to the database
# I don't think it would make sense otherwise.
db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    global db_connection_count
    db_connection_count += 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get the number of posts in the database
def get_post_count():
    connection = get_db_connection()
    post_count_row = connection.execute('SELECT COUNT(*) AS count FROM posts').fetchone()
    connection.close()

    return post_count_row['count']

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()

    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response

@app.route('/metrics')
def metrics():
    global db_connection_count
    total_posts_in_db = get_post_count()


    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count, "post_count": total_posts_in_db}),
            status=200,
            mimetype='application/json'
    )

    return response


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Found no article for id: %d', post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info('Retrieved article: %s', post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


# set logger to handle STDOUT and STDERR 
stdout_handler = logging.StreamHandler(sys.stdout)
stderr_handler = logging.StreamHandler(sys.stderr)
handlers = [stderr_handler, stdout_handler]

# format output
format_output = '%(levelname)s:%(name)s:%(asctime)s, %(message)s'


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers, datefmt='%Y-%m-%d %H:%M:%S')
    app.run(host='0.0.0.0', port='3111')
