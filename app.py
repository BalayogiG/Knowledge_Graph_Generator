# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 09:46:38 2020

@author: Dell
"""

# Packages
from spacy.lang.en import English
import streamlit as st
import pandas as pd
import wikipediaapi
import spacy
import networkx as nx
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Functions

def getSentences(text):
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    document = nlp(text)
    return [sent.string.strip() for sent in document.sents]

def printToken(token):
    print(token.text, '->', token.dep_)
    
def appendChunk(original, chunk):
    return original + ' ' + chunk

def isRelationCandidate(token):
    deps = ['ROOT', 'adj', 'attr', 'agent', 'amod']
    return any(subs in token.dep_ for subs in deps)

def isConstructionCandidate(token):
    deps = ["compound", "prep", "conj", "mod"]
    return any(subs in token.dep_ for subs in deps)

def processSubjectObjectPairs(tokens):
    subject = ''
    object = ''
    relation = ''
    subjectConstruction = ''
    objectConstruction = ''
    for token in tokens:
        printToken(token)
        if "punct" in token.dep_:
            continue
        if isRelationCandidate(token):
            relation = appendChunk(relation, token.lemma_)
        if isConstructionCandidate(token):
            if subjectConstruction:
                subjectConstruction = appendChunk(subjectConstruction, token.text)
            if objectConstruction:
                objectConstruction = appendChunk(objectConstruction, token.text)
        if "subj" in token.dep_:
            subject = appendChunk(subject, token.text)
            subject = appendChunk(subjectConstruction, subject)
            subjectConstruction = ''
        if "obj" in token.dep_:
            object = appendChunk(object, token.text)
            object = appendChunk(objectConstruction, object)
            objectConstruction = ''

    print (subject.strip(), ",", relation.strip(), ",", object.strip())
    return (subject.strip(), relation.strip(), object.strip())

def processSentence(sentence):
    tokens = nlp_model(sentence)
    return processSubjectObjectPairs(tokens)

def printGraph(triples):
    G = nx.Graph()
    for triple in triples:
        G.add_node(triple[0])
        G.add_node(triple[1])
        G.add_node(triple[2])
        G.add_edge(triple[0], triple[1])
        G.add_edge(triple[1], triple[2])

    pos = nx.kamada_kawai_layout(G)
    plt.figure(figsize=(15,10))
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='skyblue', alpha=0.9, font_color='black',
            labels={node: node for node in G.nodes()})
    st.pyplot()
    
     
def wiki_page(page_name):
    wiki_api = wikipediaapi.Wikipedia(language='en',
                                      extract_format=wikipediaapi.ExtractFormat.WIKI)
    page_name = wiki_api.page(page_name)
    if not page_name.exists():
        print('page does not exist')
        return
    page_data = {'page': page_name, 'text': page_name.text, 'link': page_name.fullurl,
                 'categories': [[y[9:] for y in list(page_name.categories.keys())]]}
    page_data_df = pd.DataFrame(page_data)
    return page_data_df

# Main driver Program
if __name__ == "__main__":
    st.title('Knowledge Graph Generator') 
    types = st.radio('Select from the option below', ('Wikipedia page', 'Sentence or Paragraph'))
    if types == 'Wikipedia page':
        wiki_page_name = st.text_input('Enter the Wiki Page name:')
        gen_kg = st.button('Generate Knowledge Graph')
        if gen_kg:
            text = wiki_page(wiki_page_name)
            text = text.loc[0,'text']
            sentences = getSentences(text)
            nlp_model = spacy.load('en_core_web_sm')
            triples = []
            for sentence in sentences:
                triples.append(processSentence(sentence))
            printGraph(triples)

    if types == 'Sentence or Paragraph': 
        user_input = st.text_input('Enter a sentence or a paragraph:')
        gen_kg = st.button('Generate Knowledge Graph')
        if gen_kg:        
            sentences = getSentences(user_input)
            nlp_model = spacy.load('en_core_web_sm')
            triples = []
            #st.write(text)
            for sentence in sentences:
                triples.append(processSentence(sentence))
            printGraph(triples)
    

        
        
        