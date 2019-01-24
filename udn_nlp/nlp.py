from udn_nlp import util

import nltk # type: ignore
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
import os
import re
from typing import *
import subprocess
from io import StringIO
import pickle
import sys

word_corpus = set([]) # type: Set[str]
with open(os.path.dirname(__file__) + '/words.txt', 'r') as f:
    word_corpus = set([word.strip() for word in f.readlines()])

from nltk.corpus import stopwords # type: ignore    
stop = stopwords.words('english')

def check_mistakes(text):
    # type: (str) -> Dict[str, List[str]]
    ''' Tokenize the given text and sort it into real words and invalid words according to words.txt (derived from Ubuntu usr/share/dict/words file)
    '''
    wrong_words = []
    right_words = []

    # Extract the tokens from the OCR that aren't real words
    with open('mistakes.ignore', 'w') as f:
        f.write('--------------------------------------------\n')
        for token in text.split(' '):
            if len(token) > 0:
                check_token = token

                

                f.write("/{}/ -> ".format(check_token))
                # strip out valid trailing punctuation, and, to be generous, invalid as well :)
                while len(check_token) > 0 and check_token[-1] in ",.;:?-'\"":
                    check_token = check_token[:-1]
                    f.write("/{}/ -> ".format(check_token))

                # corpus is all in lower-case except for proper nouns.
                check_token = check_token.lower()
                f.write("/{}/ -> ".format(check_token))
    
                # double-check the word with the first letter capitalized, so words like Halloween
                # (which are in the corpus capitalized) are not flagged
                uppercase_check_token = ''
                if len(check_token) > 1:
                    uppercase_check_token = check_token[0].upper() + check_token[1:]

                if check_token not in word_corpus and uppercase_check_token not in word_corpus:
                    # numeric tokens MUST pass, or else we will get bugs
                    try:
                        int(token)
                        f.write('NUMERIC; ACCEPTED')
                        right_words.append(token)
                    except:
                        wrong_words.append(token)
                        f.write('NOT A WORD')
                else:
                    right_words.append(token)
                    f.write('IS A WORD')
                f.write('\n')

        return { 'wrong_words': wrong_words, 'right_words': right_words }

internal_delimiter = '|'

def filter_words(text, wrong_words=True, words_to_filter=[], optional_id=""):
    # type: (str, bool, List[str], str) -> Tuple[str, List[str]]
    ''' Filter the given text.
    NOTE If words_to_filter is specified, only those words will be filtered out.
    Otherwise, use wrong_words argument to specify if only valid dictionary words should be retained.) '''

    # ensure the internal delimiter is not present to begin with
    text = text.replace(internal_delimiter, "")

    # ensure no double spaces are present
    while "  " in text:
        text = text.replace("  ", " ")

    # The programmer can directly specify which words should be filtered,
    # or alternatively choose to automatically filter valid/invalid words
    # according to nlp.check_mistakes()
    if len(words_to_filter) == 0:
        if wrong_words:
            words_to_filter = check_mistakes(text)['wrong_words']
        else:
            words_to_filter = check_mistakes(text)['right_words']
    filtered_text = text

    start_idx = 0
    for filter_word in words_to_filter:
        # replace filtered words with delimited expressions so we can process them.
        idx = filtered_text.find(filter_word, start_idx)
        filtered_text = filtered_text[:idx] + '{1}{0}{1}'.format(len(filter_word), internal_delimiter) + filtered_text[idx+len(filter_word):]
        start_idx = idx+1

    stage_2_text = filtered_text


    double_delim = '{0}{0}'.format(internal_delimiter)
    filtered_text = filtered_text.replace(double_delim, '| |')

    stage_3_text = filtered_text
    # Replace sequences of filtered words with the number consecutively
    # filtered (and char count), in brackets.
    while internal_delimiter in filtered_text:
        start_idx = filtered_text.find(internal_delimiter)
        index = start_idx + 1
        end_idx = filtered_text.find(internal_delimiter, index)
        num = 1
        num_chars = 0
        try:
            num_chars = int(filtered_text[index:end_idx])
        except ValueError as e:
            if len(optional_id) > 0:
                print("Exception while filtering document {}".format( optional_id))
            print(str(e))
            print(text)
            print(stage_2_text)
            print(stage_3_text)
            print(filtered_text)
            raise e
        index = end_idx + 1
        while index < len(filtered_text):
            next_char = filtered_text[index]
            if next_char == " ":
                index += 1
                continue
            if next_char == internal_delimiter:
                num += 1
                index += 1
                end_idx = filtered_text.find(internal_delimiter, index+1)
                try:
                    num_chars += int(filtered_text[index:end_idx])
                except ValueError as e:
                    if len(optional_id) > 0:
                        print("Exception while filtering document {}".format( optional_id))
                    print(str(e))
                    print(text)
                    print(stage_3_text)
                    print(filtered_text)
                    raise e
                index = end_idx + 1
            elif next_char == " ":
                index += 1
            else:
                break

        filtered_text = filtered_text[:start_idx] + " [{};{}] ".format(num, num_chars) + filtered_text[index:]
        while '  ' in filtered_text:
            filtered_text=filtered_text.replace('  ', ' ')
        if filtered_text[0] == ' ':
            filtered_text = filtered_text[1:]

    return (filtered_text, words_to_filter)

