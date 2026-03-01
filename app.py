from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
from flask import session, redirect, url_for
from flask import jsonify
import os, json, hashlib, secrets
from dotenv import load_dotenv
from flask import request, Response

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

load_dotenv()

# --- секретный ключ для сессий ---
app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)

# --- простое "хранилище" пользователей ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

def _load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            return json.load(open(USERS_FILE))
        except Exception:
            return {}
    return {}

def _save_users(d: dict) -> None:
    with open(USERS_FILE, 'w') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def login_required():
    if not session.get('user'):
        # куда вернуться после логина
        nxt = request.path.strip('/') 
        return redirect(url_for('login', next=nxt))
    return None

# --- страницы (как были) ---
@app.route('/')
def index():
#     пример: главную пускаем без авторизации; хочешь - включим защиту (раскомментируй 2 строки ниже)
#     guard = login_required()
#     if guard: return guard
     return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('panel.html')

@app.route('/settings')
def settings():
     guard = login_required()
     if guard: return guard
     return render_template('settings.html')
@app.route("/test")

def test():
    return render_template("test.html")

@app.route("/pro")
def pro():
    return render_template("pro.html")

@app.route('/panel')
def panel():
    return render_template('panel.html')

@app.route('/api/ping')
def ping():
    return jsonify({'ok': True})

# --- AI ассистент (как было) ---
@app.route('/api/assistant', methods=['POST'])
def api_assistant():
    data = request.get_json()
    q = data.get('question', '').strip() if data else ''
    if not q:
        return jsonify({'answer': '❗ Пустой запрос.'})
    try:
        import requests
        OPENAI_KEY = os.getenv('OPENAI_API_KEY')
        r = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {OPENAI_KEY}','Content-Type':'application/json'},
            json={'model':'gpt-3.5-turbo','messages':[{'role':'system','content':'Ты — AI-ассистент'},{'role':'user','content': q}]},
            timeout=30
        )
        reply = r.json()['choices'][0]['message']['content']
        return jsonify({'answer': reply})
    except Exception as e:
        return jsonify({'answer': f'Ошибка: {e}'})

# --- ЛОГИН / РЕГИСТРАЦИЯ / ВЫХОД ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        users = _load_users()

        if username in users and users[username] == _hash(password):
            session['user'] = username
            nxt = request.args.get('next') or '/'
            return redirect(nxt)

        # если неверный логин или пароль
        return render_template('login.html', error='❌ Неверный логин или пароль')

    # если это GET-запрос — просто отдать страницу логина
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        confirm  = (data.get('confirm')  or '').strip()
        if not username or not password:
            return render_template('register.html', error='⚠️ Заполни все поля')
        if password != confirm:
            return render_template('register.html', error='⚠️ Пароли не совпадают')
        users = _load_users()
        if username in users:
            return render_template('register.html', error='⚠️ Пользователь уже существует')
        users[username] = _hash(password)
        _save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# === АНАЛИТИКА ПРОДАЖ ===
from flask import jsonify

@app.route("/analytics_data")
def analytics_data():
    data = [
        {
            "name": "Подоконник Ecosill Белый 150 мм",
            "price": 799,
            "stock": 48,
            "sales": 12,
            "ads": "Активна"
        },
        {
            "name": "Откос Moeler Light Матовый 200 мм",
            "price": 499,
            "stock": 36,
            "sales": 9,
            "ads": "Запустить"
        },
        {
            "name": "Danke Premium Антрацит 200 мм",
            "price": 899,
            "stock": 22,
            "sales": 5,
            "ads": "Активна"
        }
    ]
    return jsonify(data)

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

def login_required():
    if not session.get('user'):
        # куда вернуться после логина
        nxt = request.path.strip('/')
        return redirect(url_for('login', next=nxt))
    return None

# === Telegram авторизация (через Mini App) ===
@app.route('/tg_login')
def tg_login():
    from urllib.parse import unquote
    init_data = request.args.get('initData')
    if not init_data:
        return "❌ Нет данных Telegram", 400

    try:
        data_str = unquote(init_data)
        username = None
        if "username=" in data_str:
            username = data_str.split("username=")[1].split("&")[0]
        elif "first_name=" in data_str:
            username = data_str.split("first_name=")[1].split("&")[0]

        if username:
            session['user'] = f"tg:{username}"
            return redirect(url_for('index'))
        else:
            return "⚠️ Не найден username в initData", 400
    except Exception as e:
        return f"Ошибка: {e}", 500
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
# === УНИВЕРСАЛЬНАЯ ЗАГРУЗКА ВНУТРЕННИХ СТРАНИЦ (БЕЗ ЗАЩИТЫ) ===
@app.route('/<page>')
def render_static_pages(page):
    import os
    template_path = os.path.join('templates', f'{page}.html')
    if os.path.exists(template_path):
        return render_template(f'{page}.html')
    return "404: Страница не найдена", 404
# ---------- API: сохранение и загрузка истории ----------
from flask import session
from flask_session import Session

app.config["SECRET_KEY"] = "sellerapp_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/api/history", methods=["GET", "POST"])
def chat_history():
    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        data = request.get_json()
        msg = data.get("message")
        role = data.get("role", "user")
        if msg:
            session["chat"].append({"role": role, "text": msg})
            session.modified = True
        return jsonify({"status": "ok"})
    else:
        return jsonify(session.get("chat", []))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# ======= Панель администратора =======
from datetime import datetime
import json

@app.route("/admin")
def admin_panel():
    auth = request.authorization
    if not auth or auth.username != "admin" or auth.password != "sellerapp123":
        return Response(
            'Доступ запрещён.\nВведите логин и пароль администратора.',
            401,
            {'WWW-Authenticate': 'Basic realm="SellerApp Admin"'}
        )

    try:
        with open("/root/sellerapp/users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    formatted_users = [
        {
            "id": uid,
            "username": d.get("username", "—"),
            "email": d.get("email", "—"),
            "pro": "✅" if d.get("pro") else "❌",
            "expires": d.get("expires", "—"),
            "registered": d.get("registered", "—"),
        }   for uid, d in users.items()
    ]
    return render_template("admin.html", users=formatted_users)
