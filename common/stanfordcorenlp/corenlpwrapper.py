import json

from corenlpfactory import CoreNLPFactory

class CoreNLPWrapper:

    __corenlp = None

    def __init__(self):
        self.__corenlp = CoreNLPFactory.createCoreNLP()

    def annotate(self, contents, properties):
        if not 'outputFormat' in properties.keys():
            properties.update({'outputFormat': 'json'})

        return json.loads(self.__corenlp.annotate(contents, properties))
