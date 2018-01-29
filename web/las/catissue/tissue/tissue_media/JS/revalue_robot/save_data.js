//chiave l'id misura e valore il nome
var diznmis2={};

$(document).ready(function () {
	//estensione per jquery per rendere il contains insensibile a maiuscole/minuscole
	$.extend($.expr[":"], {
		"containsCaseInsens": function(elem, i, match, array) {
		return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
		}
	});
	
	for(var nome in diznomimisure){
		diznmis2[diznomimisure[nome]]=nome
	}
	
	//aggiungo l'unita' di misura per le concentrazioni. thconc globale
	thconc=$("#aliq th:containsCaseInsens('conce')");
	for(var i=0;i<thconc.length;i++){
		var testo=$(thconc[i]).text();
		var classeth=$(thconc[i]).attr("class");
		var check="";
		if(thconc.length>1){
			check=" (ng/ul)<input type='checkbox' nummis='"+classeth+"' class='ch_all' style='float:right;margin:0px;'>";
		}
		else if(thconc.length==1){
			check=" (ng/ul)";
		}
		$(thconc[i]).html(testo+check);
	}
	//se c'e' solo una concentrazione allora non faccio comparire la frase in cui dico all'utente di sceglierne una
	if(thconc.length<=1){
		$("#command").hide();
	}
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Revaluation","aliquote_fin");
		return;
	}
	
	write_table_measure();
	
	var tab=$("#aliq").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"bAutoWidth": false, 
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
	});
	
	$("input.ch_all").click(function(event){
		event.stopPropagation();
		check_all_concentration(this);		
	});
	tab.$("input.ch_single").click(function(event){
		check_single_concentration(this);
	});
	
	$("th").css("padding","6px 18px 6px 10px");
	
	$("#submit_button").click(function(event){
		event.preventDefault();		
		salva_dati_server();
	});
});

function write_table_measure(){
	for (var idqualsched in dizmisure){
		//prendo la riga giusta
		var row=$("#aliq tr.interna td.lis_gen").find("input[id_alsched='"+idqualsched+"']").parent().parent();
		for(var nomemis in dizmisure[idqualsched]){
			var classecella=diznomimisure[nomemis];
			//prendo la cella in base al valore della classe che ho trovato prima
			var cella=$(row).find("td."+classecella);
			//se e' una cella con la conc allora aggiungo anche il checkbox
			var check="";
			if(nomemis.toLowerCase().indexOf("conce")!=-1){
				//se ho piu' concentrazioni, allora metto un checkbox esplicito, altrimenti metto un input nascosto per recuperare 
				//l'id della misura quando dopo salvo i dati
				if(thconc.length>1){
					check="<input type='checkbox' nummis='"+classecella+"' class='ch_single' style='float:right;margin:0px;'>";
				}
				else{
					check="<input type='hidden' nummis='"+classecella+"' class='ch_single' >";
				}
			}
			$(cella).html(dizmisure[idqualsched][nomemis]["value"]+check);
		}
	}
}

function check_all_concentration(tasto){
	var nummis=$(tasto).attr("nummis");
	var tab=$("#aliq").dataTable();
	//mi prende tutti i check di quella colonna  
	var checkrighe=tab.$("input:checkbox[nummis='"+nummis+"']");
	if ($(tasto).is(":checked")){
		for (var i=0;i<checkrighe.length;i++){
			$(checkrighe[i]).attr("checked","checked");
			$(checkrighe[i]).attr("disabled",false);
			check_single_concentration($(checkrighe[i]));
		}
		//devo disabilitare i check negli altri th
		$("th input:checkbox[nummis!='"+nummis+"']").attr("disabled",true);
	}
	else{
		for (var i=0;i<checkrighe.length;i++){
			$(checkrighe[i]).removeAttr("checked");
			check_single_concentration($(checkrighe[i]));
		}
		$("th input:checkbox[nummis!='"+nummis+"']").attr("disabled",false);
	}
}

function check_single_concentration(tasto){
	var nummis=$(tasto).attr("nummis");
	var riga=$(tasto).parent().parent();
	if ($(tasto).is(":checked")){
		$(riga).find("input:checkbox[nummis!='"+nummis+"']").attr("disabled",true);
		$(riga).find("input:checkbox[nummis!='"+nummis+"']").removeAttr("checked");
	}
	else{
		$(riga).find("input:checkbox[nummis!='"+nummis+"']").attr("disabled",false);
	}
}

function salva_dati_server(){
	var tab=$("#aliq").dataTable();
	var lisrighe=tab.$("tr");
	
	if(lisrighe.length==0){
		alert("No data to submit");
		return;
	}
	//solo se c'e' piu' di una conc controllo che l'utente ne abbia scelta una
	if(thconc.length>1){
		for(var i=0;i<lisrighe.length;i++){
			var lischeck=$(lisrighe[i]).find("input:checkbox");
			//solo se per quella riga ho effettivamente piu' valori di conc, perche' se ne ho solo uno e' scontato che prendo quello
			if(lischeck.length>1){
				var checksel=$(lisrighe[i]).find("input:checkbox:checked");
				if(checksel.length==0){
					var gen=$(lisrighe[i]).find("td.lis_gen input").val();
					alert("Please select concentration for "+gen);
					return;
				}
			}
		}
	}
	//chiave l'idqualsched e valore un diz con misura conc e valore
	var dizfin={};
	//scandisco le righe per salvare le scelte di conc fatte dall'utente
	for(var i=0;i<lisrighe.length;i++){
		var checksel=$(lisrighe[i]).find("input.ch_single");
		if(checksel.length>1){
			checksel=$(lisrighe[i]).find("input:checkbox:checked");
		}		
		var valore=$(checksel).parent().text().trim();
		var idmisura=$(checksel).attr("nummis");
		//solo se c'e' almeno un valore per la conc, altrimenti non metto niente nel diz
		if (idmisura!=undefined){
			var idqualsched=$(lisrighe[i]).find("td.lis_gen input").attr("id_alsched");
			//devo trovare il nome della misura
			var nomemis=diznmis2[idmisura];
			dizfin[idqualsched]={"nome":nomemis,"val":valore};
		}
	}
	
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	//riempio le variabili da trasmettere con la post
	var data = {
			salva:true,
    		dizfin:JSON.stringify(dizfin)
    };
	var url=base_url+"/revalue/robot/savedata/";
	$.post(url, data, function (result) {
    	if (result == "failure") {
    		alert("Error");
    	}    	
    	$("#form_conf").append("<input type='hidden' name='finish' />");
		$("#form_conf").submit();
    });
}

