import difflib
import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.nlputils import NLPUtils
from common.stanfordcorenlp.corenlpfactory import CoreNLPFactory
from common.triple import Triple

class RDFMaker:

    __prefixed = {}
    __links = {}

    __classes = {}
    __properties = {}
    __mapped_relations = set()
    __relations = set()

    def make(self, triples_filename, links_filename, verbose=False):
        if not triples_filename.startswith('/'):
            triples_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + triples_filename

        if not links_filename == None and not links_filename.startswith('/'):
            links_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + links_filename

        print('Processing triples from {}'.format(triples_filename))

        self.__prefixed = {'http://www.w3.org/2000/01/rdf-schema#': 'rdfs', 'http://local/local.owl#': 'local', 'http://local/verbnet_roles.owl#': 'vn.role'}
        if not links_filename == None:
            with open(links_filename, 'r') as links_file:
                for line in links_file.readlines():
                    if len(line) < 2: continue

                    if line.startswith('@PREFIX'):
                        line_list = line.split()
                        prefix = line_list[1]
                        prefix = prefix[:prefix.rfind(':')]

                        uri = line_list[2]
                        uri = uri[uri.find('<') + 1:uri.find('>')]

                        self.__prefixed.update({uri: prefix})

                    elif line.startswith('@LINK'):
                        line_list = line.split('\t')

                        predicate = line_list[1]
                        links = '\t'.join(line_list[2:])
                        self.__links.update({predicate: links})

                links_file.close()

        with open(triples_filename, 'r') as triples_file:
            for line in triples_file.readlines():
                line_lst = line.replace('\"', '').split('\t')
                sentence_number = line_lst[0].strip()
                subject = line_lst[1].strip()
                predicate = line_lst[2].strip()
                object = line_lst[3].strip()

                if not predicate in self.__links and predicate.find(':') < 0:
                    if verbose:
                        print('Warning: no match for predicate "{}" was found in the links! Skipping triple ...'.format(predicate))
                #    continue

                predicate_link = ''
                #if predicate.find(':') < 0: #Predicates that are already resources/links
                if predicate in self.__links:
                    predicate_link = self.__links[predicate]

                entities = set([str(X) for X in self.__links.keys()])
                closest_subjects = difflib.get_close_matches(subject, entities, n=3, cutoff=0.94)
                closest_objects = difflib.get_close_matches(object, entities, n=3, cutoff=0.94)

                if len(closest_subjects) < 1:
                    if verbose:
                        print('Warning: no match for subject "{}" was found in the links! Attempting partials ...'.format(subject))
                    #subj = subject
                    # Reverse sorted list of entities by string length
                    #lst_entities = sorted(list(entities), key=len, reverse=True)
                    #for elem in lst_entities:
                    #    if elem in subj:
                    #        if verbose:
                    #            print('-- Found: {}'.format(elem))
                    #        closest_subjects.append(elem)
                    #        subj = subj.replace(elem, '')

                    #if len(closest_subjects) < 1:
                    #    if verbose:
                    #        print('WARNING: not even partial matches were found for subject "{}" in the links!'.format(subject))
                    #    continue

                if len(closest_objects) < 1:
                    if verbose:
                        print('Warning: no match for object "{}" was found in the links! Atempting partials ...'.format(object))
                    obj = object
                    # Reverse sorted list of entities by string length
                    #lst_entities = sorted(list(entities), key=len, reverse=True)
                    #for elem in lst_entities:
                    #    if elem in obj:
                    #        if verbose:
                    #            print('-- Found: {}'.format(elem))
                    #        closest_objects.append(elem)
                    #        obj = obj.replace(elem, '')

                    #if len(closest_objects) < 1:
                    #    if verbose:
                    #        print('WARNING: not even partial matches were found for object "{}" in the links!'.format(object))
                    #    continue

                # Check for exact matches and discard the others if that's the case
                #for sub in closest_subjects:
                #    if subject == sub:
                #        closest_subjects = [sub]
                #        break
                #for ob in closest_objects:
                #    if object == ob:
                #        closest_objects = [ob]
                #        break

                subject_links = []
                for subj in closest_subjects:
                    subject_links += [self.__links[subj]]
                object_links = []
                for obj in closest_objects:
                    object_links += [self.__links[obj]]

                triple = Triple(sentence_number, subject, predicate, object, subject_links, predicate_link, object_links)

                prefixes, classes, properties, mapped, relation = triple.to_turtle()
                self.__prefixed.update(prefixes)
                self.__classes.update(classes)
                self.__mapped_relations.update(mapped)
                self.__properties.update(properties)
                self.__relations.add(relation)
                
            triples_file.close()

        output_filename = os.path.splitext(triples_filename)[0]
        output_filename = output_filename[:output_filename.rfind('_')] + '_kg.ttl'
        open(output_filename, 'w').close() # Clean the file in case it exists

        with open(output_filename, 'a') as output_file:
            for key in self.__prefixed.keys():
                output_file.write('@prefix\t{}:\t<{}>\t.\n'.format(self.__prefixed[key], key))

            output_file.write('\n#### Classes ####\n\n')
            for key in self.__classes.keys():
                output_file.write('{}\n\n'.format(self.__classes[key]))

            output_file.write('#### Properties ####\n\n')
            for key in self.__properties.keys():
                output_file.write('{}\n\n'.format(self.__properties[key]))

            output_file.write('#### Mapped Relations ####\n\n')
            for mapping in self.__mapped_relations:
                output_file.write('{}\n'.format(mapping))

            output_file.write('\n#### Relations ####\n\n')
            for relation in self.__relations:
                output_file.write('{}\n'.format(relation))

            output_file.close()
        print('RDF stored at {}'.format(output_filename))

        return output_filename

def main(args):
    arg_p = ArgumentParser('python maker.py', description='Merges the unlinked triples with the corresponding entities and predicates.')
    arg_p.add_argument('Triples', metavar='triples', type=str, default=None, help='Triples file')
    arg_p.add_argument('-l', '--links', type=str, default=None, help='Links file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    triples = args.Triples
    links = args.links
    verbose = args.verbose

    if triples is None:
        print('No triples file provided.')
        exit(1)

    maker = RDFMaker()
    maker.make(triples, links, verbose)

if __name__ == '__main__':
    exit(main(argv))

