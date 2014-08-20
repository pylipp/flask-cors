# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Flask-CORS is a simple extension to Flask allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2014 by Cory Dolphin.
    :license: MIT, see LICENSE for more details.
"""

from tests.base_test import FlaskCorsTestCase, AppConfigTest
from tests.test_origins import OriginsTestCase
from flask import Flask, jsonify

try:
    # this is how you would normally import
    from flask.ext.cors import *
except:
    # support local usage without installed package
    from flask_cors import *


class AppExtensionDefaultTestCase(AppConfigTest, OriginsTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        CORS(self.app)

        @self.app.route('/')
        @cross_origin()
        def wildcard():
            return 'Welcome!'

        @self.app.route('/test_list')
        @cross_origin(origins=["http://foo.com", "http://bar.com"])
        def test_list():
            return 'Welcome!'

        @self.app.route('/test_string')
        @cross_origin(origins="http://foo.com")
        def test_string():
            return 'Welcome!'

        @self.app.route('/test_set')
        @cross_origin(origins=set(["http://foo.com", "http://bar.com"]))
        def test_set():
            return 'Welcome!'


class AppExtensionRegexp(AppConfigTest, OriginsTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={
            r'/': {},
            r'/test_list': {'origins': ["http://foo.com", "http://bar.com"]},
            r'/test_string': {'origins': 'http://foo.com'},
            r'/test_set': {'origins': set(["http://foo.com", "http://bar.com"])}
        })

        @self.app.route('/')
        def wildcard():
            return 'Welcome!'

        @self.app.route('/test_list')
        def test_list():
            return 'Welcome!'

        @self.app.route('/test_string')
        def test_string():
            return 'Welcome!'

        @self.app.route('/test_set')
        def test_set():
            return 'Welcome!'


class AppExtensionList(FlaskCorsTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        CORS(self.app, resources=[r'/test_exposed', r'/test_other_exposed'],
             origins=['http://foo.com, http://bar.com'])

        @self.app.route('/unexposed')
        def unexposed():
            return 'Not exposed over CORS!'

        @self.app.route('/test_exposed')
        def exposed1():
            return 'Welcome!'

        @self.app.route('/test_other_exposed')
        def exposed2():
            return 'Welcome!'

        def test_exposed(self):
            for resp in self.iter_responses('/test_exposed'):
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.headers.get(ACL_ORIGIN),
                                 'http://foo.com, http://bar.com')

        def test_exposed2(self):
            for resp in self.iter_responses('/test_exposed2'):
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.headers.get(ACL_ORIGIN),
                                 'http://foo.com, http://bar.com')

        def test_unexposed(self):
            for resp in self.iter_responses('/test_exposed2'):
                self.assertEqual(resp.status_code, 200)
                self.assertFalse(ACL_ORIGIN in resp.headers)


class AppExtensionString(FlaskCorsTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        CORS(self.app, resources=r'/api/*', headers='Content-Type')

        @self.app.route('/api/v1/foo')
        def exposed1():
            return jsonify(success=True)

        @self.app.route('/api/v1/bar')
        def exposed2():
            return jsonify(success=True)

        @self.app.route('/api/v1/special')
        @cross_origin(origins='http://foo.com')
        def overridden():
            return jsonify(special=True)

        @self.app.route('/')
        def index():
            return 'Welcome'

    def test_exposed(self):
        for path in '/api/v1/foo', '/api/v1/bar':
            for resp in self.iter_responses(path):
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.headers.get(ACL_ORIGIN), '*')
                self.assertEqual(resp.headers.get(ACL_HEADERS),
                                 'Content-Type')

    def test_unexposed(self):
        for resp in self.iter_responses('/'):
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(ACL_ORIGIN in resp.headers)
            self.assertFalse(ACL_HEADERS in resp.headers)

    def test_override(self):
        for resp in self.iter_responses('/api/v1/special'):
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://foo.com')

            self.assertFalse(ACL_HEADERS in resp.headers)


class AppExtensionError(FlaskCorsTestCase):
    def test_value_error(self):
        try:
            app = Flask(__name__)
            CORS(app, resources=5)
            self.assertTrue(False, "Should've raised a value error")
        except ValueError:
            pass

if __name__ == "__main__":
    unittest.main()
