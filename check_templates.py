from flask import Flask
import os

app = Flask(__name__, template_folder='templates')

print("Текущая рабочая директория:", os.getcwd())
print("Ищет шаблоны здесь:", app.template_folder)
print("Содержимое папки templates:")
print(os.listdir(app.template_folder))
