# Import des bibliothèques nécessaires
import pymongo
from transformers import pipeline
from neo4j import GraphDatabase
from transformers import AutoTokenizer, AutoModelForTokenClassification
def main():
    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["dbDocument"]
    collection = db["test"]

    setModel = {'fr':'Jean-Baptiste/camembert-ner', 
                'ang':'Jean-Baptiste/roberta-large-ner-english'}
    # Initialisation du modèle NER HuggingFace francais
    tokenizer = AutoTokenizer.from_pretrained(setModel["fr"])
    model = AutoModelForTokenClassification.from_pretrained(setModel["fr"])
    ner_model = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    # Connexion à Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    # Boucle sur tous les documents de la collection MongoDB
    for document in collection.find():
        segments = segment_text(document['content'], 200)
        for segment in segments:
            # Extraction des NER à partir du contenu du document
            ner_output = ner_model(segment)
            # Boucle sur tous les NER extraits
            with driver.session() as session:
                session.execute_write(create_relationship, ner_output, document)
def segment_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks
def create_relationship(tx, entities, document):
    for entity in entities:
        entity_group = entity['entity_group']
        word = " ".join(entity["word"].replace("\n", " ").replace("  ", " ").split())
        if len(word.strip()) > 4:
            # if entity["entity_group"] not in ['MISC']:
                tx.run("MERGE (a:Document{id: $id, title: $title}) "
                    "MERGE (b:" + entity_group + " {name: $word}) "
                    "MERGE (a)-[r:MENTIONED]->(b)", word=word, id=str(document["_id"]), title=document["title"])    
if __name__ == "__main__":
    main()


# MATCH (n:Document{id: '63db6e54c106aadd8c36eb5c'})-[:HAS_ENTITY]->(m:NamedEntity) return *






############################################################################################################################################################################################################################
# from transformers import CamembertTokenizer, CamembertForTokenClassification, TokenClassificationPipeline, T5Tokenizer, T5ForConditionalGeneration, pipeline, AutoTokenizer, AutoModelForTokenClassification
# from neo4j import GraphDatabase
# import pymongo

# # Connexion à la base de données MongoDB
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["dbDocument"]
# collection = db["test"]

# # Connexion à la base de données Neo4j
# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
# tokenizer = T5Tokenizer.from_pretrained("plguillou/t5-base-fr-sum-cnndm")
# model = T5ForConditionalGeneration.from_pretrained("plguillou/t5-base-fr-sum-cnndm")

# pi = pipeline("summarization", model=model, tokenizer=tokenizer)

# text = """
#             Apollo 11 est une mission du programme spatial américain Apollo au cours de laquelle, 
#             pour la première fois, des hommes se sont posés sur la Lune, le lundi 21 juillet 1969. 
#             L'agence spatiale américaine, la NASA, remplit ainsi l'objectif fixé par le président 
#             John F. Kennedy en 1961 de poser un équipage sur la Lune avant la fin de la décennie 1960. 
#             Il s'agissait de démontrer la supériorité des États-Unis sur l'Union soviétique qui avait 
#             été mise à mal par les succès soviétiques au début de l'ère spatiale dans le contexte de 
#             la guerre froide qui oppose alors ces deux pays. Ce défi est lancé alors que la NASA n'a 
#             pas encore placé en orbite un seul astronaute. Grâce à une mobilisation de moyens humains 
#             et financiers considérables, l'agence spatiale rattrape puis dépasse le programme spatial soviétique.
#        """

# resume = pi(text)
# for resume in resume:
#     resume = resume

# with driver.session() as session:
#     session.run("MERGE (d:Document {id: $id, title: $title, abstract:$abstract})", id=str("_id"), title="title", abstract=resume["summary_text"])

# tokenizer = AutoTokenizer.from_pretrained('Jean-Baptiste/camembert-ner')
# model = AutoModelForTokenClassification.from_pretrained('Jean-Baptiste/camembert-ner')
# ner_model = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
# ner_output = ner_model(str(resume))

# # with driver.session() as session:
# #     for entity in ner_output:
# #         # Créer un nœud pour chaque entité
# #         session.run("MERGE (n:%s {word: '%s'})" % (entity['entity_group'], entity['word']))

# def create_relationship(tx, entities):
#     for entity in entities:
#         entity_group = entity['entity_group']
#         word = entity['word']
#         tx.run("MERGE (a:Document) "
#                "MERGE (b:" + entity_group + " {name: $word}) "
#                "MERGE (a)-[r:MENTIONED]->(b)", word=word)

# with driver.session() as session:
#     session.write_transaction(create_relationship, ner_output)

# def segment_text(text, chunk_size):
#     chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
#     return chunks


# tokenizer = CamembertTokenizer.from_pretrained('qanastek/pos-french-camembert')
# model = CamembertForTokenClassification.from_pretrained('qanastek/pos-french-camembert')
# pos = TokenClassificationPipeline(model=model, tokenizer=tokenizer)

# def make_prediction(sentence):
#     labels = [l['entity'] for l in pos(sentence)]
#     return list(zip(sentence.split(" "), labels))

# res = make_prediction(str(resume))
# print(res)
