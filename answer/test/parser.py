#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 14:07:28 2018

@author: leonshi
"""

import sys
from textblob import TextBlob
from nltk.parse.corenlp import CoreNLPParser
from nltk.metrics.distance import *
from nltk.stem import WordNetLemmatizer
from nltk.tree import ParentedTree

parser = CoreNLPParser(url='http://localhost:9000')
path = '/Users/leonshi/eclipse-workspace/NLP/a1.txt'
wh_words = ['What', 'Where', 'Who', 'When']
aux_words = ["am", "are", "is", "was", "were",
             "does", "did", "has", "had", "may", "might", "must",
             "need", "ought", "shall", "should", "will", "would"]

#Takes in an input to a text file
#Returns a list of the sentences
def parse_sentences(path):
    with open(path) as r:
        text = r.read()    
        
    #Use textblob to read file
    txt = TextBlob(text)
    res = []   
    
    #Append sentences to a list and return a list of the sentences
    for sentence in txt.sentences: 
        res.append(str(sentence)) 
        
    return res

#Takes in a sentence
#Returns the "Wh" root of the sentence
def determine_wh(sentence):
    sentence = list(parser.tokenize(sentence))
    wh_root = sentence[0].lower()
    #print(wh_root)
    return wh_root

#Takes in a text file and a list of sentences (questions)
#Return the most relevent sentence
def find_relevent(path, questions):
    sentences = parse_sentences(path)   
    
    relevent = []
    
    for question in questions:
        lisDic = {}
        for i in range(len(sentences)):
            #print(edit_distance(question, sentences[i], transpositions=True))
            lisDic[i] = edit_distance(question, sentences[i], transpositions=True)
        minInd = min(lisDic, key = lisDic.get)
        relevent.append(sentences[minInd])
    
    return relevent
 
#Takes in a text file and a list of sentences (questions)
#Return a list of the most relevent sentences        
def find_releventJ(path, questions):
    sentences = parse_sentences(path)   
    
    relevent = []
    
    #Find jaccard distance for every question/sentence pair and return the sentence w/ minimum jaccard distance
    for question in questions:
        question = set(list(parser.tokenize(question)))
        lisDic = {}
        for i in range(len(sentences)):
            token_sen = set(list(parser.tokenize(sentences[i])))
            #print(jaccard_distance(question, token_sen))
            lisDic[i] = jaccard_distance(question, token_sen)
        minInd = min(lisDic, key = lisDic.get)
        relevent.append(sentences[minInd])
    
    return relevent

def ans_type(question, relevent):
    wh_root = determine_wh(question)
    if wh_root in aux_words:
        ans_binary(question, relevent)
    else:
        ans_wh(question, relevent)



q_tree = parser.raw_parse(question)
r_tree = parser.raw_parse(relevent)        

q_tree = list(parser.raw_parse(questions[0]))
r_tree = list(parser.raw_parse(relevent[0]))

newtree = ParentedTree.convert(r_tree[0])
newtree.draw()

for subtree in newtree:
    print(subtree.left_sibling())
        
print(q_tree)
for item in q_tree:
    print(item.label())

def traverse_tree(tree):
    #print("tree:", tree)
    for subtree in tree:
        if type(subtree) == nltk.tree.ParentedTree:
            if subtree.label() == 'VP':
                print(subtree.subtrees())
                #print(subtree.leaves())
                #print(subtree.label())
            traverse_tree(subtree)
            
traverse_tree(newtree)
   
lemmatizer = WordNetLemmatizer()
print(lemmatizer.lemmatize("describes", pos='v'))

relevent = find_releventJ(path, questions)
answer(questions[0], relevent[0])

questions = ['What describes the important inscription on the tomb of Ankhtifi, a nomarch during the early First Intermediate Period?']
    
        