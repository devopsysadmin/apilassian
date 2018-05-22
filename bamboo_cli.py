#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from atlassianapi import session, bamboo

SESSION = None

def get_args():
    parser = ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--action', required=True)
    parser.add_argument('--params', required=True)
    parser.add_argument('--revision')
    parser.add_argument('--stage')
    return parser.parse_args()


def plan_enable(input_args):
    plan = bamboo.Plan(SESSION, input_args.params)
    return plan.enable()


def plan_disable(input_args):
    plan = bamboo.Plan(SESSION, input_args.params)
    return plan.disable()


def plan_build(input_args):
    plan = bamboo.Plan(SESSION, input_args.params)
    return plan.build(input_args.revision,
                      input_args.stage)


if __name__ == '__main__':
    args = get_args()
    SESSION = session.Session(url=args.url,
                              username=args.username,
                              password=args.password)

    # TODO: handle actions with client class
    action = locals().get(args.action, None)
    if action:
        result = action(args)
        if result.ok:
            print('[INFO] API response for action {action}::{params} with \
                    status {sc}'.format(
                                    action=args.action,
                                    params=args.params,
                                    sc=result.code)
        else:
            print('[ERROR] API response for action {action}::{params} returned \
                {status} : {message}'.format(
                action=args.action, status=result.code, message=result.value
                ))
    else:
        sys.exit('[ERROR] Action %s not implemented.' % args.action)
