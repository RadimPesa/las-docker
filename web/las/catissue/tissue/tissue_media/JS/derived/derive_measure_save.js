function aggiungi_riga(){
	var tabella = document.getElementById("inizio");
	//prendo il numero di righe della tabella
	var rowCount = tabella.rows.length;
	var row = tabella.insertRow(rowCount);
	//do' un identificativo alle righe aggiunte
	$(row).attr("class","aggiunte");
	//centro tutte le celle che apparterranno alla riga
	$(row).attr("align","center");
	//inserisco la cella con dentro il numero d'ordine
    var cell1 = row.insertCell(0);
    cell1.innerHTML =rowCount;
    var indice=(rowCount-1).toString();
    //inserisco la cella con dentro l'input per il tipo di misura
    var cell2 = row.insertCell(1);
    //metto un input nascosto per comunicare alla vista che e' una misura aggiunta
    //dall'utente
    cell2.innerHTML="<td align=\"center\">  <input id='nuovamis_"+indice+"' type='hidden' name='nuovamis_"+indice+"' /> <input id='tipo_"+indice+"' type='text' name='tipo_"+indice+"' size=12 /> </td>";
    //inserisco la cella con dentro l'input per l'unita' di misura
    var cell3 = row.insertCell(2);
    cell3.innerHTML="<td align='center'> <input id='unit_"+indice+"' type='text' name='unit_"+indice+"' size=10 /> </td>";
    //inserisco la cella con dentro l'input per il tipo dello strumento
    var cell4 = row.insertCell(3);
    var stringa="<td align='center'> <select id='tipostrum_"+indice+"' name='tipostrum_"+indice+"'>";
    stringa+="<option selected='selected' value=''>---------</option>";
    //vado a prendere tutti gli strumenti presenti
	var url=base_url+"/api/instrument/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			for(i=0;i<d.data.length;i++){
				stringa+="<option value='"+d.data[i].id+"'>"+d.data[i].name+" "+d.data[i].code+"</option>";
			}
		    stringa=stringa+"</td>";
		    cell4.innerHTML=stringa;
		    //metto un listener per far apparire il codice dello strumento nell'input a
		    //fianco
			$("#tipostrum_"+indice).change(aggiorna_strumento);
		}
	});

    //inserisco la cella con dentro l'input per il tipo dello strumento
    var cell5 = row.insertCell(4);
    cell5.innerHTML="<td align='center'> <input id='codstrum_"+indice+"' type='text' name='codstrum_"+indice+"' readonly='readonly' size=12 /> </td>";
    //inserisco la cella con dentro l'input per il valore della misura
    var cell6 = row.insertCell(5);
    cell6.innerHTML="<td align='center'> <input id='val_"+indice+"' type='text' name='val_"+indice+"' size=6 maxlength='7' /> </td>";

    //imposto l'autocompletamento per la nuova misura
    $("#tipo_"+indice).autocomplete({
		source:base_url+'/ajax/revalue/newmeasuretype/autocomplete/'
	});

  //imposto l'autocompletamento per la nuova unita' di misura
    $("#unit_"+indice).autocomplete({
		source:base_url+'/ajax/revalue/newmeasureunit/autocomplete/'
	});
}

function aggiorna_strumento(){
	//prendo l'id del select
	var id=$(this).attr("id");
	//divido in base al _ per prendere l'indice della misura
	var indice=id.split("_");
	//prendo il nome dello strum con il codice
	var nomestrum=$(this).children(":selected").text();
	nom=nomestrum.split(" ");
	//in indice[1] ho l'indice della misura effettuata
	//in nom[1] ho il codice dello strumento e lo scrivo nell'input
	$("#codstrum_"+indice[1]).attr("value",nom[1]);
}

//serve a mettere il numero di aliq nel campo nascosto apposito in modo da comunicare
//alla view quante aliq ho.
function copia_lunghezza_controlla(){
	var tabella = document.getElementById("inizio");
	//prendo il numero di righe della tabella
	var rowCount = tabella.rows.length;
	righe=rowCount-1;
	$("#lunghezza").attr("value",righe);
}

