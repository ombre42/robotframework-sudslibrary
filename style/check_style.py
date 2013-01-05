from os.path import join, dirname, abspath
import subprocess


THIS_DIR = dirname(abspath(__file__))
SRC_DIR = join(dirname(THIS_DIR), "src", "SudsLibrary")

def check_pep8():
    args = [
        "--max-line-length", "150",
        "."
    ]
    subprocess.call(["pep8"] + args, cwd=SRC_DIR)

if __name__ == "__main__":
    check_pep8()
