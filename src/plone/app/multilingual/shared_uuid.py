from Acquisition import aq_base, aq_chain

from zope.interface import implementer
from zope.component import adapter
import uuid

from plone.uuid.interfaces import IUUID, IAttributeUUID, ATTRIBUTE_NAME

from Products.Archetypes.config import UUID_ATTR
from archetypes.multilingual.interfaces import IArchetypesTranslatable
from plone.multilingualbehavior.interfaces import IDexterityTranslatable
from plone.app.multilingual.content.lrf import ILanguageRootFolder


@implementer(IUUID)
@adapter(IArchetypesTranslatable)
def referenceableUUID(context):
    child = context
    for element in aq_chain(context):
        if hasattr(child, '_v_is_shared_content') and ILanguageRootFolder.providedBy(element):
            uid = getattr(aq_base(context), UUID_ATTR, None)
            return uid + '-' + element.id if uid is not None else None
        child = element
    return getattr(aq_base(context), UUID_ATTR, None)


@implementer(IUUID)
@adapter(IDexterityTranslatable)
def attributeUUID(context):
    child = context
    for element in aq_chain(context):
        if hasattr(child, '_v_is_shared_content') and ILanguageRootFolder.providedBy(element):
            uid = getattr(aq_base(context), UUID_ATTR, None)
            return uid + '-' + element.id if uid is not None else None
        child = element
    return getattr(context, ATTRIBUTE_NAME, None)
