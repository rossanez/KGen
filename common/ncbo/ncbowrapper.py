import json
import os
import urllib2

KEY_FILE = 'ncbo.key'
REST_URL = "http://data.bioontology.org"
REST_URL_BASE_ANNOTATOR_PARAMS = "/annotator?"

SPARQL_ENDPOINT_URL = "http://sparql.bioontology.org"
SPARQL_BASE_ANNOTATOR_PARAMS = "/sparql?"

class NCBOWrapper:

    __key = None

    def __init__(self):
    	self.__key = self.__getKey()

    def __getKey(self):
        local_path = os.path.dirname(os.path.abspath(__file__))
        key_file = local_path + '/' + KEY_FILE

        with open(key_file, 'r') as key:
            value = key.read()
            key.close()

        return value.strip()

    def annotate(self, contents, ontologies=None, max_level=0, include=None):
        params = REST_URL_BASE_ANNOTATOR_PARAMS
        if not ontologies is None:
            params += "ontologies=" + ontologies + "&" # ontologies must be a comma-separated list

        if max_level > 0:
            params += "max_level=" + max_level + "&"

        if include is None:
            include = "prefLabel,synonym,definition" # include must also be a comma-separated list
        params += "include=" + include + "&"

        params += "text=" + urllib2.quote(contents)
        url = REST_URL + params

        opener = urllib2.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + self.__key)]
        return json.loads(opener.open(url).read())

    def query(self, query_str=None):
        if query_str is None:
            query_str = 'SELECT ?s ?p ?o WHERE { ?s ?p ?o . } LIMIT 10'

        params = SPARQL_BASE_ANNOTATOR_PARAMS
        params += "apikey=" + self.__key + "&"
        params += "query=" + urllib2.quote(query_str) + "&"
        params += "outputformat=" + "json"

        url = SPARQL_ENDPOINT_URL + params
        opener = urllib2.build_opener()
        return json.loads(opener.open(url).read())
