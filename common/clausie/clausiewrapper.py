import os

from subprocess import Popen
from sys import stderr

class ClausIEWrapper:

    @staticmethod
    def run_clausie(input_filename, output_filename, verbose=False):
        source_dir = os.path.dirname(os.path.abspath(__file__))

        jars = '{0}/clausie:{0}/clausie/build:{0}/clausie/clausie_lib/stanford-parser.jar:{0}/clausie/clausie_lib/stanford-parser-2.0.4-models.jar:{0}/clausie/clausie_lib/jopt-simple-4.4.jar'.format(source_dir)

        command = 'java -cp "' + jars + '" de.mpii.clausie.ClausIE -f {} -l -o {}'.format(input_filename, output_filename)

        if verbose:
            print('ClausIE command: {}'.format(command))
            java_process = Popen(command, stdout=stderr, shell=True)
        else:
            java_process = Popen(command, stdout=stderr, stderr=open(os.devnull, 'w'), shell=True)

        java_process.wait()

        assert not java_process.returncode, 'ERROR: ClausIE exited with a non-zero code status.'

        if verbose:
            with open(output_filename, 'r') as out_file:
                out_contents = out_file.read()
                out_file.close()
            print(out_contents)

        return output_filename
