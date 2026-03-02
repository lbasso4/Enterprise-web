"""
Copyright Grup Blanca, Clàudia, Hana i Alex V.
Stock database
"""

import mysql.connector
from datetime import datetime
import re

#Public Variables
#PERSONAL DATA (MYSQL SERVER SET UP IN SERVER o en este caso el portátil)
dades_base_dades = {
    "host": "localhost",
    "user": "root",
    "password": "engicontrasenya702406?",
    "database": "printing_shop"
}

codi_colors = {
    "R": "Red",
    "G": "Green",
    "B": "Blue",
    "Y": "Yellow",
    "K": "Black",
    "W": "White",
    "C": "Cyan",
    "M": "Magenta",
}


#setup, link de interés: https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html

def get_connection():
    return mysql.connector.connect(**dades_base_dades)


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
            colour      CHAR(1) NOT NULL,
            is_in_stock BOOLEAN NOT NULL DEFAULT TRUE,
            weight_g    VARCHAR(4) NOT NULL,
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
        raise ValueError(f"Invalid colour letter '{colourCodigo}'. Choose from: {list(codi_colors.keys())}")
    return f"{colourCodigo}{number:04d}{arrival_date.strftime('%d%m%Y')}"


def parse_id(item_id: str) -> dict:
    """Parse an ID string back into its components."""
    pattern = r'^([A-Z])(\d{4})(\d{2})(\d{2})(\d{4})$'
    match = re.match(pattern, item_id)
    if not match:
        raise ValueError(f"Invalid ID format: '{item_id}'. Expected format: R000421012026")
    colour, num, day, month, year = match.groups()
    return {
        "colourCodigo": colour,
        "colour_name": codi_colors.get(colour, "Unknown"),
        "number": int(num),
        "arrival_date": datetime(int(year), int(month), int(day))
    }


#executar las variables que aparecen en otras partes del codigo

def add_item(colourCodigo: str, number: int, arrival_date: datetime,
             weight_g: float, is_in_stock: bool = True, notes: str = ""):

    item_id = generar_id(colourCodigo, number, arrival_date)
    colour_name = codi_colors[colourCodigo.upper()]

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO stock (item_id, colour, is_in_stock, weight_g, notes, arrival_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (item_id, colour_name, is_in_stock, weight_g, notes, arrival_date.date()))
        conn.commit()
        print("HECHO")
        return item_id
    except mysql.connector.IntegrityError:
        print("Error: el item seleccionado ya existe")
    
    cursor.close()
    conn.close()


def search_items(item_id=None, colour=None, in_stock=None, min_weight=None, max_weight=None):
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

    cursor.execute(prompt_seleccionar, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def update_item(item_id: str, is_in_stock=None, weight_g=None, notes=None):
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
    print(f"Deleted item '{item_id}'." if rows else f"❌ Item '{item_id}' not found.")

#lista r con el codigo prácticamente con la excepcion de wmin y wmax
def print_results(results):
    if not results:
        print("No items found.")
        return
    print(f"\n{'ID':<16} {'Colour':<10} {'In Stock':<10} {'Weight(g)':<12} {'Arrival':<12} Notes")
    print("-" * 75)
    for r in results:
        stock_str = "Yes" if r["is_in_stock"] else "No"
        print(f"{r['item_id']:<16} {r['colour']:<10} {stock_str:<10} {r['weight_g']:<12} {str(r['arrival_date']):<12} {r['notes'] or ''}")
    print()


#mensaje consola vsCode / només per prova que vagi. Seccio creada per IA degut al seu caracter repetitiu

def interactive_menu():
    print("\n🖨️  Preparando Stock Manager")
    print("cargando, cargando, cargando...")
    while True:
        print("\n1. Add item")
        print("2. Search items")
        print("3. Update item")
        print("4. Delete item")
        print("5. List all items")
        print("0. Exit")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            print("\nAvailable colour codes:", {k: v for k, v in codi_colors.items()})
            colour = input("Colour letter (e.g. R): ").strip().upper()
            number = int(input("Number (0-9999): ").strip())
            date_str = input("Arrival date (DD/MM/YYYY): ").strip()
            arrival_date = datetime.strptime(date_str, "%d/%m/%Y")
            weight = float(input("Weight in grams: ").strip())
            in_stock = input("Is in stock? (y/n): ").strip().lower() == "y"
            notes = input("Notes (optional): ").strip()
            add_item(colour, number, arrival_date, weight, in_stock, notes)

        elif choice == "2":
            print("\nLeave blank to skip a filter.")
            item_id = input("Item ID: ").strip() or None
            colour = input("Colour (name or letter): ").strip() or None
            stock_input = input("In stock? (y/n/blank): ").strip().lower()
            in_stock = True if stock_input == "y" else (False if stock_input == "n" else None)
            min_w = input("Min weight (g): ").strip()
            max_w = input("Max weight (g): ").strip()
            results = search_items(
                item_id=item_id,
                colour=colour,
                in_stock=in_stock,
                min_weight=float(min_w) if min_w else None,
                max_weight=float(max_w) if max_w else None
            )
            print_results(results)

        elif choice == "3":
            item_id = input("Item ID to update: ").strip()
            print("Leave blank to keep current value.")
            stock_input = input("Is in stock? (y/n/blank): ").strip().lower()
            in_stock = True if stock_input == "y" else (False if stock_input == "n" else None)
            weight = input("New weight (g): ").strip()
            notes = input("New notes: ").strip() or None
            update_item(item_id, is_in_stock=in_stock,
                        weight_g=float(weight) if weight else None, notes=notes)

        elif choice == "4":
            item_id = input("Item ID to delete: ").strip()
            confirm = input(f"Delete '{item_id}'? (y/n): ").strip().lower()
            if confirm == "y":
                delete_item(item_id)

        elif choice == "5":
            results = search_items()
            print_results(results)

        elif choice == "0":
            print("HASTA PRONTO!")
            break
        else:
            print("Invalid option.")


# init, proposits experimentals

if __name__ == "__main__":
    setup_database()
    interactive_menu()