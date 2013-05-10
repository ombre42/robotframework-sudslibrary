import sys
from os.path import abspath, dirname, join


THIS_DIR = dirname(abspath(__file__))
ROOT_DIR = dirname(THIS_DIR)
SRC_DIR = join(ROOT_DIR, "src")
RESULTS_DIR = join(THIS_DIR, "results")
TEST_DATA = join(THIS_DIR, "acceptance")
