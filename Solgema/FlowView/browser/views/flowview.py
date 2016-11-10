import logging
from Products.Five.browser import BrowserView
try:
    from plone.app.contenttypes.browser.folder import FolderView
except:
    FolderView = BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from Solgema.FlowView.utils import getDisplayAdapter
from Products.CMFCore.utils import getToolByName
from zope.contentprovider.interfaces import IContentProvider
from Solgema.FlowView.interfaces import IFlowViewSettings, IFlowViewMarker
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.contentprovider.interfaces import ITALNamespaceData
from zope.contentprovider.provider import ContentProviderBase
from zope.interface import implements, alsoProvides, directlyProvides, Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope import schema
from zope.component.hooks import getSite
from Products.Five.utilities import marker
try:
    from plone.dexterity.interfaces import IDexterityContainer, IDexterityContent
    from plone.namedfile.scaling import ImageScaling
    has_dx = True
except:
    has_dx = False
try:
    from collective.plonetruegallery.utils import getGalleryAdapter
    hasTrueGallery = True
except:
    hasTrueGallery = False
LOG = logging.getLogger(__name__)

def jsbool(val):
    return str(val).lower()

class BaseFlowView(BrowserView):

    template = ViewPageTemplateFile('layout.pt')

    def __init__(self, context, request):
        super(BaseFlowView, self).__init__(context, request)
        
    @property
    def macros(self):
        return self.template.macros

    def render(self):
        return self.template()

class FlowView(FolderView):

    name = None
    description = None
    schema = None
    userWarning = None
    staticFilesRelative = '++resource++solgemaflowview.resources'
    contentclass = 'page'
    text = False

    def __init__(self, context, request):
        super(FlowView, self).__init__(context, request)
        self.settings = IFlowViewSettings(context)
        portal_state = getMultiAdapter((context, request),
                                        name='plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.staticFiles = "%s/%s" % (self.portal_url,
                                      self.staticFilesRelative)
        if hasTrueGallery:
            self.adapter = getGalleryAdapter(self.context, self.request)

    def css(self):
        return ""

    def contentStyle(self):
        out = []
        if getattr(self.settings, 'height', None):
            out.append('height:'+str(self.settings.height)+'px')
        return '; '.join(out)

    def mainClass(self):
        backnextClass = self.settings.use_backnext and ' backnext_enabled' or ''
        borderClass = getattr(self.settings, 'showBorder', True) and ' showBorder' or ''
        return 'useFlowtabs '+self.settings.effect+' '+self.settings.tab_content+backnextClass+borderClass
    
    def padding(self):
        pad = getattr(self.settings, 'flowPadding', 15)
        if pad:
            return str(pad)+'px'
        return '0'

    @memoize
    def get_start_image_index(self):
        if hasTrueGallery and 'start_image' in self.request:
            si = self.request.get('start_image', '')
            images = self.adapter.cooked_images
            for index in range(0, len(images)):
                if si == images[index]['title']:
                    return index
        return 0

    start_image_index = property(get_start_image_index)

    @memoize
    def number_of_items(self):
        if IATTopic.providedBy(self.context):
            return len(self.context.queryCatalog())
        return len(self.context.getFolderContents())
        
    @property
    def showTitle(self):
        return getattr(self.settings, 'showTitle', True)
        
    @property
    def showDescription(self):
        return getattr(self.settings, 'showDescription', True)

    def javascript(self):
        txt = ["""<script type="text/javascript">""",]
        if getattr(self.settings, 'effect', None) == 'custom' and getattr(self.settings, 'custom_effect', None):
            txt.append(self.settings.custom_effect)
        txt.append(self.activateFlowView())
        if getattr(self.settings, 'invocation_code', None):
            txt.append(self.settings.invocation_code)
        else:
            containerid = 'flow_'+self.context.getId()
            txt.append('activateFlowView($("#'+containerid+'"));')
        txt.append("""</script>""")
        return '\n'.join(txt) 

    def activateFlowView(self):
        return """
function activateFlowView(container) {
    if (!container | typeof(container) == 'function') {
        var container = $("#%(containerid)s");
    }
    if (container.length == 0) return false;
    container.data("flowview", {batch_size:%(batch_size)i,
                                contentclass:'%(contentclass)s',
                                height:%(height)s,
                                effect:'%(effect)s',
                                tooldata:'%(tooldata)s',
                                speed:'%(speed)s',
                                fadeInSpeed:%(fadeInSpeed)s,
                                fadeOutSpeed:%(fadeOutSpeed)s,
                                vertical:%(vertical)s,
                                current_extra_class:'%(current_extra_class)s',
                                randomize:%(randomize)s,
                                display_content_title:%(display_content_title)s,
                                display_content_description:%(display_content_description)s,
                                timed:%(timed)s,
                                interval:'%(interval)s',
                                autoplay:%(autoplay)s,
                                autopause:%(autopause)s,
                                });
};
"""% {
    'containerid' :'flow_'+self.context.getId(),
    'contentclass':self.context.getId()+'-'+self.contentclass,
    'batch_size'  :self.settings.effect in ['swing', 'linear'] and getattr(self.settings, 'batch_size', 1) or 1,
    'height'      :getattr(self.settings, 'height', None) and str(self.settings.height) or 'null',
    'effect'      :self.settings.effect,
    'tooldata'    :self.settings.effect in ['default', 'fade', 'ajax', 'slide', 'custom'] and 'tabs' or 'scrollable',
    'speed'       :self.settings.speed,
    'fadeInSpeed' :str(self.settings.fadeInSpeed),
    'fadeOutSpeed':str(self.settings.fadeOutSpeed),
    'vertical'    :jsbool(self.settings.vertical),
    'randomize'   :jsbool(getattr(self.settings, 'randomize', False)),
    'current_extra_class':getattr(self.settings, 'current_extra_class', ''),
    'display_content_title':jsbool(self.settings.display_content_title),
    'display_content_description':jsbool(self.settings.display_content_description),
    'timed':jsbool(self.settings.timed),
    'interval' :str(self.settings.interval),
    'autoplay' :jsbool(self.settings.autoplay),
    'autopause':jsbool(self.settings.autopause),
    'use_backnext':jsbool(self.settings.use_backnext),
    }

    
    def __call__(self):
        if self.settings.content_layout not in ['content', 'summary', 'banner', 'custom']:
            view = queryMultiAdapter((self.context, self.request), name=self.settings.content_layout, default=None)
            if view:
                return view()
        return self.index()

