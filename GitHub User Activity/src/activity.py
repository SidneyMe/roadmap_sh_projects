import requests
import argparse
import asyncio
import aiohttp
import itertools as it
from datetime import datetime
from typing import TypedDict, Callable, Any
from tabulate import tabulate

EVENT_DICT = {
    "CommitCommentEvent": "commit comment",
    "CreateEvent": "create",
    "DeleteEvent": "delete",
    "ForkEvent": "fork",
    "GollumEvent": "gollum",
    "IssueCommentEvent": "issue comment",
    "IssuesEvent": "issues",
    "MemberEvent": "member",
    "PublicEvent": "public",
    "PullRequestEvent": "pull request",
    "PullRequestReviewEvent": "pull request review",
    "PullRequestReviewCommentEvent": "pull request review comment",
    "PushEvent": "push",
    "ReleaseEvent": "release",
    "SponsorshipEvent": "sponsorship",
    "WatchEvent": "watch"
}

API_ENDPOINT = 'https://api.github.com/users/{username}/events?per_page=100&page={page}'
API_RATE_LIMIT = 'https://api.github.com/rate_limit'

class SupportedQueryArgs(TypedDict, total=False):
    name_or_flags: list[str]
    help: str
    nargs: str
    type: type
    default: Any
    action: str

class SupportedQueryProperties(TypedDict):
    target: Callable
    help: str
    args: list[SupportedQueryArgs]

class RequestLimit(Exception):
    pass

def _queries() -> dict[str, SupportedQueryProperties]:
    return{
        'hub-activity':{
            'target': print_activity,
            'help': 'gets activity of a user by username',
            'args':[
                {
                    'name_or_flags': ['username'],
                    'help': 'Username of a user on github'
                },
                {
                    'name_or_flags': ['--p'],
                    'help': 'Username of a user on github',
                    'type': int,
                    'default': 1
                },
                *({
                    'name_or_flags': [f'--{name.replace(" ", "_")}'],
                    'help': f'filter by {flag} event',
                    'action': 'store_true'
                } for flag, name in EVENT_DICT.items())
            ]
        }
    }

def get_supported_queries() -> tuple[dict[str, Any], Callable]:
    parser = argparse.ArgumentParser(
        prog='hub-parser',
        description='Parses ghub activities'
    )

    sub_parser = parser.add_subparsers(title='command', dest='command', required=True)
    sup_queries = _queries()

    for name, prop in sup_queries.items():
        s_pars = sub_parser.add_parser(name, help=prop['help'])
        for arg in prop['args']:
            kwargs = {'help' : arg['help']}
            if 'nargs' in arg:
                kwargs['nargs'] = arg['nargs']
            if 'type' in arg:
                kwargs['type'] = arg['type']
            if 'default' in arg:
                kwargs['default'] = arg['default']
            if 'action' in arg:
                kwargs['action'] = arg['action']
            s_pars.add_argument(*arg['name_or_flags'], **kwargs)

    args = vars(parser.parse_args())
    queries = sup_queries[args.pop('command')]['target']

    return args, queries

def get_remaining_api_calls() -> tuple[int, int]:
    rate_limit = requests.get(API_RATE_LIMIT, timeout=10)
    if rate_limit.status_code == 200:
        rate_limit = rate_limit.json()
        calls_remaining = rate_limit['rate']['remaining']
        reset_time = rate_limit['rate']['reset']
        return (int(calls_remaining), int(reset_time))
    else:
        raise requests.exceptions.ConnectionError(f'Exited with status {rate_limit.status_code}')

async def _get_page(session: aiohttp.client.ClientSession, username: str, page: int) -> Any:
    url = API_ENDPOINT.format(username=username, page=page)
    async with session.get(url) as page_resp:
        if page_resp.status == 403:
            raise requests.exceptions.ConnectionError('You have exceeded the API limit')
        if page_resp.status != 200:
            raise requests.exceptions.ConnectionError(f'Exited with status {page_resp.status}')
        else:
            return await page_resp.json()

async def _get_activity(username: str, n_pages: int) -> dict[str, dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        content = await asyncio.gather(*(_get_page(session, username, curr_page) for curr_page in range(1, n_pages+1)))

    activity: dict = {}
    for event in it.chain.from_iterable(content):
        event_type = event['type']
        repo_name = event['repo']['name']
        if event_type not in EVENT_DICT:
            raise KeyError(f'Event is not recognized: {event_type}')

        activity.setdefault(repo_name, {})
        activity[repo_name][event_type] = activity[repo_name].get(event_type, 0) + 1

    return activity

async def print_activity(username: str, p: int=1, **kwargs) -> None:
    if p <= 0 or not isinstance(p, int):
        raise ValueError(f'Number of pages should be a positive int got: {type(p)}')
    if not username or not isinstance(username, str):
        raise ValueError(f'Username should be str got: {type(username)}')

    active_event_types = []
    for event, name in EVENT_DICT.items():
        arg_name = name.replace(' ', '_')
        if kwargs.get(arg_name, False):
            active_event_types.append(event)

    activity_dct = await _get_activity(username, p)
    activity_display = []
    for project, _ in activity_dct.items():
        for activity, activity_count in activity_dct[project].items():
            if active_event_types and activity not in active_event_types:
                continue
            activity_display.append([
                EVENT_DICT[activity],
                activity_count,
                project
            ])

    print(tabulate(
        activity_display,
        headers=['Activity', 'Activity Count', 'Project name']
    ))

def main():

    api_limit, reset_time = get_remaining_api_calls()
    if api_limit and api_limit <= 1:
            raise RequestLimit(f"You have run out of api calls. Try after {datetime.fromtimestamp(reset_time)}")

    args, queries = get_supported_queries()
    asyncio.run(queries(**args))

    if api_limit and api_limit <= 10:
        print(f"Warning you have {api_limit} calls left")
    

if __name__ == '__main__':
    main()

#python "GitHub User Activity\src\activity.py" hub-activity kamranahmedse