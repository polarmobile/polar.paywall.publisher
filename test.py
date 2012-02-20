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
from itty import Request

# Used to test error handling code.
from publisher.utils import report_error

# Used to test http error handling code.
from publisher.errors import handle_500
#from publisher.errors import handle_404


def create_request(http_path):
    '''
    A helper function used to create fake request objects for testing.
    '''
    # WSGI and itty operate like CGI. They have a dictionary of environment
    # variables that specify the paraters of the request. For testing, all we
    # care to specify is the PATH_INFO variable, which is the URL that the
    # request is processed with.
    environ = {}
    environ['PATH_INFO'] = http_path

    # Create the request object. start_response is a function pointer to an
    # internal function that itty uses to send a request. For the purposes of
    # testing, it can be ignored.
    result = Request(environ, start_response = None)

    # Return the result.
    return result


class TestErrors(TestCase):
    '''
    Test the code in errors.py.
    '''
    def test_report_error(self):
        '''
        Tests generation of an error using positive example.
        '''
        # Generate the example.
        code = 'TestError'
        message = 'This is a test error.'
        resource = '/test'

        # Call report_error and get the result.
        result = report_error(code, message, resource)

        # Check the result's type.
        self.assertIsInstance(result, str)

        # Check the result's content.
        expected = '{"error": {"message": "This is a test error.", '\
            '"code": "TestError", "resource": "/test"}}'
        self.assertEqual(result, expected)

    def test_error_500(self):
        '''
        Tests handling of a 500 error using a single positive example.
        '''
        # Create the request object.
        request = create_request('/test')

        # Issue the request to the method being tested.
        result = handle_500(request, exception = None)

        # Check the result's content.
        expected = '{"error": {"message": "An internal server error '\
            'occurred.", "code": "InternalError", "resource": "/test/"}}'
        self.assertEqual(result, expected)

# If the script is called directly, then the global variable __name__ will
# be set to main.
if __name__ == '__main__':
    # Run unit tests if the script is called directly.
    main()
