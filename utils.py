### COMMENT IN SOLVEIT ########
from config import load_config
load_config()
###############################

YEAR = 2024

from llms import ClaudeClient
from IPython.display import Markdown
import requests
from bs4 import BeautifulSoup
import os
import re

from typing import Optional

import webbrowser
import os
from aocd import get_puzzle, submit


REPHRASE_SYSTEM_PROMPT = '\n'.join([
        "Hello, my name is Selim. We will be solving together Advent of Code puzzles",
        "I will give you as input the description of the puzzle",
        "Rephrase the problem as concisely as possible, while keeping it clear",
        "Only output what was asked from you in the instructions below",
        "Be careful about each key word to rephrase the problem without mistakes",
        "Display what the input looks like, using the exact example provided",
        "To simplify reading, put a \n after each sentence, and set in **bold** important elements",
        #"- DISPLAY WALKTHROUGH: If a walkthrough of the example is given:",
        #"at the end of the rephrasing, reprint the FULL given example and expected answer, as well as the walkthrough",
])

def setup(day, year=2024):
    AOC_SESSION = os.getenv('AOC_SESSION')
    assert AOC_SESSION is not None, "missing AOC_SESSION"
    puzzle = get_puzzle(AOC_SESSION,day=day,year=year)
    out = {}
    out["link"] = f"https://adventofcode.com/{year}/day/{day}"
    out["data"] = puzzle.input_data
    out["exmp"] = puzzle.examples[0].input_data
    out["ae1"] = puzzle.examples[0].answer_a
    out["ae2"] = puzzle.examples[0].answer_b
    out["exmps"] = puzzle.examples
    out["nb_exmps"] = len(puzzle.examples)
    print(f'nb examples: {out["nb_exmps"]}')

    def open_puzzle():
        webbrowser.open(out["link"])
    return (open_puzzle, out["data"], out["exmp"], out["ae1"], out["ae2"], out["exmps"], out)


def get_pb_desc(day: int, year: int = YEAR) -> str:

    session = os.getenv('AOC_SESSION')
    
    url = f"https://adventofcode.com/{year}/day/{day}"
    
    headers = {
        'Cookie': f'session={session}',
        #'User-Agent': 'github.com/your-username by your@email.com'  # Replace with your info
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.find_all('article', class_='day-desc')
        
        pb_desc = '\n\n'.join(article.get_text() for article in articles)
         
        # pat = r"(--- Day \d+: [^-]+ ---)"
        # mat = re.match(pat, pb_desc).group(0)
        # pb_desc = re.sub(pat, mat+'\n', pb_desc).strip()
        
        return pb_desc
        
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch problem description: {e}")

async def _rephrase_pb(pb_desc: str, prompt = REPHRASE_SYSTEM_PROMPT) -> str:
    claude = ClaudeClient(prompt)
    reph = await claude.send(pb_desc)
    return Markdown(reph)

async def rephrase_pb(day: int, year: int = YEAR, part: int = 1, prompt = REPHRASE_SYSTEM_PROMPT):
    pb_desc = get_pb_desc(day, year)
    pt2_anchor = '--- Part Two ---'
    idx = 1 if part == 2 else 0
    pb_desc = pb_desc.split(pt2_anchor)[idx]
    return await _rephrase_pb(pb_desc, prompt)