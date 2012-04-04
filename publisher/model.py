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

# Used to perform a deep copy of the users dictionary to ensure that no
# references are copied.
from copy import deepcopy


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
    it is saved. The last key is "session ids", whose value is a dictionary
    with session id keys and timestamp values. An example follows:

    users = {
        "username": {
            "valid": True,
            "products": ["test1","test2"],
            "password": "test"
            "session ids": {<session id>: (product, <time stamp>)}
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
            # Check to see if the users object is un-initialized. It will be
            # if this is the first time an instance of model is created.
            if model.users == None:
                # Initialize the shared testing data by copying the dictionary
                # in the constants file. deepcopy is used to ensure that python
                # does not copy any references when it makes a copy of the
                # users dictionary (from constants.py). Making a copy of the
                # users dictionary makes testing easier.
                model.users = deepcopy(users)

        finally:
            self.lock.release()

    def create_session_id(self, username, product):
        '''
        Creates a session key for the given user. Note that model.users is
        assumed to be locked before this function is called. The user's
        key and a timestamp are added to the model.users['session ids']
        list.

        This function takes the username and product as a parameter and returns
        the generated session key as a result.
        '''
        # To generate session ids, this sample uses uuid4, which generates
        # a random unique identifier. Note that this method is not secure.
        # Please consult the cryptographic libraries packaged in your tool
        # set for proper session id generation.
        session_id = unicode(uuid4())

        # Create a timestamp for the session id. This timestamp will be
        # checked later to make sure that the id is still valid.
        timestamp = datetime.now()

        # Insert the session id into shared memory. Note that shared sessions
        # is a map of session ids to timestamps.
        sessions = model.users[username]['session ids']
        sessions[session_id] = (product, timestamp)

        # Return the session id so that it can be reported back to the caller.
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
        # Make sure the user is known.
        assert username in model.users

        # Create a timedelta object to compare against the difference between
        # the stored timestamp and now.
        expired_limit = timedelta(hours=SESSION_TIMEOUT)

        # Loop through all the session ids and store only valid ids. We store
        # only valid ids because we can't delete from the sessions dictionary
        # while iterating over it.
        valid_ids = {}
        sessions = model.users[username]['session ids']
        for session_id in sessions:
            # If the key has not expired, store it to indicate that it is
            # valid.
            product, timestamp = sessions[session_id]
            if (datetime.now() - timestamp) < expired_limit:
                valid_ids[session_id] = (product, timestamp)

        # Swap the current session ids for the new set of valid is.
        model.users[username]['session ids'] = valid_ids

    def authenticate_user(self, url, username, password, product):
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
                HTTP Error Code: 401
                Required: Yes

            AccountProblem:

                There is a problem with the user's account. The user is
                prompted to contact technical support.

                Code: AccountProblem
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
        self.lock.acquire()
        try:
            # Most of the errors in this function share a common code and
            # status.
            code = 'InvalidPaywallCredentials'
            status = 401

            # Check to see if the username is known.
            if username not in model.users:
                message = 'The credentials you have provided are not valid.'
                raise_error(url, code, message, status)

            # Check to see if the password is valid.
            if model.users[username]['password'] != password:
                message = 'The credentials you have provided are not valid.'
                raise_error(url, code, message, status)

            # Check to see if the user is valid. The check for a valid account
            # should come after the check for the password as the password
            # validates the user's identity.
            if not model.users[username]['valid']:
                code = 'AccountProblem'
                message = 'Your account is not valid. Please contact support.'
                raise_error(url, code, message, status)

            # Check to see if the user has access to the requested product.
            if product not in model.users[username]['products']:
                code = 'InvalidProduct'
                message = 'The requested article could not be found.'
                status = 404
                raise_error(url, code, message, status)

            # Update all valid session keys. While this call is not required
            # at this time, issuing it helps keep the database of session ids
            # small; particularly since the user has likely not been accessing
            # content recently as they are logging in. Calling update now will
            # hopefully free up many keys, reducing the memory footprint of
            # the server.
            self.update_session_ids(username)

            # Return the session id and products.
            session_id = self.create_session_id(username, product)
            products = model.users[username]['products']
            return (session_id, products)

        finally:
            self.lock.release()

    def validate_session(self, url, session_id, product):
        '''
        This function takes a session id, attempts to find the users that
        it is associated with. If it finds a user, it first updates the
        session tokens and then checks to make sure that the session key
        is still valid. It then returns the list of products that the user
        has access to. If it finds no user, it reports that the session key
        has been expired.

        Client Errors:

            This section documents errors that are returned to the client. Note
            that the publisher is free to modify the content of these messages
            as they please.

            SessionExpired:

                Thrown when the session id cannot be validated.

                Code: SessionExpired
                Message: Your session has expired. Please log back in.
                HTTP Error Code: 401
                Required: Yes

            AccountProblem:

                There is a problem with the user's account. The user is
                prompted to contact technical support.

                Code: AccountProblem
                Message: Your account is not valid. Please contact support.
                HTTP Error Code: 403
                Required: Yes
        '''
        self.lock.acquire()
        try:
            # Most of the errors in this function share a common code and
            # status.
            code = 'SessionExpired'
            status = 401
            message = 'Your session has expired. Please log back in.'

            # Loop over all of the users and check for the valid session id.
            for username in model.users:
                # If the session id does not belong to this user, keep
                # searching.
                if session_id not in model.users[username]['session ids']:
                    continue

                # Check to see if the user is valid. The check for a valid
                # account should come after the check for the session id as
                # the password validates the user's identity.
                if not model.users[username]['valid']:
                    code = 'AccountProblem'
                    message = ('Your account is not valid. Please contact '
                               'support.')
                    status = 403
                    raise_error(url, code, message, status)

                # Check to make sure the product is valid.
                if product not in model.users[username]['products']:
                    code = 'InvalidProduct'
                    message = 'The requested article could not be found.'
                    status = 404
                    raise_error(url, code, message, status)

                # Update the list of valid session ids; the session may have
                # expired since the last validation.
                self.update_session_ids(username)

                # Check to see if the session id is valid; it may have been
                # invalidated by the call to update_session_ids.
                if session_id not in model.users[username]['session ids']:
                    message = 'Your session has expired. Please log back in.'
                    raise_error(url, code, message, status)

                # Check to see if the session key is registered against the
                # right product. The only way this can happen during normal
                # operation is if a product that the user has authenticated
                # has been deleted.
                session = model.users[username]['session ids'][session_id]
                stored_product, timestamp = session
                if product != stored_product:
                    # Their session has expired.
                    raise_error(url, code, message, status)

                # Return the user's products, which indicate a successful
                # validation.
                products = model.users[username]['products']
                return products

            # If nothing has been returned at this point, raise an error.
            # We can only assume that their session key has expired.
            raise_error(url, code, message, status)

        finally:
            self.lock.release()
