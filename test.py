#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012, Polar Mobile.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name Polar Mobile nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL POLAR MOBILE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Used to define and run unit tests.
from unittest import TestCase, main

# Used to mimic objects in order to test more complex calls.
from mock import patch

# Used to generate fake http requests and test for responses.
from itty import Request, Response

# Used to test error handling code in errors.py.
from simplejson import dumps
from publisher.errors import (bad_syntax, unauthorized, forbidden, not_found,
                              internal_error)
from publisher.utils import (JsonBadSyntax, JsonUnauthorized, JsonForbidden,
                             JsonNotFound, JsonAppError)

# Used to test error encoding.
from publisher.utils import encode_error, raise_error, check_base_url

# Used to test auth handling code.
from publisher.auth import (check_authorization_header, decode_body,
                            check_device, check_auth_params, auth,
                            check_publisher_auth_params,)

# Used to test the model code.
from publisher.model import model

# Used to reset the models singleton and test timeouts.
from publisher.constants import SESSION_TIMEOUT

# Used to test the timestamps in model.py.
from datetime import datetime, timedelta

# Used to test the validate API entry point.
from publisher.validate import get_session_id, validate


def test_start_response(status, headers):
    '''
    This function is a testing replacement for the start_response function
    provided by the WSGI web framework. It is called by the request object to
    start the transfer of data back to the client. For testing purposes, this
    function does not do anything.
    '''
    # In python, pass is a keyword that is synonymous for "don't do
    # anything".
    pass


def create_request(http_path):
    '''
    A helper function used to create fake request objects for testing.
    '''
    # WSGI and itty operate like CGI. They have a dictionary of environment
    # variables that specify the parameters of the request. For testing, all
    # we care to specify is the PATH_INFO variable, which is the URL that the
    # request is processed with.
    environ = {}
    environ['PATH_INFO'] = http_path

    # Create the request object. start_response is a function pointer to an
    # internal function that itty uses to send a request. For the purposes of
    # testing, we replace it with a function that does nothing.
    result = Request(environ, start_response=test_start_response)

    # Return the result.
    return result


class TestUtils(TestCase):
    '''
    Test the code in publisher/utils.py.
    '''
    def test_encode_error(self):
        '''
        Tests generation of an error report.
        '''
        # Create the seed data for the test.
        url = '/test/'
        code = 'TestError'
        message = 'This is a test error.'

        # Call encode_error and get the result.
        result = encode_error(url, code, message)

        # Check the result.
        content = '{"error": {"message": "This is a test error.", '\
            '"code": "TestError", "resource": "/test/"}}'
        self.assertEqual(result, content)

    def test_raise_error_bad_syntax(self):
        '''
        Tests generation of a 400 error.
        '''
        # Create the seed data for the test.
        url = '/test/'
        code = 'TestError'
        message = 'This is a test error.'
        status = 400

        # Call raise_error and get the result.
        try:
            raise_error(url, code, message, status)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = u'{"error": {"message": "This is a test error.", '\
                '"code": "TestError", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_raise_error_unauthorized(self):
        '''
        Tests generation of a 401 error.
        '''
        # Create the seed data for the test.
        url = '/test/'
        code = 'TestError'
        message = 'This is a test error.'
        status = 401

        # Call raise_error and get the result.
        try:
            raise_error(url, code, message, status)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonUnauthorized))
            content = u'{"error": {"message": "This is a test error.", '\
                '"code": "TestError", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_raise_error_forbidden(self):
        '''
        Tests generation of a 403 error.
        '''
        # Create the seed data for the test.
        url = '/test/'
        code = 'TestError'
        message = 'This is a test error.'
        status = 403

        # Call raise_error and get the result.
        try:
            raise_error(url, code, message, status)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonForbidden))
            content = u'{"error": {"message": "This is a test error.", '\
                '"code": "TestError", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_raise_error_not_found(self):
        '''
        Tests generation of a 404 error.
        '''
        # Create the seed data for the test.
        url = '/test/'
        code = 'TestError'
        message = 'This is a test error.'
        status = 404

        # Call raise_error and get the result.
        try:
            raise_error(url, code, message, status)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonNotFound))
            content = u'{"error": {"message": "This is a test error.", '\
                '"code": "TestError", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_raise_error_internal_error(self):
        '''
        Tests generation of a 500 error.
        '''
        # Create the seed data for the test.
        url = '/test/'
        code = 'TestError'
        message = 'This is a test error.'
        status = 500

        # Call raise_error and get the result.
        try:
            raise_error(url, code, message, status)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonAppError))
            content = u'{"error": {"message": "This is a test error.", '\
                '"code": "TestError", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_base_url_api(self):
        '''
        Tests base url checking on the api parameter.
        '''
        # Create the seed data for the test.
        url = '/test/'
        api = 'test'
        version = 'v1.0.0'
        format = 'json'

        # Call the check_base_url function and expect an exception.
        try:
            check_base_url(url, api, version, format)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonNotFound))
            content = '{"error": {"message": "The requested api is not '\
                'implemented: test", "code": "InvalidAPI", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_base_url_version(self):
        '''
        Tests base url checking on the version parameter.
        '''
        # Create the seed data for the test.
        url = '/test/'
        api = 'paywallproxy'
        version = 'test'
        format = 'json'

        # Call the check_base_url function and expect an exception.
        try:
            check_base_url(url, api, version, format)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonNotFound))
            content = '{"error": {"message": "The requested version is not '\
                'implemented: test", "code": "InvalidVersion", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_base_url_format(self):
        '''
        Tests base url checking on the format parameter.
        '''
        # Create the seed data for the test.
        url = '/test/'
        api = 'paywallproxy'
        version = 'v1.0.0'
        format = 'test'

        # Call the check_base_url function and expect an exception.
        try:
            check_base_url(url, api, version, format)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonNotFound))
            content = '{"error": {"message": "The requested format is not '\
                'implemented: test", "code": "InvalidFormat", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')


