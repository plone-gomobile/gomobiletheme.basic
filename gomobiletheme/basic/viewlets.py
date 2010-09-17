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


try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3

from gomobile.mobile.interfaces import IMobileSiteLocationManager, MobileRequestType, IMobileImageProcessor
from gomobile.mobile.behaviors import IMobileBehavior
from gomobile.mobile.utilities import getCachedMobileProperties
from gomobile.mobile.browser.resizer import getUserAgentBasedResizedImageURL

from mobile.heurestics.contenttype import get_content_type_and_doctype

from interfaces import IThemeLayer

try: 
    # Plone 4 and higher 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3 

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
        """ Get static resource URL.
        
        This will point to Zope 3 resource directory from where to load 
        resources for the head.
        
        * common.css
        
        * highend.css
        
        * lowend.css
        
        * logo.png
        
        * apple-touch-icon.png
        
        The actual registration of static media is performed 
        by five.grok, by picking up *static* folder in your add-on
        product.        
        """
        return self.portal_url + "/" + "++resource++gomobiletheme.basic"

    def is_plone4(self):
        """ Allow major viewlet change compatiblity between Plone versions from tempalte """
        return PLONE_VERSION > 3
    
    
    def generator(self):
        """
        @return: Exposed generator name 
        """
        return "Plone - http://plone.org"

    def update(self):
        portal_state = getView(self.context, self.request, "plone_portal_state")
        self.portal_url = portal_state.portal_url()

        # Create <base href=""> directive of <head>
        if IFolderish.providedBy(self.context):
            # Folderish URLs must end to slash
            self.base = self.context.absolute_url()+'/'
        else:
            self.base = self.context.absolute_url()
            
        
class AdditionalHead(Head):
    """
    Extra tags included in <head> which do not conflict with gomobiletheme.basic resources.
    
    See plonecommunity.app for usage example.
    """
    
    grok.template("additionalhead")
            
class Doctype(grok.Viewlet):
    """ Spit out document type according to what the HTTP user agent expects.
    
    NOTE: Hardcoded for XHTML basic now
    """
    grok.name("doctype")
            
    def render(self):
        content_type, doctype = get_content_type_and_doctype(self.request) 
        return doctype 

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

        path = self.getLogoPath()
        
        portal_state = getView(self.context, self.request, "plone_portal_state")
        self.portal_url = portal_state.portal_url()

        url = self.getLogoPath()
                        
        processor = getMultiAdapter((self.context, self.request), IMobileImageProcessor)
                
        parameters = {
                         "width" : "auto",
                         "height" : "85", # Maximum logo height
                         "padding_width" : 10,
                         "conserve_aspect_ration" : True,
                    }

        self.logo_url = processor.getImageDownloadURL(url, parameters)
                    

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
    
    def fixSectionText(self, text):
        """ Use non-breaking spacebar to make sure that section name will stay on one line.
        """
        
        # &#160; == &nbsp;
        # but we must remain XML compatible
        return text.replace(" ", "&#160;")
        
    
    def fixSections(self, tabs):
        """ Make sure that the text of sections is not broken across two lines in narrow mobile screen.
        
        @param tabs: Sequence of tabs to be fixed in-place
        """
        for tab in tabs:
            tab.name = self.fixSectionText(text)
    
    def update(self):

        grok.Viewlet.update(self)

        # Get tabs (top level navigation links)
        context_state = getView(self.context, self.request, u'plone_context_state')
        
        
        # This is for Plone 4 compatibility - topLevelTabs() call signature is different
        
        if PLONE_VERSION >= 4:
            actions = context_state.actions("portal_tabs")
        else:
            actions = context_state.actions()
            
        portal_state = getView(self.context, self.request, "plone_portal_state")
        self.portal_url = portal_state.portal_url()

        portal_tabs_view = getView(self.context, self.request, u'portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)


    def get_web_site_url(self):
        """
        @return: string url, web version of the same page
        """        
        return self.context.absolute_url() + "/@@go_to_web_site"



class FooterText(grok.Viewlet):
    """ Free-form HTML text at the end of the page """

    def update(self):
        super(grok.Viewlet, self).update()


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


        context = self.context.aq_inner
        helper = helper.__of__(context)

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
    
    def getMobileTrackerId(self):
        """ Subclasses may override to return different tracker e.g. by language settings.
        
        The default behavior is that tracker_renderer view gets one from mobile_properties
        if None is given.
        """
        return None

    def update(self):
        context = aq_inner(self.context)

        # provided in gomobile.mobile.tracking.view
        tracker_renderer = getMultiAdapter((context, self.request), name="mobiletracker")

        trackerId = self.getMobileTrackerId()
        self.tracking_code = tracker_renderer(trackerId)

class Description(grok.Viewlet):
    """
    Render <meta description>
    """
    
    def hasDescription(self):
        """
        """
        return self.getDescription() != None
    
    def getDescription(self):
        """
        Dublin core metadata should provide Description() function on context.
        """
        description_cb = getattr(self.context, "Description", None)
        if description_cb:
            return description_cb()
        else:
            return None
    
    

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

