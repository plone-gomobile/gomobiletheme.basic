from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.skinny import main as skinny_main

class Main(skinny_main.Main):
    """ Main view of the theme.
    """
    
    template = ViewPageTemplateFile('templates/main.pt')
    