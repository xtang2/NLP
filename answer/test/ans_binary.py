#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 14:07:28 2018

@author: leonshi
"""

import sys
from textblob import TextBlob
from nltk.metrics.distance import jaccard_distance
from nltk.corpus import wordnet as wn
from nltk.tree import Tree
from nltk.stem import WordNetLemmatizer
import SCNLP as sp

np = sp.StanfordNLP()
lm = WordNetLemmatizer()
path = '/Users/leonshi/eclipse-workspace/NLP/a1.txt'
questions = ['Was Userkaf succeed by his son Sahure?']
question_list = ['Was Userkaf succeed by his son Sahure?']
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
    sentence = list(np.word_tokenize(sentence))
    wh_root = sentence[0].lower()
    #print(wh_root)
    return wh_root
    
#Takes in a text file and a list of sentences (questions)
#Return a list of the most relevent sentences        
def find_releventJ(path, question):
    sentences = parse_sentences(path)   
    rel_sen = []
    if path is None:
        print("Please specify a file to search from.")
        return None
    
    if isinstance(questions,(list,)) == False:
        print("Please specify a list of questions")
        return None
    #Find jaccard distance for every question/sentence pair and return the sentence w/ minimum jaccard distance

    question = set(list(np.word_tokenize(question)))
    lisDic = {}
    for i in range(len(sentences)):
        token_sen = set(list(np.word_tokenize(sentences[i])))
        lisDic[i] = jaccard_distance(question, token_sen)
    rel_ind = sorted(lisDic, key=lisDic.get)[:5]
    for ind in rel_ind:
        rel_sen.append(sentences[ind])
    
    return rel_sen

def ans_type(question, relevent):
    wh_root = determine_wh(question)
    if wh_root in wh_words:
        ans_wh(question, relevent)
    else:
        ans_binary(question, relevent)   

def ans_binary(question, relevent):
    q_pos = np.pos(question)[1:-1]
    r_pos = np.pos(relevent)
    
    check = []
    for word, tag in q_pos:    
        exist = False
        for r_word, r_tag in r_pos:
            if (tag[0].lower() == 'n' or tag[0].lower() == 'v') and (r_tag[0].lower() == 'n' or r_tag[0].lower() == 'v'):
                sim = word_sim(word, r_word, tag[0].lower(), r_tag[0].lower())           
                if (sim or word == r_word) and tag[0:2] == r_tag[0:2]:
                    exist = True
            else:
                if word == r_word and tag[0:2] == r_tag[0:2]:
                    exist = True
        check.append(exist)
    
    percentage = sum(check)/len(check)
    return percentage           

def word_sim(word1, word2, w1_tag, w2_tag):
    word1_syn, word1_ant = syn_ant(word1, w1_tag)  
    
    if w1_tag == 'n' or w1_tag == 'v':
        word2 = lm.lemmatize(word2, w2_tag)    
    else:
        word2 = lm.lemmeatize(word2)
        
    sim = False
    
    if word2 in word1_syn:
        sim = True
    if word2 in word1_ant:
        sim = False
    
    return sim

def syn_ant(word, pos):
    synonyms = []
    antonyms = []
    
    for syn in wn.synsets(word, pos):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
        for syn in syn.hypernyms():
            for l in syn.lemmas():
                synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    
    return synonyms, antonyms

def main():
    question_list = []
    answer_list = []
    
    with open(questions, 'r') as r:
        for line in r:
            question_list.append(line)
            
    for question in question_list:
        found = False
        scores = []
        relevent_list = find_releventJ(path, question)
        for relevent in relevent_list:
            score = ans_binary(question, relevent)
            scores.append(score)
        for score in scores:
            if score == 1:
                found = True
                answer_list.append('Yes')
        if not found:
            answer_list.append('No')
        
