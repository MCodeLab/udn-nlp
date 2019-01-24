#! /usr/bin/env python3
# USAGE
# runscript compile-pdf [outputfile] [query] [start (default 0)] [max (default compile all)]
''' Compile a large PDF by from all scanned documents returned by an API query (or all document IDs listed in a text file)
'''

from pdfrw import PdfReader, PdfWriter

import argparse
import itertools
parser = argparse.ArgumentParser(description='Compile a large PDF by from all scanned documents returned by an API query.')
parser.add_argument('outputfile', help='file to save the result in')
parser.add_argument('query_or_path', help='a UDN API query to view documents from, or a local text file containing doc IDs on newlines')
parser.add_argument('max', help='number of documents to compile together', nargs="?", default=-1, type=int)
parser.add_argument('start', help='Number of documents from the query to skip.', nargs="?", default=0, type=int)
args = parser.parse_args()

import sys
from udn_nlp import util
import webbrowser

doc_generator = util.query_all_documents(args.query_or_path)

# Skip to the starting index
for doc in itertools.islice(doc_generator, args.start):
    pass

# Cap the number of documents
if args.max > 0:
    doc_generator = itertools.islice(doc_generator, args.max)

# Download every document's pdf
paths = [util.download_file(doc['file']) for doc in doc_generator]
    

# Concatenate them all into one pdf This part uses the same functionality as pdfrw's example cat script:

# https://github.com/pmaupin/pdfrw/blob/6c892160e7e976b243db0c12c3e56ed8c78afc5a/examples/cat.py

writer = PdfWriter()
for path in paths:
    try:
        writer.addpages(PdfReader(path).pages)
    except:
        print('Warning: {} is an empty pdf path'.format(path))

writer.write(args.outputfile)