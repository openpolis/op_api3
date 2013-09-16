# -*- coding: utf-8 -*-
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from op_api.models import PrioritizedModel, UnifiedModel
from model_utils import Choices


class Person(TimeStampedModel):
    """
    The Person main data, needed to uniquely identify her among all other persons.
    """
    SEX = Choices(
        (0, 'female', _('Female')),
        (1, 'male', _('Male')),
    )
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    sex = models.CharField(max_length=1, blank=True, null=True, choices=SEX)
    birth_date = models.DateTimeField(null=True, blank=True)
    death_date = models.DateTimeField(null=True, blank=True)
    birth_location = models.ForeignKey('locations.Location', blank=True, null=True)
    picture = models.CharField(max_length=512, null=True, blank=True)
    profession_set = models.ManyToManyField('Profession', through='PersonHasProfession', blank=True, null=True)
    educationlevel_set = models.ManyToManyField('EducationLevel', through='PersonHasEducationLevel',
                                                blank=True, null=True)

    def __unicode__(self):
        return u"{p.first_name} {p.last_name} - {p.birth_date}".format(p=self)
    #
    # helper properties to get related multiple fields, as queryset instead of managers
    #

    @property
    def akas(self):
        return self.alternativename_set.all()

    @property
    def codes(self):
        return self.code_set.all()

    @property
    def op_id(self):
        """
        Openpolis ID is unique for a given object and may be returned with a simple query
        """
        return self.codes.get(name='op_id').code

    @property
    def professions(self):
        return self.profession_set.all()

    @property
    def education_levels(self):
        return self.educationlevel_set.all()

    @property
    def contacts(self):
        return self.contact_set.all()


class AlternativeName(PrioritizedModel):
    """
    Maps alternative person names (A.K.A.).
    """
    person = models.ForeignKey('Person')
    name = models.CharField(max_length=255, help_text=_("Alternative name for the person (AKA)"))


class Code(models.Model):
    """
    Maps the different codes that may be used for the Person
    (C.F., Social Security, ID Card, Passport, ... )
    """
    person = models.ForeignKey('Person')
    name = models.CharField(max_length=255, help_text=_("Code name"))
    code = models.CharField(max_length=128)


class Profession(PrioritizedModel, UnifiedModel):
    """
    A profession, usually taken from an official classification, depending on the context
    """
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"{obj.name}".format(obj=self)



class PersonHasProfession(models.Model):
    """
    The through table to map the optional, different professions of a person

    The **description** field can contain an optional description of the details or context of the profession
    """
    person = models.ForeignKey('Person')
    profession = models.ForeignKey('Profession')
    description = models.TextField(blank=True, null=True,
                                   help_text=_("An optional, short description of the context or of some details"))


class EducationLevel(PrioritizedModel, UnifiedModel):
    """
    An education level (school, university, doctorate, master
    """
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"{obj.name}".format(obj=self)


class PersonHasEducationLevel(models.Model):
    """
    The through table to map the education level of the person.

    The **description** field can contain an optional description of the details or context of the achievment
    """
    person = models.ForeignKey('Person')
    education_level = models.ForeignKey('EducationLevel')
    description = models.TextField(blank=True, null=True,
                                   help_text=_("An optional, short description of the achievement, if needed"))


class ContactType(models.Model):
    """
    The contact type (email, web site, twitter, facebook, telephone, linked in, ...)
    """
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return u"{obj.name}".format(obj=self)


class Contact(models.Model):
    """
    A generic resource to contact the person. By specifying the contact type, and bydynamically growing the
    contact type table, many different and evolving contact types can be added.
    """
    person = models.ForeignKey('Person', null=True)
    contact_type = models.ForeignKey('ContactType')
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True,
                                   help_text=_("A short description of the contact, if needed"))

    def __unicode__(self):
        return u"{obj.value} (type: {obj.contact_type})".format(obj=self)


