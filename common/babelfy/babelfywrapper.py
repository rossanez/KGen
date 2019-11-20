import json
import os
import urllib.parse
import urllib.request

from pybabelfy.babelfy import *

KEY_FILE = 'babelfy.key'

SPARQL_ENDPOINT_URL = "https://babelnet.org"
SPARQL_BASE_ANNOTATOR_PARAMS = "/sparql/?"

class BabelfyWrapper:

    __lang = None
    __key = None

    @staticmethod
    def frag(semantic_annotation, input_text):
        start = semantic_annotation.char_fragment_start()
        end = semantic_annotation.char_fragment_end()

        return input_text[start:end+1]

    def __init__(self, language='EN'):
        self.__lang = language
        self.__key = self.__getKey()

        self.__babelapi = Babelfy()

    def __getKey(self):
        local_path = os.path.dirname(os.path.abspath(__file__))
        key_file = local_path + '/' + KEY_FILE

        with open(key_file, 'r') as key:
            value = key.read()
            key.close()

        return value.strip()

    def annotate(self, text, annType="ALL"):
        return self.__babelapi.disambiguate(text, self.__lang, self.__key, match="EXACT_MATCHING", cands="TOP", mcs="ON", anntype=annType)

    def query(self, query_str=None):
        if query_str is None:
            query_str = 'SELECT ?s ?p ?o WHERE { ?s ?p ?o . } LIMIT 10'

        params = SPARQL_BASE_ANNOTATOR_PARAMS
        params += "query=" + urllib.parse.quote(query_str) + "&"
        params += "key=" + urllib.parse.quote(self.__key) + "&"
        params += "format=" + urllib.parse.quote("application/sparql-results+json")

        url = SPARQL_ENDPOINT_URL + params
        opener = urllib.request.build_opener()
        return json.loads(opener.open(url).read())
