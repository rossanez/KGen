from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper
from common.ncbo.ncbowrapper import NCBOWrapper
from common.scispacy.scispacywrapper import ScispaCyWrapper
from common.uriutils import URIUtils

class KnowledgeBases:

    def __babelfy(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the Babelfy base')

        babelfy = BabelfyWrapper()

        prefixes = {'http://babelnet.org/rdf/': 'bn'}
        links = {}
        annotated = babelfy.annotate(contents)

        for annotation in annotated:
            entity = BabelfyWrapper.frag(annotation, contents).upper()
            uri = annotation.babelnet_url()#annotation.babel_synset_id()#

            prefix, suffix = URIUtils.get_prefix_and_suffix(uri)
            if not prefix in prefixes.keys():
                raise Exception('Unknown prefix: {}'.format(prefix))

            if verbose:
                print('Mapped "{}" to {}'.format(entity, uri))
                annotation.pprint()

            links[entity.lower()] = 'sameas\t{}:{}\t{}'.format(prefixes[prefix], suffix, entity.replace(',', ''))

        return prefixes, links

    def __ncbo(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the NCBO base')

        ncbo = NCBOWrapper()
        annotated = ncbo.annotate(contents, ontologies='NCIT')

        prefixes = {'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#': 'nci'}
        links = {}
        for annotation in annotated:
            annotated_class = annotation['annotatedClass']
            if not ('prefLabel' in annotated_class and '@id' in annotated_class):
                continue

            pref_label = annotated_class['prefLabel']
            uri = annotated_class['@id']
            ontology = annotated_class['links']['ontology']

            prefix, suffix = URIUtils.get_prefix_and_suffix(uri)
            if not prefix in prefixes.keys():
                prefixes[prefix] = URIUtils.get_key_for_prefix(prefix)

            try:
                pref_map_str = '{} \n--Ontology: {} \n--PrefLabel: {}'.format(uri, ontology, pref_label)
            except UnicodeEncodeError:
                continue # NCBO may present some Chinese characters. We will ignore them.

            for class_annotation in annotation['annotations']:
                entity = contents[class_annotation['from']-1:class_annotation['to']] # class_annotation['text'] is uppercase
                preferable_match = class_annotation['matchType'].upper() == 'PREF'

                if preferable_match or not entity in links:
                    if verbose:
                        print('-Mapped "{}" to {} \n--PrefMatch: {}'.format(entity, pref_map_str, preferable_match))

                    if preferable_match:
                        links[entity] = 'sameas\t{}:{}\t{}'.format(prefixes[prefix], suffix, pref_label.replace(',', '').replace('.', ''))
                    else:
                        links[entity] = 'synonym\t{}:{}\t{}'.format(prefixes[prefix], suffix, pref_label.replace(',', '').replace('.', ''))

                    if preferable_match: break

        return prefixes, links

    __methods = {'babelfy':__babelfy, 'ncbo':__ncbo}
    __bases = None

    def __init__(self, bases):
        self.__bases = bases.split(',')

        if not all(e in self.__methods.keys() for e in self.__bases):
            raise Exception("Unknown knowledge base!")

    def annotate(self, contents, verbose):
        prefixes = {}
        links = {}
        for base in self.__bases:
            prefs, lnks = self.__methods[base](self, contents, verbose)
            prefixes.update(prefs)
            links.update(lnks)

        return prefixes, links

    def query(self, contents, verbose):
        #TODO extend it to other KBs -- currently only NCBO.

        sci = ScispaCyWrapper()
        entities, relations, umls = sci.detect(contents, detect_relations=True, resolve_abbreviations=False, link_with_umls=True, verbose=verbose)

        if umls:
            prefixes = {'http://bioportal.bioontology.org/ontologies/umls/': 'umls'}

        links = entities.union(relations)

        ncbo = NCBOWrapper()
        #TODO continue NCBO linking.

        return prefixes, entities, relations, umls
        
