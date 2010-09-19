
/**
 * Load upscaled action icon images if we detect high enough screen resolution.
 * 
 * We could scale these icons at the server end, but doing pixel size scales
 * without orignal vector source yields to very bad results.
 * 
 */
function fixActionImages() {
        var width = jQuery(window).width();

	if(width > 480) {
	       // Assume smartphone with resolution in 640 x 480 range
	       
	       // Bump size to 24x24 -> 48x48
	       jQuery("img").each( function() {
	       	       var src = jQuery(this).attr("src");
		       src = src.replace("++resource++gomobiletheme.basic/24/", "++resource++gomobiletheme.basic/48/");		     
	       	       jQuery(this).attr("src", src);
	       });
	}
}


jQuery(document).ready(function() {
        fixActionImages();
})
