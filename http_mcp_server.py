from fastmcp import FastMCP
from pathlib import Path
import logging
import warnings
import asyncio

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("fastmcp").setLevel(logging.WARNING)

mcp = FastMCP("HTTP File server.")

"""
    The top-level directories 
    that the server is allowed to access.
"""
BASE_DIR = Path(__file__).parent / "workspace"

BASE_DIR.mkdir(exist_ok=True)


def is_within_roots(path:Path)->bool:
    """
        check if the path within allowed roots directory.
    """
    try:
        path.resolve().relative_to(BASE_DIR.resolve())
        return True
    except Exception as e:
        return False


@mcp.tool(name="read_file", description="this tool helps to read an existing file")
def read_file(file_path:str)->str:
    path = BASE_DIR /  file_path
    if not is_within_roots(path):
        return f"Error: Access denied - path outside workspace roots"
    
    elif not path.exists():
        return f"Error : the path proived doesn't exist." 
    
    else:
        try:
            content = path.read_text()
            return content
        except Exception as e:
            return f"Error: {e}"
        
@mcp.tool(name="write_file", description="this tool hepls to write a content on file.")
def write_file(file_path:str, content:str):
    path = BASE_DIR / file_path
    
    if not is_within_roots(path):
        return f"Error: Access denied - path outside workspace roots"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool(name="list_files", description="List files in a directory within the workspace.")
def list_files(directory:str="."):
    path = BASE_DIR / directory
    
    if not is_within_roots(path):
        return f"Error: Access denied - path outside workspace roots"

    if not path.exists():
        return f"Error: Directory not found: {directory}"

    if not path.is_dir():
        return f"Error: Not a directory: {directory}"
    try:
        files = []
        
        for item in sorted(path.iterdir()):
            relative_path = item.relative_to(BASE_DIR)
            type = "DIR" if item.is_dir() else "FILE"
            size = item.stat().st_size if item.is_file() else 0
            files.append(f"{type}: {relative_path} ({size} bytes)")
            return "\n".join(files) if files else "Directory is empty"

    except Exception as e:
        return f"Error listing directory: {str(e)}"




if __name__ == "__main__":
    asyncio.run(mcp.run_http_async(port=8080))
