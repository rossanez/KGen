import json
import os

from argparse import ArgumentParser
from stanfordcorenlp import StanfordCoreNLP
from sys import argv
from sys import path

path.insert(0, '../')
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory

class FactsExtractor:

    def extract_triples(self, input_filename, linkeden_filename=None, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_extracted_triples.txt'
        open(output_filename, 'w').close()

        self.__linkedens = {}
        if not linkeden_filename is None:
            with open(linkeden_filename, 'r') as linkeden_file:
                for line in linkeden_file:
                    reference, uri = line.strip().split(';', 1)
                    self.__linkedens[reference] = uri.strip()

                linkeden_file.close()

        if verbose:
            print('Searching for triples ...')
        output = self.__openie(input_filename, output_filename, verbose)
        print('Extracted triples were stored at {}'.format(output))

        return output

    def __replace_uri(self, term):
        if term.upper() in self.__linkedens:
            return term + ' <' + self.__linkedens[term.upper()] + '>'

        return term

    def __openie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, ner, depparse, parse, openie', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        for sentence in json_output['sentences']:
            for openie in sentence['openie']:
                t_sentnum = sentence['index']

                t_subject = self.__replace_uri(openie['subject'])
                t_relation = self.__replace_uri(openie['relation'])
                t_object = self.__replace_uri(openie['object'])

                with open(output, 'a') as output_file:
                    triple = '{}:({};{};{})'.format(t_sentnum, t_subject, t_relation, t_object)
                    if verbose:
                       print(triple)
                    output_file.write(triple + '\n')
                    output_file.close()

        return output

def main(args):
    arg_p = ArgumentParser('python extractor.py', description='Extracts facts from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-l', '--linkedentities', type=str, default=None, help='Linked entities text file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    linkeden_filename = args.linkedentities
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    extractor = FactsExtractor()
    extractor.extract_triples(filename, linkeden_filename, verbose)

if __name__ == '__main__':
    exit(main(argv))
