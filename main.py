from pymupdf4llm import to_markdown
import asyncio
import requests as R
import argparse as A
import pathlib  as P
import time     as T
import utility  as U
import terminalUI

"""
TODO 
- figure out how many files the user wants to convert and generate summaries for
- create that many tasks for converting to markdown
- create that many tasks for sending the response to the model
- create that many tasks for writing to the output file

given by user everytime
    - List of file to summarise
    - Output directory
Same file names

"""

INPUT_FILE_HELP     = 'this is the input file parameter for this cli utility'
OUTPUT_FILE_HELP    = 'this is the output file parameter for this cli utility' 
TOKEN_HELP          = 'this is the token parameter for this cli utility'
TEMP_HELP           = 'this is the temperature (creativity) parameter for this cli utility'
API_KEY_HELP        = 'this is the api key provided by the obsidian local REST API plugin'

# async def main(**kwargs):
#     tokens = kwargs['mrts'] 
#     temp = kwargs['temp']
    
#     md = asyncio.create_task(U.to_markdown_async(kwargs['file']))
#     md_result = await md
    
#     model_response = asyncio.create_task(U.send_md_to_model(md_result, tokens, temp))
#     model_response_result = await model_response
    
#     file_write = asyncio.create_task(U.write_model_response(kwargs['ofile'], model_response_result))
#     file_write_result = await file_write
    
if __name__ == '__main__':
    args = A.ArgumentParser('')

    args.add_argument('--filee',
                    type=str,
                    required=False,
                    help=INPUT_FILE_HELP)
    args.add_argument('--ofilee',
                    type=str,
                    required=False,
                    help=OUTPUT_FILE_HELP)
    args.add_argument('--mrts',
                    type=int,
                    default=4096,
                    required=False,
                    help=TOKEN_HELP)
    args.add_argument('--temp',
                    type=float,
                    default=0.5,
                    required=False,
                    help=TEMP_HELP)
    args.add_argument('--api',
                    type=str,
                    required=False,
                    help=API_KEY_HELP)

    pargs = args.parse_args()
    
    tui = terminalUI.SummarizerApp(**(vars(pargs)))
    tui.run()

    # asyncio.run(main(**(vars(pargs))))
