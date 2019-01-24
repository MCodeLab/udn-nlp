#! /usr/bin/env python3
# USAGE
# runscript build-corpus [directory] [query] [also generate unfiltered: default True]


import argparse
parser = argparse.ArgumentParser(description="Build an NLTK-compatible plaintext corpus from documents that fit a UDN API query")
parser.add_argument('directory', help="Directory in which to place the corpus text files.")
parser.add_argument('query', help="UDN API query for selecting corpus documents.")
parser.add_argument('unfiltered', nargs="?", default=True, type=bool, help="Also generate an unfiltered version?")
args = parser.parse_args()

import sys
import os
import multiprocessing
from multiprocessing import Pool, Lock
import subprocess

from udn_nlp import util
from udn_nlp import nlp

import nltk
from nltk.corpus import words

from html.parser import HTMLParser
import csv

''' This script will incrementally fill a given directory with text
files containing
the error-filtered OCR data of documents that match a given UDN query
(i.e. query by type, by newspaper, by date, etc).
Once such a directory exists, the following code will open it as an nltk corpus:

```
import os
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

corpus = PlaintextCorpusReader('DIRECTORY/', '.*.txt')
```

(according to https://stackoverflow.com/a/20922201)


NOTE This script tries to create an exhaustive corpus from the query, but you should be able to interrupt it without any problems to create a partial corpus.
Running the script with the same args later will continue corpus creation
from where it was stopped.

'''

directory = args.directory
query = args.query
generate_unfiltered = args.unfiltered

# Make a metadata file in the directory story the command and module version with which the corpus was built
build_info_string = "Built with query {} by udn-ocr@{}".format(query, subprocess.check_output(["git", "rev-parse", "HEAD"]).strip())

limit = 100

meta_file = ''

def make_corpus_file(doc, text, f):
    # TODO option to include or not include metadata header?
    # Put metadata for each document at the top
    util.safe_print(doc, 'articleTitle', f, '{}\r\n')
    util.safe_print(doc, 'paper', f, '{} ')
    util.safe_print(doc, 'type', f, '{} - ')
    util.safe_print(doc, 'month', f, '{} ')
    util.safe_print(doc, 'day', f, '{}, ')
    util.safe_print(doc, 'year', f, '{} ')

    f.write('\r\n---\r\n')
    
    f.write(text)

def filter_document(doc):
    # fill text files with output of nlp.filter_words(doc['ocr'])
    filename = str(doc['id']) + '.txt'
    with open(directory + '/' + filename, 'w') as f:
        with open(directory + '-unfiltered/' + filename, 'w') as uf:
            # if ocr isn't included in one of the documents, leave it empty and print a message 
            text = ''
            if 'ocr' in doc:
                text = doc['ocr']
            else:
                print('document {} has no OCR text!'.format(doc['id']))
            filtered_text, words_filtered = nlp.filter_words(text, optional_id=str(doc['id']))
            # Make 2 copies of the corpus, one unfiltered
            make_corpus_file(doc, filtered_text, f)
            if generate_unfiltered:
                make_corpus_file(doc, text, uf)

            print(doc['id'])

            # NOTE locking is necessary for the seaparate processes to store filtered words for later reference, all in one file. Speed tests without this operation didn't yield a noticeable difference
            lock.acquire()
            with open(meta_file, 'a') as filter_log:
                for key in words_filtered:
                    filter_log.write(key+'\n')
            lock.release()

if __name__ == "__main__":
    # Test the query to estimate the total size of the corpus that would
    # be created
    total_docs = util.dry_make_request(query)[0]['numFound']
    gigs_per_doc = .00002
    if args.unfiltered:
        gigs_per_doc *= 2
    print('The corpus of text from this query would have a file size of ~{} GB'.format(total_docs*gigs_per_doc))
    print('continue? (y/n)')

    if input() == 'n':
        exit()

    # make sure the corpus directory and its parent path exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(directory + '-unfiltered'):
        os.makedirs(directory + '-unfiltered')

    enclosing_dir = os.path.abspath(directory) + '/../'
    corpus_name = os.path.basename(directory)

    previous_build_info_string = ""
    meta_file = enclosing_dir + corpus_name + '.txt'
    if os.path.exists(meta_file):
        with open(meta_file, 'r') as ff:
            previous_build_info_string = ff.readline()

    with open(meta_file, 'w') as ff:
        ff.write("{}\n".format(build_info_string))

    # prompt to delete old corpus files if the two build info strings don't match
    if previous_build_info_string != build_info_string and previous_build_info_string != "":
        delete = input("A previously generated corpus exists at that location, built with an out-of-date udn-ocr module. Delete and start over? (Y/n)")
        if delete == "Y" or delete == "y":
            print("deleting")
            subprocess.call(["rm", "-rf", directory])
            os.makedirs(directory)
            subprocess.call(["rm", "-rf", directory+'-unfiltered'])
            os.makedirs(directory + '-unfiltered')

    # Start going through results at the index of the number of files already downloaded
    docs = os.listdir(path=directory)
    starting_idx = max(0, len(docs))

    # run the query from sys.args[2] using the number of existing text files as the starting index
    page_generator = util.query_all_document_pages(query, starting_idx, limit)
    locky = Lock()
    for page, cached in page_generator:
        # Start a multiprocessing pool to filter documents concurrently
        def init(l):
            global lock
            lock = l
        pool = Pool(multiprocessing.cpu_count(), initializer=init,initargs=(locky,))
        pool.map(filter_document, page)
        pool.close()
        pool.join()
