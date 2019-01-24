#! /usr/bin/env python3
# USAGE
# runscript cite [doc-id] [format (default APA)]
# NOTE currently only APA format is supported (with no guarantee of correctness).
# TODO allow full alphabetized bibliography generation?
# TODO copy/paste from terminal -> Google Docs removes formatting

import argparse

parser = argparse.ArgumentParser(description="Print a rich-text citation of the given UDN document.")
parser.add_argument("id", help="ID of a UDN document to generate a citation from.", type=int)
parser.add_argument("format", help="Citation format. Valid options: APA", nargs="?", default="APA")
args = parser.parse_args()

import sys
from udn_nlp import util
from udn_nlp import nlp

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML

print = print_formatted_text

if __name__ == "__main__":
    doc = util.retrieve_document(args.id)

    article_title = doc['articleTitle']
    author_name = ""

    possible_authors = nlp.extract_names(doc['ocr'])
    if len(possible_authors) > 0:
        print("{} names detected in document. Is one of these the author's name?".format(len(possible_authors)))
        i = 1
        for author in possible_authors:
            print("{}. {}".format(i, author))
            i += 1
        author_name = input("Choose a number, leave blank, or type a different name: ")
        try:
            author_name = possible_authors[int(author_name) -1]
        except:
            pass
    else:
        author_name = input("Author's name cannot be detected. Can you find it? ")

    year = doc['year']
    month = doc['month']
    day = doc['day']
    paper = doc['paper']

    if args.format == 'APA':
        citation_html = ""

        if len(author_name.strip()) > 0:
            if author_name.count(" "):
                [first_name, last_name] = author_name.split(" ")
                citation_html += "{}, {}. ".format(last_name, first_name[0])
                # TODO handle cases where name has more than 2 parts
            else:
                mononym = author_name
                citation_html += "{}. ".format(mononym)
        else:
            citation_html += "{}. ".format(article_title)

        citation_html += "({}, {} {}). ".format(year, month, day)
        if len(author_name.strip()) > 0:
            citation_html += "{}. ".format(article_title)
        citation_html += "<i>{}</i>.".format(paper)

        print(HTML(citation_html))
    # TODO implement more formats here