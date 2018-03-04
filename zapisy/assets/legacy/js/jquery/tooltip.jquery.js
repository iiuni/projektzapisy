/**
 *  jQuery Tooltip Plugin
 *  @requires jQuery v1.3 or 1.4
 *  http://intekhabrizvi.wordpress.com/
 *
 *  Copyright (c)  Intekhab A Rizvi (intekhabrizvi.wordpress.com)
 *  Licensed under GPL licenses:
 *  http://www.gnu.org/licenses/gpl.html
 * 
 *  Version: 3.2.2
 *  Dated : 24-Mar-2010
 *	24-Jan-2010 : V1.1 : Build tooltip without static file.
 *	07-Feb-2010 : V3.0 : ToolTip Fadein and fadeout effects added, with some coding improvement - Thx Ian for 	pointing it. And also building one seprate div tag to hold tooltip data, so no need to create file, or no need to use id tag of tooltip.
 *	08-Feb-2010 : V3.1 : Now float to right or left when tooltip come near to the browser border, thanks Max for suggestion.
 *	09-Feb-2010 : V3.2 : Now you can limit your tooltips width and height with option named, 'width', 'height' by default both run on 'auto' value;
 *	24-Mar-2010 : V3.2.1 : Now you can change default help cursor with any diffrent cursor just 'cursor' option to set by default its use 'help' cursor;
 *	08-Apr-2010 : V3.2.2 : One Bug Fix related to option 'dataAttr'. Thx Stephen for reporting it.
 */
(function($) {
	jQuery.fn.tooltip = function(options){
		 var defaults = {  
		    offsetX: 15,  //X Offset value
		    offsetY: 10,  //Y Offset value
		    fadeIn : '200', //Tooltip fadeIn speed, can use, slow, fast, number
		    fadeOut : '200',//Tooltip fadeOut speed, can use, slow, fast, number
		    dataAttr : 'data',	//Used when we create seprate div to hold your tooltip data, so plugin search div tage by using id 'data' and current href id on whome the mouse pointer is so if your href id is '_tooltip_1' then the div which hold that tooltips content should have id 'data_tooltip_1', if you change dataAttr from default then you need to build div tag with id 'current dataAttr _tooltip_1' without space
		    bordercolor: '#6CE26C', // tooltip border color
		    bgcolor: '#F8F8F8', //Tooltip background color
		    fontcolor : '#006699', //Tooltip Font color
		    fontsize : '15px', // Tooltip font size
		    folderurl : 'NULL', // Folder url, where the tooltip's content file is placed, needed with forward slash in the last (/), or can be use as http://www.youwebsitename.com/foldername/ also.
		    filetype: 'txt', // tooltip's content files type, can be use html, txt
		    height: 'auto', // Tooltip's width
		    width : 'auto', //Tooltip's Height
		    cursor : 'help' // Mouse cursor
		   };  
	var options = $.extend(defaults, options);
	//Runtime div building to hold tooltip data, and make it hidden
	var $tooltip = $('<div id="divToolTip"></div>');
	return this.each(function(){					
			$('body').append($tooltip);
			$tooltip.hide();
	//Runtime variable definations
		var element = this;
		var id = $(element).attr('class');
		var filename = options.folderurl + id + '.' + options.filetype;
		var dialog_id = '#divToolTip';
	//Tooltips main function
		$(this).hover(function(e){
				//var size = "Windows Width : " + $(document).width() + " Tip Width : " + e.pageX + "\n" + "Windows Height : " + $(document).height() + " Tip Height : " + e.pageY;
				//alert(size);
				//to check whether the tooltips content files folder is defined or not
				if(options.folderurl != "NULL"){
					$(dialog_id).load(filename);

				}else
				{
					if($('.'+options.dataAttr + '_' + id).length > 0){
						$(dialog_id).html($('.'+ options.dataAttr + '_' + id).html());
						//$(dialog_id).html(size);
					}else{
						$(dialog_id).html(id);
						//$(dialog_id).html(size);
					}
				}
				//assign css value to div
				$(element).css({'cursor' : options.cursor});
				if($(document).width() / 2 < e.pageX){
					$(dialog_id).css({
						'position' : 'absolute',
						'border' : '1px solid ' + options.bordercolor,
						'background-color' : options.bgcolor,
						'padding' : '5px 5px 5px 5px',
						'-moz-border-radius' : '5px 5px 5px 5px',
						'-webkit-border-radius' : '5px 5px 5px 5px',
						'top' : e.pageY + options.offsetY,
						'left' :  e.pageX - $(dialog_id).width() + options.offsetX,
						'color' : options.fontcolor,
						'font-size' : options.fontsize,
						'height' : options.height,
						'width' : options.width
					});
					//alert(size);
				}else{	
					$(dialog_id).css({
						'position' : 'absolute',
						'border' : '1px solid ' + options.bordercolor,
						'background-color' : options.bgcolor,
						'padding' : '5px 5px 5px 5px',
						'-moz-border-radius' : '5px 5px 5px 5px',
						'-webkit-border-radius' : '5px 5px 5px 5px',
						'top' : e.pageY + options.offsetY,
						'left' : e.pageX + options.offsetX,
						'color' : options.fontcolor,
						'font-size' : options.fontsize,
						'cursor' : options.cursor,
						'height' : options.height,
						'width' : options.width
					});
//alert(size);
				}
				//enable div block
				$(dialog_id).stop(true, true).fadeIn(options.fadeIn);	
					},function(){
				// when mouse out remove all data from div and make it hidden
				$(dialog_id).stop(true, true).fadeOut(options.fadeOut);	
					}).mousemove(function(e){	
				// to make tooltip moveable with mouse	
				if($(document).width() / 2 < e.pageX){		
				$(dialog_id).css({
					'top' : e.pageY + options.offsetY,
					'left' : e.pageX - $(dialog_id).width(),
					'height' : options.height,
					'width' : options.width
					});
				//$(dialog_id).html(e.pageX - $(dialog_id).width());
				}else{
					$(dialog_id).css({
					'top' : e.pageY + options.offsetY,
					'left' : e.pageX + options.offsetX,
					'height' : options.height,
					'width' : options.width
					});
				}
			});
		});
	};
 })(jQuery);

//FINISH, simple isnt it ??
//if you like it or have any suggestions / comments , or you have some idea to make it better, 
//or you need some more fetures in it PLS PLS PLS let me know that at
//i.rizvi@hotmail.com
//Thank you for using my plugin
