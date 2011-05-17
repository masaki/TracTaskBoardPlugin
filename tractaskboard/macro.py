# -*- coding: utf-8 -*-

import re
import pkg_resources
from genshi.builder import tag

from trac.core import *
from trac.ticket.api import TicketSystem
from trac.ticket.query import Query
from trac.wiki.api import parse_args, IWikiMacroProvider
from trac.web.chrome import add_script, add_stylesheet, ITemplateProvider

class Macro(Component):
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
        return [ ('tractaskboard', pkg_resources.resource_filename(__name__, 'htdocs')) ]

    def get_templates_dirs(self):
        return [ pkg_resources.resource_filename(__name__, 'templates') ]

    # IWikiMacroProvider methods

    def get_macros(self):
        yield 'TaskBoard'

    def get_macro_description(self, name):
        return 'Draw a task board ("Kanban").'

    def expand_macro(self, formatter, name, content):
        req = formatter.req
        add_script(req, 'tractaskboard/js/jquery-ui.js')
        add_script(req, 'tractaskboard/js/jquery.equalheights.js')
        add_script(req, 'tractaskboard/js/tractaskboard.js')
        add_stylesheet(req, 'tractaskboard/css/tractaskboard.css')

        kw = { 'query': '' }
        for arg in re.compile(r'\s*,\s*').split(content):
            k,v = arg.split(':')
            kw[k] = v
        if kw.get('status'):
            kw['status'] = kw['status'].split('|')
        self.env.log.debug(kw)

        tickets = self._get_tickets(req, kw)
        if tickets == None:
            raise TracError('No data matched')

        return self._render(req, tickets, kw)


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

    def _render(self, req, tickets, args):
        board = tag.div(class_='taskboard')

        width = 100/len(tickets) - 1
        for label in args['status']:
            # ticket lane
            lane = tag.div(
                tag.h2(label, class_='taskboard_lane_status'),
                class_='taskboard_lane',
                style="width: %s%%" % width
            )
            board.append(lane)

            ul = tag.ul(class_='taskboard_tickets')
            lane.append(ul)
            for ticket in tickets[label]:
                # ticket
                li = tag.li(
                    tag.h3(
                        tag.a("#%s" % ticket['id'], href=req.href.ticket(ticket['id'])),
                        tag.span(ticket['summary'])
                    ),
                    tag.a(href=req.href.tractaskboard(), class_='taskboard_api', style='display:none'),
                    class_='taskboard_ticket',
                    id="taskboard_ticket_%s" % ticket['id'],
                )
                ul.append(li)

                # ticket params
                fields = [ 'owner', 'priority', 'milestone', 'component', 'type' ]
                table = tag.table
                li.append(table)
                for key in fields:
                    value = ticket[key]
                    table.append(tag.tr(tag.th(key), tag.td(value, class_=key)))

        return board
