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

# Used to process the http request.
from itty import post, Response

# Used to validate the values passed into the base url and raise errors.
from publisher.utils import check_base_url, raise_error

# Used to decode and encode post bodies that contain json encoded data.
from simplejson import loads, dumps

# Used to authenticate a user to the data model.
from publisher.model import model

# Used to match URLs.
from constants import API, VERSION, FORMAT, PRODUCT_CODE


def check_authorization_header(url, environment):
    '''
    Checks for the existence of the auth-scheme token. Note that the validate 
    API entry point has a different auth-scheme token.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidAuthScheme:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidAuthScheme
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No
    '''
    # All of the errors in this function share a common code and status.
    code = 'InvalidAuthScheme'
    status = 400

    # Make sure the token is provided.
    if 'HTTP_AUTHORIZATION' not in environment:
        message = 'The authorization token has not been provided.'
        raise_error(url, code, message, status)

    # Make sure the token is provided. The auth-scheme token isn't important
    # for this part of the API, but it is for others.
    if environment['HTTP_AUTHORIZATION'] != 'PolarPaywallProxyAuthv1.0.0':
        message = 'The authorization token is incorrect.'
        raise_error(url, code, message, status)


def decode_body(url, body):
    '''
    This function checks the validity of the body parameter. It takes the
    request body and returns python objects by decoding the body using
    json.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidFormat:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidFormat
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No
    '''
    # Try to decode the json body. If the body cannot be decoded, raise an
    # error.
    try:
        json_body = loads(body)

    except ValueError, exception:
        # If a ValueError occurred, the json decoder could not decode the
        # body of the request. We need to return an error to the client.
        # Note that we do not return the body of the request as it could
        # contain access credentials.
        code = 'InvalidFormat'
        message = 'Could not decode post body. json is expected.'
        status = 400
        raise_error(url, code, message, status)

    # Make sure the body has one or two parameters and no more.
    if len(json_body) < 1 or len(json_body) > 2:
        code = 'InvalidFormat'
        message = 'Post body has an invalid number of parameters.'
        status = 400
        raise_error(url, code, message, status)

    # Return the decoded body.
    return json_body


def check_device(url, body):
    '''
    This function checks the validity of the device parameter. It takes the
    decoded json body of the request and raises an error if a problem is
    found.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidDevice:

            Returned when the request does not specify the device parameters
            properly.

            Code: InvalidDevice
            Message: Varies with the error.
            HTTP Error Code: 400
            Required: No
    '''
    # All of the errors in this function share a common code and status.
    code = 'InvalidDevice'
    status = 400

    # Validate that the device is provided as a parameter to the body. This
    # sample publisher does not store the device, but a production system
    # could store these values in order to perform analysis on the types of
    # devices that access products.
    if 'device' not in body:
        message = 'The device has not been provided.'
        raise_error(url, code, message, status)

    # Make sure the device is a dictionary.
    if isinstance(body['device'], dict) == False:
        message = 'The device is not a map.'
        raise_error(url, code, message, status)

    # Check to make sure that the manufacturer of the device has been
    # provided.
    if 'manufacturer' not in body['device']:
        message = 'The manufacturer has not been provided.'
        raise_error(url, code, message, status)

    # Check to make sure the manufacturer is of the right type.
    if isinstance(body['device']['manufacturer'], unicode) == False:
        message = 'The manufacturer is not a string.'
        raise_error(url, code, message, status)

    # Check to make sure that the model of the device has been provided.
    if 'model' not in body['device']:
        message = 'The model has not been provided.'
        raise_error(url, code, message, status)

    # Check to make sure the model is of the right type.
    if isinstance(body['device']['model'], unicode) == False:
        message = 'The model is not a string.'
        raise_error(url, code, message, status)

    # Check to make sure that the os_version of the device has been provided.
    if 'os_version' not in body['device']:
        message = 'The os_version has not been provided.'
        raise_error(url, code, message, status)

    # Check to make sure the os_version is of the right type.
    if isinstance(body['device']['os_version'], unicode) == False:
        message = 'The os_version is not a string.'
        raise_error(url, code, message, status)


