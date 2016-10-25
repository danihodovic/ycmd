# Copyright (C) 2015 ycmd contributors
#
# This file is part of ycmd.
#
# ycmd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ycmd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ycmd.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import *  # noqa
from future.utils import iterkeys
from future import standard_library
standard_library.install_aliases()

import logging
import os
import requests
import threading
import traceback
import subprocess
import json

from subprocess import PIPE
from ycmd import utils, responses
from ycmd.completers.completer import Completer
from ycmd.completers.completer_utils import GetFileContents

_logger = logging.getLogger( __name__ )

def ShouldEnableFlowCompleter():
    return True

class FlowCompleter( Completer ):
  """
  Completer for Javascript using Flow https://github.com/flowtype/flow-bin
  """

  def __init__( self, user_options ):
    super( FlowCompleter, self ).__init__( user_options )

  def ComputeCandidatesInner( self, request_data ):
    file_contents = GetFileContents( request_data, request_data['filepath'] )

    #  cmd = [
        #  'flow',
        #  'autocomplete',
        #  str(request_data['line_num']),
        #  str(request_data['start_column']),
        #  '--json'
    #  ]

    cmd = [
        'flow',
        'autocomplete',
        request_data['filepath'],
    ]


    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p.communicate(input=file_contents)

    try:
        flow_server_response = json.loads(stdout)
    except ValueError, e:
        _logger.warning(e)
        return []

    completions = []

    for completion in flow_server_response['result']:
        formatted = responses.BuildCompletionData(completion['name'], completion['type'])
        completions.append(formatted)

    return completions

  def SupportedFiletypes( self ):
    return [ 'javascript' ]

  def ServerIsHealthy( self, request_data = {} ):
      return True

