import os

from argparse import ArgumentParser
from sys import argv
from sys import path
from sys import version_info

# Version check
if version_info[0] >= 3:
    path.append('facts_extractor')
    path.append('kb_linker')
    path.append('preprocessor')

    from common.stanfordcorenlp.server import Server
    from facts_extractor.extractor import FactsExtractor
    from graph_generator.generator import GraphGenerator
    from kb_linker.linker import Linker
    from preprocessor.preprocessor import Preprocessor
    from rdf_maker.maker import RDFMaker

class Pipeline:

    __needs_server_shutdown = False
    __server_instance = None

    def __init__(self):
        self.__server_instance = Server.getServer()
        if not self.__server_instance.isServerStarted():
            self.__needs_server_shutdown = True

    def __del__(self):
        if self.__needs_server_shutdown and self.__server_instance.isServerStarted():
            self.__server_instance.stopServer()
        elif self.__server_instance.isServerStarted():
            print('-Warning: Stanford CoreNLP server instance is still running!')        

    def run(self, filename, preprocess=True, primary_triples='senna', secondary_triples=False, k_base='cso', umls=False, png=True, verbose=False):
        if preprocess:
            preprocessed_filename = None
            preprocessed_filename = Preprocessor().preprocess(filename, verbose)
            assert not preprocessed_filename is None, 'Preprocessing has failed!'
        else:
            preprocessed_filename = filename

        triples_filename = None
        triples_filename = FactsExtractor().extract_triples(preprocessed_filename, primary_triples, secondary_triples, verbose)
        assert not triples_filename is None, 'Facts Extraction has failed!'

        links_filename = None
        links_filename = Linker().link(preprocessed_filename, k_base, umls, verbose)
        assert not links_filename is None, 'Ontology linking has failed!'

        rdf_filename = None
        rdf_filename = RDFMaker().make(triples_filename, links_filename, verbose)
        assert not rdf_filename is None, 'RDF generation has failed!'

        if png:
            png_filename = None
            png_filename = GraphGenerator().generate(rdf_filename, verbose)
            assert not png_filename is None, 'Graph image generation has failed!'

def main(args):
    if version_info[0] < 3: # Python version check
        print('Please run the pipeline using Python 3')
        exit(1)

    arg_p = ArgumentParser('python pipeline.py', description='Generates a KG from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-np', '--nopreprocess', action='store_true', help='Skips preprocessing')
    arg_p.add_argument('-p', '--primary', type=str, default='senna', help='Primary triples extraction method, e.g., senna (default)), openie, clausie')
    arg_p.add_argument('-s', '--secondary', action='store_true', help='Extract secondary triples using dependency parsing')
    arg_p.add_argument('-k', '--kbase', type=str, default='cso', help='Knowledge base used for linking, e.g., cso (default), ncbo, babelfy')
    arg_p.add_argument('-u', '--umls', action='store_true', help='Use UMLS to improve linking in the biomedical domain')
    arg_p.add_argument('-ng', '--nograph', action='store_true', help='Skips PNG image generation')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    preprocess = not args.nopreprocess
    primary_triples = args.primary
    secondary_triples = args.secondary
    k_base = args.kbase
    umls = args.umls
    png = not args.nograph
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    pipeline = Pipeline()
    pipeline.run(filename, preprocess, primary_triples, secondary_triples, k_base, umls, png, verbose)

if __name__ == '__main__':
    exit(main(argv))

