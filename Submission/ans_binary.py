#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 14:07:28 2018

@author: leonshi
"""

from nltk.corpus import wordnet as wn
from nltk.tree import Tree
from nltk.stem import WordNetLemmatizer
import SCNLP as sp

class Ans_Binary:
    
    def __init__(self):
        self.np = sp.StanfordNLP()
        self.lm = WordNetLemmatizer()        
    
    def ans_binary(self, question, relevent):
        q_pos = self.np.pos(question)[1:-1]
        r_pos = self.np.pos(relevent)
        check = []
        
        for word, tag in q_pos:  
            exist = False
            q_tag = self.get_pos(tag[0].lower())
            if (q_tag == 'n' or q_tag == 'v' or q_tag == 'a' or q_tag == 'r'):
                #print(word + ' ' + tag)
                for r_word, r_tag in r_pos:
                    r_tg = self.get_pos(r_tag)
                    if (r_tg == 'n' or r_tg== 'v' or r_tg == 'j' or r_tg == 'r'):
                        r_tg = self.get_pos(r_tag[0].lower())
                    else:
                        r_tg == ''
                    #if (tag[0].lower() == 'n' or tag[0].lower() == 'v') and (r_tag[0].lower() == 'n' or r_tag[0].lower() == 'v'):
                    sim = self.word_sim(word, r_word, q_tag, r_tg)           
                    if (sim or word == r_word) and tag[0:2] == r_tag[0:2]:
                        exist = True
                    if (tag == 'VB' or r_tag == 'VB') and ('VB' in tag or 'VB' in r_tag):
                        exist = True
                    #else:
                        #if word == r_word and tag[0:2] == r_tag[0:2]:
                            #exist = True
                #print(exist)
                check.append(exist)
        percentage = sum(check)/len(check)
        return percentage           
    
    def get_pos(self, tag):
        if tag == 'n':
            return 'n'
        elif tag == 'v':
            return 'v'
        elif tag == 'j':
            return 'a'
        elif tag == 'r':
            return 'r'
        else:
            return ""
           
    def word_sim(self, word1, word2, w1_tag, w2_tag):
        word1_syn, word1_ant = self.syn_ant(word1, w1_tag)  
        
        if w2_tag != '':
            word2 = self.lm.lemmatize(word2, w2_tag)
        else:
            word2 = self.lm.lemmatize(word2)
            
        sim = False
        
        if word2 in word1_syn:
            sim = True
        if word2 in word1_ant:
            sim = False
        
        return sim
    
    def syn_ant(self, word, pos):
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
    
if __name__ == '__main__':
    question_list = []
    answer_list = []
    
#    with open(questions, 'r') as r:
#        for line in r:
#            question_list.append(line)
#            
#    for question in question_list:
#        found = False
#        scores = []
#        relevent_list = find_releventJ(path, question)
#        for relevent in relevent_list:
#            score = ans_binary(question, relevent)
#            scores.append(score)
#        for score in scores:
#            if score == 1:
#                found = True
#                answer_list.append('Yes')
#        if not found:
#            answer_list.append('No')
        
