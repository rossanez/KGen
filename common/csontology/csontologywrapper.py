import csv
import os

CSO_FILENAME = 'CSO.3.2.csv'

CSO_CONTRIBUTESTO = '<http://cso.kmi.open.ac.uk/schema/cso#contributesTo>'
CSO_PREFERENTIALDEQUIVALENT = '<http://cso.kmi.open.ac.uk/schema/cso#preferentialEquivalent>'
CSO_RELATEDEQUIVALENT = '<http://cso.kmi.open.ac.uk/schema/cso#relatedEquivalent>'
CSO_SUPERTOPICOF = '<http://cso.kmi.open.ac.uk/schema/cso#superTopicOf>'
OWL_SAMEAS = '<http://www.w3.org/2002/07/owl#sameAs>'
RDF_TYPE = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'
RDFS_LABEL = '<http://www.w3.org/2000/01/rdf-schema#label>'
SCHEMA_RELATEDLINK = '<http://schema.org/relatedLink>'

class CSOWrapper:

    def __init__(self):
        self.__load_ontology_from_file__()

    def __load_ontology_from_file__(self):
        local_path = os.path.dirname(os.path.abspath(__file__))
        cso_file_abspath = local_path + '/' + CSO_FILENAME

        with open(cso_file_abspath, 'r') as file:
            ontology = csv.reader(file, delimiter=',', quotechar='"')

            self._links = {}
            for triple in ontology:
                if triple[1] == RDFS_LABEL:
                    value = triple[2][:-5] # strip the "@en ." finale
                    uri = triple[0].replace('>', '').replace('<', '')

                    self._links[value] = uri

    def print_links(self):
        print(self._links)