import logging
from zope.component import getUtilitiesFor
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Solgema.FlowView.interfaces import IFlowViewSettings
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.vocabularies.catalog import SearchableTextSource
from plone.app.vocabularies.catalog import parse_query
from plone.app.customerize import registration
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserView, IBrowserPage
from Solgema.FlowView.interfaces import IFlowViewMarker
from Solgema.FlowView.interfaces import IFlowViewDisplayType
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from Solgema.FlowView.config import _
LOG = logging.getLogger(__name__)

class PTGVocabulary(SimpleVocabulary):

    def __init__(self, terms, *interfaces, **config):
        super(PTGVocabulary, self).__init__(terms, *interfaces)
        if 'default' in config:
            self.default = config['default']
        else:
            self.default = None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.default]
        except:
            raise LookupError(value)

def FlowViewDisplayTypeVocabulary(context):
    terms = []
    utils = list(getUtilitiesFor(IFlowViewDisplayType))
    for name, utility in sorted(utils, key=lambda x: x[1].name):
        if utility.name:
            name = utility.name or name
            terms.append(SimpleTerm(name, name, utility.description))

    return PTGVocabulary(terms,
                default=IFlowViewSettings['display_type'].default)

class FlowViewSearchableTextSource(SearchableTextSource):

    def search(self, query_string):
        results = super(FlowViewSearchableTextSource, self).search(query_string)
        utils = getToolByName(self.context, 'plone_utils')
        query = self.base_query.copy()
        if query_string == '':
            if self.default_query is not None:
                query.update(parse_query(self.default_query, self.portal_path))
        else:
            query.update(parse_query(query_string, self.portal_path))
        try:
            results = self.catalog(**query)
        except:
            results = []

        utils = getToolByName(self.context, 'plone_utils')
        for result in results:
            try:
                if utils.browserDefault(result.getObject())[1][0] ==\
                                                        "flowview":
                    yield result.getPath()[len(self.portal_path):]
            except:
                pass


class FlowViewSearchabelTextSourceBinder(SearchableTextSourceBinder):

    def __init__(self):
        self.query = {'object_provides': IFlowViewMarker.__identifier__}
        self.default_query = 'path:'

    def __call__(self, context):
        return FlowViewSearchableTextSource(
            context,
            base_query=self.query.copy(),
            default_query=self.default_query
        )

@implementer(IVocabularyFactory)
def FlowViewsVocabulary( context ):
    base = [SimpleTerm('content', 'content', _(u"label_content", default=u"Content")),
            SimpleTerm('summary', 'summary', _(u"label_summary", default=u"Summary")),
            SimpleTerm('banner', 'banner', _(u"label_banner", default=u"Banner")),
            SimpleTerm('custom', 'custom', _(u"label_custom", default=u"Custom"))]
    views = registration.getViews(IBrowserRequest)
    for name in [a.name for a in views if IFlowViewMarker in a.required and a.name not in ['flowview-settings', 'flowview-content']]:
        base.append(SimpleTerm(name,name,_(name)))
    return SimpleVocabulary(base)
