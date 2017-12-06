#!env python
# -*- coding: utf-8 -*-

"""
Python test 04:
Run user-selected command on many servers (user provided as param) with
ssh in parallel, collect output from all nodes. Script should print
collected output from all nodes on stdout, w/o using temp files
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

__author__ = "Oleksii S. Malakhov <brezerk@brezblock.org.ua>"
__license__ = "CC0"

# setup logger
logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)

class Singleton(type):
    """
    Singleton class
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class RCHandler(object):
    """
    ReturnCode handler
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.rc__ = 0

    def addRC(self, rc):
        self.rc__ += rc

    def getRC(self):
        return self.rc__

rc_handler = RCHandler()

# ok. let's define some custom exceptions
class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)

thread_fault = False

def worker():
    """
    Simple worker function.

    """
    while True:
        item = q.get()
        if item is None:
            break
        run_process(item['addr'], item['command'])
        q.task_done()

def die(message):
    """
    Print error and dies
    """
    logger.error(message)
    sys.exit(errno.EAGAIN)

def validate_command(command):
    """
    Validate command.
    Proably we should use something like shlex or so too

    command: command to validate
    """
    if not command:
        raise ValidationError("Error: empty command")

def validate_addr(addr):
    """
    Validate address
    FIXME: Yeah, I would add some more regexp, etc :D

    addr: address to validate
    """
    if not addr:
        raise ValidationError("Error: empty address")

def run_process(addr, command):
    """
    Run command and reutn the result.

    command: Command str. This one will be split using shlex.
    """
    try:
        args = shlex.split("ssh %s %s" % (addr, command))
        with subprocess.Popen(args,
                              stdout=subprocess.PIPE) as proc:
            proc.wait()
            stdout = proc.stdout.read().decode("utf-8")
            rc_handler.addRC(proc.returncode)
            if proc.returncode != 0:
                logger.error('Command %s on host %s failed' % (command, addr))
            else:
                for line in stdout.splitlines():
                    print("%s: %s" % (addr, line))

    except Exception as exp:
        logger.error('Command %s on host %s failed: %s' % str(exp))

if __name__ == "__main__":
    logger.warning("Hello, my konfu is the best! :P")

    parser = argparse.ArgumentParser(description="""Run user-selected command
on many servers via ssh in parallel, collect output from all nodes.""")
    parser.add_argument('--addr', nargs='+',
                       help='Server address',
                       required=True)
    parser.add_argument('--command', help='User-seelcted command',
                       required=True)

    ns = parser.parse_args()
    command = ns.command
    addrs = ns.addr
    # probable can be a param
    workers_count = 4

    try:
        validate_command(command)
        for addr in addrs:
            validate_addr(addr)

        q = queue.Queue()
        threads = []
        for i in range(workers_count):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        for addr in addrs:
            item = {'addr': addr, 'command': command}
            q.put(item)

        q.join()

        for i in range(workers_count):
            q.put(None)

        for t in threads:
            t.join()

    except ValidationError as exp:
        die(exp)

    sys.exit(rc_handler.getRC())

