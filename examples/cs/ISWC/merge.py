import os

from argparse import ArgumentParser
from pathlib import Path
from sys import argv

def merge_files(number):
    merged_triples_file = 'merged_triples.txt'
    merged_links_file = 'merged_links.txt'

    number = str(int(number))
    if int(number) < 10:
        number = '0{}'.format(number) # So we have '00' , '01', '02' and so forth.

    local_dir = os.path.dirname(os.path.abspath(__file__))
    spec_dir = '{}/{}'.format(local_dir, number)

    merged_triples_file = '{}/{}'.format(local_dir, merged_triples_file)
    merged_links_file = '{}/{}'.format(local_dir, merged_links_file)

    current_triples_file = '{}/{}'.format(spec_dir, 'abs_preprocessed_triples.txt')
    current_links_file = '{}/{}'.format(spec_dir, 'abs_preprocessed_links.txt')

    with open(merged_triples_file, 'a') as out_triples_file:
        with open(current_triples_file) as curr_file:
            for line in curr_file:
                line_contents = line.split('\t')
                updated_index = '{}.{}'.format(number, line_contents[0])
                out_triples_file.write('{}\t{}\t{}\t{}'.format(updated_index, line_contents[1], line_contents[2], line_contents[3]))


    all_link_lines = []
    if Path(merged_links_file).is_file(): # check if exists
        with open(merged_links_file, 'r') as out_links_file:
            all_link_lines += out_links_file.readlines()
            with open(current_links_file, 'r') as curr_file:
                all_link_lines += curr_file.readlines()
        all_link_lines = set(all_link_lines)

    with open(merged_links_file, 'w') as out_links_file:
        out_links_file.write(''.join(all_link_lines))

    print('Processed contents of: {}'.format(number))

def main(args):
    arg_p = ArgumentParser('python merge.py', description='Will merge triples and links files.')
    arg_p.add_argument('-d', '--delta', type=str, default=None, help='Delta of articles (e.g. 1,29)')

    args = arg_p.parse_args(args[1:])
    delta = args.delta

    if delta is None:
        print('Delta required!')
        exit(1)

    indexes = delta.split(',')
    for number in range (int(indexes[0]), int(indexes[1])+1):
        merge_files(number)

if __name__ == '__main__':
    exit(main(argv))
