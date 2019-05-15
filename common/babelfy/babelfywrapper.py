import os

from pybabelfy.babelfy import *

KEY_FILE = 'babelfy.key'

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

    def disambiguate(self, text):
        return self.__babelapi.disambiguate(text, self.__lang, self.__key, match="PARTIAL_MATCHING",cands="TOP",mcs="ON",anntype="ALL")
