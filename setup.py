from setuptools import setup


setup(
    # Reference: http://pythonhosted.org/distribute/setuptools.html
    name='github-social-graph',
    version='0.1.1',
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
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
    ],
)
