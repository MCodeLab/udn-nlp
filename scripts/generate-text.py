#! /usr/bin/env python3

import sys
import os

from udn_nlp import util
from udn_nlp import nlp

import nltk
from nltk.corpus import words

from html.parser import HTMLParser
import csv

from nltk.stem import WordNetLemmatizer



if __name__ == '__main__':
    # Default id to extract mistakes from is Heartitorium
    id = 18189570

    if len(sys.argv) > 1:
        # First optional argument is the ID of a document to extract from
        id = sys.argv[1]

    text = nlp.generate_nltk_text_from_doc(id)
    for i in range(len(text)):
        print(text[i] + " ")
