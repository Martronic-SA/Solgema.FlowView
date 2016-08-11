from Products.Five.browser import BrowserView
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
    from collective.plonetruegallery.utils import getGalleryAdapter
    hasTrueGallery = True
except:
    hasTrueGallery = False


def jsbool(val):
    return str(val).lower()

class BaseFlowView(BrowserView):

    def __init__(self, context, request):
        super(BaseFlowView, self).__init__(context, request)
        marker.mark( self.context, IFlowViewMarker )
        
    @property
    def macros(self):
        return self.template.macros

class FlowView(BrowserView):

    name = None
    description = None
    schema = None
    userWarning = None
    staticFilesRelative = '++resource++solgemaflowview.resources'
    contentclass = 'page'

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
        txt.append(self.resizePages())
        txt.append(self.initTabs())
        txt.append(self.activateFlowView())
        if getattr(self.settings, 'invocation_code', None):
            txt.append(self.settings.invocation_code)
        else:
            containerid = 'flow_'+self.context.getId()
            txt.append('activateFlowView($("#'+containerid+'"));')
        txt.append("""</script>""")
        return '\n'.join(txt) 

    def randomizePanes(self):
        if getattr(self.settings, 'randomize', False):
            return """
    var navitop = container.find(".navi.top li");
    if ($(navitop).length > 0) {
        var navitopParent = navitop.parent('ul');
        navitop.detach();
    }
    var navibottom = container.find(".navi.bottom li");
    if ($(navibottom).length > 0) {
        var navitopParent = navitop.parent('ul');
        navitop.detach();
    }
    var panes = container.find(".%(contentclass)s");
    if ($(panes).length > 0) panes.detach();
    var panesOrder = new Array();
    for (i=0;i<$(panes).length;i++) {
        panesOrder.push(i);
    }
    var n = panesOrder.length;
    var tempArr = [];
    for ( var i=0; i<n-1; i++ ) {
        tempArr.push(panesOrder.splice(Math.floor(Math.random()*panesOrder.length),1)[0]);
    }
    tempArr.push(panesOrder[0]);
    panesOrder=tempArr;
    for (i=0;i<n;i++) {
        s = panesOrder[i];
        if ($(navitop).length > 0) {
            $(navitop[s]).appendTo($(navitopParent));
        }
        if ($(navibottom).length > 0) {
            $(navibottom[s]).appendTo($(navibottomParent));
        }
        if ($(panes).length > 0) {
            $(panes[s]).appendTo(container.find(".items"));
        }
    }
""" % {'contentclass':self.context.getId()+'-'+self.contentclass}
        return ''

    def activateFlowView(self):
        return """
function activateFlowView(container) {
    if (!container | typeof(container) == 'function') {
        var container = $("#%(containerid)s");
    }
    if (container.length == 0) return false;
    if (container.find("img").length > 0) {
        container.find("img:last").one("load", function() {
            runFlowView(container);
        }).each(function() {
            if(this.complete) $(this).load();
        }).on("error", function(){
            runFlowView(container);
        });
    } else {
        runFlowView(container);
    }
}
"""% {
    'containerid':'flow_'+self.context.getId(),
    }

    def resizePages(self):
        return """
var pageContentHeight = %(height)s;
function resizePages(container) {
    if ($(window).height()<500) {
        $('#solgemabandeau .page').css('height','300px');
        $('#solgemabandeau .pageContent').css('height','300px');
    } else if (pageContentHeight != null) {
        $('#solgemabandeau .page').css('height', pageContentHeight+'px');
        $('#solgemabandeau .pageContent').css('height', pageContentHeight+'px');
    }
    var panes = container.find(".page");
    var contentWidth = container.find("#flowpanes_container #flowpanes").width();
    var numitems = $(panes).first().find('.pageContent').length;
    var batch_size = %(batch_size)i;
    if ($( document ).width()<768) {
      var batch_size = 1;
    }
    if (batch_size > 1) {
        var rapport = (batch_size-1)/batch_size;
    } else {
        var rapport = 1;
    }
    var rapport = 1;
    var page_width = contentWidth/batch_size;
    var content_width = page_width/numitems;
    $(panes).each( function(index) {
        var page_marginWidth = $(this).outerWidth(true)-$(this).width();
        var pagewidth = page_width-(page_marginWidth*rapport);
        $(this).width(pagewidth);
        $(this).children().each( function(index) {
            var content_marginWidth = $(this).outerWidth(true)-$(this).width();
            $(this).width( pagewidth-content_marginWidth );
        });
    });
    var flowPanesHeight = 0;
    $(panes).each( function(index) {
        if( $(this).outerHeight(true) > flowPanesHeight) flowPanesHeight = $(this).outerHeight(true);
        if($(this).children().length == 1) {
            $(this).children().each( function(index, child) {
                if( $(child).outerHeight(true) > flowPanesHeight) flowPanesHeight = $(child).outerHeight(true);
            });
        }
    });
    $(panes).each( function(index) {
        var content_marginHeight = $(this).outerHeight(true)-$(this).height();
        $(this).css("height", flowPanesHeight-content_marginHeight);
        if($(this).children().length == 1) {
            var content_marginHeight = $(this).outerHeight(true)-$(this).height();
            $(this).css("height", flowPanesHeight-content_marginHeight);
        }
    });
    container.find("#flowpanes").height(flowPanesHeight);
    var tooldata = container.find("#flowpanes").data("%(tooldata)s");
    if (tooldata) tooldata.next();
    if (pageContentHeight == null) {
        pageContentHeight = flowPanesHeight;
    }
};
""" % {'height':getattr(self.settings, 'height', None) and str(self.settings.height) or 'null',
       'batch_size':self.settings.effect in ['swing', 'linear'] and getattr(self.settings, 'batch_size', 1) or 1,
       'tooldata':self.settings.effect in ['default', 'fade', 'ajax', 'slide', 'custom'] and 'tabs' or 'scrollable'
    }

    def initTabs(self):
        return """
var panes_number = 0;
function runFlowView(container) {
    %(randomize)s
    var panes = container.find(".page");
    panes_number = $(panes).length;
    if (panes_number == 0) return false;
    containerid = container.attr('id');
    var itemid = containerid.replace('flow_','');
    var paneid = itemid+'-pane';
    container.find(".documentActions").detach().insertBefore($("#portal-column-content #region-content:first"));
    $(panes).each(function (index) {
            %(js_remove_title)s
            %(js_remove_description)s
            $(this).find("#review-history").remove();
            var lastP = $(this).find("p").last();
            if ($(lastP).html() != null) {
                if ($(lastP).html().trim() == '&nbsp;') {
                    $(lastP).remove();
                }
            }
    });
    container.css("display","block").addClass("flowEnabled");
    container.parent().addClass("flowEnabled");
    var batch_size = %(batch_size)i;
    if ($( document ).width()<768) {
      var batch_size = 1;
    }
    if (batch_size > 1) {
        container.addClass("batched");
        container.addClass("manyItems");
    }
    $(panes).each( function(index) {
        $(this).attr("id", paneid+index);
    });
    resizePages(container);
    $(window).resize(function () {
        //solgema.js needed!
        waitForFinalEvent(function(){
            resizePages(container);
            }, 100, "resizePages"+containerid);
    });
    for (i=1;i<%(batch_size)i;i++) {
        var cloned = container.find("#"+itemid+"-pane"+i).clone().addClass('cloned').appendTo("#flow_"+itemid+" #flowpanes .items:first");
    }
    %(effectjs)s
""" % {
    'randomize'            :self.randomizePanes(),
    'effect'               :self.settings.effect,
    'effectjs'             :self.settings.effect in ['default', 'fade', 'ajax', 'slide', 'custom'] and self.standardJavascript() or self.scrollableJavascript(),
    'batch_size'           :self.settings.effect in ['swing', 'linear'] and getattr(self.settings, 'batch_size', 1) or 1,
    'js_remove_title'      :not self.settings.display_content_title and """$(this).find("h1.documentFirstHeading:first, h2.tileHeadline:first").first().remove();""" or '',
    'js_remove_description':not self.settings.display_content_description and """$(this).find("p.description:first, p.documentDescription:first").first().remove();""" or ''
    }

    def scrollableJavascript(self):
        return """$("#"+containerid+" #flowtabs ul li a:first").addClass("current %(current_extra_class)s");
    container.find("#flowpanes").scrollable({
        circular   : true,
        easing     : "%(effect)s",
        speed      : %(speed)i,
        vertical   : %(vertical)s,
        next       : "#"+containerid+" .forward",
        prev       : "#"+containerid+" .backward",
//        mousewheel : true,
        activeClass: "current %(current_extra_class)s"
    })%(activateAutoscrollTimed)s.navigator({
        navi       : "#"+containerid+" .navi ul",
        naviItem   : "a",
        activeClass: "current %(current_extra_class)s"
    });
};""" % {
    'effect'                 :self.settings.effect,
    'speed'                  :self.settings.speed,
    'vertical'               :jsbool(self.settings.vertical),
    'activateAutoscrollTimed':self.activateAutoscrollTimed(),
    'current_extra_class'    :getattr(self.settings, 'current_extra_class', '')
    }

    def activateAutoscrollTimed(self):
        if not self.settings.timed:
            return ''
        return """.autoscroll({
    interval: %(interval)s,
    autoplay: %(autoplay)s,
    autopause: %(autopause)s,
    })""" % {
    'interval' :str(self.settings.interval),
    'autoplay' :jsbool(self.settings.autoplay),
    'autopause':jsbool(self.settings.autopause),
    }

    def standardJavascript(self):
        return """
    $("#"+containerid+" .navi ul").tabs("#"+containerid+" .items:first > div",IBrowserRequest
        {
        rotate: true,
        effect: "%(effect)s",
        fadeInSpeed: %(fadeInSpeed)s,
        fadeOutSpeed: %(fadeOutSpeed)s,
    })%(activateTimed)s;
};""" % {
    'effect'               :self.settings.effect,
    'speed'                :self.settings.speed,
    'vertical'             :jsbool(self.settings.vertical),
    'fadeInSpeed'          :str(self.settings.fadeInSpeed),
    'fadeOutSpeed'         :str(self.settings.fadeOutSpeed),
    'activateTimed'        :self.activateTimed()
    }

    def activateTimed(self):
        if not self.settings.timed and not self.settings.use_backnext:
            return ''
        txt = '.slideshow({'
        if self.settings.timed:
            txt += """interval: "%(interval)i",
    next     : "#"+containerid+" .forward",
    prev     : "#"+containerid+" .backward",
    autoplay : %(autoplay)s,
    autopause: %(autopause)s,""" % {
    'interval'   :self.settings.interval,
    'autoplay'   :jsbool(self.settings.autoplay),
    'autopause'  :jsbool(self.settings.autopause),
    }
        return txt+'})'
    
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
        if self.item == None:
            self.item = self.context

    @memoize
    def getImages(self):
        results = []
        if hasattr(self.item, 'getObject'):
            catalog = getToolByName(self.item, 'portal_catalog')
            if isinstance(getattr(self.item, 'image_assoc', None), list) and len(getattr(self.item, 'image_assoc', [])) > 0:
                results = catalog.searchResults({'UID':self.item.image_assoc[0], 'Language':'all'})
            elif self.item.usecontentimage:
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
                    catalog = getToolByName(self.item, 'portal_catalog')
                    results = catalog.searchResults({'UID':images[0].UID(), 'Language':'all'})
        return results
        
    def getImage(self):
        images = self.getImages()
        if images:
            return images[0].getObject()
        return []

    def imageWidth(self):
        if self.image:
            return self.image.getField('image').getSize(self.image)[0]
        return None

    def imageHeight(self):
        if self.image:
            return self.image.getField('image').getSize(self.image)[1]
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
