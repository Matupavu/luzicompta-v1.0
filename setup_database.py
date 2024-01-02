import sqlite3

def create_database():
    """
    Crée les tables nécessaires pour l'application LuziCompta dans la base de données SQLite.

    Les tables créées sont :
    - clients : pour stocker les informations des clients.
    - devis : pour stocker les informations des devis.
    - factures : pour stocker les informations des factures.
    """
    try:
        conn = sqlite3.connect('luzicompta.db')
        c = conn.cursor()

        # Création de la table Clients si elle n'existe pas déjà
        c.execute('''CREATE TABLE IF NOT EXISTS clients (
                     id INTEGER PRIMARY KEY,
                     nom TEXT,
                     adresse TEXT)''')

        # Création de la table Devis si elle n'existe pas déjà
        c.execute('''CREATE TABLE IF NOT EXISTS devis (
                     id INTEGER PRIMARY KEY,
                     client_id INTEGER,
                     date DATE,
                     details TEXT,
                     FOREIGN KEY(client_id) REFERENCES clients(id))''')

        # Création de la table Factures si elle n'existe pas déjà
        c.execute('''CREATE TABLE IF NOT EXISTS factures (
                     id INTEGER PRIMARY KEY,
                     devis_id INTEGER,
                     date_paiement DATE,
                     montant REAL,
                     FOREIGN KEY(devis_id) REFERENCES devis(id))''')

        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Erreur de base de données: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()