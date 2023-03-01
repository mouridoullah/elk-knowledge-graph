# from SPARQLWrapper import SPARQLWrapper, JSON

# # Créer une connexion à l'API SPARQL de DBpedia
# sparql = SPARQLWrapper(
#    "http://dbpedia.org/sparql"
# )
# sparql.setReturnFormat(JSON)

# # Écrire la requête SPARQL pour récupérer les noms des villes en France
# sparql.setQuery("""
#                     SELECT ?cityName WHERE {
#                         ?city rdf:type dbo:City .
#                         ?city dbo:country dbr:France .
#                         ?city foaf:name ?cityName .
#                     }
#                 """)

# try:
#     ret = sparql.queryAndConvert()

#     for r in ret["results"]["bindings"]:
#         print(r["cityName"]["value"])
# except Exception as e:
#     print(e)



from rdflib import Graph

# Create a Graph
g = Graph()

# Parse in an RDF file hosted on the Internet
g.parse("http://www.w3.org/People/Berners-Lee/card")

# Loop through each triple in the graph (subj, pred, obj)
for subj, pred, obj in g:
    # Check if there is at least one triple in the Graph
    if (subj, pred, obj) not in g:
       raise Exception("It better be!")

# Print the number of "triples" in the Graph
print(f"Graph g has {len(g)} statements.")
# Prints: Graph g has 86 statements.

# Print out the entire Graph in the RDF Turtle format
print(g.serialize(format="turtle"))