import scispacy
import spacy

from nltk.tokenize import sent_tokenize, word_tokenize
from scispacy.abbreviation import AbbreviationDetector
from scispacy.umls_linking import UmlsEntityLinker
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span

class ScispaCyWrapper:

    __model = None

    def __init__(self):
        self.__model = 'en_core_sci_lg'

    def detect(self, text, detect_relations=False, resolve_abbreviations=False, link_with_umls=False, verbose=False):
        if verbose:
            print('-- Will detect named entities using scispaCy.')
            if detect_relations:
                print('-- Will search for relations.')
            if resolve_abbreviations:
                print('-- Will search for abbreviations.')
            if link_with_umls:
                print('-- Will search for UMLS matches.')

        nlp = spacy.load(self.__model)
        if link_with_umls:
            umls_linker = UmlsEntityLinker(k=10, max_entities_per_mention=1)
            nlp.add_pipe(umls_linker)
        if resolve_abbreviations:
            abbrev_detector = AbbreviationDetector(nlp)
            nlp.add_pipe(abbrev_detector)

        doc = nlp(text)

        # Named Entities Detected:
        ner = set([X.text for X in doc.ents])
        if verbose:
            print('Named Entities detected: {}'.format(ner))

        relations = set()
        if detect_relations:
            matcher = Matcher(nlp.vocab)
            pattern = [{'DEP':'ROOT'},
                       {'DEP':'prep','OP':"?"},
                       {'DEP':'agent','OP':"?"},
                       {'POS':'ADJ','OP':"?"}]
            matcher.add("matching_1", None, pattern)

            for sentence in sent_tokenize(text):
                matches = matcher(doc)
                k = len(matches) - 1
                span = doc[matches[k][1]:matches[k][2]]

                relations.add(span.text)

            if verbose:
                print('Relations detected: {}'.format(relations))

        abbrev_refs = {}
        if resolve_abbreviations:
            for abbrv in doc._.abbreviations:
                reference = abbrv._.long_form

                if verbose:
                    print('- {} : {}'.format(abbrv, reference))

                abbrev_refs[abbrv] = reference

            if verbose:
                print('Abbreviations detected: {}'.format(abbrev_refs))

            #TODO implement resolution (i.e. replace detected abbreviations)

        linked = {}
        if link_with_umls:
            if verbose:
                print('Serching for UMLS entities...')

            entities = str(ner.union(relations))
            entities = nlp(entities).ents

            for entity in entities:
                for umls_ent in entity._.umls_ents:
                    Concept_Id, Score = umls_ent

                    if verbose:
                        print("Entity Name:" ,entity)
                        print('Concept_Id = {} Score = {}'.format(Concept_Id, Score))
                        umls_entity = umls_linker.umls.cui_to_entity[Concept_Id]
                        print(umls_entity)

                    if not entity.text in linked: # greater scores are shown first, so no need to add smaller scores.
                        linked[entity.text] = 'sameas\tumls:{}\t{}'.format(Concept_Id, umls_entity.canonical_name)
                        break

            if verbose:
                print('UMLS concepts: {}'.format(linked))

        return ner, relations, linked

