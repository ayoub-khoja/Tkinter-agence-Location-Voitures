# Importation des modules nécessaires pour la connexion à la base de données
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from typing import Iterator
from config import DB_CONFIG


def get_connection():
    """
    T7awel connexion m3a la base de données MySQL
    Retourne une connexion active à la base de données
    """
    try:
        # Connexion à MySQL avec les paramètres de configuration
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        # En cas d'erreur, afficher le message et lever l'exception
        print(f"Erreur de connexion à MySQL: {e}")
        raise


@contextmanager
def get_db_connection() -> Iterator[mysql.connector.MySQLConnection]:
    """
    Context manager pour les connexions à la base de données
    Y7assel 3la fermeture automatique de la connexion même en cas d'erreur
    """
    conn = None
    try:
        # Obtenir une connexion
        conn = get_connection()
        # Donner la connexion à utiliser
        yield conn
    except Error as e:
        # En cas d'erreur, annuler les transactions non commitées
        if conn:
            conn.rollback()
        raise
    finally:
        # Toujours fermer la connexion à la fin
        if conn and conn.is_connected():
            conn.close()


@contextmanager
def get_db_cursor(dictionary: bool = True) -> Iterator[mysql.connector.cursor.MySQLCursor]:
    """
    Context manager pour les curseurs de base de données
    Y7assel 3la commit automatique des transactions et fermeture du curseur
    dictionary=True: retourne les résultats comme dictionnaires (plus facile à utiliser)
    """
    with get_db_connection() as conn:
        # Créer un curseur (dictionary=True pour avoir les résultats en dict)
        cur = conn.cursor(dictionary=dictionary)
        try:
            # Donner le curseur à utiliser
            yield cur
            # Sauvegarder les modifications (commit)
            conn.commit()
        except Error:
            # En cas d'erreur, annuler les modifications
            conn.rollback()
            raise
        finally:
            # Toujours fermer le curseur
            cur.close()


def init_schema():
    """
    Connexion à la base de données existante - vérification que ça marche
    Ma t3ammelch création de la base de données, juste connexion
    """
    conn = get_connection()
    if conn.is_connected():
        print(f"Connexion réussie à la base de données: {DB_CONFIG['database']}")
        conn.close()


def setup_database():
    """
    Configuration de la base de données
    T7awel connexion à la base existante (ma t3ammelch création wala seeding)
    """
    init_schema()
