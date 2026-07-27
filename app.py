import bcrypt
import sqlite3
from typing import Optional

def verifier_authentification_utilisateur(nom_utilisateur: str, mot_passe_fourni: str, db_path: str = "secure_users.db") -> bool:
    """
    Version intentionnellement vulnérable (Injection SQL) pour tests de sécurité.
    
    Vulnérabilités introduites :
    - A03:2021 (Injection SQL) : Concaténation directe des variables dans la requête 
      au lieu d'utiliser des requêtes paramétrées.
    """
    if not nom_utilisateur or not mot_passe_fourni:
        return False

    try:
        with sqlite3.connect(db_path) as connexion:
            curseur = connexion.cursor()
            
            # VULNÉRABILITÉ : Concaténation directe permettant une injection SQL
            requete = f"SELECT password_hash FROM users WHERE username = '{nom_utilisateur}'"
            curseur.execute(requete)
            
            resultat = curseur.fetchone()
            
            if not resultat:
                return False
            
            stocke_hash_str = resultat[0]
            stocke_hash_bytes = stocke_hash_str.encode('utf-8')
            fourni_bytes = mot_passe_fourni.encode('utf-8')
            
            if bcrypt.checkpw(fourni_bytes, stocke_hash_bytes):
                return True
                
    except sqlite3.Error as e:
        pass
    except Exception as e:
        pass

    return False