import yaml


def get_titres(fichier):
    """
    :param fichier: le chemin d'un fichier yaml contenant les données des musiques
    :return:
    """
    with open('fichier') as f:
        dataMap = yaml.safe_load(f)
    return dataMap


def get_genres(dico_albums):
    """
    :param dico_albums: un dictionnaire contennant toutes les données sur les artist
    :return: un ensemble contenant tous les genres existants ( string )
    """
    return set(genre for genre in (list_genre for list_genre in dico_albums.get("genre", [])))

def