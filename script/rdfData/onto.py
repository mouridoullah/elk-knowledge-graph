import requests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import uuid
from SPARQLWrapper import SPARQLWrapper, JSON
from neo4j import GraphDatabase

# Effectuer une requête pour obtenir les informations de la ville de Paris

def infoGeneric(city_id):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)

    queryGeneric = f"""
                    SELECT ?paysLabel ?abstract ?superficie ?coordinates ?population ?langueLabel ?link
                    WHERE {{
                        wd:{city_id} wdt:P1082 ?population; wdt:P17 ?pays; wdt:P2046 ?superficie; wdt:P625 ?coordinates.
                        OPTIONAL {{ wd:{city_id} wdt:P2936 ?langue.}}
                        OPTIONAL {{ wd:{city_id} wdt:P856 ?link. }}
                        OPTIONAL {{
                            wd:{city_id} schema:description ?abstract.
                            FILTER (lang(?abstract) = "fr")
                        }}
                        OPTIONAL {{ wd:{city_id} wdt:P108 ?density. }}
                        OPTIONAL {{ wd:{city_id} wdt:P2044 ?ageDistribution. }}
                        OPTIONAL {{ wd:{city_id} wdt:P1582 ?birthRate. }}
                        OPTIONAL {{ wd:{city_id} wdt:P2566 ?deathRate. }}
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                    }}
                """
        # Configurer le format de réponse en JSON
    sparql.setReturnFormat(JSON)
        # Envoyer la requête et récupérer les résultats
    sparql.setQuery(queryGeneric)
    results = sparql.query().convert()

    results = sparql.queryAndConvert()
    return results

def infoLocalisee(city_id):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)

    queryGeneric = f"""
                    SELECT DISTINCT ?place ?placeLabel ?location ?dist 
                    WHERE {{
                        wd:{city_id} wdt:P625 ?loc . 
                        SERVICE wikibase:around {{
                            ?place wdt:P625 ?location . 
                            bd:serviceParam wikibase:center ?loc . 
                            bd:serviceParam wikibase:radius "100" . 
                            bd:serviceParam wikibase:distance ?dist.
                        }}
                        FILTER EXISTS {{
                            
                                {{ ?place wdt:P31/wdt:P279* wd:Q1248784 . }}
                                UNION
                                {{ ?place wdt:P31/wdt:P279* wd:Q44782 . }}
                                UNION
                                {{ ?place wdt:P31/wdt:P279* wd:Q46622 . }}
                        }}
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
                    }}
                    ORDER BY ASC(?dist) 
                    LIMIT 5
                    """
        # Configurer le format de réponse en JSON
    sparql.setReturnFormat(JSON)
        # Envoyer la requête et récupérer les résultats
    sparql.setQuery(queryGeneric)
    results = sparql.query().convert()

    results = sparql.queryAndConvert()
    return results

city = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
while city != "":
    response = requests.get(f'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=frwiki&titles={city}&props=info&format=json')

    # Extraire l'ID Wikidata de la ville de Paris
    data = response.json()
    city_id = list(data['entities'].keys())[0]

    # Créer une instance de SPARQLWrapper pour l'endpoint de Wikidata
    results = infoGeneric(city_id)
    for result in results["results"]["bindings"]:

        population = result["population"]["value"]
        abstract = result["abstract"]["value"]
        pays = result["paysLabel"]["value"]
        superficie = result["superficie"]["value"]
        coordinates = result["coordinates"]["value"]

        print("""# {} :
                - Population : {} 
                - Description : {}
                - Pays : {} 
                - Superficie : {} km carré
                - Coordonnées geographique {}"""
                .format(city.upper(), population, abstract, pays, superficie, coordinates))

        try:
            link = result["link"]["value"]
            langue = result["langueLabel"]["value"]
            print("""
                - Site internet : {} 
                - Langue parlé : {}""".format(link, langue))
        except:
            pass
    
    print("\n########### Les ports/aéroports/autoroutes les plus proches :###########")
    results = infoLocalisee(city_id)
    for result in results["results"]["bindings"]:
        place = result["place"]["value"]
        placeLabel = result["placeLabel"]["value"]
        location = result["location"]["value"]
        dist = result["dist"]["value"]
        print("{} à {} km de {}".format(placeLabel, dist, city))

    city = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")





# # Villes les plus proches de Berlin
# #defaultView:Map
# SELECT ?place ?placeLabel ?location ?dist 
# WHERE {
#   # Berlin coordinates
#   wd:Q64 wdt:P625 ?berlinLoc . 
#   SERVICE wikibase:around { 
#       ?place wdt:P625 ?location . 
#       bd:serviceParam wikibase:center ?berlinLoc . 
#       bd:serviceParam wikibase:radius "100" . 
#       bd:serviceParam wikibase:distance ?dist.
#   } 
#   FILTER EXISTS {
#     # Is a city
#     ?place wdt:P31/wdt:P279* wd:Q515 .
#   }
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } 
# } 
# ORDER BY ASC(?dist)
