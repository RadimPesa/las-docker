listavetrini=[];
//chiave il nome del file senza contatore finale e valore il contatore finale
dizduplicati={};
//chiave il nome file originario e valore il nome dell'input file corrispondente che contiene quel file e il nome nuovo del file
dizfilename={};
//chiave il genid e valore la lista di file collegati
dizgenfile={};

function isInt(n) {
	return n % 1 === 0;
}

function disabilita_inserimento(check){
	var id_tasto=$(check).attr("id");
	//in numero_tasto[1] ho il valore della riga corrispondente al check box selezionato
	var numero_tasto=id_tasto.split("_");
	//blocco il tasto per fare delle misure
	var inputfile="#filename_"+numero_tasto[1];
	var tastofile="#tastofile_"+numero_tasto[1];
	var nomenuovofile="#newname_"+numero_tasto[1];
	if($(check).attr("checked")){
		//mi occupo del tasto per misurare le aliquote		
		$(inputfile).attr("disabled",true);
		$(inputfile).val("");
		$(tastofile).attr("disabled",true);
		$(nomenuovofile).attr("disabled",true);
		//devo cancellare eventuali file che avevo gia' inserito, quindi simulo un click sul CLEAR
		$("#newname_"+numero_tasto[1]+"_list span.listdel").click();
	}
	else{
		$(inputfile).attr("disabled",false);
		$(tastofile).attr("disabled",false);
		$(nomenuovofile).attr("disabled",false);
	}
}

function aggiungi_campione(){
	//genealogy ID dell'aliquota da inserire
	gen=$("#id_valid_barc").attr("value");
	if(gen==""){
		alert("Insert a genealogy ID or barcode");
	}
	else{
		var codice=gen.replace(/#/g,"%23");
		
		var url=base_url+"/api/label/insert/"+codice+"/";
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if(d.data=="inesistente"){
					alert("Aliquot does not exist in storage");
				}
				else if(d.data=="assente"){
					alert("Aliquot is not available for file insertion");
				}
				else{
					var trovato=0;
					//in d.data ho una lista con genid|barcode|posizione
					var lisvalori=d.data;
					for (var j=0;j<lisvalori.length;j++){
						var val=lisvalori[j].split("|");
						var gen=val[0];
						var barc=val[1];
						var pos=val[2];
						var aliqmadre=val[3];
						var data=val[4];
						var protocollo=val[5];
						dizdati[gen]={'date':data,'prot':protocollo};
						//solo se non l'ho gia' caricato
						if($.inArray(gen,listavetrini)==-1){
							var stringa="<tr class='interna' align='center'><td class='lis_indici'>"+String(parseInt(lunghezza)+1)+"</td>"+
							"<td class='lis_gen'>"+gen+"<input id='gen_"+String(lunghezza)+"' type='hidden' value='"+gen+"' name='gen_"+String(lunghezza)+"'>"+
							"</td><td>"+aliqmadre+"</td><td class='lis_barcode'>"+barc+"</td><td>"+pos+"</td><td></td><td><input id='idfile_"+String(lunghezza)+"' "+
							"class='file_none' type='file' style='display:none;' name='"+gen+"_0'>"+
							"<input id='filename_"+String(lunghezza)+"' type='text' style='display:inline;' size='10'><input id='tastofile_"+String(lunghezza)+"' "+
							"class='button classetastofile' type='button' style='display:inline;' value='Browse...'></td>"+
							"<td><input id='newname_"+String(lunghezza)+"' class='newnameclass' type='text' size='45' style='display:inline;' />"+
							"<button id='add_btn_"+String(lunghezza)+"' class='button add_btn' style='display:none;'>Add</button></td>"+
							"<td><input id='nofile_"+String(lunghezza)+"' class='checknofile' type='checkbox' size='5' name='nofile_"+String(lunghezza)+"' style='margin:10px;'></td></tr>";
							$("#aliq tbody").append(stringa);
							$("#newname_"+String(lunghezza)).boxlist();
							aggiorna_nome_file(String(lunghezza));
							lunghezza=parseInt(lunghezza)+1;
							listavetrini.push(gen);							
						}
					}
					var dizfile=$.parseJSON(d.dizfile);
					if(gen in dizfile){
						//il valore e' formato da una lista con dentro i nomi dei file gia' inseriti per quel genid
						var lista=dizfile[gen];
						for (var i=0;i<lista.length;i++){
							//divido prima in base al punto per togliere l'estensione e poi in base a _ per prendere il contatore
							var primosplit=lista[i].split(".");
							var secondosplit=primosplit[0].split("_");
							//prendo l'ultima parte dello split e guardo se e' un numero
							var cont=secondosplit[(secondosplit.length)-1];
							if (isInt(cont)){
								//riempio il dizionario con i contatori gia' usati
								var nomefile="";
								for (var j=0;j<secondosplit.length-1;j++){
									nomefile+=secondosplit[j]+"_";
								}
								nomefile=nomefile.substring(0,(nomefile.length)-1);
								//potrebbe esserci gia' perche' visto che ciclo su tutti i file potrei averlo inserito prima
								if (nomefile in dizduplicati){
									var contatore=dizduplicati[nomefile];
									if((parseInt(cont)+1)>contatore){
										dizduplicati[nomefile]=parseInt(cont)+1;
									}
								}
								else{
									dizduplicati[nomefile]=parseInt(cont)+1;
								}
							}
						}
					}
					$("#aliq").show();
					$("#id_valid_barc").val("");
					$("#id_valid_barc").focus();
				}
			}
		});
	}
}

