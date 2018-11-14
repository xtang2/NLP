#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 14:07:28 2018

@author: leonshi
"""

import sys
from textblob import TextBlob
from nltk.metrics.distance import jaccard_distance
import SCNLP as sp
import ans_binary as bi
import wh_answer as wa
path = sys.argv[1]
questions = sys.argv[2]

#path = '/Users/leonshi/eclipse-workspace/NLP/a1.txt'
#questions = ['Was Userkaf succeed by his son Sahure?']

bi = bi.Ans_Binary()
wh = wa.Wh_Answer()
np = sp.StanfordNLP()

wh_words = ['what', 'where', 'who', 'when', 'why']
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
    
    # if isinstance(questions,(list,)) == False:
    #     print("Please specify a list of questions")
    #     return None
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

def ans_type(question):
    wh_root = determine_wh(question)
    if wh_root in wh_words:
        return 'Wh'
    else:
        return 'Binary'
        
def main():
    question_list = []
    answer_list = []
    
    with open(questions, 'r') as r:
        for line in r:
            question_list.append(line)
                      
    for question in question_list:
        if ans_type(question) == 'Binary':  
            found = False
            scores = []
            relevent_list = find_releventJ(path, question)
            if relevent_list is None:
                answer_list.append('No')
            else:
                for relevent in relevent_list:
                    #Answering question using binary answering module class
                    score = bi.ans_binary(question, relevent)
                    scores.append(score)
                for score in scores:
                    if score == 1:
                        found = True
                        answer_list.append('Yes')
                if not found:
                    answer_list.append('No')
        if ans_type(question) == 'Wh':
            #Do something depending on what type of question it is
            wh_root = determine_wh(question)
            
            if wh_root == 'what':
                relevant_list = find_releventJ(path,question)
                if relevant_list is None:
                    found = False
                else:
                    for relevant in relevant_list:
                        ans = wh.what_answer(question, relevant)
                        if ans != "":
                            found = True
                            answer_list.append(ans.capitalize())
                            break
                        # insert scoring scheme here
                    if not found:
                        answer_list.append('What is a What?')
            elif wh_root == 'why':
                answer_list.append('Because why not?')
            elif wh_root == 'when':
                answer_list.append('Any time is a good time!')
            elif wh_root == 'where':
                answer_list.append('Where in the world is Carmen San Diego?')
            elif wh_root == 'who':
                answer_list.append('Subra Suresh.')
    for answer in answer_list:
        print(answer)      

if __name__== "__main__":
    main()        
