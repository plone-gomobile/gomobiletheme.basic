"""

    Various reusable page parts used in main_template.pt and elsewhere.

"""

import sys, os

from Acquisition import aq_inner
from zope.component import getMultiAdapter

from zope.interface import Interface
from zope.component import queryMultiAdapter, getMultiAdapter

from five import grok
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.layout.viewlets.interfaces import IPortalHeader
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.layout.viewlets import common as plone_common_viewlets

from gomobile.mobile.interfaces import IMobileSiteLocationManager, MobileRequestType
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
        """Returns list of languages."""
        if self.tool is None:
            return []

        bound = self.tool.getLanguageBindings()
        current = bound[0]

        def merge(lang, info):
            info["code"]=lang
            if lang == current:
                info['selected'] = True
            else:
                info['selected'] = False
            return info

        languages = [merge(lang, info) for (lang,info) in
                        self.tool.getAvailableLanguageInformation().items()
                        if info["selected"]]

        # sort supported languages by index in portal_languages tool
        supported_langs = self.tool.getSupportedLanguages()
        def index(info):
            try:
                return supported_langs.index(info["code"])
            except ValueError:
                return len(supported_langs)

        return sorted(languages, key=index)

    def update(self):
        self.tool = getToolByName(self.context, 'portal_languages', None)

class Footer(grok.Viewlet):
    """ Sections + footer text
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


    def get_web_site_url(self):
        """
        @return: string url, web version of the same page
        """
        context = self.context.aq_inner
        url = self.request["ACTUAL_URL"]
        location_manager = getMultiAdapter((context, self.request), IMobileSiteLocationManager)
        new_url = location_manager.rewriteURL(url, MobileRequestType.WEB)

        # Add redirecor preventing GET parameter
        if "?" in new_url:
            new_url += "&force_web"
        else:
            new_url += "?force_web"

        return new_url



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
    """ List content of the folder or the parent folder on every page.

    Because mobile sites don't have navigation portlet
    we need to have a way to show what's inside the folder.
    """

    def update(self):
        """ """

        grok.Viewlet.update(self)

        # Get listing helper from gomobile.mobile
        helper = getMultiAdapter((self.context, self.request), name='mobile_folder_listing')

        # None or iterable of content item objects
        self.items = helper.constructListing()


    def hasListing(self):
        """
        Check whether mobile folder listing is enabled for a particular content type.
        """

        # Note: Can't use len() since iterable don't have length

        return self.items != None


class MobileTracker(grok.Viewlet):
    """ Site visitors tracking code for mobile analytics """

    def update(self):
        context = aq_inner(self.context)

        # provided in gomobile.mobile.tracking.view
        tracker_renderer = getMultiAdapter((context, self.request), name="mobiletracker")

        self.tracking_code = tracker_renderer()


class DocumentActions(plone_common_viewlets.ViewletBase):
    """
    Override document actions. Document actions (like) print is directly
    called from many templates. Thus, it is likely this viewlet leaks
    to mobile code. We don't want print in mobile.

    This viewlet is registered in configure.zcml.
    """

    def update(self):
        pass

    def render(self):
        return u""
