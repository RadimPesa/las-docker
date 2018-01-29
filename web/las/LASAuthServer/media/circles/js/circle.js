var windowWidth = $(window).width(),
	windowHeight = $(window).height(),	
 	circleLeft = $('.circle-left-ctn').outerWidth(),
	circleright = $('.circle-right-ctn').outerWidth(),
	circleWidth = windowWidth - circleLeft - 22 +"px";
	circleHeight = windowHeight - 52 +"px";

var selectedClass = 'ui-state-highlight',
    clickDelay = 600,
    // click time (milliseconds)
    lastClick, diffClick; // timestamps

var clickFunction = function() {  
  	$(".circle-list-ul > .circle-card")
    .on('mousedown mouseup', function(e) {
     	if (e.type == "mousedown") {
            lastClick = e.timeStamp; // get mousedown time
		
        } else {
            diffClick = e.timeStamp - lastClick;
            if (diffClick < clickDelay) {
                // add selected class to group draggable objects
                $(this).toggleClass(selectedClass);
            }
        }
    })
};





 
jQuery( document ).ready(function( $ ) {

    initCircles();

});
function initCircles(){
    $(".circle-list-ul > .circle-card").draggable({ 
	  	cursor: "move",
		helper: 'clone',
		distance: 15,
		grid: [ 50, 20 ],
		iframeFix: true,
		start: function(e, ui) {
           ui.helper.addClass(selectedClass);
        },
		stop: function(e, ui) {
            $('.' + selectedClass).css({
                top: 0,
                left: 0
            }).removeClass(selectedClass);
        },
        drag: function(e, ui) {
            $('.' + selectedClass).css({
                top: ui.position.top,
                left: ui.position.left
            });
        }
		
	});
    $(".circle-list-ul").droppable({
		greedy: true,
		hoverClass: "data-hover",
		accept: ".circle-drop-item > .circle-card",
        over: function (event, ui) {
            var folderName = $(event.target).attr('id');
            var targetFolder = $(event.target).attr('id');
            var parentClass =  $(ui.helper).parents('li')
            $(ui.helper).find('.draggable-tooltip').remove();
            $(ui.helper).find('.circle-bdr').append($('<span class="draggable-tooltip"></span>'));

        },
        out: function(event,ui){
           $(ui.helper).find('.draggable-tooltip').remove();
           $(ui.helper).find('.circle-bdr').append($('<span class="draggable-tooltip delete"></span>'));
        },
	    drop: function( event, ui ) {
            username=$(ui.draggable).clone()[0].getAttribute('username');
            wg=$(ui.draggable).clone()[0].getAttribute('wg');
            console.log(this);
            tag=$(ui.helper)[0].getAttribute('data-id').split('_')[0];
            if(circlesList[wg][tag].indexOf(username) != -1) {
                circlesList[wg][tag].splice(circlesList[wg][tag].indexOf(username), 1);

            }
            $(ui.helper).find('.draggable-tooltip').remove();
            $(ui.helper).find('.circle-bdr').append($('<span class="draggable-tooltip delete"></span>'));
    	}
    });

	$(".circle-drop").droppable({
		greedy: true,
		tolerance: "pointer",
		hoverClass: "drop-hover",
		over: function (event, ui) {
			outsideCircle = 1;
    		$(ui.helper).find('.draggable-tooltip').remove();
		},
     	
		drop: function( event, ui ) {
		   var cloneItem;
  		   if($('.' + selectedClass).length == 1){    
               cloneItem = $($('.' + selectedClass)[0]).removeClass('left-drop-card ui-draggable-dragging draggable' + selectedClass).addClass('dingdon').css({
                   position:'',
                   top: 0,
                   left: 0
               }).clone()
               username=cloneItem[0].getAttribute('username');
               wg=cloneItem[0].getAttribute('wg');
               tag=($(this)[0].getAttribute('identifier')).split("_")[0];
               if(circlesList[wg][tag].indexOf(username) == -1) {
                    circlesList[wg][tag].push(username);
               }
               else return false;
            }
            else{
                cloneItem = $('.' + selectedClass + ':not(.ui-draggable-dragging)').removeClass('left-drop-card draggable' + selectedClass).addClass('dingdon').css({
                    position:'',
                    top: 0,
                    left: 0
                }).clone()

            }
            console.log(wg);
	 		deleteImage(cloneItem , this ,tag ,wg);
			var dropItmeList = $(this).find('.circle-drop-item li').length;
			$(this).find('.members').text(dropItmeList);
			if(cloneItem.hasClass(selectedClass)){
 			    $(this).find(".dorp-action.add-new").text(cloneItem.length)
        		$(this).find(".dorp-action.add-new").animate({"margin-top": "-25px","opacity" : "1"}, 450, function(){	
                    $(this).animate({"margin-top": "0px","opacity" : "0" }, 450); 
				});
			}
		},
 	
		out: function (event, ui) {
			outsideCircle = 0;
			if(!$(ui.helper).hasClass('left-drop-card')){
				$(ui.helper).find('.draggable-tooltip').remove();
  				$(ui.helper).find('.circle-bdr').append($('<span class="draggable-tooltip delete"></span>'));
			}
  		},
	});
}
	function recycleImage( $item, data ) {
		$item.fadeOut(function() {
        $item
            .appendTo( ".circle-list-ul" )
            .fadeIn(function() {
		        $item
                    .removeAttr("style").addClass('left-drop-card').removeClass('dingdon')
        		    .find( "img" )
                    .removeAttr("style")
		    })
        });

  	   $item.draggable({
           helper: 'clone',
           revertDuration: 10,
           containment: '.demo',	
           start: function(e, ui) {
	 		   outside = 0
               ui.helper.addClass(selectedClass);
           },

            stop: function(e, ui) {
                $('.' + selectedClass).css({
                    top: 0,
                    left: 0
                }).removeClass(selectedClass);
            },

            drag: function(e, ui) {
                $('.' + selectedClass).css({
                    top: ui.position.top,
                    left: ui.position.left
                });
            }      
        })
    }
	
	function deleteImage($item , data ,tag , wg) {
	    var $trash = $( data );
		var itemArray = [];
		$item.each(function(){
	        var subitem = $(this);
			subitem.fadeOut(function() {
			    var $list = $( "ul", $trash ).length ?
				$( "ul", $trash ) :
				$( "<ul class='circle-drop-item ui-helper-reset clearfix'/>" ).appendTo( $trash );
				subitem.appendTo( $list).fadeIn(function() {
					subitem.animate({ 
						width: "22px" ,
						position:"absolute"
					})
        			.find( "img" )
          			.animate({ height: "22px" });
					
				});
			});
		  	subitem.draggable({ 
			    appendTo:'.content'+wg,
				helper: 'clone',
         	    start: function(e, ui) {
            		outside = 0
            		var folderName = (ui.helper).data('id');
             		var parentClass =  $(ui.helper).parents('li.circle-popover')
            		if(parentClass.has('#' + folderName)){
            	 		$(ui.helper).find('.draggable-tooltip').remove();
             		}else{
            			$(ui.helper).find('.draggable-tooltip').remove();
                		$(ui.helper).find('.circle-bdr').append($('<span class="draggable-tooltip"></span>'));
         			}
        	   },

        	   drag: function(e, ui) {	
	        	   outside = 0
      	  	   },
	
          	   stop: function(event, ui) {
		   	       var folderName = (ui.helper).data('id');
        		   var parentClass =  $(ui.helper).parents('li.circle-popover').attr('id');
			       if(outside == 0 && outsideCircle == 0){
            	        $(this).parents('li.circle-popover').find(".dorp-action.delete").animate({"margin-top": "-25px","opacity" : "1"}, 450, function(){
					        $(this).animate({"margin-top": "0px","opacity" : "0" }, 450);
					    });
        				var dropItmeList = $(this).parents('li.circle-popover').find('.circle-drop-item li').length;
        			    $(this).parents('li.circle-popover').find('.members').text(dropItmeList - 1);

                        username=this.getAttribute('username');
                        tagWG=folderName;
                        tag=tagWG.split('_')[0];
                        wg=tagWG.split('_')[1];
                        
                        if(circlesList[wg][tag].indexOf(username) != -1) {
                            circlesList[wg][tag].splice(circlesList[wg][tag].indexOf(username), 1);

                        }

					    $(this).remove();

			       }
		        },
				cursorAt: { left: 25 }
			});

			var liLength = $trash.find("ul li").length;
			if (liLength > 10){			
				subitem.css({
					display:'none'
				})
			}
			move(liLength, subitem,1500,1 ,tag);				
  		    subitem.attr('data-id',subitem.parents('li.circle-popover').attr('id'))
		}) 
      }

	 function move(count,$elem,speed,turns ,tag){
		var $circle = $elem;		
        while ($("[pos='"+tag+"_"+count+"']").length > 0)
            count++
        $circle.attr('pos',tag+"_"+count);
		/* make the circle appear in a circular movement */
        var end = 180 - 360 * (turns-1);				
        $circle
        .animate({
            path : new $.path.arc({
              center : [39,39],
              radius : 40,
              start	: 180,
              end		: -180 + count * 35,
              dir		: -1
            }),				
            opacity: '1'
         },speed);
					
     }








function loadCirclesItem(wg,username,tag){
   selClass='.ui-state-highlight';
   var cloneItem=$($("[wg='"+wg+"'][username='"+username+"']" )[0]).removeClass('left-drop-card ui-draggable-dragging draggable' + selClass).addClass('dingdon').css({
       position:'',
       top: 0,
       left: 0
   }).clone()
   var parent=$("[identifier='"+tag+"_"+wg+"']");
   tag=($(parent)[0].getAttribute('identifier')).split("_")[0];
   if(circlesList[wg][tag].indexOf(username) == -1) {
        circlesList[wg][tag].push(username);
   }
   else return false;
   deleteImage(cloneItem , parent , tag ,wg);
   var dropItmeList = $(parent).find('.circle-drop-item li').length;
   $(parent).find('.members').text(dropItmeList);
   if(cloneItem.hasClass(selectedClass)){
       $(parent).find(".dorp-action.add-new").text(cloneItem.length)
       $(parent).find(".dorp-action.add-new").animate({"margin-top": "-25px","opacity" : "1"}, 450, function(){	
            $(parent).animate({"margin-top": "0px","opacity" : "0" }, 450); 
		});
	}

}


	





 
