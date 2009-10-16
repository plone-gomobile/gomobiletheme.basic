from five import grok
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.layout.viewlets.interfaces import IPortalHeader
from zope.interface import Interface

from Products.statusmessage.interfaces import IStatusMessage
from interfaces import IThemeLayer

from gomobile.mobile.interfaces import IMobileBehavior

# Viewlets are on all content by default.
grok.context(Interface)

# Use templates directory to search for templates.
grok.templatedir('templates')

# Viewlets are active only when gomobiletheme.basic theme layer is activated
grok.layer(IThemeLayer)

class Head(grok.Viewlet):
    """ Render <head> section for every page """
    grok.baseclass()

class Logo(grok.Viewlet):
    """ Render site logo with link back to the site root """
    grok.baseclass()

class LanguageChooser(grok.Viewlet):
    """ Render langauge chooser at the top right corner if more than one site language available.
    """
    grok.baseclass()

    def getLanguages(self):
        """
        """

class Footer(grok.Viewlet):
    """ Render langauge chooser at the top right corner if more than one site language available.
    """
    grok.baseclass()

class Messages(grok.Viewlet):
    """ Render portal status messages.

    Messages are hold in the session by statusmessage product.
    """
    grok.baseclass()

    def messages(self):
        """
        Clears status message buffer and return pending current messages.
        """

        # Get status message utility by adapter look-up
        status_message = IStatusMessage(self.request)

        # Fetch buffer
        return status_message.showStatusMessages()

class MobileFolderListing(grok.Viewlet):
    """ List content of the folder.

    Because mobile sites don't have navigation portlet
    we need to have a way to show what's inside the folder.

    This viewlet is only
    """

    def update(self):
        """ """

        # Check from mobile behavior should we do the listing
        behavior = IMobileBehavior(self.context)
        if behavior.mobileFolderListing:
            self.items = self.context.getFolderContents(contentFilter, batch=False)
        else:
            self.items = []
    def hasListing(self):
        """
        Check whether mobile folder listing is enabled for a particular content type.
        """
        return len(self.items) > 0

    def render(self):
        if self.hasListing():
            return grok.Viewlet.render(self)
        else:
            return ""

class PathBar(grok.Viewlet):
    """ Render breadcrumbs where the user currently is """

    def update(self):
        super(grok.Viewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()

class Sections(grok.Viewlet):
    """ List top level folders.

    Allows users to quickly navigate around the site.

    This is placed at the bottom of the page.
    This is equivalent of portal_tabs in normal Plone.
    """
    def update(self):

        grok.Viewlet.update(self)

        # Get tabs (top level navigation links)
        context_state = getMultiAdapter((self.context, self.request),
                                    name=u'plone_context_state')
        actions = context_state.actions()


        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                       name='portal_tabs_view')


        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)
