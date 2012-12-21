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

def acceptance_tests(interpreter, args):
    runner = {'python': 'pybot', 'jython': 'jybot', 'ipy': 'ipybot'}[interpreter]
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
    if not len(sys.argv) > 1:
        print "Usage: run_tests.py python|jython"
        sys.exit(1)
    interpreter = sys.argv[1]
    args = sys.argv[2:]
    acceptance_tests(interpreter, args)