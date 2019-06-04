import difflib
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

        if openie == 'clausie':
            output = self.__clausie(input_filename, output_filename, verbose)
        elif openie == 'stanford':
            output = self.__stanford_openie(input_filename, output_filename, verbose)
        else:
            raise Exception("Unknown openie system!")

        if srl:
            output = self.__semantic_role_labeling(output_filename, verbose)

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

    def __semantic_role_labeling(self, input, verbose=False):
        if verbose:
            print('Performing Sentence Role Labeling with SENNA...')

        senna = SennaWrapper()

        out_contents = ''
        with open(input, 'r') as input_file:
            for line in input_file.readlines():
                if len(line) < 1: continue

                cont_list = line.replace('\"', '').replace('\n','').split('\t')

                sentence_number = cont_list[0]

                openie_subject = cont_list[1]
                openie_predicate = cont_list[2]
                openie_object = cont_list[3]

                senna_contents = senna.srl(' '.join(cont_list[1:]), verbose=False)
                closest_matches = difflib.get_close_matches(openie_predicate, senna_contents.keys())

                if len(closest_matches) < 1: continue

                predicate = closest_matches[0]
                dict_contents = senna_contents[predicate]

                if 'A0' in dict_contents and 'A1' in dict_contents:
                    agent = dict_contents['A0']
                    patient = dict_contents['A1']

                elif 'A0' in dict_contents:
                    agent = dict_contents['A0']
                    for key in dict_contents.keys():
                        if not key == 'A0':
                            patient = dict_contents[key]

                elif 'A1' in dict_contents:
                    patient = dict_contents['A1']
                    for key in dict_contents.keys():
                        if not key == 'A1':
                            agent = dict_contents[key]

                else:
                    agent = openie_subject
                    patient = openie_object

                triple = '{}\t"{}"\t"{}"\t"{}"'.format(sentence_number, self.__resolve_punctuation_possessives_and_determiners(agent), predicate, self.__resolve_punctuation_possessives_and_determiners(patient))
                out_contents += triple + '\n'

            input_file.close()

            with open(input, 'w') as output_file: # now, overwrite the input to the new contents
                output_file.write(out_contents)
                output_file.close()

        return input # return the overwitten input

    def __resolve_punctuation_possessives_and_determiners(self, contents):
        # This seems like a major overhead, maybe there is a better way...
        nlp = CoreNLPFactory.createCoreNLP()
        annotated = nlp.annotate(contents,  properties={'annotators': 'tokenize, ssplit, pos', 'outputFormat': 'json'})
        json_output = json.loads(annotated)

        resolved = ''
        for sentence in json_output['sentences']:
            for token in sentence['tokens']:
                if token['pos'] in self.__PUNCTUATION_LIST or (token['index'] == 1 and token['pos'] == 'DT'):
                    continue
                if token['pos'] == 'POS':
                    resolved = resolved.strip()

                resolved += token['word'] + ' '

        return resolved.strip()

def main(args):
    arg_p = ArgumentParser('python extractor.py', description='Extracts facts from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-o', '--openie', type=str, default='stanford', help='Specify the openie system, e.g. stanford (default), clausie')
    arg_p.add_argument('-s', '--srl', action='store_true', help='Perform Semantic Role Labeling (SRL)')
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
