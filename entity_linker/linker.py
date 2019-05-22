import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper
from common.ncbo.ncbowrapper import NCBOWrapper

class Linker:

    def link(self, input_filename, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        with open(input_filename, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for entities, concepts and their links ...')

        linked = {}
        linked.update(self.__babelfy(contents, verbose))

        output_filename = os.path.splitext(input_filename)[0] + '_links.txt'
        open(output_filename, 'w').close() # Clean the file in case it exists

        with open(output_filename, 'a') as output_file:
            for key in linked.keys():
                output_file.write(key + ';' + linked[key] + '\n')
            output_file.close()
        print('Linked entities and concepts were stored at {}'.format(output_filename))

        return output_filename

    def __babelfy(self, contents, verbose=False):
        babelfy = BabelfyWrapper()
        disambiguated = babelfy.disambiguate(contents)

        links = {}
        for disambiguation in disambiguated:
            entity = BabelfyWrapper.frag(disambiguation, contents)
            uri = disambiguation.babelnet_url()#disambiguation.babel_synset_id()#

            if verbose:
                print('Mapped "{}" to {}'.format(entity, uri))
                disambiguation.pprint()
            links[entity] = uri

        return links

    def __ncbo(self, contents, verbose=False):
        ncbo = NCBOWrapper()
        annotated = ncbo.annotate(contents)

        print(annotated)

        return None

def main(args):
    arg_p = ArgumentParser('python linker.py', description='Links the text entities to URIs from a knowledge base.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

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
