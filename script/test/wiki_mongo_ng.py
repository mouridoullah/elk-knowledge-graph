import warnings
warnings.filterwarnings('ignore')

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import des bibliothèques nécessaires
import pymongo
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import math
import torch
from elasticsearch import Elasticsearch
import uuid
from neo4j import GraphDatabase
import wikipediaapi

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

def extract_relations_from_model_output(text):
    relations = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    text_replaced = text.replace("<s>", "").replace("<pad>", "").replace("</s>", "")
    for token in text_replaced.split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        relations.append({
            'head': subject.strip(),
            'type': relation.strip(),
            'tail': object_.strip()
        })
    return relations


class KB():
    def __init__(self):
        self.relations = []

    def are_relations_equal(self, r1, r2):
        return all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"])

    def exists_relation(self, r1):
        return any(self.are_relations_equal(r1, r2) for r2 in self.relations)

    def merge_relations(self, r1):
        r2 = [r for r in self.relations
              if self.are_relations_equal(r1, r)][0]
        spans_to_add = [span for span in r1["meta"]["spans"]
                        if span not in r2["meta"]["spans"]]
        r2["meta"]["spans"] += spans_to_add

    def add_relation(self, r):
        if not self.exists_relation(r):
            self.relations.append(r)
        else:
            self.merge_relations(r)

    def print(self):
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")

    def get_relations(self):
        return self.relations

    def get_entities(self):
        return self.entities

def from_text_to_kb(text, span_length=128, verbose=False):
    # tokenize whole text
    inputs = tokenizer([text], return_tensors="pt")

    # compute span boundaries
    num_tokens = len(inputs["input_ids"][0])
    if verbose:
        print(f"Input has {num_tokens} tokens")
    num_spans = math.ceil(num_tokens / span_length)
    if verbose:
        print(f"Input has {num_spans} spans")
    overlap = math.ceil((num_spans * span_length - num_tokens) / 
                        max(num_spans - 1, 1))
    spans_boundaries = []
    start = 0
    for i in range(num_spans):
        spans_boundaries.append([start + span_length * i,
                                 start + span_length * (i + 1)])
        start -= overlap
    if verbose:
        print(f"Span boundaries are {spans_boundaries}")

    # transform input with spans
    tensor_ids = [inputs["input_ids"][0][boundary[0]:boundary[1]]
                  for boundary in spans_boundaries]
    tensor_masks = [inputs["attention_mask"][0][boundary[0]:boundary[1]]
                    for boundary in spans_boundaries]
    inputs = {
        "input_ids": torch.stack(tensor_ids),
        "attention_mask": torch.stack(tensor_masks)
    }

    # generate relations
    num_return_sequences = 3
    gen_kwargs = {
        "max_length": 256,
        "length_penalty": 0,
        "num_beams": 3,
        "num_return_sequences": num_return_sequences
    }
    generated_tokens = model.generate(
        **inputs,
        **gen_kwargs,
    )

    # decode relations
    decoded_preds = tokenizer.batch_decode(generated_tokens,
                                           skip_special_tokens=False)

    # create kb
    kb = KB()
    i = 0
    for sentence_pred in decoded_preds:
        current_span_index = i // num_return_sequences
        relations = extract_relations_from_model_output(sentence_pred)
        for relation in relations:
            relation["meta"] = {
                "spans": [spans_boundaries[current_span_index]]
            }
            kb.add_relation(relation)
        i += 1

    return kb


def segment_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def get_wikipedia_data(title):
    # Initialiser la connexion à Wikipédia
    wiki = wikipediaapi.Wikipedia('en')

    # Récupérer la page correspondant au titre
    page = wiki.page(title)

    # Vérifier si la page existe
    if page.exists():
        # Extraire les données de la page
        data = {
            'title': page.title,
            'summary': " ".join(page.summary.rsplit(".", 1)[0].replace("\n", " ").replace("  ", " ").split()),
            'content': " ".join(page.text.rsplit(".", 1)[0].replace("\n", " ").replace("  ", " ").split()),
        }
        return data
    else:
        return None

def store_data_in_mongodb(data):
    # Initialiser la connexion à MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['dbDocument']
    collection = db['test']

    # Insérer les données dans la base de données
    result = collection.insert_one(data)
    print('Page enregistrée dans MongoDB :', result.inserted_id)

def delete_all_documents(collection):
    documents = collection.find()
    for document in documents:
        collection.delete_one(document)

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

def delete_all_documentsES(index_name):
    # Créer une connexion à ElasticSearch
    es = Elasticsearch("http://localhost:9200")

    # Utiliser la méthode delete_by_query pour supprimer tous les documents de l'index spécifié
    es.delete_by_query(index=index_name, body={"query": {"match_all": {}}})

# Créez une instance de GraphDatabase
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

# Connexion à la base de données MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dbDocument"]
collection = db["test"]
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))



term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")
while term != "":
    data = get_wikipedia_data(term)
    if data:
        id = uuid.uuid4()
        store_data_in_mongodb(data)

        segments = segment_text(data['summary'], 2048)

        for segment in segments:
            text = " ".join(segment.replace("\n", " ").replace("  ", " ").split())
            kb = from_text_to_kb(text)

            # kb.print()
            # for r in kb.get_relations():
            #     print(r)


            triplets = kb.get_relations()

            # Exécutez une transaction pour ajouter des nœuds et des relations au graphe
            with driver.session() as session:
                # Parcourez la liste de dictionnaires et créez des nœuds pour chaque "head" et "tail"
                for triplet in triplets:
                    print(triplet)
                    try:
                        session.run("MERGE (head:Node {name: $head}) "
                                    "MERGE (tail:Node {name: $tail}) "
                                    "MERGE (head)-[r:" + triplet['type'].strip().replace(' ', '_') + "]->(tail) "
                                    "WITH head, tail "
                                    "MERGE (a:Document{id: $id, title: $title}) "
                                    "WITH a, head, tail "
                                    "MERGE (a)-[:MENTIONED]->(head) "
                                    "MERGE (a)-[:MENTIONED]->(tail)",
                                    head=triplet['head'], tail=triplet['tail'], id=str(id), title=data["title"])
                    except:
                        continue
            # Fermez la connexion du driver
            driver.close()

    else:
        print('La page', term, "n'existe pas sur Wikipédia")
    
    term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")


# fonctions pour supprimer nœuds et documents
delete_all_documents(collection)
delete_all_nodes()
delete_all_documentsES("mongo_index")