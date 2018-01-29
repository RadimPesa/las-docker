
// data structure for the request
aliquotsRequested = {'idplan':'', 'title':'', 'description':'', 'operator':'', 'owner': '', 'aliquots':{}}
// counter of requested aliquots
aliquotsCounter = 0;


// initialization function of the page
jQuery(document).ready(function(){
    // data table initialization
    generate_table();    
    readTable();
    initRequest();
	
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
            { "sTitle": "GenID" },
            { "sTitle": "Aliquot Generation Date" },
            { "sTitle": "Volume" },
            { "sTitle": "Concentration" },
            { "sTitle": "Taken Volume" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    });

}


// update dictionary. The key is the sample_identifier (genealogy or label). Manage the two cases
function updateDict(counter, genealogy, date, volume, concentration, takenvolume, owner){
    aliquotsRequested['aliquots'][genealogy] = {'genealogy':genealogy, 'date': date, 'volume': volume, 'concentration':concentration, 'takenvolume': takenvolume, 'owner':owner, 'counter':counter}
    if (counter > aliquotsCounter)
        aliquotsCounter = counter;
    if (aliquotsCounter > 0)
        jQuery('#create_req_button').removeAttr("disabled");

}



// read data from the table after post of file
function readTable(){
    var data = jQuery("#aliquot_table").dataTable().fnGetData();
    jQuery.each(data, function(key, d) { 
        updateDict(d[0], d[1], d[2], d[3], d[4], d[5], d[6]);  
        });
}


function initRequest (){
	jQuery("#create_req_button").click( function(event){		
		//get values from the page
		var idplan = jQuery('input[name="request_title"]').attr('idplan');
		var request_descr = jQuery( 'textarea[name="request_description"]' ).val();
		var request_title = jQuery( 'input[name="request_title"]' ).val();
		var request_owner = jQuery( 'input[name="request_owner"]' ).val();
		var operator_name = jQuery( 'select#operator_name' ).val();

		// check on list of aliquots (at least one)
		if (Object.keys(aliquotsRequested['aliquots']).length == 0){
			alert("No aliquots inserted.");
			return;
		}
      
		// check on title (mandatory)
		if (request_title == ""){
			alert("Insert the title before submit the request");
			return;
		}
	    url = base_url + "/new_request/";
	    
	    aliquotsRequested['idplan'] = idplan;
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



