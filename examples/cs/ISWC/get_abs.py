import os
import requests

from argparse import ArgumentParser
from bs4 import BeautifulSoup
from subprocess import Popen, PIPE
from sys import argv
from sys import stderr

def extract_abstract(base_url, number):
    if number is None:
        url = base_url
    else:
        url = '{}_{}'.format(base_url, number)

    abs_out_file = 'abs.txt'
    refs_out_file = 'references.txt'
    if not number is None:
        number = str(int(number)-1)
        if int(number) < 10:
            number = '0{}'.format(number) # So we have '00' , '01', '02' and so forth.

        local_dir = os.path.dirname(os.path.abspath(__file__))
        spec_dir = '{}/{}'.format(local_dir, number)
        if not os.path.exists(spec_dir):
            os.mkdir(spec_dir)

        abs_out_file = '{}/{}'.format(spec_dir, abs_out_file)
        refs_out_file = '{}/{}'.format(spec_dir, refs_out_file)

    r = requests.get(url)
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')
    # This format is true for the springer front page (as of jul/2020)
    abstract = soup.find('section', class_='Abstract').find('p', class_='Para').text

    command = 'echo "{}" | detex'.format(abstract)
    detex_process = Popen([command, '-p'], stdout=PIPE, shell=True)
    detex_out = detex_process.communicate()[0]

    out = detex_out.decode("utf-8")

    with open(abs_out_file, 'w') as output_abs_file:
        output_abs_file.write(out)
        output_abs_file.close()

    with open(refs_out_file, 'w') as output_refs_file:
        output_refs_file.write(url)
        output_refs_file.close()

    print('Stored contents of {} as:'.format(url))
    print(' - {}'.format(abs_out_file))
    print(' - {}'.format(refs_out_file))

def main(args):
    arg_p = ArgumentParser('python get_abs.py', description='Gets the abstract for springer')
    arg_p.add_argument('-u', '--url', type=str, default=None, help='The base url')
    arg_p.add_argument('-n', '--number', type=str, default=None, help='The article number within the base url (default None)')
    arg_p.add_argument('-d', '--delta', type=str, default=None, help='Delta of articles (e.g. 1,29)')

    args = arg_p.parse_args(args[1:])
    url = args.url
    number = args.number
    delta = args.delta

    if url is None:
        print('No URL provided.')
        exit(1)

    if not delta is None:
        indexes = delta.split(',')
        for number in range (int(indexes[0]), int(indexes[1])+1):
            extract_abstract(url, number)
    else:
        extract_abstract(url, number)

if __name__ == '__main__':
    exit(main(argv))
