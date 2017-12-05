import os
import tempfile
import shell
import stat
import shutil
from shutil import rmtree as shutil_rmtree

__dir__ = os.path.dirname( __file__ )

DIR = {}

DIR['cerberus'] = os.path.join(__dir__,'../..')
DIR['config.yaml'] = os.path.join(DIR['cerberus'],'config.yaml')

__config__=None


def rmtree(path, ignore_errors=False, onerror=None):
    '''
    shutil.rmtree often fails with access denied. On Windows this happens when
    a file is readonly. On Linux this can happen when a directory doesn't have
    the appropriate permissions (Ex: chmod 200) and many other cases.
    '''
    def force_removal(func, path, excinfo):
        '''
        This is the only way to ensure that readonly files are deleted by
        rmtree on Windows. See: http://bugs.python.org/issue19643
        '''
        # Due to the way 'onerror' is implemented in shutil.rmtree, errors
        # encountered while listing directories cannot be recovered from. So if
        # a directory cannot be listed, shutil.rmtree assumes that it is empty
        # and it tries to call os.remove() on it which fails. This is just one
        # way in which this can fail, so for robustness we just call 'rm' if we
        # get an OSError while trying to remove a specific path.
        # See: http://bugs.python.org/issue8523
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except OSError:
            shell_call('rm -rf ' + path)
    # We try to not use `rm` because on Windows because it's about 20-30x slower
    if not onerror:
        shutil_rmtree(path, ignore_errors, onerror=force_removal)
    else:
        shutil_rmtree(path, ignore_errors, onerror)

def pysetup( name, url ):
    print "install %s from %s "%(name,url)

    tmp_dir = tempfile.mkdtemp()

    try:
        shell.call("git clone %s %s"%(url,name), cmd_dir = tmp_dir)
        shell.call("python setup.py install", cmd_dir = os.path.join(tmp_dir,name))
    except Exception , e:
        print 'Failed install %s from %s'%(name,url)
        if os.path.exists( tmp_dir ):
            rmtree(tmp_dir)
        raise Exception

    rmtree(tmp_dir)


def config():
    global __config__
    global DIR

    try:
        import yaml
    except ImportError, e:
        pysetup("pyyaml","https://github.com/yaml/pyyaml.git -b 3.12")
        


    if __config__ is None:
        __config__ = yaml.load(open( DIR['config.yaml']))
    return __config__



def HTTPMirror(url):
    conf = config()
    MIRROR=conf.get('mirror',{})
    HTTP=conf.get('http',{})

    server=HTTP.get('server',{})
    for base, websites in server.viewitems():

        part=url.split('://')
        scheme=part[0]
        path=part[1]

        for website in websites:
            s=None
            p=website
            
            part=website.split('://')
            if len(part) ==2:
                s=part[0]
                p=part[1]

            if path.startswith(p):
                if s is None:
                    return '%s/%s'%(base,path)
    return url

def MinGWLocation(mirror=False):
    conf = config()
    url = conf.get('MinGW','')
    if url and mirror:
        return HTTPMirror(url)
    return url

def LoadCerberos():
    conf = config()
    bb = conf['BB']
    rootd=DIR['cerberus']
    
    for git in bb['git']:
        for name, items in git.viewitems():
            
            relpath=items['path']
            path = os.path.abspath( os.path.join( rootd, relpath ) )
            gitd = os.path.dirname(path)
            repo_name=os.path.basename(path)
            url  = items['url']
            commit = items.get('commit',None)
            branch = items.get('branch',None)

            if branch:
                shell.call('git clone %s -b %s %s'%(url, branch,path))
                
            if commit:
                if not os.path.exists(path):
                    shell.call('git clone %s %s'%(url,path))
                shell.call('git reset --hard %s'%commit)

if __name__ == "__main__":
    try:
        import gyp
    except:
        pysetup("gyp","https://github.com/Mingyiz/gyp.git")
    LoadCerberos()
