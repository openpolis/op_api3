# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from op_api3.models import PrioritizedModel
from model_utils.models import TimeStampedModel


class LocationType(PrioritizedModel):
    """
    Maps the type of the administrative division for the Location

    Types can be specified with a *name* field, usually they are:

    - Continent,
    - Region,
    - City,
    - ...
    """
    name = models.CharField(max_length=255)


class AlternativeName(PrioritizedModel):
    """
    This class maps alternative location names, used in multilingual communities.
    Italian Alto-Adige, Friuli and Aosta regions have double language names.
    """
    location = models.ForeignKey('Location')
    name = models.CharField(max_length=255, help_text=_("Alternative name for the location"))
    language_code = models.CharField(max_length=2, blank=True, null=True, help_text=_("Language code (it, en, de, ...)"))


class Code(models.Model):
    """
    This class maps the different codes that may be used for the Location (MinInt, ISTAT)
    """
    location = models.ForeignKey('Location')
    name = models.CharField(max_length=255, help_text=_("Code name (Institution"))
    code = models.CharField(max_length=64)


class Location(PrioritizedModel, TimeStampedModel):
    """
    Maps all types of locations, from a Continent to a City.

    **location_types** are stored in the separate :model:`locations.LocationType` class,
    in order to allow dynamic definitions, and flexibility with respect to different contexts.

    **acronyms** may be:

    - nation acronyms (IT, US, UK, FRA),
    - two-letters acronyms for the *Province*, once used in italian vehicles registration numbers,
    - german city acronyms, still used as such,
    - so on ...

    **alternative_names** are different names used for the location in multi-language contexts

    **alternative_codes** are the different codes the location is known at different institution (if any)

    a location may change the name, or end its status as autonomous location, for a variety of reasons
    this events are mapped through these fields:

    - date_start,
    - date_end,
    - reason_end
    - new_location_set, old_location_set

    the location *hierarchy* maps the administrative divisions continent, nation, state, macroregions,
    regions, provinces, cities, ...
    this is done through the **parent_location** field

    From **TimeStampedModel** the class inherits **created** and **modified** fields,
    to keep track of creation and modification timestamps

    From **Prioritized**, it inherits the **priority** field,
    to allow custom sorting order
    """
    location_type = models.ForeignKey('LocationType')
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    acronym = models.CharField(max_length=8, blank=True, null=True)
    inhabitants_total = models.IntegerField(null=True, blank=True)
    inhabitants_male = models.IntegerField(null=True, blank=True)
    inhabitants_female = models.IntegerField(null=True, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    reason_end = models.CharField(max_length=255, null=True, blank=True,
                                  help_text=_("The reason why the location has ended (rename, merge, split, ...)"))
    new_location_set = models.ManyToManyField('Location', blank=True, null=True,
                                              related_name='old_location_set', symmetrical=False,
                                              help_text=_("Link to location after date_end"))
    parent_location = models.ForeignKey('Location', blank=True, null=True,
                                        related_name='children_location_set',
                                        help_text=_("Parent in the locations hierarchy"))


class LocationGIS(models.Model):
    """
    GIS extension of the Location model

    **geom** maps the GIS geometry
    **gps_lat**, **gps_lon** maps the centroid coordinates of the area
    """
    location = models.OneToOneField('Location')
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)
