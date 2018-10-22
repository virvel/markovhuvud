#!/usr/bin/python3

from random import sample
from collections import defaultdict
import json
import sys

class Markover:

    wordTable = defaultdict(list)

    
    def read_file(self):
        file = open(self.filepath,'r')
        self.text = file.read()

#        self.text = self.text.replace(",", "")
        self.text = self.text.replace("\n", " ")
        self.text = self.text.replace('\"', "")

        for x in self.text.split('. '):
            sentence = x.split(" ")
            for i in range(0, len(sentence)-1):
                self.wordTable[sentence[i]].append(sentence[i+1])
        for k,v in self.wordTable.items():
            self.wordTable[k] = list(set(v))

    def get_next_sentence(self):
        randWord = sample(list(self.wordTable), 1)

        currentWord = randWord[0]
        newSentence = ""

        while (self.wordTable[currentWord]):
            nextWord = sample(self.wordTable[currentWord], 1)[0]
            newSentence = newSentence + " " + nextWord
            currentWord = nextWord

        return newSentence[1:].capitalize() + "."

    
    def generate_from_txt(self,filepath):
        self.filepath = filepath
        self.read_file()
    

    def set_wordtable(self, dic):
        self.wordTable = dic

    
    def get_wordtable(self):
        return self.wordTable


def main():
    mrkv = Markover()
    mrkv.generate_from_txt(sys.argv[1])
    
    print(mrkv.get_next_sentence())

if __name__ == "__main__":
    main()


