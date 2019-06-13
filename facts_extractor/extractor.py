import json
import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory
from common.clausie.clausiewrapper import ClausIEWrapper
from common.senna.sennawrapper import SennaWrapper

class FactsExtractor:

    __PUNCTUATION_LIST = ['.', ',', ':', ';']

    def extract_triples(self, input_filename, openie='stanford', srl=False, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_triples.txt'
        open(output_filename, 'w').close()

        if srl:
            output = self.__semantic_role_labeling(input_filename, output_filename, verbose)
        else:
            if openie == 'clausie':
                output = self.__clausie(input_filename, output_filename, verbose)
            elif openie == 'stanford':
                output = self.__stanford_openie(input_filename, output_filename, verbose)
            else:
                raise Exception("Unknown openie system!")

        print('Extracted triples were stored at {}'.format(output))

        return output

    def __stanford_openie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for triples using Stanford OpenIE ...')

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos, ner, depparse, parse, openie', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        for sentence in json_output['sentences']:
            for openie in sentence['openie']:
                with open(output, 'a') as output_file:
                    triple = '{}\t"{}"\t"{}"\t"{}"'.format(sentence['index'], openie['subject'], openie['relation'], openie['object'])
                    if verbose:
                       print(triple)
                    output_file.write(triple + '\n')
                    output_file.close()

        return output

    def __clausie(self, input, output, verbose=False):
        with open(input, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        if verbose:
            print('Searching for triples using ClausIE ...')

        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents, properties={'annotators': 'tokenize, ssplit, pos', 'outputFormat': 'json'})

        json_output = json.loads(annotated)

        input_clausie = os.path.splitext(input)[0] + '_clausie_input.txt'
        open(input_clausie, 'w').close()

        print('Preparing contents to be processed by ClausIE at {}'.format(input_clausie))

        for sentence in json_output['sentences']:
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

    def __semantic_role_labeling(self, input_filename, output_filename, verbose=False):
        if verbose:
            print('Performing Sentence Role Labeling with SENNA...')

        senna = SennaWrapper()

        out_contents = ''
        with open(input_filename, 'r') as input_file:
            sentence_number = 0
            for line in input_file.readlines():
                if len(line) < 1: continue

                senna_output = senna.srl(self.__resolve_possessives(line), verbose=False)
                for predicate in senna_output.keys():
                    dict_contents = senna_output[predicate]

                    if 'A0' in dict_contents and 'A1' in dict_contents:
                        agent = dict_contents['A0']
                        patient = dict_contents['A1']

                    elif 'A0' in dict_contents: # No A1
                        agent = dict_contents['A0']
                        if 'A2' in dict_contents:
                            patient = dict_contents['A2']
                        else:
                            for key in dict_contents.keys():
                                if not key == 'A0':
                                    patient = dict_contents

                    elif 'A1' in dict_contents: # No A0
                        patient = dict_contents['A1']
                        if 'A2' in dict_contents:
                            agent = dict_contents['A2']
                        else:
                            for key in dict_contents.keys():
                                if not key == 'A1':
                                    agent = dict_contents[key]

                    else: # Neither A0 nor A1
                        if 'A2' in dict_contents:
                            agent = dict_contents['A2']
                            for key in dict_contents.keys():
                               if not key == 'A2':
                                   patient = dict_contents[key]
                        else: # Very unlikely
                            key_lst = dict_contents.keys()
                            key_lst.sort(key = len) # sort by string length
                            agent = dict_contents[key_lst[0]]
                            patient = dict_contents[key_lst[1]]

                    triple = '{}\t"{}"\t"{}"\t"{}"'.format(sentence_number, agent, predicate, patient)

                    if verbose:
                        print(triple)

                    out_contents += triple + '\n'

                sentence_number += 1

            input_file.close()

        with open(output_filename, 'w') as output_file:
            output_file.write(out_contents)
            output_file.close()

        return output_filename

    def __resolve_possessives(self, contents):
        # This seems like a major overhead, maybe there is a better way...
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos', 'outputFormat': 'json'})
        json_output = json.loads(annotated)

        resolved = ''
        for sentence in json_output['sentences']:
            for token in sentence['tokens']:
                if token['pos'] == 'POS' or token['pos'] == '.':
                    resolved = resolved.strip()

                resolved += token['word'] + ' '

        return resolved.strip()

def main(args):
    arg_p = ArgumentParser('python extractor.py', description='Extracts facts from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-o', '--openie', type=str, default='stanford', help='Specify the openie system, e.g. stanford (default), clausie')
    arg_p.add_argument('-s', '--srl', action='store_true', help='Perform Semantic Role Labeling (SRL) - Will *NOT* perform openie!')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    openie = args.openie
    srl = args.srl
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    extractor = FactsExtractor()
    extractor.extract_triples(filename, openie, srl, verbose)

if __name__ == '__main__':
    exit(main(argv))
