from atlassianapi import session as SESSION

URL = {
    'api' : '/rest/api/latest',
    }


def test(session):
    url = '%s/plan' %URL['api']
    return not session.get(url).get('error')

def projects(session):
    retval = list()
    url = URL['api']+'/project?page=%s'
    page = 0
    response = session.get(url %page)
    results_per_page = int(response.get('projects').get('max-result'))
    size = int(response.get('projects').get('size'))

    while page < size:
        response = session.get(url %page)
        if response.get('status') in SESSION.STATUS_OK:
            for project in response.get('projects', dict()).get('project'):
                prj = Project(session, project.get('key'))
                if not any(x.key == prj.key for x in retval):
                    retval.append(prj)
        else:
            break
        page += results_per_page
    return retval

def add_url_params(url, params):
    return SESSION.add_url_params(url, params)


class Plan(object):

    __session = None
    enabled = None
    link = None
    key = None
    name = None
    shortName = None
    json = None

    def __init__(self, session, key=None, raw=None):
        self.__session = session
        if not raw:
            url = URL['api'] + '/plan/%s' %key
            raw = self.__session.get(url).value
        self.json = raw

        if isinstance(raw, str):
            raise Exception('Error getting results')
        for key, value in raw.items():
            setattr(self, key, value)

    def __dict__(self):
        me = dict()
        for item in dir(self):
            key = item
            value = getattr(self, item)
            if (not key.startswith('_')) and(
                isinstance(value, str)
                or isinstance(value, list)
                or isinstance(value, tuple)
                or isinstance(value, dict)
                ):
                me.update({ key : value })
        return me

    def __str__(self):
        return str(self.__dict__())


    def enable(self):
        url = '{api}/plan/{key}/enable'.format(api=URL['api'], key=self.key)
        return self.__session.post(url)

    def disable(self):
        # Careful: even if url says "enable", the magic is done by delete call
        url = '{api}/plan/{key}/enable'.format(api=URL['api'], key=self.key)
        return self.__session.delete(url)

    def build(self, revision=None, variables=None, stage=None):
        url = '{api}/queue/{key}'.format(api=URL['api'], key=self.key)
        if revision:
            url = add_url_params(url, 'customRevision=%s'%revision)
        if stage:
            url = add_url_params(url, 'stage=%s' %stage)
        return self.__session.post(url)

    def stop(self, build_keys):
        url = '{api}/queue/{key}-{build_keys}'.format(
                api=URL['api'],
                key=self.key,
                build_keys=build_keys
            )
        return self.__session.delete(url)

    @staticmethod
    def all(session):
        all_plans = list()
        url = URL['api'] + '/plan?start-index=%s'
        page = 0
        response = session.get(url %page)
        if response.get('error', True) is False:
            results_per_page = int(response.get('plans').get('max-result'))
            size = int(response.get('plans').get('size'))

            while page < size:
                response = session.get(url %page)
                if response.get('status') in SESSION.STATUS_OK:
                    retval = response.get('plans', dict()).get('plan')
                    for plan in retval:
                        all_plans.append(Plan(session, raw=plan))
                    page += results_per_page
                else:
                    break
        return all_plans        

    run = build


class PlanBranch(object):
    __session = None
    enabled = None
    shortName = None
    name = None
    shortKey = None
    key = None

    def __init__(self, session, raw):
        self.__session = session
        for key, value in raw.items():
            setattr(self, key, value)

    def results(self):
        url = URL['api'] + '/result/' + self.key
        response = self.__session.get(url)
        return response.get('results', dict()).get('result', dict())


class Project(object):

    session = None
    key = None
    name = None

    def __init__(self, session, key):
        self.key = key
        self.session = session
        self.name = self.session.get('%s/project/%s' %(URL['api'], self.key)).get('name')


    def __planlist_belongs_to_project(self, plan_list):
        is_in_project = list()
        for plan in plan_list:
            if self.key in plan.get('key'):
                is_in_project.append(plan)
        return is_in_project


    def plans(self):
        project_plans = list()
        for plan in Plan.all(self.session):
            if self.key in plan.key:
                project_plans.append()
        return project_plans

class ElasticConfiguration(object):

    session = None

    def __init__(self, session):
        self.session = session

    def change_image(self, old_ami_id, new_ami_id):
        url = URL['api'] + '/elasticConfiguration/image-id/%s?newImageId=%s' %(old_ami_id, new_ami_id)
        response = self.session.put(url)
        return response.get('value', 0)

class Agent(object):

    __session = None
    busy = False
    active = False
    name = False
    idx = 0

    def __init__(self, session, **kwargs):
        self.__session = session
        agent = None
        if kwargs is not None:
            key, value = kwargs.keys()[0], kwargs.values()[0]
            match = [ agent for agent in self.all(session) if agent[key] == value ]
            if len(match)>0:
                for name, value in match[0].items():
                    setattr(self, name, value)


    @staticmethod
    def all(session):
        url = URL['api'] + '/agent'
        response = session.get(url)
        if response.get('status') in SESSION.STATUS_OK:
            return response.get('value')
        else:
            return list()
