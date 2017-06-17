"""
Flask-Blogging
--------------

Flask-Blogging is a Flask extension for adding blogging support to
your web application. Flask-Blogging comes with the following
features out of the box:

- Bootstrap based site
- Markdown based blog editor
- Models to store blog
- Authentication of User's choice
- Sitemap, ATOM support
- Disqus support for comments
- Google analytics for usage tracking
- Permissions enabled to control which users can create/edit blogs
- Incorporates Flask-Cache for fast rendering
- Well documented, tested, and extensible design


Links
`````
* `documentation <http://flask-blogging.readthedocs.org/>`_
* `development version <https://github.com/gouthambs/Flask-Blogging>`_

"""

from setuptools import setup, find_packages
import os
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('flask_blogging/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))



BASE_PATH = os.path.dirname(__file__)


def get_requirements(suffix=''):
    with open(os.path.join(BASE_PATH, 'Requirements%s.txt' % suffix)) as f:
        rv = f.read().splitlines()
    return rv

setup(
    name='Flask-Blogging',
    version=version,
    url='https://github.com/gouthambs/Flask-Blogging',
    license='MIT',
    author='Gouthaman Balaraman',
    author_email='gouthaman.balaraman@gmail.com',
    description='A flask extension for adding Markdown blog support to your site',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_requirements(),
    tests_require=["nose", "mysqlclient", "psycopg2"],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
