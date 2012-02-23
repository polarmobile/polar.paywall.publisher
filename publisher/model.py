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
    # by looking for users = None. If it is, the class uses the create_users
    # function to initialize the object.
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
                # Initialize the shared testing data.
                self.create_users()
        finally:
            self.lock.release()

    def create_users(self):
        '''
        When the first instance of this singleton is created, the model.users
        object will be None. It has to be populated with data for testing in
        order to be functional. This function populates the users object.

        Note that since there will be many threads accessing the shared data
        in users, this function must block before allowing other threads to
        access the data.

        See the definition of the class above for an example of how the users
        dictionary should be structured.
        '''
        
        # Add a test user.
        model.user['user01'] = {}
        model.user['user01']['valid'] = True
        model.user['user01']['products'] = ['product01','product02']
        model.user['user01']['password'] = 'test'

        # Session ids are generated by the model class. We need to initialize
        # the "session ids" value to an empty list in order to allow this
        # generation.
        model.user['user01']['session ids'] = []

    def authenticate_user(self, username, password):
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

                Code: InvalidProduct
                Message: The requested article could not be found.
                HTTP Error Code: 404
                Required: Yes
        '''
        # Lock access to the shared memory.
        self.lock.acquire()
        try:
            # Check to see if the user is valid.

        finally:
            self.lock.release()
