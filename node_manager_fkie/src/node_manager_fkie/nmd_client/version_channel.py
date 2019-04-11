# Software License Agreement (BSD License)
#
# Copyright (c) 2018, Fraunhofer FKIE/CMS, Alexander Tiderko
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Fraunhofer nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import division, absolute_import, print_function, unicode_literals

import rospy
from python_qt_binding.QtCore import Signal

import node_manager_daemon_fkie.remote as remote
import node_manager_daemon_fkie.version_stub as vstub
from node_manager_daemon_fkie import url as nmdurl

from .channel_interface import ChannelInterface


class VersionChannel(ChannelInterface):

    version_signal = Signal(str, str, str)
    '''
      :ivar str,str,str version_signal: signal emitted on new version {grpc_url, version, date}.
    '''

    def clear_cache(self, grpc_url=''):
        pass

    def get_version_manager(self, uri='localhost:12321'):
        channel = remote.get_insecure_channel(uri)
        if channel is not None:
            return vstub.VersionStub(channel)
        raise Exception("Node manager daemon '%s' not reachable" % uri)

    def get_version_threaded(self, grpc_url='grpc://localhost:12321'):
        self._threads.start_thread("gvt_%s" % grpc_url, target=self.get_version, args=(grpc_url, True))

    def get_version(self, grpc_url='grpc://localhost:12321', threaded=False):
        rospy.logdebug("get version from %s" % (grpc_url))
        uri, _ = nmdurl.split(grpc_url)
        vm = self.get_version_manager(uri)
        try:
            version, date = vm.get_version()
            if threaded:
                self.version_signal.emit(grpc_url, version, date)
                self._threads.finished("gvt_%s" % grpc_url)
            return version, date
        except Exception as e:
            self.error.emit("get_version", "grpc://%s" % uri, "", e)
