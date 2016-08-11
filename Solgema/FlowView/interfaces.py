from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface, Attribute
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Solgema.FlowView.config import _

class ISolgemaFlowViewLayer(IDefaultPloneLayer):
    """Solgema FlowView layer"""

class IFlowViewMarker(Interface):
    """
    marker interface for content types that implement
    the flowview
    """

class IFlowViewDisplayType(Interface):
    name = Attribute("name of display type")
    description = Attribute("description of type")
    schema = Attribute("Options for this display type")
    userWarning = Attribute("A warning to be displayed to to "
                            "the user if they use this type.")
    width = Attribute("The width of the flow view")
    height = Attribute("The height of the flow view")
    start_image_index = Attribute("What image the flow view should "
                                  "start playing at.")

    def content():
        """
        the content of the display yet
        """

    def javascript():
        """
        content to be included in javascript area of template
        """

    def css():
        """
        content to be included in css area of template
        """
    
class IFlowViewSettings(Interface):

    showTitle = schema.Bool(
        title=_(u"label_showTitle", default=u"Show Title?"),
        default=False,
        required=True
    )
    
    showDescription = schema.Bool(
        title=_(u"label_showDescription", default=u"Show Description?"),
        default=True,
        required=True
    )

    event = schema.Choice(
        title=_(u"label_event", default=u"Event"),
        description=_(u"description_event",
            default=u"Specifies the event when a tab is opened."
        ),
        default='click',
        vocabulary=SimpleVocabulary([
            SimpleTerm('click', 'click', _(u"label_click", default=u"click")),
            SimpleTerm('mouseover', 'mouseover', _(u"label_mouseover", default=u"mouseover")),
            SimpleTerm('dblclick', 'dblclick', _(u"label_dblclick", default=u"dblclick")),
        ]),
        required=True
    )

    effect = schema.Choice(
        title=_(u"label_effect", default=u"Effect"),
        description=_(u"description_effect",
            default=u"The effect to be used when a tab is clicked."
        ),
        default='default',
        vocabulary=SimpleVocabulary([
            SimpleTerm('default', 'default', _(u"label_default", default=u"default")),
            SimpleTerm('fade', 'fade', _(u"label_fade", default=u"fade")),
            SimpleTerm('ajax', 'ajax', _(u"label_ajax", default=u"ajax")),
            SimpleTerm('slide', 'slide', _(u"label_slide", default=u"slide")),
            SimpleTerm('horizontal', 'horizontal', _(u"label_horizontal", default=u"horizontal")),
            SimpleTerm('swing', 'swing', _(u"label_swing", default=u"swing")),
            SimpleTerm('linear', 'linear', _(u"label_linear", default=u"linear")),
            SimpleTerm('custom', 'custom', _(u"label_custom_effect", default=u"Custom Effect")),
        ]),
        required=True
    )

    custom_effect = schema.Text(
        title=_(u"label_custom_effect", default=u"Custom Effect"),
        description=_(u"help_custom_effect", default=u'You can add your custom javascript effect code here. Only works if "custom" selected as effect. Name of you effect must be "custom"'),
        required=False
    )
    
    fadeInSpeed = schema.Int(
        title=_(u"label_fadeInSpeed", default=u"fadeInSpeed"),
        description=_(u"description_fadeInSpeed",
            default=u"Only available when used together with the \"fade\" effect."
                    u"This property defines how fast (in milliseconds) the opened pane reveals its content."
        ),
        default=200,
        required=True
    )

    fadeOutSpeed = schema.Int(
        title=_(u"label_fadeOutSpeed", default=u"fadeOutSpeed"),
        description=_(u"description_fadeOutSpeed",
            default=u"Only available when used together with the \"fade\" effect."
                    u"This property defines how fast (in milliseconds) the opened pane hides its content."
        ),
        default=0,
        required=True
    )
    
    timed = schema.Bool(
        title=_(u"label_timed", default=u"Timed?"),
        description=_(u"description_timed",
            default=u"Should this Flow View automatically "
                    u"change images for the user?"
        ),
        default=False,
        required=True
    )

    interval = schema.Int(
        title=_(u"label_interval", default=u"Interval"),
        description=_(u"description_interval",
            default=u"If slide show is timed, the interval sets "
                    u"how long before the next image is shown in miliseconds."
        ),
        default=3000,
        required=True
    )

    speed = schema.Int(
        title=_(u"label_speed", default=u"speed"),
        description=_(u"description_speed",
            default=u"The time (in milliseconds) of the scrolling animation."
        ),
        default=400,
        required=True
    )

    height = schema.Int(
        title=_(u"label_height", default=u"Height"),
        description=_(u"description_height",
            default=u"The height (in px) of the flowview content. If empty, the tallest item's height will be used."
        ),
        required=False
    )

    initialIndex = schema.Int(
        title=_(u"label_initialIndex", default=u"Initial Index"),
        description=_(u"description_initialIndex",
            default=u"Specifies the tab that is initially opened when the page loads."
        ),
        default=0,
        required=True
    )
    
    autoplay = schema.Bool(
        title=_(u"label_autoplay", default=u"Auto play?"),
        description=_(u"description_autoplay",
            default=u"If this property is set to true then the tabs will automatically advance to the next tab implementing an automatically \"playable\" slideshow."
        ),
        default=False,
        required=True
    )
    
    autopause = schema.Bool(
        title=_(u"label_autopause", default=u"Auto pause?"),
        description=_(u"description_autopause",
            default=u"If this property is set to true then the tabs will automatically advance to the next tab implementing an automatically \"playable\" slideshow."
        ),
        default=True,
        required=True
    )
    
    vertical = schema.Bool(
        title=_(u"label_vertical", default=u"Vertical?"),
        description=_(u"description_vertical",
            default=u"If empty, the scrollable will guess by itself. "
        ),
        required=False
    )
    
    flowPadding = schema.Int(
        title=_(u"label_flowPadding", default=u"Padding in px"),
        default=15,
        required=False
    )
    
    showBorder = schema.Bool(
        title=_(u"label_showBorder", default=u"Show border"),
        default=True
    )
    
    showFirstOnly = schema.Bool(
        title=_(u"label_showFirstOnly", default=u"Show first pane only"),
        description=_(u"description_showFirstOnly",
            default=u"If your flowview is not used as content but only as \"costmetics\" with images, showing only first element avoid having the page to break on load or if javascipt is not activated."
        ),
        
        default=True
    )

