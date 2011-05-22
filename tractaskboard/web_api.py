# -*- coding: utf-8 -*-

from datetime import date
import re
try:
    import json
except ImportError:
    import simplejson as json

from trac.core import *
from trac.config import Option
from trac.ticket.model import Ticket
from trac.web.api import IRequestHandler

class TaskBoardChangeHandler(Component):
    implements(IRequestHandler)

    accepted_field = Option('taskboard', 'accepted_field', '')
    closed_field   = Option('taskboard', 'closed_field',   '')

    # IRequestHandler methods

    def match_request(self, req):
        return re.compile(r'/taskboard(?:/.*)?$').match(req.path_info)

    def process_request(self, req):
        if req.path_info == '/taskboard/workflow':
            self._process_workflow(req)
        elif req.path_info == '/taskboard/ticket':
            self._process_ticket(req)

    def _process_workflow(self, req):
        #action = self._detect_action(req)
        self._write_response(req, 200, { 'action': action })

    def _process_ticket(self, req):
        self._update_ticket(req)
        self._write_response(req)

    def _detect_action(self, req):
        return ''

    def _update_ticket(self, req):
        values = req.args
        ticket_id = int(values.pop('id'))
        ticket = Ticket(self.env, ticket_id)

        self._populate_values(values, ticket)
        ticket.populate(values)
        ticket.save_changes(req.authname)

    def _populate_values(self, values, ticket):
        status = values.get('status')

        if status == 'new':
            if self.accepted_field != '':
                values[self.accepted_field] = ''
            if self.closed_field != '':
                values[self.closed_field] = ''
        elif status == 'accepted':
            if self.accepted_field != '':
                values[self.accepted_field] = self._get_today_as_ymd()
            if self.closed_field != '':
                values[self.closed_field] = ''
        elif status == 'closed':
            if self.accepted_field != '' and not ticket.values.get(self.accepted_field):
                values[self.accepted_field] = self._get_today_as_ymd()
            if self.closed_field != '':
                values[self.closed_field] = self._get_today_as_ymd()

    def _get_today_as_ymd(self):
        return date.today().strftime('%Y/%m/%d')

    def _write_response(self, req, status=200, data={}):
        body = json.dumps(data)
        req.send_response(int(status))
        req.send_header('Content-Type', 'application/json; charset=UTF-8')
        req.send_header('Content-Length', str(len(body)))
        req.send_header('Cache-Control', 'no-cache')
        req.end_headers()
        req.write(body)
