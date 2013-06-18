from Products.CMFCore.utils import getToolByName
import logging

PROFILE_ID = 'profile-plone.app.multilingual:default'


def upgrade_1_to_2(context, logger=None):
    """ Reload configuration registry """

    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('plone.app.multilingual')

    # Re-run profile installation
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')
    logger.info('Created new configuration registry options')