def generate_nltk_text_from_doc(document_id):
    # type: (int) -> Any
    ''' Create an nltk.Text object from the OCR contents of the given document.
    '''
    doc = util.retrieve_document(document_id)
    return nltk.Text(filter_words(doc['ocr'])[0].split(" ")) 
####################################################
# Functions for building corpora.
# TODO These should accept arguments for corpus name and path to create at, etc.
# TODO If example_limit is 0, take ALL examples

def build_corpus_from_query(api_query, example_limit = 100):
    # TODO refactor this functionality out of build-corpus.py
    pass

def build_nltk_corpus_from_type(document_type, example_limit=100):
    ''' Generate an nltk corpus from a large sample of documents with
    the given type in the UDN archive '''
    # TODO
    pass

def build_nltk_corpus_from_search(search_phrase, example_limit=100):
    # TODO
    pass

####################################################

####################################################
# Functions for opening and analyzing corpora

def corpus_reader(corpus_name):
    ''' Open a PlaintextCorpusReader for the given UDN corpus.
    '''
    # If the user requested an unfiltered corpus version, we need to know the root corpus name
    root_corpus = corpus_name.replace('-unfiltered', '')

    # Ensure the desired corpus's submodule is checked out
    if not os.path.exists('./corpora/{}/README.md'.format(root_corpus)):
        retcode = subprocess.call("git submodule update --init -- corpora/{}".format(root_corpus).split(" "))
        if retcode != 0:
            print("Attempt to checkout submodule for corpus '{}'. Try running 'git submodule update --init' manually.".format(root_corpus))
            exit()

    percentage = ''
    with open('./corpora/{0}/{0}.txt'.format(root_corpus), 'r') as f:
        manifest = f.readlines()
        query = manifest[0].split(" ")[3]
        num_found = util.dry_make_request(query, 0, 1)[0]['numFound']
        num_in_corpus, last_one = util.files_in_dir('./corpora/{}/{}'.format(root_corpus, corpus_name))
        percentage = '{0:.0%}'.format(num_in_corpus/num_found)
        if percentage != '100%':
            print('NOTE: This corpus is only {} complete. Last file: {}\n'.format(percentage, last_one))

    corpus = PlaintextCorpusReader('./corpora/{}/{}'.format(root_corpus, corpus_name), r'.*\.txt')
    return corpus

def corpus_collocation_list(corpus):
    pickle_file = './.{}-collocations.pkl'.format(corpus)
    if os.path.exists(pickle_file):
        pickled = []
        with open(pickle_file, 'rb') as f:
            try:
                pickled = pickle.load(f)
            except:
                pass
        use_pickled = input('Use pickled collocation list {} (Y/n)?'.format(pickled)).lower() == 'y'
        if use_pickled:
            return pickled

    corpus = corpus_reader(corpus)
    text = nltk.Text(corpus.words())

    # Retrieve collocations by redirecting from stdout until this issue of nltk is fixed: https://github.com/nltk/nltk/issues/2196
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    # TODO skip this part if it's been done before
    text.collocations()    
    collocations = mystdout.getvalue().replace('\n', ' ').split(';')
    for i in range(len(collocations)):
        collocations[i] = collocations[i].strip()

    sys.stdout = old_stdout


    print('Collocations found: ')
    for i in range(len(collocations)):
        print('{}. {}'.format(i+1, collocations[i]))

    which = input('Which of these collocations seem like good classifiers? Enter a comma-separated list: ')
    which = [int(c.strip()) for c in which.split(',')]
    collocations = [collocations[i] for i in range(len(collocations)) if which.count(i+1)]
    print(collocations)
    with open(pickle_file, 'wb') as f:
        pickle.dump(collocations, f)
    return collocations


def collocation_match_score(doc, collocations):
    ''' Score a document based on how many matches it has for a set of collocations
    '''
    score = 0
    for collocation in collocations:
        if 'ocr' in doc:
            score += doc['ocr'].count(collocation)
    return score


####################################################

####################################################
# functions based on the following: https://github.com/acrosson/nlp/blob/master/information-extraction.py

def extract_phone_numbers(string):
    # type: (str) -> List[str]
    ''' Search the given text for phone numbers
    '''
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(string)
    return [re.sub(r'\D', '', number) for number in phone_numbers]

def extract_email_addresses(string):
    # type: (str) -> List[str]
    ''' Search the given text for email addresses
    '''
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)

def preprocess(text):
    # type: (str) -> List[str]
    ''' Return a list of sentences without stopwords '''
    text = ' '.join([i for i in text.split() if i not in stop])
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def extract_names(text):
    # type: (str) -> List[str]
    ''' Search the given text for names of individuals
    '''
    # TODO Allow retrieving other types of tagged names, i.e. organizations.
    names = []
    sentences = preprocess(text)
    for tagged_sentence in sentences:
        for chunk in nltk.ne_chunk(tagged_sentence):
            if type(chunk) == nltk.tree.Tree:
                if chunk.label() == 'PERSON':
                    names.append(' '.join([c[0] for c in chunk]))
    return names

####################################################

class UDNText(nltk.Text):
    ''' Specialized nltk Text subclass that handles trimming out meta tokens and ensuring all data is pulled from mostly valid stretches of ocr text. FIXME May return less than num, even if enough are present.
    '''
    # TODO what I was going for may not be possible because Text.collocations() is implemented just to print collocations, not return them in a collection. Maybe redirect the output to a string, instead of stdout?
    pass