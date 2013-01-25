from zope.interface import Interface
from zope import schema
from plone.app.multilingual import _

SHARED_NAME = 'shared'


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


class IMultiLanguageExtraOptionsSchema(Interface):
    """ Interface for language extra options - control panel fieldset
    """

    redirect_babel_view = schema.Bool(
        title=_(
            u"heading_redirect_babel_view",
            default=u"Redirect on creation to babel view."),
        description=_(
            u"description_redirect_babel_view",
            default=(u"After creating a new translation redirecto to babel "
                       u"view")),
        default=True,
        required=False,
        )

    google_translation_key = schema.TextLine(
        title=_(
            u"heading_google_translation_key",
            default=u"Google Translation API Key"),
        description=_(
            u"description_google_translation_key",
            default=(u"Is a paying API in order to use google translation "
                       u"service")),
        required=False,
        )
