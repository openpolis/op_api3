# -*- coding: utf-8 -*-
from collections import OrderedDict
import re

__author__ = 'guglielmo'

from rest_framework.renderers import JSONRenderer


def ld(data):
    if isinstance(data, dict):
        new_dict = OrderedDict()
        for key, value in data.items():
            new_key = key

            m = re.match(r'^json_ld_(.*)', key)
            if m:
                new_key = "@{0}".format(m.group(1))

            new_dict[new_key] = ld(value)
        return new_dict


    if isinstance(data, (list, tuple)):
        for i in range(len(data)):
            data[i] = ld(data[i])
        return data

    return data


class JSONLDRenderer(JSONRenderer):
    def render(self, data, *args, **kwargs):
        return super(JSONLDRenderer, self).render(
            ld(data), *args, **kwargs)
