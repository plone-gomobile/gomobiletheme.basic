"""

    Various reusable page parts used in main_template.pt and elsewhere.

"""

import sys, os

from Acquisition import aq_inner
from zope.component import getMultiAdapter

from zope.interface import Interface
from zope.component import queryMultiAdapter

from five import grok
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.layout.viewlets.interfaces import IPortalHeader
from Products.CMFCore.interfaces._content import IFolderish
from Products.statusmessages.interfaces import IStatusMessage

from gomobile.mobile.behaviors import IMobileBehavior
from gomobile.mobile.utilities import getCachedMobileProperties, debug_layers
from gomobile.mobile.browser.resizer import getUserAgentBasedResizedImageURL



from interfaces import IThemeLayer

# Resolve templatedir and export it as an variable so that other
# packages can use our templates as well
module = sys.modules[__name__]
dirname = os.path.dirname(module.__file__)
gomobiletheme_basic_templatedir = os.path.join(dirname, "templates")

# Viewlets are on all content by default.
grok.context(Interface)

# Use templates directory to search for templates.
grok.templatedir("templates")

# Viewlets are active only when gomobiletheme.basic theme layer is activated
grok.layer(IThemeLayer)


def getView(context, request, name):
    context = aq_inner(context)
    # Will raise ComponentLookUpError
    view = getMultiAdapter((context, request), name=name)
    view = view.__of__(context)
    return view

class MainViewletManager(grok.ViewletManager):
    """ This viewlet manager is responsible for all gomobiletheme.basic viewlet registrations.

    Viewlets are directly referred in main_template.pt by viewlet name,
    thus overriding Plone behavior to go through ViewletManager render step.
    """
    grok.name('gomobiletheme.basic.viewletmanager')

# Set viewlet manager default to all following viewlets
grok.viewletmanager(MainViewletManager)

class Head(grok.Viewlet):
    """ Render <head> section for every page.

    Render the default mobile <head> section with CSS and icons.

    Render necessary bits for mobile preview feature (needs cross-site javascript).
    """

    grok.template("head")

    def resource_url(self):
        """  Tell templates which URL use for theme loading.

        This URL will be effective for

        - common.css

        - webkit.css

        - lowend.css

        - logo.png

        - apple-touch-icon.png

        """
        return self.portal_url + "/" + "++resource++gomobiletheme.basic"

    def update(self):
        portal_state = getView(self.context, self.request, "plone_portal_state")
        self.portal_url = portal_state.portal_url()

        # Create <base href=""> directive of <head>
        if IFolderish.providedBy(self.context):
            # Folderish URLs must end to slash
            self.base = self.context.absolute_url()+'/'
        else:
            self.base = self.context.absolute_url()

class Header(grok.Viewlet):
    """ Render items at the top of the page.

    This includes

    * Logo

    * Language switcher
    """



class Logo(grok.Viewlet):
    """ Render site logo with link back to the site root.

    Logo will be automatically resized in the case of
    the mobile screen is very small.
    """

    def getLogoPath(self):
        """ Subclass can override """
        return "++resource++gomobiletheme.basic/logo.png"

    def update(self):

        portal_state = getView(self.context, self.request, "plone_portal_state")
        self.portal_url = portal_state.portal_url()

        path = self.getLogoPath()

        self.logo_url = getUserAgentBasedResizedImageURL(self.context, self.request,
                                                         path=path,
                                                         width="auto",
                                                         height="85", # Maximum logo height
                                                         padding_width=10)


class LanguageChooser(grok.Viewlet):
    """ Render langauge chooser at the top right corner if more than one site language available.
    """

    def needs_language(self):
        return False

    def languages(self):
        """
        """


class Footer(grok.Viewlet):
    """ Render langauge chooser at the top right corner if more than one site language available.
    """

class Messages(grok.Viewlet):
    """ Render portal status messages.

    Messages are hold in the session by statusmessages product.
    """
    def messages(self):
        """
        Clears status message buffer and return pending current messages.
        """

        # Get status message utility by adapter look-up
        status_message = IStatusMessage(self.request)

        # Fetch buffer
        return status_message.showStatusMessages()

class PathBar(grok.Viewlet):
    """ Render breadcrumbs where the user currently is """

    def update(self):
        super(grok.Viewlet, self).update()

        self.portal_state = getView(self.context, self.request, "plone_portal_state")
        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getView(self.context, self.request, 'breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()

        self.site_url = self.portal_state.portal_url()
        self.navigation_root_url = self.portal_state.navigation_root_url()

class Sections(grok.Viewlet):
    """ List top level folders.

    Allows users to quickly navigate around the site.

    This is placed at the bottom of the page.
    This is equivalent of portal_tabs in normal Plone.
    """
    def update(self):

        grok.Viewlet.update(self)

        # Get tabs (top level navigation links)
        context_state = getView(self.context, self.request, u'plone_context_state')
        actions = context_state.actions()

        portal_state = getView(self.context, self.request, "plone_portal_state")
        self.portal_url = portal_state.portal_url()

        portal_tabs_view = getView(self.context, self.request, u'portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)

class FooterText(grok.Viewlet):
    """ Free-form HTML text at the end of the page """

    def update(self):
        super(grok.Viewlet, self).update()

        # Load footer text from the site settings if available
        properties = getCachedMobileProperties(self.context, self.request)

        self.text = getattr(properties, "footer_text", None)
        if not self.text:
            self.text = u"Please set footer text in mobile_properties"

class MobileFolderListing(grok.Viewlet):
    """ List content of the folder.

    Because mobile sites don't have navigation portlet
    we need to have a way to show what's inside the folder.

    This viewlet is only
    """

    def doListing(self):
        """
        """

    def getListingContainer(self):
        """
        """
        context = self.context.aq_inner
        if IFolderish.providedBy(context):
            return context
        else:
            return context.aq_parent

    def getActiveTemplate(self):
        state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return state.view_template_id()

    def getActiveView(self):
        """
        """

    def getTemplateIdsNoListing(self):
        """ Subclass may override.
        """
        return ["folderlisting"]

    def update(self):
        """ """

        grok.Viewlet.update(self)

        # Check from mobile behavior should we do the listing
        behavior = IMobileBehavior(self.context)

        self.items = []

        # Do listing by default, must be explictly disabledc
        if not behavior.mobileFolderListing:
            return

        # Do not list if already doing folder listing
        template = self.getActiveTemplate()
        print "Active template id:" + template
        if template in self.getTemplateIdsNoListing():
            return

        container = self.getListingContainer()

        self.items = container.getFolderContents({}, batch=False)



    def hasListing(self):
        """
        Check whether mobile folder listing is enabled for a particular content type.
        """
        return len(self.items) > 0


class MobileTracker(grok.Viewlet):
    """ Site visitors tracking code for mobile analytics """

    def update(self):
        context = aq_inner(self.context)

        # provided in gomobile.mobile.tracking.view
        tracker_renderer = getMultiAdapter((context, self.request), name="mobiletracker")

        self.tracking_code = tracker_renderer()