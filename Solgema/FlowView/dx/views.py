from Solgema.FlowView.browser.views.flowview import FlowView
from plone.app.contenttypes.browser.folder import FolderView
        
class FlowViewDX(FlowView, FolderView):

    def __init__(self, context, request):
        super(FlowViewDX, self).__init__(context, request)