function chiudi_finestra(){
	//vedo se sto usando la schermata per misurare le aliq tutte insieme o singolarmente
	var tutti=$("#tutti").attr("value");
	if(tutti=="True"){
		//serve per discriminare tra la schermata dei derivati o delle rivalutazioni
		if(volume.length==0){
			//rivalutazione
			window.opener.$("#aliq tr td:nth-child(6)").children().attr("sel","s");
			window.opener.$("#aliq tr td:nth-child(7)").children().attr("disabled",false);
			var listainp=window.opener.$("#aliq tr").children();
			for(var i=0;i<listainp.length;i++){
				//guardo se l'aliquota e' esaurita
				var fallita=window.opener.$("#exh_"+i+":checked");
				//se e' fallita
				if (fallita.length==1){
					window.opener.$("#view_misura_"+i).attr("disabled",true);
					window.opener.$("#add_misura_"+i).removeAttr("sel");
				}
			}
		}
		else{
			window.opener.$("#aliq tr td:nth-child(8)").children().attr("sel","s");
			window.opener.$("#aliq tr td:nth-child(9)").children().attr("disabled",false);
			//prendo tutte le aliquote
			var listainp=window.opener.$("#aliq tr td:nth-child(3)").children();
			for(var i=0;i<listainp.length;i++){
				//guardo se la derivazione e' fallita
				var fallita=window.opener.$("#outcome_"+i+":checked");
				//se e' fallita
				if (fallita.length==1){
					window.opener.$("#view_misura_"+i).attr("disabled",true);
				}
			}
		}
	}
	else{
		//faccio in modo che mi metta un attributo nel tasto 'add measure' per dire che
		//le misure per quell'aliquota sono state inserite
		var gen=$("#geneal").attr("value");
		var num;
		//serve per discriminare tra la schermata dei derivati o delle rivalutazioni
		if(volume.length==0){
			var listarighe=window.opener.$("#aliq tr td:nth-child(3)");
		}
		else{
			//prendo tutti i td della tabella con dentro i genid
			var listarighe=window.opener.$("#aliq tr td:nth-child(3)");
		}
		for (i=0;i<listarighe.length;i++){
			var genlocale=$(listarighe[i]).children().attr("value");
			if(genlocale==gen){
				var id=$(listarighe[i]).children().attr("id");
				var numero=id.split("_");
				var num=numero[1];
				break;
			}
		}
		var idtastomis="#add_misura_"+num;
		window.opener.$(idtastomis).attr("sel","s");
	}
	window.close();
}

