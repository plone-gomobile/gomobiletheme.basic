Plone® Logo Pack

  Plone® is a registered trademark of the Plone Foundation.

  Projects and companies that use Plone are encouraged to incorporate the Plone
  logo on their websites, brochures, packaging, and elsewhere to indicate
  suitability for use with Plone or implementation using Plone.

  However, you are not allowed to use the logo or its likeness as a company logo
  or for any other commercial purpose without permission from the Plone
  Foundation. Regional Plone User Groups have explicit permission to use the
  logo in their materials, as long as they don't make any direct profit from it.

Download

  "Download the Plone logo pack":Plone%20Logo%20Pack%20v1.zip (1.3MB ZIP)

  The original Plone logo design was done by "Vidar
  Andersen":http://blacktar.com in 1999, the logo refresh was done by "Jola
  Hyjek":http://www.linkedin.com/in/hyjek in 2008.

  The logo pack contains the following bitmap and vector variants of the logo:

  - **SVG format** — SVG export from Illustrator.

  - **PDF format** — opens in any application that supports PDF.

  - **Illustrator format** — the original master which should open as a vector
    image in Adobe Illustrator.

  - **PNG format** — the preferred format for web use. 

    - Available pre-rendered logo heights are: 16px, 32px, 40px, 48px, 56px,
      64px, 128px, 256px.

    - All images are optimized (using OptiPNG and pngcrush, see below) 
      and use alpha transparency.

    - The PNGs use an 8-bit palette to degrade gracefully without PNG hacks even
      in Internet Explorer 6 ("see
      how":http://www.sitepoint.com/blogs/2007/09/18/png8-the-clear-winner/).
      However, the antialiasing is rough on the edges, so we recommend the
      version with white background instead of transparent if you need it to
      look perfect in IE6. We include a pre-rendered version with white
      background.

    - The images has been compressed and stripped of any color profiles ("see
      why":http://hsivonen.iki.fi/png-gamma/)
 
    - You can easily use the logo on backgrounds that are not white, and get
      great antialiasing.

Font and Colors

  The font used in the logo is called 
  <a href="http://en.wikipedia.org/wiki/DIN_(typeface)">DIN</a>. 

  The color values for the official Plone logo are:

  - **RGB**: (0, 131, 190)

  - **Hex**: #0083be

  - **Pantone**: 7461C

Guidelines for Use

  The Plone logo is a worldwide registered trademark of the "Plone
  Foundation":/foundation, which is responsible for defending against any
  damaging or confusing uses of the trademark.

  For details, consult the "Plone Trademark Usage 
  Policy":http://plone.org/foundation/committees/ip/policy.

  In general, we want the logo to be used as widely as possible to promote Plone
  and the Plone community. Derivative versions of the Plone logo are generally
  prohibited, as they dilute Plone's brand identity. However, please "contact
  the IP committee via email":mailto:ip-committee@lists.plone.org if you have
  any questions.

T-shirts and other Merchandise

  Making your own shirts with the Plone logo is OK, as long as the profits are
  donated to the Plone Foundation. Please seek permission from the Plone
  Foundation if you are planning to sell merchandise that shows the Plone logo.

Creation notes

  PNGcrush gamma removal + OptiPNG compression used::

    pngcrush -rem gAMA -rem cHRM -rem iCCP -rem sRGB (files)
    optipng -o7 (files)

  Creating the zip file without system files if you do it on a Mac::

    cd [directory]
    zip -r "Plone Logo Pack v1.zip" *


History

  v1 (Apr 2, 2009): Official release of the color-corrected logo. Changes:

  - The official colors were off in the prerelease version because of color
    profile issues. The correct colors are: Web: #0083be, Pantone: 7461C

  - iPhone and Mac OS X style icons added.

  - Favicon for browser use (bookmarks etc) was added. The default favicon.ico
    file has two sizes embedded: 16px and 32px. There are two additional files
    available that includes 48px and 64px icons too, but be aware that these are
    larger downloads, and might not be a sensible default. They are included for
    future use, when default sizes might be different.

  - The registered trademark symbol was moved slightly to improve balance.

  - The 16px logo has been hand-tweaked for increased legibility.

  - All PNGs have had their gamma and color profiles removed by running 
    'pngcrush -rem gAMA -rem cHRM -rem iCCP -rem sRGB'
    and then further optimized by running
    'optipng -o7'.


  v0.9 (Feb 4, 2008): Prerelease version of the logo refresh.

