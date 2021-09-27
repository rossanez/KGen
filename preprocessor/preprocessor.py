import contractions
import os
import re
import unidecode

from argparse import ArgumentParser
from bs4 import BeautifulSoup
from sys import argv
from sys import path

from abbrevresolver import AbbrevResolver
from corefresolver import CorefResolver
from simplifier import Simplifier

path.insert(0, '../')
from common.nlputils import NLPUtils

ENUM_REGEX = re.compile(r"\(\s*(i|v|[0-9])+\s*\)", re.IGNORECASE)
ENUM_ALPHA_LOWER_REGEX = re.compile(r"\(\s*[a-e]\s*\)")
BRACKETS_REGEX = re.compile(r"(\{\[\]\})")
REF_REGEX = re.compile(r"\[\s*[0-9]+\s*\]")
ETC_REGEX = re.compile(r"\,\s*etc\s*\.")
EG_REGEX = re.compile(r"\,\s*e\.g\.\s*\,")
IE_REGEX = re.compile(r"\,\s*i\.e\.\s*\,")
CHARS_REGEX = re.compile(r"(\\|\/|\{|\}|\[|\]|\+|\*|\&|\^|\~)")

class Preprocessor:

    def preprocess(self, input_filename, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {}'.format(input_filename))
        with open(input_filename, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        contents = self.__remove_html_tags(contents)
        contents = self.__remove_accented_chars(contents)
        contents = self.__expand_contractions(contents)

        out = ENUM_REGEX.sub('', contents.replace('%', ' percent'))
        out = ENUM_ALPHA_LOWER_REGEX.sub('', out)
        out = REF_REGEX.sub('', out)
        out = ETC_REGEX.sub('', out)
        out = EG_REGEX.sub(', and', out)
        out = IE_REGEX.sub(', and', out)
        out = CHARS_REGEX.sub('', out)

        coref_resolver = CorefResolver(out)
        abbrev_resolver = AbbrevResolver(coref_resolver.resolve(verbose))
        simplified_contents = Simplifier(NLPUtils.adjust_tokens(abbrev_resolver.resolve(verbose))).simplify(verbose)

        output_filename = os.path.splitext(input_filename)[0] + '_preprocessed.txt'
        with open(output_filename, 'w') as output_file:
            output_file.write(simplified_contents)
            output_file.close()

        print('Preprocessed text stored at {}'.format(output_filename))

        return output_filename

    def __remove_html_tags(self, text):
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ")

    def __remove_accented_chars(self, text):
        return unidecode.unidecode(text)

    def __expand_contractions(self, text):
        return contractions.fix(text)

def main(args):
    arg_p = ArgumentParser('python preprocessor.py', description='Preprocess an unstructured text.')
    arg_p.add_argument('Filename', metavar='filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.Filename
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    preprocessor = Preprocessor()
    preprocessor.preprocess(filename, verbose)

if __name__ == '__main__':
    exit(main(argv))