$(document).ready(function () {
	$("#conf_all").attr("disabled",false);
	
	$("a:contains('LAS Home')").remove();
	$("#home").removeAttr("href");

	//guardo se sono nella pagina delle rivalutazioni. 
	volume=window.opener.$("#volume_0");
	//se non c'e' il campo per il volume, vuol dire che sono nella pagina della rivalutazione
	if(volume.length==0){
		//$("#inizio2,#ultimo_br").remove();
		//$("#content form").attr("action","/revalue/execute/measure/save/");
		$("#content form").append("<input type='hidden' id='riv' name='riv' />");
	}
	else{
		//cambio l'unita' di misura dei GE/ml in GE
		var unitmis=$("input[value='GE/ml']");
		var tipmis=$("input[value='GE/Vex']");
		var tdunitmis=$("td:contains('GE/ml')");
		var tdtipmis=$("td:contains('GE/Vex')");
		$(tdunitmis).text("GE");
		$(tdtipmis).text("GE");
		$(tdunitmis).append($(unitmis));
		$(tdtipmis).append($(tipmis));
	}
	
	$("#add_measure").click(function(event){
		event.preventDefault();
		aggiungi_riga();
	});
	$("#close").click(chiudi_finestra);
	
	$("#tastofile").click(function(){
		$("#id_file").click();
	});
	
	$("#id_file").change(function(){
		var files = $('#id_file')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
	});
	
	$("#conf_all").click(copia_lunghezza_controlla);
	
	//verifico che ci siano tutti i dati prima di permettere la conferma
	//Se sono nella parte di rivalutazione, controlla che non ci siano piu' valori
	//di concentrazione e se si' fa scegliere all'utente quella effettiva da salvare
	$("#conf_all").click(function(event){
		var ins_corretti=true;
		//conto le righe della tabella
		var righe=$("#inizio tr");
		var regex=/^[0-9.]+$/;
		//variabile per capire se l'utente inserisce almeno un valore nelle misure
		var inserito=false;
		//variabile per verificare che ci sia la concentrazione nelle misure inserite
		//perche' nell'ultimo passo della derivazione è fondamentale avere la concentrazione
		var concpresente=false;		
		var campiobbl=$("#campiprot").val();
		for(i=1;i<righe.length;i++){
			//verifico che ci siano tutti i valori numerici, solo se il protocollo di misura lo prevede			
			var idval="#val_"+(i-1);
			if (campiobbl=="True"){
				if(!($(idval).attr("value"))){
					alert("Insert value in line "+i);
					event.preventDefault();
					return;
				}
			}

			var numero=$(idval).val();
			if (numero!=""){
				inserito=true;
			}
			if((numero!="")&&(!regex.test(numero))){
				alert("You can only insert number. Correct value in line "+i);
				event.preventDefault();
				return;
			}
			//verifico che ci siano tutti i tipi di misure
			var idtipom="#tipo_"+(i-1);
			if(!($(idtipom).attr("value"))){
				alert("Insert measure type in line "+i);
				event.preventDefault();
				return;
			}
			else{
				var misu=$(idtipom).val();
				if((misu=="concentration")&&(numero!="")){
					concpresente=true;
				}
			}
			//verifico che ci siano tutte le unita' di misura
			var idunitm="#unit_"+(i-1);
			if(!($(idunitm).attr("value"))){
				alert("Insert measure unit in line "+i);
				event.preventDefault();
				return;
			}
			//verifico che ci siano tutti i tipi di strumenti
			var idstrum="#tipostrum_"+(i-1);
			if(!($(idstrum).attr("value"))){
				alert("Insert instrument type in line "+i);
				event.preventDefault();
				return;
			}
			//verifico che ci siano tutti i codici degli strumenti
			var codstrum="#codstrum_"+(i-1);
			if(!($(codstrum).attr("value"))){
				alert("Insert instrument code in line "+i);
				event.preventDefault();
				return;
			}
		}
		
		if(!(inserito)&&(campiobbl!="True")){
			alert("You have to insert at least one measure");
			event.preventDefault();
			return;
		}
		
		//solo se sono nella pagina delle derivazioni
		if(!(concpresente)&&(campiobbl=="False")&&(volume.length!=0)){
			alert("Please insert value for concentration");
			event.preventDefault();
			return;
		}
		
		var volinserito=$("#volusato").val();
		if((volinserito!="")&&(!regex.test(volinserito))){
			alert("You can only insert number. Correct value for used volume");
			event.preventDefault();
			return;
		}
		
		//se sono nella pagina delle rivalutazioni verifico che, se e' stato inserito il 
		//volume attuale, sia stato scritto giusto
		if(volume.length==0){
			var volattuale=$("#volattuale").val();
			if((volattuale!="")&&(!regex.test(volattuale))){
				alert("You can only insert number. Correct value for current volume");
				event.preventDefault();
				return;
			}
		}
		
		//se sono nella pagina delle derivazioni
		if(volume.length!=0){
			var gen=$("#genealogy").attr("value");
			//prendo tutti i td della tabella con dentro i genid
			var listarighe=window.opener.$("#aliq tr td:nth-child(3)");
			for (i=0;i<listarighe.length;i++){
				var genlocale=$(listarighe[i]).children().attr("value");
				if(genlocale==gen){
					var id=$(listarighe[i]).children().attr("id");
					var numero=id.split("_");
					var num=numero[1];
					break;
				}
			}
			var idvolumefin="#volume_"+num;
			var volfin=window.opener.$(idvolumefin).val();
			if(parseFloat(volinserito)>parseFloat(volfin)){
				alert("Used volume is higher than outcome volume. Please correct.");
				event.preventDefault();
				return;
			}
		}
		
		//verifico che se c'e' il file ci sia anche il giudizio selezionato
		if($("#id_file").attr("value")){
			var selezionato=$("ul li label input:checked");
			if(selezionato.length==0){
				alert("Select a judgement for the file");
				event.preventDefault();
				return;
			}
		}
		//aggiungo un controllo sulle misure aggiunte
		var listarighe=$("#inizio tr[class=aggiunte]");
		if (listarighe.length!=0){
			//prendo le righe che c'erano gia' all'inizio
			var righevecchie=$("#inizio tr[class!=aggiunte]");
			//il -1 per togliere la prima riga di intestazione della tabella
			var lun=(righevecchie.length-1);
			//creo un vettore di lunghezza pari alle righe vecchie
			var x=new Array(lun);
			//salvo nel vettore i dati delle misure che ci sono gia'
			for (var i=0;i<(lun);i++){
				var inp=$(righevecchie[i+1]).children().children();
				//scandisco i primi quattro input e prendo i valori della nuova misura inserita
				var str="";
				for(var j=0;j<4;j++){
					var val=$(inp[j]).attr("value");
					var v=val.toLowerCase();
					str=str+v;
				}
				x[i]=str;
			}
			for (var i=0;i<listarighe.length;i++){
				//mi da' i cinque input con dentro i valori
				var inp=$(listarighe[i]).children().children();
				//scandisco i primi quattro input e prendo i valori della nuova misura inserita
				var str="";
				for(j=1;j<5;j++){
					//se sono nel campo dello strumento
					if(j==3){
						var nomestrum=$(inp[j]).children(":selected").text();
						nom=nomestrum.split(" ");
						//in nom[0] ho il nome dello strumento e lo concateno
						str=str+nom[0].toLowerCase();
					}
					else{
						var val=$(inp[j]).attr("value");
						str=str+val.toLowerCase();
					}
				}
				for(k=0;k<lun;k++){
					if(str==x[k]){
						alert("Measure inserted is identical to measure in line "+(k+1)+". Please correct.");
						event.preventDefault();
						return;
					}
				}
			}
		}
		
		//devo rimettere GE alla giusta unita' di misura
		//prendo i nomi delle misure. 
		//Non mi serve piu' perche' cambio solo il text del td e non il valore dell'input
		/*var listamis=$("#inizio tr td:nth-child(2)").children();
		//prendo le unita' di misura
		var listaunit=$("#inizio tr td:nth-child(3)").children();
		for (var k=0;k<listamis.length;k++){
			var valore=$(listamis[k]).val();
			if (valore=="GE"){
				$(listamis[k]).val("GE/Vex");
				$(listaunit[k]).val("GE/ml");
			}
		}*/
		//solo se sono nella schermata delle rivalutazioni
		if(volume.length==0){
			var lista = new Array();
			//prendo tutti i tipi di misura
			var tipi=$("#inizio tr td:nth-child(2)").children();
			//prendo il nome della misura
			for (i=0;i<tipi.length;i++){
				var mis=$(tipi[i]).attr("value");
				if (mis=="concentration"){
					//devo vedere se il valore della concentrazione e' stato inserito
					var idconc="#val_"+i;
					var valconc=$(idconc).val();
					if (valconc!=""){
						lista.push(tipi[i]);
					}
				}
			}
			if (lista.length>1){
				event.preventDefault();
				for(i=1;i<righe.length;i++){
					//disabilito gli input impedendo all'utente di modificare
					//i valori che ha inserito prima
					var idval="#val_"+(i-1);
					var idtipom="#tipo_"+(i-1);
					var idunitm="#unit_"+(i-1);
					var idstrum="#tipostrum_"+(i-1);
					var codstrum="#codstrum_"+(i-1);
					$(idval+","+idtipom+","+idunitm+","+idstrum+","+codstrum).attr("readonly","readonly");
					$("#add_measure,#conf_all").remove();
				}
				//faccio apparire dei radio button per la scelta della conc
				//definitiva
				$("#ultimo_br").after("<h2>Select which concentration you want to save for the aliquot:</h2>" +
						"<table id='inizio4' border='2px' style='-moz-border-radius:0px;border-radius:0px;-webkit-border-radius:0px;float:left;border-style: solid;'>" +
						"<th>N</th><th>Measure Type</th><th>Measure Unit</th><th>Value</th><th>Select</th>");
				for(j=0;j<lista.length;j++){
					var id=$(lista[j]).attr("id");
					var numero=id.split("_");
					//lo converto a intero
					var num=parseInt(numero[1]);
					num=num+1;
					var st=num.toString()
					$("#inizio4 tr:last").after("<tr align='center'><td>"+st+"</td><td><input readonly='readonly' type='text' value="+$(lista[j]).attr("value")+" size=12 />"+
							"</td><td><input  readonly='readonly' type='text' value="+$("#unit_"+numero[1]).attr("value")+
							" size=10 /></td><td><input readonly='readonly' type='text' value="+$("#val_"+numero[1]).attr("value")+
							" size=6 /></td><td><input id='id_bad' type='radio' name='scelta_conc' value="+numero[1]+"></td></tr>");
				}
				$("#inizio4").after("<br style='clear:both'><br><input id='conf_tutto' class='button' type='submit' value='Confirm all' title='Click to confirm'/>");
				
				//verifico che sia selezionata una concentrazione
				$("#conf_tutto").click(function(event){
					var selezionato=$("#inizio4 input:checked");
					if(selezionato.length==0){
						alert("Select a concentration");
						event.preventDefault();
					}
				});
			}
		}
	});
});