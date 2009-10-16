from five import grok
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.layout.viewlets.interfaces import IPortalHeader
from zope.interface import Interface

from interfaces import IThemeLayer
from collective.fastview.template import PageTemplate

# Use templates directory to search for templates.
grok.templatedir('templates')

# Viewlets are active only when gomobiletheme.basic theme layer is activated
grok.layer(IThemeLayer)

class Document(grok.View):
    """ A page renderer.

    Render Page content for anonymous visitors.
    """

    # Render template in collective.fastview global define free mode
    template = PageTemplate("templates/content/document.pt")

