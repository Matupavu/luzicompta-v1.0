# generate_devis.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import locale
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Chemins configurables pour le logo et les polices
LOGO_PATH = 'LUZITECH LOGO.png'
FONTS_PATHS = {
    'QanelasBold': 'Qanelas-Bold.ttf',
    'QanelasMedium': 'Qanelas-Medium.ttf',
    'QanelasSemiBold': 'Qanelas-SemiBold.ttf'
}

def add_logo(canvas, logo_path, x, y, width, height):
    """
    Ajoute un logo au PDF.

    :param canvas: Le canvas du PDF.
    :param x: Position X où le logo doit être placé.
    :param y: Position Y où le logo doit être placé.
    :param width: Largeur du logo.
    :param height: Hauteur du logo.
    """
    full_path = os.path.join(os.path.dirname(__file__), logo_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Le fichier du logo '{full_path}' est introuvable.")
    canvas.drawImage(full_path, x, y, width=width, height=height, mask='auto')

def add_company_details(canvas, details, x, y, line_height, font_name, font_size, bold_font_name, bold_font_size):
    """
    Affiche les coordonnées de l'entreprise sur le PDF.

    :param canvas: Le canvas du PDF.
    :param details: Liste des lignes de texte à afficher.
    :param x: Position X de départ pour le texte.
    :param y: Position Y de départ pour le texte.
    :param line_height: Hauteur de ligne pour le texte.
    :param font_name: Nom de la police à utiliser.
    :param font_size: Taille de la police.
    :param bold_font_name: Nom de la police en gras à utiliser pour le premier élément.
    :param bold_font_size: Taille de la police en gras pour le premier élément.
    """
    # "LUZITECH" en gras et plus grand
    canvas.setFont(bold_font_name, bold_font_size)
    canvas.drawString(x, y, details[0])

    # Reste des détails
    canvas.setFont(font_name, font_size)
    for line in details[1:]:
        y -= line_height
        canvas.drawString(x, y, line)

def load_fonts():
    """
    Charge les polices nécessaires pour le PDF.

    Cette fonction recherche les polices dans le répertoire du script et les enregistre pour une utilisation ultérieure dans le PDF.
    """
    try:
        for font_name, font_path in FONTS_PATHS.items():
            full_path = os.path.join(os.path.dirname(__file__), font_path)
            pdfmetrics.registerFont(TTFont(font_name, full_path))
    except FileNotFoundError as e:
        print(f"Erreur de fichier: {e}")
        raise

def add_client_info(canvas, client_info, x, y, font_name, font_size, bold_font_name, bold_font_size):
    """
    Affiche les informations du client sur le PDF et retourne la position Y finale.

    :param canvas: Le canvas du PDF.
    :param client_info: Dictionnaire contenant les informations du client.
    :param x: Position X pour le texte.
    :param y: Position Y pour le texte.
    :param font_name: Nom de la police à utiliser.
    :param font_size: Taille de la police.
    :param bold_font_name: Nom de la police en gras à utiliser pour "CLIENT :".
    :param bold_font_size: Taille de la police en gras pour "CLIENT :".
    :return: Position Y finale après l'affichage des informations.
    """
    canvas.setFont(bold_font_name, bold_font_size)
    canvas.drawString(x, y, "CLIENT :")
    y -= bold_font_size * 1.5

    canvas.setFont(font_name, font_size)
    canvas.drawString(x, y, client_info['nom_client'])
    y -= font_size * 1.5

    for line in client_info['adresse_client'].split('\n'):
        canvas.drawString(x, y, line)
        y -= font_size * 1.2

    return y  # Retourne la position Y finale

def add_devis_title(canvas, title, devis_number, x, y, font_name, font_size):
    """
    Ajoute le titre du devis sur le PDF.

    :param canvas: Le canvas du PDF.
    :param title: Titre à afficher.
    :param devis_number: Numéro du devis.
    :param x: Position X pour le titre.
    :param y: Position Y pour le titre.
    :param font_name: Nom de la police à utiliser.
    :param font_size: Taille de la police.
    """
    canvas.setFont(font_name, font_size)
    canvas.drawString(x, y, f"{title} n°{devis_number}")

def add_demandeur_details(canvas, demandeur, x, y, font_name, font_size):
    """
    Ajoute les détails du demandeur sur le PDF.

    :param canvas: Le canvas du PDF.
    :param demandeur: Nom du demandeur.
    :param x: Position X pour le texte.
    :param y: Position Y pour le texte.
    :param font_name: Nom de la police à utiliser.
    :param font_size: Taille de la police.
    """
    canvas.setFont(font_name, font_size)
    canvas.drawString(x, y, f"Demandeur : {demandeur}")

def add_nature_intervention(canvas, intervention, x, y, label_font_name, label_font_size, desc_font_name, desc_font_size, cadre_color, page_width, espacement):
    cadre_height = 40  # Hauteur du cadre
    text_padding = 10  # Espacement entre le haut du cadre et le texte
    y += cadre_height - text_padding # Poistion y pour le texte
    
    """
    Ajoute la nature de l'intervention sur le PDF.

    :param canvas: Le canvas du PDF.
    :param intervention: Description de l'intervention.
    :param x: Position X pour le cadre.
    :param y: Position Y pour le cadre.
    :param label_font_name: Nom de la police à utiliser pour le libellé.
    :param label_font_size: Taille de la police pour le libellé.
    :param desc_font_name: Nom de la police à utiliser pour la description.
    :param desc_font_size: Taille de la police pour la description.
    :param cadre_color: Couleur du cadre.
    :param page_width: Largeur de la page.
    :param espacement: Espacement entre le cadre et le tableau des articles.
    """
    # Dessiner le cadre
    canvas.setStrokeColor(cadre_color)
    canvas.rect(x, y, page_width - 2*x, cadre_height)  # Cadre en pleine largeur

    # Positionner le libellé "Nature de l'intervention :"
    canvas.setFont(label_font_name, label_font_size)
    canvas.drawString(x + 10, y + cadre_height - label_font_size, "Nature de l'intervention :")

    # Positionner la description de l'intervention en haut du cadre
    canvas.setFont(desc_font_name, desc_font_size)
    canvas.drawString(x + 180, y + cadre_height - desc_font_size, intervention)
    
def add_articles_table(canvas, articles, x, y, col_widths, header_font_name, cell_font_name, font_size):
    """
    Crée et ajoute un tableau des articles sur le PDF.

    :param canvas: Le canvas du PDF.
    :param articles: Liste des articles à inclure dans le tableau.
    :param x: Position X pour le tableau.
    :param y: Position Y pour le tableau.
    :param col_widths: Largeurs des colonnes du tableau.
    :param header_font_name: Nom de la police à utiliser pour les en-têtes.
    :param cell_font_name: Nom de la police à utiliser pour les cellules.
    :param font_size: Taille de la police.
    """
    # Préparation des données avec formatage des montants
    data = [["Description", "U", "Qté", "Prix HT", "Total HT", "TVA", "Total TVA", "Total TTC"]]
    for art in articles:
        # Convertir et formater les valeurs numériques
        try:
            quantite = float(art['quantite']) if art['quantite'] else 0
            prix_unitaire = float(art['prix_unitaire']) if art['prix_unitaire'] else 0
            total_ht = float(art['total_ht']) if art['total_ht'] else 0
            total_tva = float(art['total_tva']) if art['total_tva'] else 0
            total_ttc = float(art['total_ttc']) if art['total_ttc'] else 0
        except ValueError:
            quantite = prix_unitaire = total_ht = total_tva = total_ttc = 0

        data.append([
            art['description'],
            art['unite'],
            "{:.2f}".format(quantite),
            "{:.2f}".format(prix_unitaire),
            "{:.2f}".format(total_ht),
            art['tva'],
            "{:.2f}".format(total_tva),
            "{:.2f}".format(total_ttc)
        ])

    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FF8C00")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), header_font_name),  # En-têtes avec police spécifiée
        ('FONTNAME', (0, 1), (-1, -1), cell_font_name),   # Cellules avec police spécifiée
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), None),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    table.wrapOn(canvas, x, y)
    table.drawOn(canvas, x, y)

