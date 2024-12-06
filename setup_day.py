import nbformat
import json
from pathlib import Path
import fire 
from pathlib import Path
import subprocess, platform
from config import PATH_TEMPLATE, PATH_WORKSPACE
from utils import build_aoc_link, open_link, download_page, get_pb_data
import json 


def create_notebook_from_template(year: int, day: int, path_out: Path|str, path_template: Path = PATH_TEMPLATE) -> None:
    
    if isinstance(path_out, str): path_out = Path(path_out)
    with open(path_template, 'r', encoding='utf-8') as f: notebook = nbformat.read(f, as_version=4)
    
    notebook_json = json.dumps(notebook)
    
    
    notebook_json = notebook_json.replace('${YEAR}', str(year))
    notebook_json = notebook_json.replace('${DAY}', str(day))

    updated_notebook = nbformat.reads(notebook_json, as_version=4)
    
    with open(path_out, 'w', encoding='utf-8') as f: nbformat.write(updated_notebook, f)


def open_file_in_cursor(path_nb: Path, path_ws: Path = PATH_WORKSPACE):
    cursor_cmd = "cursor" if platform.system() != "Windows" else "cursor.exe"
    cmd = [
        cursor_cmd,
        path_ws,
        '-g',
        path_nb,
    ]
    subprocess.run(cmd)


def setup_day(day: int, year: int, path_cursor_ws: Path = PATH_WORKSPACE) -> None:

    pth_folder = Path(f"{year}/{day}")
    #pth_folder = pth_folder.resolve() #use absolute path
    pth_nb = pth_folder / 'first_try.ipynb'
    pth_html = pth_folder / '_puzzle.html'
    pth_data = pth_folder / '_puzzle_data.json'
    if not pth_folder.exists():
        pth_folder.mkdir(parents=True)
    
    if not pth_nb.exists(): 
        create_notebook_from_template(year, day, pth_nb)
    else: 
        print(f'WARNING:  Notebook "{pth_nb}" already exists')
    
    open_file_in_cursor(pth_nb, path_cursor_ws)
    link, _, _, _, _, _, out = get_pb_data(day, year)
    download_page(link, pth_html)
    with open(pth_data, 'w') as f: f.write(json.dumps(out))
    open_link(link)
    


    print(f'local puzzle.html: file://{pth_html.resolve()}')


if __name__ == '__main__':
    fire.Fire(setup_day)