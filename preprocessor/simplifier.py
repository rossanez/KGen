from sys import path

path.insert(0, '../')
from common.isimp.isimpwrapper import iSimpWrapper

class Simplifier:

    __contents_stack = None

    def __init__(self, contents):
        self.__contents_stack = contents.splitlines()

    def simplify(self, verbose):
        simplified_contents = []

        isimp = iSimpWrapper()
        while len(self.__contents_stack) > 0:
            sentence = self.__contents_stack.pop()
            if verbose:
                print('- sentence: {}'.format(sentence))

            annotated = isimp.run_isimp(sentence, verbose)
            simplified_contents.insert(0, isimp.generate_simpler_sentences(annotated)) # insert at the beginning

        return '\n'.join(simplified_contents)
