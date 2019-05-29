import json
import os

from argparse import ArgumentParser
from nltk.tree import Tree
from sys import argv
from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper
from common.ncbo.ncbowrapper import NCBOWrapper
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory

class Linker:

    def link(self, input_filename, k_base='babelfy', tsv_file=False, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {}'.format(input_filename))

        with open(input_filename, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        linked = {}
        k_bases = k_base.split(',')
        for base in k_bases:
            if base == 'babelfy':
                linked.update(self.__babelfy(contents, verbose))
            elif base == 'ncbo':
                linked.update(self.__ncbo(contents, verbose))
            else:
                raise Exception("Unknown knowledge base!")

        entities_linked = self.__associate_entities_to_links(self.__extract_np_entities(contents), linked)

        output_filename = os.path.splitext(input_filename)[0] + '_links.txt'
        open(output_filename, 'w').close() # Clean the file in case it exists

        with open(output_filename, 'a') as output_file:
            for key in entities_linked.keys():
                output_file.write(key.encode('utf-8') + ';' + entities_linked[key] + '\n')
            output_file.close()
        print('Linked entities were stored at {}'.format(output_filename))

        if tsv_file:
            self.__gen_tsv_file(contents, linked, input_filename)

        return output_filename

    def __babelfy(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the Babelfy base')

        babelfy = BabelfyWrapper()

        links = {}
        annotated = babelfy.annotate(contents)

        for annotation in annotated:
            entity = BabelfyWrapper.frag(annotation, contents).upper()
            uri = annotation.babelnet_url()#annotation.babel_synset_id()#

            if verbose:
                print('Mapped "{}" to {}'.format(entity, uri))
                annotation.pprint()

            links[entity.lower()] = uri

        return links

    def __ncbo(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the NCBO base')

        ncbo = NCBOWrapper()
        annotated = ncbo.annotate(contents, ontologies='NCIT')

        links = {}
        for annotation in annotated:
            annotated_class = annotation['annotatedClass']
            if not ('prefLabel' in annotated_class and '@id' in annotated_class):
                continue

            pref_label = annotated_class['prefLabel']
            uri = annotated_class['@id']
            ontology = annotated_class['links']['ontology']

            try:
                pref_map_str = '{} \n--Ontology: {} \n--PrefLabel: {}'.format(uri, ontology, pref_label)
            except UnicodeEncodeError:
                continue # NCBO may present some Chinese characters. We will ignore them.

            for class_annotation in annotation['annotations']:
                entity = class_annotation['text']
                preferable_match = class_annotation['matchType'].upper() == 'PREF'

                if preferable_match or not entity in links:
                    if verbose:
                        print('-Mapped "{}" to {} \n--PrefMatch: {}'.format(entity, pref_map_str, preferable_match))

                    links[entity] = uri
                    if preferable_match: break

        return links

    def __extract_np_entities(self, contents):
        print('Determining the ultimate entities. \n Please wait, as it may take a while ...')
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, parse', 'outputFormat': 'json'})

        entity_set = set()
        json_output = json.loads(annotated)
        for sentence in json_output['sentences']:
            parsed_sentence = sentence['parse'].replace('\n', '')
            parse_tree = Tree.fromstring(parsed_sentence)
            for sub_tree in parse_tree.subtrees():
                if sub_tree.label() == 'NP':
                    np_entity = self.__resolve_possessives_and_determiners(' '.join(sub_tree.leaves()))
                    entity_set.add(np_entity)

        return entity_set

    def __resolve_possessives_and_determiners(self, contents):
        # This is a major overhead (and kinda dumb...). Must be reworked!
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos', 'outputFormat': 'json'})
        json_output = json.loads(annotated)

        resolved = ''
        for sentence in json_output['sentences']:
            for token in sentence['tokens']:
                if token['pos'] == 'POS':
                     resolved = resolved.strip()

                resolved += token['word'] + ' '

        return resolved.strip()

    def __associate_entities_to_links(self, entities, links):
        entity_links = {}
        for entity in entities:
            link_list = list()
            for key in links:
                if key.lower() in entity.lower():
                    link_list.append(links[key])

            entity_links[entity.lower()] = ','.join(link_list)

        return entity_links

    def __gen_tsv_file(self, contents, linked, input_filename):
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner', 'outputFormat': 'json'})

        json_output = json.loads(annotated)
        tsv_filename = os.path.splitext(input_filename)[0] + '_ner.tsv'
        open(tsv_filename, 'w').close() # Clean the file in case it exists

        with open(tsv_filename, 'a') as tsv_file:
            for sentence in json_output['sentences']:
                for token in sentence['tokens']:
                   tk = token['ner']
                   if tk == 'O' and token['word'].upper() in linked:
                       tk = 'MISC'
                   tsv_file.write(token['word'] + '\t' + tk + '\n')
        tsv_file.close()
        print('TSV file has been stored at {}'.format(tsv_filename))

        return tsv_filename

def main(args):
    arg_p = ArgumentParser('python linker.py', description='Links the text entities to URIs from a knowledge base.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-k', '--kgbase', type=str, default='babelfy', help='Knowledge base to be used, e.g. babelfy (default) or ncbo')
    arg_p.add_argument('-t', '--tsv', action='store_true', help='Generates *.tsv file for NER model training')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    kg_base = args.kgbase
    tsv_file = args.tsv
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    linker = Linker()
    linker.link(filename, kg_base, tsv_file, verbose)

if __name__ == '__main__':
    exit(main(argv))
