#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

NAME    = 'TracTaskBoard'
PACKAGE = 'taskboard'
VERSION = '0.1'

setup(
    name         = NAME,
    version      = VERSION,
    author       = 'NAKAGAWA Masaki',
    author_email = 'masaki.nakagawa@gmail.com',
    license      = 'MIT',
    packages     = [ PACKAGE ],
    package_data = {
        PACKAGE : [
            'templates/*.html',
            'htdocs/js/*.js',
            'htdocs/css/*.css',
        ]
    },
    entry_points = {
        'trac.plugins' : [
            'taskboard = taskboard',
        ]
    },
)
