import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper

class Linker:

    def link(self, input_filename, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_annotated_entities.txt'
        open(output_filename, 'w').close()

        if verbose:
            print('Searching for entities ...')
        output = self.__babelfy(input_filename, output_filename, verbose)
        print('Extracted entities were stored at {}'.format(output))

        return output

    def __babelfy(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        babelfy = BabelfyWrapper()
        annotated = babelfy.disambiguate(contents)

        for annotation in annotated:
            entity = BabelfyWrapper.frag(annotation, contents)
            uri = annotation.babel_synset_id()

            if verbose:
                print('Mapped "{}" to {}'.format(entity, uri))
                annotation.pprint()
            with open(output, 'a') as output_file:
                output_file.write(entity + ';' + uri + '\n')
                output_file.close()

        return output

def main(args):
    arg_p = ArgumentParser('python linker.py')
    arg_p.add_argument('-f', '--filename', type=str, default=None)
    arg_p.add_argument('-v', '--verbose', action='store_true')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    linker = Linker()
    linker.link(filename, verbose)

if __name__ == '__main__':
    exit(main(argv))
