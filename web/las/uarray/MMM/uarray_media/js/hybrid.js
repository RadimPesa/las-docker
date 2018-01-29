var chips_requested = {};
var chips_tohyb = {};
var current_chip;
var planid;

jQuery(document).ready(function(){
    jQuery("input#id_barcode").focus();

	// CRFS TOKEN
	jQuery('html').ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
	});

    planid = jQuery('#message').attr('planid');
    var start_event = false;

    jQuery("#bar_search_button").click(function(){
        barcodeSubmit();
    });
    autoAdding();
    saveChip();
    hybTermination();

	jQuery('#term_event').attr("disabled", "disabled");
    jQuery('#save_chip').attr("disabled", "disabled");
    jQuery('#auto_adding').attr("disabled", "disabled");

    // PRE-SELECTED SAMPLE LIST SORTABLE AND SELECTABLE (personalized)
	jQuery(".sel_sample_list").sortable();
	jQuery(".sel_sample_list li").click(function() {
		if (jQuery(this).hasClass("selected")){
			jQuery(this).removeClass("selected");
		}
  		else
  			jQuery(this).addClass("selected").siblings().removeClass("selected");
  	});


});
	

function updateChipLayout (barcode){
    // reset chip info e layout
    jQuery("#message2").empty();
    jQuery('#chip_layout tbody').children().remove();
    jQuery("#message2").append('<table><tr><th>Chip Barcode:</th><td>' + chips_requested[barcode]['barcode'] + '</td> </tr> <tr> <th>Chip type:</th><td> ' + chips_requested[barcode]['chip_type'] + '</td> </tr> <tr> <th>Number of positions:</th><td> ' + chips_requested[barcode]['npos'] + '</td> </tr> <tr> <th>Owner:</th><td> ' + chips_requested[barcode]['owner'] + ' </td> </tr> <tr> <th>Expiration date:</th><td>' + chips_requested[barcode]['expdate'] +'</td></tr></table>');
    for (var i=1; i<= chips_requested[barcode]['npos']; i++){
        jQuery('#chip_layout tbody').append('<tr style="height:30px"><td style="width:10%">'+ chips_requested[barcode]['geometry'][i] +'</td><td class="sample_chip ui-widget-content" style"width:500px"><span class="sample_added ui-icon ui-icon-closethick" style="float:right"></span></td></tr>');
    }
}


function checkKeyP(evt){
        var charCode = (evt.which) ? evt.which : event.keyCode
        if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
            barcodeSubmit();
}


function barcodeSubmit(){
    // get values from the page
    var barcode = jQuery('#barcode_hyb_form').find( 'input[name="barcode"]' ).val();
    if (chips_tohyb.hasOwnProperty(barcode)){
        alert('Chips already in the hybridization list');
        return;
    }
    if (barcode == current_chip || barcode == ''){
        return;
    }
    if (chips_requested.hasOwnProperty(barcode) ){
        updateChipLayout(barcode);
        clickOnChip();
        removeSample();
        current_chip = barcode;
        jQuery('#id_barcode:text').val('');
        jQuery('#auto_adding').removeAttr("disabled");
        return;
    }
    
    var url = base_url + '/api.getchip/' + barcode + '/tohybrid';    
    jQuery.ajax({
        type: 'get',
        url: url,
        success: function(transport) {
                if (transport.hasOwnProperty('response') ){
                    alert(transport['response'], "Error");
                } 
                else{
                    // save the chip info
                    chips_requested[transport['barcode']] = transport;
                    // uodate layotu chip
                    updateChipLayout (barcode);
                    clickOnChip();
                    removeSample();
                    // set current chip
                    current_chip = barcode;
                    jQuery('#id_barcode:text').val('');
                    jQuery('#auto_adding').removeAttr("disabled");
                }                        
    		
    	    },
        error: function(data) {
    			 alert(data.responseText, "Error");
    	    }
    });
   
}



