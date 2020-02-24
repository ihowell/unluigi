# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Package containing core gaps functionality.
"""

from gaps.__meta__ import __version__

from gaps import task
from gaps.task import Task, Config, ExternalTask, WrapperTask, namespace, auto_namespace

from gaps import target
from gaps.target import Target

from gaps import local_target
from gaps.local_target import LocalTarget

from gaps import parameter
from gaps.parameter import (
    Parameter, DateParameter, MonthParameter, YearParameter, DateHourParameter,
    DateMinuteParameter, DateSecondParameter, DateIntervalParameter,
    TimeDeltaParameter, IntParameter, FloatParameter, BoolParameter,
    TaskParameter, EnumParameter, DictParameter, ListParameter, TupleParameter,
    NumericalParameter, ChoiceParameter, OptionalParameter)

from gaps import worker
from gaps.worker import Worker

from gaps import configuration

from gaps import interface
from gaps.interface import run, build
from gaps.execution_summary import GapsStatusCode

from gaps import event
from gaps.event import Event

__all__ = [
    'task',
    'Task',
    'Config',
    'ExternalTask',
    'WrapperTask',
    'namespace',
    'auto_namespace',
    'target',
    'Target',
    'LocalTarget',
    'parameter',
    'Parameter',
    'DateParameter',
    'MonthParameter',
    'YearParameter',
    'DateHourParameter',
    'DateMinuteParameter',
    'DateSecondParameter',
    'DateIntervalParameter',
    'TimeDeltaParameter',
    'IntParameter',
    'FloatParameter',
    'BoolParameter',
    'TaskParameter',
    'ListParameter',
    'TupleParameter',
    'EnumParameter',
    'DictParameter',
    'configuration',
    'interface',
    'local_target',
    'run',
    'build',
    'worker',
    'Worker',
    'event',
    'Event',
    'NumericalParameter',
    'ChoiceParameter',
    'OptionalParameter',
    'GapsStatusCode',
    '__version__',
]
