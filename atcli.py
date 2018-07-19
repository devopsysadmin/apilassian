#!/usr/bin/env python3
import json, os, sys
import atcli
from argparse import ArgumentParser
from apilassian import session

def get_args():
    parser = ArgumentParser()
    parser.add_argument('element', choices=['bamboo', 'bitbucket', 'crowd', 'jira'])
    parser.add_argument('-p', '--profile', default='default')
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    return parser.parse_args()


def load_profile(profile):
    settings = {}
    filename = os.path.join(os.getenv('HOME'), '.config', 'atcli.json')
    if(os.path.isfile(filename)):
        with open(filename, 'r') as fn:
            contents = json.load(fn)
        settings.update(contents.get('profiles', dict()).get(profile, dict()))
    return settings


def parse_input(inputparams):
    inputs = {}
    for element in inputparams.split(','):
        keyvalue = element.split('=')
        inputs[keyvalue[0]] = ''.join(keyvalue[1:])
    return inputs


def main():
    args = get_args()
    settings = load_profile(args.profile)
    instance_map = {
        'bitbucket' : atcli.bitbucket,
        #'bamboo' : atcli.bamboo,
        #'jira' : atcli.jira,
        #'crowd' : atcli.crowd
    }
    
    inputs = parse_input(args.input) if args.input else dict()
    inputs.update(settings)
    action = instance_map[args.element]
    action.call(args.output)(inputs)


if __name__ == '__main__':
    main()