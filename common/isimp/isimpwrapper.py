import json
import os

from subprocess import Popen
from sys import stderr

ISIMP_DIR = 'isimp_v2/'
ISIMP_BIN_DIR = ISIMP_DIR + 'bin'
ISIMP_LIB_DIR = ISIMP_DIR + 'lib'

TMP_FILENAME = 'isimp.tmp'
TMP_OUT_FILENAME = 'isimp.out.tmp'

class iSimpWrapper:

    __isimp_location = None

    def __init__(self):
        self.__isimp_location = self.__det_location()

    def __det_location(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), ISIMP_DIR)

    def run_isimp(self, sentence, verbose):
        tmp_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), TMP_FILENAME)
        tmp_out_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), TMP_OUT_FILENAME)

        if verbose:
            print('iSimp temporary files: {}, {}'.format(tmp_filename, tmp_out_filename))

        with open(tmp_filename, 'w') as tmp:
            tmp.write(sentence)
            tmp.close()

        tmp_out_file = open(tmp_out_filename, 'w').close() # Cleanup

        source_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        os.chdir(self.__isimp_location)

        jars = './lib/*:./bin'
        command = 'java -Xmx1024m -classpath ' + jars + ' main.Console -json -tokenized {} {}'.format(tmp_filename, tmp_out_filename)

        if verbose:
            print('iSimp command: {}'.format(command))
            java_process = Popen(command, stdout=stderr, shell=True)
        else:
            java_process = Popen(command, stdout=stderr, stderr=open(os.devnull, 'w'), shell=True)

        java_process.wait()

        os.chdir(current_dir)
        os.remove(tmp_filename)

        assert not java_process.returncode, 'ERROR: iSimp exited with a non-zero code status.'

        with open(tmp_out_filename, 'r') as out_file:
            out_contents = out_file.read()
            out_file.close()

        os.remove(tmp_out_filename)

        return json.loads(out_contents)

