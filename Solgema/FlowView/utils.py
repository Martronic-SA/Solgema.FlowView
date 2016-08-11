from zope.interface import implements
from zope.component import getUtilitiesFor
from zope.component import getUtility
from Solgema.FlowView.interfaces import IFlowViewDisplayType
from zope.component import getMultiAdapter
from settings import FlowViewSettings
from interfaces import IFlowViewSettings
from Solgema.FlowView.config import DISPLAY_NAME_VIEW_PREFIX
from vocabularies import FlowViewDisplayTypeVocabulary


def getDisplayAdapter(context, request, display_type=None):
    if display_type is None:
        display_type = FlowViewSettings(context).display_type

    possible_types = FlowViewDisplayTypeVocabulary(context)
    if display_type not in possible_types.by_value.keys():
        display_type = IFlowViewSettings['display_type'].default

    return getMultiAdapter(
        (context, request),
        name=DISPLAY_NAME_VIEW_PREFIX + display_type
    )


def getDisplayType(name):
    return getUtility(IFlowViewDisplayType, name=DISPLAY_NAME_VIEW_PREFIX + name)


def getAllDisplayTypes():
    utils = list(getUtilitiesFor(IFlowViewDisplayType))
    utils = sorted(utils, key=lambda x: x[1].name)
    return [utility for name, utility in utils]


def createSettingsFactory(schema):
    class Settings(FlowViewSettings):
        implements(schema)

        def __init__(self, context, interfaces=[schema]):
            super(Settings, self).__init__(context, interfaces)

    return Settings
