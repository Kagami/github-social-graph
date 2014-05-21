"""
Build simple social graphs for GitHub.

Examples:

# Draw graph for vim-jp organization (without authorization):
$ github-social-graph --orgs vim-jp -o 1.png

# Draw graph for organization and users (with authorization by password):
$ github-social-graph -u Kagami -p --orgs vim-jp --users Shougo -o 1.png

# Only fetch data for future use and analysis:
$ github-social-graph --orgs vim-jp -o jp.json

# Use pre-fetched data to draw graph:
$ github-social-graph -i jp.json -o jp.png
"""

import sys
import json
import argparse
import os.path as path

from pygithub3 import Github
from pygraphviz import AGraph


def log(text, *args, **kwargs):
    out = text.format(*args, **kwargs)
    out += '\n'
    sys.stderr.write(out)


def fetcher(options):
    github = Github(
        login=options.username, password=options.password,
        token=options.token)

    graph_data = {}
    usernames = set()

    log('Start fetching GitHub data. It may take some time, be patient.')
    for org_name in options.orgs:
        log('Fetching {}\'s members...', org_name)
        users = github.orgs.members.list_public(org_name).all()
        for user in users:
            usernames.add(user.login)
    for username in options.users:
        log('Fetching {}\'s followers and following...', username)
        followers = github.users.followers.list(username).all()
        following = github.users.followers.list_following(username).all()
        graph_data[username] = {
            'followers': [f.login for f in followers],
            'following': [f.login for f in following],
        }
    log('Fetching is complete.')

    return graph_data


def process_options():
    class _NoPassword: pass
    class _NoToken: pass
    SUPPORTED_INPUT_FORMATS=['json', 'dot']

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-u', '--username',
        help='GitHub username for authenticated requests')
    parser.add_argument(
        '-p', '--password', nargs='?',
        default=_NoPassword,
        help='GitHub password for authenticated requests; '
             'omit value if you wish to enter it by hand')
    parser.add_argument(
        '-t', '--token', metavar='TOKEN', nargs='?',
        default=_NoToken,
        help='GitHub token for authenticated requests; '
             'omit value if you wish to enter it by hand')
    parser.add_argument(
        '-i', '--input', type=argparse.FileType('r'),
        help='pre-fetched data filename or "-" for stdin')
    parser.add_argument(
        '-if', '--input-format', choices=SUPPORTED_INPUT_FORMATS,
        help='format of the input data; '
             'if not specified will be guessed from the filename')
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), required=True,
        help='output filename or "-" for stdout')
    parser.add_argument(
        '-of', '--output-format',
        help='format of the output data (json, dot, png, etc.); '
             'if not specified will be guessed from the filename')
    parser.add_argument(
        '--orgs', metavar='ORGANIZATION', nargs='*', default=[],
        help='organizations to start fetching data with')
    parser.add_argument(
        '--users', metavar='USERNAME', nargs='*', default=[],
        help='users to start fetching data with')

    options = parser.parse_args()

    # Post-validate.
    if options.username and options.password is _NoPassword:
        parser.error('password should be specified')
    if options.password is not _NoPassword and options.username is None:
        parser.error('username should be specified')
    if options.password is not _NoPassword and options.token is not _NoToken:
        parser.error('password and token could not be used together')
    if options.input is sys.stdin and not options.input_format:
        parser.error('input format should be specified')
    if options.output is sys.stdout and not options.output_format:
        parser.error('output format should be specified')
    if options.input and not options.input_format:
        options.input_format = path.splitext(options.input.name)[1][1:]
    if options.input_format and \
            options.input_format not in SUPPORTED_INPUT_FORMATS:
        parser.error('specified input format do not supported')
    if options.output and not options.output_format:
        options.output_format = path.splitext(options.output.name)[1][1:]
    if not options.input and not options.orgs and not options.users:
        parser.error('no input data and no users/organizations is provided')

    # Fill additional values.
    if options.password is _NoPassword:
        # Clear hackish value for later options uses.
        options.password = None
    else:
        if options.password is None:
            options.password = raw_input('Enter password: ')
    if options.token is _NoToken:
        options.token = None
    else:
        if options.token is None:
            options.token = raw_input('Enter token: ')

    return options


def create_graph(graph_data, format):
    if format == 'dot':
        graph = AGraph(graph_data, directed=True)
    else:
        graph = AGraph(directed=True)
        for username, info in graph_data.iteritems():
            for f in info['followers']:
                graph.add_edge(f, username)
            for f in info['following']:
                graph.add_edge(username, f)
    return graph


def draw_graph(graph, output, format):
    graph.draw(output, format=format, prog='dot')


def main():
    options = process_options()

    if options.input:
        if options.input_format == 'json':
            graph_data = json.load(options.input)
        elif options.input_format == 'dot':
            graph_data = options.input.read()
        else:
            raise NotImplementedError
        if options.input is not sys.stdin:
            options.input.close()
    else:
        graph_data = fetcher(options)

    if options.output_format == 'json':
        json.dump(graph_data, options.output)
    else:
        graph = create_graph(graph_data, options.input_format)
        if options.output_format == 'dot':
            graph.write(options.output)
        else:
            draw_graph(graph, options.output, options.output_format)
    if options.output is not sys.stdout:
        options.output.close()


if __name__ == '__main__':
    main()
