from five import grok
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.interface import Interface

from interfaces import IThemeLayer
from collective.fastview.template import PageTemplate

# Use templates directory to search for templates.
grok.templatedir('templates')

# Viewlets are active only when gomobiletheme.basic theme layer is activated
grok.layer(IThemeLayer)

from Products.ATContentTypes.interface import IATDocument
class MobileDocumentDefault(grok.CodeView):
    """ A page renderer.

    Render Page content for anonymous visitors.
    """
    grok.context(IATDocument)
    grok.require('zope2.View')

    # Render template in collective.fastview global define free mode
    render = PageTemplate("templates/content/document.pt")

from Products.ATContentTypes.interface import IATFolder
class MobileFolderDefault(grok.CodeView):
    """ A page renderer.

    Render Page content for anonymous visitors.
    """
    grok.context(IATFolder)
    grok.require('zope2.View')

    # Render template in collective.fastview global define free mode
    #render = PageTemplate("templates/content/folder.pt")

    def render(self):
        """
        """

        # Check if we have a default page
