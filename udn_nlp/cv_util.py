import cv2 # type: ignore
import os

from udn_nlp import util

def images_from_query(query, flags, delete_after=False, starting_idx=0):
    '''Return a generator that will provide a cv2 image object for each UDN pdf responding to the given query
    '''

    doc_generator = util.query_all_documents(query, starting_idx)

    for doc in doc_generator:
        print(doc['file'])
        file = util.download_file(doc['file'])
        print(file)
        # TODO this is deprecated until a solution without imagemagick is found
        #util.convert_pdf(file, 'temp.jpg')
        #yield cv2.imread('temp.jpg', flags)
        #if delete_after:
            #os.remove(file)

