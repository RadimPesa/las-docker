hybrid_prot = {'instrument':'', 'protocol':'', 'loadQuantity': '', 'hybridTemp':'', 'hybTime':'', 'hybBuffer':'', 'totalVolume':'', 'denTemp':'', 'denTime':''};

chips_layout = {};
chipCounter = 0;

aliquotsHyb = {};


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
	

    jQuery('#Save_Cont').attr('disabled','disabled');
    jQuery('#Save_Stop').attr('disabled','disabled');

    // dropping of elements
	jQuery( "ul.droptrue" ).sortable({
			connectWith: "ul"
	});

	jQuery( "ul.dropfalse" ).sortable({
		connectWith: "ul",
		dropOnEmpty: true
	});

	jQuery( "#sortable1, #sortable2, #sortable3" ).disableSelection();
    jQuery(".sample_group_ul").selectable();

    checkNumSample();
    addAccordionLogic();
    // ADDING A SAMPLE TO A CHIP (BY CLICKING)
    addClickToChip();
    //OPEN ADD CHIP DIALOG- dialog box per la scelta del layout
	jQuery("#Add_chip").click(function(){
		insertChip();
	});
    // manage the protocol setting button
    protocol_setting();
    clearButton ();
    proceed();
    save_stop();

	var order = define_order( '#sort_date' );
	sort_requestsDate('date', order);

    order_requests();



    jQuery(document).on("click", ".sample_added span.ui-icon-info", function(){
		var aliquot_id = jQuery(this).attr("id");
        console.log(aliquot_id);
        infoDialog(aliquot_id);
    });


    jQuery(document).on("click",  ".sample_added span.ui-icon-closethick", function(){
		var aliquot_id = jQuery(this).attr("id");
        var chip_id = jQuery(this).attr("chip_id");
        var request = jQuery(this).parent().attr('id_group');
        console.log(aliquot_id);
        remove(aliquot_id, chip_id, request);
        jQuery(this).parent().remove();
    });




});	


function checkNumSample(){
    jQuery('.catalog_header').each(function(){
        var nSample = jQuery(this).find('li');
        jQuery(this).attr('nos', nSample.length);
        jQuery(this).attr('cnos', nSample.length);
        jQuery(this).find("span[id=number_of_samples]").text(nSample.length);
        jQuery(this).find("span[id=tot_samples]").text(nSample.length);
    });

}


function remove(aliquot_id, chip_id, request){
    //console.log(chip_id);
    chips_layout[chip_id]['pos'].splice( jQuery.inArray(aliquot_id, chips_layout[chip_id]['pos']), 1 );
    jQuery('.catalog .catalog_header').find('[id_group=' + request+ ']').find('[id=' + aliquot_id +']').show();
    //console.log(jQuery.find('.catalog_header[id_group=' + request + ']')[0]);
    updateTab(jQuery.find('.catalog_header[id_group=' + request + ']'),false);
    delete aliquotsHyb[aliquot_id];
    //console.log(Object.keys(aliquotsHyb).length);
    if (Object.keys(aliquotsHyb).length == 0){
	   	jQuery('#Save_Cont').attr('disabled','disabled');
	    jQuery('#Save_Stop').attr('disabled','disabled');
    }
}


function clearButton (){
	jQuery("#Clear").click(function(){
		jQuery(".chip_item").remove();
		jQuery("li.ui-selectee").show();
        jQuery(".catalog .catalog_header").each(function(){
            var nsamples = jQuery(this).attr('nos');
            jQuery(this).attr('cnos', nsamples)
            jQuery(this).find("span[id=number_of_samples]").text(nsamples);
            chips_layout = {};
            chipCounter = 0;
            aliquotsHyb = {};
		});
	});
}
	


