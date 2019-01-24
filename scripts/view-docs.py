#! /usr/bin/env python3
# USAGE
# runscript view-docs [query] [n (default 5) (how many to open at once)] [start (default 0)]
''' Automatically open UDN documents from a query conveniently in the default web browser. (This process is very tedious otherwise.)
'''

import argparse
import itertools
parser = argparse.ArgumentParser(description='Automatically open UDN documents from a query conveniently in the default web browser.')
parser.add_argument('query_or_path', help='a UDN API query to view documents from, or a local text file containing doc IDs on newlines')
parser.add_argument('n', help='number of documents to open at once', nargs="?", default=5, type=int)
parser.add_argument('start', help='Number of documents from the query to skip.', nargs="?", default=0, type=int)
args = parser.parse_args()

import os.path
import sys
from udn_nlp import util
import webbrowser

q_or_p = args.query_or_path
doc_generator = util.query_all_documents(q_or_p, args.start, args.n)

while True:
    doc_remaining = False
    for doc in itertools.islice(doc_generator, 0, args.n):
        doc_remaining = True

        webbrowser.open_new_tab("https://newspapers.lib.utah.edu/details?id={}".format(doc['id']))

    if not doc_remaining:
        break
    else:
        input("Press ENTER when you're ready for {} more documents.".format(args.n))