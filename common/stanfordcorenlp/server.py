import os
import requests

from argparse import ArgumentParser
from commands import getoutput
from subprocess import Popen
from sys import argv
from sys import stderr

port = 9000
base_url = 'http://localhost'
url = base_url + ':{}'.format(port)

timeout = 15000

shutdown_url = url + '/shutdown'

tmpdir_prop = 'java.io.tmpdir'
tmpdir = '/tmp/'
shutdown_key_file = tmpdir + 'corenlp.shutdown'

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
        return base_url, port, timeout

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
        return os.path.isfile(shutdown_key_file)

    def startServer(self, verbose=False, wait_for_subprocess=False):
    	assert not self.isServerStarted(), 'ERROR: Server already started.'

        source_dir = os.path.dirname(os.path.abspath(__file__))
        if verbose:
            print('Starting Stanford CoreNLP Server from {}'.format(source_dir))

        jars = '{0}/stanford-corenlp.jar:{0}/stanford-corenlp-models.jar'.format(source_dir)

        command = 'java -D' + tmpdir_prop + '="' + tmpdir + '" -mx4g' + \
                  ' -cp "' + jars + '" edu.stanford.nlp.pipeline.StanfordCoreNLPServer' + \
                  ' -port {} -timeout {}'.format(port, timeout)

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

        shutdown_key = getoutput('cat ' + shutdown_key_file)
        if verbose:
            print('Stopping Stanford CoreNLP Server with {}?key={}'.format(shutdown_url, shutdown_key))

        response = requests.post(shutdown_url, data="", params={"key": shutdown_key})
        if response:
            print('Stop request issued successfully.')
        else:
            print('ERROR: status_code: {}'.format(response.status_code))
        print('Server response: {}'.format(response.text))

def main(argv):
    arg_p = ArgumentParser('python server.py', description='Starts the Stanford CoreNLP Server.')
    arg_p.add_argument('-c', '--check', action='store_true', help='Checks if there is an active server running.')
    arg_p.add_argument('-k', '--kill', action='store_true', help='Stops the server, if already started.')

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
