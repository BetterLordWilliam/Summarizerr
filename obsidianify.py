import requests
from pathlib import Path
from datetime import datetime

def push_to_obsidian(
    content: str,
    api_key: str,
    filename: str,
    base_url: str = "http://127.0.0.1:27123"
) -> dict:
    """
    push the response from the model into the obsidian vault
    args:
        content: the text from the model
        api_key: obisidian local REST API api key
        filename: name of the file with or without extension bruh
        base_url: API endpoint
    """

    if not filename.endswith('.md'):
        filename = f"{filename}.md"

    url = f"{base_url}/vault/{filename}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "text/markdown"
    }

    payload = {
        "content": content
    }

    response = requests.put(
        url,
        headers=headers,
        data=content.encode('utf-8'),
        verify=False
    )

    response.raise_for_status()
    print(response)
    
    return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("usage: python obsidianify.py <file> <api_key> <filename>")
        sys.exit(1)
    
    content = Path(sys.argv[1]).read_text(encoding='utf-8')
    result = push_to_obsidian(content, sys.argv[2], sys.argv[3])
    print(f"created {result}")
