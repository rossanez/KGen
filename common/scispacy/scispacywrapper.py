import scispacy
import spacy

from collections import OrderedDict, Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from scispacy.abbreviation import AbbreviationDetector
from scispacy.umls_linking import UmlsEntityLinker
from spacy import displacy

class ScispaCyWrapper:

    __model = None

    def __init__(self):
        self.__model = 'en_core_sci_lg'

    def resolve_abbreviations(self, text, verbose=False):
        abbrev_refs = self.__detect_abbreviations(text, verbose)
        print(text)

        resolved_contents = ''
        for sentence in sent_tokenize(text):
            for token in word_tokenize(sentence):
                if token in abbrev_refs:
                    resolved_contents += abbrev_refs[token] + ' '
                else:
                    resolved_contents += token + ' '

        print(abbrev_refs)
        for key in abbrev_refs:
            resolved_contents = resolved_contents.replace('{} ( {} )'.format(abbrev_refs[key], abbrev_refs[key]), abbrev_refs[key])

        return resolved_contents

    def __detect_abbreviations(self, text, verbose=False):
        if verbose:
            print('Serching for abbreviations using scispaCy')

        nlp = spacy.load(self.__model)
        abbreviation_pipe = AbbreviationDetector(nlp)
        nlp.add_pipe(abbreviation_pipe)

        doc = nlp(text)

        abbrev_refs = {}
        for abbrv in doc._.abbreviations:
            reference = abbrv._.long_form

            if verbose:
                print('- {} : {}'.format(abbrv, reference))

            abbrev_refs[abbrv] = reference

        return abbrev_refs
