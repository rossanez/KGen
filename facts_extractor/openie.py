import os

from sys import path

path.insert(0, '../')
from common.clausie.clausiewrapper import ClausIEWrapper
from common.stanfordcorenlp.corenlpwrapper import CoreNLPWrapper
from common.triple import Triple

class OpenIE:

    def __stanford_openie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for triples using Stanford OpenIE ...')

        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, ner, depparse, parse, openie'})

        for sentence in annotated['sentences']:
            for openie in sentence['openie']:
                with open(output, 'a') as output_file:
                    triple = Triple(sentence['index'], openie['subject'], openie['relation'], openie['object'])
                    if verbose:
                       print(triple.to_string())
                    output_file.write(triple.to_string() + '\n')
                    output_file.close()

        return output

    def __clausie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for triples using ClausIE ...')

        input_clausie = os.path.splitext(input)[0] + '_clausie_input.txt'
        open(input_clausie, 'w').close()

        print('Preparing contents to be processed by ClausIE at {}'.format(input_clausie))
        
        nlp = CoreNLPWrapper()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos'})

        for sentence in annotated['sentences']:
            sent_str = ''
            for token in sentence['tokens']:
                if token['pos'] == 'POS':
                    sent_str.strip()

                sent_str += token['word'] + ' '

            with open(input_clausie, 'a') as clausie_file:
                clausie_file.write(str(sentence['index']) + '\t' + sent_str.strip() + '\n')
                clausie_file.close()

        clausie_out =  ClausIEWrapper.run_clausie(input_clausie, output, verbose)

        os.remove(input_clausie)

        return clausie_out

    __methods = {'stanford':__stanford_openie, 'clausie':__clausie}
    __systems = None

    def __init__(self, systems):
        self.__systems = systems.split(',')

        if not all(e in self.__methods.keys() for e in self.__systems):
            raise Exception("Unknown OpenIE system!")

    def extract(self, input, output, verbose):
        for system in self.__systems:
            return self.__methods[system](self, input, output, verbose)
            
        return None

