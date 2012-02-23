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

# Used to control access to the model's shared data.
from threading import RLock

# Used to raise authentication errors.
from publisher.utils import raise_error

# Used to generate random session keys.
from uuid import uuid4

# Used to track the persistence of session keys.
from datetime import datetime, timedelta

# Used to initialize the model.users dictionary and define the timeout for
# session keys.
from constants import SESSION_TIMEOUT, users


class model:
    '''
    In order to simplify the design of this sample, the state of the system is
    stored in memory, as opposed to a database. The server is then run in a
    single process with multiple threads. This model class contains a singleton
    that stores the state of the server.

    The model is structured as follows. The model contains a dictionary called
    users that is keyed against the usersnames of the valid users. Each value
    in this dictionary is a dictionary containing a number of keys.

    The first key is "valid". The value of this key is a boolean indicating if
    a user's account is valid or not. The second key is "products", which
    contains a list of product codes that the user has access to. The next key
    is "password", which contains the user's password. Note that in a
    production system, the user's password should be salted and hashed before
    it is saved. The last key is "session ids", whose values are a list of
    tuples containing the session key and a timestamp. An example follows:

    users = {
        "username": {
            "valid": True,
            "products": ["test1","test2"],
            "password": "test"
            "session ids": [("abcde", 123456)]
            }
        }
    '''
    # The object that contains the shared memory. Note how it is associated
    # to the class and not an instance of the class. It is accessed using
    # model.users. When an instance of this class is created, it checks to
    # see if this is the first time the model singleton has been created
    # by looking for users = None.
    users = None

    def __init__(self):
        '''
        The constructor for the class. Note that self is a reference to the
        class' instance. It is like the "this" pointer in C++.
        '''
        # If this is the first instance of the model class, we need to populate
        # the users object with test data. We can check for the first instance
        # by looking to see if users is None. Since multiple threads access the
        # data, we need to block access to the shared object using a lock
        # before modifying the data.
        self.lock = RLock()

        # The try finally block is like an exception handler, except that it
        # ensures that the code in the finally block is always run. It is
        # useful in this case because we want to ensure that we do not
        # permanently lock other threads if this thread fails.
        self.lock.acquire()
        try:
            # Check to see if the users object is un-initialized.
            if model.users == None:
                # Initialize the shared testing data by copying the dictionary
                # in the constants file. A deep copy is used to ensure that all
                # references are resolved.
                global users
                mode.users = users.deepcopy()
        finally:
            self.lock.release()

    def create_session_id(self, username):
        '''
        Creates a session key for the given user. Note that model.users is
        assumed to be locked before this function is called. The user's
        key and a timestamp are added to the model.users['session ids']
        list.

        This function takes the username as a parameter and returns the
        generated session key as a result.
        '''
        # Create the new session id.
        session_id = uuid4()

        # Create a timestamp for the session id.
        timestamp = datetime.now()

        # Insert the session id and the timestamp as a python tuple.
        model.users['user01']['session ids'].append((session_id, timestamp))

        # Return the session id.
        return session_id

    def update_session_ids(self, username):
        '''
        Loops through all of the session ids for a given user and checks to
        see if session keys have been expired. This function should be
        called when a user has been authenticated or when a product has been
        validated.

        Allowing a user to have multiple valid session keys lets them log into
        multiple devices without logging them out of their previous device.
        '''
        # Make sure the user is valid.
        assert username in model.users

        # Create a timedelta object to compare against the difference between
        # the stored timestamp and now.
        expired_limit = timedelta(hours=SESSION_TIMEOUT)

        # Loop through all the valid session ids and store keys that are still
        # valid.
        valid_keys = []
        for session in model.users[username]['session ids']:
            # Unpack the session id and the timestamp.
            session_id, timestamp = session

            # Check to see if the session has expired. If it hasn't then add
            # it to the list of valid keys.
            if (datetime.now() - timestamp) < expired_limit:
                valid_keys.append(session_id, timestamp)

        # Update the list of valid session ids.
        model.users[username]['session ids'] = valid_keys

    def authenticate_user(self, username, password, product):
        '''
        This function first checks to see if a user is valid. If it is, it
        will then attempt to authenticate the user with the password. If
        the password attempt succeeds, this function generates and inserts
        a new session key and returns it.

        If any failures occur as a result of authenticating the user, an
        exception will be thrown. The exceptions are detailed below.

        Client Errors:

            This section documents errors that are returned to the client. Note
            that the publisher is free to modify the content of these messages
            as they please.

            InvalidPaywallCredentials:

                Thrown when the authentication parameters are invalid.

                Code: InvalidPaywallCredentials
                Message: Varies with the error.
                HTTP Error Code: 403
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
        '''
        # Lock access to the shared memory.
        self.lock.acquire()
        try:
            # Most of the errors in this function share a common code and
            # status.
            code = 'InvalidPaywallCredentials'
            status = 403

            # Check to see if the username is known.
            if username not in model.users:
                message = 'The credentials you have provided are not valid.'
                raise_error(url, code, message, status)

            # Check to see if the user is valid.
            if model.users[username]['valid'] == False:
                code = 'AccountProblem'
                message = 'Your account is not valid. Please contact support.'
                status = 403
                raise_error(url, code, message, status)

            # Check to see if the password is valid.
            if model.users[username]['password'] != password:
                message = 'The credentials you have provided are not valid.'
                raise_error(url, code, message, status)

            # Check to see if the user has access to the requested product.
            if product not in model.users[username]['products']:
                code = 'InvalidProduct'
                message = 'The requested article could not be found.'
                status = 404
                raise_error(url, code, message, status)

            # Update all valid session keys.
            self.update_session_ids(username)

            # Create a new session key.
            session_id = self.create_session_id(username)

            # Return the session id.
            return session_id

        finally:
            self.lock.release()
