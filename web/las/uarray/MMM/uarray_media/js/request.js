
// data structure for the request
aliquotsRequested = {'title':'', 'description':'', 'operator':'', 'owner': '', 'aliquots':{}}
// counter of requested aliquots
aliquotsCounter = 0;


// initialization function of the page
jQuery(document).ready(function(){

    //calendario
   
    jQuery(function() {
        jQuery('#id_date').datepicker({ dateFormat: "yy-mm-dd", maxDate: "D" });
    });
    
    // data table initialization
    generate_table();    
    readTable();
    initRequest();


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
	
});




// init the data table
function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    //var oTable = jQuery("table#aliquot_table").dataTable();
    //oTable.fnDestroy();
    jQuery("table#aliquot_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "#" },
            { "sTitle": "Barcode/Label" },
            { "sTitle": "Sample Feature" },
            { "sTitle": "Experimental Group" },
            { "sTitle": "Aliquot Generation Date" },
            { "sTitle": "Volume (ul)" },
            { "sTitle": "Concetration (ul/ng)" },
            { "sTitle": "Owner" },
            { "sTitle": "Technical Replicates" },
            { "sTitle": "Present"},
            { "sTitle": null, 
              "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-closethick"></span><span class ="ui-icon ui-icon-pencil"></span>'
            },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    "aoColumnDefs": [
        { "bSortable": false, "aTargets": [ 10 ] },
        { "bVisible": false, "aTargets": [ 9 ] },
    ],
   'fnRowCallback': function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        //console.log(aData);

        if (aData[9] == "Warning") {
              $('td:eq(0)', nRow).addClass('conditionalRowColor');
              $('td:eq(1)', nRow).addClass('conditionalRowColor');
              $('td:eq(2)', nRow).addClass('conditionalRowColor');
              $('td:eq(3)', nRow).addClass('conditionalRowColor');
              $('td:eq(4)', nRow).addClass('conditionalRowColor');
              $('td:eq(5)', nRow).addClass('conditionalRowColor');
              $('td:eq(6)', nRow).addClass('conditionalRowColor');
              $('td:eq(7)', nRow).addClass('conditionalRowColor');
              $('td:eq(8)', nRow).addClass('conditionalRowColor');
              $('td:eq(9)', nRow).addClass('conditionalRowColor');
              $('td:eq(10)', nRow).addClass('conditionalRowColor');
            }
        else{

            if (aData[9] == "True") {
                  $('td:eq(0)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(1)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(2)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(3)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(4)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(5)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(6)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(7)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(8)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(9)', nRow).addClass('conditionalRowColor2');
                  $('td:eq(10)', nRow).addClass('conditionalRowColor2');
                }
            else{
                  $('td:eq(0)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(1)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(2)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(3)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(4)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(5)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(6)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(7)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(8)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(9)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(10)', nRow).removeClass('conditionalRowColor');
                  $('td:eq(0)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(1)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(2)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(3)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(4)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(5)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(6)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(7)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(8)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(9)', nRow).removeClass('conditionalRowColor2');
                  $('td:eq(10)', nRow).removeClass('conditionalRowColor2');
            }
        }
        return nRow;
        }
    });

    /* Add event listener for delete row  */
   jQuery(document).on('click','#aliquot_table tbody td span.ui-icon-closethick', function() {
        var nTr = jQuery(this).parents('tr')[0];
        console.log(nTr);
        var posAl = jQuery("#aliquot_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var idAl = jQuery("#aliquot_table").dataTable().fnGetData(posAl[0]);
        delete aliquotsRequested['aliquots'][idAl[1]];
        jQuery("table#aliquot_table").dataTable().fnDeleteRow( nTr );
    } );
    /* Add event listener for edit row  */
  jQuery(document).on('click','#aliquot_table tbody td span.ui-icon-pencil', function(){
        var posAl = jQuery("#aliquot_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var idAl = jQuery("#aliquot_table").dataTable().fnGetData(posAl[0]);
        console.log(idAl);
        editRow(idAl[1], posAl[0]);
    } );


}


function checkAliquotExists (barcode, date, owner){

    var url =  base_url +'/api.findaliquot/' + barcode + '/' + date + '/' + owner ;
    var checkFlag = 'False';
    jQuery.ajax({
        type: 'get',
        url: url,
        async: false,
        success: function(transport) {
            checkFlag = transport;
            console.log(checkFlag);
            return checkFlag;
        }
    });
    return checkFlag;
    
}


// insert a new row using the data of the form
function insertRow(){
    var table = jQuery("#aliquot_table");  
    // initialize variable depending on genealogy
    var genealogy = '';
    var sample_identifier = '';
    var volume = '';
    var concentration = '';
  
    var owner = jQuery("#owner").val();
    var sample_features = jQuery("#sample_features").val();
    var exp_group = jQuery("#exp_group").val();
    var tech_replicates = jQuery("#tech_replicates").val();
    var date = '';

    var existFlag = 'False';
    
    sample_identifier = jQuery("#aliquot_identifier").val();
    if (aliquotsRequested['aliquots'].hasOwnProperty(sample_identifier) || sample_identifier==""){
        //console.log('exit');
        return;
    }
    volume = jQuery("#volume").val();
    concentration = jQuery("#concentration").val();
    date = jQuery("#id_date").val();
    console.log(sample_identifier);
    if (date=="" || owner == "" || volume == "" || concentration == "") {
        alert("Date, owner, volume and concetration should be specified for external aliquots.");
        return;   

    }
    existFlag = checkAliquotExists (sample_identifier, date, owner)
  
    aliquotsCounter++;
    console.log([aliquotsCounter, sample_identifier, sample_features, exp_group, date, volume, concentration, owner, tech_replicates, existFlag, null]);
    updateDict(aliquotsCounter, sample_identifier, sample_features, exp_group, date, volume, concentration, owner, tech_replicates, existFlag)
    table.dataTable().fnAddData([aliquotsCounter, sample_identifier, sample_features, exp_group, date, volume, concentration, owner, tech_replicates, existFlag, null] );
    jQuery('#upload').attr("disabled","disabled");

}


// update dictionary. The key is the sample_identifier (genealogy or label). Manage the two cases
function updateDict(counter, sample_identifier, sample_features, exp_group, date, volume, concentration, owner, tech_replicates, present){
    aliquotsRequested['aliquots'][sample_identifier] = {'sample_identifier': sample_identifier, 'sample_features': sample_features, 'exp_group': exp_group, 'date': date, 'volume': volume, 'concentration':concentration, 'owner':owner, 'tech_replicates':tech_replicates, 'counter':counter, 'present':present}
    if (counter > aliquotsCounter)
        aliquotsCounter = counter;
    if (aliquotsCounter > 0)
        jQuery('#create_req_button').removeAttr("disabled");

}


// edit a row of the table
function editRow(idAl, posAl){
  console.log("editRow");
  console.log(idAl);
  console.log(aliquotsRequested['aliquots'][idAl]);
	jQuery("#dialog-form").find('input[name=sample_identifier]').attr('value',aliquotsRequested['aliquots'][idAl]['sample_identifier']);
	jQuery("#dialog-form").find('input[name=sample_features]').attr('value',aliquotsRequested['aliquots'][idAl]['sample_features']);
	jQuery("#dialog-form").find('input[name=date]').attr('value',aliquotsRequested['aliquots'][idAl]['date']);
	jQuery("#dialog-form").find('input[name=exp_group]').attr('value',aliquotsRequested['aliquots'][idAl]['exp_group']);
	jQuery("#dialog-form").find('input[name=volume]').attr('value',aliquotsRequested['aliquots'][idAl]['volume']);
	jQuery("#dialog-form").find('input[name=concentration]').attr('value',aliquotsRequested['aliquots'][idAl]['concentration']);
	jQuery("#dialog-form").find('input[name=owner]').attr('value',aliquotsRequested['aliquots'][idAl]['owner']);
	jQuery("#dialog-form").find('input[name=tech_replicates]').attr('value',aliquotsRequested['aliquots'][idAl]['tech_replicates']);
  jQuery("#dialog-form").find('input[name=date]').datepicker({ dateFormat: "yy-mm-dd", maxDate: "D" });


    
    if (aliquotsRequested['aliquots'][idAl]['present'] == "False"){
        jQuery("#dialog-form").find('input[name=sample_identifier]').attr("disabled","disabled");
    }

    jQuery( "#dialog-form" ).dialog({
            resizable: false,			
            height: 465,
			width: 380,
			modal: true,
            draggable: false,
			buttons: {
					"Ok": function(){
							// take the values from popup
							var sample_identifier = jQuery("#dialog-form").find('input[name=sample_identifier]').val();
							var sample_features = jQuery("#dialog-form").find('input[name=sample_features]').val();
							var exp_group = jQuery("#dialog-form").find('input[name=exp_group]').val();
							var volume = jQuery("#dialog-form").find('input[name=volume]').val();
							var concentration = jQuery("#dialog-form").find('input[name=concentration]').val();
							var owner = jQuery("#dialog-form").find('input[name=owner]').val();
							var date = jQuery("#dialog-form").find('input[name=date]').val();
							var tech_replicates = jQuery("#dialog-form").find('input[name=tech_replicates]').val();
                            var present = aliquotsRequested['aliquots'][idAl]['present'];
                            var counter = aliquotsRequested['aliquots'][idAl]['counter'];
                            if (present == "Warning")
                                present = checkAliquotExists (sample_identifier, date, owner);
                            // update the dictionary
                            delete aliquotsRequested['aliquots'][idAl];
                            updateDict(counter, sample_identifier, sample_features, exp_group, date, volume, concentration, owner, tech_replicates, present);
                            // update the row with the new values
                            var newid = sample_identifier;
                            updateRowTable(newid, posAl);
							// popup close
						    jQuery('#dialog-form').dialog("close");
						},
					"Cancel": function(){
                        // edit canceled
                        jQuery(this).dialog("close");
                        }
			}
		});
}


// update a row (pencil button)
function updateRowTable(idAl, posAl){
    jQuery("#aliquot_table").dataTable().fnUpdate([aliquotsRequested['aliquots'][idAl]['counter'], aliquotsRequested['aliquots'][idAl]['sample_identifier'], aliquotsRequested['aliquots'][idAl]['sample_features'], aliquotsRequested['aliquots'][idAl]['exp_group'], aliquotsRequested['aliquots'][idAl]['date'], aliquotsRequested['aliquots'][idAl]['volume'], aliquotsRequested['aliquots'][idAl]['concentration'], aliquotsRequested['aliquots'][idAl]['owner'], aliquotsRequested['aliquots'][idAl]['tech_replicates'], aliquotsRequested['aliquots'][idAl]['present'], null], posAl);
}



// read data from the table after post of file
function readTable(){
    var data = jQuery("#aliquot_table").dataTable().fnGetData();
    jQuery.each(data, function(key, d) { 
        updateDict(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9]);  
        });
}




