import requests

# Effectuer une requête pour obtenir les informations de la ville de Paris
city = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
while city != "":
    response = requests.get(f'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=frwiki&titles={city}&props=info&format=json')

    # Extraire l'ID Wikidata de la ville de Paris
    data = response.json()
    city_id = list(data['entities'].keys())[0]

    print(city_id)

    city = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
