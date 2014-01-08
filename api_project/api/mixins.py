# -*- coding: utf-8 -*-
from django.http import Http404
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

class ShortListModelMixin(ListModelMixin):
    """
    Extends ListModelMixin,
    allowing the specification of the list_fields arguments for the .list() method
    different fields can be shown for list and detail views
    """

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.object_list = self.filter_queryset(queryset)

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and not self.object_list:
            class_name = self.__class__.__name__
            error_msg = self.empty_error % {'class_name': class_name}
            raise Http404(error_msg)

        # Pagination size is set by the `.paginate_by` attribute,
        # which may be `None` to disable pagination.
        page_size = self.get_paginate_by(self.object_list)
        if page_size:
            packed = self.paginate_queryset(self.object_list, page_size)
            paginator, page, queryset, is_paginated = packed
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list)

        if 'list_fields' in kwargs:
            serializer.data['results'] = [
                dict((k,v) for k, v in i.iteritems() if k in kwargs['list_fields']) for i in serializer.data['results']
            ]

        return Response(serializer.data)
