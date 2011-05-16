#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

NAME    = 'TracTaskBoard'
PACKAGE = 'tractaskboard'
VERSION = '0.1'

setup(
    name         = NAME,
    version      = VERSION,
    author       = 'Masaki Nakagawa',
    author_email = 'masaki.nakagawa@gmail.com',
    license      = 'BSD',
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
            'tractaskboard = tractaskboard',
        ]
    },
)
