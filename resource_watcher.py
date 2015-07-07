#!/usr/bin/python
#
# Copyright (C) 2015, Ary Pablo Batista <arypbatista@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#


import os, sys, json
import pynotify
import logging
from time import sleep

streamLog = logging.StreamHandler(sys.stdout)
streamLog.setLevel(logging.DEBUG)

formatter_keys = ('asctime', 'name', 'levelname', 'message')
formatter_string = '|'.join(['%%(%s)s' % key for key in formatter_keys])
formatter = logging.Formatter(formatter_string)
streamLog.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(streamLog)


CHECK_DELAY = 30 # seconds

root_path = os.path.dirname(__file__)

class ResourceWatcher(object):

    def __init__(self, resources, delay):
        pynotify.init("Resource Watcher")
        self.resources = resources
        self.delay = delay
        self.states = dict([ (name, False) for name, _ in self.resources.items()])

    def notify(self, title, message):
        notice = pynotify.Notification(title, message)
        notice.show()

    def is_online(self, resource):
        return os.system("ping -c 1 %s > /dev/null 2>&1" % (resource,)) == 0

    def notify_state_change(self, name, current_state):
        if current_state:
            message = "Resource '%s' has gone up." % (name,)
            title = name + " UP"
        else:
            message = "Resource '%s' has gone down." % (name,)
            title = name + " DOWN"
        logger.info(message)
        self.notify(title, message)

    def watch(self):
        for name, resource in self.resources.items():
            current_state = self.is_online(resource)
            if current_state != self.states[name]:
                self.notify_state_change(name, current_state)
                self.states[name] = current_state

    def busy_watch(self):
        while True:
            self.watch()
            sleep(self.delay)

def main():
    resources = json.loads(open(os.path.join(root_path, 'resources.json')).read())
    logger.info("Busy watch starts")
    ResourceWatcher(resources, CHECK_DELAY).busy_watch()

if __name__ == '__main__':
    main()
