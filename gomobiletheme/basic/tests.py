__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

from AccessControl import Unauthorized

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc
from zope.component import getUtility

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.PloneTestCase.layer import PloneSite

from gomobile.mobile.tests import utils as test_utils

from gomobile.mobile.interfaces import MobileRequestType, IMobileRequestDiscriminator
from gomobile.mobile.tests.utils import TestMobileRequestDiscriminator


# ZCML to override media discriminator with test stub
ZCML_FIXES="""
<configure
    xmlns="http://namespaces.zope.org/zope">
 <utility
     provides="gomobile.mobile.interfaces.IMobileRequestDiscriminator"
     factory="gomobile.mobile.tests.utils.TestMobileRequestDiscriminator" />
</configure>
"""


MOBILE_HTML_MARKER = "apple-touch-icon"


@onsetup
def setup_zcml():

    fiveconfigure.debug_mode = True
    import gomobiletheme.basic
    zcml.load_config('configure.zcml', gomobiletheme.basic)
    zcml.load_string(ZCML_FIXES)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    ztc.installPackage('gomobile.mobile')
    ztc.installPackage('gomobile.convergence')
    ztc.installPackage('gomobiletheme.basic')



# The order here is important.
setup_zcml()
ptc.setupPloneSite(products=['gomobile.mobile', 'gomobile.convergence', "gomobiletheme.basic"])

class BaseTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    def setUp(self):
        ptc.FunctionalTestCase.setUp(self)

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
        """
        Spoof the following HTTP request media.

        @param: "mobile", "web" or other MobileRequestType pseudo-constant
        """
        TestMobileRequestDiscriminator.setModes([mode])

        # skin manager must update active skin for the request
        self._refreshSkinData()

class ThemeTestCase(BaseTestCase):
    """
    Test gomobiletheme.basic functionality.
    """

    def afterSetUp(self):
        self._refreshSkinData()

    def prepare_render(self, object):
        """
        Render page both logged in and logged out.

        The object must implement simple workflow and must not be published.

        """

        self.browser.open(object.absolute_url())

        return self.browser.contents

    def assertNotDefaultPloneTheme(self, html):
        self.assertFalse("http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" in html, "The rendered page used default Plone theme")

    def test_installed(self):
        """ Check that we are installed
        """
        mobile_properties = self.portal.portal_properties.mobile_properties
        self.assertEqual(mobile_properties.mobile_skin, "Plone Go Mobile Default Theme")

        skins = self.portal.portal_skins
        self.assertTrue("gomobiletheme_basic" in skins.objectIds(), "Had skin layers " + str(skins.objectIds()))

    def test_load_resource(self):
        """
        See that our static resources are loaded correctly.
        """

        file = "++resource++gomobiletheme.basic/logo.gif"

        #self.browser.open(self.portal.absolute_url() +"/" + file)
        #self.assertEqual(self.browser.headers["content-type"], "image/gif")
        pass

    def test_render_main_template(self):
        """
        Render main template in mobile mode
        """
        self.setDiscriminateMode(MobileRequestType.MOBILE)

        html = self.prepare_render(self.portal)

        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)

    def test_render_web_mode(self):
        """
        Check that Plone renders page normally if not in mobile mode
        """
        self.setDiscriminateMode(MobileRequestType.WEB)
        utility = getUtility(IMobileRequestDiscriminator)
        #import pdb ; pdb.set_trace()
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
        """ Assert no exceptions risen when we are rendering old fashioned page template and HTTP POST """

        from Products.PloneTestCase.setup import portal_owner, default_password
         # Go admin
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/login_form")

        html = browser.contents
        self.assertNotDefaultPloneTheme(html)
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)

        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()

        html = browser.contents
        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)

    def test_mobile_folder_listing(self):
        """ """
        from gomobiletheme.basic.viewlets import MobileFolderListing
        self.setDiscriminateMode(MobileRequestType.MOBILE)

        # Create a sample folder
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Folder", "folder")
        self.portal.folder.invokeFactory("Document", "page1")
        self.portal.folder.invokeFactory("Document", "page2")

        # Get the viewlet
        viewlet = MobileFolderListing(self.portal.folder, self.portal.folder.REQUEST, None, None)
        self.assertNotEqual(viewlet, None, "Could not find mobilefolderlisting viewlet")
        viewlet.update()

        self.assertEqual(len(viewlet.items), 2)

        # Now set one of the pages as default
        #default_page_helper = getMultiAdapter((self.portal.folder, self.portal.REQUEST), name='default_page')
        #default_page_helper.
        self.portal.folder.default_page = "page1"
        viewlet.update()
        self.assertEqual(len(viewlet.items), 1)

    def test_empty_analytics(self):
        """ Render empty analytics viewlet """
        from gomobiletheme.basic.viewlets import MobileTracker
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        self.portal.portal_properties.mobile_properties.tracker_name = ""
        self.portal.portal_properties.mobile_properties.tracking_id = ""
        viewlet = MobileTracker(self.portal, self.portal.REQUEST, None, None)
        viewlet.update()
        viewlet.render()

    def test_admob_analytics(self):
        """ Render AdMob analytics code """
        from gomobiletheme.basic.viewlets import MobileTracker
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        self.portal.portal_properties.mobile_properties.tracker_name = "admob"
        self.portal.portal_properties.mobile_properties.tracking_id = "123"


        viewlet = MobileTracker(self.portal, self.portal.REQUEST, None, None)
        viewlet.update()
        viewlet.render()


