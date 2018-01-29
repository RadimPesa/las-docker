
$(document).ready(function () {	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Dilution","aliquote_fin");
		return;
	}
	
	$("#aliq").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
	});
	
	derivazioni_fallite(lisfallite);
	
	$("#update").click(function(event){		
		var tab=$("#aliq").dataTable();
		var numtr=tab.$("tr");
		if(numtr.length==0){
			event.preventDefault();
			alert("No data to submit");
			return;
		}
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
	});
});

function derivazioni_fallite(lisfallite){
	var tab=$("#aliq").dataTable();
	//devo rendere opache le derivazioni fallite
	for(var i=0;i<lisfallite.length;i++){
		var idaldersched=lisfallite[i];
		var input=tab.$("tr.interna").find("input[id_aldersched="+idaldersched+"]");
		var tr=$(input).parent().parent();
		$(tr).children().css("opacity","0.3");
		$(tr).addClass("failed");
		$(tr).find("td.td_name").text("Failed");
	}
}