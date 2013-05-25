import testenv
import os
import sys
import subprocess
from os.path import join
import robot
import statuschecker


ROBOT_ARGS = [
    '--doc', 'SudsLibrary_Acceptance_Tests',
    '--outputdir', testenv.RESULTS_DIR,
    '--report', 'none',
    '--log', 'none',
    '--pythonpath', testenv.SRC_DIR,
    '--debugfile', join(testenv.RESULTS_DIR, 'syslog.txt')
]

def acceptance_tests(args):
    runner = 'pybot'
    if os.sep == '\\':
        runner += '.bat'
    _make_results_dir()
    cmd = [runner] + ROBOT_ARGS + args + [testenv.TEST_DATA]
    print "Executing:\n" + " ".join(cmd)
    subprocess.call(cmd)
    outputxml = join(testenv.RESULTS_DIR, "output.xml")
    statuschecker.process_output(outputxml)
    rc = robot.rebot(outputxml, outputdir=testenv.RESULTS_DIR)
    if rc == 0:
        print 'All tests passed'
    else:
        print '%d test%s failed' % (rc, 's' if rc != 1 else '')
    
def _make_results_dir():
    if not os.path.exists(testenv.RESULTS_DIR):
        os.mkdir(testenv.RESULTS_DIR)

if __name__ ==  '__main__':
    args = sys.argv[1:]
    acceptance_tests(args)
