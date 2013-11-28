from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from api.models import PrioritizedModel


class PlaceType(PrioritizedModel):
    """
    Maps the type of the administrative division for the Location

    Types can be specified with a *name* field, usually they are:

    - Continent,
    - Region,
    - City,
    - ...
    """
    name = models.CharField(max_length=255)


class I18NName(PrioritizedModel):
    """
    This class maps Internationalized names.
    The main name is copied in Place.name field
    """
    place = models.ForeignKey('Place')
    name = models.CharField(max_length=255, help_text=_("Alternative name for the location"))
    language_code = models.CharField(max_length=2, blank=True, null=True, help_text=_("ISO 639-1 language code (it, en, de, ...)"))


class Place(PrioritizedModel, TimeStampedModel):
    """
    Maps all types of places, from a Continent to a neighborhood.

    **place_types** are stored in the separate :model:`locations.PlaceType` class,
    in order to allow dynamic definitions, and flexibility with respect to different contexts.

    **acronyms** may be:

    - nation acronyms (IT, US, UK, FRA),
    - two-letters acronyms for the *Province*, once used in italian vehicles registration numbers,
    - german city acronyms, still used as such,
    - so on ...

    **internationalized names** are  names used for the place in multi-language contexts

    **identifiers** are the different codes or handles the place is known at different institution (if any)

    a place may change the name, or end its status as autonomous place, for a variety of reasons
    this events are mapped through these fields:

    - date_start,
    - date_end,
    - reason_end
    - new_place_set, old_place_set

    the location *hierarchy* maps the administrative divisions continent, nation, state, macroregions,
    regions, provinces, cities, entities, geographic organizations
    this is done through the parent_place, and child_place_set field

    From **TimeStampedModel** the class inherits **created** and **modified** fields,
    to keep track of creation and modification timestamps

    From **Prioritized**, it inherits the **priority** field,
    to allow custom sorting order
    """
    place_type = models.ForeignKey('PlaceType')
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    inhabitants_total = models.IntegerField(null=True, blank=True)
    area_total = models.FloatField(null=True, blank=True)

    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    reason_end = models.CharField(max_length=255, null=True, blank=True,
                                  help_text=_("The reason why the location has ended (rename, merge, split, ...)"))
    new_place_set = models.ManyToManyField('Place', blank=True, null=True,
                                           related_name='old_place_set', symmetrical=False,
                                           help_text=_("Link to place(s) after date_end"))

    parent_place_set = models.ManyToManyField('Place', blank=True, null=True,
                                              related_name='child_place_set', through='GeoMembership',
                                              help_text=_("Parent(s) in the hierarchy"))


class PlaceGEOInfo(gis_models.Model):
    """
    GIS extension of the Location model

    **geom** maps the GIS geometry
    **gps_lat**, **gps_lon** maps the centroid coordinates of the area
    """
    location = models.OneToOneField('Place')
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)


class PlaceContextInfo(models.Model):
    """
    Context information related to a place.
    """
    place = models.ForeignKey('Place')
    key = models.CharField(_("label"), max_length=128, help_text=_("A short label to indicate the value meaning"))
    value_num = models.FloatField(_("numeric value"), help_text=_("A numeric value, useable in comparisons"))
    value_char = models.CharField(_("char value"), max_length=256, help_text=_("A string value"))


class Identifier(models.Model):
    """
    All issued identifiers related to the place
    Regional ID, MinintID, ...
    """
    place = models.ForeignKey('Place')
    scheme = models.CharField(_("scheme"), max_length=128, blank=True, help_text=_("An identifier scheme, e.g. ISTAT_REG_ID"))
    identifier = models.CharField(_("identifier"), max_length=128, help_text=_("An issued identifier, e.g. '012'"))


class Link(models.Model):
    """
    All URLs where info about the place can be found on the internet.
    """
    place = models.ForeignKey('Place')
    url = models.URLField(_("url"), help_text=_("A URL"))
    note = models.CharField(_("note"), max_length=128, blank=True, help_text=_("A note, e.g. 'Wikipedia page'"))


class GeoMembership(models.Model):
    """
    Maps membership of a geographic place to another place.
    For example a province is a member of a Region.
    """
    parent = models.ForeignKey('Place')
    child = models.ForeignKey('Place')
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    note = models.TextField(null=True, blank=True,
                            help_text=_("Some unstructured note about why the membership started, changed, or ended"))
