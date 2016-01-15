# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints the author's description information.

Description contains "Home Institute (short) - Department/Group".
Example: CERN - IT/OIS
"""


def format_element(bfo, icon="yes"):
    """Return description for the record.

    :param string icon: display icon for the element if 'yes'
    """
    result = ""
    description = bfo.fields("371__h")

    if description:
        result = description[0]
        if icon.lower() == "yes":
            icon_class = "fa fa-home"
            result = "<i class='{0}'></i> {1}".format(icon_class, result)

    return result


def escape_values(bfo):
    """Escape return value of element.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
