import os
__dir__ = os.path.dirname( __file__ )

DIR = {}

DIR['cerberus'] = os.path.join(__dir__,'../..')
DIR['config.yaml'] = os.path.join(DIR['cerberus'],'config.yaml')

__config__=None

def config():
    global __config__
    global DIR
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
