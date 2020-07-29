from sys import path

path.insert(0, '../')
from common.nlputils import NLPUtils
from common.senna.sennawrapper import SennaWrapper
from common.triple import Triple

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
                if len(line) < 1:
                    continue

                senna_output = senna.srl(line, verbose=False)
                for predicate in senna_output.keys():
                    pred_args = senna_output[predicate]
                    pred_arg_names = NLPUtils.get_verbnet_args(predicate, verbose)
                    if len(pred_arg_names) < 1:
                        print('WARNING -- Unable to retrieve predicate arg names for "{}"'.format(predicate))

                    if verbose:
                        print('predicate: {}, args: {}'.format(predicate, pred_args))

                    for pred_arg in pred_args:
                        if 'AM-NEG' == pred_arg:
                            predicate = 'not {}'.format(predicate)
                        elif 'AM-MOD' == pred_arg:
                            predicate = ' '.join([pred_args['AM-MOD'].strip(), predicate])
                        elif pred_arg.startswith('AM-'):
                            # Remove initial stopwords (e.g. determiners)
                            s = pred_args[pred_arg].strip()
                            split = s.split(' ', 1)
                            if NLPUtils.is_stopword(split[0]) and len(split) > 1:
                                s = s.split(' ', 1)[1]

                            triple = Triple(sentence_number, predicate, 'local:{}'.format(pred_arg), s)
                            if verbose:
                                print(triple.to_string())

                            out_contents += triple.to_string() + '\n'

                    for i in range(len(pred_arg_names)):
                        pred_args_index = 'A{}'.format(i)
                        if pred_args_index in pred_args:
                            # Remove initial stopwords (e.g. determiners)
                            s = pred_args[pred_args_index].strip()
                            split = s.split(' ', 1)
                            if NLPUtils.is_stopword(split[0]) and len(split) > 1:
                                s = s.split(' ', 1)[1]

                            triple = Triple(sentence_number, predicate, 'vn.role:{}'.format(pred_arg_names[i]), s)
                            if verbose:
                                print(triple.to_string())

                            out_contents += triple.to_string() + '\n'

                sentence_number += 1

            input_file.close()

        with open(output_filename, 'w') as output_file:
            output_file.write(out_contents)
            output_file.close()

        return output_filename
