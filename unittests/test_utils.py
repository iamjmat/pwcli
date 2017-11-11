#!/usr/bin/env python
#
# Copyright (c) 2015, The Linux Foundation.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import unittest
import mock

import pwcli

class TestUtils(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(pwcli.clean('\n\t  foo  '), 'foo')

    def test_parse_list(self):
        self.assertEqual(pwcli.parse_list('1-3'), [1, 2, 3])
        self.assertEqual(pwcli.parse_list(''), [])
        self.assertEqual(pwcli.parse_list('99'), [99])
        self.assertEqual(pwcli.parse_list('0,77,7777'), [0, 77, 7777])
        self.assertEqual(pwcli.parse_list('0-3,5'), [0, 1, 2, 3, 5])
        self.assertEqual(pwcli.parse_list('10,11,12,14-15,16'),
                         [10, 11, 12, 14, 15, 16])
        self.assertEqual(pwcli.parse_list('0-3,2'), [0, 1, 2, 3])
        self.assertEqual(pwcli.parse_list('1-4,0-3,2,1-2'), [0, 1, 2, 3, 4])

        # negative tests
        with self.assertRaises(Exception):
            pwcli.parse_list('1 2')

        with self.assertRaises(Exception):
            pwcli.parse_list('foo')

        with self.assertRaises(Exception):
            pwcli.parse_list('foo-bar')

        with self.assertRaises(Exception):
            pwcli.parse_list('foo,bar')

        with self.assertRaises(Exception):
            pwcli.parse_list('1-bar')

        with self.assertRaises(Exception):
            pwcli.parse_list('1,bar')

        with self.assertRaises(Exception):
            pwcli.parse_list('bar,2')

        with self.assertRaises(Exception):
            pwcli.parse_list('bar-2')

    def test_shrink(self):
        f = pwcli.shrink
        self.assertEqual(f('12345678', 5), '12...')
        self.assertEqual(f('12345678', 5, ellipsis=False), '12345')

        # last space should be replaced with a dot
        self.assertEqual(f('yyy kaa koo nee', 11), 'yyy kaa....')

    def test_person(self):
        p = pwcli.Person
        self.assertEqual(p('Ed Example <ed@example.com>').get_name(),
                         'Ed Example')
        self.assertEqual(p('Ed Example <ed@example.com>').get_email(),
                         'ed@example.com')

        # if no name the email address should be returned
        self.assertEqual(p('<ed@example.com>').get_name(),
                         'ed@example.com')

if __name__ == '__main__':
    unittest.main()
