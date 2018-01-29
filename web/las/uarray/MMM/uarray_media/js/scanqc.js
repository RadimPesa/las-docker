var chips_qc = {};
var current_chip;

// init document
jQuery(document).ready(function(){
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

    selectChip();
    saveChip();
    saveQC();


});


function selectChip(){
    jQuery('.chip').click(function(){
        var barcode = jQuery(this).attr('barcode');
        if ( barcode != ""){
            var url = base_url + '/api.getchip/' + barcode + '/scanqc';    
            jQuery.ajax({
                type: 'get',
                url: url,
                success: function(transport) {
                        if (transport.hasOwnProperty('response') ){
                            alert(transport['response'], "Error");
                        } 
                        else{
                            // save the chip info
                            chips_qc[transport['barcode']] = transport;
                            removeChipLayout();
                            // update layout chip
                            updateChipLayout (barcode);
                            // set current chip
                            current_chip = barcode;
                            jQuery('#chip_info').text('Chip Info: ' + barcode);
                            jQuery('#save_chip').show();
                            //jQuery('#id_barcode:text').val('');
                            changeQC();
                        }                             
                    },
                error: function(data) {
                         alert(data.responseText, "Error");
                    }
            });
        }
    else{
        resetChip();
        jQuery('#chip_info').text('No chip available at this position.');
        }
    });
}


function updateChipLayout (barcode){
    jQuery('#chip_positions').show();
    jQuery.each(chips_qc[barcode]['pos'], function(index, value){
        jQuery('#chip_layout tbody').append('<tr style="height:30px"><td class="ui-widget-content" style="width:10%;background:#eee">'+ value['idPos'] +'</td><td class="ui-widget-content sample" style="width:300px;background:#5DB95D" idpos="' + value['idPos'] + '" qc="true"><span style="float:center">' + value['sample_identifier'] + '</span></td></tr>');
    });       
}

function removeChipLayout(){
    jQuery('#chip_layout tbody').empty();
}


function changeQC(){
    jQuery('.sample').click(function(){
        console.log(jQuery(this).attr('qc'));
        var qc = jQuery(this).attr('qc');
        if (qc == "true"){
            jQuery(this).attr('qc', "false");
            jQuery(this).css("background-color", "#A11717");
        }
        else{
            jQuery(this).attr('qc', "true");   
            jQuery(this).css("background-color", "#5DB95D");
        }
    });
}


function saveChip(){
    jQuery('#save_chip').click(function(event){
        jQuery('.sample').each(function(index){
            var qc = jQuery(this).attr('qc');
            chips_qc[current_chip]['pos'][index]['qc'] = qc;
            jQuery(jQuery('.chip').filter('[barcode="' + current_chip + '"]')[0]).unbind('click');
            jQuery(jQuery('.chip').filter('[barcode="' + current_chip + '"]')[0]).css("background", "#CCCCDD");
        });
        insertQCChip(current_chip);
        resetChip();            
    });
}


function resetChip(){
    jQuery('#save_chip').hide();
    removeChipLayout();
    current_chip = '';
    jQuery('#chip_info').text('');
}


function insertQCChip(barcode){
    jQuery('#chip_qc tbody').append('<tr style="height:30px"><td class="ui-widget-content" style="width:10%;background:#eee" barcode="'+ barcode + '">'+ barcode +'<span class="chip_added ui-icon ui-icon-closethick" style="float:right"></span></td></tr>');
    removeQCChip();
}


function removeQCChip(){
    jQuery('.chip_added.ui-icon-closethick').click(function(){
        var chip_barcode = jQuery(this).parent().attr('barcode');
        jQuery(this).parents('tr').remove();
        jQuery(jQuery('.chip').filter('[barcode="' + chip_barcode + '"]')[0]).bind('click', selectChip());
        jQuery(jQuery('.chip').filter('[barcode="' + chip_barcode + '"]')[0]).css("background", "");
    });
}

function saveQC(){
    jQuery('#save_qc').click(function(event){
        var json_response = JSON.stringify(chips_qc);
        var url = base_url + '/scanqc/';
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