# CONTENT FIELDS
    
    invocation_code = schema.Text(
        title=_(u"label_invocation_code", default=u"Custom Invocation Code"),
        description=_(u'You can add your custom javascript invocation code here. Leave blank to use default. Default code is: ${default_code}'),
        required=False
    )
    
    content_layout = schema.Choice(
        title=_(u"label_content_layout", default=u"Content Layout"),
        description=_(u"description_content_layout",
        ),
        default='content',
        vocabulary='Solgema.FlowView.FlowViews',
        required=True
    )
    
    thumb_size = schema.Choice(
        title=_(u"label_thumb_size", default=u"Thumbnail image size"),
        description=_(u"description_thumb_size",
            default=u"The size of thumbnail images. "
        ),
        default='tile',
        vocabulary=SimpleVocabulary([
            SimpleTerm('tile', 'tile', _(u"label_tile", default=u"tile")),
            SimpleTerm('thumb', 'thumb', _(u"label_thumb", default=u"thumb")),
            SimpleTerm('mini', 'mini', _(u"label_mini", default=u"mini")),
            SimpleTerm('preview', 'preview', _(u"label_preview", default=u"preview")),
        ]),
        required=True
    )
    
    thumb_position = schema.Choice(
        title=_(u"label_thumb_position", default=u"Thumbnail image position"),
        description=_(u"description_thumb_position",
            default=u"The position of thumbnail images. "
        ),
        default='top',
        vocabulary=SimpleVocabulary([
            SimpleTerm('top', 'top', _(u"label_top", default=u"top")),
            SimpleTerm('undertitle', 'undertitle', _(u"label_undertitle", default=u"undertitle")),
            SimpleTerm('bottom', 'bottom', _(u"label_bottom", default=u"bottom")),
        ]),
        required=True
    )
    
    thumb_side = schema.Choice(
        title=_(u"label_thumb_side", default=u"Thumbnail image side"),
        description=_(u"description_thumb_side",
            default=u"The side of thumbnail images. "
        ),
        vocabulary=SimpleVocabulary([
            SimpleTerm('left', 'left', _(u"label_left", default=u"Left")),
            SimpleTerm('right', 'right', _(u"label_right", default=u"Right")),
        ]),
        required=False
    )
    
    display_content_title = schema.Bool(
        title=_(u"label_display_content_title", default=u"Display Content Title?"),
        default=False,
        required=True
    )
    
    display_content_description = schema.Bool(
        title=_(u"label_display_content_description", default=u"Display Content Description?"),
        default=True,
        required=True
    )
    
    display_content_image = schema.Bool(
        title=_(u"label_display_content_image", default=u"Display Content Image?"),
        default=True,
        required=True
    )
    
    display_content_text = schema.Bool(
        title=_(u"label_display_content_text", default=u"Display Content Text?"),
        default=True,
        required=True
    )
    
    display_more_link = schema.Bool(
        title=_(u"label_display_more_link", default=u"Display \"More...\" link?"),
        default=True,
        required=True
    )
    
    navigator = schema.Bool(
        title=_(u"label_navigator", default=u"Use Navigator?"),
        description=_(u"description_navigator",
            default=u"Should this Flow View display navigation tabs?"
        ),
        default=True,
        required=True
    )
    
    tab_content = schema.Choice(
        title=_(u"label_tab_content", default=u"Tab Content"),
        description=_(u"description_tab_content",
            default=u"Choose what you want to be displayed in tabs. "
        ),
        default='title',
        vocabulary=SimpleVocabulary([
            SimpleTerm('title', 'title', _(u"label_title", default=u"title")),
            SimpleTerm('description', 'description', _(u"label_description", default=u"description")),
            SimpleTerm('image', 'image', _(u"label_image", default=u"image")),
            SimpleTerm('slidetabs', 'slidetabs', _(u"label_slidetabs", default=u"slidetabs")),
        ]),
        required=True
    )
    
    tab_position = schema.Choice(
        title=_(u"label_tab_position", default=u"Tab Position"),
        description=_(u"description_tab_content",
            default=u"Choose if you want to display tab on the top or the bottom of the content."
        ),
        default='top',
        vocabulary=SimpleVocabulary([
            SimpleTerm('top', 'top', _(u"label_top", default=u"top")),
            SimpleTerm('bottom', 'bottom', _(u"label_bottom", default=u"bottom")),
        ]),
        required=True
    )
    
    use_backnext = schema.Bool(
        title=_(u"label_use_backnext", default=u"Display Back and Next buttons?"),
        default=False,
        required=True
    )
    
    tabs_extra_class = schema.TextLine(
        title=_(u"label_tabs_extra_class", default=u"Extra class for tabs"),
        required=False
    )
    
    current_extra_class = schema.TextLine(
        title=_(u"label_current_extra_class", default=u"Extra class for current slide tab"),
        required=False
    )
    
    prev_extra_class = schema.TextLine(
        title=_(u"label_prev_extra_class", default=u"Extra class for current prev button"),
        required=False
    )
    
    next_extra_class = schema.TextLine(
        title=_(u"label_next_extra_class", default=u"Extra class for current next button"),
        required=False
    )

    batch_size = schema.Int(
        title=_(u"label_batch_size", default=u"Batch Size"),
        description=_(u"description_batch_size",
            default=u"Sets the number of items to display per pane. "
        ),
        default=1,
        required=True
    )

    randomize = schema.Bool(
        title=_(u"label_randomize", default=u"Randomize content order"),
        default=False
    )
