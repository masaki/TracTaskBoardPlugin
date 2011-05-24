# -*- coding: utf-8 -*-

from datetime import date
import re

# taken from XmlRpcPlugin
try:
    import json
    if not (hasattr(json, 'JSONEncoder') and hasattr(json, 'JSONDecoder')):
        raise AttributeError("Incorrect JSON library found.")
except (ImportError, AttributeError):
    import simplejson as json

from trac.core import *
from trac.ticket.default_workflow import ConfigurableTicketWorkflow
from trac.ticket.model import Ticket
from trac.web.api import IRequestHandler

class TaskBoardChangeHandler(Component):
    implements(IRequestHandler)

    def __init__(self):
        self.controller = ConfigurableTicketWorkflow(self.env)

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/taskboard'

    def process_request(self, req):
        self.env.log.debug("taskboard API received: %s" % req.args)
        if not req.args.get('id') or not req.args.get('status'):
            self._write_response(req, 400, {})
            return

        ticket = Ticket(self.env, int(req.args['id']))
        ticket_available_actions = []
        for weight, action in self.controller.get_ticket_actions(req, ticket):
            changes = self.controller.get_ticket_changes(req, ticket, action)
            if not changes.get('status'):
                continue
            if changes['status'] == req.args['status']:
                ticket_available_actions.append([ weight, action ])
        ticket_available_actions.sort()
        self.env.log.debug("taskboard API actions: %s" % ticket_available_actions)

        if len(ticket_available_actions) > 0:
            actions = ticket_available_actions.pop()
            self._write_response(req, 200, { 'action': actions[1] })
        else:
            self._write_response(req, 400, {})

    def _write_response(self, req, status=200, data={}):
        body = json.dumps(data)
        req.send_response(int(status))
        req.send_header('Content-Type', 'application/json; charset=UTF-8')
        req.send_header('Content-Length', str(len(body)))
        req.send_header('Cache-Control', 'no-cache')
        req.end_headers()
        req.write(body)
