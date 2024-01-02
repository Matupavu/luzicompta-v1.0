# database.py

import sqlite3

def connect_db():
    try:
        conn = sqlite3.connect('luzicompta.db')
        return conn
    except sqlite3.DatabaseError as e:
        print(f"Erreur de connexion à la base de données: {e}")
        # Gérer l'erreur ou la propager selon les besoins de votre application
        raise

def get_last_devis_number():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT last_number FROM devis_numbers ORDER BY id DESC LIMIT 1')
            last_number = c.fetchone()[0]
        return last_number
    except sqlite3.DatabaseError as e:
        print(f"Erreur lors de la récupération du dernier numéro de devis: {e}")
        raise

def update_devis_number(new_number):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('UPDATE devis_numbers SET last_number = ? WHERE id = (SELECT id FROM devis_numbers ORDER BY id DESC LIMIT 1)', (new_number,))
            conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Erreur lors de la mise à jour du numéro de devis: {e}")
        raise

def add_client(nom, adresse):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO clients (nom, adresse) VALUES (?, ?)', (nom, adresse))
            conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Erreur lors de l'ajout d'un client: {e}")
        raise

def get_all_clients():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM clients')
            clients = c.fetchall()
        return clients
    except sqlite3.DatabaseError as e:
        print(f"Erreur lors de la récupération des clients: {e}")
        raise

# Ajoutez ici d'autres fonctions pour gérer les devis et les factures
