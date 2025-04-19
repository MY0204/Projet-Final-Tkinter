import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import uuid
from decimal import Decimal

class MobileMoneyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mobile Money")
        self.root.geometry("400x650")
        self.root.configure(bg="#f5f5f5")
        self.root.resizable(False, False)
        
        # Initialiser la base de données
        self.init_db()
        
        # Utilisateur actuel (normalement, il y aurait un système d'authentification)
        self.current_user = {"id": 1, "nom": "Utilisateur Test", "telephone": "0123456789", "solde": 1000.00}
        
        # État d'affichage du solde (True = visible, False = masqué)
        self.show_balance = True
        
        # Création de l'interface
        self.create_ui()
    
    def init_db(self):
        """Initialise la base de données SQLite"""
        self.conn = sqlite3.connect(':memory:')  # Base de données en mémoire pour la démonstration
        self.cursor = self.conn.cursor()
        
        # Créer la table des utilisateurs
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            telephone TEXT NOT NULL UNIQUE,
            solde DECIMAL(10, 2) DEFAULT 0.00
        )
        ''')
        
        # Créer la table des transactions
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            utilisateur_id INTEGER,
            montant DECIMAL(10, 2) NOT NULL,
            date_transaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type TEXT NOT NULL,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id)
        )
        ''')
        
        # Insérer un utilisateur de test
        self.cursor.execute("INSERT INTO utilisateurs (id, nom, telephone, solde) VALUES (1, 'Utilisateur Test', '0123456789', 1000.00)")
        
        # Insérer quelques transactions de test
        transactions = [
            (str(uuid.uuid4()), 1, 500.00, datetime.datetime.now(), "DÉPÔT"),
            (str(uuid.uuid4()), 1, 200.00, datetime.datetime.now(), "RETRAIT")
        ]
        
        self.cursor.executemany(
            "INSERT INTO transactions (id, utilisateur_id, montant, date_transaction, type) VALUES (?, ?, ?, ?, ?)",
            transactions
        )
        
        self.conn.commit()
    
    def create_ui(self):
        """Crée l'interface utilisateur principale"""
        # En-tête
        header_frame = tk.Frame(self.root, bg="#3498db", height=80)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text="Mobile Money", font=("Arial", 22, "bold"), bg="#3498db", fg="white")
        title_label.pack(pady=20)
        
        # Section du solde
        balance_container = tk.Frame(self.root, bg="#f5f5f5", pady=10)
        balance_container.pack(fill=tk.X)
        
        self.balance_frame = tk.Frame(balance_container, bg="white", bd=1, relief=tk.RAISED)
        self.balance_frame.pack(fill=tk.X, padx=20)
        
        balance_header = tk.Frame(self.balance_frame, bg="#f0f0f0")
        balance_header.pack(fill=tk.X)
        
        balance_title = tk.Label(balance_header, text="Solde actuel", font=("Arial", 14), bg="#f0f0f0", padx=10, pady=5)
        balance_title.pack(side=tk.LEFT)
        
        # Bouton pour basculer l'affichage du solde
        self.toggle_icon = tk.StringVar(value="👁️")
        toggle_button = tk.Button(balance_header, textvariable=self.toggle_icon, bg="#f0f0f0", bd=0,
                                font=("Arial", 12), command=self.toggle_balance_display)
        toggle_button.pack(side=tk.RIGHT, padx=10)
        
        # Solde
        self.balance_value_frame = tk.Frame(self.balance_frame, bg="white", height=50)
        self.balance_value_frame.pack(fill=tk.X)
        
        self.balance_label = tk.Label(self.balance_value_frame, text=f"{self.current_user['solde']:.2f} €", 
                                   font=("Arial", 22, "bold"), bg="white", fg="#2c3e50", pady=10)
        self.balance_label.pack()
        
        self.hidden_balance_label = tk.Label(self.balance_value_frame, text="••••••", 
                                         font=("Arial", 22, "bold"), bg="white", fg="#2c3e50", pady=10)
        
        # Afficher le solde par défaut
        self.update_balance_display()
        
        # Section transaction
        transaction_frame = tk.Frame(self.root, bg="#f5f5f5", pady=10)
        transaction_frame.pack(fill=tk.X, padx=20)
        
        transaction_label = tk.Label(transaction_frame, text="Nouvelle transaction", 
                                  font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#2c3e50")
        transaction_label.pack(anchor=tk.W, pady=(10, 15))
        
        # Menu déroulant
        type_frame = tk.Frame(transaction_frame, bg="white", bd=1, relief=tk.RAISED)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = tk.Label(type_frame, text="Type d'opération:", font=("Arial", 12), bg="white", padx=10, pady=5)
        type_label.pack(anchor=tk.W)
        
        self.transaction_type = tk.StringVar()
        type_options = ["Sélectionnez une option", "Dépôt", "Retrait"]
        
        style = ttk.Style()
        style.configure('TCombobox', font=('Arial', 12), padding=5)
        
        self.type_dropdown = ttk.Combobox(type_frame, textvariable=self.transaction_type, 
                                       values=type_options, font=("Arial", 12), state="readonly")
        self.type_dropdown.current(0)
        self.type_dropdown.pack(fill=tk.X, padx=10, pady=10)
        self.type_dropdown.bind("<<ComboboxSelected>>", self.on_transaction_type_selected)
        
        # Section montant (initialement masquée)
        self.amount_frame = tk.Frame(transaction_frame, bg="white", bd=1, relief=tk.RAISED)
        
        amount_label = tk.Label(self.amount_frame, text="Montant (€):", font=("Arial", 12), bg="white", padx=10, pady=5)
        amount_label.pack(anchor=tk.W)
        
        self.amount_var = tk.StringVar()
        amount_entry = tk.Entry(self.amount_frame, textvariable=self.amount_var, 
                             font=("Arial", 14), bd=1, relief=tk.SOLID)
        amount_entry.pack(fill=tk.X, padx=10, pady=5)
        
        self.confirm_button = tk.Button(self.amount_frame, text="Confirmer l'opération", 
                                     font=("Arial", 12, "bold"), bg="#3498db", fg="white",
                                     padx=10, pady=8, command=self.process_transaction)
        self.confirm_button.pack(fill=tk.X, padx=10, pady=10)
        
        # Section historique
        history_frame = tk.Frame(self.root, bg="#f5f5f5", pady=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        history_label = tk.Label(history_frame, text="Historique des transactions", 
                              font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#2c3e50")
        history_label.pack(anchor=tk.W, pady=(10, 15))
        
        # Conteneur pour l'historique
        self.history_container = tk.Frame(history_frame, bg="white", bd=1, relief=tk.RAISED)
        self.history_container.pack(fill=tk.BOTH, expand=True)
        
        # Charger l'historique
        self.update_transaction_history()
    
    def toggle_balance_display(self):
        """Bascule l'affichage du solde entre visible et masqué"""
        self.show_balance = not self.show_balance
        self.update_balance_display()
        
        # Mettre à jour l'icône du bouton
        if self.show_balance:
            self.toggle_icon.set("👁️")
        else:
            self.toggle_icon.set("👁️‍🗨️")
    
    def update_balance_display(self):
        """Met à jour l'affichage du solde en fonction de l'état"""
        if self.show_balance:
            self.hidden_balance_label.pack_forget()
            self.balance_label.pack()
        else:
            self.balance_label.pack_forget()
            self.hidden_balance_label.pack()
    
    def on_transaction_type_selected(self, event):
        """Gère la sélection du type de transaction"""
        selected_option = self.transaction_type.get()
        
        if selected_option != "Sélectionnez une option":
            self.amount_frame.pack(fill=tk.X, pady=5)
            
            # Personnaliser le bouton en fonction du type
            if selected_option == "Dépôt":
                self.confirm_button.config(text="Confirmer le dépôt", bg="#27ae60")
            else:  # Retrait
                self.confirm_button.config(text="Confirmer le retrait", bg="#e74c3c")
        else:
            self.amount_frame.pack_forget()
    
    def process_transaction(self):
        """Traite la transaction (dépôt ou retrait)"""
        transaction_type = self.transaction_type.get()
        
        if transaction_type == "Sélectionnez une option":
            messagebox.showerror("Erreur", "Veuillez sélectionner un type d'opération")
            return
        
        # Validation du montant
        try:
            amount = Decimal(self.amount_var.get().strip().replace(',', '.'))
            if amount <= 0:
                messagebox.showerror("Erreur", "Le montant doit être supérieur à 0")
                return
        except:
            messagebox.showerror("Erreur", "Montant invalide")
            return
        
        # Vérifier le solde pour un retrait
        if transaction_type == "Retrait" and amount > self.current_user["solde"]:
            messagebox.showerror("Erreur", "Solde insuffisant")
            return
        
        # Confirmation
        confirmation_message = f"Confirmer le {transaction_type.lower()} de {amount:.2f} € ?"
        confirm = messagebox.askyesno("Confirmation", confirmation_message)
        
        if not confirm:
            return
        
        # Traitement de la transaction
        try:
            # Mettre à jour le solde
            if transaction_type == "Dépôt":
                new_balance = self.current_user["solde"] + amount
                self.cursor.execute(
                    "UPDATE utilisateurs SET solde = solde + ? WHERE id = ?", 
                    (amount, self.current_user["id"])
                )
            else:  # Retrait
                new_balance = self.current_user["solde"] - amount
                self.cursor.execute(
                    "UPDATE utilisateurs SET solde = solde - ? WHERE id = ?", 
                    (amount, self.current_user["id"])
                )
            
            # Enregistrer la transaction
            transaction_id = str(uuid.uuid4())
            self.cursor.execute(
                "INSERT INTO transactions (id, utilisateur_id, montant, date_transaction, type) VALUES (?, ?, ?, ?, ?)",
                (transaction_id, self.current_user["id"], amount, datetime.datetime.now(), transaction_type.upper())
            )
            
            self.conn.commit()
            
            # Mettre à jour l'interface
            self.current_user["solde"] = new_balance
            self.balance_label.config(text=f"{new_balance:.2f} €")
            
            # Réinitialiser les champs
            self.type_dropdown.current(0)
            self.amount_var.set("")
            self.amount_frame.pack_forget()
            
            # Mettre à jour l'historique
            self.update_transaction_history()
            
            # Message de succès
            messagebox.showinfo("Succès", f"{transaction_type} de {amount:.2f} € effectué avec succès")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Erreur", f"Erreur lors de la transaction: {str(e)}")
    
    def update_transaction_history(self):
        """Met à jour l'affichage de l'historique des transactions"""
        # Nettoyer l'historique actuel
        for widget in self.history_container.winfo_children():
            widget.destroy()
        
        # Récupérer les transactions récentes
        self.cursor.execute("""
        SELECT montant, date_transaction, type 
        FROM transactions 
        WHERE utilisateur_id = ? 
        ORDER BY date_transaction DESC
        LIMIT 10
        """, (self.current_user["id"],))
        
        transactions = self.cursor.fetchall()
        
        if not transactions:
            no_data = tk.Label(self.history_container, text="Aucune transaction", 
                             font=("Arial", 12), bg="white", fg="#7f8c8d", pady=20)
            no_data.pack()
            return
        
        # En-tête du tableau
        header_frame = tk.Frame(self.history_container, bg="#f0f0f0")
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="Type", font=("Arial", 10, "bold"), bg="#f0f0f0", width=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(header_frame, text="Montant", font=("Arial", 10, "bold"), bg="#f0f0f0", width=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(header_frame, text="Date", font=("Arial", 10, "bold"), bg="#f0f0f0", width=20).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Afficher chaque transaction
        for t in transactions:
            montant, date, t_type = t
            
            # Formater la date
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            date_str = date_obj.strftime("%d/%m/%Y %H:%M")
            
            # Couleur selon le type
            bg_color = "#e8f8f5" if t_type == "DÉPÔT" else "#fadbd8"
            
            # Créer la ligne pour cette transaction
            row_frame = tk.Frame(self.history_container, bg=bg_color)
            row_frame.pack(fill=tk.X)
            
            # Icône selon le type
            icon = "➕" if t_type == "DÉPÔT" else "➖"
            type_text = f"{icon} {t_type}"
            
            tk.Label(row_frame, text=type_text, font=("Arial", 10), bg=bg_color, width=10).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Label(row_frame, text=f"{montant:.2f} €", font=("Arial", 10), bg=bg_color, width=10).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Label(row_frame, text=date_str, font=("Arial", 10), bg=bg_color, width=20).pack(side=tk.LEFT, padx=5, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = MobileMoneyApp(root)
    root.mainloop()