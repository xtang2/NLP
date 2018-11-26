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
        self.np = sp.StanfordNLP()

    def ans_who(self, question, relevent):
        names = self.np.ner(relevent)

        ans = ''
        q_tokens = self.np.word_tokenize(question)
        #First do a title check and a person check
        for i in range(len(names)):
            if names[i][1] == 'TITLE' and names[i][0][0].istitle():
                if names[i+1][0][0].istitle():
                    ans = names[i][0] + ' ' + names[i+1][0] + '.'
                    break
            elif names[i][1] == 'PERSON':
                ans = names[i][0] + '.'

        #If NER does not recognize named entities, check for capitalized names
        for i in range(len(names)):
            if names[i][0][0].istitle() and names[i][0] not in q_tokens:
                ans = names[i]

        if ans == '':
            ans = 'NONEFOUND'

        return ans
