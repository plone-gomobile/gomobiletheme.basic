$(document).ready(function () {
    $('li.action-search').click(function (e) {
        e.preventDefault();
        $("#search-box-top").slideToggle("fast");
        $("li.action-search").toggleClass("action-search-selected");
    });
    
    $('#searchboxtop').blur(function(){
        $('#searchboxtop').toggleClass("blackText");
        if (this.value == '') {
            this.value = 'Search...';
        }
        })
        .focus(function(){
            $('#searchboxtop').toggleClass("blackText");
            if (this.value == 'Search...') {
                this.value = '';
            }
        });
    
    $('#searchboxbottom').blur(function(){
        $('#searchboxbottom').toggleClass("blackText");
        if (this.value == '') {
            this.value = 'Search...';
        }
        })
        .focus(function(){
            $('#searchboxbottom').toggleClass("blackText");
            if (this.value == 'Search...') {
                this.value = '';
            }
        });
    
});