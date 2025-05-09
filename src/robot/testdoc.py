#!/usr/bin/env python

#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Module implementing the command line entry point for the `Testdoc` tool.

This module can be executed from the command line using the following
approaches::

    python -m robot.testdoc
    python path/to/robot/testdoc.py

Instead of ``python`` it is possible to use also other Python interpreters.

This module also provides :func:`testdoc` and :func:`testdoc_cli` functions
that can be used programmatically. Other code is for internal usage.
"""

import sys
import time
from pathlib import Path

if __name__ == "__main__" and "robot" not in sys.modules:
    from pythonpathsetter import set_pythonpath

    set_pythonpath()

from robot.conf import RobotSettings
from robot.htmldata import HtmlFileWriter, JsonWriter, ModelWriter, TESTDOC
from robot.running import TestSuiteBuilder
from robot.utils import (
    abspath, Application, file_writer, get_link_path, html_escape, html_format,
    is_list_like, secs_to_timestr, seq2str2, timestr_to_secs, unescape
)

USAGE = """robot.testdoc -- Robot Framework test data documentation tool

Version:  <VERSION>

Usage:  python -m robot.testdoc [options] data_sources output_file

Testdoc generates a high level test documentation based on Robot Framework
test data. Generated documentation includes name, documentation and other
metadata of each test suite and test case, as well as the top-level keywords
and their arguments.

