from apilassian import bitbucket, session
import json

INDENT = 2

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
        print( json.dumps(response, indent=INDENT) )
    else:    
        print( json.dumps(response.json, indent=INDENT) )

def projects(args):
    project = args.get('project', None)
    if project:
        response = bb(args).projects(project).get()
    else:
        response = bb(args).projects()
    pprint(response)

def repos(args):
    project = args.get('project', None)
    repo = args.get('repo', None)
    if repo:
        response = bb(args).projects(project).repos(repo).get()
    else:
        response = bb(args).projects(project).repos()
    pprint(response)

def tags(args):
    print(args)