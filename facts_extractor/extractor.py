import json
import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory
from common.clausie.clausiewrapper import ClausIEWrapper

class FactsExtractor:

    def extract_triples(self, input_filename, openie='stanford', verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_triples.txt'
        open(output_filename, 'w').close()

        if openie == 'clausie':
            output = self.__clausie(input_filename, output_filename, verbose)
        elif openie == 'stanford':
            output = self.__stanford_openie(input_filename, output_filename, verbose)
        else:
            raise Exception("Unknown openie system!")

        print('Extracted triples were stored at {}'.format(output))

        return output

    def __stanford_openie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for triples using Stanford OpenIE ...')

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, ner, depparse, parse, openie', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        for sentence in json_output['sentences']:
            for openie in sentence['openie']:
                with open(output, 'a') as output_file:
                    triple = '{}\t"{}"\t"{}"\t"{}"'.format(sentence['index'], openie['subject'], openie['relation'], openie['object'])
                    if verbose:
                       print(triple)
                    output_file.write(triple + '\n')
                    output_file.close()

        return output

    def __clausie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for triples using ClausIE ...')

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        input_clausie = os.path.splitext(input)[0] + '_clausie_input.txt'
        open(input_clausie, 'w').close()

        print('Preparing contents to be processed by ClausIE at {}'.format(input_clausie))

        for sentence in json_output['sentences']:
            sent_str = ''
            for token in sentence['tokens']:
                if token['pos'] == 'POS':
                    sent_str.strip()

                sent_str += token['word'] + ' '

            with open(input_clausie, 'a') as clausie_file:
                clausie_file.write(str(sentence['index']) + '\t' + sent_str.strip() + '\n')
                clausie_file.close()

        return ClausIEWrapper.run_clausie(input_clausie, output, verbose)

def main(args):
    arg_p = ArgumentParser('python extractor.py', description='Extracts facts from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-o', '--openie', type=str, default='stanford', help='Specify the openie system, e.g. stanford (default), clausie')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    openie = args.openie
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    extractor = FactsExtractor()
    extractor.extract_triples(filename, openie, verbose)

if __name__ == '__main__':
    exit(main(argv))
