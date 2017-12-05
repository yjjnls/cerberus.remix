import logging
import subprocess
import shlex
import sys
import os
import tarfile
import zipfile
import tempfile
import time
import glob
import shutil
import hashlib
import platform

LOGFILE = None  # open('/tmp/cerbero.log', 'w+')
DRY_RUN = False

class FatalError(Exception):
    header = ''
    msg = ''

    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.header + msg)

def to_unixpath(path):
    if path[1] == ':':
        path = '/%s%s' % (path[0], path[2:])
    return path

class StdOut:

    def __init__(self, stream=sys.stdout):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def _fix_mingw_cmd(path):
    reserved = ['/', ' ', '\\', ')', '(', '"']
    l_path = list(path)
    for i in range(len(path)):
        if path[i] == '\\':
            if i + 1 == len(path) or path[i + 1] not in reserved:
                l_path[i] = '/'
    return ''.join(l_path)


def call(cmd, cmd_dir='.', fail=True, verbose=False):
    '''
    Run a shell command

    @param cmd: the command to run
    @type cmd: str
    @param cmd_dir: directory where the command will be run
    @param cmd_dir: str
    @param fail: whether or not to raise an exception if the command fails
    @type fail: bool
    '''
    try:
        if LOGFILE is None:
            if verbose:
                print("Running command '%s'" % cmd)
        else:
            LOGFILE.write("Running command '%s'\n" % cmd)
            LOGFILE.flush()
        shell = True
        
        if platform.system() == "Windows":
            # windows do not understand ./
            if cmd.startswith('./'):
                cmd = cmd[2:]
            # run all processes through sh.exe to get scripts working
            cmd = '%s "%s"' % ('sh -c', cmd)
            # fix paths with backslashes
            cmd = _fix_mingw_cmd(cmd)
            # Disable shell which uses cmd.exe
            shell = False
        stream = LOGFILE or sys.stdout
        if DRY_RUN:
            # write to sdterr so it's filtered more easilly
            print("cd %s && %s && cd %s" % (cmd_dir, cmd, os.getcwd()))
            ret = 0
        else:
            ret = subprocess.check_call(cmd, cwd=cmd_dir,
                                       stderr=subprocess.STDOUT,
                                       stdout=StdOut(stream),
                                       env=os.environ.copy(), shell=shell)
    except subprocess.CalledProcessError:
        if fail:
            raise FatalError("Error running command: %s"% cmd)
        else:
            ret = 0
    return ret


def unpack(filepath, output_dir):
    '''
    Extracts a tarball

    @param filepath: path of the tarball
    @type filepath: str
    @param output_dir: output directory
    @type output_dir: str
    '''
    logging.info("Unpacking %s in %s" % (filepath, output_dir))
    if filepath.endswith('tar.gz') or filepath.endswith('tgz'):
        tf = tarfile.open(filepath, mode='r:gz')
        tf.extractall(path=output_dir)
    elif filepath.endswith('tar.bz2') or filepath.endswith('tbz2'):
        tf = tarfile.open(filepath, mode='r:bz2')
        tf.extractall(path=output_dir)
    elif filepath.endswith('tar.xz'):
        call("%s -Jxf %s" % (TAR, to_unixpath(filepath)), output_dir)
    elif filepath.endswith('.zip'):
        zf = zipfile.ZipFile(filepath, "r")
        zf.extractall(path=output_dir)
    else:
        raise FatalError("Unknown tarball format %s" % filepath)


def download(url, destination=None, recursive=False, check_cert=True, overwrite=False):
    '''
    Downloads a file with wget

    @param url: url to download
    @type: str
    @param destination: destination where the file will be saved
    @type destination: str
    '''
    cmd = "wget %s " % url
    path = None
    if recursive:
        cmd += "-r "
        path = destination
    else:
        if destination is not None:
            cmd += "-O %s " % destination

    if not check_cert:
        cmd += " --no-check-certificate"

    if not recursive and not overwrite and os.path.exists(destination):
        if LOGFILE is None:
            logging.info("File %s already downloaded." % destination)
    else:
        if not recursive and not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        elif recursive and not os.path.exists(destination):
            os.makedirs(destination)

        if LOGFILE:
            LOGFILE.write("Downloading %s\n" % url)
        else:
            logging.info("Downloading %s", url)
        try:
            call(cmd, path)
        except FatalError, e:
            if os.path.exists(destination):
                os.remove(destination)
            raise e
