from sys import path

path.insert(0, '../')
from common.nlputils import NLPUtils
from common.senna.sennawrapper import SennaWrapper

class SemanticRoleLabeler:

    def extract(self, input_filename, output_filename, verbose=False):
      return self.__senna(input_filename, output_filename, verbose)

    def __senna(self, input_filename, output_filename, verbose=False):
        if verbose:
            print('Performing Sentence Role Labeling with SENNA...')

        senna = SennaWrapper()

        out_contents = ''
        with open(input_filename, 'r') as input_file:
            sentence_number = 0
            for line in input_file.readlines():
                if len(line) < 1: continue

                senna_output = senna.srl(NLPUtils.adjust_tokens(line), verbose=False)
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
