from os import listdir
from os.path import abspath, dirname, isfile, join
from stanfordcorenlp import StanfordCoreNLP
from server import Server

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
        default_model = 'edu/stanford/nlp/models/ner/english.all.3class.distsim.crf.ser.gz'

        models = list()
        models.append(default_model)

        current_dir = dirname(abspath(__file__))
        models_dir = current_dir + '/ner_models/'

        for model in listdir(models_dir):
            if isfile(join(models_dir, model)):
                models.append(model)

        return ','.join(models)
