from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.dexterity.utils import createContentInContainer
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import ITranslationManager
from Products.CMFCore.utils import getToolByName

import transaction


def makeContent(context, portal_type, id='doc', **kw):
    context.invokeFactory(portal_type, id, **kw)
    return getattr(context, id)


def makeTranslation(content, language='en'):
    manager = ITranslationManager(content)
    manager.add_translation(language)
    return manager.get_translation(language)


def setup_pam_site_fixture(portal, languages):
        language_tool = getToolByName(portal, 'portal_languages')
        for lang in languages:
            language_tool.addSupportedLanguage(lang)
        workflowTool = getToolByName(portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(portal)


def setup_test_content(portal):

    atdoc = makeContent(portal['en'], 'Document', id='atdoc', title='EN doc')
    atdoc.setLanguage('en')
    atdoc_ca = makeTranslation(atdoc, 'ca')
    atdoc_ca.edit(title="CA doc", language='ca')

    dxdoc = createContentInContainer(portal['en'], "dxdoc", id="dxdoc", title='EN doc')
    ILanguage(dxdoc).set_language('en')
    dxdoc_ca = makeTranslation(dxdoc, 'ca')
    dxdoc_ca.title = "CA doc"
    ILanguage(dxdoc_ca).set_language('ca')

    transaction.commit()
