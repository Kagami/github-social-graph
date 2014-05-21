from setuptools import setup, find_packages


setup(
    # Reference: http://pythonhosted.org/distribute/setuptools.html
    name='github-social-graph',
    version='0.0.1',
    author='Kagami Hiiragi',
    author_email='kagami@genshiken.org',
    url='https://github.com/Kagami/github-social-graph',
    description='Build simple social graphs for GitHub',
    install_requires=[
        'pygithub3>=0.5',
        'pygraphviz>=1.2',
    ],
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'github-social-graph = github_social_graph:main',
            'gsg = github_social_graph:main',
        ],
    })
