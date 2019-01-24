#! /usr/bin/env python3

# TODO this script is incomplete & deprecated. The goal was to generate a CSV file for localturk ground truth annotation of commonly misidentified words.

import sys
import os
import nltk

from udn_nlp import util
from udn_nlp import nlp

import nltk
from nltk.corpus import words

from html.parser import HTMLParser
import csv

from nltk.stem import WordNetLemmatizer



if __name__ == '__main__':
    # Default id to extract mistakes from is a Heartitorium sample
    id = 18189570

    if len(sys.argv) > 1:
        # First optional argument is the ID of a document to extract from
        id = sys.argv[1]


    # Import an article as JSON
    doc = util.retrieve_document(id)

    word_corpus = None
    lemmatizer = None
    while True:
        try:
            word_corpus = words.words()
            lemmatizer = WordNetLemmatizer()
            lemmatizer.lemmatize("named")
            break

        except LookupError:
            nltk.download('words')
            nltk.download('wordnet')
            # TODO make a reusable nltk corpus-open function
            print('looping again')


    sorted_tokens = nlp.check_mistakes(doc['ocr'])

    valid_words = len(sorted_tokens['right_words'])
    invalid_words = len(sorted_tokens['wrong_words'])

    ocr_accuracy = valid_words / (valid_words + invalid_words)

    print('OCR accuracy for document {}: {}'.format(id, ocr_accuracy))

    # TODO from here onwards is for constructing training data, and should only be executed optionally.

    wrong_words = sorted_tokens['wrong_words']

    # Download the document's PDF file if necessary
    util.download_file(doc[u'file'])
    filename = util.global_dest_for_webfile(doc[u'file'])
    output_file = filename.replace('.pdf', '.xhtml')
    csv_file = filename.replace('.pdf', '.csv')

    # Generate a csv file with info on wrong word bounding boxes
    if not os.path.exists(csv_file):
        if not os.path.exists(output_file):
            # Use `pdftotext -bbox` to convert it to an xhtml file with bounding boxes for words, if this isn't done yet
            util.call_console('pdftotext -bbox {} {}'.format(filename, output_file))


    with open(csv_file, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Parse the xhtml file. Loop through its word bounding boxes, and for ones whose words are in the bad token list,
        # add them to a CSV file with the bounding box and the file they came from.
        class BoundingBoxParser(HTMLParser):
            bbox = []
            page = 0

            def handle_starttag(self, tag, attributes):
                if tag == 'page':
                    self.page += 1
                if tag == 'word':
                    self.bbox = [attr[1] for attr in attributes]
                    
            def handle_data(self, data):
                # If a bounding box has been set, this must be the contents of that bounding box.
                if len(self.bbox) > 0:
                    # If the word is one of the mistakes, add its bounding box
                    if data in wrong_words:
                        # print('adding bbox to csv for ' + data)
                        csv_writer.writerow([filename, self.page, data] + self.bbox)
                    
                    self.bbox = []
        
        parser = BoundingBoxParser()
        parser.feed(open(output_file, 'r').read())
