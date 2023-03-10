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
    print("########### Les aéroports les plus proches :###########")
    print_results(queryAirports(get_city_id(city)))
    print("########### Les ports les plus proches :###########")
    print_results(queryPorts(get_city_id(city)))
    print("########### Les autoroutes les plus proches :###########")
    print_results(queryHighways(get_city_id(city)))
    print("########### Les villes les plus proches :###########")
    print_results(queryNearestCities(get_city_id(city)))


def afficherInfoGenerales(results):
    for result in results["results"]["bindings"]:
        print("Pays:", result["paysLabel"]["value"])
        if "abstract" in result:
            print("Description:", result["abstract"]["value"])
        print("Superficie:", result["superficie"]["value"])
        print("Coordonnées:", result["coordinates"]["value"])
        print("Population:", result["population"]["value"])
        if "langues" in result:
            print("Langues:", result["langues"]["value"])
        if "link" in result:
            print("Lien:", result["link"]["value"])
        if "density" in result:
            print("Densité de population:", result["density"]["value"])
        if "ageDistribution" in result:
            print("Répartition de l'âge:", result["ageDistribution"]["value"])
        if "birthRate" in result:
            print("Taux de natalité:", result["birthRate"]["value"])
        if "deathRate" in result:
            print("Taux de mortalité:", result["deathRate"]["value"])
        print()

city = input("Entrez un nom de ville (appuyez sur Entrée pour quitter) : ")


while city != "":
    results = queryInfoGeneric(get_city_id(city))
    afficherInfoGenerales(results)
    city = input("Entrez un nom de ville (appuyez sur Entrée pour quitter) : ")



# def display_city_info(results):
#     for result in results["results"]["bindings"]:
#         print("Pays:", result["paysLabel"]["value"])
#         if "abstract" in result:
#             print("Description:", result["abstract"]["value"])
#         print("Superficie:", result["superficie"]["value"])
#         print("Coordonnées:", result["coordinates"]["value"])
#         print("Population:", result["population"]["value"])

#         # Afficher le pays
#         if 'paysLabel' in results:
#             print(f"Pays : {results['paysLabel']['value']}")
#         else:
#             print("Pays : N/A")

#         # Afficher la superficie
#         if 'superficie' in results:
#             print(f"Superficie : {results['superficie']['value']} km²")
#         else:
#             print("Superficie : N/A")

#         # Afficher les coordonnées
#         if 'coordinates' in results:
#             coordinates = results['coordinates']['value'].split("(")[1].split(")")[0].split(" ")
#             lat = coordinates[0]
#             long = coordinates[1]
#             print(f"Latitude : {lat}")
#             print(f"Longitude : {long}")
#         else:
#             print("Coordonnées : N/A")

#         # Afficher la population
#         if 'population' in results:
#             print(f"Population : {results['population']['value']}")
#         else:
#             print("Population : N/A")

#         # Afficher la densité de population
#         if 'density' in results:
#             print(f"Densité de population : {results['density']['value']} hab/km²")
#         else:
#             print("Densité de population : N/A")

#         # Afficher la liste des langues parlées
#         if 'langueLabel' in results:
#             langues = [langue['value'] for langue in results['langueLabel']]
#             langues_str = ', '.join(langues)
#             print(f"Langues parlées : {langues_str}")
#         else:
#             print("Langues parlées : N/A")

#         # Afficher la description
#         if 'abstract' in results:
#             print(f"Description : {results['abstract']['value']}")
#         else:
#             print("Description : N/A")

#         # Afficher le lien Wikipédia
#         if 'link' in results:
#             print(f"Lien Wikipédia : {results['link']['value']}")
#         else:
#             print("Lien Wikipédia : N/A")

#     print("----------")