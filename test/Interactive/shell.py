#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Verify the ability of the "shell" command (and its "sh" and "!" aliases)
to shell out of interactive mode.
"""

import string
import sys

import TestSCons

test = TestSCons.TestSCons(combine=1)

_python_ = TestSCons._python_

shell_command_py    = test.workpath('shell_command.py')
_shell_command_py_  = '"%s"' % string.replace(shell_command_py, '\\', '\\\\')

test.write(shell_command_py, """\
print 'hello from shell_command.py'
""")

test.write('SConstruct', """\
Command('foo.out', 'foo.in', Copy('$TARGET', '$SOURCE'))
Command('1', [], Touch('$TARGET'))
""")

test.write('foo.in', "foo.in 1\n")



scons = test.start(arguments = '-Q --interactive')

scons.send("build foo.out 1\n")

test.wait_for(test.workpath('1'))

test.must_match(test.workpath('foo.out'), "foo.in 1\n")



scons.send('!%(_python_)s %(_shell_command_py_)s\n' % locals())

scons.send("\n")

scons.send('shell %(_python_)s %(_shell_command_py_)s\n' % locals())

scons.send("\n")

scons.send('sh %(_python_)s %(_shell_command_py_)s\n' % locals())

scons.send("\n")

scons.send('!no_such_command arg1 arg2\n')

scons.send("\n")

scons.send("build foo.out\n")

scons.send("\n")

if sys.platform == 'win32':
    no_such_error = 'The system cannot find the file specified'
else:
    no_such_error = 'No such file or directory'

expect_stdout = """\
scons>>> Copy("foo.out", "foo.in")
Touch("1")
scons>>> hello from shell_command.py
scons>>> !%(_python_)s %(_shell_command_py_)s
hello from shell_command.py
scons>>> hello from shell_command.py
scons>>> shell %(_python_)s %(_shell_command_py_)s
hello from shell_command.py
scons>>> hello from shell_command.py
scons>>> sh %(_python_)s %(_shell_command_py_)s
hello from shell_command.py
scons>>> scons: no_such_command: %(no_such_error)s
scons>>> !no_such_command arg1 arg2
scons: no_such_command: %(no_such_error)s
scons>>> scons: `foo.out' is up to date.
scons>>> build foo.out
scons: `foo.out' is up to date.
scons>>> 
""" % locals()

test.finish(scons, stdout = expect_stdout)



test.pass_test()