class IBannerView(Interface):
    item = schema.Field(title=u"Item")
    settings = schema.Field(title=u"Settings")

directlyProvides(IBannerView, ITALNamespaceData)
   
class BannerView(ContentProviderBase):
    implements(IBannerView)
    
    item = None
    settings = None

    index = ViewPageTemplateFile('banner-view.pt')

    def render(self):
        return self.index()
        
#    def __init__(self, context, request, view):
#        super(BannerView, self).__init__(context, request, view)

    def update(self):
        super(BannerView, self).update()
#        self.settings = IFlowViewSettings(self.__parent__.context)
        portal_state = getMultiAdapter((self.context, self.request),
                                        name='plone_portal_state')
        self.portal = portal_state.portal()
        self.image = self.getImage()
        self.imageDict = self.getImageDict()
        if not self.item:
            self.item = self.context

    @memoize
    def getImages(self):
        results = []
        if hasattr(self.item, 'getObject'):
            if self.item.portal_type == 'Image':
                results = [self.item,]
            else:
                catalog = getToolByName(getSite(), 'portal_catalog')
                if isinstance(getattr(self.item, 'image_assoc', None), list) and len(getattr(self.item, 'image_assoc', [])) > 0:
                    results = catalog.searchResults({'UID':self.item.image_assoc[0], 'Language':'all'})
                elif getattr(self.item, 'usecontentimage', True):
                    path = self.item.getPath()
                    if path:
                        results = catalog.searchResults(path=path, portal_type='Image', sort_on='getObjPositionInParent')
        else:
            if getattr(self.item, 'displayimginsummary', False):
                try:
                    images = self.item.getField('image_assoc').get(self.item)
                except:
                    pass
                if images:
                    catalog = getToolByName(getSite(), 'portal_catalog')
                    results = catalog.searchResults({'UID':images[0].UID(), 'Language':'all'})
        return results
        
    def getImage(self):
        images = self.getImages()
        if images:
            return images[0].getObject()
        return []

    def imageWidth(self):
        if self.image:
            if hasattr(self.image, 'getWidth'):
                return self.image.getWidth()
            else:
                return ImageScaling(self.image, self.request).scale().width
        return None

    def imageHeight(self):
        if self.image:
            if hasattr(self.image, 'getHeight'):
                return self.image.getHeight()
            else:
                return ImageScaling(self.image, self.request).scale().height
        return None

    def getImageDict(self):
        if not self.image:
            return None
        return {'image_url'   :self.image.absolute_url(),
                'image_width' :self.imageWidth(),
                'image_height':self.imageHeight(),
                'image_title' :self.image.Title()
                }

    def getStyle(self):
        out = []
        if self.imageDict:
            out.append('background-image:url('+self.imageDict['image_url']+')')
        return '; '.join(out)
