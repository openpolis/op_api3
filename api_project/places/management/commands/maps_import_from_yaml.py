# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from optparse import make_option
import logging
import yaml
from places.models import ClassificationTreeNode, ClassificationTreeTag, Place

__author__ = 'guglielmo'



class Command(BaseCommand):
    """
    Import a tree from a --yaml-file into the ClassificationTreeNode,
    starting from the node identified by the
    --place-slug and --tag-slug parameters.

    The --tag-slug is used to assign a tag to the whole tree

    If --place-slug is not given, the tree is added as root,


    YML sample::

        - europa-continent:
          - italia-nation:
            - nord-macroregion:
              - piemonte-region>istat-reg
              - lombardia-region>istat-reg
            - centro-macroregion:
              - toscana-region>istat-reg
              - lazio-region>istat-reg
            - sud-macroregion:
              - campania-region>istat-reg
              - sicilia-region>istat-reg

    the ``place_slug>tag_slug`` syntax is used in case of equivalent_to relations

    it can be used only in tree leaves

    it means that an *equivalent node* must be inserted in the tree
    the place should be null, and the equivalent_to attribute should point
    to the node identified by ``place_slug`` and ``tag_slug``, after splitting them
    """
    help = "Import a tree from a yaml file, using a give tag, under a specified node (or as root)"

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual import is made.'),
        make_option('--yaml-file',
                    dest='yamlfile',
                    default='./tree.yml',
                    help='Select yaml file to use. Relative paths '+
                         'from project\'s root can be used.'),
        make_option('--place-slug',
                    dest='placeslug',
                    default='',
                    help='Slug of the place to identify the node '+
                         'to add the tree under (i.e: italia-nation). '+
                         'Leave blank to add to root level. '+
                         'The corresponding ClassificationTreeNode instance '+
                         'must already exist.'
                    ),
        make_option('--tag-slug',
                    dest='tagslug',
                    default='',
                    help="Required. Tag slug of the tree. The corresponding " +
                         "ClassificationTreeTag instance must already exist. "
                    ),

    )

    logger = logging.getLogger('management')

    def handle(self, *args, **options):

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        f_yaml = open(options['yamlfile'], 'r')
        tree = yaml.load(f_yaml.read())
        place_slug = options['placeslug']
        tag_slug = options['tagslug']

        node = None
        if place_slug:
            try:
                node = ClassificationTreeNode.objects.get(place__slug=place_slug, tag__slug=tag_slug)
            except ObjectDoesNotExist:
                raise Exception(
                    "Node not found for place: {0}, tag: {0}.".format(
                        place_slug, tag_slug
                    )
                )

        tree_tag = ClassificationTreeTag.objects.get(slug=tag_slug)

        self.add_tree(tree, node, tree_tag)
        f_yaml.close()

    ##
    # generic recursive method to add elements to tree
    ##
    def add_tree(self, tree, parent_node, tree_tag):
        for element in tree:
            if isinstance(element, dict):
                for key, subtree in element.iteritems():
                    self.logger.info(u"{0}:{1}".format(parent_node,key))
                    node = self.add_node_to_mptt(key, tree_tag, parent_node)
                    self.add_tree(subtree, node, tree_tag)
            else:
                key = element
                self.logger.info(u"{0}:{1}".format(parent_node, key))
                self.add_node_to_mptt(key, tree_tag, parent_node)

    ##
    # methods binding to the real MPTT tree instance (ClassificationTreeNode)
    ##
    def add_node_to_mptt(self, key, tree_tag, parent_node=None):
        """
        Add an mptt tree element to a given node.

        Split the key, to check equivalent_to relations.
        """
        try:
            (key, eq_tree_tag_slug) = key.split('>')
        except:
            eq_tree_tag_slug = None

        if eq_tree_tag_slug:
            # add a node with null place reference,
            # and non-null equivalent_to reference
            equivalent_node = ClassificationTreeNode.objects.get(
                place__slug=key, tag__slug=eq_tree_tag_slug
            )
            n = ClassificationTreeNode(
                tag=tree_tag,
                equivalent_to=equivalent_node
            )
        else:
            # add a standard node with non-null place reference
            try:
                place = Place.objects.get(slug=key)
            except:
                raise Exception("Place with slug {0} must exist".format(
                    key
                ))
            n = ClassificationTreeNode(
                place=place, tag=tree_tag,
            )

        ClassificationTreeNode.objects.insert_node(n, parent_node)
        n.save()
        return n
