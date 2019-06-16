from sys import path

path.insert(0, '../')
from common.isimp.isimpwrapper import iSimpWrapper

class Simplifier: # TODO implement it further...

    __contents_stack = None

    def __init__(self, contents):
        self.__contents_stack = contents.splitlines()

    def simplify(self, verbose):
        simplified_contents = []

        isimp = iSimpWrapper()
        while len(self.__contents_stack) > 0:
            sentence = self.__contents_stack.pop()
            annotated = isimp.run_isimp(sentence, verbose)
            if len(annotated['SIMP']) == 0 or annotated['SIMP'][0]['TYPE'] not in self.__methods.keys():
                simplified_contents.append(sentence)
            else:
                self.__contents_stack.append(self.__reduced_relative_clause(sentence, annotated['SIMP'][0]))

        return '\n'.join(simplified_contents)

    def __reduced_relative_clause(self, sentence, simp):
        begin = sentence[:simp['FROM']]
        end = sentence[simp['TO  ']:]

        clauses = []
        for comp in simp['COMP']:
            if comp['TYPE'] == 'clause':
                clauses.append(sentence[comp['FROM']:comp['TO  ']])

        return '{} {} {}'.format(begin, ' '.join(clauses), end)

    
    __methods = {'reduced relative clause':__reduced_relative_clause}

