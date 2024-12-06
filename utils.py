### COMMENT IN SOLVEIT ########
from config import load_config
load_config()
###############################

from llms import ClaudeClient
from IPython.display import Markdown
import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path

import webbrowser
import os
from aocd import get_puzzle

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

def get_pb_data(day: int, year: int):
    AOC_SESSION = os.getenv('AOC_SESSION')
    assert AOC_SESSION is not None, "missing AOC_SESSION"
    puzzle = get_puzzle(AOC_SESSION,day=day,year=year)
    out = {}
    out["link"] = build_aoc_link(day, year)
    out["data"] = puzzle.input_data
    out["exmp"] = puzzle.examples[0].input_data
    out["ae1"] = puzzle.examples[0].answer_a
    out["ae2"] = puzzle.examples[0].answer_b
    out["exmps"] = puzzle.examples
    out["nb_exmps"] = len(puzzle.examples)
    print(f'nb examples: {out["nb_exmps"]}')

    return (out["link"], out["data"], out["exmp"], out["ae1"], out["ae2"], out["exmps"], out)


def build_aoc_link(day: int, year: int) -> str:
    return f"https://adventofcode.com/{year}/day/{day}"


def open_link(link: str):
    webbrowser.open(link) 


def get_pb_desc(day: int, year: int) -> str:

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


async def rephrase_pb(day: int, year: int, part: int = 1, prompt = REPHRASE_SYSTEM_PROMPT):
    pb_desc = get_pb_desc(day, year)
    pt2_anchor = '--- Part Two ---'
    idx = 1 if part == 2 else 0
    pts = pb_desc.split(pt2_anchor)
    if len(pts) == 1 and part == 2:
        raise ValueError('Part 2 not available yet.')
    pb_desc = pts[idx]
    return await _rephrase_pb(pb_desc, prompt)


def download_page(url, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()
    Path(output_path).write_text(response.text, encoding='utf-8')
    return output_path


import json
import uuid

from IPython.core.display import HTML, display


class RenderJSON(object):
    def __init__(self, json_data):
        if isinstance(json_data, dict):
            self.json_str = json.dumps(json_data)
        else:
            self.json_str = json_data
        self.uuid = str(uuid.uuid4())
        # This line is missed out in most of the versions of this script across the web, it is essential for this to work interleaved with print statements
        self._ipython_display_()

    def _ipython_display_(self):
        display(
            HTML(
                '<div id="{}" style="height: auto; width:100%;"></div>'.format(
                    self.uuid
                )
            )
        )
        display(
            HTML(
                """<script>
        require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {
          renderjson.set_show_to_level(1)
          document.getElementById('%s').appendChild(renderjson(%s))
        });</script>
        """
                % (self.uuid, self.json_str)
            )
        )


def cast_to_string(obj):
    if isinstance(obj, dict):
        return {key: cast_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [cast_to_string(item) for item in obj]
    else:
        return str(obj)


# def render_json(d, return_res=False):
#     e = cast_to_string(d)
#     r = RenderJSON(e)
#     if return_res:
#         return r

# def render_json(d, return_res=False, delete_str=False):
#     def process_value(obj):
#         if isinstance(obj, dict):
#             return {key: process_value(value) for key, value in obj.items()}
#         elif isinstance(obj, list):
#             return [process_value(item) for item in obj]
#         elif delete_str and isinstance(obj, str):
#             return None
#         return str(obj)
    
#     e = process_value(d)
#     r = RenderJSON(e)
#     if return_res:
#         return r
    
def render_json(d, return_res=False):
   def escape_str(obj):
       if isinstance(obj, dict):
           return {key: escape_str(value) for key, value in obj.items()}
       elif isinstance(obj, list):
           return [escape_str(item) for item in obj]
       elif isinstance(obj, str):
           # Escape quotes, newlines and other problematic characters
           return json.dumps(str(obj))[1:-1]  # [1:-1] removes outer quotes
       return str(obj)
   
   e = escape_str(d)
   r = RenderJSON(e)
   if return_res:
       return r
   

from IPython.display import HTML, display
import json, uuid

class RenderJSON:
    def __init__(self, json_data):
        self.json_str = json.dumps(json_data) if isinstance(json_data, dict) else json_data
        self.uuid = str(uuid.uuid4())
        self._ipython_display_()

    def _ipython_display_(self):
        display(HTML(f'<div id="{self.uuid}" style="height: auto; width:100%;"></div>'))
        display(HTML(f"""
        <script>
        require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {{
          renderjson.set_show_to_level(1)
          document.getElementById('{self.uuid}').appendChild(renderjson({self.json_str}))
        }});
        </script>
        """))

def render_json(d, return_res=False):
    try:
        json_str = json.dumps(d)  # Validate JSON serialization
        r = RenderJSON(d)
        return r if return_res else None
    except Exception as e:
        print(f"JSON error: {e}")