Options
=======

  -T --title title       Set the title of the generated documentation.
                         Underscores in the title are converted to spaces.
                         The default title is the name of the top level suite.
  -N --name name         Override the name of the top level suite.
  -D --doc document      Override the documentation of the top level suite.
  -M --metadata name:value *  Set/override metadata of the top level suite.
  -G --settag tag *      Set given tag(s) to all test cases.
  -t --test name *       Include tests by name.
  -s --suite name *      Include suites by name.
  -i --include tag *     Include tests by tags.
  -e --exclude tag *     Exclude tests by tags.
  -A --argumentfile path *  Text file to read more arguments from. Use special
                          path `STDIN` to read contents from the standard input
                          stream. File can have both options and data sources
                          one per line. Contents do not need to be escaped but
                          spaces in the beginning and end of lines are removed.
                          Empty lines and lines starting with a hash character
                          (#) are ignored.
                          Example file:
                          |  --name Example
                          |  # This is a comment line
                          |  my_tests.robot
                          |  output.html
                          Examples:
                          --argumentfile argfile.txt --argumentfile STDIN
  -h -? --help           Print this help.

All options except --title have exactly same semantics as same options have
when executing test cases.

Execution
=========

Data can be given as a single file, directory, or as multiple files and
directories. In all these cases, the last argument must be the file where
to write the output. The output is always created in HTML format.

Testdoc works with all interpreters supported by Robot Framework.
It can be executed as an installed module like
`python -m robot.testdoc` or as a script like `python path/robot/testdoc.py`.

Examples:

  python -m robot.testdoc my_test.robot testdoc.html
  python path/to/robot/testdoc.py first_suite.txt second_suite.txt output.html

For more information about Testdoc and other built-in tools, see
http://robotframework.org/robotframework/#built-in-tools.
"""


class TestDoc(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(2,))

    def main(self, datasources, title=None, **options):
        outfile = abspath(datasources.pop())
        suite = TestSuiteFactory(datasources, **options)
        self._write_test_doc(suite, outfile, title)
        self.console(outfile)

    def _write_test_doc(self, suite, outfile, title):
        with file_writer(outfile, usage="Testdoc output") as output:
            model_writer = TestdocModelWriter(output, suite, title)
            HtmlFileWriter(output, model_writer).write(TESTDOC)


def TestSuiteFactory(datasources, **options):
    settings = RobotSettings(options)
    if not is_list_like(datasources):
        datasources = [datasources]
    suite = TestSuiteBuilder(process_curdir=False).build(*datasources)
    suite.configure(**settings.suite_config)
    return suite


class TestdocModelWriter(ModelWriter):

    def __init__(self, output, suite, title=None):
        self._output = output
        self._output_path = getattr(output, "name", None)
        self._suite = suite
        self._title = title.replace("_", " ") if title else suite.name

    def write(self, line):
        self._output.write('<script type="text/javascript">\n')
        self.write_data()
        self._output.write("</script>\n")

    def write_data(self):
        model = {
            "suite": JsonConverter(self._output_path).convert(self._suite),
            "title": self._title,
            "generated": int(time.time() * 1000),
        }
        JsonWriter(self._output).write_json("testdoc = ", model)


class JsonConverter:

    def __init__(self, output_path=None):
        self._output_path = output_path

    def convert(self, suite):
        return self._convert_suite(suite)

    def _convert_suite(self, suite):
        return {
            "source": str(suite.source or ""),
            "relativeSource": self._get_relative_source(suite.source),
            "id": suite.id,
            "name": self._escape(suite.name),
            "fullName": self._escape(suite.full_name),
            "doc": self._html(suite.doc),
            "metadata": [
                (self._escape(name), self._html(value))
                for name, value in suite.metadata.items()
            ],
            "numberOfTests": suite.test_count,
            "suites": self._convert_suites(suite),
            "tests": self._convert_tests(suite),
            "keywords": list(self._convert_keywords((suite.setup, suite.teardown))),
        }

    def _get_relative_source(self, source):
        if not source or not self._output_path:
            return ""
        return get_link_path(source, Path(self._output_path).parent)

    def _escape(self, item):
        return html_escape(item)

    def _html(self, item):
        return html_format(unescape(item))

    def _convert_suites(self, suite):
        return [self._convert_suite(s) for s in suite.suites]

    def _convert_tests(self, suite):
        return [self._convert_test(t) for t in suite.tests]

    def _convert_test(self, test):
        if test.setup:
            test.body.insert(0, test.setup)
        if test.teardown:
            test.body.append(test.teardown)
        return {
            "name": self._escape(test.name),
            "fullName": self._escape(test.full_name),
            "id": test.id,
            "doc": self._html(test.doc),
            "tags": [self._escape(t) for t in test.tags],
            "timeout": self._get_timeout(test.timeout),
            "keywords": list(self._convert_keywords(test.body)),
        }

    def _convert_keywords(self, keywords):
        for kw in keywords:
            if not kw:
                continue
            if kw.type in kw.KEYWORD_TYPES:
                yield self._convert_keyword(kw)
            elif kw.type == kw.FOR:
                yield self._convert_for(kw)
            elif kw.type == kw.WHILE:
                yield self._convert_while(kw)
            elif kw.type == kw.IF_ELSE_ROOT:
                yield from self._convert_if(kw)
            elif kw.type == kw.TRY_EXCEPT_ROOT:
                yield from self._convert_try(kw)
            elif kw.type == kw.VAR:
                yield self._convert_var(kw)

    def _convert_for(self, data):
        name = f"{', '.join(data.assign)} {data.flavor} {seq2str2(data.values)}"
        return {"type": "FOR", "name": self._escape(name), "arguments": ""}

    def _convert_while(self, data):
        return {"type": "WHILE", "name": self._escape(data.condition), "arguments": ""}

    def _convert_if(self, data):
        for branch in data.body:
            yield {
                "type": branch.type,
                "name": self._escape(branch.condition or ""),
                "arguments": "",
            }

    def _convert_try(self, data):
        for branch in data.body:
            if branch.type == branch.EXCEPT:
                patterns = ", ".join(branch.patterns)
                as_var = f"AS {branch.assign}" if branch.assign else ""
                name = f"{patterns} {as_var}".strip()
            else:
                name = ""
            yield {"type": branch.type, "name": name, "arguments": ""}

    def _convert_var(self, data):
        if data.name[0] == "$" and len(data.value) == 1:
            value = data.value[0]
        else:
            value = "[" + ", ".join(data.value) + "]"
        return {"type": "VAR", "name": f"{data.name} = {value}"}

    def _convert_keyword(self, kw):
        return {
            "type": kw.type,
            "name": self._escape(self._get_kw_name(kw)),
            "arguments": self._escape(", ".join(kw.args)),
        }

    def _get_kw_name(self, kw):
        if kw.assign:
            assign = ", ".join(a.rstrip("= ") for a in kw.assign)
            return f"{assign} = {kw.name}"
        return kw.name

    def _get_timeout(self, timeout):
        if timeout is None:
            return ""
        try:
            tout = secs_to_timestr(timestr_to_secs(timeout))
        except ValueError:
            tout = timeout
        return tout


def testdoc_cli(arguments):
    """Executes `Testdoc` similarly as from the command line.

    :param arguments: command line arguments as a list of strings.

    For programmatic usage the :func:`testdoc` function is typically better. It
    has a better API for that and does not call :func:`sys.exit` like
    this function.

    Example::

        from robot.testdoc import testdoc_cli

        testdoc_cli(['--title', 'Test Plan', 'mytests', 'plan.html'])
    """
    TestDoc().execute_cli(arguments)


def testdoc(*arguments, **options):
    """Executes `Testdoc` programmatically.

    Arguments and options have same semantics, and options have same names,
    as arguments and options to Testdoc.

    Example::

        from robot.testdoc import testdoc

        testdoc('mytests', 'plan.html', title='Test Plan')
    """
    TestDoc().execute(*arguments, **options)


if __name__ == "__main__":
    testdoc_cli(sys.argv[1:])
