# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2015, 2016 CERN.
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
"""BibFormat element - Prints the control number of an Authority Record.
"""

from invenio.bibauthority_config import \
    CFG_BIBAUTHORITY_AUTHORITY_COLLECTION_NAME, \
    CFG_BIBAUTHORITY_RECORD_CONTROL_NUMBER_FIELD, \
    CFG_BIBAUTHORITY_RECORD_AUTHOR_CONTROL_NUMBER_FIELDS
from invenio.bibauthority_engine import \
    get_low_level_recIDs_from_control_no, \
    get_dependent_records_for_control_no
from invenio.config import CFG_CACHEDIR
from invenio.viafutils import get_wikipedia_link, get_wiki_link_from_record

import json
import urllib2
import os.path

__revision__ = "$Id$"


def get_inspire_name_by_inspire_id(
        inspire_id,
        json_file=os.path.join(CFG_CACHEDIR, "inspirehep-names-mapping.json")):
    """Get INSPIRE-HEP-name given the INSPIRE-ID.

    :param string inspire_id: INSPIRE-ID
    :param file json_file: INSPIRE-HEP mapping
    """
    inspire_name = None
    try:
        with open(json_file) as f:
            try:
                inspire_mapping = json.load(f)
                inspire_name = inspire_mapping.get(inspire_id)
            except ValueError:
                pass
    except EnvironmentError:
        pass
    return inspire_name


def get_inspire_profile(inspire_id, val, use_inspirehepname=False):
    """Get HTML element for INSPIRE-HEP Profile.

    :param bool use_inspirehepname: use INSPIRE-HEP search query if
        False, otherwise call get_inspire_name_by_inspire_id
    """
    result = None

    if use_inspirehepname:
        inspirehep_name = get_inspire_name_by_inspire_id(inspire_id)
        if inspirehep_name:
            url = "https://inspirehep.net/author/profile/{0}".format(
                inspirehep_name)
    else:
        url = ("http://inspirehep.net/search?cc=HepNames&p=035__a%3A{0}&of=hd"
               .format(inspire_id))

    result = "<a href='{0}'>{1}</a>".format(url, val)
    return result


def get_cern_phonebook(cern_id, val):
    """Get HTML element for CERN Phonebook."""
    phonebook_url = (
        "https://phonebook.cern.ch/phonebook/#personDetails/?id={0}"
        .format(cern_id))
    return "<a href='{0}'>{1}</a>".format(phonebook_url, val)


def get_cern_profile(cern_id, val):
    """Get HTML element for CERN Profile."""
    html_element = None
    cern_profile_url = "http://profiles.web.cern.ch/{0}".format(cern_id)
    req = urllib2.Request(cern_profile_url)

    try:
        urllib2.urlopen(req)
        html_element = "<a href='{0}'>{1}</a>".format(cern_profile_url, val)
    except urllib2.HTTPError:
        pass
    return html_element


def format_element(bfo, print_title="yes"):
    """ Prints the control number of an author authority record in HTML.
    By default prints brief version.

    @param brief: whether the 'brief' rather than the 'detailed' format
    @type brief: 'yes' or 'no'
    """

    from invenio.messages import gettext_set_language
    _ = gettext_set_language(bfo.lang)    # load the right message language

    control_nos = [d['a'] for d in bfo.fields('035__') if d['a'] is not None]
    control_nos = filter(None, control_nos) # fastest way to remove empty ""s

    links_formatted = []
    for control_no in control_nos:
        from urllib import quote
        image_pattern = "<a href='%(external_article)s'><img class='author_usefull_link' src='/img/%(image)s'/>%(text)s</a>"

        if (control_no.find("|(VIAF)") != -1):
            viaf_id = control_no.split("|(VIAF)")[1]
            link_to_wikipedia = get_wiki_link_from_record(bfo)
            if not link_to_wikipedia:
                link_to_wikipedia = get_wikipedia_link(viaf_id)
            ## Wikipedia link with wiki icon
            if link_to_wikipedia:
                image_element = image_pattern % { "text": "Wikipedia", "image": "wikipedia.png", "external_article": link_to_wikipedia}
                links_formatted.append(image_element)
            ## VIAF link
            image_element = image_pattern \
                    % { "text" : "VIAF cluster","image": "viaf.png", "external_article": str("http://viaf.org/viaf/"+viaf_id) }
            links_formatted.append(image_element)
            ## Library of congress link

        if (control_no.find("|(DLC)") != -1):
            dlc_id = control_no.split("|(DLC)")[1].replace(" ","")
            link_to_lccn = "http://lccn.loc.gov/"+ dlc_id
            image_element = image_pattern % { "text": "Library of Congress", "image": "library_of_congress.png", "external_article" : link_to_lccn }
            links_formatted.append(image_element)

        if (control_no.find("|(INSPIRE)") != -1):
            inspire_profile = get_inspire_profile(
                    control_no.split("|(INSPIRE)")[1],
                    _("INSPIRE-HEP Profile"))

            (links_formatted.append(inspire_profile)
                if inspire_profile is not None else None)

        if (control_no.find("|(SzGeCERN)") != -1):
            cern_id = control_no.split("|(SzGeCERN)")[1]
            links_formatted.append(
                get_cern_phonebook(cern_id, _("CERN Phonebook")))

            html_element = get_cern_profile(cern_id, _("CERN Profile"))
            if html_element:
                links_formatted.append(html_element)

    result = ""
    if links_formatted:
        result = "<ul><li>" + "</li><li> ".join(links_formatted) + "</li></ul>"

    if print_title.lower() == "yes":
        title = "<strong>" + _("Useful links") + "</strong>"
        result = title + ": " + result

    return result


def escape_values(bfo):
    """Escape return value of element.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
