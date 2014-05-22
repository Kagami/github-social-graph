from setuptools import setup


setup(
    # Reference: http://pythonhosted.org/distribute/setuptools.html
    name='github-social-graph',
    version='0.0.1',
    author='Kagami Hiiragi',
    author_email='kagami@genshiken.org',
    url='https://github.com/Kagami/github-social-graph',
    description='Build simple social graphs for GitHub',
    install_requires=[
        'pygithub3>=0.5.1',
        'pygraphviz>=1.2',
        'grequests>=0.2.0',
    ],
    dependency_links=[
        'https://github.com/Kagami/python-github3/archive/0.5.1.zip#egg=pygithub3-0.5.1',
    ],
    py_modules=['github_social_graph'],
    entry_points={
        'console_scripts': [
            'github-social-graph = github_social_graph:main',
            'gsg = github_social_graph:main',
        ],
    })
