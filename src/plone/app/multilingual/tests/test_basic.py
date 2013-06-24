import unittest2 as unittest
from AccessControl import Unauthorized

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.dexterity.utils import createContentInContainer
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import setRoles

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.multilingual.tests.utils import setup_pam_site_fixture
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT


import transaction


class PAMIntTestHelperViews(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setup_pam_site_fixture(self.portal, ['ca', 'es'])

    def test_add_dx_content_no_translatable_to_a_rlf(self):
        dxdocnt = createContentInContainer(self.portal['en'], "dxdocnt", id="dxdocnt", title='Not translatable in a LRF')
        self.assertEqual(dxdocnt.language, 'en')
