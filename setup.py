from setuptools import setup, find_packages
import os
"""
Flask-Blogging
--------------

Flask-Blogging is a Flask extension for adding blogging support to
your web application. Flask-Login comes with the following
features out of the box:

- Bootstrap based site
- Markdown based blog editor
- Models to store blog
- Authentication of User's choice
- Sitemap, ATOM support
- Disqus support for comments
- Google analytics for usage tracking
- Well documented, tested, and extensible design


Links
`````
* `documentation <http://flask-blogging.readthedocs.org/>`_
* `development version <https://github.com/gouthambs/Flask-Blogging>`_

"""

BASE_PATH = os.path.dirname(__file__)
print BASE_PATH


def get_requirements(suffix=''):
    with open(os.path.join(BASE_PATH, 'Requirements%s.txt' % suffix)) as f:
        rv = f.read().splitlines()
    return rv

setup(
    name='Flask-Blogging',
    version="0.1.1",
    url='https://github.com/gouthambs/Flask-Blogging',
    license='MIT',
    author='Gouthaman Balaraman',
    author_email='gouthaman.balaraman@gmail.com',
    description='A flask extension for adding blog support to your site',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)