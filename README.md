# github-social-graph

This program helps to build simple social graphs for GitHub using it's
API and [graphviz](http://www.graphviz.org/).

## Installation

Installation via PIP:

```bash
pip install https://github.com/Kagami/github-social-graph/archive/master.zip
```

## Usage

Show help:
```bash
github-social-graph -h
```

(or `gsg -h`)

Usage examples:

```bash
# Draw graph for vim-jp organization members (without authorization):
$ github-social-graph --orgs vim-jp -o 1.png

# Draw graph for organization and users (with authorization by password):
$ github-social-graph -u Kagami -p --orgs vim-jp --users Shougo -o 1.png

# Only fetch data for future use and analysis:
$ github-social-graph --orgs vim-jp -o jp.json

# Use pre-fetched data to draw graph:
$ github-social-graph -i jp.json -o jp.png
```

## Examples

This image demonstrates some curious social relations between
japan/vim/haskell users (click for fullsize image):

[![](http://dump.bitcheese.net/files/eburote/jp-shrink-min.png)](http://dump.bitcheese.net/files/ebugipo/jp-min.png)