def add_totals(canvas, articles, x, y, page_width, semi_bold_font_name, medium_font_name, font_size):
    """
    Crée et ajoute un tableau des totaux sur le PDF.

    :param canvas: Le canvas du PDF.
    :param articles: Liste des articles pour le calcul des totaux.
    :param x: Position X pour le tableau.
    :param y: Position Y pour le tableau.
    :param page_width: Largeur de la page.
    :param semi_bold_font_name: Nom de la police en semi gras à utiliser pour les libellés.
    :param medium_font_name: Nom de la police medium à utiliser pour les valeurs.
    :param font_size: Taille de la police.
    """
    total_ht = sum(float(article['total_ht']) for article in articles)
    total_tva = sum(float(article['total_tva']) for article in articles)
    total_ttc = sum(float(article['total_ttc']) for article in articles)

    data = [
        ["TOTAL HT", f"{total_ht:.2f} €"],
        ["TOTAL TVA", f"{total_tva:.2f} €"],
        ["TOTAL TTC", f"{total_ttc:.2f} €"]
    ]

    col_widths = [70, 70]  # Largeurs des colonnes
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), semi_bold_font_name),  # Libellés en semi gras
        ('FONTNAME', (1, 0), (1, -1), medium_font_name),     # Valeurs en medium
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Positionner le tableau à droite
    table.wrapOn(canvas, page_width - sum(col_widths) - x, y)
    table.drawOn(canvas, page_width - sum(col_widths) - x, y)

