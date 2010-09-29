$(document).ready(function () {
    $('li.action-search').click(function (e) {
        e.preventDefault();
        $("#search-box-top").slideToggle("fast");
        $("li.action-search").toggleClass("action-search-selected");
    });
    
    $('#searchboxtop').blur(function(){
        if (this.value == '') {
            this.value = 'Search...';
        }
        })
        .focus(function(){
            if (this.value == 'Search...') {
                this.value = '';
            }
        });
    
    $('#searchboxbottom').blur(function(){
        if (this.value == '') {
            this.value = 'Search...';
        }
        })
        .focus(function(){
            if (this.value == 'Search...') {
                this.value = '';
            }
        });
    
});