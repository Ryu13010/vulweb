from flask import Flask, jsonify, request
import platform
import sqlite3

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
            <style>
                .hidden-link {
                    color: white;
                    background-color: white;
                }
                .hidden-link:hover {
                    color: black;
                    background-color: white;
                }
            </style>
        </head>
        <body>
            <h1>Login Page</h1>
            
            <!-- Hint: Try accessing /admin -->

            <a href="/admin" class="hidden-link">Admin</a>
            
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

                // Fetch system info from /system-info endpoint
                fetch('/system-info')
                    .then(response => response.json())
                    .then(data => {
                        console.log('System Info:', data.os_info);
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

@app.route('/system-info', methods=['GET'])
def system_info():
    os_info = {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }
    return jsonify(os_info=os_info)

@app.route('/server-info', methods=['GET'])
def server_info():
    server_info = {
        'server_software': request.environ.get('SERVER_SOFTWARE', 'unknown'),
        'server_name': request.environ.get('SERVER_NAME', 'unknown'),
        'server_protocol': request.environ.get('SERVER_PROTOCOL', 'unknown'),
        'http_host': request.environ.get('HTTP_HOST', 'unknown'),
        'server_port': request.environ.get('SERVER_PORT', 'unknown'),
        'client_ip': request.remote_addr,
        'python_version': platform.python_version()
    }
    return jsonify(server_info=server_info)

@app.route('/admin', methods=['GET'])
def admin():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Page</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <h1>Admin Page</h1>
            <p>Welcome to the admin page. Only authorized users should be here.</p>
        </body>
        </html>
    '''

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

