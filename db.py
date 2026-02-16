# Importation du connecteur MySQL
import mysql.connector
# Importation de la classe Error pour gérer les exceptions
from mysql.connector import Error
# Importation du décorateur contextmanager pour créer des context managers
from contextlib import contextmanager
# Importation de Iterator pour les annotations de type
from typing import Iterator
# Importation de la configuration de la base de données
from config import DB_CONFIG


def get_connection():
    """Connexion à MySQL"""
    try:
        # Créer une connexion à MySQL avec les paramètres de configuration
        conn = mysql.connector.connect(**DB_CONFIG)
        # Vérifier que la connexion est active
        if conn.is_connected():
            # Retourner la connexion
            return conn
    except Error as e:
        # En cas d'erreur, afficher le message et lever l'exception
        print(f"Erreur de connexion à MySQL: {e}")
        raise


@contextmanager
def get_db_connection() -> Iterator[mysql.connector.MySQLConnection]:
    """Context manager pour connexions - fermeture automatique"""
    # Initialiser la variable de connexion à None
    conn = None
    try:
        # Obtenir une connexion à la base de données
        conn = get_connection()
        # Donner la connexion à utiliser dans le bloc with
        yield conn
    except Error as e:
        # En cas d'erreur, annuler les transactions non commitées
        if conn:
            conn.rollback()
        # Relancer l'exception
        raise
    finally:
        # Toujours fermer la connexion à la fin
        if conn and conn.is_connected():
            conn.close()


@contextmanager
def get_db_cursor(dictionary: bool = True) -> Iterator[mysql.connector.cursor.MySQLCursor]:
    """Context manager pour curseurs - commit et fermeture automatiques"""
    # Obtenir une connexion à la base de données
    with get_db_connection() as conn:
        # Créer un curseur (dictionary=True retourne les résultats comme dictionnaires)
        cur = conn.cursor(dictionary=dictionary)
        try:
            # Donner le curseur à utiliser dans le bloc with
            yield cur
            # Sauvegarder les modifications (commit)
            conn.commit()
        except Error:
            # En cas d'erreur, annuler les modifications
            conn.rollback()
            # Relancer l'exception
            raise
        finally:
            # Toujours fermer le curseur à la fin
            cur.close()


def setup_database():
    """Vérifier connexion à la base de données"""
    # Obtenir une connexion à la base de données
    conn = get_connection()
    # Vérifier que la connexion est active
    if conn.is_connected():
        # Afficher un message de succès avec le nom de la base de données
        print(f"Connexion réussie: {DB_CONFIG['database']}")
        # Fermer la connexion
        conn.close()