// dialog to insert new chip
function insertChip (){
	jQuery( "#dialog-form" ).dialog({
		autoOpen: false,
		height: 200,
		width: 250,
		modal: true,
		buttons: {
				"Ok": function(){
						var n_pos = jQuery("#id_new_chip_positions").val();
						var item_height = jQuery("#list_num li").height();

						// calculate height depending on number of positions - keeping 5px margin
						item_height = ((item_height+1)*n_pos);

                        if (chips_layout.hasOwnProperty(chipCounter+1) == false){
                            chipCounter++;
                            chips_layout[chipCounter] = {'npos':  parseInt(n_pos), 'pos':[]};						
                        }

						// creo la struttura html per avere la giusta dimensione del chip
						var structure = [
						                 '<div class="chip_item">',
						                 	'<div class="chip_list" id_chip="' + chipCounter + '">',
						                 		'<h3 class="chip_title" style="padding: 0.2em 1em; text-align: left;">Chip ('+n_pos+') </h3>',
						                 		'<ul n_pos="'+n_pos+'" id="sortable1" class="droptrue" style="height: '+item_height+'px;"></ul>',
						                 	'</div>',
						                 '</div>'
						                ];
						var structure = structure.join('');			
						// appendo la struttura al chip layout
						jQuery("#chip_layout").append(structure);
						jQuery("ul.droptrue").sortable({
							connectWith: "ul"
						});
						addClickToChip();

					},
				"Cancel": function(){jQuery(this).dialog("close");}
		    }
	});
    jQuery("#dialog-form").dialog("open");
}


// gestione dell'accordion tramite una funzione
function addAccordionLogic(){
	// rendo il catalogo accordion
	jQuery( ".catalog" ).accordion({
			header: "> div > h3",
            active: false,
            autoHeight: false,
            collapsible: true,
			change: function(event, ui) { 
				//rimuovi la classe ui-selected al cambio del tab
				jQuery(".sample").removeClass("ui-selected")
				 }
		});
}

	


// Proceed button
function proceed() {
	jQuery("#Save_Cont").click(function() {
	
		
		var smpl_sel_list = new Array();
		// ciclo su ogni elemento dei chip
        jQuery(".chip_list").each(function(i, chip){
            chip_id = jQuery(chip).attr('id_chip');
            chips_layout[chip_id]['pos'] = new Array();
            jQuery(chip).find(".sample_added").each(function(j, sample){
                aliquot_id = (jQuery(this).attr("id"));
                chips_layout[chip_id]['pos'].push(aliquot_id);
                if (jQuery.inArray(aliquot_id, smpl_sel_list) == -1)
        			smpl_sel_list.push(aliquot_id);

            });

        });
		
        console.log(smpl_sel_list);       
      	submitData('continue');
    });
}


// Proceed button
function save_stop() {
	jQuery("#Save_Stop").click(function() {
	
		
		var smpl_sel_list = new Array();
		// ciclo su ogni elemento dei chip
        jQuery(".chip_list").each(function(i, chip){
            chip_id = jQuery(chip).attr('id_chip');
            chips_layout[chip_id]['pos'] = new Array();
            jQuery(chip).find(".sample_added").each(function(j, sample){
                aliquot_id = (jQuery(this).attr("id"));
                chips_layout[chip_id]['pos'].push(aliquot_id);
                if (jQuery.inArray(aliquot_id, smpl_sel_list) == -1)
        			smpl_sel_list.push(aliquot_id);

            });

        });
		
        console.log(smpl_sel_list);
        submitData('stop');    
    });  
}


