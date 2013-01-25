from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.multilingual.browser.vocabularies import translated_urls

from plone.multilingualbehavior.interfaces import ILanguageIndependentField

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema

from plone.app.i18n.locales.interfaces import ISelectorAdapter


class MultilingualEditForm(DefaultEditForm):

    babel = ViewPageTemplateFile("templates/dexterity_edit.pt")

    def gtenabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.google_translation_key != ''

    def languages(self):
        """ Deprecated """
        context = aq_inner(self.context)

        ls = ISelectorAdapter(context, self.request)
        results = ls.languages()

        translations = translated_urls(context)

        # We want to see the babel_view
        append_path = ('', 'babel_view',)

        non_viewable = set()
        for data in results:
            code = str(data['code'])
            data['translated'] = code in translations.keys()

            appendtourl = '/'.join(append_path)

            if data['translated']:
                # XXX we should check if it has permission
                trans = translations[code]
                data['url'] = trans + appendtourl
            else:
                non_viewable.add((data['code']))

        # filter out non-viewable items
        results = [r for r in results if r['code'] not in non_viewable]
        return results

    def portal_url(self):
        portal_tool = getToolByName(self.context, 'portal_url', None)
        if portal_tool is not None:
            return portal_tool.getPortalObject().absolute_url()
        return None

    def render(self):
        self.request['disable_border'] = True

        for field in self.fields.keys():
            if field in self.schema:
                if ILanguageIndependentField.providedBy(self.schema[field]):
                    self.widgets[field].addClass('languageindependent')
            # With plone.autoform, fieldnames from additional schematas
            # reference their schema by prefixing their fieldname
            # with schema.__identifier__ and then a dot as a separator
            # See autoform.txt in the autoform package
            if '.' in field:
                schemaname, fieldname = field.split('.')
                for schema in self.additionalSchemata:
                    if schemaname == schema.__identifier__ and fieldname in schema:
                        if ILanguageIndependentField.providedBy(\
                            schema[fieldname]):
                            self.widgets[field].addClass('languageindependent')
        self.babel_content = super(MultilingualEditForm, self).render()
        return self.babel()

DefaultMultilingualEditView = layout.wrap_form(MultilingualEditForm)
