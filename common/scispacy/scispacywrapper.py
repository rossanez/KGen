import scispacy
import spacy

from collections import OrderedDict
from nltk.tokenize import sent_tokenize, word_tokenize
from scispacy.abbreviation import AbbreviationDetector
from scispacy.umls_linking import UmlsEntityLinker
from spacy import displacy

class ScispaCyWrapper:

    __model = None

    def __init__(self):
        self.__model = 'en_core_sci_lg'

    def detect_entities(self, text, verbose=False):
        if verbose:
            print('Detecting named entities using scispaCy.')

        nlp = spacy.load(self.__model)
        doc = nlp(text)

        return set([(X.text, X.label_) for X in doc.ents])

    def link_entities_with_umls(self, text, verbose=False)
        if verbose:
            print('Detecting named entities and linking them with UMLS, using scispaCy.')

        nlp = spacy.load(self.__model)
        umls_linker = UmlsEntityLinker(k=10, max_entities_per_mention=2)
        nlp.add_pipe(umls_linker)
        doc = nlp(text)

        entities = [str(item) for item in doc.ents]
        entities = str(OrderedDict.fromkeys(entities))
        entities = nlp(entities).ents

        if verbose:
            for entity in entities:
                for umls_ent in entity._.umls_ents:
                    print("Entity Name:" ,entity)
                    Concept_Id, Score = umls_ent
                    print('Concept_Id = {} Score = {}'.format(Concept_Id,Score))
                    print(linker.umls.cui_to_entity[umls_ent[0]])

        return entities

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
