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

    def getAllWords(self,label,t):
        if type(t) == str:
            return []
        else:
            elems = []
            for subtree in t:
                if type(subtree) == str and t.label() == label:
                    elems.append(t)
                else:
                    elems += self.getAllWords(label,subtree)
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


    # where
    place_prep = ['above', 'across', 'along', 'among', 'around', 'at',
                  'behind', 'below', 'beside', 'between', 'by', 'down',
                  'from', 'inside', 'in', 'into', 'near', 'on', 'onto',
                  'opposite', 'outside', 'over', 'past',
                  'through', 'to', 'towards', 'under', 'up']
    two_place_prep = [('close','to'), ('in','front'), ('next','to'),
                      ('out','of')]

    time_prep = ['on', 'in', 'at', 'since', 'for', 'ago', 'before',
                 'from', 'till', 'until', 'by']

    v_to_be = ['be', 'is', 'am', 'are', 'was', 'were']

    verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    def answer_npvp(self, vstem, nstem, t):
        # look for ADJP, ADVP, PP in VPs first
        plabels = ['ADJP', 'ADVP', 'PP']
        for vp in self.getAll("VP", t)[::-1]:
            componentStem = [self.stemmer.stem(w) for w in vp.leaves()]
            if vstem in componentStem:
                if vp.label() == "VP":
                    pchildren = [c for c in vp if c.label() in plabels]
                    ans = ""
                    if len(pchildren) > 0:
                        for p in pchildren:
                            nps = self.getAll("NP", p)
                            if len(nps) > 0:
                                ans += " ".join(p.leaves()) + " "
                    if ans != "":
                        return ans

        for np in self.getAll("NP", t):
            componentStem = [self.stemmer.stem(w) for w in np.leaves()]
            if nstem in componentStem:
                if np.label() == "NP":
                    pchildren = [c for c in np if c.label() in plabels]
                    ans = ""
                    if len(pchildren) > 0:
                        for p in pchildren:
                            nps = self.getAll("NP", p)
                            if len(nps) > 0:
                                ans += " ".join(p.leaves()) + " "
                    if ans != "":
                        return ans
        return ""


    def location_answer(self, q_tokens, relevant):
        names = self.nlp.ner(relevant)
        locations = [w for (w,c) in names if c =='LOCATION']



    def where_answer(self, question, relevant):
        t = Tree.fromstring(self.nlp.parse(relevant))

        doc = self.snlp(question)
        for token in doc:
            if token.dep_ == 'nsubj' and token.head.dep_ == 'ROOT':
                nkey = token.text
                nstem = self.stemmer.stem(token.text)
                vstem = ""
                root = token.head.text
                if root in self.v_to_be:
                    #find the verb
                    for vtoken in doc:
                        if (vtoken.dep_ == 'relcl' and
                            vtoken.head.text == nkey):
                            vkey = vtoken.text
                            vstem = self.stemmer.stem(vtoken.text)
                else:
                    vstem = self.stemmer.stem(root)

                ans = self.answer_npvp(vstem, nstem, t)

                if ans != "":
                    return ans
        return ""

    def ans_who(self, question, relevent):
        names = self.nlp.ner(relevent)

        ans = ''
        q_tokens = self.nlp.word_tokenize(question)
        #First do a title check and a person check
        for i in range(len(names)):
            if names[i][1] == 'TITLE' and names[i][0][0].istitle():
                if names[i+1][0][0].istitle():
                    ans = names[i][0] + ' ' + names[i+1][0] + '.'
                    break
                elif names[i][0][0].istitle():
                    ans = 'The ' + names[i][0] + '.'
                    break
            elif names[i][1] == 'PERSON':
                ans = names[i][0] + '.'

        #If NER does not recognize named entities, check for capitalized names
        for i in range(len(names)):
            if names[i][0][0].istitle() and names[i][0] not in q_tokens:
                ans = names[i][0]

        if ans == '':
            ans = 'NONEFOUND'

        return ans