function initRequest (){
jQuery("#create_request").submit( function(event){
			
			/*stop form from submitting normally*/
			event.stopImmediatePropagation();
			event.preventDefault();
			// get values from the page
			var request_descr = jQuery( 'input[name="request_description"]' ).val();
			var request_title = jQuery( 'input[name="request_title"]' ).val();
            var request_owner = jQuery( 'input[name="request_owner"]' ).val();
                        var operator_name = jQuery( 'select#operator_name' ).children(":selected").attr('id');

            // check on list of aliquots (at least one)
            var count = 0;
            var existAl = 0;
            jQuery.each(aliquotsRequested['aliquots'], function(key, d) { 
                count++;
                if (d['present'] == "True")
                    existAl++;
            });
            if (count == 0){
                alert("No aliquots inserted.");
                return;
            }
            if (existAl > 0){
                alert("Remove the exhausted aliquots before procede with the request.");
                return;
            }
            
            // check on title (mandatory)
            if (request_title == ""){
                alert("Insert the title before submit the request");
                return;
            }

		    url = base_url + "/new_request/";
		    
		    aliquotsRequested['title'] = request_title;
            aliquotsRequested['description'] = request_descr;
            aliquotsRequested['owner'] = request_owner;
            aliquotsRequested['operator'] = operator_name;
			
			//serializzo tutto
			var json_response = JSON.stringify(aliquotsRequested);
			// invio al server
			jQuery.ajax({
						type:'POST',    
                        url:url,
				        data: json_response, 
                        dataType: "json",                  
						error: function(data) { 
                            alert("Submission data error! Please, try again.\n" +data.responseText.slice(0,500), "Error"); 
                        }

            });
     });
}