function submitData (status){
	var response = {'sel_aliquots':  aliquotsHyb, 'chips':chips_layout, 'hybrid_prot': hybrid_prot, 'status':status};
	var json_response = JSON.stringify(response);
    var url = base_url + '/plan_hybrid/';
	jQuery.ajax({
        type:'POST',    
        url:url,
        data: json_response, 
        dataType: "json",                  
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


// manage the click event for chip
function addClickToChip(){
	
	jQuery("div.chip_list").click(function() {
        var id_chip = jQuery(this).attr("id_chip");
		
		var chip_item = jQuery(this);
		var selected = jQuery(".ui-selected.sample", ".catalog");
		if (selected.length==0){
            return;
        }

		if((jQuery(this).children("ul").children("li")).length + selected.length - 1 < chips_layout[id_chip].npos){
		// per ogni elemento selezionato lo nascondo e lo appendo nel chip dove e' avvenuto il click
		selected.children().removeClass('ui-selected');
		selected.each(function(){
			text = jQuery(this).html();

			var aliqvarid;
			var alertI = false;
			
			// GRUPPO E CAMPIONE SERVONO PER L'ELIMINAZIONE e per la show
			var group_id = jQuery(this).parents(".ui-accordion-content").attr("id_group");
			var sample_id = jQuery(this).attr("id_sample");
            // retrieve the aliquot info for the list of aliquots to hybridize
			var aliquot_id = jQuery(this).attr("id");
            var aliquot_concentration = parseFloat(jQuery(this).attr("concentration"));
			var aliquot_volume = parseFloat(jQuery(this).attr("volume"));
            var aliquot_tech_replicates = parseInt(jQuery(this).attr("tech_replicates"));
            var aliquot_exp_group = jQuery(this).attr("exp_group");
            var aliquot_date = jQuery(this).attr("date");
            var aliquot_owner = jQuery(this).attr("owner");
            var aliquot_exhausted = jQuery(this).attr("exhausted");
            var aliquot_sample_features = jQuery(this).attr("sample_features");

		    // compute cRNA volume according to the protocol info
            var cRNAVolume = (hybrid_prot['loadQuantity']/aliquot_concentration);
            console.log(cRNAVolume,aliquot_volume);
            // check if the volume is sufficient for the hybridization
            if (cRNAVolume > aliquot_volume){
                alert("Insufficient Volume!","Warning");
				alertI = true;
            }
            var temp = cRNAVolume + hybrid_prot['hybBuffer'];
			var waterVolume = (hybrid_prot['totalVolume'] - temp);
			var color = ""
			if(jQuery(this).attr("style"))
				color = jQuery(this).attr("style");
			console.log(color);
			if (text != ""){
				(chip_item.find(".droptrue")).append("<li style='position:relative;overflow:hidden;"+color+"' id='"+aliquot_id+"' id_sample='"+sample_id+"' id_group='"+group_id+"' volume='" + aliquot_volume +"' concentration='" + aliquot_concentration + "'  tech_replicates='" + aliquot_tech_replicates + "' exp_group='"+ aliquot_exp_group + "' date='" + aliquot_date + "' owner='"+ aliquot_owner + "' exhausted='" + aliquot_exhausted + "' sample_features='" + aliquot_sample_features + "' class='sample_added sample_selected'><span id='"+aliquot_id+"' class='ui-icon ui-icon-info' style='position:absolute;right:2px;bottom:2px;cursor:pointer'></span><b>"+sample_id+"</b><br><b>cRNA Volume (ul): </b>"+cRNAVolume.toFixed(2)+" ul<br><b>Water Volume (ul): </b>"+waterVolume.toFixed(2)+" ul<br><b>Hybridization Buffer (ul): </b>"+ hybrid_prot['hybBuffer'].toFixed(2) +" ul <span id='"+aliquot_id+"' chip_id='" + id_chip + "' class='ui-icon ui-icon-closethick' style='position:absolute;right:2px;top:2px;cursor:pointer'> </li>");
				catalog_item = jQuery(this).parents(".catalog_header");
				updateTab(catalog_item, true);

                // update global variable
                chips_layout[id_chip]['pos'].push(sample_id);
                aliquotsHyb[aliquot_id] = {'owner':aliquot_owner, 'sample_identifier': sample_id, 'sample_features': aliquot_sample_features, 'exp_group': aliquot_exp_group, 'volume': aliquot_volume, 'concentration': aliquot_concentration, 'tech_replicates': aliquot_tech_replicates, 'date': aliquot_date, 'group_id': group_id, 'exhausted': 'False'};
                jQuery('#Save_Cont').removeAttr('disabled');
                jQuery('#Save_Stop').removeAttr('disabled');



				if(alertI==true)
					jQuery("li:last").append('<span style="position:absolute;right:2px;top:2px" title="Insufficient Volume!" class="ui-icon ui-icon-alert"></span>');
			}
		});
		jQuery(".catalog li.ui-selected").hide(100);
		jQuery(".catalog li").removeClass("ui-selected");
		
		

	}
	else{
		alert("Chip full or trying to add too much aliquots", "Warning");
		jQuery("div.ui-dialog").children(".ui-dialog-titlebar:contains(Warning)").parent().children(".ui-dialog-content").css("font-size","1.6em");
		exit();
	}
	
	});
	
}


// update of sample list
function updateTab(j,remove){
	var span = jQuery("#number_of_samples", j);
	
	if(remove == true){
		//updating current num of samples
        var num = (parseInt)(j.attr("cnos"));
		num--;
		j.attr("cnos", num);
		span.text(num);
		
	}
	else{
		//updating current num of samples
        var num = (parseInt)(jQuery(j).attr("cnos"));
		num++;
		jQuery(j).attr("cnos", num);
		span.text(num);

	}
}

function toTimestamp(dateString){
	 var datum = new Date(dateString);
	 return datum.getTime()/1000;
}

function sort_requestsDate(attribute, order){
	var list = jQuery('div.catalog_header');
	list.sortElements(function(a, b){
		if (order == "asc"){
	    	return toTimestamp(jQuery(a).attr(attribute)) > toTimestamp(jQuery(b).attr(attribute)) ? 1 : -1;
	    }
	    else{
	    	if (order == "desc"){
				return toTimestamp(jQuery(a).attr(attribute)) < toTimestamp(jQuery(b).attr(attribute)) ? 1 : -1;
			}
	    }
	});
}

function sort_requestsString(attribute, order){
	var list = jQuery('div.catalog_header');
	list.sortElements(function(a, b){
		if (order == "asc"){
	    	return jQuery(a).attr(attribute) > jQuery(b).attr(attribute) ? 1 : -1;
	    }
	    else{
	    	if (order == "desc"){
				return jQuery(a).attr(attribute) < jQuery(b).attr(attribute) ? 1 : -1;
			}
	    }
	});
}

function sort_requestsInt(attribute, order){
	var list = jQuery('div.catalog_header');
	list.sortElements(function(a, b){
		if (order == "asc"){
	    	return parseInt(jQuery(a).attr(attribute)) > parseInt(jQuery(b).attr(attribute)) ? 1 : -1;
	    }
	    else{
	    	if (order == "desc"){
				return parseInt(jQuery(a).attr(attribute)) < parseInt(jQuery(b).attr(attribute)) ? 1 : -1;
			}
	    }
	});
}




function define_order(idObj){
	var order = jQuery(idObj).attr('order')
	if (order == "None"){
		order = "asc";
		jQuery(idObj).attr('src', '/uarray_media/images/sort_asc.png');
	}
	else{
		if (order == "asc"){
			order = "desc";
			jQuery(idObj).attr('src', '/uarray_media/images/sort_desc.png');
		}
		else{
			order = "asc";
			jQuery(idObj).attr('src', '/uarray_media/images/sort_asc.png');
		}
	}
	jQuery(idObj).attr('order', order);
	return order;
}


function reset_imgs(){
	jQuery('#sort_id').attr('src', '/uarray_media/images/sort_both.png');
	jQuery('#sort_date').attr('src', '/uarray_media/images/sort_both.png');
	jQuery('#sort_owner').attr('src', '/uarray_media/images/sort_both.png');
	jQuery('#sort_nsamples').attr('src', '/uarray_media/images/sort_both.png');
}

	
// funzione per l'ordinamento in base agli attributi "date" "user" e "quantity"
function order_requests() {
	// put all your jQuery goodness in here.

	jQuery('#sort_id').click(function(event){
		reset_imgs();
		var order = define_order('#sort_id');
		sort_requestsInt('id_group', order);
	});


	jQuery('#sort_date').click(function(event){
		reset_imgs();
		var order = define_order( '#sort_date' );
		sort_requestsDate('date', order);
	});


	jQuery('#sort_owner').click(function(event){
		reset_imgs();
		var order = define_order( '#sort_owner' );
		sort_requestsString('id_user', order);
	});

	jQuery('#sort_nsamples').click(function(event){
		reset_imgs();
		var order = define_order( '#sort_nsamples');
		sort_requestsInt('cnos', order);
	});
}
	
	

// set the protocol and instrument values
function protocol_setting (){
	
	jQuery("#protocol_button").click(function(){
		var protocol_is_set = false;
		//PRENDO I VALORI PER METTERLI IN SESSIONE TRAMITE UNA POST
		var prot = jQuery("#id_Hyb_protocol option:selected").text();
		var instrument = jQuery("#id_Hyb_instrument option:selected").text();
        jQuery("#messagediv").append('<table style:"text-align:leftpadding:1px"><tr><th>Hybridization protocol:</th><td>' +prot  + '</td></tr><th>Instrument:</th><td>' + instrument +'</td></tr></table>');
        jQuery("#messagediv").show();
        var url =  base_url + '/api.hybprotocolinfo/' + prot + '/' + instrument;
                  
        jQuery.ajax({
            type: 'get',
            url: url,
            async: false,
            success: function(transport) {
                hybrid_prot = transport;
            }
        });
        // show the rest of the page
        jQuery("#prehybrid").show();
        jQuery("#chip_planning").show();
        jQuery(this).attr('disabled', 'disabled');
        jQuery("#id_Hyb_protocol").attr('disabled', 'disabled');
        jQuery("#id_Hyb_instrument").attr('disabled', 'disabled');
    }); 
}



// set the info of aliquot
function infoDialog(aliquot_id){

    jQuery(jQuery("#aliqinfo").find('td[name=owner]')[0]).text(aliquotsHyb[aliquot_id]['owner']);
    jQuery(jQuery("#aliqinfo").find('td[name=sample_identifier]')[0]).text(aliquotsHyb[aliquot_id]['sample_identifier']);
    jQuery(jQuery("#aliqinfo").find('td[name=sample_features]')[0]).text(aliquotsHyb[aliquot_id]['sample_features']);
    jQuery(jQuery("#aliqinfo").find('td[name=exp_group]')[0]).text(aliquotsHyb[aliquot_id]['exp_group']);
    jQuery(jQuery("#aliqinfo").find('td[name=volume]')[0]).text(aliquotsHyb[aliquot_id]['volume']);
    jQuery(jQuery("#aliqinfo").find('td[name=concentration]')[0]).text(aliquotsHyb[aliquot_id]['concentration']);
	if (aliquotsHyb[aliquot_id]['tech_replicates'] > 1){
    	jQuery(jQuery("#aliqinfo").find('td[name=tech_replicates]')[0]).text(aliquotsHyb[aliquot_id]['tech_replicates']);
	}
	else{
		jQuery(jQuery("#aliqinfo").find('td[name=tech_replicates]')[0]).text('---');
	}
    jQuery(jQuery("#aliqinfo").find('td[name=date]')[0]).text(aliquotsHyb[aliquot_id]['date']);

    jQuery( "#aliqinfo" ).dialog({
            resizable: false,			
			width: 400,
			modal: false,
            draggable: false,
			buttons: {
					"Ok": function(){
						    jQuery('#aliqinfo').dialog("close");			    
						}					
			}
		});
}
	


