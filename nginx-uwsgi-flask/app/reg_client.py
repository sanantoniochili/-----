#!/usr/bin/env python

# Copyright 2014 The University of Edinburgh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import curses
import collections
import argparse
import datetime
import logging

logging.basicConfig()
logger = logging.getLogger('DJREG_CLIENT')
logger.setLevel(logging.INFO)

from reg_lib import VerceRegManager

class VerceRegClient:
  HISTORY_LENGTH = 5000
  history = None
  manager = None

  def __init__(self):
    self.history = collections.deque(maxlen=self.HISTORY_LENGTH)
    self.manager = VerceRegManager()


def main():
  # TODO: Define and implement commands for the client
  # parser = argparse.ArgumentParser(description='Client for the VERCE Registry.')
  # parser.add_argument('command', metavar='Command', type=str,
  #                      help='a VERCE Registry command')
                     
  manager = VerceRegManager()
  manager.login('iraklis', 'iraklis')
  logger.info(manager.get_auth_token())
  # manager.login('admin', 'admin')
  # logger.info(manager.get_auth_token())
  # manager.clone(1, 'cloned_wspc'+'@'.join(str(datetime.datetime.now()).split()))

  # logger.info(manager.get_pe_spec(1, 'pes', 'MyPE'))
  # logger.info(manager.get_pe_spec(1, 'fns', 'Fn1')) # should raise an exception
  
  manager.delete_pe_spec(1, 'libpck', 'LibPE11')
  new_pe = manager.register_pe_spec(1, 'libpck', 'LibPE11', descr='Some description for a test PE')
  new_conn = manager.add_pe_connection(str(new_pe['id']), kind='IN', name='CnName', stype='str', dtype='DTYPE', comment='My comment', is_array=True, modifiers='one:two')
  manager.add_pe_connection(str(new_pe['id']), kind='OUT', name='outconn')

  
  


if __name__ == '__main__':
  main()