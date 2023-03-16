from rdflib import Graph, Namespace, URIRef, Literal

# Créer un graphe RDF vide
g = Graph()

# Définir les namespaces nécessaires
dbo = Namespace("http://dbpedia.org/ontology/")
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
ex = Namespace("http://example.org/")

# Définir la classe City
city = URIRef("http://dbpedia.org/ontology/City")
g.add((city, rdf.type, owl.Class))
g.add((city, rdfs.label, Literal("City")))

# Définir la classe Country
country = URIRef("http://dbpedia.org/ontology/Country")
g.add((country, rdf.type, owl.Class))
g.add((country, rdfs.label, Literal("Country")))

# Définir les propriétés liées aux villes
has_name = URIRef("http://example.org/hasName")
g.add((has_name, rdf.type, owl.DatatypeProperty))
g.add((has_name, rdfs.label, Literal("has name")))
g.add((has_name, rdfs.domain, city))
g.add((has_name, rdfs.range, Literal("string", datatype=rdf.XMLLiteral)))

is_capital_of = URIRef("http://example.org/isCapitalOf")
g.add((is_capital_of, rdf.type, owl.ObjectProperty))
g.add((is_capital_of, rdfs.label, Literal("is capital of")))
g.add((is_capital_of, rdfs.domain, city))
g.add((is_capital_of, rdfs.range, country))

# Définir les propriétés liées aux pays
has_name_country = URIRef("http://example.org/hasNameCountry")
g.add((has_name_country, rdf.type, owl.DatatypeProperty))
g.add((has_name_country, rdfs.label, Literal("has name")))
g.add((has_name_country, rdfs.domain, country))
g.add((has_name_country, rdfs.range, Literal("string", datatype=rdf.XMLLiteral)))

has_capital = URIRef("http://example.org/hasCapital")
g.add((has_capital, rdf.type, owl.ObjectProperty))
g.add((has_capital, rdfs.label, Literal("has capital")))
g.add((has_capital, rdfs.domain, country))
g.add((has_capital, rdfs.range, city))

has_population = URIRef("http://example.org/hasPopulation")
g.add((has_population, rdf.type, owl.DatatypeProperty))
g.add((has_population, rdfs.label, Literal("has population")))
g.add((has_population, rdfs.domain, country))
g.add((has_population, rdfs.range, Literal("int", datatype=rdf.XMLLiteral)))

has_area = URIRef("http://example.org/hasArea")
g.add((has_area, rdf.type, owl.DatatypeProperty))
g.add((has_area, rdfs.label, Literal("has area")))
g.add((has_area, rdfs.domain, country))
g.add((has_area, rdfs.range, Literal("float", datatype=rdf.XMLLiteral)))

# Écrire le graphe RDF dans un fichier
g.serialize(destination='city_ontology.rdf', format='turtle') #'turtle'
