from flask import Flask, request, redirect, render_template, jsonify
import string, random, sqlite3, os

app = Flask(__name__)
DATABASE = 'url_data.db'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE,
                long_url TEXT
            )
        ''')

# Generate short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Insert URL into database
def insert_url(short_code, long_url):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO urls (short_code, long_url) VALUES (?, ?)', (short_code, long_url))
        conn.commit()

# Get long URL from short code
def get_long_url(short_code):
    with sqlite3.connect(DATABASE) as conn:
        result = conn.execute('SELECT long_url FROM urls WHERE short_code = ?', (short_code,)).fetchone()
        return result[0] if result else None

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form.get('long_url') or request.json.get('long_url')
    short_code = generate_short_code()
    
    # Ensure uniqueness
    while get_long_url(short_code) is not None:
        short_code = generate_short_code()
    
    insert_url(short_code, long_url)
    short_url = request.host_url + short_code
    return jsonify({'short_url': short_url})

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    return 'URL not found', 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