from zope.component import getMultiAdapter, getUtility

from gomobile.convergence.interfaces import IOverrider
from gomobile.convergence.overrider.base import IOverrideStorage

class TestMobileOverrides(BaseTestCase):
    """ Check that field level overrides are rendered correctly in mobile mode.

    TODO This should be moved to gomobile.convergence
    """

    def afterSetUp(self):
        self._refreshSkinData()

    def create_doc(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")

    def test_helper_view_mobile(self):
        """
        See that we get proper proxy object through helper view.
        """
        self.setDiscriminateMode(MobileRequestType.MOBILE)
        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Not reached")
        overrider = IOverrider(doc)
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["Title"]
        storage.Title = u"Foobar"

        helper = doc.restrictedTraverse("multichannel_overrider")
        context = helper() # Return mobile proxy object with overriden values

        # In mobile mode, you get override
        self.assertEqual(context.Title(), u"Foobar")

    def test_helper_view_web(self):
        """
        See that we get proper proxy object through helper view.
        """
        self.setDiscriminateMode(MobileRequestType.WEB)
        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Not reached")
        overrider = IOverrider(doc)
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["Title"]
        storage.Title = u"Foobar"

        helper = doc.restrictedTraverse("multichannel_overrider")
        context = helper() # Return mobile proxy object with overriden values

        # In web mode, you dont get override
        self.assertEqual(context.Title(), "Not reached")

    def test_render_mobile_override(self):
        """ Render a document with mobile overrides enabled.

        """

        self.setDiscriminateMode("mobile")


        self.create_doc()
        doc = self.portal.doc
        doc.setTitle("Not reached") # This title should not be visible in mobile mode
        overrider = IOverrider(doc)
        storage = IOverrideStorage(doc)
        storage.enabled_overrides = ["Title"]
        storage.Title = u"Foobar"

        self.portal.portal_workflow.doActionFor(doc, "submit")
        self.portal.portal_workflow.doActionFor(doc, "publish")


        browser = self.browser
        browser.open(self.portal.doc.absolute_url())
        html = browser.contents

        self.assertTrue(MOBILE_HTML_MARKER in html, "Got page:" + html)
        assert "Foobar" in html

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ThemeTestCase))
    suite.addTest(unittest.makeSuite(TestMobileOverrides))
    return suite
