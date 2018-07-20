from apilassian.bitbucket.settings import *
from apilassian.session import paginated

def search(arraydict, **keyvalue):
    key, value = list(keyvalue.items())[0]
    results = [item for item in arraydict if item[key] == value]
    if len(results) > 0:
        return results
    else:
        return None

def _paginated(session, url):
    return paginated(session, url,
                        end_key=DEFAULT_PAGE_END_KEY,
                        end_value=DEFAULT_PAGE_END_VALUE,
                        page_size=DEFAULT_PAGE_SIZE
                    )


class Project(object):
    route = '{api}/projects'

    @staticmethod
    def all(session):
        url = Project.route.format(api=API)
        projects = _paginated(session=session, url=url)
        return projects

    def __init__(self, session, project):
        self.project = project
        self.session = session
        self.route = '{context}/{project}'.format(context=self.route,
                                                    project=self.project)\
                                            .format(api=API)

    def me(self):
        response = self.session.get(self.route)
        if response.ok:
            self.json = response.value
        return self


    def repos(self, slug=None):
        if slug:
            return Repo(session=self.session, project=self.project, slug=slug)
        else:
            return Repo.all(self.session, self.project)


class Repo(object):
    route = '{api}/projects/{project}/repos'

    @staticmethod
    def all(session, project):
        url = Repo.route.format(api=API, project=project)
        repos = _paginated(session, url)
        return repos

    def __init__(self, session, project, slug):
        self.session = session
        self.slug = slug
        self.project = project
        self.route = '{context}/{slug}'.format(context=self.route,
                                                 slug=slug)\
                                         .format(api=API,
                                                 project=project)

    def me(self):
        response = self.session.get(self.route)
        if response.ok:
            self.json = response.value
        return self


    def tags(self):
        context = '{route}/tags'.format(route=self.route)
        response = self.session.get(context)
        if response.ok:
            return [ tag['displayId'] for tag in response.value['values'] ]


    def branches(self, name=None, simple=False):
        context = '{route}/branches'.format(route=self.route)
        response = session.get(context)
        if response.ok:
            if simple:
                return [ element['displayId'] for element in response.value['values'] ]
            else:
                return response.value['values']

    def commits(self, hash=None):
        pass


class Commit(object):
    route = '{api}/projects/{project}/repos/{repo}'



