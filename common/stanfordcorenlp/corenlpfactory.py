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
    