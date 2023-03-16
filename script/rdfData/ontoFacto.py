from SPARQLWrapper import SPARQLWrapper, JSON
import requests

def get_city_id(city):
    response = requests.get(f'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=frwiki&titles={city}&props=info&format=json')
    data = response.json()
    city_id = list(data['entities'].keys())[0]
    return city_id

def queryWikidata(query):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # sparql.addParameter("language", language)
    results = sparql.query().convert()
    return results

def queryInfoGeneric(city_id):
    query = f"""
                SELECT ?paysLabel ?abstract ?superficie ?coordinates ?population (GROUP_CONCAT(DISTINCT ?langueLabel; separator=", ") AS ?langues) ?link ?density ?ageDistribution ?birthRate ?deathRate
                WHERE {{
                        wd:{city_id} wdt:P1082 ?population; wdt:P17 ?pays; wdt:P2046 ?superficie; wdt:P625 ?coordinates.
                        OPTIONAL {{ wd:{city_id} wdt:P2936 ?langue. ?langue rdfs:label ?langueLabel. FILTER (lang(?langueLabel) = "fr"). }}
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
                GROUP BY ?paysLabel ?abstract ?superficie ?coordinates ?population ?link ?density ?ageDistribution ?birthRate ?deathRate
            """

    return queryWikidata(query)

def queryAirports(city_id):
    query = f"""
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
                    ?place wdt:P31/wdt:P279* wd:Q1248784 .
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
            }}
            ORDER BY ASC(?dist) 
            LIMIT 5
            """
    return queryWikidata(query)

def queryPorts(city_id):
    query = f"""
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
                    ?place wdt:P31/wdt:P279* wd:Q44782 .
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
            }}
            ORDER BY ASC(?dist) 
            LIMIT 5
            """
    return queryWikidata(query)


def queryNearestCities(city_id):
    query = f"""
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
                    ?place wdt:P31/wdt:P279* wd:Q515 .
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
            }}
            ORDER BY ASC(?dist) 
            LIMIT 5
            """
    return queryWikidata(query)

def queryHighways(city_id):
    query = f"""
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
                    ?place wdt:P31/wdt:P279* wd:Q46622 .
                }}
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
            }}
            ORDER BY ASC(?dist) 
            LIMIT 5
            """
    return queryWikidata(query)

def print_results(results):
    for result in results['results']['bindings']:
        id = result['place']['value'].split('/')[-1]
        name = result['placeLabel']['value']
        distance = result["dist"]["value"]
        print(f"ID Wikidata : {id} - Nom : {name} - Distance : {distance} km")
    print("\n")

def afficherInfoLocalisee(city):
    print("########### Les villes les plus proches :###########")
    print_results(queryNearestCities(get_city_id(city)))
    print("########### Les aéroports les plus proches :###########")
    print_results(queryAirports(get_city_id(city)))
    print("########### Les ports les plus proches :###########")
    print_results(queryPorts(get_city_id(city)))
    print("########### Les autoroutes les plus proches :###########")
    print_results(queryHighways(get_city_id(city)))



def afficherInfoGenerales(results):
    for result in results["results"]["bindings"]:
        print("Pays:", result["paysLabel"]["value"])
        print("Superficie:", result["superficie"]["value"])
        print("Coordonnées:", result["coordinates"]["value"])
        print("Population:", result["population"]["value"])
        if "abstract" in result:
            print("Description:", result["abstract"]["value"])
        if "langues" in result:
            print("Langues:", result["langues"]["value"])
        if "link" in result:
            print("Lien:", result["link"]["value"])
        if "density" in result:
            print("Densité de population:", result["density"]["value"])
        if "ageDistribution" in result:
            print("Altitude au-dessus du niveau de la mer:", result["ageDistribution"]["value"])
        if "birthRate" in result:
            print("Taux de natalité:", result["birthRate"]["value"])
        if "deathRate" in result:
            print("Taux de mortalité:", result["deathRate"]["value"])
        print()

city = input("Entrez un nom de ville (appuyez sur Entrée pour quitter) : ")


while city != "":
    city_id = get_city_id(city)
    if city_id == "-1":
        print(f"L'identifiant wikidata pour {city} n'a pas été trouvé.")
    else:
        print(f"L'identifiant wikidata pour {city} est : {city_id}")
        results = queryInfoGeneric(city_id)
        afficherInfoGenerales(results)
    city = input("Entrez un nom de ville (appuyez sur Entrée pour quitter) : ")

