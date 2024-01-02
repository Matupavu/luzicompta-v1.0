# home.py

import wx
from datetime import datetime
import wx.grid
from generate_devis import create_pdf, create_pdf_safe
import database
import subprocess
import os
import tempfile
import webbrowser

def createBoldFont(size):
    return wx.Font(size, wx.DEFAULT, wx.NORMAL, wx.BOLD)

class LuziCompta(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(LuziCompta, self).__init__(*args, **kwargs)
        self.InitUI()
        self.Maximize(True)  # Maximise la fenêtre
        
    def InitUI(self):
        # Créer un panneau
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # En-tête avec logo et coordonnées
        hbox_header = wx.BoxSizer(wx.HORIZONTAL)
        # Charger et redimensionner le logo
        logo_image = wx.Image('LUZITECH LOGO.png', wx.BITMAP_TYPE_ANY)
        logo_image = logo_image.Scale(300, 150)  # Taille du logo
        logo_bitmap = wx.StaticBitmap(panel, -1, logo_image.ConvertToBitmap())
        hbox_header.Add(logo_bitmap, flag=wx.RIGHT, border=10)

        # Sizer vertical pour les coordonnées
        vbox_coordonnees = wx.BoxSizer(wx.VERTICAL)
        coordonnees = ["LUZITECH", "", "23 Rue le Brecq", "45290 NOGENT SUR VERNISSON", 
                   "tél : 06 50 65 01 00", "Mail : luzitech45@gmail.com"]
        bold_font = createBoldFont(13)
        for ligne in coordonnees:
            coord_text = wx.StaticText(panel, label=ligne)
            coord_text.SetFont(bold_font)
            vbox_coordonnees.Add(coord_text, flag=wx.BOTTOM, border=5)

        # Ajouter le sizer vertical au sizer horizontal
        hbox_header.Add(vbox_coordonnees, flag=wx.LEFT, border=10)
        vbox.Add(hbox_header, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Chargement des clients dans la liste
        self.loadClients()

        # Récupérer la liste des noms de clients pour l'autocomplétion
        client_names = self.getClientNames()

        # Définir une police en gras
        bold_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        # Étiquette pour le champ de saisie du nom du client
        client_name_label = wx.StaticText(panel, label="Nom du Client :")
        client_name_label.SetFont(createBoldFont(12))
        vbox.Add(client_name_label, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Créer un sizer horizontal pour les boutons
        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)

        # Champ de saisie pour le nom du client avec auto-complétion
        self.clientNameTxt = wx.TextCtrl(panel, size=(300, -1))  # Limiter la largeur à 300
        client_name_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.clientNameTxt.SetFont(client_name_font)
        self.clientNameTxt.AutoComplete(client_names)  # Activer l'auto-complétion
        hbox_buttons.Add(self.clientNameTxt, flag=wx.RIGHT, border=10)

        # Bouton pour ajouter un nouveau client
        add_client_btn = wx.Button(panel, label='+', size=(50, 30))
        bold_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        add_client_btn.SetFont(createBoldFont(12))
        add_client_btn.SetToolTip("Créer un nouveau client")
        add_client_btn.Bind(wx.EVT_BUTTON, self.OnAddClient)
         
        # Ajouter le bouton au sizer horizontal
        hbox_buttons.Add(add_client_btn, flag=wx.RIGHT, border=10)

        # Ajouter un espace flexible pour pousser le bouton "Nouveau Devis" vers la droite
        hbox_buttons.AddStretchSpacer()

        # Bouton pour ajouter un nouveau devis
        new_devis_btn = wx.Button(panel, label='Créer un nouveau Devis', size=(210, 40))
        new_devis_btn.SetFont(createBoldFont(12))
        new_devis_btn.SetForegroundColour(wx.Colour(255, 127, 0))  # Couleur orange

        # Ajouter le bouton au sizer horizontal
        hbox_buttons.Add(new_devis_btn)

        # Ajouter le sizer horizontal au sizer vertical principal
        vbox.Add(hbox_buttons, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Définir une police en gras
        bold_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        
        # Étiquettes pour les listes de devis et de factures
        devis_label = wx.StaticText(panel, label='Devis :')
        devis_label.SetFont(createBoldFont(12))
        factures_label = wx.StaticText(panel, label='Factures :')
        factures_label.SetFont(createBoldFont(12))
        
        # Sizer horizontal pour les étiquettes des listes
        hbox_lists_labels = wx.BoxSizer(wx.HORIZONTAL)
        hbox_lists_labels.Add(devis_label, flag=wx.RIGHT, proportion=1)
        hbox_lists_labels.Add(factures_label, flag=wx.ALIGN_LEFT)

        # Ajouter le sizer horizontal au sizer vertical principal
        vbox.Add(hbox_lists_labels, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Liste déroulante pour les années
        from datetime import datetime
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year, current_year + 11)]
        self.year_choice = wx.Choice(panel, size=(70, -1), choices=years)  # Taille plus grande

        # Définir une police plus grande pour les éléments de la liste
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.year_choice.SetFont(font)
        self.year_choice.SetStringSelection(str(current_year))  # Sélectionner l'année en cours par défaut

        # Ajouter la liste déroulante au sizer horizontal
        hbox_lists_labels.Add(self.year_choice, flag=wx.RIGHT|wx.LEFT, border=10)
       
        # Lier le bouton "Nouveau Devis" à la méthode OnAddDevis
        new_devis_btn.Bind(wx.EVT_BUTTON, self.OnAddDevis)     

        # Zone pour afficher les listes de devis et de factures
        hbox_lists = wx.BoxSizer(wx.HORIZONTAL)
        self.quotesList = wx.ListBox(panel)
        hbox_lists.Add(self.quotesList, proportion=1, flag=wx.EXPAND)

        # Ajouter un espace entre les listes
        hbox_lists.AddSpacer(50)
        self.invoicesList = wx.ListBox(panel)
        hbox_lists.Add(self.invoicesList, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox_lists, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        
        panel.SetSizer(vbox)
        self.SetTitle('LuziCompta v1.0')
        self.Centre()

    def OnYearSelected(self, event):
        selected_year = self.year_choice.GetStringSelection()
        self.updateDevisList(selected_year)
        self.updateFacturesList(selected_year)

    def updateDevisList(self, year):
        # Mettre à jour la liste des devis en fonction de l'année sélectionnée
        # Implémentez la logique pour récupérer et afficher les devis pour l'année donnée
        pass

    def updateFacturesList(self, year):
        # Mettre à jour la liste des factures en fonction de l'année sélectionnée
        # Implémentez la logique pour récupérer et afficher les factures pour l'année donnée
        pass

    def getClientInfoByName(self, client_name):
        try:
            conn = database.connect_db()
            c = conn.cursor()
            c.execute('SELECT * FROM clients WHERE nom = ?', (client_name,))
            client_info = c.fetchone()
            conn.close()
            if client_info:
                return {'nom': client_info[1], 'adresse': client_info[2]}
            return None
        except Exception as e:
            wx.MessageBox(f"Erreur lors de la récupération des informations du client : {e}", "Erreur", wx.OK | wx.ICON_ERROR)
            return None

    def getClientNames(self):
        try:
            clients = database.get_all_clients()  # Assurez-vous que cette méthode récupère les données les plus récentes
            client_names = [client[1] for client in clients]  # Supposons que le nom est à l'indice 1
            return client_names
        except Exception as e:
            wx.MessageBox(f"Erreur lors de la récupération des noms de clients : {e}", "Erreur", wx.OK | wx.ICON_ERROR)
            return []

    def OnClientSelected(self, event):
        # Récupérer le nom du client sélectionné
        selected_client_name = self.clientsList.GetString(self.clientsList.GetSelection())
        # Mettre à jour le champ de recherche avec le nom du client
        self.searchBox.SetValue(selected_client_name)

    def OnAddClient (self, event):
        client_name = self.clientNameTxt.GetValue()
        if not self.validate_client_name(client_name):
            wx.MessageBox("Le nom du client est invalide ou manquant.", "Erreur", wx.OK | wx.ICON_ERROR)
            return
        new_client_window = NewClientWindow(self)
        new_client_window.ShowModal()
        new_client_window.Destroy()
        self.loadClients()  # Recharger la liste des clients après la fermeture de la fenêtre

    def validate_client_name(self, name):
        """ Valide le nom du client. """
        if not name:
            return False
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -.'"
        return all(char in allowed_chars for char in name)
    
    def SetClientName(self, name):
        """
        Met à jour le champ de texte avec le nom du client.
        """
        self.clientNameTxt.SetValue(name)
    
    def OnAddDevis(self, event):
        client_name = self.clientNameTxt.GetValue()  # Utilisez la valeur du champ avec l'autocomplétion
        # Récupérez les autres informations du client (comme l'adresse) en fonction du nom
        client_info = self.getClientInfoByName(client_name)
        if client_info:
            devis_window = DevisWindow(self, "Ajouter un Devis", client_info)
            devis_window.ShowModal()
            devis_window.Destroy()

    def getSelectedClient(self):
        selection = self.clientsList.GetSelection()
        if selection != wx.NOT_FOUND:
            client_name = self.clientsList.GetString(selection)
            # Récupérez l'adresse du client depuis la base de données ou votre structure de données
            client_address = "Adresse du client"  # Remplacez par la logique réelle
            return {'nom': client_name, 'adresse': client_address}
        return None
   
    def OnNewClient(self, event):
        # Réinitialiser les champs de saisie ou autres actions
        self.clientNameTxt.SetValue('')
        self.clientAddressTxt.SetValue('')

    def OnSaveClient(self, event):
        name = self.clientNameTxt.GetValue()
        address = self.clientAddressTxt.GetValue()
        database.add_client(name, address)
        self.loadClients()  # Recharger la liste des clients

    def loadClients(self):
        try:
            clients = database.get_all_clients()
            return [client[1] for client in clients]  # Supposons que le nom est à l'indice 1
        except Exception as e:
            wx.MessageBox(f"Erreur lors de la récupération des clients : {e}", "Erreur", wx.OK | wx.ICON_ERROR)
            return []

    def OnSearch(self, event):
        # Fonction à compléter pour la recherche de clients
        pass

    def updateClientList(self):
        client_names = self.getClientNames()
        if hasattr(self, 'clientNameTxt'):
            self.clientNameTxt.AutoComplete(client_names)

class DevisWindow(wx.Dialog):
    def __init__(self, parent, title, client_info):
        super(DevisWindow, self).__init__(parent, title=title, size=(800, 600))
        self.Maximize(True)  # Maximise la fenêtre
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.client_info = client_info  # Stocker les informations du client

        # Générer et afficher le titre du devis
        self.devis_title = self.generate_devis_title()
        self.titleLbl = wx.StaticText(self.panel, label=self.devis_title)
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)  # Police plus grande et en gras
        self.titleLbl.SetFont(title_font)
        self.titleLbl.SetForegroundColour(wx.Colour(255, 140, 0))  # Orange foncé
        self.vbox.Add(self.titleLbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Sizer horizontal pour le nom du client
        hbox_client_name = wx.BoxSizer(wx.HORIZONTAL)

        # Étiquette "Nom du Client"
        self.clientNameLbl = wx.StaticText(self.panel, label="Nom du Client :")
        hbox_client_name.Add(self.clientNameLbl, flag=wx.RIGHT, border=10)

        # Nom du client en plus gros et en gras
        client_name_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.clientNameTxt = wx.StaticText(self.panel, label=client_info['nom'])
        self.clientNameTxt.SetFont(client_name_font)
        hbox_client_name.Add(self.clientNameTxt, flag=wx.EXPAND)

        # Ajouter le sizer horizontal au sizer vertical principal
        self.vbox.Add(hbox_client_name, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Sizer horizontal pour l'adresse du client
        hbox_client_address = wx.BoxSizer(wx.HORIZONTAL)

        # Étiquette "Adresse du Client"
        self.clientAddressLbl = wx.StaticText(self.panel, label="Adresse du Client:")
        hbox_client_address.Add(self.clientAddressLbl, flag=wx.RIGHT, border=10)

        # Adresse du client en plus gros et en gras
        client_address_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.clientAddressTxt = wx.StaticText(self.panel, label=client_info['adresse'])
        self.clientAddressTxt.SetFont(client_address_font)
        hbox_client_address.Add(self.clientAddressTxt, flag=wx.EXPAND)

        # Ajouter le sizer horizontal au sizer vertical principal
        self.vbox.Add(hbox_client_address, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Sizer horizontal pour le demandeur
        hbox_demandeur = wx.BoxSizer(wx.HORIZONTAL)

        # Étiquette "Demandeur"
        self.demandeurLbl = wx.StaticText(self.panel, label="Demandeur :")
        hbox_demandeur.Add(self.demandeurLbl, flag=wx.RIGHT, border=10)

        # Champ de saisie pour le demandeur
        self.demandeurTxt = wx.TextCtrl(self.panel, size=(300, -1))
        self.demandeurTxt.SetMaxLength(50)  # Limiter la longueur du texte à 50 caractères
        hbox_demandeur.Add(self.demandeurTxt, flag=wx.EXPAND)
        demandeurFont = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.demandeurTxt.SetFont(demandeurFont)

        # Ajouter le sizer horizontal au sizer vertical principal
        self.vbox.Add(hbox_demandeur, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Sizer horizontal pour la date du devis
        hbox_date_devis = wx.BoxSizer(wx.HORIZONTAL)

        # Étiquette "Date du Devis"
        self.devisDateLbl = wx.StaticText(self.panel, label="Date du Devis :")
        hbox_date_devis.Add(self.devisDateLbl, flag=wx.RIGHT, border=10)

        # wx.TextCtrl pour la date du devis avec la date actuelle formatée
        formatted_date = datetime.now().strftime("%d/%m/%Y")
        self.devisDateTxt = wx.TextCtrl(self.panel, value=formatted_date, size=(100, -1))
        hbox_date_devis.Add(self.devisDateTxt, flag=wx.EXPAND)

        # Ajouter le sizer horizontal au sizer vertical principal
        self.vbox.Add(hbox_date_devis, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Nature de l'Intervention
        self.natureInterventionLbl = wx.StaticText(self.panel, label="Nature de l'Intervention :")
        self.natureInterventionTxt = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(400, 70))  # Hauteur ajustée pour trois lignes
        self.vbox.Add(self.natureInterventionLbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.vbox.Add(self.natureInterventionTxt, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
       # Créer le Grid pour les articles du devis
        self.devisGrid = wx.grid.Grid(self.panel)
        self.devisGrid.CreateGrid(5, 8)  # 5 lignes, 8 colonnes
        self.setupGrid()

        # Définir les largeurs des colonnes
        self.devisGrid.SetColSize(0, 740)  # Largeur de la première colonne
        self.devisGrid.SetColSize(1, 60)  # Largeur de la deuxième colonne
        self.devisGrid.SetColSize(2, 60)
        self.devisGrid.SetColSize(3, 80)
        self.devisGrid.SetColSize(4, 80)
        self.devisGrid.SetColSize(5, 60)
        self.devisGrid.SetColSize(6, 80)
        self.devisGrid.SetColSize(7, 80)
        # ...

        self.vbox.Add(self.devisGrid, proportion=1, flag=wx.EXPAND|wx.ALL, border=10)

        self.panel.SetSizer(self.vbox)

        # Créer une police en gras de taille 11
        instructionFont = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Ajouter une instruction avec style modifié
        instructionLbl = wx.StaticText(self.panel, label="Cliquez sur les cellules des colonnes 'U' et 'TVA' pour voir plus d'options.")
        instructionLbl.SetFont(createBoldFont(11))
        instructionLbl.SetForegroundColour(wx.Colour(70, 70, 70))  # Gris foncé

        # Aligner le texte à droite
        instructionLblStyle = instructionLbl.GetWindowStyle()
        instructionLbl.SetWindowStyle(instructionLblStyle | wx.ALIGN_RIGHT)

        # Ajouter l'instruction à la boîte de mise en page (sizer)
        self.vbox.Add(instructionLbl, flag=wx.ALL | wx.ALIGN_RIGHT, border=5)

        # Ajouter les boutons
        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)

        # Créer une police en gras et de taille plus grande
        buttonFont = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Bouton "Visualiser le Devis"
        btn_visualiser = wx.Button(self.panel, label='Visualiser le Devis')
        btn_visualiser.SetFont(createBoldFont(12))
        btn_visualiser.SetForegroundColour(wx.Colour(255, 127, 0))  # Orange foncé
        btn_visualiser.Bind(wx.EVT_BUTTON, self.OnVisualiserDevis)
        hbox_buttons.Add(btn_visualiser, flag=wx.RIGHT, border=10)

        # Bouton "Enregistrer le Devis"
        btn_enregistrer = wx.Button(self.panel, label='Enregistrer le Devis')
        btn_enregistrer.SetFont(createBoldFont(12))
        btn_enregistrer.SetForegroundColour(wx.Colour(0, 128, 0))  # Vert foncé
        btn_enregistrer.Bind(wx.EVT_BUTTON, self.OnEnregistrerDevis)
        hbox_buttons.Add(btn_enregistrer, flag=wx.RIGHT, border=10)

        # Bouton "Annuler"
        btn_annuler = wx.Button(self.panel, label='Annuler')
        btn_annuler.SetFont(createBoldFont(12))
        btn_annuler.SetForegroundColour(wx.Colour(255, 0, 0))  # Rouge
        btn_annuler.Bind(wx.EVT_BUTTON, self.OnAnnulerDevis)
        hbox_buttons.Add(btn_annuler)

        # Ajouter les boutons à la boîte de mise en page (sizer)
        self.vbox.Add(hbox_buttons, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

    def generate_devis_title(self):
        year = datetime.now().year  # Utilisez datetime.now() pour obtenir l'année actuelle
        num_seq = self.get_next_devis_number()
        return f"DEVIS n°{year}-{num_seq}"

    def get_next_devis_number(self):
        last_number = database.get_last_devis_number()
        new_number = last_number + 1
        database.update_devis_number(new_number)
        return new_number

    def OnVisualiserDevis(self, event):
        # Convertir la date du format DD/MM/YYYY au format YYYY-MM-DD
        date_str = self.devisDateTxt.GetValue()
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            formatted_date_for_pdf = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            wx.MessageBox("Format de date incorrect. Utilisez le format JJ/MM/AAAA.", "Erreur", wx.OK | wx.ICON_ERROR)
            return

        devis_info = {
            'nom_client': self.clientNameTxt.GetLabel(),
            'adresse_client': self.clientAddressTxt.GetLabel(),
            'date': formatted_date_for_pdf,  # Utiliser la date formatée pour le PDF
            'demandeur': self.demandeurTxt.GetValue(),
            'nature_intervention': self.natureInterventionTxt.GetValue()
        }
        articles = self.get_devis_articles()
        devis_number = self.get_next_devis_number()
        client_name = self.client_info['nom']

        # Générer un fichier PDF temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
            pdf_file_path = tmpfile.name
            create_pdf_safe(devis_info, articles, devis_number, client_name, pdf_file_path)

        # Ouvrir le PDF temporaire pour visualisation
        self.open_pdf(pdf_file_path)

    def open_pdf(self, file_path):
        if os.path.exists(file_path):
            webbrowser.open_new(file_path)
        else:
            wx.MessageBox("Le fichier PDF n'existe pas.", "Erreur", wx.OK | wx.ICON_ERROR)

    def OnEnregistrerDevis(self, event):
        devis_info = self.collect_devis_info()

        # Validation des données
        if not self.validate_devis_info(devis_info):
            wx.MessageBox("Veuillez remplir tous les champs nécessaires.", "Information manquante", wx.OK | wx.ICON_WARNING)
            return

        articles = self.get_devis_articles()
        devis_number = self.get_next_devis_number()
        client_name = self.client_info['nom']

        # Spécifier un chemin de fichier pour enregistrer le devis de manière permanente
        pdf_file_path = f"devis_permanents/devis_{devis_number}_{client_name.replace(' ', '_')}.pdf"

        # Vérifier si le dossier 'devis_permanents' existe, sinon le créer
        if not os.path.exists('devis_permanents'):
            os.makedirs('devis_permanents')

        try:
            create_pdf_safe(devis_info, articles, devis_number, client_name, pdf_file_path)
            wx.MessageBox(f"Le devis {devis_number} a été enregistré avec succès.", "Succès", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Une erreur est survenue lors de l'enregistrement du devis : {e}", "Erreur", wx.OK | wx.ICON_ERROR)
    
    def validate_devis_info(self, devis_info):
        required_fields = ['nom_client', 'adresse_client', 'date', 'demandeur', 'nature_intervention']
        for field in required_fields:
            if not devis_info.get(field):
                return False
        return True

    def collect_devis_info(self):
        # Collecter les informations du devis
        return {
            'nom_client': self.clientNameTxt.GetLabel(),
            'adresse_client': self.clientAddressTxt.GetLabel(),
            'date': self.devisDateTxt.GetValue(),
            'demandeur': self.demandeurTxt.GetValue(),
            'nature_intervention': self.natureInterventionTxt.GetValue()
        }

    def OnAnnulerDevis(self, event):
        self.Close()
    
    def setupGrid(self):
        # Créer une police plus grande pour les cellules
        cellFont = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        # Appliquer la police aux cellules de la grille
        self.devisGrid.SetDefaultCellFont(cellFont)

        # Créer une police plus grande pour les en-têtes de colonnes
        headerFont = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # Appliquer la police aux en-têtes de colonnes
        self.devisGrid.SetLabelFont(headerFont)

        # Configurer les en-têtes de colonne
        headers = ["Description", "U", "Qté", "Prix HT", "Total HT", "TVA", "Total TVA", "Total TTC"]
        for col, header in enumerate(headers):
            self.devisGrid.SetColLabelValue(col, header)

        # Ajouter un gestionnaire d'événements pour les changements de cellule
        self.devisGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnCellChanged)

        # Configurer les éditeurs et les choix pour certaines colonnes
        for row in range(self.devisGrid.GetNumberRows()):
            # Configurer la colonne "U" avec une liste déroulante
            choiceEditorU = wx.grid.GridCellChoiceEditor(["U", "F", "Ens"], False)
            self.devisGrid.SetCellEditor(row, 1, choiceEditorU)
            self.devisGrid.SetCellEditor(row, 2, wx.grid.GridCellNumberEditor())  # Qté
            self.devisGrid.SetCellEditor(row, 3, wx.grid.GridCellFloatEditor())   # Prix HT
            self.devisGrid.SetCellEditor(row, 4, wx.grid.GridCellFloatEditor())   # Total HT
            # Configurer la colonne "TVA" avec une liste déroulante
            choiceEditorTVA = wx.grid.GridCellChoiceEditor(["20%", "10%"], False)
            self.devisGrid.SetCellEditor(row, 5, choiceEditorTVA)  # Colonne "TVA"            
            self.devisGrid.SetCellEditor(row, 6, wx.grid.GridCellFloatEditor())   # Total TVA
            self.devisGrid.SetCellEditor(row, 7, wx.grid.GridCellFloatEditor())   # Total TTC

            # Configurer le rendu des cellules pour afficher deux décimales
            self.devisGrid.SetCellRenderer(row, 3, wx.grid.GridCellFloatRenderer(0, 2))  # Prix HT
            self.devisGrid.SetCellRenderer(row, 4, wx.grid.GridCellFloatRenderer(0, 2))  # Total HT
            self.devisGrid.SetCellRenderer(row, 6, wx.grid.GridCellFloatRenderer(0, 2))  # Total TVA
            self.devisGrid.SetCellRenderer(row, 7, wx.grid.GridCellFloatRenderer(0, 2))  # Total TTC
        
        # Ajouter un gestionnaire d'événements pour le clic sur la cellule
        self.devisGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)

        # Format des cellules pour les montants
        self.devisGrid.SetCellRenderer(row, 3, wx.grid.GridCellFloatRenderer())  # Prix HT
        self.devisGrid.SetCellRenderer(row, 4, wx.grid.GridCellFloatRenderer())  # Total HT
        self.devisGrid.SetCellRenderer(row, 6, wx.grid.GridCellFloatRenderer())  # Total TVA
        self.devisGrid.SetCellRenderer(row, 7, wx.grid.GridCellFloatRenderer())  # Total TTC

        # Configurer les largeurs des colonnes
        for col in range(self.devisGrid.GetNumberCols()):
            self.devisGrid.SetColSize(col, 100)

        # Définir la hauteur des lignes
        row_height = 30  # ou la hauteur que vous souhaitez
        for row in range(self.devisGrid.GetNumberRows()):
            self.devisGrid.SetRowSize(row, row_height)

        # S'assurer que les nouvelles lignes ajoutées auront la même hauteur
        self.devisGrid.SetDefaultRowSize(row_height, resizeExistingRows=False)

        # Désactiver l'ajout automatique de nouvelles lignes
        self.devisGrid.EnableEditing(True)
        self.devisGrid.DisableDragRowSize()

    def OnCellLeftClick(self, event):
        # Ouvrir la liste déroulante lors du clic sur une cellule de la colonne "U"
        if event.GetCol() == 1:
            self.devisGrid.EnableCellEditControl()
        event.Skip()

    def OnGridResize(self, event):
        # Ajuster la largeur des colonnes pour remplir l'espace disponible
        grid_width = self.devisGrid.GetClientSize().width
        col_count = self.devisGrid.GetNumberCols()
        for col in range(col_count):
            self.devisGrid.SetColSize(col, grid_width // col_count)
        self.devisGrid.ForceRefresh()
        event.Skip()

    def get_devis_articles(self):
        articles = []
        for row in range(self.devisGrid.GetNumberRows()):
            description = self.devisGrid.GetCellValue(row, 0)
            unite = self.devisGrid.GetCellValue(row, 1)
            quantite = self.devisGrid.GetCellValue(row, 2)
            prix_unitaire = self.devisGrid.GetCellValue(row, 3)
            total_ht = self.devisGrid.GetCellValue(row, 4)
            tva = self.devisGrid.GetCellValue(row, 5)
            total_tva = self.devisGrid.GetCellValue(row, 6)
            total_ttc = self.devisGrid.GetCellValue(row, 7)

            # Ajouter l'article à la liste s'il contient des informations
            if description or quantite or prix_unitaire:
                articles.append({
                    'description': description,
                    'unite': unite,
                    'quantite': quantite,
                    'prix_unitaire': prix_unitaire,
                    'total_ht': total_ht,
                    'tva': tva,
                    'total_tva': total_tva,
                    'total_ttc': total_ttc
                })
        return articles

    def OnCellChanged(self, event):
        row = event.GetRow()
        col = event.GetCol()

        # Vérifier si la modification a eu lieu dans la colonne "Description"
        if col == 0:  # Index 0 pour la colonne "Description"
            description = self.devisGrid.GetCellValue(row, col)
            if description:
                # Remplir les cellules "U" et "TVA" pour cette ligne
                self.devisGrid.SetCellValue(row, 1, "U")  # Colonne "U"
                self.devisGrid.SetCellValue(row, 5, "20%")  # Colonne "TVA"

        # Effectuer les calculs pour les colonnes spécifiques
        if col in [2, 3, 5]:  # Qté, Prix HT ou TVA changé
            self.calculateLineTotals(row)

        # Vérifier si l'utilisateur remplit la dernière ligne
        if row == self.devisGrid.GetNumberRows() - 1:
            self.devisGrid.AppendRows(1)
            self.configure_new_row(self.devisGrid.GetNumberRows() - 1)

        event.Skip()  # Ne pas oublier de passer l'événement pour le traitement par défaut

    def configure_new_row(self, row):
        # Configurer la colonne "U" avec une liste déroulante
        choiceEditorU = wx.grid.GridCellChoiceEditor(["U", "F", "Ens"], False)
        self.devisGrid.SetCellEditor(row, 1, choiceEditorU)

        # Configurer la colonne "TVA" avec une liste déroulante
        choiceEditorTVA = wx.grid.GridCellChoiceEditor(["20%", "10%"], False)
        self.devisGrid.SetCellEditor(row, 5, choiceEditorTVA)

        # Configurer les éditeurs pour les colonnes de montants
        self.devisGrid.SetCellEditor(row, 3, wx.grid.GridCellFloatEditor())  # Prix HT
        self.devisGrid.SetCellEditor(row, 4, wx.grid.GridCellFloatEditor())  # Total HT
        self.devisGrid.SetCellEditor(row, 6, wx.grid.GridCellFloatEditor())  # Total TVA
        self.devisGrid.SetCellEditor(row, 7, wx.grid.GridCellFloatEditor())  # Total TTC

        # Configurer le rendu des cellules pour afficher deux décimales
        self.devisGrid.SetCellRenderer(row, 3, wx.grid.GridCellFloatRenderer(0, 2))  # Prix HT
        self.devisGrid.SetCellRenderer(row, 4, wx.grid.GridCellFloatRenderer(0, 2))  # Total HT
        self.devisGrid.SetCellRenderer(row, 6, wx.grid.GridCellFloatRenderer(0, 2))  # Total TVA
        self.devisGrid.SetCellRenderer(row, 7, wx.grid.GridCellFloatRenderer(0, 2))  # Total TTC

    def calculateLineTotals(self, row):
        # Récupérer les valeurs de Qté et Prix HT
        try:
            qty = float(self.devisGrid.GetCellValue(row, 2))
            price_ht = float(self.devisGrid.GetCellValue(row, 3))
        except ValueError:
            qty, price_ht = 0, 0

        # Calculer le Total HT
        total_ht = qty * price_ht
        self.devisGrid.SetCellValue(row, 4, str(total_ht))

        # Calculer la TVA et le Total TTC
        tva_choice = self.devisGrid.GetCellValue(row, 5)
        tva_rate = 0.20 if tva_choice == "20%" else 0.10
        total_tva = total_ht * tva_rate
        total_ttc = total_ht + total_tva

        self.devisGrid.SetCellValue(row, 6, str(total_tva))
        self.devisGrid.SetCellValue(row, 7, str(total_ttc))

class NewClientWindow(wx.Dialog):
    def __init__(self, parent):
        super(NewClientWindow, self).__init__(parent, title="Nouveau Client", size=(400, 300))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Champ de saisie pour le nom du client
        name_lbl = wx.StaticText(panel, label="Nom du Client")
        self.name_txt = wx.TextCtrl(panel)
        vbox.Add(name_lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(self.name_txt, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Champ de saisie pour l'adresse du client
        address_lbl = wx.StaticText(panel, label="Adresse du Client")
        self.address_txt = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        vbox.Add(address_lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(self.address_txt, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Bouton pour enregistrer le nouveau client
        save_btn = wx.Button(panel, label='Enregistrer')
        save_btn.Bind(wx.EVT_BUTTON, self.OnSave)
        vbox.Add(save_btn, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

    def OnSave(self, event):
        try:
            client_name = self.name_txt.GetValue()
            client_address = self.address_txt.GetValue()
            database.add_client(client_name, client_address)
            wx.MessageBox(f"Le client '{client_name}' a été enregistré avec succès.", "Client Enregistré", wx.OK | wx.ICON_INFORMATION)
            self.GetParent().updateClientList()
            if isinstance(self.GetParent(), LuziCompta):
                self.GetParent().SetClientName(client_name)
        except Exception as e:
            wx.MessageBox(f"Une erreur s'est produite lors de l'enregistrement : {e}", "Erreur", wx.OK | wx.ICON_ERROR)
        finally:
            # Fermer la fenêtre après l'enregistrement
            self.Destroy()

def main():
    app = wx.App()
    frame = LuziCompta(None)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

