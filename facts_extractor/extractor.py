import os

from argparse import ArgumentParser
from sys import argv
from sys import path

from openie import OpenIE
from srl import SemanticRoleLabeler
from secondary import SecondaryFactsExtractor

class FactsExtractor:

    def extract_triples(self, input_filename, primary='stanford', secondary=False, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_triples.txt'
        open(output_filename, 'w').close()

        if primary in ['senna']:
            output = SemanticRoleLabeler().extract(input_filename, output_filename, verbose)
        elif primary in ['stanford', 'clausie']:
            output = OpenIE(primary).extract(input_filename, output_filename, verbose)
        else:
            raise Exception("Unknown system/method to extract primary facts!")

        if secondary:
            output = SecondaryFactsExtractor().extract(input_filename, output_filename, verbose)

        print('Extracted triples were stored at {}'.format(output))

        return output

def main(args):
    arg_p = ArgumentParser('python extractor.py', description='Extracts facts from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-p', '--primary', type=str, default='stanford', help='Specify system/method to extract the primary facts: stanford (default), clausie, or senna')
    arg_p.add_argument('-s', '--secondary', action='store_true', help='Attempt to retrieve secondary facts')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    primary = args.primary
    secondary = args.secondary
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    extractor = FactsExtractor()
    extractor.extract_triples(filename, primary, secondary, verbose)

if __name__ == '__main__':
    exit(main(argv))

