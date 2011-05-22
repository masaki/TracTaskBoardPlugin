# -*- coding: utf-8 -*-

from datetime import date
import re

from trac.core import *
from trac.config import Option
from trac.ticket.model import Ticket
from trac.web.api import IRequestHandler

class TaskBoardChangeHandler(Component):
    implements(IRequestHandler)

    accepted_field = Option('tractaskboard', 'accepted_field', '')
    closed_field   = Option('tractaskboard', 'closed_field',   '')

    # IRequestHandler methods

    def match_request(self, req):
        return re.compile(r'/taskboard(?:/.*)?$').match(req.path_info)

    def process_request(self, req):
        self._update_ticket(req)
        self._write_response(req)

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

    def _write_response(self, req):
        body = 'OK'
        req.send_response(200)
        req.send_header('Content-Type', 'content=text/plain; charset=UTF-8')
        req.send_header('Content-Length', str(len(body)))
        req.send_header('Cache-Control', 'no-cache')
        req.end_headers()
        req.write(body)
