from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query import EmptyQuerySet
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from api.models import PrioritizedModel
from popolo.behaviors.models import Dateframeable
from mptt.models import MPTTModel, TreeForeignKey


class Language(models.Model):
    """
    Maps languages, with names and 2-char iso 639-1 codes.
    Taken from http://dbpedia.org, using a sparql query
    """
    dbpedia_resource = models.CharField(max_length=255,
        help_text=_("DbPedia URI of the resource"), unique=True)
    iso639_1_code = models.CharField(max_length=2)
    name = models.CharField(max_length=128,
        help_text=_("English name of the language"))

    def __unicode__(self):
        return u"{0} ({1})".format(self.name, self.iso639_1_code)


class Place(PrioritizedModel, TimeStampedModel, Dateframeable):
    """
    Maps all types of places, from a Continent to a neighborhood.

    **place_types** are stored in the separate
    :model:`places.PlaceType` class,
    in order to allow dynamic definitions, and flexibility with
    respect to different contexts.

    **acronyms** may be:

    - nation acronyms (IT, US, UK, FRA),
    - two-letters acronyms for the *Province*, once used in
      italian vehicles registration numbers,
    - german city acronyms, still used as such,
    - so on ...

    **internationalized names** are  names used for the place
    in multi-language contexts

    **placeidentifiers** are the different codes or handles the place is
    known at different institution (if any)

    **identifiers** identify the different scheme and names of
    the place_identifiers

    **links** to resources on the internet where more info or data
    can be found, relating to a place

    a place may change the name, or end its status as autonomous place,
    for a variety of reasons this events are mapped through these
    fields:

    - reason_end
    - new_place_set, old_place_set
    - popolo.behaviours.Dateframeable's start_date and end_date fields

    the places *hierarchy* maps the administrative divisions continent,
    nation, state, macroregions, regions, provinces, cities, entities,
    geographic organizations, ...
    this is done through the parent_place, and child_place_set field

    From **TimeStampedModel** the class inherits **created** and
    **modified** fields, to keep track of creation and
    modification timestamps

    From **Prioritized**, it inherits the **priority** field,
    to allow custom sorting order
    """
    place_type = models.ForeignKey('PlaceType')
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    inhabitants = models.IntegerField(null=True, blank=True)
    area = models.FloatField(null=True, blank=True)

    reason_end = models.CharField(max_length=255, null=True, blank=True,
        help_text=_(
            "The reason why the place has ended (rename, merge, split, ...)"
        )
    )
    new_places = models.ManyToManyField('Place', blank=True, null=True,
        related_name='old_places', symmetrical=False,
        help_text=_("Link to place(s) after date_end")
    )

    identifiers = models.ManyToManyField('Identifier', blank=True, null=True,
         related_name='place_set', through='PlaceIdentifier',
         help_text=_('External identifiers')
    )

    @property
    def placeidentifiers(self):
        return self.placeidentifier_set.all()

    def referencing_nodes(self, tree_slug):
        """
        Returns the set of nodes that reference the Place instance.
        Handles the situation where a Place is not referenced in the
        SubdivisionTree identified by tree_slug, but in one of the
        trees specified in the used_trees link.

        Return a queryset or an EmptyQuerySet if no such nodes exist.
        """
        nodes = EmptyQuerySet()
        treetag = SubdivisionTreeTag.objects.get(slug=tree_slug)
        nodes = self.subdivision_nodes_set.filter(
            tag=treetag
        )
        if not nodes:
            usedtrees =  treetag.used_trees.all()
            if usedtrees:
                nodes = self.subdivision_nodes_set.filter(
                    tag__in=usedtrees
                )

        return nodes


    def __unicode__(self):
        return self.name


class PlaceType(PrioritizedModel):
    """
    Maps the type of the administrative division for the Place

    Types can be specified with a *name* field, usually they are:

    - Continent,
    - Region,
    - City,
    - ...
    """
    name = models.CharField(_("name"), max_length=255,
        help_text="English name of the place type")
    description = models.TextField(_("description"),
        blank=True, null=True,
        help_text=_(
            "An extended description of the place type, when needed"
        )
    )
    subdivision_tree = models.ForeignKey('SubdivisionTreeTag',
        null=True, blank=True,
        help_text=_(
            "A reference to the Subdivision Tree where the PlaceType is used"
        )
    )

    def __unicode__(self):
        return self.name


class PlaceAcronym(models.Model):
    """
    Maps acronyms related to a Place
    - nation acronyms (IT, US, UK, FRA),
    - two-letters acronyms for the *Province*, once used in italian
      vehicles registration numbers,
    - german city acronyms, still used as such,
    - so on ...
    """
    place = models.ForeignKey('Place')
    acronym = models.CharField(_("acronym"), max_length=128,
        help_text=_("An acronym for the place, e.g. 'PV'")
    )

    def __unicode__(self):
        return u"{0} - {1}".format(self.place, self.acronym)

    class Meta:
        verbose_name = 'Acronym'
        verbose_name_plural = 'Acronyms'


class PlaceI18Name(models.Model):
    """
    Internationalized name for a Place.
    Contains the reference to the language.
    """
    place = models.ForeignKey('Place')
    language = models.ForeignKey('Language')
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        verbose_name = 'I18N Name'
        verbose_name_plural = 'I18N Names'


