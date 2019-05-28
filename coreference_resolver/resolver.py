import json
import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory

class CorefResolver:

    def resolve(self, input_filename, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {}'.format(input_filename))

        resolved_contents = self.__coref(input_filename, verbose)

        output_filename = os.path.splitext(input_filename)[0] + '_resolved.txt'
        with open(output_filename, 'w') as output_file:
            output_file.write(resolved_contents)
            output_file.close()

        print('Resolved coreferences were stored at {}'.format(output_filename))

        return output_filename

    def __coref(self, input, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Resolving coreferences with Stanford corefs annotator.')
        print('Please wait, as it may take a while ...')

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, parse, coref', 'coref.algorithm': 'neural', 'coref.neural.greedyness': '0.51', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        return self.__rebuild_contents(json_output['sentences'], self.__eval_corefs(json_output['corefs'], verbose))

    def __eval_corefs(self, json_corefs, verbose=False):
        corefs = {}

        for k, chain in json_corefs.items():
            if len(chain) > 1:
                if verbose:
                    print('Chain key: {}'.format(k))

                for r in chain:
                    if r['isRepresentativeMention']:
                        if verbose:
                            print('- Representative: {} - {}[{} {}]'.format(r['text'], r['sentNum'], r['startIndex'], r['endIndex']))

                        representative = r['text']

                for m in chain:
                    if not m['isRepresentativeMention']:
                        if verbose:
                            print('-- mention: {} - {}[{} {}]'.format(m['text'], m['sentNum'], m['startIndex'], m['endIndex']))

                        corefs['{}:{},{}'.format(m['sentNum'], m['startIndex'], m['endIndex'])] = representative.strip()

        return corefs

    def __replace(self, s_index, token, corefs):
        t_index = token['index']

        for key in corefs.keys():
            if key.startswith(str(s_index) + ':'):
                s, coref_range = key.strip().split(':', 1)
                coref_range_start, coref_range_end = coref_range.strip().split(',', 1)

                if t_index in range(int(coref_range_start), int(coref_range_end)):

                    if t_index == int(coref_range_start):
                        return corefs[key]

                    return ''

        return None

    def __rebuild_contents(self, json_sentences, corefs):
        resolved = ''
        s_index = 0
        for sentences in json_sentences:
            s_index += 1
            for token in sentences['tokens']:
                replacement = self.__replace(s_index, token, corefs)

                if replacement is None:
                    resolved += token['word'] + ' '
                elif not replacement is '':
                    resolved += replacement + ' '

        return resolved

def main(args):
    arg_p = ArgumentParser('python resolver.py', description='Resolve coreferences from an unstructured text.')
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
