#!/usr/bin/env python3
# -*- encoding: utf8 -*-

## Crowd library to work with Crowd API
from apilassian.session import HEADERS, STATUS_OK
import requests
import json
import xml.etree.ElementTree as ET

BASE_URL     = '/rest/usermanagement/latest'
hyphen_keys = ('last-name', 'display-name', 'first-name')
ATTRIBUTES = {
    'lastActive'
    }


def hyphen_upper(key):
    newkey = key.replace('_', '-')
    return newkey if newkey in hyphen_keys else key

def hyphen_lower(key):
    return key.replace('-', '_') if key in hyphen_keys else key

class Group(object):
    session = None
    active = False
    name = None
    response = None

    def __init__(self, session, name):
        self.session = session
        self.name = name

        ## Get group properties
        group_url = '%s/group?groupname=%s' %(BASE_URL, name)
        group_response = self.session.get(group_url)
        if group_response.ok:
            self.active = group_response.value.get('active')

    def users(self):
        members_url = '%s/group/user/direct?groupname=%s' %(BASE_URL, self.name)
        members_response = self.session.get(members_url)
        if members_response.ok:
            return sorted([ x.get('name') for x in members_response.value.get('users')])
        else:
            self.response = members_response
            return list()

    ## TODO: To be tested
    @staticmethod
    def all(session):
        url = '%s/search?entity-type=group' %BASE_URL
        response = session.get(url)
        if response.ok:
            return response.value
        else:
            return list()


class User(object):

    cached = None

    def __init__ (self, session, name, cached=False, expand_attributes=False):
        self.session = session
        self.name = name
        self.context = '{base}/user'.format(base=BASE_URL)
        self.expand_attributes=expand_attributes
        if cached is True:
            self.cached = self.values(expand_attributes=expand_attributes)

    def __str__(self):
        if self.cached:
            return str(self.cached)
        else:
            return str(self.values())


    def attributes(self):
        url = '{context}/attribute?username={username}'.format(
                context=self.context,
                username=self.name
            )
        response = self.session.get(url)
        if response.ok:
            return response.value.get('attributes')


    def refresh_cache(self):
        self.cached = self.values(self.expand_attributes)            


    def values(self, expand_attributes=False):
        url = '%s?username=%s' %(self.context, self.name)
        response = self.session.get(url)
        userdef = dict()
        if response.ok:
            for key in response.value.keys():
                userdef[hyphen_lower(key)] = response.value[key]
            if expand_attributes:
                userdef['attributes'] = self.attributes()
        return userdef


    def get(self, key):
        if key in ATTRIBUTES:
            return self.get_attribute(key)
        else:
            values = self.cached if self.cached else self.values()
            if key == 'all':
                return values
            else:
                return values.get(key, None)


    def get_attribute(self, key):
        attributes = self.cached.get('attributes') if self.cached else self.attributes()
        for attribute in attributes:
            if attribute['name'] == key:
                return attribute['values']


    def add_to_group(self, group):
        pass


    def remove_from_group(self, group):
        url = '{context}/group/direct?username={user}&groupname={group}'.format(
                context=self.context, user=self.name, group=group
                )
        response = self.session.delete(url)
        return response.ok


    def is_member(self, group):
        return group in self.groups()


    def groups(self):
        userdef = self.values()
        url = '{context}/group/direct?username={username}'.format(
                context=self.context,
                username=self.name
                )
        response = self.session.get(url)
        if response.ok:
            return sorted([ group.get('name') for group in response.value.get('groups') ])


    def member(self, group, action=None):
        # action: 1=add, 0=delete, None=ask
        if action is True:
            return self.add_to_group(group)
        elif action is False:
            return self.remove_from_group(group)
        else:
            return self.is_member(group)

