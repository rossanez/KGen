import csv
import itertools
import os

from nltk import ngrams
from nltk.tokenize import word_tokenize
from sys import path
from Levenshtein.StringMatcher import StringMatcher

path.insert(0, '../')
from common.nlputils import NLPUtils

CSO_FILENAME = 'CSO.3.2.csv'

CSO_CONTRIBUTESTO = '<http://cso.kmi.open.ac.uk/schema/cso#contributesTo>'
CSO_PREFERENTIALDEQUIVALENT = '<http://cso.kmi.open.ac.uk/schema/cso#preferentialEquivalent>'
CSO_RELATEDEQUIVALENT = '<http://cso.kmi.open.ac.uk/schema/cso#relatedEquivalent>'
CSO_SUPERTOPICOF = '<http://cso.kmi.open.ac.uk/schema/cso#superTopicOf>'
OWL_SAMEAS = '<http://www.w3.org/2002/07/owl#sameAs>'
RDF_TYPE = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'
RDFS_LABEL = '<http://www.w3.org/2000/01/rdf-schema#label>'
SCHEMA_RELATEDLINK = '<http://schema.org/relatedLink>'

class CSOWrapper:

    def __init__(self):
        self.min_similarity = 0.94
        self.key_stems = dict()

        self.__load_ontology_from_file__()

    def __load_ontology_from_file__(self):
        local_path = os.path.dirname(os.path.abspath(__file__))
        cso_file_abspath = local_path + '/' + CSO_FILENAME

        with open(cso_file_abspath, 'r') as file:
            ontology = csv.reader(file, delimiter=',', quotechar='"')

            self._links = {}
            for triple in ontology:
                if triple[1] == RDFS_LABEL:
                    value = triple[2][:-5] # strip the "@en ." at the end
                    uri = triple[0].replace('>', '').replace('<', '')

                    self._links[value] = uri

            for key in self._links.keys():
                if key[:4] not in self.key_stems:
                    self.key_stems[key[:4]] = list()
                self.key_stems[key[:4]].append(key)

    def __get_ngrams__(self, concept):
        for n in range(3, 0, -1):
            pos = 0
            for ng in ngrams(word_tokenize(concept, preserve_line=True), n):
                yield {"position": pos, "size": n, "ngram": ng}
                pos += 1

    def find_matches(self, candidates, verbose=False):
        if verbose:
            print('Searching for matches')

        found_topics = dict()

        for candidate in candidates:
            matched_trigrams = set()
            matched_bigrams = set()
            for comprehensive_grams in self.__get_ngrams__(candidate):
                position = comprehensive_grams["position"]
                size = comprehensive_grams["size"]
                grams = comprehensive_grams["ngram"]
                # if we already matched the current token to a topic, don't reprocess it
                if size <= 1 and (position in matched_bigrams or position-1 in matched_bigrams):
                    continue
                if size <= 2 and (position in matched_trigrams or position-1 in matched_trigrams or position-2 in matched_trigrams):
                    continue
                # otherwise unsplit the ngram for matching so ('quick', 'brown') => 'quick brown'
                gram = ' '.join(grams)
                if verbose:
                    print(gram)

                try:
                    # if there isn't an exact match on the first 4 characters of the ngram and a topic, move on
                    #topic_block = [key for key, _ in self.cso.topics.items() if key.startswith(gram[:4])]
                    topic_block = self.key_stems[gram[:4]]
                except KeyError:
                    continue

                for topic in topic_block:
                    # otherwise look for an inexact match
                    match_ratio = StringMatcher(None, topic, gram).ratio()
                    if match_ratio >= self.min_similarity:
                        #try:
                        #    # if a 'primary label' exists for the current topic, use it instead of the matched topic
                        #    topic = self.cso.primary_labels[topic]
                        #except KeyError:
                        #    pass
                        # note the tokens that matched the topic and how closely
                        if gram in found_topics:
                            current_similarity = found_topics[gram]['similarity']
                            if current_similarity >= match_ratio:
                                continue

                        found_topics[gram] = {'matched': topic, 'similarity': match_ratio}
                        # don't reprocess the current token
                        if size == 2: matched_bigrams.add(position)
                        elif size == 3: matched_trigrams.add(position)

        return found_topics

    def annotate(self, contents, verbose=False):
        candidates = NLPUtils.extract_candidate_entities(contents, grammar=False, stopwords=True).union(NLPUtils.extract_candidate_relations(contents))

        matches = self.find_matches(candidates, verbose)
        annotations = list()
        for match in matches:
            annotations.append({'instance': match, 'link': self._links[matches[match]['matched']]})

        return annotations
