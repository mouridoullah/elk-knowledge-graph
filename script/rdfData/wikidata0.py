from SPARQLWrapper import SPARQLWrapper, JSON

# Initialise le point d'accès SPARQL de Wikidata
endpoint_url = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(endpoint_url)

# Définit la ville recherchée
ville = "Dakar"
query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT DISTINCT ?countryLabel ?population ?area
        WHERE {{
            ?city rdfs:label ?label.
            FILTER (LANG(?label) = "fr" && STR(?label) = STR("{ville}"@en)).
            ?city wdt:P17 ?country.
            ?city wdt:P1082 ?population.
            ?city wdt:P2046 ?area.
            SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "en".
                ?country rdfs:label ?countryLabel.
            }}
        }}
"""


# Envoie la requête et récupère le résultat au format JSON
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# Traite les résultats
bindings = results['results']['bindings']
if len(bindings) > 0:
    ville_info = bindings[0]
    pays = ville_info['countryLabel']['value']
    population = ville_info['population']['value']
    superficie = ville_info['area']['value']
    print("Pays :", pays)
    print("Population :", population)
    print("Superficie :", superficie)
else:
    print("Aucune information trouvée pour la ville de", ville)
