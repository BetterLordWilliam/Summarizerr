from test.dorf import sigma
from pymupdf4llm import to_markdown
from requests import *
from argparse import *
from pathlib import *
from time import *
from obsidianify import push_to_obsidian


INPUT_FILE_HELP     = 'this is the input file parameter for this cli utility'
OUTPUT_FILE_HELP    = 'this is the output file parameter for this cli utility' 
TOKEN_HELP          = 'this is the token parameter for this cli utility'
TEMP_HELP           = 'this is the temperature (creativity) parameter for this cli utility'
API_KEY_HELP        = 'this is the api key provided by the obsidian local REST API plugin'

# summarize_endpoint  = 'https://summarizer.blindy.net/summarize'
summarize_endpoint  = 'http://localhost:8000/summarize'
model_response_bad  = 'response from the model was absolutely cooked'
model_response_what = 'response from the model was erroneous and maddening'


def send_md_to_model(md: str, tokens: int, temp: float) -> Response:
    response = post(summarize_endpoint, json={
        "input": md,
        "max_tokens": tokens,
        "temperature": temp
    })

    print(response.headers)
    print(response.status_code)
    print(response.text)
    # print(response)

    if (response.status_code - 200 > 100):
        raise Exception(model_response_bad)
    if (response.status_code - 200 < 0):
        raise Exception(model_response_what)

    print(response.text)

    return response

def write_model_response(path: str, response: Response):
    summary = response.json()['summary']
    Path(path).write_text(summary, encoding='utf-8')

def main(**kwargs):
    start = time()
    md = to_markdown(kwargs['file'])
    end = time()
    print(f'parse time: {end - start}')
    
    start = time() 
    model_response = send_md_to_model(md, kwargs.get('mrts', 4096), kwargs.get('temp', 0.5))
    end = time()
    print(f'model generation time: {start - end}')
    
    start = time()
    write_model_response(kwargs['ofile'], model_response)
    end = time()
    print(f'write time: {start - end}')

    api_key = kwargs.get('api')
    if api_key:
        print('\npushing to obsidian because api key passed')
        try:
            filename = Path(kwargs['file']).stem
            summary = model_response.json()['summary']
            result = push_to_obsidian(summary, api_key, filename)
            print(f'obsidianified successfully {result}')
        except Exception as err:
            print(f'failed to obsidianify: {err}')
        

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
                    default=32768,
                    required=False,
                    help=TOKEN_HELP)
    args.add_argument('--temp',
                    type=float,
                    default=0.1,
                    required=False,
                    help=TEMP_HELP)
    args.add_argument('--api',
                    type=str,
                    required=False,
                    help=API_KEY_HELP)

    pargs = args.parse_args()

    main(**(vars(pargs)))
