# -*- encoding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.content import Container
from zope.interface import alsoProvides
from zope.interface import implements
from zope.component.hooks import getSite

from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.layout.navigation.interfaces import INavigationRoot

from plone.folder.ordered import CMFOrderedBTreeFolderBase
from Acquisition import aq_base, aq_inner, aq_parent
from Products.Archetypes.interfaces import IBaseObject

_marker = object()


class LanguageRootFolder(Container):
    """ Language root folder type that holds the shared and is navigation root
    """

    implements(ILanguageRootFolder, INavigationRoot)

    def __getattr__(self, name):
        try:
            return Container.__getattr__(self, name)
        except AttributeError:
            # Check if it's on shared folder
            # Search for the content on the shared folder
            portal = getSite()
            if name in portal:
                return portal.__getattr__(name)
            else:
                raise

    def _getOb(self, id, default=_marker):
        import pdb; pdb.set_trace()
        aliased = getSite()
        try:
            obj = aliased._getOb(id, default)
            if obj is default:
                if default is _marker:
                    raise KeyError(id)
                return default
            return aq_base(obj).__of__(self)
        except KeyError:
            return CMFOrderedBTreeFolderBase._getOb(self, id, default)

    def objectIds(self, spec=None, ordered=True):
        import pdb; pdb.set_trace()
        aliased = getSite()
        if spec is None:
            spec = ['ATDocument', 'ATFolder']
        aliased_objectIds = aliased.objectIds(spec)
        # Ordering should be taking care here
        return CMFOrderedBTreeFolderBase.objectIds(self, spec, ordered) + aliased_objectIds

    def __getitem__(self, key):
        import pdb; pdb.set_trace()
        aliased = getSite()
        try:
            obj = aliased.__getitem__(key)
            return aq_base(obj).__of__(self)
        except KeyError:
            return CMFOrderedBTreeFolderBase.__getitem__(self, key)


class LRFOrdering(object):
    """ Ordering of the language root folders
    """