def check_auth_params(url, body):
    '''
    This function checks the validity of the authParams parameter as per the
    API. It takes the decoded json body of the request and raises an exception
    if a problem is found.

    The difference between check_auth_params and check_publisher_auth_params
    is that check_auth_params enforces validity to the API. In contrast,
    check_publisher_auth_params enforces validity as to this implementation.
    It checks specifically for the existence of the "username" and "password"
    fields.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidAuthParams:

            Returned when the request does not specify the authParams parameter
            properly.

            Code: InvalidAuthParams
            Message: Varies with the error.
            HTTP Error Code: 400
            Required: No
    '''
    # All of the errors in this function share a common code and status.
    code = 'InvalidAuthParams'
    status = 400

    # Note that not having an authParams key is valid.
    if 'authParams' not in body:
        return

    # When authParams is provided, the type must be a dictionary.
    if isinstance(body['authParams'], dict) == False:
        message = 'The authParams is not a map.'
        raise_error(url, code, message, status)

    # Make sure that all the values in the dictionary are strings.
    for key in body['authParams']:
        # If the value isn't a string, raise an error.
        if isinstance(body['authParams'][key], unicode) == False:
            message = 'This authParams value is not a string: ' + unicode(key)
            raise_error(url, code, message, status)


def check_publisher_auth_params(url, body):
    '''
    This function checks for the existence of the authParams dictionary and
    the exiistence of the "username" and "password" keys in the authParams
    dictionary.

    The difference between check_auth_params and check_publisher_auth_params
    is that check_auth_params enforces validity to the API. In contrast,
    check_publisher_auth_params enforces validity as to this implementation.
    It checks specifically for the existence of the "username" and "password"
    fields.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidAuthParams:

            Returned when the request does not specify the authParams parameter
            properly.

            Code: InvalidAuthParams
            Message: Varies with the error.
            HTTP Error Code: 400
            Required: No
    '''
    # All of the errors in this function share a common code and status.
    code = 'InvalidAuthParams'
    status = 400

    # In this implementation, authParams is required. The check for authParams
    # being a dictionary has already been carried out by check_auth_params.
    if 'authParams' not in body:
        message = 'The authParams has not been provided.'
        raise_error(url, code, message, status)

    # Make sure username is provided. The check_auth_params has already
    # checked the type of the username.
    if 'username' not in body['authParams']:
        message = 'The username has not been provided.'
        raise_error(url, code, message, status)

    # Make sure password is provided. The check_auth_params has already
    # checked the type of the password.
    if 'password' not in body['authParams']:
        message = 'The password has not been provided.'
        raise_error(url, code, message, status)


