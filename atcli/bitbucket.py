from apilassian import session
from apilassian import bitbucket
import json

def call(action):
    return globals().get(action)

def bb(args):
    s = session.Session(
                            username=args.get('username'),
                            password=args.get('password'),
                            token=args.get('token'),
                            url=args.get('url')
                        )
    return bitbucket.Bitbucket(s)

def pprint(response):
    if isinstance(response, list):
        print( json.dumps(response) )
    else:    
        print( json.dumps(response.json) )

def projects(args):
    project = args.get('project', None)
    if project:
        response = bb(args).projects(project).me()
    else:
        response = bb(args).projects()
    pprint(response)

def repos(args):
    project = args.get('project', None)
    repo = args.get('repo', None)
    if repo:
        response = bb(args).projects(project).repos(repo).me()
    else:
        response = bb(args).projects(project).repos()
    pprint(response)

def tags(args):
    project = args.get('project', None)
    repo = args.get('repo', None)
    response = bb(args).projects(project).repos(repo).tags()
    pprint(response)

def branches(args):
    project = args.get('project', None)
    repo = args.get('repo', None)
    response = bb(args).projects(project).repos(repo).branches(simple=True)
    pprint(response)
