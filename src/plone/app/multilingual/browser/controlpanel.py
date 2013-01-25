from zope.interface import Interface
from zope.interface import implementsOnly
from zope.schema import Choice
from zope.schema import Bool
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

from plone.app.form.validators import null_validator

from plone.fieldsets.fieldsets import FormFieldsets

from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.app.controlpanel.language import LanguageControlPanel as BasePanel
from plone.app.controlpanel.language import LanguageControlPanelAdapter
from plone.app.controlpanel.language import ILanguageSelectionSchema
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.protect import CheckAuthenticator

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

from zope.schema.interfaces import IVocabularyFactory

from plone.app.uuid.utils import uuidToObject

import json

from plone.app.multilingual import isLPinstalled
from plone.multilingual.interfaces import ILanguage

from Products.CMFPlone import PloneMessageFactory as _Plone
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.multilingual')


class IInitialCleanSiteSetupAdapter(Interface):

    set_default_language = Bool(
        title=_(u"heading_set_default_language",
                default=u"Set the default language"),
        description=_(
            u"description_set_default_language",
            default=(u"Set the default language on all content without "
                     u"language defined. This value is not stored so you need "
                     u"to check every time you want to run it")),
        default=False,
        required=False,
        )

    move_content_to_language_folder = Bool(
        title=_(u"heading_move_content_to_language_folder",
                default=u"Move root content to default language folder"),
        description=_(
            u"description_move_content_to_language_folder",
            default=(u"Move the content that is on the root folder to the "
                     u"default language folder. This value is not stored so "
                     u"you need to check every time you want to run it")),
        default=False,
        required=False,
        )

selector_policies = SimpleVocabulary(
    [SimpleTerm(value=u'closest', title=_(u'Search for closest translation in parent\'s content chain.')),
     SimpleTerm(value=u'dialog', title=_(u'Show user dialog with information about the available translations.'))
    ]
)


class IMultiLanguagePolicies(Interface):
    """ Interface for language policies - control panel fieldset
    """

    selector_lookup_translations_policy = Choice(
        title=_(u"heading_selector_lookup_translations_policy",
                default=u"The policy used to determine how the lookup for available "
                         "translations will be made by the language selector."),
        description=_(u"description_selector_lookup_translations_policy",
                      default=u"The default language used for the content "
                              u"and the UI of this site."),
        required=True,
        vocabulary=selector_policies
    )


class MultiLanguageExtraOptionsAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageExtraOptionsSchema)

    def __init__(self, context):
        super(MultiLanguageExtraOptionsAdapter, self).__init__(context)
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(
            IMultiLanguageExtraOptionsSchema)

    def get_filter_content(self):
        return self.settings.filter_content

    def set_filter_content(self, value):
        self.settings.filter_content = value

    def get_google_translation_key(self):
        return self.settings.google_translation_key

    def set_google_translation_key(self, value):
        self.settings.google_translation_key = value

    def get_redirect_babel_view(self):
        return self.settings.redirect_babel_view

    def set_redirect_babel_view(self, value):
        self.settings.redirect_babel_view = value

    google_translation_key = property(get_google_translation_key,
                              set_google_translation_key)

    filter_content = property(get_filter_content,
                              set_filter_content)

    redirect_babel_view = property(get_redirect_babel_view,
                                   set_redirect_babel_view)


class InitialCleanSiteSetupAdapter(LanguageControlPanelAdapter):
    implementsOnly(IInitialCleanSiteSetupAdapter)

    def get_set_default_language(self):
        return False

    def set_set_default_language(self, value):
        if value:
            SetupMultilingualSite(self.context).set_default_language_content()

    def get_move_content_to_language_folder(self):
        return False

    def set_move_content_to_language_folder(self, value):
        if value:
            SetupMultilingualSite(self.context).move_default_language_content()

    set_default_language = property(get_set_default_language,
                                    set_set_default_language)

    move_content_to_language_folder = property(
        get_move_content_to_language_folder,
        set_move_content_to_language_folder)


class MultiLanguagePoliciesAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguagePolicies)

    def __init__(self, context):
        super(MultiLanguagePoliciesAdapter, self).__init__(context)
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)

    def get_selector_lookup_translations_policy(self):
        return self.settings.selector_lookup_translations_policy

    def set_selector_lookup_translations_policy(self, value):
        self.settings.selector_lookup_translations_policy = value

    selector_lookup_translations_policy = property(get_selector_lookup_translations_policy,
                                                   set_selector_lookup_translations_policy)

selection = FormFieldsets(ILanguageSelectionSchema)
selection.label = _(u'Site languages')

extras = FormFieldsets(IMultiLanguageExtraOptionsSchema)
extras.label = _(u'Extra options')

policies = FormFieldsets(IMultiLanguagePolicies)
policies.label = _(u'Policies')

clean_site_setup = FormFieldsets(IInitialCleanSiteSetupAdapter)
clean_site_setup.label = _(u'Clean site setup')
clean_site_setup.description = _(u"""If you are installing PAM for the first
                                  time in a Plone site, either if it's on an
                                  existing or a brand new one you should run the
                                  following procedures in order to move the
                                  default site content to its right root
                                  language folder and be sure that all the
                                  content have the language attribute set up
                                  correctly. Previous to run them, please be
                                  sure that you have set up your site's
                                  languages in the 'Site languages' tab and have
                                  saved that setting. Finally, in case you have
                                  an existing Plone site with
                                  Products.LinguaPlone installed, please do not
                                  run this steps and refer directly to the
                                  'Migration' tab.""")


