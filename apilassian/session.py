import requests
import requests.packages.urllib3
import os, sys
import yaml
import json
import urllib

HEADERS = {
    'xml' : {'Accept' : 'application/xml', 'Content-Type':'application/xml'},
    'json' : {'Accept' : 'application/json', 'Content-Type':'application/json'}
    }

DEFAULT_RETRIES = 1
DEFAULT_PAGE_SIZE = 25
STATUS_OK = range(200, 299)
CREDENTIALS_FILE = os.path.join(os.getenv('HOME'), '.config', 'atlassian', 'settings.yml')

def add_url_params(url, params):
    _url = url + '?' if '?' not in url else url
    if isinstance(params, list) or isinstance(params, tuple):
        where = '&'.join(params)
    else:
        where = '&' + params
    return _url + where


def get_from_settings(key, args):
    app = args.get('application', 'generic')
    value = args.get(key)
    osenv = 'ATL_' + key.upper()
    if not value:
        if os.getenv(osenv, None) is not None:
            value = os.getenv(osenv)
        elif os.path.isfile(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r') as fn:
                yml = yaml.load(fn)
                value = yml.get(app, dict()).get(key)
    return value

def paginated(session, url, page_size=DEFAULT_PAGE_SIZE):
    array = list()
    start = 0
    end = False
    if '?' in url:
        page = '%s&start=%s'
    else:
        page = '%s?start=%s'
    while not end:
        response = session.get(page %(url, start))
        start += page_size
        end = response.get('isLastPage')
        if response.get('status') in STATUS_OK:
            array.extend(response.get('values'))
        else:
            end = True
    return array

class Response(object):
    ok = None
    code = None
    value = None

    def __init__(self, **kwargs):
        self.code = kwargs.get('status')

        for key, value in kwargs.items():
            setattr(self, key, value)

        if 'value' in kwargs:
            value = kwargs['value']
            if value.startswith('{'):
                self.value = json.loads(value)
            else:
                self.value = value


    def __str__(self):
        return str({
            'ok' : self.ok,
            'code' : self.code,
            'value' : self.value
        })

class Session(object):

    session = None
    username = None
    password = None
    url = None
    content_type = None

    def __init__(self, **args):
        self.session = requests.Session()
        self.url = self.__set_url(args.get('url'))
        self.content_type = args.get('content_type', 'json')
        token = args.get('token', None)

        ## Username and Password are ALWAYS asked with any API, so let's get them
        ## with arguments, file or environment
        self.username = get_from_settings('username', args)
        self.password = get_from_settings('password', args)

        if args.get('disable_warnings', False) is True:
            requests.packages.urllib3.disable_warnings()

        requests.adapters.DEFAULT_RETRIES = args.get('retries', DEFAULT_RETRIES)

        if token is not None:
            self.session.headers.update(token)
        elif self.username is not None and self.password is not None:
            self.session.auth = (self.username, self.password)

        if self.content_type is not None:
            self.session.headers.update(HEADERS[self.content_type])

        if not self.url:
            raise Exception('No url was set')

    def __response(self, request):
        return Response(
            status=request.status_code,
            ok=request.status_code in STATUS_OK,
            value=request.text
        )

    def __set_url(self, url):
        token = urllib.parse.urlparse(url)
        min_attributes = ('scheme', 'netloc')
        if not all([getattr(token, attr) for attr in min_attributes]):
            raise Exception('Bad URL Sintax at "{url}"'.format(url=url))
        else:
            return url

    def set_content_type(content):
        self.session.headers.update(HEADERS[content])

    def get(self, slug, **kwargs):
        request = self.url + slug
        headers = kwargs.get('headers', self.session.headers)
        response = self.session.get(request, headers=headers)
        return self.__response(self.session.get(request, headers=headers))


    def post(self, slug, **kwargs):
        request = self.url + slug
        headers = kwargs.get('headers', self.session.headers)
        if 'data' in kwargs:
            return self.__response(self.session.post(request, data=kwargs['data']))
        elif 'json' in kwargs:
            return self.__response(self.session.post(request, json=kwargs['json']))
        else:
            return self.__response(self.session.post(request))

    def put(self, slug, **kwargs):
        request = self.url + slug
        data = kwargs.get('data', None)
        headers = kwargs.get('headers', self.session.headers)
        return self.__response(self.session.put(request, data=data, headers=headers))

    def delete(self, slug):
        request = self.url + slug
        return self.__response(self.session.delete(request))
