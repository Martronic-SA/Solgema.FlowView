from zope.interface import implements
from plone.memoize.view import memoize

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from interfaces import ISFWUtility
from Solgema.FlowView.settings import FlowViewSettings

class SFWUtility(BrowserView):
    """Information about the state of the portal
    """
    implements(ISFWUtility)

    @memoize
    def should_include(self, display_type):
        context = aq_inner(self.context)
        try:
            return self.enabled() and FlowViewSettings(context).display_type == display_type
        except TypeError:
            return False
            
    @memoize
    def enabled(self):
        utils = getToolByName(self.context, 'plone_utils')
        try:
            return utils.browserDefault(self.context)[1][0] == "flowview"
        except:
            return False
        
