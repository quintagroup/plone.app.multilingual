# -*- encoding: utf-8 -*-

from Acquisition import aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID
from zope.component.hooks import getSite


def reindex_neutral(obj, event):
    # we need to look for the parent that is already indexed
    if IPloneSiteRoot.providedBy(obj):
        return
    parent = aq_parent(obj)
    site = getSite()
    language_tool = getToolByName(site, 'portal_languages')
    language_infos = language_tool.supported_langs
    if IPloneSiteRoot.providedBy(parent):
        # It's plone site root we need to look at LRF
        for language_info in language_infos:
            lrf_to_reindex = getattr(parent, language_info, None)
            to_reindex = getattr(lrf_to_reindex, obj.id, None)
            if to_reindex is not None:
                to_reindex.reindexObject()
    else:
        content_id = IUUID(parent).split('-')[0]
        pc = getToolByName(site, 'portal_catalog')
        for language_info in language_infos:
            brains = pc.unrestrictedSearchResults(UID=content_id + '-' + language_info)
            if len(brains):
                obj.unrestrictedTraverse(brains[0].getPath() + '/' + obj.id).reindexObject()
    return
