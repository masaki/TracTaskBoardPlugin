# -*- coding: utf-8 -*-

import pkg_resources
from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiMacroProvider
from trac.web.chrome import add_script, add_stylesheet, ITemplateProvider

class Macro(Component):
    implements(ITemplateProvider, IWikiMacroProvider)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return [ ('tractaskboard', pkg_resources.resource_filename(__name__, 'htdocs')) ]

    def get_templates_dirs(self):
        return [ pkg_resources.resource_filename(__name__, 'templates') ]

    # IWikiMacroProvider methods

    def get_macros(self):
        yield 'TaskBoard'

    def get_macro_description(self, name):
        return 'Draw a task board ("Kanban").'

    def expand_macro(self, formatter, name, content):
        return ''
