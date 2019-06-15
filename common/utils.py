from stanfordcorenlp.corenlpwrapper import CoreNLPWrapper

class Utils:

    PUNCTUATION = ['.', ',', ':', ';']

    @staticmethod
    def remove_punctuation(contents):
        # This seems like a major overhead, maybe there is a better way...
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos'})

        resolved = ''
        for sentence in annotated['sentences']:
            for token in sentence['tokens']:
                if token['pos'] in Utils.PUNCTUATION or token['pos'] == 'POS':
                    resolved = resolved.strip()

                resolved += token['word'] + ' '

            resolved = resolved.strip()
            resolved += '\n'

        return resolved.strip()

