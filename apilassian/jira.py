# devops apps imports
from .constants import JIRA_API_PATH


class Issue(object):

    session = None
    key = None
    attributes = None
    __expand = None
    __transitions = None

    def __init__(self, session, key, expand=False):
        self.session = session
        self.key = key
        self.__expand = expand
        self.__transitions = None

    def __str__(self):
        me = dict()
        for item in dir(self):
            key = item
            value = getattr(self, item)
            if (not key.startswith('_')) and (
                    isinstance(value, str) or
                    isinstance(value, list) or
                    isinstance(value, tuple) or
                    isinstance(value, dict)):
                me.update({key: value})

        return str(me)

    @property
    def type(self):
        if self.attributes is None:
            self.attributes = self.json()
        return self.attributes['fields']['issuetype']['name'] \
                if self.attributes else None

    @property
    def status(self):
        if self.attributes is None:
            self.attributes = self.json()
        return self.attributes['fields']['status']['name'] \
                if self.attributes else None

    def json(self):
        url = '{base}/issue/{key}'.format(base=JIRA_API_PATH, key=self.key)
        if self.__expand:
            url += '?expand=changelog'

        response = self.session.get(url)
        return response.value

    def get_transitions(self, force=False):
        ''' Force is used to force API calls. Usually it won't be necessary'''
        if self.__transitions and not force:
            return self.__transitions
        else:
            url = '{base}/issue/{key}/transitions'.format(base=JIRA_API_PATH,
                                                          key=self.key)
            response = self.session.get(url)
            if response.ok:
                values = response.value.get('transitions')
                self.__transitions = values
                return values
            else:
                return None

    def set_transition(self, transition_id):
        url = '{base}/issue/{key}/transitions'.format(base=JIRA_API_PATH,
                                                      key=self.key)

        data = {"transition": {"id": int(transition_id)}}
        response = self.session.post(url, json=data)
        if response.ok:
            self.get_transitions(True)
        return response

    def get_transition(self, **kwargs):
        """ Get issue trasition by id/name """
        if 'name' in kwargs:
            search_field = 'name'
        elif 'id' in kwargs:
            search_field = 'id'
        else:
            return {}

        # get issue transitions
        # auto transition has auto- prefix
        search_value = kwargs.get(search_field)
        issue_transitions = self.get_transitions()
        if issue_transitions is None:
            return {}
        issue_transition_iter = \
                (transition for transition in issue_transitions if
                    search_value in transition[search_field])

        # get first transition matching with search criteria
        try:
            return next(issue_transition_iter)
        except StopIteration:
            return {}

    def get_transition_id(self, name):
        return self.get_transition(name=name).get('id')

    def get_transition_name(self, transition_id):
        return self.get_transition(id=transition_id).get('name')

    def delete(self):
        url = '{base}/issue/{key}'.format(base=JIRA_API_PATH,
                                          key=self.key)
        return self.session.delete(url)
