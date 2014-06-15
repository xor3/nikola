# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Roberto Alsina, Chris Warrick and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
from nikola import __version__
import os
import json
import shutil
from io import BytesIO

try:
    import requests
except ImportError:
    requests = None  # NOQA

from nikola.plugin_categories import Command
from nikola import utils

LOGGER = utils.get_logger('install_bs3', utils.STDERR_HANDLER)


# Stolen from textwrap in Python 3.3.2.
def indent(text, prefix, predicate=None):  # NOQA
    """Adds 'prefix' to the beginning of selected lines in 'text'.

    If 'predicate' is provided, 'prefix' will only be added to the lines
    where 'predicate(line)' is True. If 'predicate' is not provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.
    """
    if predicate is None:
        def predicate(line):
            return line.strip()

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if predicate(line) else line)
    return ''.join(prefixed_lines())


class CommandInstallThemeBS3(Command):
    """Install a theme.  Bootstrap 3, to be precise."""

    name = "install_bs3"
    doc_usage = ""
    doc_purpose = "install bootstrap3 into the current site"
    output_dir = 'themes'
    cmd_options = []

    def _execute(self, options, args):
        """Install theme into current site."""
        if requests is None:
            utils.req_missing(['requests'], 'install the bootstrap3 theme')

        url = 'http://themes.getnikola.com/bs3/v{0}/bs3.json'.format(__version__)

        data = requests.get(url).text
        data = json.loads(data)
        installstatus1 = self.do_install('bootstrap3', data)
        installstatus2 = self.do_install('bootstrap3-jinja', data)
        if installstatus1:
            LOGGER.info('Remember to set THEME="bootstrap3" or THEME="bootstrap3-jinja" in conf.py if you want to use one of the themes.')

        return installstatus1 and installstatus2


    def do_install(self, name, data):
        if name in data:
            utils.makedirs(self.output_dir)
            LOGGER.info('Downloading: ' + data[name])
            zip_file = BytesIO()
            zip_file.write(requests.get(data[name]).content)
            LOGGER.info('Extracting: {0} into themes'.format(name))
            utils.extract_all(zip_file)
            dest_path = os.path.join('themes', name)
        else:
            try:
                theme_path = utils.get_theme_path(name)
            except:
                LOGGER.error("Can't find theme " + name)
                return False

            utils.makedirs(self.output_dir)
            dest_path = os.path.join(self.output_dir, name)
            if os.path.exists(dest_path):
                LOGGER.error("{0} is already installed".format(name))
                return False

            LOGGER.info('Copying {0} into themes'.format(theme_path))
            shutil.copytree(theme_path, dest_path)
        return True
