var contatore=1;

function aggiorna_prot(){
	var prot=$("#id_protocol option:selected").attr("value");
	var urlpr=base_url+"/api/slide/protocol/"+prot;
	$.getJSON(urlpr,function(d){
		if(d.data!="errore"){
			var tab=$("#aliq").dataTable();
			var righe=$("#temp tr");
			for(var j=0;j<righe.length;j++){
				var idriga=$(righe[j]).attr("id");
				var figli=$(righe[j]).children();
				var listmp=[];
				for(var kk=1;kk<=figli.length;kk++){
					listmp.push($(righe[j]).children(":nth-child("+kk+")").html());
				}
				var rowPos=tab.fnAddData(listmp);
				var tableRowElement = tab.fnGetNodes(rowPos[0]);
				$(tableRowElement).attr("id",idriga);
				$(tableRowElement).children(":nth-child(12)").children(":nth-child(1)").click(seleziona_aliquote);
				$(tableRowElement).children(":nth-child(13)").children(":nth-child(1)").click(elimina_pianificazione);
				$(righe[j]).remove();
			}
			tab.$("tr").attr("align","center");
			var listaaliqtipi=d.tipi;
			//prendo il valore del tipo di aliq per tutte quelle della tabella
			var lista=tab.$("tr");
			var k=1;
			var nodes = tab.$("tr");
			var oid = [];
			var ii=0;
			$(nodes).filter('tr').each( function() {
				oid[ii] = $(this).attr('id'); 
				ii++;
			});
			for(var i=0;i<lista.length;i++){
				//devo vedere se il tipo di aliq in ingresso va
				//bene per quel protocollo
				var tipoaliqoriginale=$($(lista[i]).children(":nth-child(9)").children()).val();
				trovato=0;
				for(var j=0;j<listaaliqtipi.length;j++){
					if(listaaliqtipi[j]==tipoaliqoriginale){
						trovato=1;
						break;
					}
				}
				if (trovato==0){
					$(lista[i]).hide();
					$("#temp").append($(lista[i]));
					var pos = tab.fnGetPosition($("#" + oid[i]).get(0));
					tab.fnDeleteRow( pos,null,true);
				}
				else{
					//devo rimettere a posto la numerazione
					//non uso l'update del data table perche' tanto dopo ricreo la tabella
					$(lista[i]).children(":nth-child(1)").text(k);
					k=k+1;
				}			
			}
			$("#aliq").dataTable({
				"bDestroy":true,
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"bInfo": true,
				"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
				"bAutoWidth": false });
			tab.fnDraw();
		}
		else{
			alert("Select protocol");
		}
	});		
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function controlla(){
	if($("#id_protocol option:selected").text()=="---------"){
		alert("Please select a protocol");
		return false;
	}	
	else{
		return true;
	}
}

function seleziona_aliquote(){
	if(controlla()){
		var tab=$("#aliq").dataTable();
		var righetab=tab.$("tr");
		//conto quante sono le aliquote selezionate nella colonna select
		var lista=$(righetab).children(":nth-child(12)").children(":checked");
		var listaabort=$(righetab).children(":nth-child(13)").children(":nth-child(1)");
		//se non c'e' niente selezionato, riabilito il protocollo
		if (lista.length==0){
			$("#id_protocol").attr("disabled",false);
			$(listaabort).attr("disabled",false);
		}
		else{
			//disabilito la possibilita' di cambiare il protocollo
			$("#id_protocol").attr("disabled",true);
			$(listaabort).attr("disabled",true);
		}
		
		if(lista.length==righetab.length){
			$("#seltutte").val("Deselect all");
			$("#seltutte").attr("sel","s");
		}
		else{
			$("#seltutte").val("Select all");
			$("#seltutte").removeAttr("sel");
		}
		//metto il select selezionato all'interno della div chiamata select per fare 
		//in modo che se anche l'utente cambia pagina nella tabella, le aliquote che
		//ha selezionato nella pagina prima rimangano memorizzate
		var selez=$(this).is(':checked');
		if(selez){
			$("#select").append($(this).parent().html());
			//copio anche il gen id
			$("#select").append($(this).parent().parent().children(":nth-child(2)").html());
		}
		else{
			//se l'utente ha deselezionato il select, tolgo quest'ultimo dalla lista
			var idsel=$(this).attr("id");
			$("#"+idsel).remove();
		}
	}
	else{
		$(this).removeAttr("checked");
	}
}

//viene eseguita quando si clicca su un abort qualsiasi
function elimina_pianificazione(){
	if(controlla()){
		var tab=$("#aliq").dataTable();
		var righetab=tab.$("tr");
		//conto quante sono le aliquote selezionate nella colonna abort
		var listaabort=$(righetab).children(":nth-child(13)").children(":checked");
		var listaselect=$(righetab).children(":nth-child(12)").children(":nth-child(1)");
		//se non c'e' niente selezionato, riabilito il protocollo
		if (listaabort.length==0){
			$("#id_protocol,#seltutte,#deseltutte").attr("disabled",false);
			$(listaselect).attr("disabled",false);
			$("#cancella").val("");
		}
		else{
			//disabilito la possibilita' di cambiare il protocollo
			$("#id_protocol,#seltutte,#deseltutte").attr("disabled",true);
			$(listaselect).attr("disabled",true);
			$("#cancella").val("s");
		}
		var selez=$(this).is(':checked');
		if(selez){
			$("#select").append($(this).parent().html());
			//copio anche il gen id
			$("#select").append($(this).parent().parent().children(":nth-child(2)").html());
		}
		else{
			//se l'utente ha deselezionato il select, tolgo quest'ultimo dalla lista
			var idsel=$(this).attr("id");
			$("#"+idsel).remove();
		}
	}
	else{
		$(this).removeAttr("checked");
	}
}

function selez_deselez(){
	if(controlla()){
		if ($(this).attr("sel")=="s"){
			$(this).val("Select all");
			$(this).removeAttr("sel");
			var tab=$("#aliq").dataTable();
			var righetab=tab.$("tr");
			//conto quante sono le aliquote selezionate nella colonna select
			var listaabort=$(righetab).children(":nth-child(13)").children(":nth-child(1)");
			//abilito la possibilita' di cambiare protocollo e di cancellare le pianificazioni
			$("#id_protocol").attr("disabled",false);
			$(listaabort).attr("disabled",false);
			//cancello tutto quello che c'è nella div select
			$("#select").children().remove();
			$("#select").text("");
			var lista=$(righetab).children(":nth-child(12)").children();
			$(lista).removeAttr("checked");
		}
		else{
			$(this).val("Deselect all");
			$(this).attr("sel","s");
			var tab=$("#aliq").dataTable();
			var righetab=tab.$("tr");
			//conto quante sono le aliquote selezionate nella colonna abort
			var listaabort=$(righetab).children(":nth-child(13)").children(":nth-child(1)");
			//disabilito la possibilita' di cambiare protocollo e di cancellare le pianificazioni
			$("#id_protocol").attr("disabled",true);
			$(listaabort).attr("disabled",true);
			//cancello tutto quello che c'è nella div select
			$("#select").children().remove();
			$("#select").text("");
			var lista=$(righetab).children(":nth-child(12)").children();
			for (var j=0;j<lista.length;j++){
				$(lista[j]).attr("checked","checked");
				$("#select").append($(lista[j]).parent().html());
				//copio anche il gen id
				$("#select").append($(lista[j]).parent().parent().children(":nth-child(2)").html());
			}
		}
	}
}

function aggiorna_dati(){
	//solo se nella tabella ho delle aliquote
	var listarighe=$("#aliq tr");
	if (listarighe.length>1){
		var lbarc="";
		var lgen="";
		var lis_pezzi_url=[];
		var utente=$("#actual_username").val();
		var url=base_url+"/api/storage/tube/";
		var listagen=$("#aliq tr").children(":nth-child(2)").not("th");
		//prendo i barcode della tabella
		var listabarc=$("#aliq tr").children(":nth-child(8)").not("th");
		//prendo i campi relativi alla piastra
		var listapias=$("#aliq tr").children(":nth-child(6)").not("th");
		//prendo i campi relativi alla posizione della provetta
		var listapos=$("#aliq tr").children(":nth-child(7)").not("th");
		//prendo i campi relativi alla posizione della piastra
		var listapospiastra=$("#aliq tr").children(":nth-child(5)").not("th");
		//prendo i campi relativi al rack
		var listarack=$("#aliq tr").children(":nth-child(4)").not("th");
		//prendo i campi relativi al freezer
		var listafreezer=$("#aliq tr").children(":nth-child(3)").not("th");
		
		for (var i=0;i<listagen.length;i++){
			//mi da' il gen attuale
			var gen=$(listagen[i]).text();
			lgen=lgen+gen+"&";
			lgen = lgen.replace(/#/g, "%23");
			if (lgen.length>2000){
	            lis_pezzi_url.push(lgen);
	            lgen="";
			}
		}
		if (lgen==""){
			lgen="-";
			lis_pezzi_url.push("-");
		}
		else{
			lis_pezzi_url.push(lgen);
		}
		var timer = setTimeout(function(){$("body").addClass("loading");},1000);
		for (var j=0;j<lis_pezzi_url.length;j++){		
			urlst=url+lis_pezzi_url[j]+"/"+utente;
			$.getJSON(urlst,function(d){
				if (d.data!="errore"){
					diz=JSON.parse(d.data);
					if(Object.size(diz)!=0){
						//scrivo nel campo apposito l'indicazione della posizione della provetta
						for(var i=0;i<listagen.length;i++){
							var gen=String($(listagen[i]).text().trim());
							var listaval=diz[gen];
							if(listaval!=undefined){
								var val=listaval.split("|");								
								
								$(listabarc[i]).text(val[0]);
								$(listapos[i]).text(val[1]);
								$(listapias[i]).text(val[2]);
								$(listapospiastra[i]).text(val[3]);
								$(listarack[i]).text(val[4]);
								$(listafreezer[i]).text(val[5]);
							}
						}
					}
					//lo faccio solo una volta alla fine del ciclo generale
					if (contatore==lis_pezzi_url.length){
						$("#aliq").dataTable({
							"bPaginate": true,
							"bLengthChange": true,
							"bFilter": true,
							"bSort": true,
							"bInfo": true,
							"bAutoWidth": false, 
							"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]});
						
						clearTimeout(timer);
						$("body").removeClass("loading");
						//salvo il numero totale di righe della tabella
						var tab=$("#aliq").dataTable();
						var righetab=tab.$("tr");

						$("#num_aliq").attr("value",righetab.length);
						//metto l'evento click sul select
						$(righetab).children(":nth-child(12)").children(":nth-child(1)").click(seleziona_aliquote);
						//metto l'evento click sull'abort
						$(righetab).children(":nth-child(13)").children(":nth-child(1)").click(elimina_pianificazione);
					}				
				}
				else{
					alert("Problems while interacting with storage");
				}
				contatore++;
			});
		}
	}
	else{
		$("#aliq").dataTable({
			"bPaginate": true,
			"bLengthChange": true,
			"bFilter": true,
			"bSort": true,
			"bInfo": true,
			"bAutoWidth": false, 
			"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]});
		//salvo il numero totale di righe della tabella
		var tab=$("#aliq").dataTable();
		var righetab=tab.$("tr");

		$("#num_aliq").attr("value",righetab.length);
		//metto l'evento click sul select
		$(".check_sel").click(seleziona_aliquote);
		//metto l'evento click sull'abort
		$(".check_canc").click(elimina_pianificazione);
	}	
}

$(document).ready(function () {
	var tabfin=$("#finale");
	//se sono nella pagina del report per il canc
	if (tabfin.length!=0){
    	generate_result_table("Deleted","finale");
	}
	else{		
		aggiorna_dati();
	}
		
	$("#id_protocol").change(aggiorna_prot);
	$("#seltutte").click(selez_deselez);
		
	$("#conferma").click(function(event){
		var righe=$("#aliq :checked");
		
		//controllo se tutti i campi sono stati riempiti
		if(!controlla()){
			event.preventDefault();
		}
		else{			
			//seleziono tutti i select della div select
			$("#select :checkbox").attr("checked", true);		
			$("#id_protocol").attr("disabled",false);
		}		
	});
});