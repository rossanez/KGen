import os

from argparse import ArgumentParser
from sys import argv
from sys import path

from kb import KnowledgeBases

path.insert(0, '../')
from common.stanfordcorenlp.corenlpwrapper import CoreNLPWrapper
from common.nlputils import NLPUtils

class Linker:

    def link(self, input_filename, k_base='babelfy', umls=False, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {}'.format(input_filename))

        with open(input_filename, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if umls:
            prefixes, entities, relations, links = KnowledgeBases(k_base).query(contents, verbose)
            
        else:
            entities, relations = NLPUtils.extract_np_and_verbs(contents)
            prefixes, links = KnowledgeBases(k_base).annotate(contents, verbose)

        output_filename = os.path.splitext(input_filename)[0] + '_links.txt'
        open(output_filename, 'w').close() # Clean the file in case it exists

        with open(output_filename, 'a') as output_file:
            for key in prefixes.keys():
                output_file.write('@PREFIX\t{}:\t<{}>\t\n'.format(prefixes[key], key))

            for key in relations:
                if key in links.keys():
                    output_file.write('@PREDICATE\t{}\t{}\t\n'.format(key, links[key]))
                else:
                    output_file.write('@PREDICATE\t{0}\tno_match\tnot_found\t{0}\t\n'.format(key))

            for key in entities:
                if key in links.keys():
                    output_file.write('@ENTITY\t{}\t{}\t\n'.format(key, links[key]))
                else:
                    output_file.write('@ENTITY\t{0}\tno_match\tnot_found\t{0}\t\n'.format(key))

            output_file.close()

        print('Linked entities were stored at {}'.format(output_filename))

        return output_filename

def main(args):
    arg_p = ArgumentParser('python linker.py', description='Links the text entities to URIs from a knowledge base.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-k', '--kgbase', type=str, default='babelfy', help='Knowledge base to be used, e.g. babelfy (default) or ncbo')
    arg_p.add_argument('-u', '--use_umls', action='store_true', help='Use UMLS as an intermediate link step.')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    kg_base = args.kgbase
    umls = args.use_umls
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    linker = Linker()
    linker.link(filename, kg_base, umls, verbose)

if __name__ == '__main__':
    exit(main(argv))
