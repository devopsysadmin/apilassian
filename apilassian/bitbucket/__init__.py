from apilassian.bitbucket import repository as repo
from apilassian.bitbucket import administration as admin
from apilassian.bitbucket.settings import *

class Bitbucket(object):

    def __init__(self, session):
        self.session = session
        self.route = API

    def projects(self, name=None):
        if name:
            return repo.Project(self.session, name)
        else:
            return repo.Project.all(self.session)

    def security(self):
        return admin.Security(self.session)
