from Solgema.FlowView.config import _
from Products.CMFPlone import PloneMessageFactory as _pmf
from zope.interface import Interface
from plone.z3cform.fieldsets import group as plonegroup
from z3c.form import form, field as z3field, group, button
from plone.app.z3cform.layout import wrap_form
from Solgema.FlowView.interfaces import IFlowViewSettings
from Solgema.FlowView.utils import getDisplayType
from Solgema.FlowView.utils import getAllDisplayTypes
from Solgema.FlowView.settings import FlowViewSettings
import zope.i18n


class INothing(Interface):
    pass

class FlowViewSettingsForm(group.GroupForm, form.EditForm):
    """
    The page that holds all the flowview settings
    """

    fields = z3field.Fields()
    contentFields = ['content_layout',
                     'display_content_title',
                     'display_content_image',
                     'display_content_description',
                     'display_content_text',
                     'display_more_link',
                     'thumb_size',
                     'thumb_position',
                     'thumb_side']
    navigationFields = ['navigator', 'tab_content', 'tab_position', 'use_backnext']
    
    label = _(u'heading_flowview_settings_form', default=u'Flow View')
    
    description = _(u'description_flowview_settings_form',
        default=u'Configure the parameters for this Flow View.')

    successMessage = _(u'successMessage_flowview_settings_form',
        default=u'Flow View Settings Saved.')
    noChangesMessage = _(u'noChangesMessage_flowview_settings_form',
        default=u'There are no changes in the Flow View settings.')

    def update(self):
        fields = z3field.Fields(IFlowViewSettings)
#        fields['invocation_code'].field.default += u"activateFlowView($('#flow_%s'));" % (self.context.id, self.context.id)
#        fields['invocation_code'].field.description += u"activateFlowView($('#flow_%s'));" % (self.context.id)
        fields['invocation_code'].field.description = _(u'You can add your custom javascript invocation code here. Leave blank to use default. Default code is: ${default_code}',
            mapping={'default_code':u"activateFlowView($('#flow_%s'));" % (self.context.id)})
        fieldsid = [field.field.__name__ for field in fields.values()]
        main = plonegroup.GroupFactory(_pmf(u"label_choose_template"), fields.select(*[a for a in fieldsid if a not in self.contentFields+self.navigationFields]))
        content = plonegroup.GroupFactory(_pmf(u"label_schema_default"), fields.select(*[a for a in fieldsid if a in self.contentFields]))
        navigation = plonegroup.GroupFactory(_pmf(u"Navigation"), fields.select(*[a for a in fieldsid if a in self.navigationFields]))
        self.groups = [main, content, navigation]
        super(FlowViewSettingsForm, self).update()
        
    def set_status_message(self, settings, has_changes):
        msg = has_changes and self.successMessage or self.noChangesMessage
        msg = zope.i18n.translate(msg)
        self.status = msg

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        settings = FlowViewSettings(self.context)

        has_changes = False
        if changes:
#            settings = FlowViewSettings(self.context)
#            settings.last_cooked_time_in_seconds = 0
            has_changes = True

        self.set_status_message(settings, has_changes)

FlowViewSettingsView = wrap_form(FlowViewSettingsForm)
