#! /usr/bin/env python3 

# USAGE
# runscript open-corpus [name]
''' Open the desired UDN corpus with an nltk PlaintextCorpusReader and provide an interactive python console for analyzing it.
'''

import argparse
parser = argparse.ArgumentParser(description='Open the desired UDN corpus with an nltk PlaintextCorpusReader and provide an interactive python console for analyzing it.')
parser.add_argument('name', help='Name of a UDN corpus to open. (must be a root-level directory of udn-corpora)')
args = parser.parse_args()

import sys

import nltk
import code
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
import os, os.path
import subprocess
from udn_nlp import util
from udn_nlp import nlp



if __name__ == '__main__':
    corpus = nlp.corpus_reader(args.name)
    text = nltk.Text(corpus.words())
    code.interact(banner="\n\nOpened the {} corpus for manual analysis.\nThe following nltk objects are locally available:\n\n* corpus: a PlaintextCorpusReader of all the corpus's text files\n* text: a Text object of all the corpus's text\n\nType exit() or Ctrl+D to exit.".format(args.name), local=locals())
    # TODO provide utils in local scope?