function aggiorna_nome_file(jj){	
	var genid=$("#gen_"+String(jj)).val();
	var data=dizdati[genid]["date"];
	var prot=dizdati[genid]["prot"];
	prot = prot.replace(/ /g, '_');
	var nomefile=genid.substring(0,17)+"_"+prot+"_"+data;
	$("#newname_"+String(jj)).val(nomefile);	
}

function post_server(){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	//riempio le variabili da trasmettere con la post
	var data = {
			dati:true,
    		diz:JSON.stringify(dizfilename)
    };
	var url=base_url+"/label/save/file/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    		return;
    	}
    	$("#form_fin").append("<input type='hidden' name='finish' />");
    	clearTimeout(timer);
		$("body").removeClass("loading");
		$("#form_fin").submit();
    });
}

$(document).ready(function () {	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("File_label","aliquote_fin");
	}
	
	//abilito il boxlist per ogni riga della tabella
	$(".newnameclass").each(function( index ) {
		$(this).boxlist();
	});
	
	$(".add_btn").live("click", function(event){
		event.preventDefault();
	});
	for (var jj=0;jj<lunghezza;jj++){
		aggiorna_nome_file(jj);
	}
	
	
	
	$("#id_valid_barc").autocomplete({
	    source: function(request, response) {
    		var diz={
	                term: request.term,
	                WG:workingGroups,
	                filelabel:"Yes"
	        };
	        $.ajax({
	            url: base_url+'/ajax/derived/autocomplete/',
	            dataType: "json",
	            data: diz,
	            success: function(data) {
	                response(data);
	            }
	        });
	    },
    });
	
	$(".classetastofile").live("click", function(){
		var id=$(this).attr("id");
		var val=id.split("_");
		$("#idfile_"+val[1]).click();
	});
	
	lisestensioni=["jpg","jpeg","gif","png","tiff"];
	var stringa="";
	for (var j=0;j<lisestensioni.length;j++){
		stringa+="\""+lisestensioni[j]+"\", ";
	}
	stringa=stringa.substring(0,stringa.length-2);
	$("#istruzioni").text("Please note that only "+stringa+" files are allowed.");
	
	if(lunghezza==0){
		$("#aliq").hide();
	}
	
	$(".file_none").live("change", function(){
		var files = $(this)[0].files;
		var nomfile="";
		var id=$(this).attr("id");
		var val=id.split("_");
		for (var i = 0; i < files.length; i++) {
			var valfile=files[i].name.split(".");
			var estens=valfile[valfile.length-1];
			if($.inArray(estens,lisestensioni)==-1){
				alert("File extension of "+files[i].name+" is not allowed");
				$("#filename_"+val[1]).val("");
				$(this).val("");
				return;
			}			
	        nomfile+=files[i].name.split("\\").pop()+",";	    
			//tolgo la virgola finale
			nomfile = nomfile.substring(0, nomfile.length - 1);
			if(nomfile in dizfilename){
				alert("File already loaded in this session. Please rename it.");
				$("#filename_"+val[1]).val("");
				$(this).val("");
				return;
			}
			$("#filename_"+val[1]).val(nomfile);
			//prendo il valore attuale dell'input con il nome proposto
			var nuovonome=$("#newname_"+val[1]).val();
			if (nuovonome==""){
				alert("Please insert new file name in line "+String(parseInt(val[1])+1));
				return;
			}
					
			//salvo nel dizionario che ho usato questo nome
			if (nuovonome in dizduplicati){
				var contatore=dizduplicati[nuovonome];			
			}
			else{
				var contatore=1;
				dizduplicati[nuovonome]=1;
			}
			dizduplicati[nuovonome]+=1;
			nuovonome+="_"+String(contatore);
			//aggiungo all'inizio il nome del file inserito
			$("#newname_"+val[1]).val(nomfile+": "+nuovonome);
			//simulo il click sul tasto nascosto Add per inserire il file nella lista di quelli confermati		
			$("#add_btn_"+val[1]).click();
			//devo creare un nuovo nome per il file
			aggiorna_nome_file(val[1])
			
			var name=$("#idfile_"+val[1]).attr("name");
			var namesplit=name.split("_");
			var cont=parseInt(namesplit[1])+1;
			//scrivo il nuovo campo file
			$("#idfile_"+val[1]).after("<input id='idfile_"+val[1]+"' class='file_none' type='file' name='"+namesplit[0]+"_"+String(cont)+"' style='display:none;' />");
			//cambio l'id al vecchio file input e lo chiamo come il name		
			$("#idfile_"+val[1]).attr("id",name);
			dizfilename[nomfile]={"newname":nuovonome,"input":name};
			if (namesplit[0] in dizgenfile){
				var listafile=dizgenfile[namesplit[0]];
				listafile.push(nomfile);
			}
			else{
				var listafile=[nomfile];
			}
			dizgenfile[namesplit[0]]=listafile;
		}
	});
	
	//per cancellare con il CLEAR
	$("span.listdel").live("click", function () {
		//prendo il genid dell'LS
		var genid=$(this).parents(".interna").find(".lis_gen").text().trim();
		if(genid in dizgenfile){
			var listafile=dizgenfile[genid];
			for (var ii=0;ii<listafile.length;ii++){
				var input=dizfilename[listafile[ii]]["input"];
				//devo cancellare quell'input
				$("#"+input).remove();
				delete dizfilename[listafile[ii]];
			}
			delete dizgenfile[genid];
		}
	});
	
	//per cancellare con la singola x
	$("span.boxlistdel").live("click", function () {		
		//nome che compare nell'etichetta del boxlist
		var nomelabel=$(this).parent().text();
		//prima dei due punti ho il nome originale del file
		var nomesplit=nomelabel.split(":");
		var input=dizfilename[nomesplit[0]]["input"];
		//devo cancellare quell'input
		$("#"+input).remove();
		delete dizfilename[nomesplit[0]];
		//devo cancellare dall'altro dizionario il file che ho tolto adesso
		var genid=input.split("_")[0]
		//e' una lista con i nomi originali dei file caricati
		var listemp=dizgenfile[genid];
		if (listemp.length==1){
			delete dizgenfile[genid];
		}
		else{
			for (var kk=0;kk<listemp.length;kk++){
				if (listemp[kk] == nomesplit[0]){
		        	listemp.splice(kk,1);
		        }
			}
		}
	});
	
	//per i checkbox del no file
	$(".checknofile").live("click", function () {
		disabilita_inserimento(this);
	});
	
	$("#add_slide").click(function(event){
		event.preventDefault();
		aggiungi_campione();
	});
	$("#id_valid_barc").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_campione();
		}
	});
	
	$("#conf_all").click(function(event){
		event.preventDefault();
		var lischeck=$(".checknofile:checked");
		var lisfile=$(".file_none");
		var trovato=false;
		for (var i=0;i<lisfile.length;i++){
			var valore=$(lisfile[i]).val();
			if (valore!=""){
				trovato=true;
				break;
			}
		}
		if(!(trovato)&&(lischeck.length==0)){
			alert("Please insert some files");
			return;
		}
		//metto nel campo nascosto il valore della lunghezza della tabella
		$("#lung_tabella").val(String(lunghezza));
		
		post_server();
	});
});
