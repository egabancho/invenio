{#
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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
#}

{% extends "format/record/Default_HTML_detailed_base.tpl" %}

{% block header %}
    <h3>{{ record.get('title.title') }}</h3>
{% endblock %}

{% block details %}
    {{ record.get('authors.full_name')|join('; ') }}
{% endblock %}

{% block abstract %}
    <small><strong>Abstract: </strong>
    {{ record.get('abstract.summary')}}
    </small><br />

    <br /><small><strong>Keyword(s): </strong></small>
    {{ record.get('keywords.term')|join(', ')|wrap(prefix='<small>', suffix='</small>')}}
     </strong></small>
{% endblock %}
