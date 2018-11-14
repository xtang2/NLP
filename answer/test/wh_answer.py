#!/usr/bin/env python3

from nltk.parse.corenlp import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.stem.porter import *
from stanfordcorenlp import StanfordCoreNLP
from queue import Queue
from nltk.tree import Tree
import spacy
import sys
import json
import SCNLP as sp

class Wh_Answer:

    def __init__(self):
        self.nlp = sp.StanfordNLP()
        self.stemmer = PorterStemmer()
        self.snlp = spacy.load('en_core_web_sm')

    # #text = "Egyptians in this era worshipped their Pharaoh as a god, believing that he ensured the annual flooding of the Nile that was necessary for their crops."
    # text = "The cat did eat the cake."
    # q = "What did the cat eat?"
    # nlp = sp.StanfordNLP()
    # parse = nlp.parse(text)
    # t = Tree.fromstring(parse)
    # print(type(t))
    # stemmer = PorterStemmer()
    # sentenceStem = [stemmer.stem(w) for w in text.split()]
    # print(sentenceStem)
    # snlp = spacy.load('en_core_web_sm')
    # doc = snlp(q)
    # for token in doc:
    #     print (token.text, token.pos_, token.dep_)
    #     if token.dep_ == 'ROOT':
    #         root = token.text


    # parser = CoreNLPParser(url='http://localhost:9000')
    # parse = parser.raw_parse(text)
    #depparse = nlp.dependency_parse("Who did Ehyptians in this era worship?")
    #print(depparse)

    # strategy for who, what questions:
    # look for NP be NP, match either of them and return the unmatched one
    # this assumes that the question doesn't come in the form of NP,NP,blah! (that might be for later)


    # keyphrase = root
    # keystem = stemmer.stem(keyphrase)
    # print(keystem)

    def getAll(self,label,t):
        if type(t) == str:
            return []
        elems = []
        for subtree in t:
            if type(subtree) != str and subtree.label() == label:
                elems.append(subtree)
            elems += self.getAll(label,subtree)
        return elems

    def what_answer_s(self,keyphrase, t):
        for s in self.getAll("S", t)[::-1]:
           for components in s:
              componentStem = [self.stemmer.stem(w) for w in components.leaves()]
              if keystem in componentStem:
                  if components.label() == "VP":
                      # print(components)
                      npchildren = [c for c in components if c.label() == "NP"]
                      if len(npchildren) == 0:
                          continue
                      else:
                          return " ".join(npchildren[0].leaves())
        return ""


    def what_answer_vp(self,keystem, t):
        for components in self.getAll("VP", t)[::-1]:
          # print(components)
          componentStem = [self.stemmer.stem(w) for w in components.leaves()]
          if keystem in componentStem:
              if components.label() == "VP":
                  # print(components)
                  npchildren = [c for c in components if c.label() == "NP"]
                  if len(npchildren) == 0:
                      continue
                  else:
                      return " ".join(npchildren[0].leaves())
        return ""

    # requires: relevant is a single sentence string, not a list!
    def what_answer(self,question,relevant):
        # dependency parse question
        t = Tree.fromstring(self.nlp.parse(relevant))

        doc = self.snlp(question)
        for token in doc:
            if token.dep_ == 'ROOT' or token.dep_ == 'acl': # will need to fine tune
                keystem = self.stemmer.stem(token.text)
                ans = self.what_answer_vp(keystem, t)
                if ans != "":
                    return ans
        return ""

