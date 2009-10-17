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
    ztc.installPackage('gomobiletheme.basic')



# The order here is important.
setup_zcml()
ptc.setupPloneSite(products=['gomobile.mobile', "gomobiletheme.basic"])

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


class ThemeTestCase(BaseTestCase):
    """
    Test gomobiletheme.basic functionality.
    """

    def afterSetUp(self):
        self._refreshSkinData()

    def setDiscriminateMode(self, mode):
        """
        Spoof the following HTTP request media.

        @param: "mobile", "web" or other MobileRequestType pseudo-constant
        """
        TestMobileRequestDiscriminator.setModes([mode])

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

        self.browser.open(self.portal.absolute_url() +"/" + file)
        self.assertEqual(self.browser.headers["content-type"], "image/gif")


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
        self._refreshSkinData()
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
