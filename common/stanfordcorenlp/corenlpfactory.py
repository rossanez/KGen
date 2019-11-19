import glob

from os import listdir
from os.path import abspath, dirname
from stanfordcorenlp import StanfordCoreNLP
from .server import Server

class CoreNLPFactory:

    @staticmethod
    def createCoreNLP():
        server = Server.getServer()

        if not server.isServerStarted():
            server.startServer()

        host, port, timeout = Server.getURLParams()

        return StanfordCoreNLP(host, port=port, timeout=timeout)

    @staticmethod
    def getNERModels():
        default_model = 'edu/stanford/nlp/models/ner/english.conll.4class.distsim.crf.ser.gz'

        models = list()

        current_dir = dirname(abspath(__file__))
        models_path = current_dir + '/ner_models/*.ser.gz'

        for model in glob.glob(models_path):
            models.append(model)

        models.append(default_model)
        return ','.join(models)