def add_additional_info(canvas, infos, y, font_name, font_size, line_spacing, page_width):
    """
    Ajoute des informations supplémentaires sur le PDF.

    :param canvas: Le canvas du PDF.
    :param infos: Liste des lignes d'informations à ajouter.
    :param y: Position Y de départ pour le texte.
    :param font_name: Nom de la police à utiliser.
    :param font_size: Taille de la police.
    :param line_spacing: Espacement entre les lignes.
    :param page_width: Largeur de la page pour le centrage.
    """
    canvas.setFont(font_name, font_size)
    for i, info in enumerate(infos):
        text_width = canvas.stringWidth(info, font_name, font_size)
        x = (page_width - text_width) / 2
        canvas.drawString(x, y - (line_spacing * i), info)

def add_signature_and_stamp_frames(canvas, x1, y1, x2, y2, cadre_height, cadre_color, font_name, font_size):
    """
    Dessine des cadres pour la signature et le cachet sur le PDF.

    :param canvas: Le canvas du PDF.
    :param x1: Position X pour le premier cadre.
    :param y1: Position Y pour le premier cadre.
    :param x2: Position X pour le second cadre.
    :param y2: Position Y pour le second cadre.
    :param cadre_height: Hauteur des cadres.
    :param cadre_color: Couleur des cadres.
    :param font_name: Nom de la police à utiliser pour le texte.
    :param font_size: Taille de la police pour le texte.
    """
    canvas.setStrokeColor(cadre_color)
    canvas.rect(x1, y1, 250, cadre_height)
    canvas.rect(x2, y2, 250, cadre_height)

    # Position y pour le texte en haut du cadre
    position_y_texte = y1 + cadre_height - 10  # Ajustez selon la hauteur du texte

    # Ajouter le texte
    canvas.setFont(font_name, font_size)
    canvas.drawString(x1 + 10, position_y_texte, "Nom client :")
    canvas.drawString(x1 + 10, position_y_texte - 15, "Signature :")  # Ajustez l'espacement si nécessaire
    canvas.drawString(x2 + 10, position_y_texte, "Cachet de l'entreprise :")

