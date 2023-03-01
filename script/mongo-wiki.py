import wikipediaapi
import pymongo

def get_wikipedia_data(title):
    # Initialiser la connexion à Wikipédia
    wiki = wikipediaapi.Wikipedia('en')

    # Récupérer la page correspondant au titre
    page = wiki.page(title)

    # Vérifier si la page existe
    if page.exists():
        # Extraire les données de la page
        data = {
            'title': page.title,
            'summary': " ".join(page.summary.rsplit(".", 1)[0].replace("\n", " ").replace("  ", " ").split()),
            'content': " ".join(page.text.rsplit(".", 1)[0].replace("\n", " ").replace("  ", " ").split()),
        }
        return data
    else:
        return None

def store_data_in_mongodb(data):
    # Initialiser la connexion à MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['dbDocument']
    collection = db['test']

    # Insérer les données dans la base de données
    result = collection.insert_one(data)
    print('Page enregistrée dans MongoDB :', result.inserted_id)

term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")

while term != "":
    data = get_wikipedia_data(term)
    if data:
        store_data_in_mongodb(data)
    else:
        print('La page', term, "n'existe pas sur Wikipédia")
    
    term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
