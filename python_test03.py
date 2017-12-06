#!env python
# -*- coding: utf-8 -*-

"""
Python test 03:
Detect local mounted disk (make sure it is local) with at least X MB free space,
create Z files of size Y, run Z "dd" processes which where each process will 
fill selected file with Data and print time took to complete the work.
"""

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import sys
import errno

# we need >= 3.4 b/c of queue, threading module naming changes
# yeah, if it is needed we can support 2.x and 3.x branches, but hey 
# this is kinda out of the scope, right? :D
try:
    assert sys.version_info >= (3,4)
except AssertionError:
    print("ERROR: Python >= 3.4 is REQUIRED")
    sys.exit(errno.ENOPKG)

import shlex
import queue
import threading
import subprocess
import argparse
import logging
from datetime import datetime

__author__ = "Oleksii S. Malakhov <brezerk@brezblock.org.ua>"
__license__ = "CC0"

# setup logger
logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)


# ok. let's define some custom exceptions
class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)

class Foo(object):
    """
    Just placeholder
    """
    pass

def worker(command, q):
    """
    Simple worker function.

    command: command to run. Str.
    q: queue reference
    """
    q.put(run_process(command))
    q.task_done()

def die(message):
    """
    Print error and dies
    """
    logger.error(message)
    sys.exit(errno.EAGAIN)

def run_process(command):
    """
    Run command and reutn the result.

    command: Command str. This one will be split using shlex.
    """
    ret = {
            'command': command,
            'stdout': None,
            'stderr': None,
            'returncode': None}

    try:
        args = shlex.split(command)
        with subprocess.Popen(args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as proc:
            proc.wait()
            ret['stdout'] = proc.stdout.read().decode("utf-8")
            # stderr=subprocess.STDOUT so stdout and stderr will be combined
            #ret['stderr'] = proc.stderr.read().decode("utf-8")
            ret['returncode'] = proc.returncode
    except Exception as exp:
        ret['stderr'] = str(exp)
        ret['returncode'] = 255
    return ret

if __name__ == "__main__":
    logger.warning("Hello, my konfu is the best! :P")

    # Yeah, argparse here. have no time sorry :(

    parser = argparse.ArgumentParser(description="""Run user-selected command
on many servers via ssh in parallel, collect output from all nodes.""")
    parser.add_argument('--count', help='How many files',
                       required=True, type=int)
    parser.add_argument('--size', help='Files size',
                       required=True, type=int)
    parser.add_argument('--free', help='Free sapce on disk',
                       required=True, type=int)

    ns = parser.parse_args()
    Z_files_num = ns.count
    Y_size = ns.size
    X_free = ns.free

    try:
        local_disks = run_process('df -l --output=size,target')

        for line in local_disks['stdout'].splitlines():
            try:
                size, mount_point = line.split(' /')
                # this should be moved into separate function :)
                if int(size) >= X_free:
                    logger.warning("Oprating on mount point: %s" % mount_point)
                    startTime = datetime.now()
                    q = queue.Queue()
                    threads = []
                    for fine_no in range(Z_files_num):
                        command = "dd if=/dev/zero of=/%s/file.%s bs=%s count=1" % (mount_point, fine_no, Y_size)
                        logger.warning(command)
                        t = threading.Thread(target=worker, args=(command, q))
                        t.start()
                        threads.append(t)
                    q.join()

                    for t in threads:
                        t.join()
                    logger.warning("Toook: %s" % (datetime.now() - startTime))
            except ValueError:
                pass


    except ValidationError as exp:
        die(exp)

    sys.exit(0)

