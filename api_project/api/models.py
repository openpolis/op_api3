# -*- coding: utf-8 -*-
"""
Abstract models, that can be extended through multiple-inheritance,
to activate the desired behaviours in concrete application classes.
"""
from django.db import models


class PrioritizedModel(models.Model):
    """
    An abstract base class that provides an optional priority field,
    to impose a custom sorting order.
    """
    priority = models.IntegerField(null=True, blank=True, default=0,
                                   help_text="Sort order in case ambiguities arise")

    class Meta:
        abstract = True


class UnifiedModel(models.Model):
    """
    An abstrat base class that provides a simple 2-levels hierarchy with main instances and
    sub-instances, to allow *unification* of different records under a wider cathegory.

    The *get_main* method returns the main instance (self if it is already main)
    """
    main = models.ForeignKey('self', blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def get_main(self):
        """
        Return the main instance (self if already main)
        """
        if not self.is_main():
            return self.main
        else:
            return self

    def is_main(self):
        """
        Return True/False if the instance is a main instance or not
        """
        return self.main is None