from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import ILanguage, ITranslatable
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.indexer import indexer

from plone.app.content.browser.foldercontents import (FolderContentsView,
                                                     FolderContentsTable)
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema, SHARED_NAME
from Acquisition import aq_inner
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IPloneSiteRoot
from App.special_dtml import DTMLFile

from plone.i18n.locales.languages import _languagelist


NO_FILTER = ['Language', 'UID', 'id', 'getId']
_enabled = []


def language_filter(query):

    if query.get('Language') == 'all':
        del query['Language']
        return
    for key in NO_FILTER:    # any "nofilter" indexing prevent mangling
        if key in query:
            return
    site = getSite()
    languageTool = getToolByName(site, 'portal_languages', None)
    if languageTool is None:
        return
    query['Language'] = [languageTool.getPreferredLanguage(),
                         LANGUAGE_INDEPENDENT]
    old_path = query.get('path', None)
    # In case is a depth path search
    if isinstance(old_path, dict) and 'query' in old_path and IPloneSiteRoot.providedBy(site):
        old_path_url = old_path['query']
        # We are going to check if is language root
        root_path = '/'.join(site.getPhysicalPath())

        # Check is a language root folder to add the shared folder
        if old_path['query'].split('/')[-1] in _languagelist:
            old_path['query'] = [old_path_url, root_path + '/' + SHARED_NAME]

        # Check if its shared folder to add the root path
        #elif old_path['query'].split('/')[-1] == SHARED_NAME:
        #    old_path['query'] = [old_path_url, root_path + '/' + languageTool.getPreferredLanguage()]


def AlreadyApplied(patch):
    if patch in _enabled:
        return True
    _enabled.append(patch)
    return False


def I18nAwareCatalog():
    # Patches the catalog tool to filter languages
    if AlreadyApplied('I18nAwareCatalog'):
        return

    def searchResults(self, REQUEST=None, **kw):
        if REQUEST is not None and kw.get('Language', '') != 'all':
            language_filter(REQUEST)
        else:
            language_filter(kw)
        return self.__pam_old_searchResults(REQUEST, **kw)

    CatalogTool.__pam_old_searchResults = CatalogTool.searchResults
    CatalogTool.searchResults = searchResults
    CatalogTool.__call__ = searchResults
    CatalogTool.manage_catalogView = DTMLFile('www/catalogView', globals())


try:
    # Check if there is a patch applied by LinguaPlone
    from Products.LinguaPlone import patches
except ImportError:
    pass
    # We try to not apply catalog patch
    # I18nAwareCatalog()

