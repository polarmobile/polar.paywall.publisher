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
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

def create_error(http_headers, code, message, resource):
	'''
	For Client Errors (400-series) and Server Errors (500-series), an error
	report should be returned. Note that some errors will be returned to the
	client as printable text. It is up to the publisher to ensure the
	quality of the content of these messages.

	Error are encoded using json. The body of the error is a json dictionary
	with a key called "error". The "error" value is another dictionary with
	the following parameters.

	 * "id"
	 * "code"
	 * "message"
	 * "resource"

	"id" is generated using the create_error_id function below.

	"code" is a string error code that both Polar's server and the client
	can use to easily triage an error. Each entry point in this project
	contains documentation on the error codes it may return.

	"message" is a description of the error. Note that this message should
	never contain a users password.

	"resource" is the resource URI the request was attempting to access.
	'''

def create_error_id(headers):
	'''
	"id" is an attribute that is claculated from the other values in the
	message. To calculate the "id", you need to generate an SHA1 hash of
	the following values in order:

	 1. HTTP Header Values
	  * Note that only the headers that start with HTTP- will be used.
	 1. Date and Time
	 1. Resource URI
	 1. Originating IP Address

	The date and time fields iso formatted values in UTC. Specifically,
	in the format YYYY-MM-DDTHH:MM:SS.mmmmmm. The following is an example
	of a date time value:

	    "2012-02-10T19:06:31.996996"

	The originating IP address is the contents of the REMOTE\_ADDR field
	in the HTTP header.

	This function takes a hash table of HTTP headers and generates the
	appropriate error code as a string.
	'''
