from pymupdf4llm import to_markdown
import asyncio
import requests as R
import argparse as A
import pathlib  as P
import time     as T
import utility  as U
import terminalUI

INPUT_FILE_HELP     = 'this is the input file parameter for this cli utility'
OUTPUT_FILE_HELP    = 'this is the output file parameter for this cli utility' 
TOKEN_HELP          = 'this is the token parameter for this cli utility'
TEMP_HELP           = 'this is the temperature (creativity) parameter for this cli utility'
API_KEY_HELP        = 'this is the api key provided by the obsidian local REST API plugin'
    
if __name__ == '__main__':
    args = A.ArgumentParser('')

    args.add_argument('--file',
                    type=str,
                    required=False,
                    help=INPUT_FILE_HELP)
    args.add_argument('--odir',
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
    
    tui = terminalUI.SummarizerApp(
        filee       = pargs.file,
        ofilee      = pargs.odir,
        mrts        = pargs.mrts,
        temp        = pargs.temp,
        api_keyy    = pargs.api 
    )
    tui.run()