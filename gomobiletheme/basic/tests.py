__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

from AccessControl import Unauthorized

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from gomobile.mobile.tests import utils as test_utils

from gomobile.mobile.interfaces import MobileRequestType 

@onsetup
def setup_zcml():

    fiveconfigure.debug_mode = True
    import gomobiletheme.basic
    zcml.load_config('configure.zcml', gomobiletheme.basic)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('collective.skinny')
    ztc.installPackage('gomobile.mobile')    
    ztc.installPackage('gomobiletheme.basic')
    
# The order here is important.
setup_zcml()
ptc.setupPloneSite(products=['gomobile.mobile', "gomobiletheme.basic"])

class BaseTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    
    def setUp(self):
        ptc.PloneTestCase.setUp(self)
        
        # Enable unit test friendly errors
        
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising
        
        from Products.Five.testbrowser import Browser
        
        self.browser = Browser()
        self.browser.handleErrors = False
        

            
    def setDiscriminateMode(self, mode):
        test_utils.setDiscriminateMode(self.portal.REQUEST, mode)        
    
MOBILE_HTML_MARKER = "//WAPFORUM//DTD XHTML Mobile 1.1//EN"

class ThemeTestCase(BaseTestCase):
    """
    Test gomobiletheme.basic functionality.
    """
    
    def prepare_render(self, object):
        """
        Render page both logged in and logged out.
        
        The object must implement simple workflow and must not be published. 
                
        """
                
        self.browser.open(object.absolute_url())
        
        return self.browser.contents
        
    def test_installed(self):
        """ Check that we are installed
        """
        mobile_properties = self.portal.portal_properties.mobile_properties
        self.assertEqual(mobile_properties.theme_interface, "gomobiletheme.basic.interfaces.IThemeLayer")

    def test_load_resource(self):
        """
        See that our static resources are loaded correctly.
        """
        
        file = "++resource++gomobiletheme.basic/logo.gif"
        
        self.browser.open(self.portal.absolute_url() +"/" + file)
        self.assertEqual(self.browser.headers["content-type"], "image/gif")

        
    def test_render_main_template(self):
        """
        Render main template in mobile mode
        """
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        
        
        html = self.prepare_render(self.portal)
        
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)
        
    def test_render_main_template_web(self):
        """
        Check that Plone renders page normally if not in mobile mode
        """
        self.setDiscriminateMode(MobileRequestType.WEB)
        
        html = self.prepare_render(self.portal)

        self.assertFalse(MOBILE_HTML_MARKER in html, "Got page:" + html)
            
    def test_render_page(self):
        """ Assert no exceptions risen """
        
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "page")
        
        object = self.portal.page
        self.portal.portal_workflow.doActionFor(object, "submit")        
        self.portal.portal_workflow.doActionFor(object, "publish")
        
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        
        
        html = self.prepare_render(self.portal.page)
            
    def test_render_folder(self):
        """ Assert no exceptions risen """
        
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Folder", "folder")

        object = self.portal.folder
        #self.portal.portal_workflow.doActionFor(object, "submit")        
        self.portal.portal_workflow.doActionFor(object, "publish")

        self.setDiscriminateMode(MobileRequestType.MOBILE)
    
        html = self.prepare_render(self.portal.folder)
        
    def test_render_login(self):
        """ Assert no exceptions risen """
        
        self.setDiscriminateMode(MobileRequestType.MOBILE)

        from Products.PloneTestCase.setup import portal_owner, default_password   
         # Go admin
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/login_form")
        
        html = browser.contents
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)
        
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        
        html = browser.contents
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)
                