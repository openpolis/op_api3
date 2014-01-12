from django.contrib.gis.db import models as gis_models
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

    **acronym** may be:

    - nation acronym (IT, US, UK, FRA),
    - two-letters acronym for the *Province*, once used in
      italian vehicles registration numbers,
    - german city acronym, still used as such,
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
        ClassificationTree identified by tree_slug, but in one of the
        trees specified in the used_trees link.

        Return a queryset or an EmptyQuerySet if no such nodes exist.
        """
        treetag = ClassificationTreeTag.objects.get(slug=tree_slug)
        nodes = self.classification_nodes_set.filter(
            tag=treetag
        )
        if not nodes:
            usedtrees =  treetag.used_trees.all()
            if usedtrees:
                nodes = self.classification_nodes_set.filter(
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
    - Regione, Provincia, Comune
    - City,
    - ...
    """
    name = models.CharField(_("name"), max_length=255,
        help_text="English name of the place type")
    slug = models.SlugField(_("slug"), max_length=255,
        help_text="Slug of the place type. Must be unique.", unique=True,)
    description = models.TextField(_("description"),
        blank=True, null=True,
        help_text=_(
            "An extended description of the place type, when needed"
        )
    )
    classification_tree = models.ForeignKey('ClassificationTreeTag',
        null=True, blank=True,
        help_text=_(
            "A reference to the Classification Tree where the PlaceType is used"
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
    place = models.OneToOneField('Place', related_name="acronyms")
    acronym = models.CharField(_("acronym"), max_length=32,
        help_text=_("An acronym for the place, e.g. 'PV'")
    )

    def __unicode__(self):
        return u"{0} - {1}".format(self.place, self.acronym)

    class Meta:
        verbose_name = 'Acronym'
        verbose_name_plural = 'Acronyms'
        unique_together = ('place', 'acronym')


class PlaceI18Name(models.Model):
    """
    Internationalized name for a Place.
    Contains the reference to the language.
    """
    place = models.ForeignKey('Place', related_name='names')
    language = models.ForeignKey('Language')
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        verbose_name = 'I18N Name'
        verbose_name_plural = 'I18N Names'
        unique_together = ('place', 'language', 'name')



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
    slug = models.SlugField(_("slug"), max_length=255,
        help_text="Slug of the place type. Must be unique.", unique=True,)
    classification_tree = models.ForeignKey('ClassificationTreeTag',
        null=True, blank=True,
        help_text=_("""A reference to the root node of the classification
            where the PlaceType is used""")
    )

    def __unicode__(self):
        return u"{0}:{1}".format(
            self.scheme, self.name
        )

    class Meta:
        unique_together = ('scheme', 'name')


class PlaceIdentifier(models.Model):
    """
    All issued identifiers (value) related to the place
    Regional ID, MinintID, ...
    """
    place = models.ForeignKey('Place', related_name='placeidentifiers')
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
        unique_together = ('place', 'identifier')


class PlaceLink(models.Model):
    """
    All URLs where info about the place can be found on the internet.
    """
    place = models.ForeignKey('Place', related_name='links')
    uri = models.URLField(_("url"),
        help_text=_("The URI of a web page related to the Place"))
    text = models.CharField(_("text"), max_length=255,
        help_text=_("A descriptive text") )

    class Meta:
        verbose_name = 'Link'
        verbose_name_plural = 'Links'
        unique_together = ('place', 'uri')


class PlaceGEOInfo(gis_models.Model):
    """
    GIS extension of the Place model

    **geom** maps the GIS geometry
    **gps_lat**, **gps_lon** maps the centroid coordinates of the area
    """
    place = models.OneToOneField('Place', related_name='geoinfo')
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'Geo-based information'


class ClassificationTreeNode(MPTTModel, Dateframeable, PrioritizedModel):
    """
    Maps places classifications as trees.

    A classification may be an official administrative classification,
    a.k.a. categorization, or any other hierarchical grouping of
    existing places, i.e. Electoral Constituencies, or official or
    unofficial international organizations (OECD, BRICS, ...)

    A common void tree may host many classification trees (level 1 nodes).

    A node may either link back to just one existing Place instance
    (place attribute), or it may have an equivalent_to FK set.

    A node may have an ``equivalent_to`` link to another node,
    in a diferent classification tree.
    The meaning of the ``equivalent_to`` is that children
    and descendants of the original node, can be fetched from
    the destination node.
    This is to avoid replication of the same nodes over classification
    trees that differ only in the upper nodes.
    """
    tag = models.ForeignKey('ClassificationTreeTag',
        related_name='node_set')
    place = models.ForeignKey('Place', blank=True, null=True,
        related_name='classification_nodes_set')
    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')
    note = models.TextField(null=True, blank=True,
        help_text=_("""Some unstructured note about why the
        membership started, changed, or ended"""))

    equivalent_to = models.ForeignKey('self',
        null=True, blank=True,
        related_name='equivalent_from_set'
    )

    class MPTTMeta:
        verbose_name = 'Classification tree'
        verbose_name_plural = 'Classification trees'
        unique_together = (
            ('place', 'tag',),
            ('parent', 'tag', 'start_date',),
        )

    @property
    def reference_place(self):
        if self.place:
            return self.place
        else:
            return self.equivalent_to.reference_place

    @property
    def children_slugs(self):
        return self.children.all().values_list(
            'place__slug', 'tag__slug',
            'equivalent_to__place__slug'
        )

    @property
    def ancestors_slugs(self):
        return self.get_ancestors().values_list(
            'place__slug', 'tag__slug',
            'equivalent_to__place__slug'
        )

    def __unicode__(self):
        return u"id: {0}, place: {1}, tag: {2}".format(
            self.pk, self.place, self.tag
        )


class ClassificationTreeTag(models.Model):
    """
    Tag used to identify different ClassificationTrees, or categorizations.

    A ClassificationTreeTag identifies a Tree.

    A tag may be linked, by the ``used_trees`` relation to one or more
    different classification tags.
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

    def get_root_node(self):
        nodes_qs = ClassificationTreeNode.objects.filter(tag=self)
        n = nodes_qs.count()
        if n:
            return nodes_qs[0].get_root()
        else:
            return None

    def __unicode__(self):
        return self.label



#
####### Signals handling #####
#
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ClassificationTreeNode)
def check_equivalent_nodes(sender, instance, created, **kwargs):
    """
    Check the currently active equivalent_to relations
    for all nodes in the same tree (ClassificationTreeTag)
    belonging to the node just saved.
    Align the tree.used_trees with the current situation.
    """

    # the node just saved
    node = instance

    # the node's tree (ClassificationTreeTag)
    tree = node.tag

    # TODO: I know there's a better way to do the following fetching

    # list of nodes in the tree, having equivalent_to relations
    tree_equivalents = ClassificationTreeNode.objects.filter(
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

