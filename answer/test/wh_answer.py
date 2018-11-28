#!/usr/bin/env python3

from nltk.parse.corenlp import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
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
        self.lm = WordNetLemmatizer()


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

    def getAtLevel(self,i,t):
        if i <= 0:
            return [t]
        else:
            if type(t) == str:
                return []
            else:
                elems = []
                for subtree in t:
                    elems += self.getAtLevel(i-1,subtree)
                return elems

    def what_answer_s(self,keyphrase, t):
        for s in self.getAll("S", t)[::-1]:
           for components in s:
              componentStem = [self.stemmer.stem(w) for w in components.leaves()]
              if keyphrase in componentStem:
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

    def when_answer(self,question,relevant):
        return self.where_answer(question,relevant)

    def find_stem(self, doc):
        nkey = ''
        vstem = ''
        npos = ''
        for token in doc:
            #print (token.text, token.pos_, token.dep_, token.head.dep_)
            if (token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass') and token.head.dep_ == 'ROOT':
                nkey = token.text
                #nstem = stemmer.stem(nkey)
                npos = token.pos_
            if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
                root = token.head.text
                vstem = self.lm.lemmatize(root,'v')
        return nkey, vstem, npos

    def who_answer(self, question, relevant):
        ques = self.snlp(question)
        rele = self.snlp(relevant)

        q_nstem, q_vstem, q_npos = self.find_stem(ques)
        r_nstem, r_vstem, r_npos = self.find_stem(rele)

        ans = ""
        if r_vstem == q_vstem:
            ans = r_nstem

        if ans != "":
            return ans + "."
        else:
            return ""

#    def who_answer(self, question, relevant):
#        return self.where_answer(question,relevant)
#
#    def who_answer(self, question, relevant):
#        names = self.nlp.ner(relevant)
#
#        ans = ''
#        q_tokens = self.nlp.word_tokenize(question)
#        #First do a title check and a person check
#        for i in range(len(names)):
#            if names[i][1] == 'TITLE' and names[i][0][0].istitle():
#                if names[i+1][0][0].istitle():
#                    ans = names[i][0] + ' ' + names[i+1][0] + '.'
#                    break
#                elif names[i][0][0].istitle():
#                    ans = 'The ' + names[i][0] + '.'
#                    break
#            elif names[i][1] == 'PERSON':
#                ans = names[i][0] + '.'
#
#        #If NER does not recognize named entities, check for capitalized names
#        for i in range(len(names)):
#            if names[i][0][0].istitle() and names[i][0] not in q_tokens:
#                ans = names[i][0]
#
#        if ans == '':
#            ans = 'NONEFOUND'
#
#        return ans

    why_words = ['because', 'since', 'therefore', 'as a result of', 'as long as',
             'by reason of', 'by virtue of', 'considering', 'due to', 'for the reason that',
             'for the sake of', 'in as much as', 'in behalf of', 'in that', 'in the interest of'
             'now that', 'for the reason that', 'by cause of', 'thanks to']

    def find_S(self, tree):
        phrases = []
        if tree.label()[0] == 'S':
            phrases.append(tree)
        for child in tree:
            if type(child) is Tree:
                list_of_phrases = self.find_S(child)
                if (len(list_of_phrases) > 0):
                    phrases.extend(list_of_phrases)
        return phrases

    def why_answer(self, question, relevant):
        #Get all nouns in the question
        Q_nouns = [tup[0] for tup in self.nlp.pos(question) if tup[1][0] == 'N']

        #Find all phrases and sub phrases from the relevent sentence
        r_out = Tree.fromstring(self.nlp.parse(relevant))
        phrase_ans = []
        phrases = self.find_S(r_out)

        #For each phrase, find the NP and VP and parse out the nouns in the NP
        for tree in phrases:
            #print(tree.label())
            #print(tree.leaves())
            found = False
            for subtree in tree:
                #print(subtree.label())
                #print(subtree.leaves())
                if subtree.label() == 'NP':
                    nounP = " ".join(subtree.leaves())
                    R_nouns = [tup[0] for tup in self.nlp.pos(nounP) if tup[1][0] == 'N']
                    for noun in R_nouns:
                        #If nouns in the subphrase are not in the question, we are in the wrong phrase, append wrong phrase and skip the current phrase
                        if noun not in Q_nouns:
                            phrase_ans.append('WrongPhrase')
                            break
                verbP = ''
                if subtree.label() == 'VP':
                    verbP = " " .join(subtree.leaves())
                #If we find an instance of a "Why" word, find the position and return the string starting from that position.
                for word in self.why_words:
                    if word in verbP:
                        found = True
                        location = verbP.find(word)
                        verbP = verbP[location:]
                        phrase_ans.append(verbP.capitalize())
                        break

            #If there was no phrase, append WrongPhrase
            if found == False:
                phrase_ans.append('WrongPhrase')

        ans = ''
        #Check all the answers in phrase answers, the correct answer is the one that is not from a Wrong Phrase
        for answer in phrase_ans:
            if answer != 'WrongPhrase':
                ans = answer + '.'

        if ans == '':
            return relevant
        else:
            return ans




