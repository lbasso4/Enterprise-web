"""
Copyright  Grup Blanca, Clàudia, Hana i Alex V.
Stock database
"""

from flask import render_template
from flask import jsonify, redirect, url_for
from app import app
from flask import request

import requests
import time

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector
from datetime import datetime
import serial
import re

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
#meter datos
dades_base_dades = {
    "host": "localhost",
    "user": "root",
    "password": "engicontrasenya702406?",
    "database": "printing_shop"
}

codi_colors = {
    "R": "Vermell", "G": "Verd", "B": "Blau", "Y": "Groc",
    "K": "Negre", "W": "Blanc", "C": "Cyan", "M": "Magenta",
}
SERIAL_PORT = 'COM3'    # aquí hem de posar el nostre port
BAUD_RATE = 9600        # velocitat de comunicació amb l'Arduino
FLASK_URL = 'http://127.0.0.1:5000/stock_web'


def get_connection():
    return mysql.connector.connect(**dades_base_dades)

# User model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

# Create database
with app.app_context():
    db.create_all()

def setup_database():
    # Crear taula buida - comencem eliminant l'inexistent base de dades, del contrari quin sentit tindria cridar-la??
    config = {key: val for key, val in dades_base_dades.items() if key != "database"}
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    #crear if no existeix
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dades_base_dades['database']}")
    cursor.execute(f"USE {dades_base_dades['database']}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            item_id     VARCHAR(20) PRIMARY KEY,
            colour      VARCHAR(10) NOT NULL,
            is_in_stock BOOLEAN NOT NULL DEFAULT TRUE,
            weight_g    VARCHAR(4) NOT NULL,
            marca       VARCHAR(20) NOT NULL,
            notes       TEXT,
            arrival_date DATE NOT NULL
        )
    """
    
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("BASE DE DADES CREADA. GRACIES PER FER SERVIR SERVEIS ENGICONSULTING S.A.")


#GENERAR el codi d'identificació del producte (no es sql)
def generar_id(colourCodigo: str, number: int, arrival_date: datetime) -> str:
    colourCodigo = colourCodigo.upper()
    if colourCodigo not in codi_colors:
        raise ValueError(f"Lletra invalida '{colourCodigo}'. Choose from: {list(codi_colors.keys())}")
    return f"{colourCodigo}{number:04d}{arrival_date.strftime('%d%m%Y')}"

#executar las variables que aparecen en otras partes del codigo

def add_item(colourCodigo: str, number: int, arrival_date: datetime,
             weight_g: float, is_in_stock: bool = True, marca:str="", notes: str = ""):

    item_id = generar_id(colourCodigo, number, arrival_date)
    colour_name = codi_colors[colourCodigo.upper()]

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO stock (item_id, colour, is_in_stock, weight_g, marca, notes, arrival_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (item_id, colour_name, is_in_stock, weight_g, marca, notes, arrival_date.date()))
        conn.commit()
        print("HECHO")
        return item_id
    except mysql.connector.IntegrityError:
        print("Error: el item seleccionado ya existe")
    
    cursor.close()
    conn.close()


def search_items(item_id=None, colour=None, in_stock=None, marca=None,min_weight=None, max_weight=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    #1=1 sempre sera true pero s'inclou per seguir amb els AND params
    prompt_seleccionar = "SELECT * FROM stock WHERE 1=1"
    params = []

    if item_id:
        prompt_seleccionar += " AND item_id = %s"
        params.append(item_id)
    if colour:
        # Accept either full name or single letter
        if len(colour) == 1:
            colour = codi_colors.get(colour.upper(), colour)
        prompt_seleccionar += " AND colour = %s"
        params.append(colour)
    if in_stock is not None:
        prompt_seleccionar += " AND is_in_stock = %s"
        params.append(in_stock)
    if min_weight is not None:
        prompt_seleccionar += " AND weight_g >= %s"
        params.append(min_weight)
    if max_weight is not None:
        prompt_seleccionar += " AND weight_g <= %s"
        params.append(max_weight)
    if marca is not None:
        prompt_seleccionar += " AND marca = %s"
        params.append(marca)

    cursor.execute(prompt_seleccionar, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def update_item(item_id: str, is_in_stock=None, weight_g=None, marca=None, notes=None):
    updates = []
    params = []

    if is_in_stock is not None:
        updates.append("is_in_stock = %s")
        params.append(is_in_stock)
        if is_in_stock == False:
            updates.append("weight_g = %s")
            params.append(0)
    if weight_g is not None:
        updates.append("weight_g = %s")
        params.append(weight_g)
    if notes is not None:
        updates.append("notes = %s")
        params.append(notes)
    if marca is not None:
        updates.append("marca = %s")
        params.append(marca)
    if not updates:
        print("ERROR: No hay ningun campo que puedas actualizar.")
        return

    params.append(item_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE stock SET {', '.join(updates)} WHERE item_id = %s", params)
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    print(f"Updated {rows} item(s)." if rows else f"Item '{item_id}' not found.")


def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stock WHERE item_id = %s", (item_id,))
    conn.commit()
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    print(f"Deleted item '{item_id}'." if rows else f"Item '{item_id}' no identificat.")

#codi claudia
def llegir_arduino():
    print("Esperant dades de l'Arduino...")

    # obrim la connexió amb l'Arduino per USB
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # esperem que l'Arduino s'inicialitzi

    try:
        if ser.in_waiting > 0:
            linia = ser.readline().decode('utf-8').strip()
            print(f"Rebut: {linia}")

            # el format que envia l'Arduino és: DATA:UID:PES
            # exemple: DATA:A3 F2 10 BC:312.5
            if linia.startswith('DATA:'):
                parts = linia.split(':')    # separem per ':'
                codi_nfc = parts[1]         # la segona part és el UID
                pes_g = float(parts[2])     # la tercera part és el pes en grams

                # enviem les dades al servidor Flask
                dades = {
                    'codi_nfc': codi_nfc,
                    'pes_g': pes_g  # convertim grams a grams
                }

                return codi_nfc, pes_g
    except:
        return None, None

#upon finishing la fase beta introducir EngiLab.html que, con su php, hará que todo tire
@app.route('/')
def index():
    return render_template('index.html')

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/index')
def index2():
    items = search_items()
    # serialise dates for template
    for item in items:
        if hasattr(item.get('arrival_date'), 'strftime'):
            item['arrival_date'] = item['arrival_date'].strftime('%d/%m/%Y')
    return render_template("stock_web.html",
                                  items=items,
                                  colours=codi_colors,
                                  msg=request.args.get('msg'),
                                  err=request.args.get('err'))


@app.route('/read_weight', methods=['GET'])
def api_read_weight():
    codi_nfc, pes = llegir_arduino()
    if pes is None:
        return jsonify({"ok": False, "error": "No s'ha obtingut cap resposta."})
    return jsonify({"ok": True, "item_id": codi_nfc, "weight": pes})


@app.route('/add', methods=['POST'])
def add():
    try:
        colour   = request.form['colour'].strip().upper()
        number   = int(request.form['number'])
        date_str = request.form['arrival_date'].strip()
        arrival  = datetime.strptime(date_str, "%d/%m/%Y")
        marca = request.form['marca'].strip().upper()
        notes    = request.form.get('notes', '').strip()
        in_stock = request.form.get('in_stock') == 'on'

        use_arduino = request.form.get('use_arduino') == 'on'
        if use_arduino:
            weight = llegir_arduino()
            if weight is None:
                return jsonify({"ok": False, "error": "Arduino not reachable — enter weight manually."})
        else:
            weight = float(request.form['weight_g'])

        item_id = add_item(colour, number, arrival, weight, in_stock,marca, notes)
        if not item_id:
            return jsonify({"ok": False, "error": "Item already exists."})
        return jsonify({"ok": True, "item_id": item_id})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route('/update', methods=['POST'])
def update():
    try:
        item_id  = request.form['item_id'].strip()
        item_id  = request.form['item_id'].strip()

        stock_v  = request.form.get('is_in_stock', '')
        in_stock = True if stock_v == 'y' else (False if stock_v == 'n' else None)
        weight   = request.form.get('weight_g', '').strip()
        notes    = request.form.get('notes', '').strip() or None
        update_item(item_id, is_in_stock=in_stock,
                    weight_g=float(weight) if weight else None, notes=notes)
        return jsonify({"ok": True, "message": f"Item '{item_id}' updated."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# Register route
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if Users.query.filter_by(username=username).first():
            return render_template("sign_up.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    
    return render_template("sign_up.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            items = search_items()
            for item in items:
                if hasattr(item.get('arrival_date'), 'strftime'):
                    item['arrival_date'] = item['arrival_date'].strftime('%d/%m/%Y')
                    return render_template("stock_web.html",
                                        items=items,
                                        colours=codi_colors,
                                        msg=request.args.get('msg'),
                                        err=request.args.get('err'))
        else:
            return render_template("sign_up.html", error="Invalid username or password")

    return render_template("index.html")

@app.route('/delete/<item_id>', methods=['POST'])
def delete(item_id):
    try:
        rows = delete_item(item_id)
        msg  = f"Deleted '{item_id}'." if rows else f"Item '{item_id}' not found."
        return jsonify({"ok": bool(rows), "message": msg})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route('/search')
def search():
    item_id   = request.args.get('item_id') or None
    colour    = request.args.get('colour') or None
    stock_v   = request.args.get('in_stock', '')
    in_stock  = True if stock_v == 'y' else (False if stock_v == 'n' else None)
    marca = request.args.get('marca') or None
    min_w     = request.args.get('min_weight', '')
    max_w     = request.args.get('max_weight', '')
    items = search_items(
        item_id=item_id, colour=colour, in_stock=in_stock, marca=marca,
        min_weight=float(min_w) if min_w else None,
        max_weight=float(max_w) if max_w else None
    )
    for item in items:
        if hasattr(item.get('arrival_date'), 'strftime'):
            item['arrival_date'] = item['arrival_date'].strftime('%d/%m/%Y')
    return jsonify(items)