from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vulnerable Site</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <h1>Login Page</h1>
            
            <form id="loginForm">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username"><br><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password"><br><br>
                <input type="submit" value="Login">
            </form>
            <div id="result"></div>

            <h2>Leave a Comment</h2>
            <form id="commentForm">
                <label for="comment">Comment:</label>
                <input type="text" id="comment" name="comment"><br><br>
                <input type="submit" value="Submit">
            </form>
            <div id="comments"></div>

            <h2>Include a File</h2>
            <form id="includeForm">
                <label for="filename">Filename:</label>
                <input type="text" id="filename" name="filename"><br><br>
                <input type="submit" value="Include">
            </form>
            <div id="fileContent"></div>

            <script>
                document.getElementById('loginForm').addEventListener('submit', function(event) {
                    event.preventDefault();
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;

                    fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ username, password })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('result').innerText = data.message;
                    });
                });

                document.getElementById('commentForm').addEventListener('submit', function(event) {
                    event.preventDefault();
                    const comment = document.getElementById('comment').value;
                    const commentsDiv = document.getElementById('comments');
                    commentsDiv.innerHTML += `<p>${comment}</p>`;
                });

                document.getElementById('includeForm').addEventListener('submit', function(event) {
                    event.preventDefault();
                    const filename = document.getElementById('filename').value;

                    fetch('/include?file=' + filename)
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('fileContent').innerText = data;
                    });
                });

                // Fetch credentials from /get-credentials endpoint
                fetch('/get-credentials')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Credentials:', data.credentials);
                    });
            </script>
        </body>
        </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    with open('login.txt', 'r') as f:
        stored_username, stored_password = f.read().strip().split(':')

    if username == stored_username and password == stored_password:
        return jsonify(message='Login successful!')
    else:
        return jsonify(message='Login failed!')

@app.route('/get-credentials', methods=['GET'])
def get_credentials():
    with open('login.txt', 'r') as f:
        credentials = f.read().strip()
    return jsonify(credentials=credentials)

@app.route('/comments', methods=['POST'])
def comments():
    comment = request.form['comment']
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute("INSERT INTO comments (comment) VALUES (?)", (comment,))
    conn.commit()
    conn.close()
    return f'<p>{comment}</p>'

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    # Vulnérabilité d'injection SQL
    query = f"SELECT * FROM comments WHERE comment LIKE '%{query}%'"
    c.execute(query)
    results = c.fetchall()
    conn.close()
    return jsonify(results=results)

@app.route('/include', methods=['GET'])
def include():
    filename = request.args.get('file')
    try:
        with open(filename, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e)

def init_db():
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment TEXT
    )
    ''')
    c.execute("INSERT INTO comments (comment) VALUES ('Test comment')")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')

