#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 00:52:06 2018

@author: leonshi
"""

from nltk.corpus import wordnet as wn
from nltk.tree import Tree
from nltk.stem import WordNetLemmatizer
import SCNLP as sp

class Ans_Who:

    def __init__(self):
        self.nlp = sp.StanfordNLP()

    def who_answer(self, question, relevant):
        names = self.nlp.ner(relevant)
        ans = ''
        q_tokens = self.nlp.word_tokenize(question)
        #First do a title check and a person check
        found = False
        for i in range(len(names)):
            if names[i][1] == 'TITLE' and names[i][0][0].istitle():
                if names[i+1][0][0].istitle():
                    ans = names[i][0] + ' ' + names[i+1][0] + '.'
                    found = True
                    break
                elif names[i][0][0].istitle():
                    ans = 'The ' + names[i][0] + '.'
                    found = True
                    break
            elif names[i][1] == 'PERSON':
                ans = names[i][0] + '.'
                found = True

        #If NER does not recognize named entities, check for capitalized names
        if found == False:
            for i in range(len(names)):
                if names[i][0][0].istitle() and names[i][0] not in q_tokens:
                    ans = names[i][0] + '.'

        if ans == '':
            ans = 'NONEFOUND'

        return ans
    
    def main():
        wa = Ans_Who()
        np = sp.StanfordNLP()
        path = '/Users/leonshi/Desktop/NLP 11611/Project Progress Report/a1.txt'
        sentences = parse_sentences(path)
        rel_sen = find_releventS(sentences, question)
        relevant = rel_sen[0]
        parsed = Tree.fromstring(np.parse(relevant))
        nppos = np.pos(relevant)
        dep_parsed = np.dependency_parse(relevant)
        rel = np.word_tokenize(relevant)
        dep = dep_out(dep_parsed,rel)
        for tree in parsed[0]:
            print(tree.label())
            print(tree.leaves())
        np.ner(relevant)
        question = 'Who was the first Pharaoh of the Old Kingdom?'
        print(wa.who_answer(question, relevant))
        

