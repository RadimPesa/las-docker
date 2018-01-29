//per dire al server di eliminare quel trasferimento
function canc(id){
	var data = {
			canc:true,
			idtrasf:id
    };
	var url=base_url+"/transfer/pending/";
	$.post(url, data, function (result) {
    	if (result == "failure") {
    		alert("Error");
    	}
    });
	
}

/* Get the rows which are currently selected */
function fnGetSelected( oTableLocal )
{
	var aReturn = new Array();
	var aTrs = oTableLocal.fnGetNodes();
	
	for ( var i=0 ; i<aTrs.length ; i++ )
	{
		if ( $(aTrs[i]).hasClass('row_selected') )
		{
			aReturn.push( aTrs[i] );
		}
	}
	return aReturn;
}

$(document).ready(function () {
	var tabella=$("#trasf").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });
	
	/* Add event listener for deleting row  */
    $("#trasf tbody td.control_center img").live("click", function () {
    	var nTr = $(this).parents('tr')[0];
    	var id=$(nTr).children(":nth-child(1)").children().val();
    	canc(id);
        
        $("#trasf").dataTable().fnDeleteRow( nTr );
        
    } );
	
	/* Add a click handler to the rows - this could be used as a callback */
	$("#trasf tbody").click(function(event) {
		$(tabella.fnSettings().aoData).each(function (){
			$(this.nTr).removeClass('row_selected');
		});
		$(event.target.parentNode).addClass('row_selected');
		$("#select").attr("disabled",false);
	});
	
	$("#select").click(function(event){
		event.preventDefault();
		var anSelected = fnGetSelected( tabella );
		//prendo l'id del trasferimento
		var id=$(anSelected[0]).children(":nth-child(1)").children().val();
		if(id!=undefined){
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			idtrasf:id
		    };
	    	var ricev=$("#ricezione").val();
	    	if (ricev=="True"){
	    		var url=base_url+"/transfer/receive/";
	    	}
	    	else{
	    		var url=base_url+"/transfer/pending/";
	    	}
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	
		    	$("#form_fin").append("<input type='hidden' name='final' />");
		    	$("#form_fin").submit();
		    });
		}
		else{
			alert("Please select a request.");
		}
		
	});
});
