# -*- coding: utf-8 -*-

import re
import pkg_resources
from genshi.builder import tag

from trac.core import *
from trac.ticket.api import TicketSystem
from trac.ticket.query import Query
from trac.wiki.api import parse_args, IWikiMacroProvider
from trac.web.chrome import add_script, add_stylesheet, ITemplateProvider, Chrome

class TaskBoardMacro(Component):
    implements(ITemplateProvider, IWikiMacroProvider)

    # taken from QueryChart, thanks
    # http://svn.coderepos.org/share/platform/trac/plugins/querychart/trunk/querychart/macro.py

    def _urlstring_to_reqarg(self,urlstr):
        args={}
        for uslarg in urlstr[1:].split('&'):
            uslarg_sp = uslarg.split('=')
            key = uslarg_sp[0]
            val = '='.join(uslarg_sp[1:])
            if len(val)>1 and val[0] in ['~','^','$','!']:
                if val[0] == '!':
                    args[key+'_mode']=val[:1]
                    val = val[2:]
                else:
                    args[key+'_mode']=val[0]
                    val = val[1:]
            if not args.get(key):
                args[key] = []
            args[key].append(val)
        return args

    def _get_constraints(self, args):

        constraints = {}
        ticket_fields = [f['name'] for f in
                         TicketSystem(self.env).get_ticket_fields()]
        ticket_fields.append('id')

        for field in [k for k in args.keys() if k in ticket_fields]:
            vals = args[field]
            if not isinstance(vals, (list, tuple)):
                vals = [vals]
            if vals:
                mode = args.get(field + '_mode')
                if mode:
                    vals = [mode + x for x in vals]
                constraints[field] = vals

        return constraints

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return [ ('taskboard', pkg_resources.resource_filename(__name__, 'htdocs')) ]

    def get_templates_dirs(self):
        return [ pkg_resources.resource_filename(__name__, 'templates') ]

    # IWikiMacroProvider methods

    def get_macros(self):
        yield 'TaskBoard'

    def get_macro_description(self, name):
        return 'Draw a task board ("Kanban").'

    def expand_macro(self, formatter, name, content):
        req = formatter.req
        add_script(req, 'taskboard/js/jquery-ui.js')
        add_script(req, 'taskboard/js/jquery.form.js')
        add_script(req, 'taskboard/js/taskboard.js')
        add_stylesheet(req, 'taskboard/css/taskboard.css')

        kw = {
            'query' : '',
            'status': [ 'new', 'accepted', 'closed' ],
            'column': [ 'owner', 'priority', 'type', 'component' ],
        }
        for arg in re.compile(r'\s*,\s*').split(content):
            k,v = arg.split(':')
            if k == 'status' or k == 'column':
                v = v.split('|')
            kw[k] = v
        self.env.log.debug(kw)

        tickets = self._get_tickets(req, kw)
        if tickets == None:
            raise TracError('No data matched')

        data = {
            'users'  : [username for username, name, email in self.env.get_known_users()],
            'tickets': tickets,
            'req'    : req,
            'args'   : kw,
        }
        return Chrome(self.env).render_template(req, 'taskboard.html', data, None, fragment=True)


    def _get_tickets(self, req, args):
        query = self._construct_query(req, args)
        self.log.debug(query.get_sql())

        tickets = query.execute(req, db=None, cached_ids=None)
        return self._filter_tickets(tickets, args)

    def _construct_query(self, req, args):
        qstring = args['query']
        columns = args['status']

        if len(qstring) > 1 and qstring[0] != '?':
            qstring = qstring + '&status=' + '|'.join(columns)
            return Query.from_string(self.env, qstring)
        elif len(qstring) > 1 and qstring[0] == '?':
            qstring = qstring + ''.join(['&status=%s' % status for status in columns])
            constraints = self._get_constraints(self._urlstring_to_reqarg(qstring))
            return Query(self.env, constraints=constraints)
        else:
            constraints = self._get_constraints(req.args)
            return Query(self.env, constraints=constraints)

    def _filter_tickets(self, tickets, args):
        if tickets == None:
            return None;

        new_tickets = {}
        for col in args['status']:
            new_tickets[col] = []
        for ticket in tickets:
            if ticket['status'] in args['status']:
                new_tickets[ticket['status']].append(ticket)
        return new_tickets
