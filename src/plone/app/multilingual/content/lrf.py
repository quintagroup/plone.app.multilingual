# -*- encoding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.content import Container
from zope.interface import alsoProvides
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.utils import getToolByName

from plone.folder.interfaces import IExplicitOrdering
from zope.component.hooks import getSite

from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.layout.navigation.interfaces import INavigationRoot

from plone.folder.ordered import CMFOrderedBTreeFolderBase
from Acquisition import aq_base, aq_inner, aq_parent
from Products.Archetypes.interfaces import IBaseObject
from BTrees.OIBTree import union
from Products.ZCatalog.Lazy import LazyMap
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.folder.default import DefaultOrdering

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from plone.i18n.locales.languages import _languagelist
from plone.i18n.locales.languages import _combinedlanguagelist

_marker = object()


class LanguageRootFolder(Container):
    """ Language root folder type that holds the shared and is navigation root
    """

    implements(ILanguageRootFolder, INavigationRoot, IPloneSiteRoot)

    def has_key(self, id):
        """Indicates whether the folder has an item by ID.
        """
        if CMFOrderedBTreeFolderBase.has_key(self, id):
            return True
        return id in getSite()

    hasObject = has_key

    def __contains__(self, name):
        return self.has_key(name)

    def objectMap(self):
        # Returns a tuple of mappings containing subobject meta-data.
        return LazyMap(lambda (k, v):
                       {'id': k, 'meta_type': getattr(v, 'meta_type', None)},
                       self._tree.items(), self._count())


    def __getattr__(self, name):
        try:
            return Container.__getattr__(self, name)
        except AttributeError:
            # Check if it's on shared folder
            # Search for the content on the shared folder
            portal = getSite()
            if portal is not None and name in portal:
                # XXX Check that is content

                return aq_base(getattr(portal, name)).__of__(self)
            else:
                raise

    def _getOb(self, id, default=_marker):
        aliased = getSite()
        try:
            if aliased:
                obj = aliased._getOb(id, default)
                if obj is default:
                    if default is _marker:
                        raise KeyError(id)
                    return default
                return aq_base(obj).__of__(self)
            else:
                return CMFOrderedBTreeFolderBase._getOb(self, id, default)
        except KeyError:
            return CMFOrderedBTreeFolderBase._getOb(self, id, default)

    def objectIds(self, spec=None, ordered=True):
        aliased = getSite()
        # XXX : need to find better aproach
        try:
            # We do a try to avoid problems removing the portal
            # if spec is None:
            #     # XXX
            #     spec = ['ATDocument', 'ATFolder']
            if aliased is not None:
                to_remove = []
                aliased_objectIds = aliased.objectIds(spec)
                for id in aliased_objectIds:
                    if id in _languagelist or id in _combinedlanguagelist:
                        to_remove.append(id)
                        
                for id in to_remove:
                    aliased_objectIds.remove(id)
            else:
                aliased_objectIds = ()

        except AttributeError:
            # Ordering should be taking care here
            aliased_objectIds = ()

        own_elements = CMFOrderedBTreeFolderBase.objectIds(self, spec, False)

        if len(own_elements) == 0 and aliased_objectIds:
            return aliased_objectIds
        else:
            return own_elements + aliased_objectIds


    def __getitem__(self, key):
        aliased = getSite()
        try:
            obj = aliased.__getitem__(key)
            return aq_base(obj).__of__(self)
        except KeyError:
            return CMFOrderedBTreeFolderBase.__getitem__(self, key)


class LRFOrdering(DefaultOrdering):
    """ This implementation checks if there is any object that is not on the list
    in case its a shared object so you can move. """

    implements(IExplicitOrdering)
    adapts(ILanguageRootFolder)

    def idsInOrder(self):
        """ see interfaces.py """
        to_renew = [x for x in self.context.objectIds() if x not in self._pos().keys()]
        to_remove = [x for x in self._pos().keys() if x not in self.context.objectIds()]
        for id in to_renew:
            self.notifyAdded(id)
        for id in to_remove:
            self.notifyRemoved(id)
        return list(self._order())

