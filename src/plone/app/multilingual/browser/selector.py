from ZTUtils import make_query
from zope.component import queryAdapter
from plone.multilingual.interfaces import ITG
from plone.multilingual.interfaces import NOTG
from plone.app.i18n.locales.browser.selector import SelectorAdapter
from zope.component.hooks import getSite
from zope.interface import implements
from plone.app.i18n.locales.interfaces import ISelectorAdapter



def addQuery(request, url, exclude=tuple(), **extras):
    """Adds the incoming GET query to the end of the url
    so that is propagated through the redirect hoops
    """
    formvariables = {}
    for k, v in request.form.items():
        if k not in exclude:
            if isinstance(v, unicode):
                formvariables[k] = v.encode('utf-8')
            else:
                formvariables[k] = v
    formvariables.update(extras)
    try:
        if len(formvariables) > 0:
            url += '?' + make_query(formvariables)
    # Again, LinguaPlone did this try/except here so I'm keeping it.
    except UnicodeError:
        pass
    return url


def getPostPath(context, request):
    """Finds the path to be added at the end of a context.

    This is useful because you might have a view or even something more long
    (form and widget traversing) at the very end of the absolute_url
    of a translated item.
    When you get the translated item absolute_url,
    you want to also have the eventual views etc ported over:
    this function does that.
    """
    # This is copied over from LinguaPlone
    # because there's a lot of knowledge embed in it.

    # We need to find the actual translatable content object. As an
    # optimization we assume it is within the last three segments.
    path = context.getPhysicalPath()
    path_info = request.get('PATH_INFO', '')
    match = [ p for p in path[-3:] if p ]
    current_path = [ pi for pi in path_info.split('/') if pi ]
    append_path = []
    stop = False
    while current_path and not stop:
        check = current_path.pop()
        if check == 'VirtualHostRoot' or check.startswith('_vh_'):
            # Once we hit a VHM marker, we should stop
            break
        if check not in match:
            append_path.insert(0, check)
        else:
            stop = True
    if append_path:
        append_path.insert(0, '')
    return "/".join(append_path)


NOT_TRANSLATED_YET_TEMPLATE = '/not_translated_yet'


class LanguageSelectorPAM(SelectorAdapter):
    """Language selector for translatable content.
    """

    implements(ISelectorAdapter)

    def __init__(self, context):
        super(LanguageSelectorPAM, self).__init__(context)
        self.translation_group = queryAdapter(context, ITG)
        if self.translation_group is None:
            self.translation_group = NOTG

    def setRequest(self, request):
        super(LanguageSelectorPAM, self).setRequest(request)
        self.query_extras = {}
        post_path = getPostPath(self.context, request)
        if post_path:
            self.query_extras['post_path'] = post_path

    def getTGUrl(self):
        portal_url = getSite().absolute_url()
        return portal_url + '/@@multilingual-selector/' + self.translation_group

    def urlForLanguage(self, code):
        return addQuery(self.request, self.getTGUrl() + '/' + code, **self.query_extras)
