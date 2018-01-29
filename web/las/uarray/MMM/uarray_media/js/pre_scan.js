scan_prot = {'protocol': '', 'software':''};
var chips_requested = {};
var chips_toscan = {};
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

    setProtocol();
    jQuery("#load_chip").click(function(){
        barcodeSubmit();
    });

    procede();
    jQuery('#id_barcode').attr('disabled', 'disabled');
    jQuery('#id_notes').attr('disabled', 'disabled');

});


function setProtocol(){
	jQuery("#protocol_button").click(function(){
		console.log('protocol setting');
        var prot = jQuery("#id_Protocol option:selected").val();

        var url =  base_url + '/api.getscanprotocol/' + prot;

        jQuery.ajax({
            type: 'get',
            url: url,
            async: false,
            success: function(transport) {
                scan_prot = transport;
            }
        });
        var table_message = '<table style="text-align:left"><tr><th>Scan protocol:</th><td>' + scan_prot['protocol'] + '</td></tr> <tr><th>Instrument:</th><td>' + scan_prot['instrument'] + '</td></tr> <tr><th>Software:</th><td>' + scan_prot['software'] + '</td></tr> <tr><th>Parameters: </th><td></td>';
        jQuery.each(scan_prot['params'], function (index, value){
            table_message += '<tr><td><i>' + value['name'] + ':</i></td><td>' + value['value'] + ' (' + value['unity'] + ')</td></tr>';
        });

        table_message += '</table>';
        jQuery("#message").append(table_message);
        for (var i=0; i< scan_prot['instrument_pos']; i++){
            jQuery('.positions').append('<li class="position" style="position: relative;"> <span class="chip_on_scan"></span> <span class="chip_added ui-icon ui-icon-closethick" style="float:right"></span> </li>');
        }

        jQuery("#id_barcode").removeAttr('disabled');
        jQuery("#load_chip").removeAttr('disabled');
        jQuery("#id_notes").removeAttr('disabled');
        // show the rest of the page
        jQuery("#scan").show();
        jQuery(this).attr('disabled', 'disabled');
        jQuery('#id_Protocol').attr('disabled', 'disabled');
        removeChip();

    });
}

function checkKeyP(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        barcodeSubmit();
}

function barcodeSubmit(){
    // get values from the page
    var barcode = jQuery('#barcode_scan_form').find( 'input[name="barcode"]' ).val();
    if (chips_toscan.hasOwnProperty(barcode)){
        alert('Chips already in the scan list');
        return;
    }
    if (barcode == current_chip || barcode == ''){
        return;
    }
    if (chips_requested.hasOwnProperty(barcode) ){
        removeChipLayout();
        updateChipLayout(barcode);
        current_chip = barcode;
        jQuery('#chip_info').text(barcode);
        jQuery('#add_chip').removeAttr("disabled");
        return;
    }
    
    var url = base_url + '/api.getchip/' + barcode + '/toscan';    
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
                    removeChipLayout();
                    // update layout chip
                    updateChipLayout (barcode);
                    
                    // set current chip
                    current_chip = barcode;
                    jQuery('#chip_info').text(barcode);
                    jQuery('#add_chip').removeAttr("disabled");
                    jQuery('#id_barcode:text').val('');

                    addChip();
                }                        
    		
    	    },
        error: function(data) {
    			 alert(data.responseText, "Error");
    	    }
    });
}


function updateChipLayout (barcode){
    jQuery('#chip_positions').show();
    jQuery.each(chips_requested[barcode]['pos'], function(index, value){
        jQuery('#chip_layout tbody').append('<tr style="height:30px"><td class="ui-widget-content" style="width:10%;background:#eee;text-align:center">'+ value['idPos'] +'</td><td class="ui-widget-content" style="width:300px"><span style="float:center">' + value['sample_identifier'] + '</span></td></tr>');
    });
       
}


function addChip(){
    console.log(current_chip);
    if (current_chip != ''){
        jQuery('.position').each(function(){
            var chip_on_scan = jQuery(this).find('.chip_on_scan');
            console.log(chip_on_scan);
            if (!jQuery(chip_on_scan).attr('barcode')){
                jQuery(chip_on_scan).attr('barcode', current_chip);
                jQuery(chip_on_scan).text('Chip barcode:' + current_chip);
                return false;
            }
        });
        jQuery('ol.positions').sortable({});
        jQuery('#terminate').removeAttr('disabled');
        chips_toscan[current_chip] = '';
        current_chip = '';
    }
}


function removeChipLayout(){
    jQuery('#chip_layout tbody').empty();

}


function removeChip(){
    jQuery('.chip_added.ui-icon-closethick').click(function(){
        if( jQuery(this).parent().find('[barcode]').length != 0){
            console.log(this);
            var barcode = jQuery(this).parent().find('[barcode]').attr('barcode');
            console.log(barcode);
            delete chips_toscan[barcode];
            jQuery(this).parent().find('[barcode]').text('');
            jQuery(this).parent().find('[barcode]').removeAttr('barcode');
            if (jQuery('.chip_on_scan').filter('[barcode]').length == 0){
                jQuery('#terminate').attr('disabled','disabled');
            }
        }

    });
}


function procede(){
    jQuery('#terminate').click(function(){
        var notes = jQuery('#id_notes').val();

        jQuery('.chip_on_scan').each(function (index, value){
            if (jQuery(this).attr('barcode')){
                chips_toscan[jQuery(this).attr('barcode')] = index+1;
            }

        });
        var response = {'protocol':  scan_prot['protocolid'], 'notes': notes, 'chips_to_scan': chips_toscan};
        var json_response = JSON.stringify(response);
        console.log(json_response);    
        var url = base_url + '/pre_scan/';
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

