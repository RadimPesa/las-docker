var duplicates=false;

$(document).ready(function () {
	$("a:contains('LAS Home')").remove();	
	$("#home").removeAttr("href");
	//devo vedere che nella lista dei gen non ci siano doppioni. Se si' blocco la possibilita' di inserire il file
	$("#aggiungi_file").attr("disabled",false);
	var lisgen=window.opener.$(".gen_aliq_der");
	var lisvalgen=[];
	for(var i=0;i<lisgen.length;i++){
		var gen=$(lisgen[i]).val();
		if($.inArray(gen,lisvalgen)==-1){
			lisvalgen.push(gen);
		}
		else{
			duplicates=true;
			$("#aggiungi_file").attr("disabled",true);
		}
	}	
	//se sto usando questa pagina per la rivalutazione devo inserire un campo
	//per comunicare alla vista che e' una rivalutazione
	volume=window.opener.$("#volume_0");
	//se non c'e' il campo per il volume, vuol dire che sono nella pagina della rivalutazione
	if(volume.length==0){
		$("#iniziale form").append("<input type='hidden' id='riv' name='riv' />");
	}
	
	//per sottomettere il form quando si clicca sulla scritta "file template"
	$("#file").click(function(){
		if(duplicates){
			alert("There are some duplicates in the aliquots to be derived. You cannot insert a file");
		}
		else{
			$("#templ").val("vedi_file");
			$("#form_gen").submit();
		}
	});
	
	$("#aggiungi_file").click(function(event){
		var file=$("#id_file").attr("value");
		if(file==""){
			alert("Please load a file");
			event.preventDefault();
		}
		else{
			var val=file.split(".");
			var estens=val[val.length-1];
			if ((estens=="xls")||(estens=="xlsx")){
				alert("Please change Excel file in a tab delimited one");
				event.preventDefault();
			}
			else{
				$("#templ").val("ins_file");
				$("#form_gen").submit();
			}
		}
	});
	
	//all'inizio imposto il campo hidden del protocollo al valore attuale
	var prot=$("#id_prot option:selected").val();
	$("#tipo_prot").val(prot);
	
	$("#id_prot").change(function(){
		var prot=$("#id_prot option:selected").val();
		$("#tipo_prot").val(prot);
	});
});