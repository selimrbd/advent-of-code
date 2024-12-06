from dotenv import load_dotenv
from pathlib import Path 

PATH_TEMPLATE = Path(__file__).parent/'template.ipynb'
PATH_WORKSPACE = Path(__file__).parent/'aoc.code-workspace'

def load_config():
    p = Path(__file__).parent/'.env'
    load_dotenv()
