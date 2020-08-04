import os

from platform import architecture, system
from subprocess import Popen
from sys import stderr

SENNA_DIR = 'senna/'

TMP_FILENAME = 'senna.tmp'
TMP_OUT_FILENAME = 'senna.out.tmp'

class SennaWrapper:

    __senna_executable = None
    __senna_location = None

    def __init__(self):
        self.__senna_location = self.__det_location()
        self.__senna_executable = self.__det_executable()

    def __det_location(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), SENNA_DIR)

    def __det_executable(self):
        os_name = system()

        executable = ''
        if os_name == 'Linux':
            bits = architecture()[0]
            if bits == '64bit':
                executable='senna-linux64'
            elif bits == '32bit':
                executable='senna-linux32'
            else:
                executable='senna'
        elif os_name == 'Windows':
            executable='senna-win32.exe'
        elif os_name == 'Darwin':
            executable='senna-osx'
        else:
        	raise Exception("Unable to determine the current OS!")

        return os.path.join(self.__senna_location, executable)

    def srl(self, sentence, verbose=False):
        tmp_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), TMP_FILENAME)
        tmp_out_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), TMP_OUT_FILENAME)

        if verbose:
            print('SENNA temporary files: {}, {}'.format(tmp_filename, tmp_out_filename))

        with open(tmp_filename, 'w') as tmp:
            tmp.write(sentence)
            tmp.close()
        tmp_file = open(tmp_filename, 'r')

        tmp_out_file = open(tmp_out_filename, 'w')

        command = self.__senna_executable + ' -srl -usrtokens '

        current_dir = os.getcwd()
        os.chdir(self.__senna_location)

        if verbose:
            print('SENNA command: {}'.format(command))
            process = Popen(command, stdin=tmp_file, stdout=tmp_out_file, shell=True)
        else:
            process = Popen(command, stdin=tmp_file, stdout=tmp_out_file, stderr=open(os.devnull, 'w'), shell=True)

        process.wait()
        out, err = process.communicate()

        os.chdir(current_dir)

        if verbose:
            print('Removing SENNA temporary files...')

        tmp_file.close()
        os.remove(tmp_filename)
        tmp_out_file.close()

        assert not process.returncode, 'ERROR: SENNA exited with a non-zero code status.'

        with open(tmp_out_filename, 'r') as out_file:
            pred_list = list()
            predicates = {}
            for line in out_file.readlines():
                line_list = line.split()
                if len(line_list) > 1 and not line_list[1] == '-':
                    predicates[line_list[1]] = []
                    pred_list.append(line_list[1]) # list to iterate later - dictionary will not keep keys in order

            out_file.seek(0)
            for line in out_file.readlines():
                line_list = line.split()
                if len(line_list) < 1: continue

                term = line_list[0]

                pred_offset = 1
                pred_index = 0
                for key in pred_list: # iterate over list instead of dictionary
                    pred_dict = predicates[key]
                    pred_index += 1
                    srl_tag = line_list[pred_offset + pred_index]

                    if not (srl_tag == 'O' or srl_tag == 'S-V'):
                        srl = '-'.join(srl_tag.split('-')[1:])

                        if srl_tag.startswith('S-') or srl_tag.startswith('B-'): # Single occurrence or beginning of a composite.
                            pred_dict.append((srl, term))
                            predicates[key] = pred_dict
                            continue

                        last_tuple = pred_dict[-1]
                        pred_dict[-1] = (srl, last_tuple[1] + ' ' + term)
                        predicates[key] = pred_dict

            out_file.close()
            os.remove(tmp_out_filename)

        return predicates
