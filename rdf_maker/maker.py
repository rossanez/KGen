import difflib
import json
import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory

class RDFMaker:


    def make(self, triples_filename, links_filename, verbose=False):
        if not triples_filename.startswith('/'):
            triples_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + triples_filename

        if not links_filename.startswith('/'):
            links_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + links_filename

        print('Processing predicates from {}'.format(triples_filename))

        predicates = {}
        prefixed = {}
        entities = {}
        with open(links_filename, 'r') as links_file:
            for line in links_file.readlines():
                if len(line) < 2: continue

                if line.startswith('@PREFIX'):
                    line_list = line.split()
                    prefix = line_list[1]
                    prefix = prefix[:prefix.rfind(':')]

                    uri = line_list[2]
                    uri = uri[uri.find('<') + 1:uri.find('>')]

                    prefixed.update({uri: prefix})

                elif line.startswith('@PREDICATE'):
                    line_list = line.split()
                    line = ' '.join(line_list[1:])

                    line_list = line.split(';')
                    predicate = line_list[0]
                    link = line_list[1]
                    predicates.update({predicate: link})

                elif line.startswith('@ENTITY'):
                    line_list = line.split()
                    line = ' '.join(line_list[1:])

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

                #TODO implement!
                
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

def main(args):
    arg_p = ArgumentParser('python maker.py', description='Merges the unlinked triples with the corresponding entities and predicates.')
    arg_p.add_argument('-t', '--triples', type=str, default=None, help='Triples file')
    arg_p.add_argument('-l', '--links', type=str, default=None, help='Links file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    triples = args.triples
    links = args.links
    verbose = args.verbose

    if triples is None:
        print('No triples file provided.')
        exit(1)
    if links is None:
        print('No links file provided.')
        exit(1)

    maker = RDFMaker()
    maker.make(triples, links, verbose)

if __name__ == '__main__':
    exit(main(argv))
