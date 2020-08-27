import copy
import json
import os
import re

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

############################ Below is highly inspired by the generate_sentences.py script from https://github.com/bionlplab/isimp

    def generate_simpler_sentences(self, sentence):
        simplified_contents = []
        total_sentences = []
        self.__simplify_helper(sentence, total_sentences)
        sentences_text = set(s['TEXT'] for s in total_sentences)
        for s in sentences_text:
            s = re.sub('\\s+', ' ', s)
            s = re.sub('\\n', ' ', s)
            s = s.strip()#.capitalize()
            if len(s) == 0:
                continue
            if s[-1] != '.':
                s += '.'
            simplified_contents.append(s)

        return '\n'.join(simplified_contents)

    def __simplify_helper(self, sentence, total_simp_sentences):
        if len(sentence['SIMP']) == 0:
            total_simp_sentences.append(sentence)
            return
        simp_idx = len(sentence['SIMP'])
        simp = sentence['SIMP'].pop(-1)
        if simp['TYPE'] == 'parenthesis':
            ss = self.__process_parenthesis(sentence, simp)
        elif 'relative' in simp['TYPE']:
            ss = self.__process_relative(sentence, simp)
        elif 'coordination' in simp['TYPE']:
            ss = self.__process_coordination(sentence, simp)
        elif simp['TYPE'] == 'member-collection':
            ss = [sentence]
        elif simp['TYPE'] == 'hypernymy':
            ss = [sentence]
        elif simp['TYPE'] == 'apposition':
            ss = self.__process_apposition(sentence, simp)
        else:
            print('Cannot parse type: {}'.format(simp['TYPE']))
            ss = [sentence]
        for i, s in enumerate(ss):
            s['id'] = '{simp_idx}/{i}'
            self.__simplify_helper(s, total_simp_sentences)

    def __process_parenthesis(self, sentence, simp):
        sentences = []
        begin = sentence['FROM']
        for comp in simp['COMP']:
            if comp['TYPE'] in ('referred noun phrase', 'parenthesized elements'):
                s = copy.deepcopy(sentence)
                text = s['TEXT']
                text = self.__repl_space(text, simp['FROM'] - begin, simp['TO  '] - begin + 1)
                text = self.__repl_text(text, sentence['TEXT'], comp['FROM'] - begin, comp['TO  '] - begin)
                s['TEXT'] = text
                sentences.append(s)
            else:
                raise KeyError(comp['TYPE'])
        return sentences


    def __process_apposition(self, sentence, simp):
        sentences = []
        begin = sentence['FROM']
        for comp in simp['COMP']:
            if comp['TYPE'] in ('referred noun phrase', 'appositive'):
                s = copy.deepcopy(sentence)
                text = s['TEXT']
                text = self.__repl_space(text, simp['FROM'] - begin, simp['TO  '] - begin)
                text = self.__repl_text(text, sentence['TEXT'], comp['FROM'] - begin, comp['TO  '] - begin)
                s['TEXT'] = text
                sentences.append(s)
            else:
                raise KeyError(comp['TYPE'])
        return sentences


    def __process_coordination(self, sentence, simp):
        sentences = []
        begin = sentence['FROM']
        for comp in simp['COMP']:
            if comp['TYPE'] in ('conjunct', ):
                s = copy.deepcopy(sentence)
                text = s['TEXT']
                text = self.__repl_space(text, simp['FROM'] - begin, simp['TO  '] - begin + 1)
                text = self.__repl_text(text, sentence['TEXT'], comp['FROM'] - begin, comp['TO  '] - begin)
                s['TEXT'] = text
                sentences.append(s)
            elif comp['TYPE'] in ('conjunction', ):
                pass
            else:
                raise KeyError(comp['TYPE'])
        return sentences


    def __process_relative(self, sentence, simp):
        sentences = []
        begin = sentence['FROM']
        np = None
        for comp in simp['COMP']:
            if comp['TYPE'] in ('referred noun phrase', ):
                np = comp
                s = copy.deepcopy(sentence)
                text = s['TEXT']
                text = self.__repl_space(text, simp['FROM'] - begin, simp['TO  '] - begin + 1)
                text = self.__repl_text(text, sentence['TEXT'], comp['FROM'] - begin, comp['TO  '] - begin)
                s['TEXT'] = text
                sentences.append(s)
            elif comp['TYPE'] in ('clause', ):
                s = copy.deepcopy(sentence)
                text = ' ' * len(s['TEXT'])
                text = self.__repl_text(text, sentence['TEXT'], comp['FROM'] - begin, comp['TO  '] - begin)
                text = self.__repl_text(text, sentence['TEXT'], np['FROM'] - begin, np['TO  '] - begin)
                s['TEXT'] = text
                sentences.append(s)
            else:
                raise KeyError(comp['TYPE'])
        return sentences

    def __repl_space(self, s, begin, end):
        return s[:begin] + ' ' * (end - begin) + s[end:]

    def __repl_text(self, s, target, begin, end):
        return s[: begin] + target[begin: end] + s[end:]
