#! /usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description="Attempt to classify documents matching the given corpus's collocations")
parser.add_argument("corpus", help="Corpus to classify against")
parser.add_argument("query_to_classify", help="A UDN query from which to attempt to classify instances that fit the given corpus")
args = parser.parse_args()

import os.path
from io import StringIO
import sys
from udn_nlp import util
from udn_nlp import nlp
import nltk

if __name__ == "__main__":
    collocations = nlp.corpus_collocation_list(args.corpus)

    last_id_checked = 0
    write_mode = 'w'
    done_skipping=True
    if os.path.exists('{}-hits.txt'.format(args.corpus)):
        with open('{}-hits.txt'.format(args.corpus), 'r') as hit_list:
            lines =  hit_list.readlines()
            if len(lines) > 0:
                if util.confirm('Start classifying from last document checked?'):
                    last_id_checked = int(lines[-1])
                    write_mode='a'
                    done_skipping=False


    with open('{}-hits.txt'.format(args.corpus), write_mode) as hit_list:
        # Start applying this classification to unclassified documents
        for doc in util.query_all_documents(args.query_to_classify):
            if int(doc['id']) <= last_id_checked:
                continue

            if not done_skipping:
                print('Done catching up')
                done_skipping = True

            score = nlp.collocation_match_score(doc, collocations)
            if score > 0:
                print('{} scored {}'.format(doc['id'], score))
                hit_list.write('{}\n'.format(doc['id']))