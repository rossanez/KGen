import itertools
import re

from nltk import everygrams, pos_tag, RegexpParser, tree, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sys import path

path.insert(0, '../')
from common.nlputils import NLPUtils
from common.triple import Triple

ENTITY_GRAMMAR = "ENTITY: {<R.*>*<HYPH>*<R.*>*<JJ.*>*<HYPH>*<JJ.*>*<HYPH>*<NN.*>*<HYPH>*<NN.*>+}"

class SecondaryFactsExtractor:

    def extract(self, input_filename, output_filename, verbose=False):
        return self.__dep_parse(input_filename, output_filename, verbose)

    def __extract_entity_candidates_delimited_by_stopwords(self, contents):
        tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
        tokens = tokenizer.tokenize(contents)
        filtered_words = [a for a in [w if w not in stopwords.words('english') else ':delimiter:' for w in tokens] if a != '']
        matrix_of_tokens = [list(g) for k,g in itertools.groupby(filtered_words,lambda x: x == ':delimiter:') if not k]
        return {" ".join(row) for row in matrix_of_tokens}

    def __extract_entity_candidates_using_grammar(self, contents):
        pos_tags = pos_tag(word_tokenize(contents))

        grammar_parser = RegexpParser(ENTITY_GRAMMAR)

        candidates = set()
        pos_tags_with_grammar = grammar_parser.parse(pos_tags)
        for node in pos_tags_with_grammar:
            if isinstance(node, tree.Tree) and node.label() == 'ENTITY':
                candidate = ''
                for leaf in node.leaves():
                    #part = re.sub('[\=\,\…\’\'\+\-\–\“\”\"\/\‘\[\]\®\™\%]', ' ', leaf[0])
                    #part = re.sub('\.$|^\.', '', part)
                    #part = part.lower().strip()
                    candidate += ' ' + leaf[0]
                candidate = re.sub('\.+', '.', candidate)
                candidate = re.sub('\s+', ' ', candidate)
                candidates.add(candidate.strip())
        return candidates

    def __compose_subconcepts(self, concepts):
        entity_composites = set()

        for concept in concepts:
            grams = everygrams(concept.split(), 1, len(concept))
            previous_compounds = []
            for gram in grams:
                if len(gram) == 1:
                    previous_compounds.append(gram[0])
                    continue

                if (gram[-1] in previous_compounds):
                    subClass = ' '.join(gram)
                    klass = gram[-1]
                    part = ' '.join(gram[:-1])

                    entity_composites.add((subClass, 'rdfs:subClassOf', klass))
                    entity_composites.add((part, 'local:partOf', subClass))

        return entity_composites

    def __extract_candidate_concepts(self, contents):
        candidates = self.__extract_entity_candidates_using_grammar(contents)
        #candidates = candidates.union(self.__extract_entity_candidates_delimited_by_stopwords(contents))
        return self.__compose_subconcepts(candidates)

    def __dep_parse(self, input_filename, output_filename, verbose=False):
        if verbose:
            print('Attempting to extract secondary facts using dependency parsing...')

        out_contents = ''
        with open(input_filename, 'r') as input_file:
            sentence_number = 0
            for line in input_file.readlines():
                if len(line) < 1:
                    continue

                entity_composites = self.__extract_candidate_concepts(line)
                for entry in entity_composites:
                    triple = Triple(sentence_number, entry[0], entry[1], entry[2])
                    if verbose:
                        print(triple.to_string())

                    out_contents += triple.to_string() + '\n'

                dependency_list = NLPUtils.dependency_parse(line, deps_key='enhancedPlusPlusDependencies', verbose=verbose)

                previous_term = ''
                previous_compound = ''
                dict_basic_to_most_specific = {}
                connective_dependencies = []
                while len(dependency_list) > 0:
                    elem = dependency_list.pop()

                    if elem[1] in ['ROOT', 'punct', 'det'] or 'subj' in elem[1] or 'obj' in elem[1]:
                        continue

                    if elem[1] in ['compound', 'nmod:poss', 'aux', 'neg'] or elem[1].endswith('mod'):
                        if previous_term == elem[0]:
                            updated_term = '{} {}'.format(elem[2], previous_compound)
                        else:
                            updated_term = '{} {}'.format(elem[2], elem[0])
                            previous_compound = elem[0]
                        dict_basic_to_most_specific[elem[0]] = updated_term

                        triple = Triple(sentence_number, updated_term, 'rdfs:subClassOf', previous_compound)

                        previous_compound = updated_term
                        previous_term = elem[0]

                        if triple.to_tuple() in entity_composites:
                            if verbose:
                                print('Skipping repeated triple: {}'.format(triple.to_string()))
                            continue

                        if verbose:
                            print(triple.to_string())

                        out_contents += triple.to_string() + '\n'

                    elif elem[1] in ['acl', 'appos'] or elem[1].startswith('nmod:'):
                        connective_dependencies.append(elem)

                while len(connective_dependencies) > 0:
                    elem = connective_dependencies.pop()

                    if elem[1] == 'nmod:poss':
                        continue

                    if elem[1].find(':') > 0: # e.g. 'nmod:of'
                        connector = elem[1][elem[1].find(':')+1:]
                    elif elem[1] in ['acl', 'appos']:
                        connector = ''
                    else:
                        connector = elem[1]

                    first = elem[0]
                    if first in dict_basic_to_most_specific.keys():
                        first = dict_basic_to_most_specific[first]

                    second = elem[2]
                    if second in dict_basic_to_most_specific.keys():
                        second = dict_basic_to_most_specific[second]

                    if connector == '':
                        full = '{} {}'.format(first, second)
                    else:
                        full = '{} {} {}'.format(first, connector, second)
                    
                    triple = Triple(sentence_number, full, 'local:{}_{}'.format(connector, second.replace(' ', '')), first)
                    if verbose:
                        print(triple.to_string())
                    out_contents += triple.to_string() + '\n'

                    triple = Triple(sentence_number, full, 'local:{}_{}'.format(first.replace(' ', ''), connector), second)
                    if verbose:
                        print(triple.to_string())
                    out_contents += triple.to_string() + '\n'

                    dict_basic_to_most_specific[elem[0]] = full

                sentence_number += 1

            input_file.close()

        with open(output_filename, 'a') as output_file:
            output_file.write(out_contents)
            output_file.close()

        return output_filename
