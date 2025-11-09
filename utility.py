from pymupdf4llm import to_markdown
import requests as R
import aiohttp
import asyncio
import aiofiles
import pathlib
import pathlib  as P

SUMMARIZE_ENDPOINT = 'https://tommye-summitless-nonamorously.ngrok-free.dev/summarize'
MODEL_RESPONSE_BAD  = 'response from the model was absolutely cooked'

async def to_markdown_async(filepath: str) -> str:
    """
    Converts a file to markdown format asynchronously.
    """
    return await asyncio.to_thread(to_markdown, filepath)

async def send_md_to_model(md: str, tokens: int, temp: float) -> dict:
    """
    Sends markdown content to the summarization model endpoint asynchronously.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(SUMMARIZE_ENDPOINT, json={
            'input': md,
            'max_tokens': tokens,
            'temperature': temp
        }) as resp:
            print(resp.headers)
            print(resp.status)
            
            try:
                print(await resp.text())
                print(await resp.json())
            except Exception as e:
                print(e)
    
            if (not resp.ok):
                raise Exception(MODEL_RESPONSE_BAD)

            return await resp.json()

async def write_model_response(oldfile: str, path: str, md_content: str):
    """
    Writes the model response markdown content to a file asynchronously.
    """
    oldfilepath = pathlib.Path(oldfile)
    oldfilename = oldfilepath.name.split('.')[0]
    
    async with aiofiles.open(f'{path}/{oldfilename}.md', mode='w') as file:
        await file.write(md_content) 
