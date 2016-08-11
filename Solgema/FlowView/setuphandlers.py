from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from zope.component import adapter, getUtility, getAdapters, getMultiAdapter, getSiteManager
from Products.GenericSetup.interfaces import IProfileImportedEvent
import logging
LOG = logging.getLogger('Solgema.FlowView')

def installSolgemaFlowView(context):
    if context.readDataFile('solgemaflowview_various.txt') is None:
        return
    site = context.getSite()
    
    catalog = getToolByName(site, 'portal_catalog')
    folderish = catalog.searchResults(portal_type=['Folder', 'FolderRoot', 'MemberFolder', 'Topic'])
    for citem in folderish:
        item = citem.getObject()
        if not hasattr(item, 'getLayout'):
            LOG.info('Solgema Update: item %s has no getLayout attribute.'%(str(item)))
            continue
        if item.getLayout() == 'folder_full_view_tabs':
            item._updateProperty('layout', 'flowview')
    LOG.info('Solgema Update: old views replaced')

    setup = getToolByName(site, 'portal_setup')
    ttool = getToolByName(site, 'portal_types')
    types = [ttool.Folder,]
    if hasattr(ttool, 'Topic'):
        types.append(ttool.Topic)
    if hasattr(ttool, 'Collection'):
        types.append(ttool.Collection)
    for ttype in types:
        methods = ttype.view_methods
        if 'folder_full_view_tabs' in methods:
            ttype.manage_changeProperties(view_methods=tuple([a for a in methods if a !='folder_full_view_tabs']))

    if getFSVersionTuple()[0] == 4:
        setup.runAllImportStepsFromProfile('profile-Solgema.FlowView:plone4')
        jstool = getToolByName(site, 'portal_javascripts')
        jstool.cookResources()
        csstool = getToolByName(site, 'portal_css')
        csstool.cookResources()
    else:
        setup.runAllImportStepsFromProfile('profile-Solgema.FlowView:plone5')
        
def uninstallSolgemaFlowView(context):
    if context.readDataFile('solgemaflowview_uninstall.txt') is None:
        return
    site = context.getSite()

@adapter(IProfileImportedEvent)
def handleProfileImportedEvent(event):
    context = event.tool
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    if portal_quickinstaller.isProductInstalled('Solgema.FlowView') and 'to500' in event.profile_id and event.full_import:
        portal_setup = getToolByName(context, 'portal_setup')
        portal_setup.runAllImportStepsFromProfile('profile-Solgema.FlowView:uninstall4')
        portal_setup.runAllImportStepsFromProfile('profile-Solgema.FlowView:plone5')

