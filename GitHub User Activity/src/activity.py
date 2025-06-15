import requests
import argparse
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

def _get_page(username: str, n_pages: int=1) -> list[Any]:
    pages = []
    for i in range(0, n_pages):
        url = API_ENDPOINT.format(username=username, page=i)
        page = requests.get(url, timeout=10)
        if page.status_code != 200:
            raise requests.ConnectionError(f'Exited with status {page.status_code}')
        else:
            pages.extend(page.json())
    return pages

def _get_activity(username: str, n_pages: int=1) -> dict[str, dict[str, str]]:
    activity = {}
    content = _get_page(username, n_pages)
    for event in content:
        event_type = event['type']
        repo_name = event['repo']['name']
        if event_type not in EVENT_DICT:
            raise KeyError(f'Even is not recognized: {event_type}')

        activity.setdefault(repo_name, {})
        activity[repo_name][event_type] = activity[repo_name].get(event_type, 0) + 1

    return activity

def print_activity(username: str, p: int, **kwargs) -> None:
    if not p and not isinstance(p, int):
        raise ValueError(f'Number of pages should be a positive int got: {type(p)}')
    if not username or not isinstance(username, str):
        raise ValueError(f'Username should be str got: {type(username)}')

    activity_dct = _get_activity(username, p)
    active_event_types = []
    for event, name in EVENT_DICT.items():
        arg_name = name.replace(' ', '_')
        if kwargs.get(arg_name, False):
            active_event_types.append(event)

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
        headers=['Activity', 'Commit count', 'Project name']
    ))

def main():
    args, queries = get_supported_queries()
    queries(**args)

if __name__ == '__main__':
    main()

#python "GitHub User Activity\src\activity.py" hub-activity kamranahmedse