from  urllib.request import urlopen
import sys
import requests
import subprocess
import os
import errno
import datetime
import requests_cache # type: ignore
from typing import *

request_root = 'https://api.lib.utah.edu/udn/v1/'
dir_path = os.path.dirname(os.path.realpath(__file__))


# Cache UDN requests without expiry by default because UDN documents are
# never updated as far as I know
requests_cache.install_cache('udn_requests', backend='sqlite')

def is_windows():
    # type: () -> bool
    return os.name == 'nt'

def is_linux():
    # type: () -> bool
    return os.name == 'posix'

def call_console(command, use_shell=True):
    print('Calling command: ' + command)

    if is_linux():
        print(subprocess.check_output(command, executable='/bin/bash', shell=use_shell))
    else:
        print(subprocess.check_output(command, shell=use_shell))

def retrieve_document(id):
    # type: (int) -> Dict
    ''' Retrieve the json data of the document with the given id
    '''
    response, _ = dry_make_request('docs/id/{}'.format(id))
    if 'docs' in response and len(response['docs']) == 1:
        return response['docs'][0]
    else:
        raise BaseException('There is no document with id {}'.format(id))

def open_file_make_dirs(filename, access_type):
    # type: (str, str) -> IO
    ''' Open a file from the local disk, creating directories for
    every folder in its path that doesn't exist
    '''

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    return open(filename, access_type)

def global_dest_for_webfile(url):
    # type: (str) -> str
    ''' Parse out a local path to save a file from the internet.
    '''
    filename = url[url.rfind("/")+1:]

    return os.path.expanduser('~') + "/ocr-temp/" + filename

def download_file(url, dest=""):
    # type: (str, str) -> str
    ''' Download a file to the given location. Return the local filepath
    '''

    if len(dest) == 0:
        dest = global_dest_for_webfile(url)

    # Don't re-download a file that's already been downloaded
    if not os.path.exists(global_dest_for_webfile(url)):
        print('downloading file from ' + url)

        with open_file_make_dirs(dest, 'wb') as f:
            webfile = urlopen(url)
            f.write(webfile.read())

    return dest

def open_webfile(url, access_type):
    # type: (str, str) -> IO
    ''' Open a file from the internet (downloading if necessary)
    '''
    download_file(url)
    return open(global_dest_for_webfile(url), access_type)

def files_in_dir(dir):
    # type: (str) -> Tuple[int, str]
    ''' Count the files in a directory and return the name of the last one (alphabetically)
    '''
    files = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    return len(files), files[-1]
False
print_on_request = True
def dry_make_request(query, starting_idx=0, limit=100, timeout=0.1):
    # type: (str, int, int) -> Tuple[Dict, bool]
    ''' Convenience function for querying the UDN API. Uses cached responses where possible.
    NOTE returns 2 values: response json, and bool from_cache
    '''
    req = requests.Request('GET', request_root + query, params={
        'sort': 'id|asc',
        'start': starting_idx,
        'limit': limit,
    })
    prepared = req.prepare()
    if print_on_request:
        print('{} {}'.format(prepared.method, prepared.url))

    try:
        with requests.Session() as session:
            response = session.send(prepared,timeout=timeout)
            if print_on_request:
                print("Used Cache: {0}".format(response.from_cache))
            # return a tuple of the response object with whether the query was cached
            # in case a script wants to know if it was already run partially
            return response.json(), response.from_cache
    except BaseException as e:
        if type(e) is KeyboardInterrupt or type(e) is EOFError:
            raise e
        else:
            input("An HTTPS query failed. Check your internet connection and press ENTER to try again.")
            return dry_make_request(query, starting_idx, limit)

def query_all_document_pages(query, starting_idx=0, limit=100):
    # type: (str, int, int) -> Iterator[Tuple[List[Dict], bool]]
    ''' Return a generator that will eventually yield all "pages" of documents
    matching the given UDN query (page = list of 100, the maximum API query).

    Returns pages instead of individual documents in order to be multiprocessing-friendly

    NOTE this returns a second value, cached! Do not ignore it or you may end up iterating through
    the tuple, not the page
    '''
    while True:
        next_batch, cached = dry_make_request(query, starting_idx, limit)

        total_num_found = next_batch['numFound']
        if total_num_found == 0:
            print('No docs respond to query {}'.format(query))
            break

        if len(next_batch['docs']) == 0:
            print('Reached the last page')
            break

        starting_idx+=len(next_batch['docs'])
        yield next_batch['docs'], cached


def query_all_documents(query_or_list_file, starting_idx=0, limit=100):
    # type: (str, int, int) -> Iterator[Dict]

    ''' Generator that will eventually yield every document matching the given UDN query, OR every document whose ID is listed in a given text file
    NOTE limit is max 100, and the generator will slow down to query the next page every time it reaches the limit.
    '''

    last_id = 0
    docs_yielded = 0

    if os.path.exists(query_or_list_file):
        # If this function is called with the path to a file listing document IDs, query every document listed in the file
        doc_list = open(query_or_list_file, 'r').readlines()
        for doc_id in doc_list[starting_idx:]:
            yield retrieve_document(doc_id.strip())
    else:
        # Otherwise, this function must be called with a valid UDN query. Iterate through pages of results and return documents
        query = query_or_list_file
        dummy_batch, _ = dry_make_request(query, starting_idx, limit)
        total_docs = dummy_batch['numFound']

        for page, _ in query_all_document_pages(query, starting_idx, limit):
            # print(page)
            # print(len(page))
            for doc in page:
                # print(len(doc))
                # Sanity check for ascending id sort order
                # print(doc['id'])
                if int(doc['id']) < last_id:
                    print('Error! The query {} is not respecting sort order!'.format(query))
                docs_yielded += 1

                # if docs_yielded % 5 == 0:
                    # print('So far, Retrieved {}/{} documents for query {}'.format(docs_yielded, total_docs, query))

                last_id = int(doc['id'])
                yield doc

        if docs_yielded < total_docs:
                print('Query stopped returning docs at {1}  (probably) because you started the query at id {0}. {0} + {1} = {2} '.format(starting_idx, docs_yielded, (starting_idx+docs_yielded)/ total_docs))

def safe_print(document, field, outfile=None, format_str="{}\n"):
    # type: (Dict, str, Optional[IO], str) -> None
    ''' Print a field from a UDN document if it exists.
    format_str can define a structure for the field to be printed in where {} will be replaced with the field's value. For example:
    
    util.safe_print(doc, 'title', format_str = "Title: {}\n")
    '''

    if field in document:
        outstr = format_str.format(document[field])
        if outfile:
            outfile.write(outstr)
        else:
            print(outstr, end="")


def confirm(message):
    y_n = input('{} (Y/n)'.format(message))
    return y_n.lower() == 'y'

def choose_from_list(message):
    # TODO refactor the collocation-classifier int csv parsing here
    pass