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
"""BibFormat element - Prints the author's contact information."""

from invenio.messages import gettext_set_language


def format_email(email, email_href="yes", icon="no", vcard_support="no"):
    """Return formatted email address."""
    vcard_enabled = True if vcard_support.lower() == "yes" else False

    if email_href.lower() == "yes":
        email = "<a {0}href='mailto:{1}'>{1}</a>".format(
            "class='email' " if vcard_enabled else "", email)
    else:
        if vcard_enabled:
            email = "<span class='email'>{0}</span>".format(email)
    if icon.lower() == "yes":
        icon_class = "fa fa-envelope"
        email = "<i class='{0}' style='font-size: 0.9em;'></i> {1}".format(
            icon_class, email)
    return email


def format_phone_number(phone_number, icon="no", vcard_support="no"):
    """Return formatted phone number."""
    if vcard_support.lower() == "yes":
        phone_number = (
            "<span class='tel'>"
            "<span class='type' style='display: none;'>work</span>"
            "<span class='value'>{0}</span>"
            "</span>".format(phone_number))
    if icon.lower() == "yes":
        icon_class = "fa fa-phone"
        phone_number = "<i class='{0}'></i> {1}".format(
            icon_class, phone_number)
    return phone_number


def format_mobile_number(mobile_number, icon="no", vcard_support="no"):
    """Return formatted mobile phone number."""
    if vcard_support.lower() == "yes":
        mobile_number = (
            "<span class='tel'>"
            "<span class='type' style='display: none;'>cell</span>"
            "<span class='value'>{0}</span>"
            "</span>".format(mobile_number))
    if icon.lower() == "yes":
        icon_class = "fa fa-mobile"
        mobile_number = "<i class='{0}'></i> {1}".format(
            icon_class, mobile_number)
    return mobile_number


def format_fax_number(fax_number, icon="no", vcard_support="no"):
    """Return formatted fax number."""
    if vcard_support.lower() == "yes":
        fax_number = (
            "<span class='tel'>"
            "<span class='type' style='display: none;'>fax</span>"
            "<span class='value'>{0}</span>"
            "</span>".format(fax_number))
    if icon.lower() == "yes":
        icon_class = "fa fa-fax"
        fax_number = "<i class='{0}'></i> {1}".format(icon_class, fax_number)
    return fax_number


def format_element(bfo, contact_type="all", vcard_support="no",
                   email_href="yes", icon="no"):
    """Return contact information for the record.

    :param string contact_type: return all contact information if 'all',
        other values: 'email', 'phone', 'mobile', or 'fax'
    :param string vcard_support: enables vCard support if 'yes'
    :param string email_href: link email address using mailto if 'yes'
    :param string icon: display icon for the specified contact_type if 'yes'
    """
    _ = gettext_set_language(bfo.lang)
    result = ""

    # Get all contact information data
    email = bfo.fields("371__m")
    phone_number = bfo.fields("371__k")
    mobile_number = bfo.fields("371__l")
    fax_number = bfo.fields("371__f")

    if contact_type.lower() == "all":
        tbl_row = "<tr><th>{0}</th><td>{1}</td></tr>"
        if email:
            result += tbl_row.format(
                _("Email address"), format_email(
                    email[0].lower(), email_href, vcard_support=vcard_support))
        if phone_number:
            result += tbl_row.format(
                _("Phone number"), format_phone_number(
                    phone_number[0], vcard_support=vcard_support))
        if mobile_number:
            result += tbl_row.format(
                _("Mobile number"), format_mobile_number(mobile_number[0]))
        if fax_number:
            result += tbl_row.format(
                _("Fax number"), format_fax_number(fax_number[0]))
    elif contact_type.lower() == "email":
        if email:
            result = format_email(email[0].lower(), email_href, icon)
    elif contact_type.lower() == "phone":
        if phone_number:
            result = format_phone_number(phone_number[0], icon)
    elif contact_type.lower() == "mobile":
        if mobile_number:
            result = format_mobile_number(mobile_number[0], icon)
    elif contact_type.lower() == "fax":
        if fax_number:
            result = format_fax_number(fax_number[0], icon)

    return result


def escape_values(bfo):
    """Escape return value of element.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
