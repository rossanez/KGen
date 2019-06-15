import os

from stanfordcorenlp.corenlpwrapper import CoreNLPWrapper

class Utils:

    PUNCTUATION = ['.', ',', ':', ';']

    @staticmethod
    def adjust_tokens(contents, remove_punctuation=False):
        # This seems like a major overhead, maybe there is a better way...
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos'})

        resolved = ''
        for sentence in annotated['sentences']:
            for token in sentence['tokens']:
                if remove_punctuation and (token['pos'] in Utils.PUNCTUATION or (token['index'] == 1 and token['pos'] == 'DT')):
                    continue

                if token['pos'] in Utils.PUNCTUATION or token['pos'] == 'POS':
                    resolved = resolved.strip()

                resolved += token['word'] + ' '

            resolved = resolved.strip()
            resolved += '\n'

        return resolved.strip()

    @staticmethod
    def generate_tsv_file(self, contents, linked, input_filename):
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner'})

        tsv_filename = os.path.splitext(input_filename)[0] + '_ner.tsv'
        open(tsv_filename, 'w').close() # Clean the file in case it exists

        with open(tsv_filename, 'a') as tsv_file:
            for sentence in annotated['sentences']:
                for token in sentence['tokens']:
                   tk = token['ner']
                   if tk == 'O' and token['word'].upper() in linked:
                       tk = 'MISC'
                   tsv_file.write(token['word'] + '\t' + tk + '\n')
        tsv_file.close()
        print('TSV file has been stored at {}'.format(tsv_filename))

        return tsv_filename

