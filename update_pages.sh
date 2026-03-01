# === Создаём 5 HTML-шаблонов ===
for page in stocks analytics forecast settings promo; do
cat << HTML > /root/sellerapp/templates/${page}.html
{% extends "base.html" %}
{% block content %}
<h2>
  {% if page == 'stocks' %}📦 Остатки и продажи
  {% elif page == 'analytics' %}📊 Аналитика и графики
  {% elif page == 'forecast' %}🧠 Прогноз спроса
  {% elif page == 'settings' %}⚙️ Настройки
  {% elif page == 'promo' %}💰 Реклама и продвижение{% endif %}
</h2>
<p>Контент страницы <b>${page}</b> загружен через AJAX.</p>
<a href="/" class="btn" onclick="navigate('/'); return false;">⬅ Назад</a>
{% endblock %}
HTML
done

# === Обновляем app.py ===
cat << PY > /root/sellerapp/app.py
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<page>')
def subpage(page):
    pages = ['stocks', 'analytics', 'forecast', 'settings', 'promo']
    if page in pages:
        return render_template(f'{page}.html', page=page)
    else:
        return "Страница не найдена", 404

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "SellerApp Pro", "code": 200})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
PY

# === Перезапускаем сервис ===
systemctl restart sellerapp && systemctl status sellerapp --no-pager
