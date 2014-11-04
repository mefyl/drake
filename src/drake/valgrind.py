# Copyright (C) 2013-2014, Quentin "mefyl" Hocquet
#
# This software is provided "as is" without warranty of any kind,
# either expressed or implied, including but not limited to the
# implied warranties of fitness for a particular purpose.
#
# See the LICENSE file for more information.

import drake
import os
import subprocess

class Valgrind:

  def __init__(self, path = None):
    if path is None:
      path = drake.Path('valgrind')
    elif isinstance(path, Valgrind):
      self.__path = drake.Path(path.__path)
      self.__version = drake.Version(path.__version)
      return
    self.__path = drake.Path(path)
    try:
      output = subprocess.check_output([str(self.path), '--version'])
    except Exception as e:
      raise Exception('Unable to find %s' % self.path) from e
    output = output.decode()
    prefix = 'valgrind-'
    if not output.startswith(prefix):
      raise Exception('Unable to parse valgrind version: %s' % output)
    output = output[len(prefix):]
    self.__version = drake.Version(output)

  @property
  def path(self):
    return self.__path

  @property
  def version(self):
    return self.__version


class ValgrindRunner(drake.Runner):

  def __init__(self, exe, args = None, env = None, valgrind = None):
    super().__init__(exe, args = args, env = env)
    self.__valgrind = Valgrind(valgrind)
    self.__valgrind_status = drake.node(
      '%s.valgrind' % self.executable.name_relative)
    self.__valgrind_status.builder = self
    self.valgrind_reporting = drake.Runner.Reporting.on_failure

  @property
  def command(self):
    return [
      str(self.__valgrind.path),
      '--leak-check=full',
      '--num-callers=50',
      '--log-file=%s' % self.__valgrind_status.path(),
      '--error-exitcode=1',
    ] + super().command

  def _report(self, status):
    super()._report(status)
    if self._must_report(self.valgrind_reporting, status):
      self._report_node(self.__valgrind_status)
