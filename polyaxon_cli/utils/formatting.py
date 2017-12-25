# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from collections import OrderedDict

import click
import six
import sys

from polyaxon_schemas.experiment import ContainerResourcesConfig
from polyaxon_schemas.utils import to_list
from tabulate import tabulate


def get_meta_response(response):
    results = {}
    if response.get('next'):
        results['next'] = '--page={}'.format(response['next'])
    if response.get('previous'):
        results['previous'] = '--page={}'.format(response['previous'])
    if response.get('count'):
        results['count'] = response['count']
    return results


def list_dicts_to_tabulate(list_dicts):
    results = OrderedDict()
    for d_value in list_dicts:
        for k, v in six.iteritems(d_value):
            if k in results:
                results[k].append(v)
            else:
                results[k] = [v]

    return results


def dict_tabulate(dict_value, is_list_dict=False):
    if is_list_dict:
        headers = six.iterkeys(dict_value)
        click.echo(tabulate(dict_value, headers=headers))
    else:
        click.echo(tabulate(six.iteritems(dict_value)))


class Printer(object):
    COLORS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

    @staticmethod
    def print_header(text):
        click.secho('\n{}\n'.format(text), fg='yellow')

    @staticmethod
    def print_warning(text):
        click.secho('\n{}\n'.format(text), fg='magenta')

    @staticmethod
    def print_success(text):
        click.secho('\n{}\n'.format(text), fg='green')

    @staticmethod
    def print_error(text):
        click.secho('\n{}\n'.format(text), fg='red')

    @staticmethod
    def add_color(value, color):
        return click.style('{}'.format(value), fg=color)

    @classmethod
    def add_status_color(cls, obj_dict):
        if obj_dict.get('is_running'):
            obj_dict['last_status'] = cls.add_color(obj_dict['last_status'], color='yellow')
        elif obj_dict.get('is_done'):
            color = 'green' if obj_dict['last_status'] == 'Succeeded' else 'red'
            obj_dict['last_status'] = cls.add_color(obj_dict['last_status'], color=color)
        elif obj_dict.get('last_status'):
            obj_dict['last_status'] = cls.add_color(obj_dict['last_status'], color='cyan')
        return obj_dict

    @classmethod
    def decorate_format_value(cls, text_format, values, color):
        values = to_list(values)
        values = [cls.add_color(value, color) for value in values]
        click.echo(text_format.format(*values))

    @staticmethod
    def log(value):
        click.echo(value, nl=False)

    @classmethod
    def resources(cls, jobs_resources):
        jobs_resources = to_list(jobs_resources)
        click.clear()
        data = [['Job', 'Mem Usage/Limit', 'CPU%-CPUs', 'GPU Mem', 'GPU Usage']]
        for job_resources in jobs_resources:
            job_resources = ContainerResourcesConfig.from_dict(job_resources)
            line = [
                job_resources.job_uuid.hex,
                '{} / {}'.format(job_resources.memory_used / (1024 ** 3),
                                 job_resources.memory_limit / (1024 ** 3)),
                '{} - {}'.format(job_resources.cpu_percentage,
                                 len(job_resources.percpu_percentage))]
            if job_resources.gpu_resources:
                pass
            data.append(line)
        click.echo(tabulate(data, headers="firstrow"))
        sys.stdout.flush()