function clickOnChip(){
    jQuery('.sample_chip').click(function(){
        var sample = jQuery('.sample_todo.selected');
        if (sample.length!=0 && jQuery(this).attr('sample_id') == undefined){
            var sample_id = jQuery(sample[0]).attr('sample_id');
            var sample_identifier = jQuery(sample[0]).attr('sample_identifier');
            jQuery(this).append('<span class="info">' + sample_identifier + '</span>');
            jQuery(this).attr('sample_id', sample_id);
            jQuery(sample[0]).removeClass('selected');
            jQuery(sample[0]).hide();
            jQuery('#save_chip').removeAttr("disabled");
            
        }
    
    });
}


function removeSample(){
    jQuery('.sample_added.ui-icon-closethick').click(function(){
        jQuery(this).parent().children().remove('.info');
        var sample_id = jQuery(this).parent().attr('sample_id');
        if (sample_id){
            jQuery(this).parent().removeAttr('sample_id');
            jQuery('.sample_todo[sample_id=' + sample_id + ']').show();
            if (jQuery('.sample_chip').filter('[sample_id]').length == 0)
                jQuery('#save_chip').attr("disabled", "disabled");
        }        

    });
}



function removeChip(){
    jQuery('.chip_added.ui-icon-closethick').click(function(){
        var chip_barcode = jQuery(this).parent().attr('chip');
        jQuery(this).parents('tr').remove();
        jQuery.each(chips_tohyb[chip_barcode], function(key, value){
            jQuery('.sample_todo[sample_id=' + value['sample_id'] + ']').show();
        });
        delete chips_tohyb[chip_barcode];
        if (jQuery('.hyb_chip').length == 0)
            jQuery('#term_event').attr("disabled", "disabled");

    });
}

function autoAdding (){
//AUTO-ADDING BUTTON

    jQuery("#auto_adding").click( function(){
        jQuery(".sample_todo").not(':hidden').each(function(){
            var positions_on_chip = jQuery('.sample_chip').not('[sample_id]')
            if (positions_on_chip.length > 0){
                var sample_id = jQuery(this).attr('sample_id');
                var sample_identifier = jQuery(this).attr('sample_identifier');
                jQuery(positions_on_chip[0]).append('<span class="info">' + sample_identifier + '</span>');
                jQuery(positions_on_chip[0]).attr('sample_id', sample_id);
                jQuery(this).removeClass('selected');
                jQuery(this).hide();
            }
            else{
                
                return;
            }            
        });
    jQuery('#save_chip').removeAttr("disabled");
    });
}


// SAVE CHIP BUTTON
function saveChip (){
    jQuery("#save_chip").click(function(){
	    jQuery("#save_chip").attr('disabled', "disabled");
        jQuery("span#message2").empty();
        jQuery('#chip_hybrid tbody').append('<tr style="height:30px"><td class="hyb_chip ui-widget-content" style="width:100px" chip="' + current_chip + '">' + current_chip + '<span class="chip_added ui-icon ui-icon-closethick" style="float:right"></span></td></tr>');
        // TODO aggiungere il chip con relativi sample alla variabile globale
        chips_tohyb[current_chip] = {};
        var i = 1;
        jQuery('.sample_chip').each(function(){
            if (jQuery(this).attr('sample_id')){
                chips_tohyb[current_chip][i]  = {'sample_id':jQuery(this).attr('sample_id')};
            }
            i++;
        });

        jQuery('#chip_layout tbody').children().remove();
        removeChip();
        if (jQuery('.sample_todo:visible').length == 0){
            jQuery('#term_event').removeAttr("disabled");    
        }
        jQuery('#auto_adding').attr("disabled", "disabled");
        current_chip = '';
        
    });
}


function hybTermination (){
    jQuery("#term_event").click(function(){
        console.log('terminate hybridization');
		var response = {'chips_tohyb':  chips_tohyb, 'planid': planid};
        var json_response = JSON.stringify(response);
        var url = base_url + '/hybrid/';
        console.log(json_response);
        jQuery.ajax({
            type:'POST',    
            url:url,
            data: json_response, 
            dataType: "json",                  
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status + ' ' +data.responseText.slice(0,500), "Error");
            }

        });
    });
}



