"""
Flask-Blogging
-------------

"""
from setuptools import setup, find_packages


def get_requirements(suffix=''):
    with open('Requirements%s.txt' % suffix) as f:
        rv = f.read().splitlines()
    return rv

setup(
    name='Flask-Blogging',
    version='0.1.0',
    url='http://flask-blogging.readthedocs.org',
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
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)