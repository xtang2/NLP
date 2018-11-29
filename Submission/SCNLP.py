#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 14:20:53 2018

@author: leonshi
"""

'''
A sample code usage of the python package stanfordcorenlp to access a Stanford CoreNLP server.
Written as part of the blog post: https://www.khalidalnajjar.com/how-to-setup-and-use-stanford-corenlp-server-with-python/ 
'''

from stanfordcorenlp import StanfordCoreNLP
from collections import defaultdict
import logging
import json

class StanfordNLP:
    def __init__(self, host='http://localhost', port=8889):
        self.nlp = StanfordCoreNLP(host, port=port,
                                   timeout=30000)  # , quiet=False, logging_level=logging.DEBUG)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }

    def word_tokenize(self, sentence):
        return self.nlp.word_tokenize(sentence)

    def pos(self, sentence):
        return self.nlp.pos_tag(sentence)

    def ner(self, sentence):
        return self.nlp.ner(sentence)

    def parse(self, sentence):
        return self.nlp.parse(sentence)

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))

    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = defaultdict(dict)
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
            }
        return tokens

if __name__ == '__main__':
    sNLP = StanfordNLP()
    text = 'Did the cat cry?'
    print("Annotate:", sNLP.annotate(text))
    print("POS:", sNLP.pos(text))
    print("Tokens:", sNLP.word_tokenize(text))
    print("NER:", sNLP.ner(text))
    print("Parse:", sNLP.parse(text))
    print("Dep Parse:", sNLP.dependency_parse(text))
        
    atext = 'Egyptians in this era worshipped their Pharaoh as a god, believing that he ensured the annual flooding of the Nile that was necessary for their crops.'
    print("Annotate:", sNLP.annotate(atext))
    print("POS:", sNLP.pos(atext))
    print("Tokens:", sNLP.word_tokenize(atext))
    print("NER:", sNLP.ner(atext))
    print("Parse:", sNLP.parse(atext))
    print("Dep Parse:", sNLP.dependency_parse(atext))