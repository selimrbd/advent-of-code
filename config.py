from dotenv import load_dotenv
from pathlib import Path 

def load_config():
    p = Path(__file__).parent/'.env'
    load_dotenv()