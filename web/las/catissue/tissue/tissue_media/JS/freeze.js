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
		$("#conferma").attr("disabled",false);
	});
	
	//creo la finestra di popup
	$(".anchor").popupWindow({
		height:500, 
		width:800, 
		top:50, 
		left:50,
		scrollbars:1,
		resizable:1,
		menubar:1
	});
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
    	generate_result_table("Genotype_mismatch","aliquote_fin");
	}
	
	$("#conferma").click(function(){
		$("body").addClass("loading");
	});
	
});