'''
class Repo(object):
    session = None
    project = None
    slug = None
    context = '{api}/projects/{project}/repos'

    class Tag(object):

        def __init__(self, session, project, slug, context):
            self.session = session
            self.project = project
            self.slug = slug
            self.route = '{context}/tags'.format(context=context)

        def get(self):
            self.route = '{context}/tags'.format(context=context)
            response = self.session.get(self.route)
            if response.ok:
                return [ tag['displayId'] for tag in response.value['values'] ]

        def set(self, commit, name, message=None):
            data = {
                    'name' : name,
                    'startPoint' : commit
                    }
            if message: data.update({'message' : message})
            response = self.session.post(self.route, json = data)
            return response.ok

    class Branch(object):
        def __init__(self, session, project, slug, context):
            self.session = session
            self.project = project
            self.slug = slug

        def get(self):
            self.route = '{context}/branches'.format(context=context)
            response = self.session.get(self.route)
            if response.ok:
                return response.value['values']



    def pullrequests(self, key=None):
        if key:
            return PullRequest(self.session, self.project, self.slug, self.key)
        else:
            return PullRequest.all(self.session, self.project, self.slug)


class PullRequest(object):
    session = None
    project = None
    slug = None
    context = '{api}/projects/{project}/repos/{slug}/pull-requests'
    __attributes = dict()

    @classmethod
    def from_json(cls, session, jsondict):
        repo = jsondict['fromRef']['repository']
        pullrequest = cls(
            session=session,
            project=repo['project']['key'],
            slug=repo['name'],
            key=jsondict['id'],
            json=jsondict)
        return pullrequest

    def __init__(self, session, project, slug, key, **kwargs):
        self.session = session
        self.project = project
        self.slug = slug
        self.key = key
        self.__attributes = kwargs.get('json', kwargs)
        self.route = '{context}/{key}'.format(context=self.route,
                                                key=self.key)\
                                        .format(api=BBUCKET_API_PATH,
                                                project=self.project,
                                                slug=self.slug)

    def attributes(self):
        return self.__attributes

    def get(self, key):
        QUICK_MAP = {
            'orig': self.__attributes.get('fromRef', dict()).get('id'),
            'dest': self.__attributes.get('toRef', dict()).get('id'),
            'id': self.key
        }

        return QUICK_MAP.get(key, self.__attributes.get(key, None))

    def json(self):
        request = self.session.get(self.route)
        return request.value

    @staticmethod
    def all(session, project, slug):
        url = PullRequest.context.format(api=BBUCKET_API_PATH,
                                         project=project,
                                         slug=slug)
        request = paginated(session, url)
        return request

    def merge(self):
        version = self.get('version')
        url = '{context}/merge?version={version}'.format(
            context=self.route,
            version=version)
        request = self.session.post(url)
        return request

    def accept(self):
        return self.merge()


class Branch:

    session = None
    project = None
    repository = None
    context = '{api}/projects/{project}/repos/{repo}/{scope}'

    def __init__(self, session, project, repository, name):
        self.session = session
        self.name = name
        self.repository = repository
        self.project = project

    @staticmethod
    def all(session, project, repository):
        """ Get all repository branches """
        url = Branch.context.format(
            api=BBUCKET_API_PATH,
            project=project,
            repo=repository,
            scope='branches')
        request = paginated(session, url)
        return request

    def json(self):
        """ Get json from repository branch """
        url = Branch.context.format(
            api=BBUCKET_API_PATH,
            project=self.project,
            repo=self.repository,
            scope='branches')
        response = self.session.get(url)
        if 'values' not in response.value:
            return {}

        try:
            branch_iterator = \
                (branch for branch in response.value['values'] if
                    'displayId' in branch['matcher'] and
                    branch['matcher']['displayId'] == self.name)
            branch_response = next(branch_iterator)
        except StopIteration:
            return {}

        return branch_response

    def set_restriction(self, restriction, users=[], groups=[]):
        """
        Set permission to certain branch affecting users, groups or all

        :param:restriction code to grant/revoke permission (see constants)
        :param:users single users who will be affected for restriction
        :param:groups groups which will be affected for restriction
        :return:dict branch restriction set in json format
        """
        url = Branch.context.format(
            api=BBUCKET_PERM_API_PATH,
            project=self.project,
            repo=self.repository,
            scope='restrictions')

        branch_full_name = 'refs/heads/%s' % self.name
        payload = {
            "type": restriction,
            "matcher": {
                "id": branch_full_name,
                "type": {
                    "id": BBUCKET_MATCHERTYPE_BRANCH
                }
            }
        }

        # apply to groups or users if needed
        if users:
            payload["users"] = users
        if groups:
            payload["groups"] = groups

        response = self.session.post(url, json=payload)
        return response.value

    def unset_restriction(self, restriction):
        """
        UnSet permission to certain branch depending on scope

        :param:restriction code to grant/revoke permission (see constants)
        :return: blank if succeded
        """
        # due to BBucket API restrictions we have to retrieve all restrictions
        # and select the one that applies to our branch
        url = Branch.context.format(
            api=BBUCKET_PERM_API_PATH,
            project=self.project,
            repo=self.repository,
            scope='restrictions')
        response = self.session.get(url)

        if 'values' not in response.value:
            print("[WARNING] Couldnt unset %s in branch %s."
                  "API Response invalid" % (restriction, self.name))
            return {"errors": "Invalid API response %s" % response.value}

        # filter branch restrictions from response
        try:
            branch_iterator = \
                (branch for branch in response.value['values'] if
                    'displayId' in branch['matcher'] and
                    branch['matcher']['displayId'] == self.name and
                    branch['type'] == restriction)
            branch_response = next(branch_iterator)
        except StopIteration:
            print("[WARNING] Couldnt unset %s in branch %s. Doesnt exist." %
                    (restriction, self.name))
            return {"warning": "Restriction %s for branch %s doesnt exist." %
                    (restriction, self.name)}

        restriction_id = branch_response['id']
        url = '{restriction_base_url}/{id}'.format(
            restriction_base_url=url,
            id=restriction_id)
        response = self.session.delete(url)
        return response.value

    def get_restrictions(self):
        """
        UnSet permission to certain branch depending on scope

        :return:dict branch restriction list in json format
        """
        url = Branch.context.format(
            api=BBUCKET_PERM_API_PATH,
            project=self.project,
            repo=self.repository,
            scope='restrictions')
        response = self.session.get(url)

        if 'values' not in response.value:
            print("[WARNING] Couldnt retrieve restrictions in branch %s."
                  "API Response invalid" % self.name)
            return {"errors": "Invalid API response %s" % response.value}

        return response.value['values']
'''