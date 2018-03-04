/*

	Sitemap Styler v0.1
	written by Alen Grakalic, provided by Css Globe (cssglobe.com)
	visit http://cssglobe.com/lab/sitemap_styler/

*/


(function($){
    $.fn.treemenu = function(options){

        var defaults = {},
        opt = $.extend(defaults, options);
        return this.each(function(){
            var $this = this,

                toggleOffElem = function( elem ){

                },

                toggleOff = function( elem ){

                },

                toggleOnElem = function( el ){

                },

                toggleOn = function( elem ){
                    for( var el in elem ){
                        toggleOnElem( el );
                    }
                },

                showActive = function() {
                    $this.find('.active').each(function(){ toggleOn( $this ) });
                },

                clickSpan = function(){

                },

                createSpan = function( li ) {
                    var span = document.createElement("span");
                        span.className = "collapsed";
                        span.onclick = clickSpan;
                    li.appendChild(span);

                };



        });

    }
})(jQuery);



this.sitemapstyler = function(){
	var sitemap = document.getElementById("sitemap")
	if(sitemap){

		this.listItem = function(li){
			if(li.getElementsByTagName("ul").length > 0){
				var ul = li.getElementsByTagName("ul")[0];
				ul.style.display = "none";
			};
		};

		var items = sitemap.getElementsByTagName("li");
		for(var i=0;i<items.length;i++){
			listItem(items[i]);
		};

	};
};

window.onload = sitemapstyler;
