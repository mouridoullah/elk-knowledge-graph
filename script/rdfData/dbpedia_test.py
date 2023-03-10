import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

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

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
while term != "":
    sparql.setQuery(f"""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX dbo: <http://dbpedia.org/ontology/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX dbr: <http://dbpedia.org/resource/>

                        SELECT ?label ?country ?abstract ?population ?area
                        WHERE {{
                            dbr:{term} rdfs:label ?label ;
                                        dbo:abstract ?abstract ;
                                        dbo:country ?country ;
                                        dbo:populationTotal ?population ;
                                        dbo:areaTotal ?area .
                        FILTER (lang(?label) = 'fr' && lang(?abstract) = 'fr')
                        }}
                    """)
    try:
        results = sparql.queryAndConvert()
        for result in results["results"]["bindings"]:
            print("Label:", result["label"]["value"])
            print("Abstract:", result["abstract"]["value"])
            # Créer un nœud "Ville" avec le nom de la ville en tant qu'attribut
            ville = session.run("MERGE (v:Ville {nom: $nom, sommaire: $sommaire}) RETURN v", 
                                nom=result["label"]["value"], sommaire=result["abstract"]["value"]).single()[0]
            print("Country:", result["country"]["value"])
            # Créer un nœud "Pays" avec le nom du pays en tant qu'attribut
            pays = session.run("MERGE (p:Pays {nom: $nom}) RETURN p", nom=result["country"]["value"].split("/")[-1]).single()[0]
            # Créer une relation "EST_DANS" entre la ville et le pays
            session.run("MATCH (v:Ville), (p:Pays) WHERE id(v) = $ville_id AND id(p) = $pays_id MERGE (v)-[:EST_DANS]->(p)",
                        ville_id=ville.id, pays_id=pays.id)
            print("Population:", result["population"]["value"])
            # Créer un nœud "Population" avec le nombre d'habitants en tant qu'attribut
            population = session.run("MERGE (pop:Population {nombre: $nombre}) RETURN pop", 
                                    nombre=result["population"]["value"]).single()[0]
            # Créer une relation "A_POUR_POPULATION" entre la ville et la population
            session.run("MATCH (v:Ville), (pop:Population) WHERE id(v) = $ville_id AND id(pop) = $population_id MERGE (v)-[:A_POUR_POPULATION]->(pop)",
                        ville_id=ville.id, population_id=population.id)
            print("Area:", result["area"]["value"])
            # Créer un nœud "Superficie" avec la superficie de la ville en tant qu'attribut
            superficie = session.run("MERGE (sup:Superficie {nombre: $nombre}) RETURN sup", nombre=result["area"]["value"]).single()[0]
            # Créer une relation "A_POUR_SUPERFICIE" entre la ville et la superficie
            session.run("MATCH (v:Ville), (sup:Superficie) WHERE id(v) = $ville_id AND id(sup) = $superficie_id MERGE (v)-[:A_POUR_SUPERFICIE]->(sup)",
                        ville_id=ville.id, superficie_id=superficie.id)
            print("\n")
    except Exception as e:
        print(e)
    term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
session.close()
delete_all_nodes()



# PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX dbpedia-owl:<http://dbpedia.org/ontology/>
# PREFIX dbpprop:<http://dbpedia.org/property/>

# SELECT ?film ?titre ?photo ?date ?wiki ?resume
# WHERE {
#  ?film a <http://dbpedia.org/ontology/Film> ;
#                dbpedia-owl:abstract ?resume ;
#                rdfs:label ?titre;
#                foaf:isPrimaryTopicOf ?wiki;
#                dbpedia-owl:thumbnail ?photo
# OPTIONAL { ?film dbpprop:released ?date }
# FILTER langMatches(lang(?resume), 'fr')
# FILTER langMatches(lang(?titre), 'fr')
# }
# ORDER BY DESC(?date)
# LIMIT 20