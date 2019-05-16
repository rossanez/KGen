import os

from argparse import ArgumentParser
from subprocess import Popen
from sys import argv
from sys import stderr

class GraphGenerator:

    def generate(self, triples_filename, verbose=False):
        if not triples_filename.startswith('/'):
            triples_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + triples_filename

        with open(triples_filename, 'r') as input_file:
            triples = input_file.readlines()
            input_file.close()

        print('Processing triples from {} \nPlease wait, as it may take a while ...'.format(triples_filename))
        entity_relations = self.__process_entity_relations(triples, verbose)
        self.__generate_graphviz_graph(entity_relations, triples_filename, verbose)

    def __process_entity_relations(self, entity_relations_str, verbose=False):
        entity_relations = list()

        for string in entity_relations_str:
            str = string[string.find("(") + 1:string.find(")")].split(';')
            entity_relations.append(str)

        return entity_relations

    def __generate_graphviz_graph(self, entity_relations, triples_filename, verbose=False):
        """digraph G {
        # a -> b [ label="a to b" ];
        # b -> c [ label="another label"];
        }"""
        graph = list()
        graph.append('digraph {')
        for er in entity_relations:
            graph.append('"{}" -> "{}" [ label="{}" ];'.format(er[0], er[2], er[1]))
        graph.append('}')

        filename_base = os.path.splitext(triples_filename)[0]

        out_dot = filename_base + '_kg.dot'
        with open(out_dot, 'w') as output_file:
            output_file.writelines(graph)

        out_png = filename_base + '_kg.png'
        command = 'dot -Tpng {} -o {}'.format(out_dot, out_png)

        if verbose:
            print('Executing dot command: {}'.format(command))
        dot_process = Popen(command, stdout=stderr, shell=True)
        dot_process.wait()

        print(dot_process.returncode)
        assert not dot_process.returncode, 'ERROR: Call to dot exited with a non-zero code status.'

        print('KG generated and stored in: {} and {}'.format(out_dot, out_png))

def main(args):
    arg_p = ArgumentParser('python graphgen.py', description='Generates a graph from a set of triples.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Triples file')
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