def create_pdf(devis_info, articles, devis_number, client_name, pdf_file_path):
    """
    Crée un PDF pour un devis spécifique.

    Args:
    - devis_info: Dictionnaire contenant les informations du devis.
    - articles: Liste des articles du devis.
    - devis_number: Numéro du devis.
    - client_name: Nom du client.
    - pdf_file_path: Chemin du fichier PDF à créer.

    Cette fonction génère un PDF avec toutes les informations du devis, y compris les détails du client, les articles, et les totaux.
    """
    try:
        # Définir le chemin du fichier PDF
        c = canvas.Canvas(pdf_file_path, pagesize=letter)

        # Définir la locale en français
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            print("Locale française non disponible. La date sera affichée dans le format par défaut.")

        # Charger les polices nécessaires pour le PDF
        load_fonts()

        # Récupérer la largeur et la hauteur de la page
        width, height = letter

        # Ajouter le logo
        add_logo(c, 'LUZITECH LOGO.png', 40, height - 120, width=3*inch, height=1.5*inch)

        # Coordonnées de l'entreprise
        company_details = ["LUZITECH", "23 Rue le Brecq", "45290 NOGENT SUR VERNISSON", "06 50 65 01 00", "luzitech45@gmail.com"]
        add_company_details(c, company_details, 40, height - 140, 15, "QanelasMedium", 12, "QanelasBold", 14)

        # Ajout du titre du devis
        add_devis_title(c, "Devis", devis_number, 400, height - 60, "QanelasBold", 25)

        # Affichage des informations du client et récupération de la position Y finale
        y_fin_adresse_client = add_client_info(c, devis_info, 400, height - 140, "QanelasMedium", 12, "QanelasBold", 14)

        # Espacement après l'adresse du client
        espacement_apres_adresse = 20  # valeur en points

        # Taille de la police utilisée pour la date
        taille_police_date = 12  # estimation basée sur les polices similaires utilisées

        # Espacement souhaité entre la date et le cadre de la nature de l'intervention
        espacement_souhaite = 20  # valeur en points
        
        # Définir l'espacement entre les éléments du PDF
        espacement = 10  # ajustez cette valeur selon vos besoins

        # Affichage de la date
        date_str = devis_info.get('date', None)
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
            except ValueError:
                formatted_date = f'Format de date incorrect: {date_str}'
        else:
            formatted_date = 'Date non spécifiée'
        
        # Affichage du demandeur
        espacement_apres_adresse = 15
        y_position_demandeur = y_fin_adresse_client - espacement_apres_adresse
        add_demandeur_details(c, devis_info['demandeur'], 400, y_position_demandeur, "QanelasMedium", 12)
        
        # Espacement entre le demandeur et la date
        espacement_entre_lignes = 14
        c.drawString(400, y_position_demandeur - espacement_entre_lignes, f"Date : {formatted_date}")

        # Calcul de la position Y pour la nature de l'intervention
        y_nature_intervention = y_fin_adresse_client - espacement_apres_adresse - taille_police_date - espacement_souhaite
        
        # Ajout de la nature de l'intervention
        add_nature_intervention(c, devis_info['nature_intervention'], 40, y_nature_intervention, "QanelasSemiBold", 12, "QanelasMedium", 12, colors.HexColor("#FF8C00"), width, espacement)

        # Hauteur du cadre de la nature de l'intervention
        hauteur_cadre_nature_intervention = 80  # Gardez ou ajustez cette valeur en fonction de vos besoins

        # Position Y pour le tableau des articles
        y_articles_table = y_nature_intervention - espacement - hauteur_cadre_nature_intervention

        # Tableau des articles
        col_widths = [227, 30, 30, 55, 55, 30, 50, 55]
        add_articles_table(c, articles, 40, height - y_articles_table, col_widths, 'QanelasSemiBold', 'QanelasMedium', 10)

        # Tableau des totaux
        add_totals(c, articles, 40, height - y_articles_table - 100, width, 'QanelasSemiBold', 'QanelasMedium', 10)

        # Informations supplémentaires
        additional_infos = ["Délai d'intervention : A convenir suivant planning", "Durée de validité du devis : 1 mois. Conditions de paiement : A réception de facture.", "Conditions de règlement : Virement bancaire ou chèque à l'ordre de LUZITECH."]
        add_additional_info(c, additional_infos, 120, "QanelasSemiBold", 10, 10, width)

        # Cadres pour signature et cachet
        add_signature_and_stamp_frames(c, 50, 30, 320, 30, 60, colors.HexColor("#FF8C00"), "QanelasSemiBold", 10)

        # Numéros de page
        num_pages = c.getPageNumber()
        for i in range(1, num_pages + 1):
            c.drawString((width - 50) / 2, 20, f"Page {i} / {num_pages}")
            if i < num_pages:
                c.showPage()

        c.save()

    except Exception as e:
        print(f"Une erreur est survenue lors de la création du PDF : {e}")
        raise

    return pdf_file_path 

def create_pdf_safe(devis_info, articles, devis_number, client_name, pdf_file_path):
    try:
        # Vérifier si le répertoire existe, sinon le créer
        directory = os.path.dirname(pdf_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Appel à la fonction create_pdf
        create_pdf(devis_info, articles, devis_number, client_name, pdf_file_path)
        print(f"PDF créé avec succès : {pdf_file_path}")
    except OSError as e:
        print(f"Erreur du système de fichiers : {e}")
    except Exception as e:
        print(f"Une autre erreur est survenue : {e}")

# Exemple d'utilisation
if __name__ == '__main__':
    devis_info = {
        'nom_client': 'Client XYZ',
        'adresse_client': '123 Rue Exemple',
        'adresse_suit_client': 'ligne 2',
        'ville_client': 'ville',
        'date': '2023-01-01',
        'demandeur': 'Nom Demandeur',
        'nature_intervention': 'Description de l\'intervention'
    }

    articles = [
        {'description': 'Article 1', 'unite': 'U', 'quantite': 2, 'prix_unitaire': 100.00, 'total_ht': 200.00, 'tva': '20%', 'total_tva': 40.00, 'total_ttc': 240.00},
        {'description': 'Article 2', 'unite': 'F', 'quantite': 1, 'prix_unitaire': 50.00, 'total_ht': 50.00, 'tva': '20%', 'total_tva': 10.00, 'total_ttc': 60.00}
        # Ajoutez d'autres articles ici
    ]

    devis_number = 101
    client_name = 'Client XYZ'

    # Spécifier un chemin de fichier pour le test
    test_pdf_file_path = "C:/Users/peggy/Documents/LuziCompta v1.0/test devis/test_devis.pdf"

    # Appel sécurisé à create_pdf
    create_pdf_safe(devis_info, articles, devis_number, client_name, test_pdf_file_path)


