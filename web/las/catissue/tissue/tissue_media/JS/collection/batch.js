$(document).ready(function () {

	$("#tastofile").click(function(){
		$("#id_file_cont").click();
	});
	
	//per far comparire nell'input i nomi dei file caricati
	$("#id_file_cont").change(function(){
		var files = $('#id_file_cont')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+",";
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1);
		$("#filename").val(nomfile);
	});
	
	$("#conferma").click(function(event){
		var files=$("#id_file_cont")[0].files;
		if (files.length==0){
			alert("Please insert a file");
			event.preventDefault();
		}
	});
	
	$("#aliquots_table").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
	});
	
	var columnsToHide=[];
	$("#aliquots_table").find('th').each(function(i) {
		 
        var columnIndex = $(this).index();
        var rows = $(this).parents('table').find('tr td:nth-child(' + (i + 1) + ')'); //Find all rows of each column 
        var rowsLength = $(rows).length;
        var emptyRows = 0;
 
        rows.each(function(r) {
            if (this.innerHTML == '')
                emptyRows++;
        }); 
 
        if(emptyRows == rowsLength) {
            columnsToHide.push(columnIndex);  //If all rows in the colmun are empty, add index to array
        } 
    });
    for(var i=0; i< columnsToHide.length; i++) {
    	$("#aliquots_table").dataTable().fnSetColumnVis( columnsToHide[i], false ); //Hide columns by index
    }
	
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Collection","aliquote_fin");
	}
	
	//per popolare la lista con dentro i wg
	var lisworkgr=$("#id_workgr");
	if(lisworkgr.length!=0){
		var liswg=workingGroups.split(",");
		for (var i=0;i<liswg.length;i++){
			$("#id_workgr").append("<option value="+liswg[i]+">"+liswg[i]+"</option>");
		}
	}
	//per prendere il valore del wg dal campo nascosto nel caso abbia gia' caricato il file
	var ww=$("#id_wgroup").val();
	if(ww!="/"){
		$("#id_workgr option[value="+ww+"]").attr("selected","selected");
		$("#id_workgr").attr("disabled",true);
	}
	$("#salvafin").click(function(event){
		var timer = setTimeout(function(){$("body").addClass("loading");},50);
	});	
});