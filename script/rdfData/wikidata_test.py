import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import uuid
from SPARQLWrapper import SPARQLWrapper, JSON
from neo4j import GraphDatabase

def connect_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver.session()

def delete_all_nodes():
    # Se connecter à la base de données Neo4j
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "password"
    driver = GraphDatabase.driver(uri, auth=(username, password))

    # Ouvrir une session Neo4j
    with driver.session() as session:
        # Supprimer tous les nœuds
        session.run("MATCH (n) DETACH DELETE n")

    # Fermer le pilote Neo4j
    driver.close()

uri = "bolt://localhost:7687"  # remplacer avec votre URI
user = "neo4j"  # remplacer avec votre nom d'utilisateur
password = "password"  # remplacer avec votre mot de passe
session = connect_neo4j(uri, user, password)

# Créer une instance de SPARQLWrapper pour l'endpoint de Wikidata
endpoint_url = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(endpoint_url)

# Construire la requête SPARQL

query = """
            SELECT ?city ?cityLabel ?countryLabel ?population ?area ?abstract
            WHERE {
                wd:Q458 wdt:P150 ?country.
                ?country wdt:P36 ?city.
                ?city wdt:P1082 ?population.
                ?city wdt:P2046 ?area
                OPTIONAL {
                    ?article schema:about ?city ;
                            schema:inLanguage "en" ;
                            schema:isPartOf <https://en.wikipedia.org/> ;
                            schema:text ?abstract .
                }
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }
        """

# Configurer le format de réponse en JSON
sparql.setReturnFormat(JSON)

# Envoyer la requête et récupérer les résultats
sparql.setQuery(query)
results = sparql.query().convert()

try:
    results = sparql.queryAndConvert()
    for result in results["results"]["bindings"]:
        label = result["cityLabel"]["value"]
        population = result["population"]["value"]
        area = result["area"]["value"]
        pays = result["countryLabel"]["value"]

        id = {
            "ville":str(uuid.uuid4()),
            "pays":str(uuid.uuid4()),
            "population":str(uuid.uuid4()),
            "area":str(uuid.uuid4())
        }
        # Créer un nœud "Ville" avec le nom de la ville en tant qu'attribut
        print(f"Ville : {label}")
        session.run("MERGE (v:Ville {id: $id, nom: $nom})", id=id["ville"], nom=label)
        # Créer un nœud "Pays" avec le nom du pays en tant qu'attribut
        print(f"Pays : {pays}")
        session.run("MERGE (p:Pays {id: $id, nom: $nom})", id=id["pays"], nom=pays)
        # Créer une relation "EST_DANS" entre la ville et le pays
        session.run("MATCH (v:Ville {id: $id_ville}), (p:Pays {id: $id_pays}) MERGE (v)-[:EST_DANS]->(p)", id_ville=id["ville"], id_pays=id["pays"])
        # Créer un nœud "Population" avec le nombre d'habitants en tant qu'attribut
        print(f"Population : {population}")
        population = session.run("MERGE (pop:Population {id: $id, nombre: $nombre})", id=id["population"], nombre=population)
        # Créer une relation "A_POUR_POPULATION" entre la ville et la population
        session.run("MATCH (v:Ville {id: $id_ville}), (pop:Population {id: $id_pop}) MERGE (v)-[:A_POUR_POPULATION]->(pop)",
                    id_ville=id["ville"], id_pop=id["population"])
        # Créer un nœud "Superficie" avec la superficie de la ville en tant qu'attribut
        print(f"Superficie : {area}")
        superficie = session.run("MERGE (sup:Superficie {id: $id, nombre: $nombre})",id=id["area"], nombre=area)
        # Créer une relation "A_POUR_SUPERFICIE" entre la ville et la superficie
        session.run("MATCH (v:Ville {id: $id_ville}), (sup:Superficie {id: $id_area}) MERGE (v)-[:A_POUR_SUPERFICIE]->(sup)",
                    id_ville=id["ville"], id_area=id["area"])
        print("\n")
except Exception as e:
    print(e)

session.close()
# delete_all_nodes()