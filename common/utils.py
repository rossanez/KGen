import json

from stanfordcorenlp.corenlpfactory import CoreNLPFactory

class Utils:

    PUNCTUATION = ['.', ',', ':', ';']

    @staticmethod
    def remove_punctuation(contents):
        # This seems like a major overhead, maybe there is a better way...
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos', 'outputFormat': 'json'})
        json_output = json.loads(annotated)

        resolved = ''
        for sentence in json_output['sentences']:
            for token in sentence['tokens']:
                if token['pos'] in Utils.PUNCTUATION or token['pos'] == 'POS':
                    resolved = resolved.strip()

                resolved += token['word'] + ' '

            resolved = resolved.strip()
            resolved += '\n'

        return resolved.strip()