class TestErrors(TestCase):
    '''
    Test the code in publisher/errors.py.
    '''
    def test_bad_syntax_pass(self):
        '''
        Checks to make sure that json encoded exceptions are passed through
        the exception handling framework properly.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        content = unicode(dumps('test'))
        exception = JsonBadSyntax(content)

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = bad_syntax(request, exception)

        # Check the result.
        self.assertEqual(result, content)

    def test_bad_syntax_unknown_exception(self):
        '''
        Checks to make sure that the framework fails when an unknown exception
        is passed.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        exception = Exception(u'test')

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested and ensure it raises
        # an assertion error.
        self.assertRaises(AssertionError, bad_syntax, request, exception)

    def test_unauthorized_pass(self):
        '''
        Checks to make sure that json encoded exceptions are passed through
        the exception handling framework properly.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        content = unicode(dumps('test'))
        exception = JsonUnauthorized(content)

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = unauthorized(request, exception)

        # Check the result.
        self.assertEqual(result, content)

    def test_unauthorized_unknown_exception(self):
        '''
        Checks to make sure that the framework fails when an unknown exception
        is passed.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        exception = Exception(u'test')

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested and ensure it raises
        # an assertion error.
        self.assertRaises(AssertionError, unauthorized, request, exception)

    def test_forbidden_pass(self):
        '''
        Checks to make sure that json encoded exceptions are passed through
        the exception handling framework properly.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        content = unicode(dumps('test'))
        exception = JsonForbidden(content)

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = forbidden(request, exception)

        # Check the result.
        self.assertEqual(result, content)

    def test_forbidden_unknown_exception(self):
        '''
        Checks to make sure that the framework fails when an unknown exception
        is passed.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        exception = Exception(u'test')

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested and ensure it raises
        # an assertion error.
        self.assertRaises(AssertionError, forbidden, request, exception)

    def test_not_found_pass(self):
        '''
        Checks to make sure that json encoded exceptions are passed through
        the exception handling framework properly.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        content = unicode(dumps('test'))
        exception = JsonNotFound(content)

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = not_found(request, exception)

        # Check the result.
        self.assertEqual(result, content)

    def test_not_found_unknown_exception(self):
        '''
        Tests handling of a 404 error when an unknown exception is passed.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        exception = Exception(u'test')

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = not_found(request, exception)

        # Check the result.
        content = u'{"error": {"message": "No handler could be found for the '\
            'requested resource.", "code": "NoHandler", "resource": "/test/"}}'
        self.assertEqual(result, content)

    def test_internal_error_pass(self):
        '''
        Checks to make sure that json encoded exceptions are passed through
        the exception handling framework properly.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        content = unicode(dumps('test'))
        exception = JsonAppError(content)

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = internal_error(request, exception)

        # Check the result.
        self.assertEqual(result, content)

    def test_internal_error_unknown_exception(self):
        '''
        Tests handling of a 500 error when an unknown exception is passed.
        '''
        # Create the seed data for the test.
        request = create_request('/test/')
        exception = Exception(u'test')

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Issue the request to the method being tested.
        result = internal_error(request, exception)

        # Check the result.
        content = u'{"error": {"message": "An internal server error '\
            'occurred.", "code": "InternalError", "resource": "/test/"}}'
        self.assertEqual(result, content)


class TestAuth(TestCase):
    '''
    Test the code in publisher/auth.py.
    '''
    def test_check_authorization_header_exists(self):
        '''
        Tests to see if the check_authorization_header function checks for
        the existence of the "Authorization" header.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}

        # Call the check_authorization_header function and expect an exception.
        try:
            check_authorization_header(url, environment)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The authorization token has '\
                'not been provided.", "code": "InvalidAuthScheme", '\
                '"resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_authorization_header_value(self):
        '''
        Tests to see if the check_authorization_header function checks for
        the right authorization header.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'invalid'

        # Call the check_authorization_header function and expect an exception.
        try:
            check_authorization_header(url, environment)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The authorization token is '\
                'incorrect.", "code": "InvalidAuthScheme", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_authorization_header(self):
        '''
        Tests to see if the check_authorization_header function passes a
        proper header.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'

        # Call the check_authorization_header function.
        check_authorization_header(url, environment)

    def test_decode_body_invalid_json(self):
        '''
        Tests to see if the decode_json function checks for invalid json.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = '{"test'

        # Call the check_device function and expect an exception.
        try:
            decode_body(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "Could not decode post body. '\
                'json is expected.", "code": "InvalidFormat", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_decode_body_many_arguments(self):
        '''
        Tests to see if the decode_json function checks for an invalid number
        of json parameters.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['parameter1'] = 'test'
        body['parameter2'] = 'test'
        body['parameter3'] = 'test'
        body['parameter4'] = 'test'

        # Call the check_device function and expect an exception.
        try:
            decode_body(url, dumps(body))

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "Post body has an invalid '\
                'number of parameters.", "code": "InvalidFormat", '\
                '"resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_device_exists(self):
        '''
        Tests to see if the check_device function checks for a missing device.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['test'] = 'test'

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The device has not been '\
                'provided.", "code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_device_type(self):
        '''
        Tests to see if the check_device function checks for an invalid device
        type.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = 'test'

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The device is not a map.", '\
                '"code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_manufacturer_exists(self):
        '''
        Tests to see if the check_device function checks for a missing
        manufacturer.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The manufacturer has not been '\
                'provided.", "code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_manufacturer_type(self):
        '''
        Tests to see if the check_device function checks for an invalid
        manufacturer type.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = []

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The manufacturer is not a '\
                'string.", "code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_model_exists(self):
        '''
        Tests to see if the check_device function checks for a missing
        model.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = u'test'

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The model has not been '\
                'provided.", "code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_model_type(self):
        '''
        Tests to see if the check_device function checks for an invalid
        model type.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = u'test'
        body['device']['model'] = []

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The model is not a string.",'\
                ' "code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_os_version_exists(self):
        '''
        Tests to see if the check_device function checks for a missing
        os_version.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = u'test'
        body['device']['model'] = u'test'

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The os_version has not been '\
                'provided.", "code": "InvalidDevice", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_os_version_type(self):
        '''
        Tests to see if the check_device function checks for an invalid
        os_version type.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = u'test'
        body['device']['model'] = u'test'
        body['device']['os_version'] = []

        # Call the check_device function and expect an exception.
        try:
            check_device(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The os_version is not a '\
                'string.", "code": "InvalidDevice", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_device(self):
        '''
        Tests to see if the check_device with a positive example to make sure
        that None is returned.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = u'test'
        body['device']['model'] = u'test'
        body['device']['os_version'] = u'test'

        # Issue the request to the method being tested. The function should
        # not do anything.
        check_device(url, body)

    def test_check_no_auth_params(self):
        '''
        Tests to see if the check_auth_params function passes for a missing
        authParams parameter.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}

        # Issue the request to the method being tested. The function should not
        # do anything or raise any exceptions.
        check_auth_params(url, body)

    def test_check_auth_params_type(self):
        '''
        Tests to see if the check_auth_params function checks for an invalid
        authParams type.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['authParams'] = u'test'

        # Call the check_auth_params function and expect an exception.
        try:
            check_auth_params(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = u'{"error": {"message": "The authParams is not a '\
                'map.", "code": "InvalidAuthParams", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_auth_params_value_types(self):
        '''
        Tests to see if the check_auth_params function checks for an invalid
        authParams value types.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['authParams'] = {}
        body['authParams']['test'] = []

        # Call the check_auth_params function and expect an exception.
        try:
            check_auth_params(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "This authParams value is not a '\
                'string: test", "code": "InvalidAuthParams", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_auth_params(self):
        '''
        Tests to see if the check_auth_params with a positive example.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['authParams'] = {}
        body['authParams']['test'] = u'test'

        # Issue the request to the method being tested. The function should not
        # do anything or raise any exceptions.
        check_auth_params(url, body)

    def test_check_publisher_auth_params_exists(self):
        '''
        Tests to see if the check_publisher_auth_params function checks
        to ensure that authParams is provided.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}

        # Call the check_publisher_auth_params function and expect an
        # exception.
        try:
            check_publisher_auth_params(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The authParams has not been '\
                'provided.", "code": "InvalidAuthParams", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_publisher_auth_params_username_exists(self):
        '''
        Tests to see if the check_publisher_auth_params function checks
        to ensure that username is provided.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['authParams'] = {}

        # Call the check_publisher_auth_params function and expect an
        # exception.
        try:
            check_publisher_auth_params(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The username has not been '\
                'provided.", "code": "InvalidAuthParams", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_check_publisher_auth_params_password_exists(self):
        '''
        Tests to see if the check_publisher_auth_params function checks
        to ensure that password is provided.
        '''
        # Create seed data for the test.
        url = '/test/'
        body = {}
        body['authParams'] = {}
        body['authParams']['username'] = 'test'

        # Call the check_publisher_auth_params function and expect an
        # exception.
        try:
            check_publisher_auth_params(url, body)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The password has not been '\
                'provided.", "code": "InvalidAuthParams", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    @patch('publisher.model.uuid4')
    def test_auth(self, model_uuid4):
        '''
        Tests a positive case of the auth function.
        '''
        # Create a test request
        request = create_request('/test/')

        # Create the url parameters.
        api = 'paywallproxy'
        version = 'v1.0.0'
        format = 'json'
        product_code = 'product01'

        # Create the http headers.
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'PolarPaywallProxyAuthv1.0.0'
        request._environ = environment

        # Create the post body.
        body = {}
        body['device'] = {}
        body['device']['manufacturer'] = 'test'
        body['device']['model'] = 'test'
        body['device']['os_version'] = 'test'
        body['authParams'] = {}
        body['authParams']['username'] = 'user01'
        body['authParams']['password'] = 'test'
        request.body = unicode(dumps(body))

        # Create seed data for the test. Mock will override uuid4 in the call
        # to create_session_id to insert our testing values.
        session_id = 'test'

        # Set the return value of the mocked function to the session id being
        # tested.
        model_uuid4.return_value = session_id

        # Run the auth function.
        result = auth(request, api, version, format, product_code)

        # Check the result.
        self.assertTrue(isinstance(result, Response))
        expected = '{"sessionKey": "test", "products": ["product01", '\
                   '"product02"]}'
        self.assertEquals(result.output, expected)
        self.assertEquals(result.content_type, 'application/json')
        self.assertEquals(result.status, 200)


class TestModel(TestCase):
    '''
    Test the code in publisher/model.py. Unlike other test suites, this test
    code must contend with the fact that the model is a singleton.
    '''
    def tearDown(self):
        '''
        This function is called after every test to reset the state of the
        singleton in model.py.
        '''
        # Reset the shared data in the model class. When users is set to None
        # the model class copies it again from constants.py.
        model.users = None

    @patch('publisher.model.datetime')
    def create_expired_session(self, username, model_datetime):
        '''
        In order to test session key expiry, we need to create a session that
        has expired using the mock testing library to override datetime.now.
        Unfortunately, the code to check for outdated keys also uses
        datetime.now. So we have to mock the datetime.now function using a
        separate function.
        '''
        # Create a timestamp that is intentionally outdated so that the
        # update function expires the id.
        timestamp = datetime.now() - timedelta(hours=SESSION_TIMEOUT + 1)
        model_datetime.now.return_value = timestamp

        # Generate the session id and return it.
        return model().create_session_id(username)

    @patch('publisher.model.datetime')
    @patch('publisher.model.uuid4')
    def test_create_session_id(self, model_uuid4, model_datetime):
        '''
        Tests to see if a user's session id is created properly. There is no
        need to worry about threading as all the tests are run in a single
        thread, so locking isn't an issue.
        '''
        # Create seed data for the test. Mock will override uuid4 and datetime
        # in the call to create_session_id to insert our testing values.
        session_id = 'test'

        # Set the return value of the mocked function to the session id being
        # tested.
        model_uuid4.return_value = session_id

        # Create a fake timestamp and mock out the datetime class in the
        # called function so that a comparison can be made.
        timestamp = datetime.now()
        model_datetime.now.return_value = timestamp

        # Note that the test user has already been loaded in constants.py.
        username = 'user01'

        # Generate the session key. There is no need to worry about threading
        # as all the tests are run in a single thread, so locking isn't an
        # issue.
        result = model().create_session_id(username)

        # Make sure the session key was generated properly.
        self.assertEqual(result, session_id)

        # Introspect into the model class to make sure the session key was
        # generated properly.
        sessions = model.users[username]['session ids']
        session_timestamp = sessions[session_id]
        self.assertEqual(session_timestamp, timestamp)

    def test_update_session_id(self):
        '''
        Test to make sure that a generated session id expires. There is no
        need to worry about threading as all the tests are run in a single
        thread, so locking isn't an issue.
        '''
        # Create the expired session. user01 has already been created in
        # constants.py.
        username = 'user01'
        self.create_expired_session(username)

        # Expire the old key by calling update.
        model().update_session_ids(username)

        # Make sure a session id was removed.
        session_ids = model.users[username]['session ids']
        self.assertEqual(len(session_ids), 0)

    def test_authenticate_user_username(self):
        '''
        Test to make sure the authenticate_user function checks for a valid
        username.
        '''
        # Create seed data for the test.
        url = '/test/'
        username = 'invalid'
        password = 'invalid'
        product = 'invalid'

        # Try to authenticate the invalid user.
        try:
            model().authenticate_user(url, username, password, product)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonUnauthorized))
            content = u'{"error": {"message": "The credentials you have '\
                'provided are not valid.", "code": '\
                '"InvalidPaywallCredentials", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_authenticate_user_password(self):
        '''
        Test to make sure the authenticate_user function checks for a valid
        password.
        '''
        # Create seed data for the test.
        url = '/test/'
        username = 'user01'
        password = 'invalid'
        product = 'invalid'

        # Try to authenticate the invalid user.
        try:
            model().authenticate_user(url, username, password, product)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonUnauthorized))
            content = u'{"error": {"message": "The credentials you have '\
                'provided are not valid.", "code": '\
                '"InvalidPaywallCredentials", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_authenticate_user_valid(self):
        '''
        Test to make sure the authenticate_user function checks to make sure
        a user's account is valid.
        '''
        # Create seed data for the test.
        url = '/test/'
        username = 'user02'
        password = 'test'
        product = 'invalid'

        # Try to authenticate the invalid user.
        try:
            model().authenticate_user(url, username, password, product)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonUnauthorized))
            content = u'{"error": {"message": "Your account is not valid. '\
                'Please contact support.", "code": "AccountProblem", '\
                '"resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_authenticate_user_product(self):
        '''
        Test to make sure the authenticate_user function checks to make sure
        the product is valid.
        '''
        # Create seed data for the test.
        url = '/test/'
        username = 'user01'
        password = 'test'
        product = 'invalid'

        # Try to authenticate the invalid user.
        try:
            model().authenticate_user(url, username, password, product)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonNotFound))
            content = u'{"error": {"message": "The requested article could '\
                'not be found.", "code": "InvalidProduct", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    @patch('publisher.model.uuid4')
    def test_authenticate_user(self, model_uuid4):
        '''
        Test to make sure the authenticate_user function passes for a valid
        set of credentials. session ids are generated using uuid4 so we mock
        it out for testing.
        '''
        # Create seed data for the test.
        url = '/test/'
        username = 'user01'
        password = 'test'
        product = 'product01'
        products = ['product01', 'product02']

        # Create seed data for the test. Mock will override uuid4 in the call
        # to create_session_id to insert our testing values.
        session_id = 'test'

        # Set the return value of the mocked function to the session id being
        # tested.
        model_uuid4.return_value = session_id

        # Try to authenticate the valid user.
        (result_id, result_products) = model().authenticate_user(url, username,
                                                             password, product)

        # Make sure the session ids match.
        self.assertEqual(unicode(result_id), session_id)

        # Make sure the products match.
        self.assertEqual(result_products, products)

    def test_validate_session_not_found(self):
        '''
        Test to make sure the validate_session function checks to make sure
        that an invalid session token is handled.
        '''
        # Create seed data for the test.
        url = '/test/'
        session_id = 'invalid'

        # Try to validate the invalid session.
        try:
            model().validate_session(url, session_id)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonUnauthorized))
            content = u'{"error": {"message": "Your session has expired. '\
                'Please log back in.", "code": "SessionExpired", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_validate_session_account_problem(self):
        '''
        Test to make sure the validate_session function checks to make sure
        that an invalid account does not get validated.
        '''
        # Create seed data for the test.
        url = '/test/'

        # Create a valid session for the invalid test user.
        username = 'user02'
        session_id = model().create_session_id(username)

        # Try to validate the invalid session.
        try:
            model().validate_session(url, session_id)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonForbidden))
            content = u'{"error": {"message": "Your account is not valid. '\
                'Please contact support.", "code": "AccountProblem", '\
                '"resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_validate_session_expired_session(self):
        '''
        Test to make sure the validate_session function checks to make sure
        that expired sessions are not valid.
        '''
        # Create seed data for the test.
        url = '/test/'
        username = 'user01'
        session_id = self.create_expired_session(username)

        # Try to validate the invalid session.
        try:
            model().validate_session(url, session_id)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonUnauthorized))
            content = u'{"error": {"message": "Your session has expired. '\
                'Please log back in.", "code": "SessionExpired", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_validate_session(self):
        '''
        Test to make sure the validate_session function passes a valid
        session.
        '''
        # Create seed data for the test. user01 is defined in constants.py.
        url = '/test/'
        username = 'user01'
        session_id = model().create_session_id(username)
        products = ['product01', 'product02']

        # Run validation.
        result = model().validate_session(url, session_id)

        # Make sure the products match.
        self.assertEqual(result, products)


class TestValidate(TestCase):
    '''
    Test the code in publisher/validate.py.
    '''
    def test_get_session_id_exists(self):
        '''
        Tests to see if the get_session_id function checks for the existence
        of the "Authorization" header.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}

        # Call the get_session_id function and expect an exception.
        try:
            get_session_id(url, environment)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The authorization token has '\
                'not been provided.", "code": "InvalidAuthScheme", '\
                '"resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_get_session_id_value(self):
        '''
        Tests to see if the get_session_id function checks for the right
        authorization header.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}
        environment['HTTP_AUTHORIZATION'] = 'invalid'

        # Call the get_session_id function and expect an exception.
        try:
            get_session_id(url, environment)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The authorization token is '\
                'incorrect.", "code": "InvalidAuthScheme", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_get_session_id_value_exists(self):
        '''
        Tests to see if the get_session_id function checks for the provision
        of an actual session id.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}
        token = 'PolarPaywallProxySessionv1.0.0 session: '
        environment['HTTP_AUTHORIZATION'] = token

        # Call the get_session_id function and expect an exception.
        try:
            get_session_id(url, environment)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = '{"error": {"message": "The session id has not been '\
                'provided.", "code": "InvalidAuthScheme", "resource": '\
                '"/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_get_session_id(self):
        '''
        Tests to see if the get_session_id function passes a
        proper header.
        '''
        # Create seed data for the test.
        url = '/test/'
        environment = {}
        token = 'PolarPaywallProxySessionv1.0.0 session: test'
        environment['HTTP_AUTHORIZATION'] = token

        # Call the get_session_id function.
        result = get_session_id(url, environment)

        # Check for the right result.
        self.assertEqual(result, 'test')

    def test_validate_with_post_body(self):
        '''
        Test to see if the validate function raises an exception if the post
        body is provided.
        '''
        # Create seed data for the test. user01 is defined in constants.py.
        username = 'user01'
        session_id = model().create_session_id(username)

        # Create a test request
        request = create_request('/test/')

        # Create the url parameters.
        api = 'paywallproxy'
        version = 'v1.0.0'
        format = 'json'
        product_code = 'product01'

        # Create the http headers.
        environment = {}
        scheme = 'PolarPaywallProxySessionv1.0.0 session:' + session_id
        environment['HTTP_AUTHORIZATION'] = scheme
        request._environ = environment

        # Create the post body.
        request.body = 'test'

        # Call the validate function and expect an exception.
        try:
            validate(request, api, version, format, product_code)

        # Catch the exception and analyze it.
        except Exception, exception:
            self.assertTrue(isinstance(exception, JsonBadSyntax))
            content = u'{"error": {"message": "Invalid post body.", '\
                '"code": "InvalidFormat", "resource": "/test/"}}'
            self.assertEqual(unicode(exception), content)

        # If no exception was raised, raise an error.
        else:
            raise AssertionError('No exception raised.')

    def test_validate(self):
        '''
        Tests a positive case of the validate function.
        '''
        # Create seed data for the test. user01 is defined in constants.py.
        username = 'user01'
        session_id = model().create_session_id(username)

        # Create a test request
        request = create_request('/test/')

        # Create the url parameters.
        api = 'paywallproxy'
        version = 'v1.0.0'
        format = 'json'
        product_code = 'product01'

        # Create the http headers.
        environment = {}
        scheme = 'PolarPaywallProxySessionv1.0.0 session:' + session_id
        environment['HTTP_AUTHORIZATION'] = scheme
        request._environ = environment

        # Create the post body.
        request.body = ''

        # Run the validate function.
        result = validate(request, api, version, format, product_code)

        # Check the result.
        self.assertTrue(isinstance(result, Response))
        expected = '{"sessionKey": "%s", "products": ["product01", '\
                   '"product02"]}' % session_id
        self.assertEquals(result.output, expected)
        self.assertEquals(result.content_type, 'application/json')
        self.assertEquals(result.status, 200)


# If the script is called directly, then the global variable __name__ will
# be set to main.
if __name__ == '__main__':
    # Run unit tests if the script is called directly.
    main()
