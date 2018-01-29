
// data structure for the request
aliquotsRequested = {'idplan':'', 'title':'', 'description':'', 'operator':'', 'owner': ''}
// counter of requested aliquots


// initialization function of the page
jQuery(document).ready(function(){

    // data table initialization
    generate_table();    
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
            { "sTitle": "GenID" },
            { "sTitle": "Aliquot Generation Date" },
            { "sTitle": "Volume (ul)" },
            { "sTitle": "Concentration (ng/ul)" },
            { "sTitle": "Technical Replicates" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    });

}


function initRequest (){
jQuery("#create_req_button").click( function(event){
			
			// get values from the page
      var idplan = jQuery('input[name="request_title"]').attr('idplan');
			var request_descr = jQuery( 'textarea[name="request_description"]' ).val();
			var request_title = jQuery( 'input[name="request_title"]' ).val();
      var request_owner = jQuery( 'input[name="request_owner"]' ).val();
                        var operator_name = jQuery( 'select#operator_name' ).children(":selected").attr('id');

      // check on title (mandatory)
      if (request_title == ""){
          alert("Insert the title before submit the request");
          return;
      }
      console.log('send data');
	    url = base_url + "/finalize_request/";
	    
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