class LanguageControlPanel(BasePanel):
    """A modified language control panel, allows selecting multiple languages.
    """

    template = ViewPageTemplateFile('templates/controlpanel.pt')

    form_fields = FormFieldsets(selection, policies, extras, clean_site_setup)

    label = _("Multilingual Settings")
    description = _("All the configuration of P.A.M. If you want to set "
                    "the default language to all the content without language "
                    "and move all the content on the root folder to the "
                    "default language folder, go to Extra Options section ")
    form_name = _("Multilingual Settings")

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_save_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _Plone("Changes saved.")
            self._on_save(data)
        else:
            self.status = _Plone("No changes made.")
        setupTool = SetupMultilingualSite()
        output = setupTool.setupSite(self.context)
        self.status += output

    @form.action(_Plone(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(
            _Plone("Changes canceled."), type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''

    isLPinstalled = isLPinstalled


class MigrationView(BrowserView):
    """ The view for display the migration information, actions and results """
    __call__ = ViewPageTemplateFile('templates/migration.pt')

    isLPinstalled = isLPinstalled


class MigrationViewAfter(BrowserView):
    """ The view for display the migration information, actions and results """
    __call__ = ViewPageTemplateFile('templates/cleanup.pt')

    isLPinstalled = isLPinstalled


class multilingualMapViewJSON(BrowserView):
    """ Helper view to get json translations """

    def __call__(self):
        """ Get the JSON information about based on a nodeId
        """

        # We get the language we are looking for
        lang = ''
        tool = getToolByName(self.context, 'portal_languages', None)
        if 'lang' in self.request:
            lang = self.request['lang']

        if lang == '':
            lang = tool.getDefaultLanguage()

        # We want all or just the missing translations elements
        if 'all' in self.request:
            get_all = (self.request['all'] == 'true')
        else:
            get_all = True

        # Which is the root nodeId
        folder_path = ''
        if 'nodeId' in self.request:
            # We get the used UUID
            nodeId = (self.request['nodeId'])
            if (nodeId != 'root'):
                new_root = uuidToObject(nodeId)
                if ILanguage(new_root).get_language() == lang:
                    folder_path = '/'.join(new_root.getPhysicalPath())
        if folder_path == '':
            # We get the root folder
            root = getToolByName(self.context, 'portal_url')
            root = root.getPortalObject()
            folder_path = '/'.join(root.getPhysicalPath())

        self.request.response.setHeader("Content-type", "application/json; charset=utf-8")
        pcatalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        query['path'] = {'query': folder_path, 'depth': 1}
        query['sort_on'] = "sortable_title"
        query['sort_order'] = "ascending"
        query['Language'] = lang
        search_results = pcatalog.searchResults(query)
        resultat = {'id': 'root', 'name': folder_path, 'data': {}, 'children': []}
        supported_languages = tool.getSupportedLanguages()
        for sr in search_results:
            # We want to know the translated and missing elements
            translations = {}
            if 'TranslationGroup' in sr:
                # We look for the brain for each translation
                brains = pcatalog.unrestrictedSearchResults(TranslationGroup=sr['TranslationGroup'])
                languages = {}
                for brain in brains:
                    languages[brain.Language] = brain.UID
                for lang in supported_languages:
                    if lang in languages.keys():
                        translated_obj = uuidToObject(languages[lang])
                        translations[lang] = {'url': translated_obj.absolute_url(), 'title': translated_obj.getId()}
                    else:
                        url_to_create = sr.getURL() + "/@@create_translation?form.widgets.language"\
                            "=%s&form.buttons.create=1" % lang
                        translations[lang] = {'url': url_to_create, 'title': _(u'Not translated')}
            if get_all:
                resultat['children'].append({'id': sr['UID'], 'name': sr['Title'], 'data': translations, 'children': []})
            else:
                pass
        return json.dumps(resultat)


class multilingualMapView(BrowserView):
    """ The view for display the current multilingual map for the site """
    __call__ = ViewPageTemplateFile('templates/mmap.pt')

    def languages(self):
        langs = getUtility(IVocabularyFactory, name=u"plone.app.multilingual.vocabularies.AllAvailableLanguageVocabulary")
        tool = getToolByName(self.context, 'portal_languages', None)
        lang = tool.getDefaultLanguage()
        return {'default': lang, 'languages': langs(self.context)}

    def canonicals(self):
        """ We get all the canonicals and see which translations are missing """
        # Get the language
        tool = getToolByName(self.context, 'portal_languages', None)
        pcatalog = getToolByName(self.context, 'portal_catalog', None)
        languages = tool.getSupportedLanguages()
        num_lang = len(languages)
        # Get the canonicals
        # Needs to be optimized
        not_full_translations = []
        already_added_canonicals = []
        brains = pcatalog.searchResults(Language='all')
        for brain in brains:
            if not isinstance(brain.TranslationGroup, str):
                # is alone, with a Missing.Value
                missing_languages = [lang for lang in languages if lang != brain.Language]
                translations = [{'url': brain.getURL(), 'path': brain.getPath(), 'lang': brain.Language}]
                not_full_translations.append({'id': 'None',
                                              'last_url': brain.getURL(),
                                              'missing': missing_languages,
                                              'translated': translations})
            elif isinstance(brain.TranslationGroup, str):
                tg = brain.TranslationGroup
                brains_tg = pcatalog.searchResults(Language='all', TranslationGroup=tg)
                if len(brains_tg) < num_lang and tg not in already_added_canonicals:
                    translated_languages = [a.Language for a in brains_tg]
                    missing_languages = [lang for lang in languages if lang not in translated_languages]
                    translations = []
                    last_url = ''
                    for brain_tg in brains_tg:
                        last_url = brain_tg.getURL()
                        translations.append({'url': brain_tg.getURL(),
                                             'path': brain_tg.getPath(),
                                             'lang': brain_tg.Language})

                    not_full_translations.append({'id': tg,
                                              'last_url': last_url,
                                              'missing': missing_languages,
                                              'translated': translations})
                already_added_canonicals.append(tg)
        return not_full_translations

    isLPinstalled = isLPinstalled
