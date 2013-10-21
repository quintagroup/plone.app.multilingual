# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.multilingual import upgrades
from plone.app.multilingual.testing import \
    PLONEAPPMULTILINGUAL_INTEGRATION_TESTING
from plone.multilingual.interfaces import ILanguage

import unittest2 as unittest
import transaction


class PAM_1_to_2_TestCase(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.ltool = getToolByName(self.portal, 'portal_languages')

        shared_id = upgrades.SHARED_NAME
        self.portal.invokeFactory('Folder', shared_id, title=u"Shared")
        self.portal[shared_id].invokeFactory('Folder', 'a1', title=u"A1")
        self.portal[shared_id].invokeFactory('Folder', 'b1', title=u"B1")

    def test_migration(self):
        self.ltool.addSupportedLanguage('de')
        self.portal.invokeFactory('Folder', 'de', title=u"Deutsch")
        ILanguage(self.portal['de']).set_language('de')
        self.portal['de'].invokeFactory('Folder', 'oel', title=u"Öl")
        self.portal['de'].invokeFactory('Folder', 'aether', title=u"Äther")

        self.ltool.addSupportedLanguage('fr')
        self.portal.invokeFactory('Folder', 'fr', title=u"French")
        ILanguage(self.portal['fr']).set_language('fr')
        self.portal['fr'].invokeFactory('Folder', 'petrole', title=u"pétrole")
        self.portal['fr'].invokeFactory('Folder', 'ether', title=u"Ether")

        transaction.savepoint()

        # Validate setup
        self.assertIn('de', self.portal)
        self.assertEqual(ILanguage(self.portal['de']).get_language(), 'de')
        self.assertIn('fr', self.portal)
        self.assertEqual(ILanguage(self.portal['fr']).get_language(), 'fr')
        self.assertIn(upgrades.SHARED_NAME, self.portal)
        self.assertIn('a1', self.portal[upgrades.SHARED_NAME])
        self.assertIn('b1', self.portal[upgrades.SHARED_NAME])
        self.assertEqual(ILanguage(
            self.portal[upgrades.SHARED_NAME]['a1']).get_language(), '')
        self.assertEqual(ILanguage(
            self.portal[upgrades.SHARED_NAME]['b1']).get_language(), '')

        self.assertEqual(self.portal['de'].portal_type, 'Folder')
        self.assertEqual(self.portal['fr'].portal_type, 'Folder')
        self.assertEqual(
            self.portal[upgrades.SHARED_NAME].portal_type, 'Folder')

        # Now run migration
        upgrades.migration_pam_1_to_2(self.portal)

        # New LRF items
        self.assertIn('de', self.portal)
        self.assertEqual(ILanguage(self.portal['de']).get_language(), 'de')
        self.assertIn('fr', self.portal)
        self.assertEqual(ILanguage(self.portal['fr']).get_language(), 'fr')
        self.assertEqual(self.portal['de'].portal_type, 'LRF')
        self.assertEqual(self.portal['fr'].portal_type, 'LRF')

        # Is migrated content in new LRF folder?
        self.assertIn('oel', self.portal['de'])
        self.assertIn('aether', self.portal['de'])
        self.assertEqual(self.portal['de']['oel'].portal_type, 'Folder')
        self.assertEqual(self.portal['de']['aether'].portal_type, 'Folder')
        self.assertEqual(ILanguage(self.portal['de']).get_language(), 'de')
        self.assertEqual(self.portal['fr']['petrole'].portal_type, 'Folder')
        self.assertEqual(self.portal['fr']['ether'].portal_type, 'Folder')
        self.assertEqual(ILanguage(self.portal['fr']).get_language(), 'fr')

        # Shared items should be on root
        self.assertIn('a1', self.portal)
        self.assertIn('b1', self.portal)
        self.assertEqual(ILanguage(self.portal['a1']).get_language(), '')
        self.assertEqual(ILanguage(self.portal['b1']).get_language(), '')

        # Old items should have been removed
        self.assertNotIn(upgrades.OLD_PREFIX + 'de', self.portal)
        self.assertNotIn(upgrades.OLD_PREFIX + 'fr', self.portal)
        self.assertNotIn(upgrades.SHARED_NAME, self.portal)
        self.assertNotEqual(self.portal['de'].portal_type, 'Folder')
        self.assertNotEqual(self.portal['fr'].portal_type, 'Folder')

    def test_migration_of_combined_language_codes(self):
        # Use combined language codes
        self.ltool.use_combined_language_codes = True

        self.ltool.addSupportedLanguage('de-at')
        self.portal.invokeFactory('Folder', 'de-at', title=u"Deutsch")
        ILanguage(self.portal['de-at']).set_language('de-at')
        self.portal['de-at'].invokeFactory('Folder', 'oel', title=u"Öl")
        self.portal['de-at'].invokeFactory('Folder', 'aether', title=u"Äther")

        self.ltool.addSupportedLanguage('fr-fr')
        self.portal.invokeFactory('Folder', 'fr-fr', title=u"French")
        ILanguage(self.portal['fr-fr']).set_language('fr-fr')
        self.portal['fr-fr'].invokeFactory('Folder', 'petrole',
                                           title=u"pétrole")
        self.portal['fr-fr'].invokeFactory('Folder', 'ether',
                                           title=u"Ether")

        transaction.savepoint()

        # Validate setup
        self.assertIn('de-at', self.portal)
        self.assertEqual(
            ILanguage(self.portal['de-at']).get_language(), 'de-at')
        self.assertIn('fr-fr', self.portal)
        self.assertEqual(
            ILanguage(self.portal['fr-fr']).get_language(), 'fr-fr')
        self.assertIn(upgrades.SHARED_NAME, self.portal)
        self.assertIn('a1', self.portal[upgrades.SHARED_NAME])
        self.assertIn('b1', self.portal[upgrades.SHARED_NAME])
        self.assertEqual(ILanguage(
            self.portal[upgrades.SHARED_NAME]['a1']).get_language(), '')
        self.assertEqual(ILanguage(
            self.portal[upgrades.SHARED_NAME]['b1']).get_language(), '')

        self.assertEqual(self.portal['de-at'].portal_type, 'Folder')
        self.assertEqual(self.portal['fr-fr'].portal_type, 'Folder')
        self.assertEqual(
            self.portal[upgrades.SHARED_NAME].portal_type, 'Folder')

        # Now run migration
        upgrades.migration_pam_1_to_2(self.portal)

        # New LRF items
        self.assertIn('de-at', self.portal)
        self.assertEqual(
            ILanguage(self.portal['de-at']).get_language(), 'de-at')
        self.assertIn('fr-fr', self.portal)
        self.assertEqual(
            ILanguage(self.portal['fr-fr']).get_language(), 'fr-fr')
        self.assertEqual(self.portal['de-at'].portal_type, 'LRF')
        self.assertEqual(self.portal['fr-fr'].portal_type, 'LRF')

        # Is migrated content in new LRF folder?
        self.assertIn('oel', self.portal['de-at'])
        self.assertIn('aether', self.portal['de-at'])
        self.assertEqual(self.portal['de-at']['oel'].portal_type, 'Folder')
        self.assertEqual(self.portal['de-at']['aether'].portal_type, 'Folder')
        self.assertEqual(
            ILanguage(self.portal['de-at']).get_language(), 'de-at')
        self.assertEqual(self.portal['fr-fr']['petrole'].portal_type, 'Folder')
        self.assertEqual(self.portal['fr-fr']['ether'].portal_type, 'Folder')
        self.assertEqual(
            ILanguage(self.portal['fr-fr']).get_language(), 'fr-fr')

        # Shared items should be on root
        self.assertIn('a1', self.portal)
        self.assertIn('b1', self.portal)
        self.assertEqual(ILanguage(self.portal['a1']).get_language(), '')
        self.assertEqual(ILanguage(self.portal['b1']).get_language(), '')

        # Old items should have been removed
        self.assertNotIn(upgrades.OLD_PREFIX + 'de-at', self.portal)
        self.assertNotIn(upgrades.OLD_PREFIX + 'fr-fr', self.portal)
        self.assertNotIn(upgrades.SHARED_NAME, self.portal)
        self.assertNotEqual(self.portal['de-at'].portal_type, 'Folder')
        self.assertNotEqual(self.portal['fr-fr'].portal_type, 'Folder')