class Identifier(models.Model):
    """
    Maps identifiers that can be used, with scheme, description,
    referred by PlaceIdentifier; normalizes external identifiers relations
    Regional ID, MinintID, ...
    """
    scheme = models.CharField(_("scheme"), max_length=512,
        help_text=_("An identifier scheme, e.g. ISTAT, OP, MININT, ..."))
    name = models.CharField(_("name"), max_length=128,
        help_text=_("The name of the identifier: CITY_ID, REGION_ID, ..."))
    subdivision_tree = models.ForeignKey('SubdivisionTreeTag',
        null=True, blank=True,
        help_text=_("""A reference to the root node of the subdivision
            where the PlaceType is used""")
    )

    def __unicode__(self):
        return u"{0}:{1}".format(
            self.scheme, self.name
        )


class PlaceIdentifier(models.Model):
    """
    All issued identifiers (value) related to the place
    Regional ID, MinintID, ...
    """
    place = models.ForeignKey('Place')
    identifier = models.ForeignKey('Identifier')
    value = models.CharField(_("identifier"), max_length=128,
        help_text=_("An issued identifier, e.g. '012'")
    )

    def __unicode__(self):
        return u"{0}:{1} - {2}".format(
            self.place, self.identifier, self.value
        )

    class Meta:
        verbose_name = 'External identifier'
        verbose_name_plural = 'External identifiers'


class PlaceLink(models.Model):
    """
    All URLs where info about the place can be found on the internet.
    """
    place = models.ForeignKey('Place')
    url = models.URLField(_("url"), help_text=_("A URL"))

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'


class PlaceGEOInfo(gis_models.Model):
    """
    GIS extension of the Place model

    **geom** maps the GIS geometry
    **gps_lat**, **gps_lon** maps the centroid coordinates of the area
    """
    place = models.OneToOneField('Place')
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'Geo-based information'


class SubdivisionTreeNode(MPTTModel, Dateframeable, PrioritizedModel):
    """
    Maps places subdivisions as trees.

    A subdivision may be an official administrative subdivision,
    a.k.a. categorization, or any other hierarchical grouping of
    existing places, i.e. Electoral Constituencies, or official or unofficial
    international organizations (OECD, BRICS, ...)

    A common void tree may host many subdivision trees (level 1 nodes).

    A node may link back to just one existing Place instance
    (place attribute).

    A node not linking to a Place, is a virtual place
    (it exists only as container of real places).

    A node may have an ``equivalent_to`` link to another node,
    in a diferent subdivision tree.
    The meaning of the ``equivalent_to`` is that from children
    and descendants of the original node, can be fetched from
    the destination node.
    This is to avoid replication of the same nodes over subdivision
    trees that differ only in the upper nodes.
    """
    tag = models.ForeignKey('SubdivisionTreeTag',
        related_name='node_set')
    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')
    note = models.TextField(null=True, blank=True,
        help_text=_("""Some unstructured note about why the
        membership started, changed, or ended"""))
    place = models.ForeignKey('Place',
        related_name='subdivision_nodes_set', blank=True, null=True)

    equivalent_to = models.ForeignKey('self',
        null=True, blank=True,
        related_name='equivalent_from_set'
    )

    class MPTTMeta:
        verbose_name = 'Subdivision tree'
        verbose_name_plural = 'Subdivision trees'
        unique_together= (('parent', 'tag', 'start_date'),)

    def __unicode__(self):
        return u"id: {0}, place: {1}, tag: {2}".format(
            self.pk, self.place, self.tag
        )


class SubdivisionTreeTag(models.Model):
    """
    Tag used to identify different SubdivisionTrees, or categorizations.

    A SubdivisionTreeTag identifies a Tree.

    A tag may be linked, by the ``used_trees`` relation to one or more
    different subdivision tags.
    The meaning of this is that the original tree (identified by
    the original tag), has some relations
    of type equivalent_to directed towards the destination trees.
    This allows the dereferencing operation, from a Place instance
    to the set of TreeNodes referencing it,
    in those situation where ``equivalent_to`` relations
    among nodes are involved.

    This helps in dereferencing a place, given a tag slug.
    """
    label = models.CharField(max_length=64,
        help_text=_("The visualized Tag label"))
    slug = models.SlugField(max_length=64, unique=True,
        help_text=_("The slug used in URIs"))
    description = models.TextField(blank=True, null=True)
    used_trees = models.ManyToManyField('self',
        null=True, blank=True, related_name='used_by_set')

    def __unicode__(self):
        return self.label



#
####### Signals handling #####
#
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=SubdivisionTreeNode)
def check_equivalent_nodes(sender, instance, created, **kwargs):
    """
    Check the currently active equivalent_to relations
    for all nodes in the same tree (SubdivisionTreeTag)
    belonging to the node just saved.
    Align the tree.used_trees with the current situation.
    """

    # the node just saved
    node = instance

    # the node's tree (SubdivisionTreeTag)
    tree = node.tag

    # list of node in the tree, having equivalents_to relations
    tree_equivalents = SubdivisionTreeNode.objects.filter(
       tag=tree, equivalent_to__isnull=False
    )

    # set of trees destinations of equivalent_to relations
    # (emulates distinct)
    currently_used_trees_set = set([
        n.equivalent_to.tag for n in tree_equivalents
    ])

    # tree.used_trees as a set
    used_trees_set = set(tree.used_trees.all())

    # alignment of current and stored used_trees lists
    # subtracion between two sets depends on the orders of factors

    # remove items stored but not currently used
    remove_list = used_trees_set - currently_used_trees_set
    for t in remove_list:
        tree.used_trees.remove(t)

    # add items currently used and not stored
    add_list = currently_used_trees_set - used_trees_set
    for t in add_list:
        tree.used_trees.add(t)

