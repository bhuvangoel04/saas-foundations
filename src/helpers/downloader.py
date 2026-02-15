# downloads static vendor files into your project during deployment

import requests
from pathlib  import Path

# download files from url to local  
def download_to_local(url:str, out_path:Path, parent_mkdir:bool=True):
    if not isinstance(out_path, Path):
        raise ValueError(f"{out_path} must be a valid pathlib.PathObject")
    # auto create parent directory
    if parent_mkdir:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        # write the file in binary to prevent inline conversions
        out_path.write_bytes(response.content)
        return True
    except requests.RequestException as e:
        print(f"Failed to download {url}:{e}")
        return False
