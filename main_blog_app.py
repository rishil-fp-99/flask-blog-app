from flask import Flask,flash,request, redirect, url_for, render_template, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from time import sleep

app = Flask(__name__)
app.secret_key = "mysecretkey"

def init_db():
    conn = sqlite3.connect("blog.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

init_db()

home_template = "home_template.html"

add_post_template = "add_post_template.html"

edit_post_template = "edit_post_template.html"

auth_template = "auth_template.html"


def get_posts():
    conn = sqlite3.connect("blog.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    conn.close()
    return posts

@app.route('/')
def home():
    return render_template(home_template, posts=get_posts())


@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn = sqlite3.connect("blog.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        flash("Post Added successfully!", "success")
        # sleep(5)
        return redirect(url_for('home'))
    return render_template(add_post_template)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("blog.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    print(post)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        c.execute("UPDATE posts SET title=?, content=? WHERE id=?", (title, content, post_id))
        conn.commit()
        conn.close()
        flash("Post Edited successfully!", "success")
        return redirect(url_for('home'))
    conn.close()
    return render_template(edit_post_template, post=post)

@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("blog.db")
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    flash("Post Deleted successfully!", "success")
    # sleep(1)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = sqlite3.connect("blog.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "Username already taken."
        conn.close()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template(auth_template, title="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("blog.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        return "Invalid credentials."
    return render_template(auth_template, title="Login")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
