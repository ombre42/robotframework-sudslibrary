import testenv
import os
import sys
import subprocess


ROBOT_ARGS = [
    '--doc', 'SudsLibrary_Acceptance_Tests',
    '--outputdir', testenv.RESULTS_DIR,
    '--log', 'none',
    '--pythonpath', testenv.SRC_DIR,
]

def acceptance_tests(args):
    runner = 'pybot'
    if os.sep == '\\':
        runner += '.bat'
    _make_results_dir()
    cmd = [runner] + ROBOT_ARGS + args + [testenv.TEST_DATA]
    print "Executing:\n" + " ".join(cmd)
    subprocess.check_output(cmd)
    
def _make_results_dir():
    if not os.path.exists(testenv.RESULTS_DIR):
        os.mkdir(testenv.RESULTS_DIR)

if __name__ ==  '__main__':
    args = sys.argv[1:]
    acceptance_tests(args)
