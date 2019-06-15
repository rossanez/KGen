import os

from argparse import ArgumentParser
from sys import argv
from sys import path

from corefresolver import CorefResolver
from abbrevresolver import AbbrevResolver

path.insert(0, '../')
from common.utils import Utils

class Preprocessor:

    def preprocess(self, input_filename, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {}'.format(input_filename))
        with open(input_filename, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        coref_resolver = CorefResolver(contents)
        abbrev_resolver = AbbrevResolver(coref_resolver.resolve(verbose))
        resolved_contents = Utils.remove_punctuation(abbrev_resolver.resolve(verbose))

        output_filename = os.path.splitext(input_filename)[0] + '_preprocessed.txt'
        with open(output_filename, 'w') as output_file:
            output_file.write(resolved_contents)
            output_file.close()

        print('Preprocessed text stored at {}'.format(output_filename))

        return output_filename

def main(args):
    arg_p = ArgumentParser('python preprocessor.py', description='Preprocess an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    preprocessor = Preprocessor()
    preprocessor.preprocess(filename, verbose)

if __name__ == '__main__':
    exit(main(argv))

