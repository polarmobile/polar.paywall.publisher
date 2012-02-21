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
from mock import patch, MagicMock

# Used to generate fake http requests.
from itty import Request, Response

# Used to test error handling code.
from publisher.utils import report_error, check_base_url

# Used to test http error handling code.
from publisher.errors import handle_500, handle_404


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
    def test_report_error(self):
        '''
        Tests generation of an error report.
        '''
        # Generate the example.
        code = 'TestError'
        message = 'This is a test error.'
        request = create_request('/test/')
        status = 200

        # Call report_error and get the result.
        result = report_error(code, message, request, status)

        # Check the result's type.
        self.assertIsInstance(result, Response)

        # Check the result's content.
        content = '{"error": {"message": "This is a test error.", '\
            '"code": "TestError", "resource": "/test/"}}'
        self.assertEqual(result.output, content)

        # Check the result's content type.
        self.assertEqual(result.content_type, 'application/json')

        # Check the result's status.
        self.assertEqual(result.status, 200)

    def test_check_base_url_api(self):
        '''
        Tests base url checking on the api parameter.
        '''
        # Generate the example. In this case the only invalid parameter is the
        # api.
        request = create_request('/test/')
        api = 'test'
        version = 'v1.0.0'
        format = 'json'

        # Call the check_base_url function to get the result.
        result = check_base_url(request, api, version, format)

        # Check the result's type.
        self.assertIsInstance(result, Response)

        # Check the result's content.
        content = '{"error": {"message": "The requested api is not '\
            'implemented: test", "code": "InvalidAPI", "resource": "/test/"}}'
        self.assertEqual(result.output, content)

        # Check the result's content type.
        self.assertEqual(result.content_type, 'application/json')

        # Check the result's status.
        self.assertEqual(result.status, 404)

    def test_check_base_url_version(self):
        '''
        Tests base url checking on the version parameter.
        '''
        # Generate the example. In this case the only invalid parameter is the
        # version.
        request = create_request('/test/')
        api = 'paywallproxy'
        version = 'test'
        format = 'json'

        # Call the check_base_url function to get the result.
        result = check_base_url(request, api, version, format)

        # Check the result's type.
        self.assertIsInstance(result, Response)

        # Check the result's content.
        content = '{"error": {"message": "The requested version is not '\
            'implemented: test", "code": "InvalidVersion", "resource": '\
            '"/test/"}}'
        self.assertEqual(result.output, content)

        # Check the result's content type.
        self.assertEqual(result.content_type, 'application/json')

        # Check the result's status.
        self.assertEqual(result.status, 404)

    def test_check_base_url_format(self):
        '''
        Tests base url checking on the format parameter.
        '''
        # Generate the example. In this case the only invalid parameter is the
        # format.
        request = create_request('/test/')
        api = 'paywallproxy'
        version = 'v1.0.0'
        format = 'test'

        # Call the check_base_url function to get the result.
        result = check_base_url(request, api, version, format)

        # Check the result's type.
        self.assertIsInstance(result, Response)

        # Check the result's content.
        content = '{"error": {"message": "The requested format is not '\
            'implemented: test", "code": "InvalidFormat", "resource": '\
            '"/test/"}}'
        self.assertEqual(result.output, content)

        # Check the result's content type.
        self.assertEqual(result.content_type, 'application/json')

        # Check the result's status.
        self.assertEqual(result.status, 404)


class TestErrors(TestCase):
    '''
    Test the code in publisher/errors.py.
    '''
    def test_handle_500(self):
        '''
        Tests handling of a 500 error.
        '''
        # Create the request object.
        request = create_request('/test/')

        # Issue the request to the method being tested.
        result = handle_500(request, exception=None)

        print result

        # Check the result's type.
        self.assertIsInstance(result, str)

        # Check the result's content.
        content = '{"error": {"message": "An internal server error '\
            'occurred.", "code": "InternalError", "resource": "/test/"}}'
        self.assertEqual(result, content)

    def test_handle_404(self):
        '''
        Tests handling of a 404 error.
        '''
        # Create the request object.
        request = create_request('/test/')

        # Issue the request to the method being tested.
        result = handle_404(request, exception=None)

        # Check the result's type.
        self.assertIsInstance(result, str)

        # Check the result's content.
        content = '{"error": {"message": "No handler could be found for the '\
            'requested resource.", "code": "NoHandler", "resource": "/test/"}}'
        self.assertEqual(result, content)


class TestAuth(TestCase):
    '''
    Test the code in publisher/auth.py.
    '''
    pass


# If the script is called directly, then the global variable __name__ will
# be set to main.
if __name__ == '__main__':
    # Run unit tests if the script is called directly.
    main()
