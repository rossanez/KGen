from nltk import everygrams
from sys import path

path.insert(0, '../')
from common.nlputils import NLPUtils
from common.statement import Statement
from common.triple import Triple

class SecondaryFactsExtractor:

    def extract(self, main_triples_filename, output_filename, verbose=False):
        return self.__dep_parse(main_triples_filename, output_filename, verbose)

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
                    entity_composites.add((subClass, 'rdfs:member', part))

        return entity_composites

    def __dep_parse(self, main_triples_filename, output_filename, verbose=False):
        if verbose:
            print('Attempting to extract secondary facts using dependency parsing...')

        out_contents = ''
        with open(main_triples_filename, 'r') as input_file:
            statements = {}
            for line in input_file.readlines():
                line_lst = line.split('\t')
                
                if len(line_lst) == 2: # A statement
                    stm_id = line_lst[0].strip()
                    stm_contents = line_lst[1].replace('"', '').strip()
                    statement = Statement(stm_id, stm_contents)
                    if verbose:
                        print(statement.to_string())
                    statements[stm_contents] = statement
                    out_contents += line # Let us leave this line alone.
                    continue

                if len(line_lst) < 4: # Ill-formed. Let us ignore it...
                    print('Warning: bad line: "{}"'.format(line))
                    continue

                statement_id = line_lst[0].strip()
                stmt = line_lst[1].replace('"', '').strip()
                predicate = line_lst[2].strip()
                obj = line_lst[3].replace('"', '').strip()

                out_contents += line # The original line must be kept.

                if predicate == 'rdf:predicate':
                    # This should be either a verb or a 'not' followed by a verb. No need to decompose it.
                    continue

                if obj in statements.keys():
                    if verbose:
                        print(f'Existing statement for object: {obj} - {statements[obj].get_res_id()}')
                    continue # Leave alone - secondary relations should have been obtained already!

                replacements = {}

                candidate_entities = NLPUtils.extract_candidate_entities(obj)
                if len(candidate_entities) > 1:
                    for candidate in candidate_entities:
                        triple = Triple(statement_id, obj, 'rdfs:member', candidate)
                        if verbose:
                            print(triple.to_string())

                        out_contents += triple.to_string() + '\n'

                entity_composites = self.__compose_subconcepts(candidate_entities)
                for entry in entity_composites:
                    triple = Triple(statement_id, entry[0], entry[1], entry[2])
                    if verbose:
                        print(triple.to_string())

                    out_contents += triple.to_string() + '\n'

                dependency_list = NLPUtils.dependency_parse(obj, deps_key='enhancedPlusPlusDependencies', verbose=False)

                previous_term = ''
                previous_compound = ''
                connective_dependencies = []
                while len(dependency_list) > 0:
                    elem = dependency_list.pop()

                    if not elem[0] in replacements:
                        replacements[elem[0]] = elem[0].split(':')[0]
                    governor = replacements[elem[0]]
                    if not elem[2] in replacements:
                        replacements[elem[2]] = elem[2].split(':')[0]
                    dependent = replacements[elem[2]]

                    if elem[1] in ['punct', 'det'] or 'subj' in elem[1] or 'obj' in elem[1]:
                        continue

                    if elem[1] in ['compound', 'nmod:poss', 'aux', 'neg'] or elem[1].endswith('mod'):
                        if previous_term == governor:
                            updated_term = '{} {}'.format(dependent, previous_compound)
                        else:
                            updated_term = '{} {}'.format(dependent, governor)
                            previous_compound = governor

                        replacements[elem[0]] = updated_term

                        triple = Triple(statement_id, updated_term, 'rdfs:subClassOf', previous_compound)

                        previous_compound = updated_term
                        previous_term = governor

                        if triple.to_tuple() in entity_composites:
                            if verbose:
                                print('Skipping repeated triple: {}'.format(triple.to_string()))
                            continue

                        if verbose:
                            print(triple.to_string())

                        out_contents += triple.to_string() + '\n'

                    elif elem[1] in ['acl', 'appos'] or elem[1].startswith('nmod:'):
                        connective_dependencies.append(elem)
                    elif elem[1] == 'ROOT':
                        connective_dependencies.insert(0, elem) # Should be the last of the stack

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
                    if first in replacements.keys():
                        first = replacements[first]

                    second = elem[2]
                    if second in replacements.keys():
                        second = replacements[second]

                    if elem[1] == 'ROOT':
                        continue

                    if connector == '':
                        full = '{} {}'.format(first, second)
                    else:
                        full = '{} {} {}'.format(first, connector, second)
                    
                    triple = Triple(statement_id, full, 'rdfs:member', first)
                    if verbose:
                        print(triple.to_string())
                    out_contents += triple.to_string() + '\n'

                    triple = Triple(statement_id, full, 'rdfs:member', second)
                    if verbose:
                        print(triple.to_string())
                    out_contents += triple.to_string() + '\n'

                    replacements[elem[0]] = full

            input_file.close()

        with open(output_filename, 'w') as output_file:
            output_file.write(out_contents)
            output_file.close()

        return output_filename
