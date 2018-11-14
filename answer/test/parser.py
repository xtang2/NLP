#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 14:07:28 2018

@author: leonshi
"""

import io
import sys
from textblob import TextBlob
from nltk.parse.corenlp import CoreNLPParser
from nltk.metrics.distance import *
from nltk.stem import WordNetLemmatizer
from nltk.tree import ParentedTree

parser = CoreNLPParser(url='http://localhost:9000')
path = sys.argv[1]
question_file = sys.argv[2]

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
#Return the most relevant sentence
def find_relevant(path, questions):
    sentences = parse_sentences(path)

    relevant = []

    for question in questions:
        lisDic = {}
        for i in range(len(sentences)):
            #print(edit_distance(question, sentences[i], transpositions=True))
            lisDic[i] = edit_distance(question, sentences[i], transpositions=True)
        minInd = min(lisDic, key = lisDic.get)
        relevant.append(sentences[minInd])

    return relevant

#Takes in a text file and a list of sentences (questions)
#Return a list of the most relevant sentences
def find_relevantJ(path, questions):
    sentences = parse_sentences(path)

    relevant = []

    #Find jaccard distance for every question/sentence pair and return the sentence w/ minimum jaccard distance
    for question in questions:
        question = set(list(parser.tokenize(question)))
        lisDic = {}
        for i in range(len(sentences)):
            token_sen = set(list(parser.tokenize(sentences[i])))
            #print(jaccard_distance(question, token_sen))
            lisDic[i] = jaccard_distance(question, token_sen)
        minInd = min(lisDic, key = lisDic.get)
        relevant.append(sentences[minInd])

    return relevant

def ans_type(question, relevant):
    wh_root = determine_wh(question)
    if wh_root in aux_words:
        ans_binary(question, relevant)
    else:
        ans_wh(question, relevant)

def answer(question, relevant):
    print(question)
    print(relevant)

#
#q_tree = parser.raw_parse(question)
#r_tree = parser.raw_parse(relevant)
#
#q_tree = list(parser.raw_parse(questions[0]))
#r_tree = list(parser.raw_parse(relevant[0]))
#
#newtree = ParentedTree.convert(r_tree[0])
#newtree.draw()
#
#for subtree in newtree:
#    print(subtree.left_sibling())
#
#print(q_tree)
#for item in q_tree:
#    print(item.label())
#
#def traverse_tree(tree):
#    #print("tree:", tree)
#    for subtree in tree:
#        if type(subtree) == nltk.tree.ParentedTree:
#            if subtree.label() == 'VP':
#                print(subtree.subtrees())
#                #print(subtree.leaves())
#                #print(subtree.label())
#            traverse_tree(subtree)
#
#traverse_tree(newtree)
#
#lemmatizer = WordNetLemmatizer()
#print(lemmatizer.lemmatize("describes", pos='v'))
#

with io.open(question_file, 'r', encoding='utf-8') as f:
    questions = f.read().splitlines()


relevant = find_relevantJ(path, questions)
answer(questions, relevant)

#
#
