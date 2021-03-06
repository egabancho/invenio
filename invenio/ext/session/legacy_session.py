# -*- coding: utf-8 -*-

## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013, 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Implementation of legacy Invenio methods for Flask session."""

from flask import current_app, request
from flask.sessions import SessionMixin
from flask.ext.login import current_user
from werkzeug.datastructures import CallbackDict


class Session(CallbackDict, SessionMixin):

    """Implement compatible legacy Invenio session."""

    def __init__(self, initial=None, sid=None):
        """Initialize session with optional default value."""
        self.sid = sid
        self.logging_in = False
        self.modified = initial is not None

        def _on_update(d):
            d.modified = True

        CallbackDict.__init__(self, initial, _on_update)

    def need_https(self):
        """Check if the user was previously authenticated.

        If True session identifier need to be sent via HTTPS.
        """
        return request.cookies.get(
            current_app.session_cookie_name + 'stub', 'NO') == 'HTTPS'

    def delete(self, clear=True):
        """Delete the session."""
        if clear:
            self.clear()

    def invalidate(self):
        """Declare the session as invalid."""
        self._invalid = 1

    def set_remember_me(self, remember_me=True):
        """Set or unset the ``_remember_me`` flag.

        :param remember_me: True if the session cookie should last one day or
            until the browser is closed.
        """
        self._remember_me = remember_me
        self['_permanent'] = remember_me

    def save_ip(self, request):
        """Save IP for current scheme."""
        remote_ip = request.remote_addr
        scheme_a = '_http_ip' if request.scheme == 'http' else '_https_ip'
        scheme_b = '_https_ip' if request.scheme == 'http' else '_http_ip'

        if scheme_a not in self:
            self[scheme_a] = remote_ip
        if scheme_b not in self:
            self[scheme_b] = None

    def check_ip(self, request):
        """Check that session is used from the same IP where it was created."""
        remote_ip = request.remote_addr
        if self.get('_{0}_ip'.format(request.scheme), remote_ip) != remote_ip:
            return False
        return True

    def _get_uid(self):
        return self.get('user_id', -1)

    def _set_uid(self, uid):
        if self.get('user_id') != uid:
            self.logging_in = True
        self['user_id'] = self['_uid'] = self['uid'] = uid

    def _get_user_info(self):
        return current_user

    uid = property(_get_uid, _set_uid)
    user_info = property(_get_user_info)
    del _get_uid, _set_uid, _get_user_info
