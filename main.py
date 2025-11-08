from test.dorf import sigma
from pymupdf4llm import to_markdown
from argparse import *
from pathlib import *
from time import *

def main(**kwargs):
    """
    Main epic program head that fire toatly 
    :author: will otterbein
    """

    start = time()
    md = to_markdown(kwargs['file'])
    end = time()
    print(f'Goated 🔥🐏🐏🐏 {end - start}')
    Path(kwargs['ofile']).write_bytes(md.encode())

if __name__ == '__main__':
    args = ArgumentParser('dummy')
    args.add_argument('--file', required=True, help='this is a file')
    args.add_argument('--ofile', required=True, help='this is the new file')

    pargs = args.parse_args()

    main(**(vars(pargs)))
