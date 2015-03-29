"""
Build simple social graphs for GitHub.

Examples:

# Draw graph for vim-jp organization members (without authorization):
$ github-social-graph --orgs vim-jp -o 1.png

# Draw graph for organization and users (with authorization by password):
$ github-social-graph -u Kagami -p --orgs vim-jp --users Shougo -o 1.png

# Only fetch data for future use and analysis:
$ github-social-graph --orgs vim-jp -o jp.json

# Use pre-fetched data to draw graph:
$ github-social-graph -i jp.json -o jp.png
"""

from __future__ import division
import six

import os
import sys
import errno
import tempfile
import os.path as path
import json
import argparse
from copy import deepcopy
from threading import Thread
from io import BytesIO
from six.moves import queue
from six.moves.urllib.request import urlopen

from pygithub3 import Github
from pygraphviz import AGraph
from PIL import Image, ImageDraw


SUPPORTED_INPUT_FORMATS = ['json', 'dot']
AVATAR_DOWNLOADING_PARALLEL_LEVEL = 10
AVATAR_SIZE = 60
DPI = 96
# blues4
BACKGROUND_COLOR = '#eff3ff'
ARROWS_BORDER_COLOR = '#bdd7e7'
CIRCLES_BORDER_COLOR = '#6baed6'
TEXT_COLOR = '#2171b5'


def log(text, *args, **kwargs):
    out = text.format(*args, **kwargs)
    out += '\n'
    sys.stderr.write(out)


def fetcher(options):
    def get_or_set(username):
        try:
            info = graph_data[username]
        except KeyError:
            graph_data[username] = info = {}
        return info

    github = Github(
        login=options.username, password=options.password,
        token=options.token)

    graph_data = {}
    usernames = set(options.users)

    log('Start fetching GitHub data. It may take some time, be patient.')
    for org_name in set(options.orgs):
        log('Fetching {}\'s members...', org_name)
        users = github.orgs.members.list_public(org_name).all()
        for user in users:
            usernames.add(user.login)
    for username in usernames:
        log('Fetching {}\'s followers and following...', username)
        followers = github.users.followers.list(username).all()
        following = github.users.followers.list_following(username).all()
        info = get_or_set(username)
        info['followers'] = [f.login for f in followers]
        info['following'] = [f.login for f in following]
    if not options.full_graph:
        graph_data = process_graph_data(graph_data)
    if options.avatars:
        for username, info in list(six.iteritems(graph_data)):
            log('Fetching {}\'s info...', username)
            info['avatar_url'] = github.users.get(username).avatar_url
            if options.full_graph:
                for f in set(info['followers'] + info['following']):
                    f_info = get_or_set(f)
                    if 'avatar_url' in f_info:
                        continue
                    log('Fetching {}\'s info...', f)
                    f_info['avatar_url'] = github.users.get(f).avatar_url
    log('Fetching is complete.')
    return graph_data


def process_graph_data(graph_data):
    """
    Fix graph data to make it easier to create big graphs.
    """
    graph_data = deepcopy(graph_data)
    for username, info in six.iteritems(graph_data):
        # Leave only users with followers info (do not draw huge amount
        # of isolated nodes).
        info['followers'] = [
            f
            for f in info.get('followers', [])
            if 'followers' in graph_data.get(f, {})
        ]
        info['following'] = [
            f
            for f in info.get('following', [])
            if 'followers' in graph_data.get(f, {})
        ]
    return graph_data


def process_options():
    class _NoPassword: pass
    class _NoToken: pass

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
        '-o', '--output', type=argparse.FileType('wb'), required=True,
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
    parser.add_argument(
        '-na', '--no-avatars', action='store_false', dest='avatars',
        help='do not show avatars in graphs')
    parser.add_argument(
        '-fg', '--full-graph', action='store_true',
        help='fetch and draw full graph '
             '(this may take a long time and lot of API requests)')

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
    if options.input_format == 'dot' and options.output_format == 'json':
        parser.error('could not convert dot to json')
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


def get_avatars_cache_dir():
    return path.join(tempfile.gettempdir(), 'github-social-graph')


