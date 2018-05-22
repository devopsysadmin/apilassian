# python imports

# devops apps imports
from .constants import (BBUCKET_API_PATH, BBUCKET_PERM_API_PATH,
    BBUCKET_MATCHERTYPE_BRANCH)

DEFAULT_PAGE_SIZE = 25
MAX_LOOP_PAGES = 1000


def search(arraydict, **keyvalue):
    key, value = list(keyvalue.items())[0]
    results = [item for item in arraydict if item[key] == value]
    if len(results) > 0:
        return results
    else:
        return None


def paginated(session, url, page_size=DEFAULT_PAGE_SIZE):
    array = list()
    start = 0
    end = False
    if '?' in url:
        page = '%s&start=%s'
    else:
        page = '%s?start=%s'
    while not end:
        response = session.get(page % (url, start))
        start += page_size
        end = response.value.get('isLastPage', True)
        if response.ok:
            array.extend(response.value.get('values'))
        else:
            end = True
    return array


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


class Project(object):
    session = None
    project = None
    context = '{api}/projects'

    @staticmethod
    def all(session):
        url = Project.context.format(api=BBUCKET_API_PATH)
        projects = paginated(session.get(url))
        return sorted(projects)

    def __init__(self, session, project):
        self.project = project
        self.session = session
        self.context = '{context}/{project}'.format(context=self.context,
                                                    project=self.project)\
                                            .format(api=BBUCKET_API_PATH)

    def json(self):
        response = self.session.get(self.context)
        return response.value

    def repos(self, slug=None):
        if slug:
            return Repo(session=self.session, project=self.project, slug=slug)
        else:
            return Repo.all(self.session, self.project)


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
            self.context = '{context}/tags'.format(context=context)

        def get(self):
            response = self.session.get(self.context)
            if response.ok:
                return [ tag['displayId'] for tag in response.value['values'] ]

        def set(self, commit, name, message=None):
            data = {
                    'name' : name,
                    'startPoint' : commit
                    }
            if message: data.update({'message' : message})
            response = self.session.post(self.context, json = data)
            return response.ok

    class Branch(object):
        def __init__(self, session, project, slug, context):
            self.session = session
            self.project = project
            self.slug = slug
            self.context = '{context}/branches'.format(context=context)

        def get(self):
            response = self.session.get(self.context)
            if response.ok:
                return response.value['values']

        def set(self, commit, name, message=None):
            data = {
                'name' : name,
                'startPoint': commit
            }
            if message: data.update({'message' : message})
            response  = self.session.post(self.context, json = data)
            return response.ok

    def __init__(self, session, project, slug):
        self.session = session
        self.slug = slug
        self.project = project
        self.context = '{context}/{slug}'.format(context=self.context,
                                                 slug=slug)\
                                         .format(api=BBUCKET_API_PATH,
                                                 project=project)
        self.tags = self.Tag(session=session, project=project, slug=slug, context=self.context)
        self.branches = self.Branch(session=session, project=project, slug=slug, context=self.context)

    @staticmethod
    def all(session, project):
        _repos = paginated(session,
                           Repo.context.format(
                               api=BBUCKET_API_PATH,
                               project=project))
        return sorted(_repos)

    def json(self):
        response = self.session.get(self.context)
        return response.value

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
        self.context = '{context}/{key}'.format(context=self.context,
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
        request = self.session.get(self.context)
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
            context=self.context,
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
