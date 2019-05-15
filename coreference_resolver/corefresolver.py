import json
import os

from argparse import ArgumentParser
from stanfordcorenlp import StanfordCoreNLP
from sys import argv
from sys import path

path.insert(0, '../')
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory

class CorefResolver:

    def resolve(self, input_filename, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_coreferences.txt'
        open(output_filename, 'w').close()

        if verbose:
            print('Resolving coreferences ...')
        output = self.__dcoref(input_filename, output_filename, verbose)
        print('Resolved coreferences were stored at {}'.format(output))

        return output

    def __dcoref(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, parse, dcoref', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        for k, mentions in json_output['corefs'].items():
            simplified_mentions = ''
            for m in mentions:
#                simplified_mentions(m['sentNum'], m['startIndex'], m['endIndex'], m['text']))
                simplified_mentions += '{}:{};'.format(m['sentNum'] -1, m['text']) # Sentence numbers are one-based

            if verbose:
                print(simplified_mentions)
            with open(output, 'a') as output_file:
                output_file.write(simplified_mentions + '\n')
                output_file.close()

        return output

def main(args):
    arg_p = ArgumentParser('python corefresolver.py', description='Resolve coreferences from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    coref = CorefResolver()
    coref.resolve(filename, verbose)

if __name__ == '__main__':
    exit(main(argv))
