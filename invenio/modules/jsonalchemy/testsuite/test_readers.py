# -*- coding: utf-8 -*-
##
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

"""Unit tests for the parser engine."""

__revision__ = \
    "$Id$"

from invenio.base.wrappers import lazy_import
from flask.ext.registry import PkgResourcesDirDiscoveryRegistry, \
    ImportPathRegistry, RegistryProxy
from invenio.ext.registry import ModuleAutoDiscoverySubRegistry
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

Field_parser = lazy_import('invenio.modules.jsonalchemy.parser:FieldParser')
Model_parser = lazy_import('invenio.modules.jsonalchemy.parser:ModelParser')

TEST_PACKAGES = ['invenio.modules.jsonalchemy.testsuite', ]

test_registry = RegistryProxy('testsuite', ImportPathRegistry,
                              initial=TEST_PACKAGES)

field_definitions = lambda: PkgResourcesDirDiscoveryRegistry(
    'fields', registry_namespace=test_registry)
model_definitions = lambda: PkgResourcesDirDiscoveryRegistry(
    'models', registry_namespace=test_registry)
function_proxy = lambda: ModuleAutoDiscoverySubRegistry(
    'functions', registry_namespace=test_registry)


class TestReader(InvenioTestCase):

    @classmethod
    def setUpClass(cls):
        """Invalidate any previous field definition"""
        Field_parser._field_definitions = {}
        Field_parser._legacy_field_matchings = {}
        Model_parser._model_definitions = {}

    def setUp(self):
        self.app.extensions['registry'][
            'testsuite.fields'] = field_definitions()
        self.app.extensions['registry'][
            'testsuite.models'] = model_definitions()
        self.app.extensions['registry'][
            'testsuite.functions'] = function_proxy()

    def tearDown(self):
        del self.app.extensions['registry']['testsuite.fields']
        del self.app.extensions['registry']['testsuite.models']
        del self.app.extensions['registry']['testsuite.functions']

    def test_wrong_parameters(self):
        """JSONAlchemy - wrong parameters"""
        from invenio.modules.jsonalchemy.errors import ReaderException
        from invenio.modules.jsonalchemy.reader import Reader
        from invenio.modules.jsonalchemy.wrappers import SmartJson

        self.assertRaises(
            ReaderException, Reader.translate, blob=None, json_class=None)
        self.assertRaises(
            ReaderException, Reader.translate, blob={}, json_class=dict)
        self.assertRaises(NotImplementedError, Reader.add, json=SmartJson(
            master_format='json'), fields='foo')


class TestJSONReader(InvenioTestCase):

    @classmethod
    def setUpClass(cls):
        """Invalidate any previous field definition"""
        Field_parser._field_definitions = {}
        Field_parser._legacy_field_matchings = {}
        Model_parser._model_definitions = {}

    def setUp(self):
        self.app.extensions['registry'][
            'testsuite.fields'] = field_definitions()
        self.app.extensions['registry'][
            'testsuite.models'] = model_definitions()
        self.app.extensions['registry'][
            'testsuite.functions'] = function_proxy()
        Field_parser.reparse('testsuite')
        Model_parser.reparse('testsuite')

    def tearDown(self):
        del self.app.extensions['registry']['testsuite.fields']
        del self.app.extensions['registry']['testsuite.models']
        del self.app.extensions['registry']['testsuite.functions']

    def test_json_reader(self):
        """JSONAlchemy - Json reader"""
        from invenio.modules.jsonalchemy.reader import Reader
        from invenio.modules.jsonalchemy.wrappers import SmartJson

        blob = {'abstract': {'summary': 'Candidate for the associated production of the Higgs boson and Z boson. Both, the Higgs and Z boson decay into 2 jets each. The green and the yellow jets belong to the Higgs boson. They represent the fragmentation of a bottom andanti-bottom quark. The red and the blue jets stem from the decay of the Z boson into a quark anti-quark pair. Left: View of the event along the beam axis. Bottom right: Zoom around the interaction point at the centre showing detailsof the fragmentation of the bottom and anti-bottom quarks. As expected for b quarks, in each jet the decay of a long-lived B meson is visible. Top right: "World map" showing the spatial distribution of the jets in the event.'},
                'authors': [{'first_name': '',
                             'full_name': 'Photolab',
                             'last_name': 'Photolab'}],
                'collection': {'primary': 'PICTURE'},
                'keywords': [{'term': 'LEP'}],
                'number_of_authors': 1,
                'title': {'title': 'ALEPH experiment: Candidate of Higgs boson production'}}

        json = Reader.translate(
            blob, SmartJson, master_format='json', namespace='testsuite')
        self.assertIsNotNone(json)
        self.assertTrue(all([key in json for key in blob.keys()]))
        self.assertTrue('__meta_metadata__' in json)
        self.assertTrue('modification_date' in json)
        self.assertEquals(json['default_values_test'],
                          {'field2': False, 'field3': False, 'field1': False})

    def test_json_reader_add_and_set_fields(self):
        """JSONAlchemy - add and set fields"""
        from invenio.modules.jsonalchemy.reader import Reader
        from invenio.modules.jsonalchemy.wrappers import SmartJson

        blob = {'abstract': {'summary': 'Candidate for the associated production of the Higgs boson and Z boson. Both, the Higgs and Z boson decay into 2 jets each. The green and the yellow jets belong to the Higgs boson. They represent the fragmentation of a bottom andanti-bottom quark. The red and the blue jets stem from the decay of the Z boson into a quark anti-quark pair. Left: View of the event along the beam axis. Bottom right: Zoom around the interaction point at the centre showing detailsof the fragmentation of the bottom and anti-bottom quarks. As expected for b quarks, in each jet the decay of a long-lived B meson is visible. Top right: "World map" showing the spatial distribution of the jets in the event.'},
                'authors': [{'first_name': '',
                             'full_name': 'Photolab',
                             'last_name': 'Photolab'}],
                'collection': {'primary': 'PICTURE'},
                'keywords': [{'term': 'LEP'}]}

        json = Reader.translate(
            blob, SmartJson, master_format='json', namespace='testsuite')
        self.assertIsNotNone(json)
        self.assertTrue('abstract' in json)
        Reader.add(json, 'number_of_authors', blob)
        self.assertTrue('number_of_authors' in json)
        self.assertEquals(json.get('number_of_authors'), 1)

        Reader.set(
            json, 'title', {'title': 'ALEPH experiment: Candidate of Higgs boson production'})
        self.assertTrue('title' in json)
        self.assertTrue('title' in json['__meta_metadata__'])
        Reader.set(json, 'title')
        self.assertEquals(
            json['title'], {'title': 'ALEPH experiment: Candidate of Higgs boson production'})
        Reader.set(json, 'title', {'title': 'New title'})
        self.assertEquals(json['title'], {'title': 'New title'})

        Reader.set(json, 'foo', 'bar')
        self.assertTrue('foo' in json)
        self.assertTrue('foo' in json['__meta_metadata__'])
        self.assertEquals('UNKNOWN', json['__meta_metadata__']['foo']['type'])
        self.assertEquals('bar', json['foo'])


TEST_SUITE = make_test_suite(TestReader, TestJSONReader)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
