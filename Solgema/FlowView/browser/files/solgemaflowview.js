waitForFinalEvent = (function () {
  var timers = {};
  return function (callback, ms, uniqueId) {
    if (!uniqueId) {
      uniqueId = "Don't call this twice without a uniqueId";
    }
    if (timers[uniqueId]) {
      clearTimeout (timers[uniqueId]);
    }
    timers[uniqueId] = setTimeout(callback, ms);
  };
})();


var standardEffects = ['default', 'fade', 'ajax', 'slide', 'custom'];

function randomizePanes(container) {
    var navitop = container.find(".navi.top li");
    if ($(navitop).length > 0) {
        var navitopParent = navitop.parent('ul');
        navitop.detach();
    }
    var navibottom = container.find(".navi.bottom li");
    if ($(navibottom).length > 0) {
        var navibottomParent = navibottom.parent('ul');
        navibottom.detach();
    }
    var panes = container.find("."+container.data('flowview').contentclass);
    if ($(panes).length > 0) {
        panes.detach();
    } else {
        return;
    }
    var panesOrder = new Array();
    for (var i=0;i<$(panes).length;i++) {
        panesOrder.push(i);
    }
    var n = panesOrder.length;
    var tempArr = [];
    for ( var i=0; i<n-1; i++ ) {
        tempArr.push(panesOrder.splice(Math.floor(Math.random()*panesOrder.length),1)[0]);
    }
    tempArr.push(panesOrder[0]);
    panesOrder=tempArr;
    for (var i=0;i<n;i++) {
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
};

function scrollableJavascript(container) {
    var flowview = container.data("flowview");
    var containerid = container.attr('id');
    container.find(" #flowtabs ul li a:first").addClass("current "+flowview.current_extra_class);
    container.find("#flowpanes").scrollable({
        circular   : true,
        easing     : flowview.effect,
        speed      : flowview.speed,
        vertical   : flowview.vertical,
        next       : "#"+containerid+" .forward",
        prev       : "#"+containerid+" .backward",
        activeClass: "current "+flowview.current_extra_class,
    });
    if (flowview.timed){
        container.find("#flowpanes").autoscroll({
            interval: flowview.interval,
            autoplay: flowview.autoplay,
            autopause: flowview.autopause,
        });
    }
    container.find("#flowpanes").navigator({
        navi       : "#"+containerid+" .navi ul",
        naviItem   : "a",
        activeClass: "current "+flowview.current_extra_class
    });
};

function standardJavascript(container) {
    var flowview = container.data("flowview");
    var containerid = container.attr('id');
    $("#"+containerid+" .navi ul").tabs("#"+containerid+" .items:first > div",
        {
        current: "current "+flowview.current_extra_class,
        rotate: true,
        effect: flowview.effect,
        fadeInSpeed: flowview.fadeInSpeed,
        fadeOutSpeed: flowview.fadeOutSpeed,
    })
    if (flowview.timed | flowview.use_backnext) {
        $("#"+containerid+" .navi ul").slideshow({
            interval:flowview.interval,
            next     : "#"+containerid+" .forward",
            prev     : "#"+containerid+" .backward",
            autoplay : flowview.autoplay,
            autopause : flowview.autopause,
        });
    }
};

function resizePages(container) {
    var pageContentHeight = container.data("flowview").height;
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
    var batch_size = container.data("flowview").batch_size;
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
        $(this).css("height", 'auto');
        if($(this).children().length == 1) {
            $(this).css("height", 'auto');
        }
    });
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
    var tooldata = container.find("#flowpanes").data(container.data("flowview").tooldata);
    if (tooldata) tooldata.next();
    if (pageContentHeight == null) {
        pageContentHeight = flowPanesHeight;
    }
};

function runFlowView(container) {
    var flowview = container.data("flowview")
    if (flowview.randomize){
        randomizePanes(container);
    }
    var panes = container.find(".page");
    var panes_number = $(panes).length;
    if (panes_number == 0) return false;
    var containerid = container.attr('id');
    var itemid = containerid.replace('flow_','');
    var paneid = itemid+'-pane';
    container.find(".documentActions").detach().insertBefore($("#portal-column-content #region-content:first"));
    $(panes).each(function (index) {
        if (!flowview.display_content_title){
            $(this).find("h1.documentFirstHeading:first, h2.tileHeadline:first").first().remove();
        }
        if (!flowview.display_content_description){
            $(this).find("p.description:first, p.documentDescription:first").first().remove();
        }
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
    var batch_size = flowview.batch_size;
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
    $(window).on('resize', function () {
        waitForFinalEvent(function(){
            resizePages(container);
            }, 100, "resizePages"+containerid);
    });
    for (i=1;i<batch_size;i++) {
        var cloned = container.find("#"+itemid+"-pane"+i).clone().addClass('cloned').appendTo("#flow_"+itemid+" #flowpanes .items:first");
    }
    if ((standardEffects).indexOf(flowview.effect) != -1) {
        standardJavascript(container);
    } else {
        scrollableJavascript(container);
    }
};

$(function(){
    $('.useFlowtabs').each(function(){
        var container = $(this);
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
    });
});
