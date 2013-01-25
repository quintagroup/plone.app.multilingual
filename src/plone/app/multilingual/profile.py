from zope.interface import implements

from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as INonQ


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [
            u'plone.multilingual:default',
            u'plone.multilingual:uninstall',
            u'archetypes.multilingual:default',
            ]

class HiddenProducts(object):
    implements(INonQ)

    def getNonInstallableProducts(self):
        return [
            u'plone.multilingual:default',
            u'archetypes.multilingual:default',
            ]