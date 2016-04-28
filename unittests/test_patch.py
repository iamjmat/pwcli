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
import email
import re

import pwcli

FAKE_ATTRIBUTES = {
    'name' : 'nnnn',
    'id' : '11',
    'delegate' : 'dddd',
    'state_id' : '1234',
    'state' : 'ssss'
}

TEST_MBOX = 'Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: [1/7] foo\nFrom: Dino Dinosaurus <dino@example.com>\nX-Patchwork-Id: 12345\nMessage-Id: <11111@example.com>\nTo: list@example.com\nDate: Thu,  10 Feb 2011 15:23:31 +0300\n\nFoo commit log. Ignore this text\n\nSigned-off-by: Dino Dinosaurus <dino@example.com>\n\n---\nFIXME: add the patch here\n'

class TestPatch(unittest.TestCase):
    @mock.patch('pwcli.PWCLI')
    def test_attributes(self, pw):
        attributes = FAKE_ATTRIBUTES
        patch = pwcli.Patch(pw, attributes, False)

        self.assertEqual(patch.get_name(), attributes['name'])
        self.assertEqual(patch.get_id(), attributes['id'])
        self.assertEqual(patch.get_delegate(), attributes['delegate'])
        self.assertEqual(patch.get_state_id(), attributes['state_id'])
        self.assertEqual(patch.get_state_name(), attributes['state'])

        pw.get_state_id = mock.Mock(return_value='7777')
        patch.set_state_name('Accepted')
        self.assertEqual(patch.get_state_name(), 'Accepted')
        self.assertEqual(patch.get_state_id(), '7777')
        pw.rpc.patch_set.assert_called_with(attributes['id'], { 'state' : '7777'})

    def test_reply_msg(self):
        attributes = FAKE_ATTRIBUTES
        patch = pwcli.Patch(None, attributes, False)

        patch.get_email = mock.Mock(return_value=email.message_from_string(TEST_MBOX))

        reply = patch.get_reply_msg('Timo Testi', 'test@example.com')

        self.assertEqual(reply['From'], 'Timo Testi <test@example.com>')
        self.assertEqual(reply['To'], 'Dino Dinosaurus <dino@example.com>')
        self.assertFalse('Cc' in reply)
        self.assertEqual(reply['Subject'], 'Re: [1/7] foo')

    def test_get_mbox_for_stgit(self):
        attributes = FAKE_ATTRIBUTES
        patch = pwcli.Patch(None, attributes, False)

        patch.get_mbox = mock.Mock(return_value=TEST_MBOX)

        mbox = patch.get_mbox_for_stgit()
        msg = email.message_from_string(mbox)

        # Check that the first line matches mbox format
        #
        # It would be nice to mock datetime.datetime so that we would
        # not have to skip the date from the first line but I didn't
        # figure out how to do that, without a library like freezegun.
        firstline = mbox.splitlines()[0]
        self.assertTrue(firstline.startswith('From nobody '))

        self.assertEqual(msg['Subject'], 'foo')

        # check that Patchwork-Id is set
        id_line = r'\nPatchwork-Id: %s\n' % (attributes['id'])
        search = re.search(id_line, msg.get_payload())
        self.assertTrue(search != None)

    def test_clean_subject(self):
        attributes = FAKE_ATTRIBUTES
        patch = pwcli.Patch(None, attributes, False)

        c = patch.clean_subject

        self.assertEqual(c('[] One two three four'), 'One two three four')
        self.assertEqual(c('[1/100] One two three four'), 'One two three four')
        self.assertEqual(c('[PATCH 1/100] One two three four'),
                         'One two three four')
        self.assertEqual(c('[PATCH RFC 14/14] foo: bar koo'), 'foo: bar koo')
        self.assertEqual(c('[RFC] [PATCH 14/99]   foo: bar koo'), 'foo: bar koo')
        self.assertEqual(c('bar: use array[]'), 'bar: use array[]')
        self.assertEqual(c('[PATCH] bar: use array[]'), 'bar: use array[]')
        self.assertEqual(c('[] [A] [B] [   PATCH 1/100000  ] bar: use [] in array[]'),
                         'bar: use [] in array[]')

if __name__ == '__main__':
    unittest.main()
