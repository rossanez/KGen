import os
import requests

from argparse import ArgumentParser
from commands import getoutput
from subprocess import Popen
from sys import argv
from sys import stderr

PORT = 9000
BASE_URL = 'http://localhost'
URL = BASE_URL + ':{}'.format(PORT)

TIMEOUT = 15000

SHUTDOWN_URL = URL + '/shutdown'

TMPDIR_PROP = 'java.io.tmpdir'
TMPDIR = '/tmp/'
SHUTDOWN_KEY_FILE = TMPDIR + 'corenlp.shutdown'

class Server:
    # Singleton
    __instance = None

    @staticmethod
    def getServer():
        """ Static access method. """
        if Server.__instance == None:
            Server()
        return Server.__instance 

    @staticmethod
    def getURLParams():
        return BASE_URL, PORT, TIMEOUT

    def __init__(self):
        """ Virtually private constructor. """
        if Server.__instance != None:
            raise Exception("The Server is a singleton!")
        else:
            Server.__instance = self

    def __del__(self):
        if self.isServerStarted():
            stopServer()

    def isServerStarted(self):
        # There might be a better way...
        return os.path.isfile(SHUTDOWN_KEY_FILE)

    def startServer(self, verbose=False, wait_for_subprocess=False):
    	assert not self.isServerStarted(), 'ERROR: Server already started.'

        source_dir = os.path.dirname(os.path.abspath(__file__))
        if verbose:
            print('Starting Stanford CoreNLP Server from {}'.format(source_dir))

        jars = '{0}/stanford-corenlp.jar:{0}/stanford-corenlp-models.jar:{0}/slf4j-api.jar:{0}/slf4j-simple.jar:{0}/ejml.jar'.format(source_dir)

        command = 'java -D' + TMPDIR_PROP + '="' + TMPDIR + '" -mx5g' + \
                  ' -cp "' + jars + '" edu.stanford.nlp.pipeline.StanfordCoreNLPServer' + \
                  ' -port {} -timeout {}'.format(PORT, TIMEOUT)

        if verbose:
            print('Stanford CoreNLP Server startup command: {}'.format(command))
            java_process = Popen(command, stdout=stderr, shell=True)
        else:
            java_process = Popen(command, stdout=stderr, stderr=open(os.devnull, 'w'), shell=True)

        if wait_for_subprocess:
            java_process.wait()

        assert not java_process.returncode, 'ERROR: Stanford CoreNLP Server exited with a non-zero code status.'

    def stopServer(self, verbose=False):
    	assert self.isServerStarted(), 'ERROR: Server not running.'

        shutdown_key = getoutput('cat ' + SHUTDOWN_KEY_FILE)
        if verbose:
            print('Stopping Stanford CoreNLP Server with {}?key={}'.format(SHUTDOWN_URL, shutdown_key))

        response = requests.post(SHUTDOWN_URL, data="", params={"key": shutdown_key})
        if response:
            print('Stop request issued successfully.')
        else:
            print('ERROR: status_code: {}'.format(response.status_code))
        print('Server response: {}'.format(response.text))

def main(argv):
    arg_p = ArgumentParser('python server.py', description='Starts the Stanford CoreNLP Server.')
    arg_p.add_argument('-c', '--check', action='store_true', help='Checks if the server is running')
    arg_p.add_argument('-k', '--kill', action='store_true', help='Stops the server')

    args = arg_p.parse_args(argv[1:])
    check = args.check
    stop_server = args.kill

    server = Server.getServer()

    if check:
        if server.isServerStarted():
            print('The server is already running.')
        else:
            print('The server is NOT running.')
    elif stop_server:
        server.stopServer(verbose=True)
    else:
        server.startServer(verbose=True, wait_for_subprocess=True)

if __name__ == '__main__':
    exit(main(argv))