@post(API + VERSION + FORMAT + r'/auth' + PRODUCT_CODE)
def auth(request, api, version, format, product_code):
    '''
    Overview:

        Attempt an authentication for a product using supplied credentials. If
        successful, a session key is obtained that can be used for requests to
        protected resources/content. The base URL scheme for this entry point
        is:

            /:api/:version/:format/auth/:productcode

        In this particular case, the api is "paywallproxy" and the version is
        v1.0.0. Currently, the only supported format is "json". The URL for
        this entry point therefore looks like:

            /paywallproxy/v1.0.0/json/auth/:productcode

        If the product cannot be found, an "InvalidProduct" error should be
        returned. This error will be returned to the client. A full list of
        errors that this entry point returns is available below. Client errors
        are proxied to the client. Server errors remain on Polar's server.

        An auth-scheme token is expected when a call is made to this API end
        point. It must conform to RFC 2617 specifications. The authorization
        header has the following form:

            Authorization: PolarPaywallProxyAuthv1.0.0

    Parameters:

        There are two sets of parameters that this API entry point requires.
        The first set consists of the product code, which is specified in the
        URL and the post body, which contains formatted json. Technical details
        will follow after a description of the parameters and an example will
        follow after that.

        The product code is part of the URL. It is a publisher-assigned unique
        identifier for this product. The product code is required.

        The post body is a json map with two keys. The first key is "device",
        which is a json map describing the device requesting authorization.
        This key is required. The second key is "authParams", which is
        optional.

        The "device" map contains three keys. "manufacturer" is the full name
        of the device manufacturer. "model" is the device's model number and
        name. "os_version" is a string that describes the version of the
        device's operating system.

        The contents of the "authParams" map will vary based on the settings
        on the Polar server. The keys of the map is the name of the parameter
        set on the server. The values of the map is the value entered by the
        user.

        Details regarding the various parameters are described below.

        Product Code:

            A publisher-assigned unique identifier for this product.

            Availability: >= v1.0.0
            Required: Yes
            Location: URL
            Format: URL
            Type: String
            Max Length: 256

        device:

            A json map describing the device requesting authorization.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: json map
            Max Length: N/A

        manufacturer:

            The full name of the device manufacturer. Contained in the "device"
            map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        model:

            The device's model number and name. Contained in the "device" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        os_version:

            The version of the device's operating system. Contained in the
            "device" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        authParams:

            A map of the authentication parameters and their values.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: map
            Max Length: N/A

        authParams key:

            The name of the authentication parameter. Contained in the
            "authParams" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        authParams value:

            The user entered value of the authentication parameter. Contained
            in the "authParams" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 512

    Response:

        The following parameters are returned by this API end point. The
        resposne is json encoded. It has two keys; "sessionKey" and "products".
        "sessionKey" is a key that allows the client to re-authenticate without
        the supplied authentication parameters. "products" is a list of product
        identifiers that the user has access to.

        sessionKey:

            A key that allows the client to re-authenticate without the
            supplied authentication parameters.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 512

        products:

            A list of product identifiers that the user has access to.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: list
            Max Length: N/A

        product:

            A publisher-assigned unique identifier for this product that the
            user has access to. Contained in the "products" list.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

    Example:

        Example Request:

            POST /paywallproxy/v1.0.0/json/auth/gold-level HTTP/1.1
            Authorization: PolarPaywallAuthv1.0.0 123:x
            Content-Type: application/json

            {
                "device": {
                    "manufacturer": "Phake Phones Inc.",
                    "model": "90",
                    "os_version": "1.1.1"
                },

                "authParams": {
                    "username": "polar",
                    "password": "mobile"
                }
            }

        Example Response:

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "sessionKey": "9c4a51cc08d1879570c",

                "products": [
                    "gold-level",
                    "silver-level"
                ]
            }

    Client Errors:

        This section documents errors that are returned to the client. Note
        that the publisher is free to modify the content of these messages as
        they please.

        InvalidPaywallCredentials:

            Thrown when the authentication parameters are invalid.

            Code: InvalidPaywallCredentials
            Message: Varies with the error.
            HTTP Error Code: 401
            Required: Yes

        AccountProblem:

            There is a problem with the user's account. The user is
            prompted to contact technical support.

            Code: InvalidPaywallCredentials
            Message: Your account is not valid. Please contact support.
            HTTP Error Code: 403
            Required: Yes

        InvalidProduct:

            Thrown when the product code indicated is invalid.

            Code: InvalidProduct
            Message: The requested article could not be found.
            HTTP Error Code: 404
            Required: Yes

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        Some of the following errors are marked optional. They are included in
        this example for completeness and testing purposes. Implementing them
        makes testing the connection between Polar's server and the publishers
        server easier.

        InvalidAPI:

            Returned when the publisher does not recognize the requested api.

            Code: InvalidAPI
            Message: The requested api is not implemented: <api>
            HTTP Error Code: 404
            Required: No

        InvalidVersion:

            Returned when the publisher does not recognize the requested
            version.

            Code: InvalidVersion
            Message: The requested version is not implemented: <version>
            HTTP Error Code: 404
            Required: No

        InvalidFormat:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidFormat
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No

        InvalidDevice:

            Returned when the request does not specify the device parameters
            properly.

            Code: InvalidDevice
            Message: Varies with the error.
            HTTP Error Code: 400
            Required: No

        InvalidAuthParams:

            Returned when the request does not specify the authParams parameter
            properly.

            Code: InvalidAuthParams
            Message: Varies with the error.
            HTTP Error Code: 400
            Required: No

        InvalidAuthScheme:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidAuthScheme
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No
    '''
    # Store the full URL string so that it can be used to report errors.
    url = request.path

    # Validate the base URL.
    check_base_url(url, api, version, format)

    # Check for the auth-scheme token.
    check_authorization_header(url, request._environ)

    # Decode the json body from the post body.
    body = decode_body(url, request.body)

    # Check to make sure the device parameter is valid.
    check_device(url, body)

    # Check to make sure the authParams parameter correct with respect to the
    # API.
    check_auth_params(url, body)

    # Check to make sure that the parameters that this implementation expects
    # are there.
    check_publisher_auth_params(url, body)

    # Extract the username and password from the body.
    username = body['authParams']['username']
    password = body['authParams']['password']

    # Authenticate the user to get the session id and the products.
    data_model = model()
    (session_id, products) = data_model.authenticate_user(url, username,
                                                 password, product_code)

    # Create the resulting response.
    result = {}
    result['sessionKey'] = session_id
    result['products'] = products

    # Encode the result as a json object.
    content = dumps(result)

    # Extract the authentication token.
    authorization = request._environ['HTTP_AUTHORIZATION']
    headers = [('Authorization', authorization)]

    # Create and send a response.
    status = 200
    content_type = 'application/json'
    return Response(content, headers, status, content_type)
