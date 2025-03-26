from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def initialize_db():
    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        price REAL,
                        gst_rate REAL)''')
    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        quantity INTEGER,
                        total_price REAL,
                        gst_amount REAL,
                        final_price REAL,
                        FOREIGN KEY (product_id) REFERENCES products(id))''')

    conn.commit()
    conn.close()

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    name = data.get("name")
    price = data.get("price")
    gst_rate = data.get("gst_rate")

    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, gst_rate) VALUES (?, ?, ?)", (name, price, gst_rate))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added successfully!"}), 201


@app.route('/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return jsonify(products)


@app.route('/purchase', methods=['POST'])
def purchase_item():
    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price, gst_rate FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    price, gst_rate = product
    total_price = price * quantity
    gst_amount = (total_price * gst_rate) / 100
    final_price = total_price + gst_amount

    cursor.execute("INSERT INTO bills (product_id, quantity, total_price, gst_amount, final_price) VALUES (?, ?, ?, ?, ?)",
                   (product_id, quantity, total_price, gst_amount, final_price))
    conn.commit()
    conn.close()

    return jsonify({"message": "Purchase successful!", "final_price": final_price}), 201


@app.route('/bills', methods=['GET'])
def get_bills():
    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills")
    bills = cursor.fetchall()
    conn.close()

    return jsonify(bills)