def get_avatar_path(node):
    return path.join(get_avatars_cache_dir(), '{}.png'.format(node))


def create_graph(graph_data, input_format, avatars):
    def add_node(node):
        attrs = {
            'label': node,
            'shape': 'circle',
            'margin': 0,
            'color': CIRCLES_BORDER_COLOR,
            'fontcolor': TEXT_COLOR,
            'fontsize': 10,
        }
        if avatars:
            # TODO: Draw some placeholder image for users without avatars?
            if 'avatar_url' in graph_data.get(node, {}):
                attrs['image'] = get_avatar_path(node)
                attrs['label'] = ''
                attrs['xlabel'] = node
                attrs['width'] = AVATAR_SIZE / DPI
                attrs['height'] = AVATAR_SIZE / DPI
                attrs['fixedsize'] = 'true'
        graph.add_node(node, **attrs)

    graph_attrs = {
        'directed': True,
        'dpi': DPI,
        'background': BACKGROUND_COLOR,
    }
    if input_format == 'dot':
        graph = AGraph(graph_data, **graph_attrs)
    else:
        graph = AGraph(**graph_attrs)
        for username, info in six.iteritems(graph_data):
            add_node(username)
            for f in info.get('followers', []):
                add_node(f)
                graph.add_edge(f, username, color=ARROWS_BORDER_COLOR)
            for f in info.get('following', []):
                add_node(f)
                graph.add_edge(username, f, color=ARROWS_BORDER_COLOR)
    return graph


def download_avatars(graph_data):
    def is_cached(username):
        avatar_path = get_avatar_path(username)
        if path.exists(avatar_path):
            return True

    def mkdirp(dirname):
        # See <https://stackoverflow.com/a/600612> for details.
        try:
            os.makedirs(dirname)
        except OSError as exc:
            if exc.errno == errno.EEXIST and path.isdir(dirname):
                pass
            else:
                raise

    def download(urlsq, res):
        # TODO(Kagami): Error handling, timeouts...
        while True:
            try:
                url, username = urlsq.get_nowait()
            except queue.Empty:
                return
            try:
                data = urlopen(url).read()
                res.append((data, username))
            finally:
                urlsq.task_done()

    mkdirp(get_avatars_cache_dir())
    urls_usernames = [
        (info['avatar_url'], username)
        for username, info in six.iteritems(graph_data)
        if 'avatar_url' in info and not is_cached(username)]
    if not urls_usernames:
        return
    log('Downloading {} avatars...', len(urls_usernames))

    urlsq = queue.Queue()
    for u in urls_usernames:
        urlsq.put(u)
    res = []
    threads_num = min(AVATAR_DOWNLOADING_PARALLEL_LEVEL, len(urls_usernames))
    for _ in six.moves.range(threads_num):
        Thread(target=download, args=(urlsq, res)).start()
    urlsq.join()
    for data, username in res:
        with open(get_avatar_path(username), 'wb') as fh:
            fh.write(process_avatar(data))


def process_avatar(data):
    """
    Shrink avatar image and do some post-processing.
    """
    image = Image.open(BytesIO(data))

    width, height = image.size
    mask = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, width, height], fill=(255,255,255,255))
    mask.paste(image, mask=mask)
    image = mask
    image.thumbnail((AVATAR_SIZE, AVATAR_SIZE), Image.ANTIALIAS)

    output = BytesIO()
    image.save(output, 'PNG')
    return output.getvalue()


def draw_graph(graph, output, format):
    graph.draw(output, format=format, prog='dot', args='-q')


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
        options.output.write(json.dumps(graph_data).encode('utf-8'))
    else:
        graph = create_graph(graph_data, options.input_format, options.avatars)
        if options.output_format == 'dot':
            graph.write(options.output)
        else:
            if options.avatars and \
                    (options.input_format == 'json' or not options.input):
                download_avatars(graph_data)
            draw_graph(graph, options.output, options.output_format)
    if options.output is not sys.stdout:
        options.output.close()


if __name__ == '__main__':
    main()
