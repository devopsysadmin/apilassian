from apilassian.bitbucket.settings import *

class Security(object):
    
    def __init__(self, session):
        self.session = session


'''
class Group(object):

    session = None
    context = '{api}/groups'

    def __init__(self, session):
        self.session = session

    @staticmethod
    def all(session):
        url = Group.context.format(api=BBUCKET_API_PATH)
        groups = paginated(session, url)
        return sorted(groups)
'''
