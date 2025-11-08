from test.dorf import sigma
from pymupdf4llm import to_markdown
from requests import *
from argparse import *
from pathlib import *
from time import *


INPUT_FILE_HELP     = 'this is the input file parameter for this cli utility'
OUTPUT_FILE_HELP    = 'this is the output file parameter for this cli utility' 

summarize_endpoint  = 'https://summarizer.blindy.net/summarize'
model_response_bad  = 'response from the model was absolutely cooked'
model_response_what = 'response from the model was erroneous and maddening'


def send_md_to_model(md: str) -> Response:
    response = post(summarize_endpoint, json={
        "input": md,
        "max_tokens": 1024,
        "temperature": 0.5
    })

    print(response.headers)
    print(response.status_code)
    # print(response)

    if (response.status_code - 200 > 100):
        raise Exception(model_response_bad)
    if (response.status_code - 200 < 0):
        raise Exception(model_response_what)

    print(response.text)

    return response

def write_model_response(path: str, response: str):
    Path(path).write_bytes(response.encode())

def main(**kwargs):
    start = time()
    md = to_markdown(kwargs['file'])
    end = time()

    model_response = send_md_to_model(md)
    write_model_response(kwargs['ofile'], model_response)

    print(f'eta: {end - start}')
    # Path(kwargs['ofile']).write_bytes(md.encode())


if __name__ == '__main__':
    args = ArgumentParser('')

    args.add_argument('--file',
                    type=str,
                    required=True,
                    help=INPUT_FILE_HELP)
    args.add_argument('--ofile',
                    type=str,
                    required=True,
                    help=OUTPUT_FILE_HELP)
    args.add_argument('--mrts',
                    type=int,
                    required=False,
                    help='')

    pargs = args.parse_args()

    main(**(vars(pargs)))
