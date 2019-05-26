import os
import requests

from argparse import ArgumentParser
from commands import getoutput
from subprocess import Popen
from sys import argv
from sys import stderr

def train(prop_filename=None):
    assert not prop_filename is None, 'ERROR: Must specify a properties file!'

    source_dir = os.path.dirname(os.path.abspath(__file__))

    jars_dir = source_dir + '/..'
    jars = '{0}/stanford-corenlp.jar:{0}/stanford-corenlp-models.jar:{0}/slf4j-api.jar:{0}/slf4j-simple.jar:{0}/ejml.jar'.format(jars_dir)

    command = 'java -mx5g' + \
              ' -cp "' + jars + '" edu.stanford.nlp.ie.crf.CRFClassifier' + \
              ' -prop {}'.format(prop_filename)

    print('Stanford NER training command: {}'.format(command))
    java_process = Popen(command, stdout=stderr, shell=True)

    java_process.wait()

def main(argv):
    arg_p = ArgumentParser('python train.py', description='Trains and generates a model file for Stanford NER')
    arg_p.add_argument('-p', '--props', type=str, default=None, help='Properties file')

    args = arg_p.parse_args(argv[1:])
    prop_filename = args.props

    if prop_filename is None:
        prop_filename = 'ner.prop'

    train(prop_filename)

if __name__ == '__main__':
    exit(main(argv))
