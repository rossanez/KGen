from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper

class Linker:

    def link(self, input_filename, verbose=False):
        babelfy = BabelfyWrapper()
        annotated = babelfy.disambiguate('I wonder if this would work')

        for token in annotated:
            token.pprint()

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
