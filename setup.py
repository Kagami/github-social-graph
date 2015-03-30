from setuptools import setup


setup(
    # Reference: http://pythonhosted.org/distribute/setuptools.html
    name='github-social-graph',
    version='0.1.0',
    author='Kagami Hiiragi',
    author_email='kagami@genshiken.org',
    url='https://github.com/Kagami/github-social-graph',
    description='Build simple social graphs for GitHub',
    license='CC0',
    install_requires=[
        'pygithub33>=0.6.2',
        'pygraphviz>=1.3rc2',
        'Pillow>=2.4.0',
        'six',
    ],
    py_modules=['github_social_graph'],
    entry_points={
        'console_scripts': [
            'github-social-graph = github_social_graph:main',
            'gsg = github_social_graph:main',
        ],
    })
