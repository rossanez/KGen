import difflib
import json
import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper
from common.ncbo.ncbowrapper import NCBOWrapper
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory

class Merger:


    def merge(self, triples_filename, links_filename, k_base='babelfy', verbose=False):
        if not triples_filename.startswith('/'):
            triples_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + triples_filename

        if not links_filename.startswith('/'):
            links_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + links_filename

        print('Processing predicates from {}'.format(triples_filename))

        predicated = {}
        prefixed = {}
        entities = {}
        with open(links_filename, 'r') as links_file:
            for line in links_file.readlines():
                if len(line) < 2: continue

                if line.startswith('@prefix'):
                    line_list = line.split()
                    prefix = line_list[1]
                    prefix = prefix[:prefix.rfind(':')]

                    uri = line_list[2]
                    uri = uri[uri.find('<') + 1:uri.find('>')]

                    prefixed.update({uri: prefix})

                else:
                    line_list = line.split(';')
                    entity = line_list[0]
                    links = line_list[1].split(',')
                    entities.update({entity: links})

            links_file.close()

        with open(triples_filename, 'r') as triples_file:
            for line in triples_file.readlines():
                line_lst = line.replace('\"', '').split('\t')
                sentence_number = line_lst[0]
                subject = line_lst[1]
                predicate = line_lst[2]
                object = line_lst[3]

                # First deal with the predicate
                k_bases = k_base.split(',')
                for base in k_bases:
                    if base == 'babelfy':
                        prefixes, predicates = self.__babelfy(self.__get_lemma(predicate), verbose)
                        prefixed.update(prefixes)
                        predicated.update(predicates)
                    elif base == 'ncbo':
                        prefixes, predicates = self.__ncbo(self.__get_lemma(predicate), verbose)
                        prefixed.update(prefixes)
                        predicated.update(predicates)
                    else:
                        raise Exception("Unknown knowledge base!")

                # Then, let us deal with the subject and object
                all_entities = entities.keys()
                subj_closest_matches = difflib.get_close_matches(subject, all_entities)
                obj_closest_matches = difflib.get_close_matches(object, all_entities)
                print('{} pred {}'.format(subj_closest_matches, obj_closest_matches))

            triples_file.close()

        linked_triples = []

        output_filename = os.path.splitext(triples_filename)[0] + '_linked.txt'
        open(output_filename, 'w').close() # Clean the file in case it exists

        with open(output_filename, 'a') as output_file:
            for key in prefixed.keys():
                output_file.write('@prefix {}: <{}> .\n'.format(prefixed[key], key))
            output_file.write('\n\n')

            for triple in linked_triples:
                output_file.write(triple + '\n')
            output_file.close()
        print('Linked entities were stored at {}'.format(output_filename))

        return output_filename

    def __babelfy(self, contents, verbose=False):
        if verbose:
            print('Searching for predicates using the Babelfy base')

        babelfy = BabelfyWrapper()

        prefixes = {'http://babelnet.org/rdf/': 'bn'}
        links = {}

        # TODO: Implement

        return prefixes, links

    def __ncbo(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the NCBO base')

        ncbo = NCBOWrapper()
        results = ncbo.property_search(contents, ontologies='NCIT')

        prefixes = {'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#': 'nci'}
        links = {}
        

        return prefixes, links

    def __get_lemma(self, term):
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(term, properties={'annotators': 'tokenize, ssplit, pos, lemma', 'outputFormat': 'json'})
        json_out = json.loads(annotated)

        for sentence in json_out['sentences']:
            for token in sentence['tokens']:
                print token['lemma']
                return token['lemma'] # should be used for a single term!

def main(args):
    arg_p = ArgumentParser('python merger.py', description='Merges the unlinked triples with the corresponding entities and predicates.')
    arg_p.add_argument('-t', '--triples', type=str, default=None, help='Triples file')
    arg_p.add_argument('-l', '--links', type=str, default=None, help='Links file')
    arg_p.add_argument('-k', '--kgbase', type=str, default='babelfy', help='Knowledge base to be used for predicates, e.g. babelfy (default) or ncbo')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    triples = args.triples
    links = args.links
    kg_base = args.kgbase
    verbose = args.verbose

    if triples is None:
        print('No triples file provided.')
        exit(1)
    if links is None:
        print('No links file provided.')
        exit(1)

    merger = Merger()
    merger.merge(triples, links, kg_base, verbose)

if __name__ == '__main__':
    exit(main(argv))
