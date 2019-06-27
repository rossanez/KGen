import os

from argparse import ArgumentParser
from subprocess import Popen
from sys import argv
from sys import stderr

class GraphGenerator:

    def generate(self, turtle_filename, verbose=False):
        if not turtle_filename.startswith('/'):
            turtle_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + turtle_filename

        print('Processing turtle file: {} '.format(turtle_filename))
        return self.__generate_graph(turtle_filename, verbose)

    def __generate_graph(self, turtle_filename, verbose=False):
        if verbose:
            print('Generating graph with Raptor and Graphviz ...')

        filename_base = os.path.splitext(turtle_filename)[0]

        out_png = filename_base + '.png'
        command = 'rapper -i turtle -o dot {} | dot -Tpng -o{}'.format(turtle_filename, out_png)

        if verbose:
            print('rapper | dot commands: {}'.format(command))
        dot_process = Popen(command, stdout=stderr, shell=True)
        dot_process.wait()

        print(dot_process.returncode)
        assert not dot_process.returncode, 'ERROR: Call to rapper | graphviz exited with a non-zero code status.'

        print('Graph generated and stored in: {}'.format(out_png))
        return out_png

def main(args):
    arg_p = ArgumentParser('python generator.py', description='Generates a graph from a turtle file.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Turtle file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    generator = GraphGenerator()
    generator.generate(filename, verbose)

if __name__ == '__main__':
    exit(main(argv))

