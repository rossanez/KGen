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
            if verbose:
                print('- sentence: {}'.format(sentence))

            annotated = isimp.run_isimp(sentence, verbose)
            if len(annotated['SIMP']) == 0 or annotated['SIMP'][0]['TYPE'] not in self.__methods.keys():
                if verbose:
                    print('-- simplification annotations length: {}'.format(len(annotated['SIMP'])))
                    if len(annotated['SIMP']) > 0:
                        for anntype in annotated['SIMP']:
                            print('--- NOT handling: {}'.format(anntype['TYPE']))
                simplified_contents.insert(0, sentence) # insert at the beginning
            else:
                if verbose:
                    print('-- handling "{}"'.format(annotated['SIMP'][0]['TYPE']))
                sentences = self.__methods[annotated['SIMP'][0]['TYPE']](self, sentence, annotated['SIMP'][0])
                for sentence in sentences:
                    self.__contents_stack.append(sentence)

        return '\n'.join(simplified_contents)

    def __reduced_relative_clause(self, sentence, simp):
        begin = sentence[:simp['FROM']]
        end = sentence[simp['TO  ']:]

        clauses = []
        for comp in simp['COMP']:
            if comp['TYPE'] == 'clause':
                clauses.append(sentence[comp['FROM']:comp['TO  ']])

        return ['{}{}{}'.format(begin, ' '.join(clauses), end)]

    def __phrase_coordination(self, sentence, simp):
        begin = sentence[:simp['FROM']]
        end = sentence[simp['TO  ']:]

        coordinates = set()
        for comp in simp['COMP']:
            if comp['TYPE'] == 'conjunct':
                coordinate = sentence[comp['FROM']:comp['TO  ']]
                coordinates.add('{}{}{}'.format(begin, coordinate, end))

        return list(coordinates)

    __methods = {'reduced relative clause':__reduced_relative_clause, 'verb or verb phrase coordination':__phrase_coordination, 'noun or noun phrase coordination':__phrase_coordination, 'adj or adj phrase coordination':__phrase_coordination}

