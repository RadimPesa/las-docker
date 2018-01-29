aliquote_inserite=new Array();
valori_campioni=[];

function inizializza(){
	var tab=$("#riass").dataTable();
	var righe=tab.$("tr");

	if(righe.length>0){
		$("#prossimo").attr("disabled",false);
	}
	var nascondi=true;
	for(var i=0;i<righe.length;i++){
		var gen=$(righe[i]).children(":nth-child(2)").text();
		var barc=$(righe[i]).children(":nth-child(3)").text();
		var pos=$(righe[i]).children(":nth-child(4)").text();
		var concattuale=$(righe[i]).children(":nth-child(5)").text();
		var volattuale=$(righe[i]).children(":nth-child(6)").text();
		var replicati=$(righe[i]).children(":nth-child(7)").children("input").val();
		if(pos!=""){
			nascondi=false;
		}
		var stringa=gen+"|"+barc+"|"+pos+"|"+concattuale+"|"+volattuale+"|"+replicati;
		valori_campioni.push(stringa);
		aliquote_inserite.push(gen);
	}
	if(nascondi){
		tab.fnSetColumnVis( 3, false );
	}
}

function cancella(riga){
	
	var tab=$("#riass").dataTable();
	var righe=tab.$("tr");
    var genealogy=$(righe[(riga.rowIndex)-1]).children(":nth-child(2)").text();
    //cancello il campione dalla lista finale prendendo il suo indice all'interno della lista
    var indice=$.inArray(genealogy,aliquote_inserite);
    if(indice!=-1){
    	aliquote_inserite.splice(indice,1);
    }
    //cancello il campione anche dalla lista con tutti i dati
    for (var j=0;j<valori_campioni.length;j++){
    	var valore=valori_campioni[j];
    	var val=valore.split("|");
    	//il gen e' il primo valore
    	var gen=val[0];
    	if(gen==genealogy){
    		valori_campioni.splice(j,1);
    		break;
    	}
    }
    //cancello la riga dal data table
    var indice=tab.fnGetPosition(riga);
    tab.fnDeleteRow(indice);
    
    if (!vuota()){
    	var lista=tab.$("tr").children(":first-child");
    	for (var j=0;j<lista.length;j++){
    		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
    		tab.fnUpdate(j+1,j,0);
    	}
    }
}

function inserisci(){
	//genealogy ID o barcode dell'aliquota inserita
	var gen=$("#id_aliquot").attr("value");
	//esperimento scelto
	var esp=$("#id_experiment option:selected").attr("value");
	
	if(gen==""){
		alert("Insert a valid genealogy ID or barcode");
	}
	else{
		$.ajaxSetup({
            beforeSend: function (request){
                request.setRequestHeader("workingGroups", WG);
            }
        });
		var codice=gen.replace(/#/g,"%23");
		url=base_url+"/api/genidbarc/"+codice+"/"+esp;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if(d.data=="inesistente"){
					alert("Aliquot doesn't exist in storage");
				}
				else if(d.data=="esperimento"){
					alert("Experiment chosen can't support this aliquot type");
				}
				else if(d.data=="presente"){
					alert("Aliquot is already scheduled for this procedure. Please first confirm past action.");
				}
				else{
					//prendo la lista di dizionari
					var lisgen=JSON.parse(d.data);
					for(var i=0;i<lisgen.length;i++){
						var diz=lisgen[i];
						
						var tab = $("#riass").dataTable();
						var val=diz.val.split("|");					
						//se la conc o il volume non sono definiti, allora blocco la 
					    //possibilita' di agire sulla schermata
					    if (val[3]=="None"){
					    	alert("Aliquot concentration is not defined. Please first revalue this aliquot");
					    	break;
					    }
					    else if (val[4]=="None"){
					    	alert("Aliquot volume is not defined. Please first revalue this aliquot");
					    	break;
					    }
					    else{
					    	$("#riass_wrapper,#inizio").css("display","");
							var trovato=0;
							var gen=val[0];
							var barc=val[1];
							var pos=val[2];
							var concattuale=val[3];
							var volattuale=val[4];

							//funzione che restituisce la posizione di un valore in una lista. Se il valore non c'è, allora restituisce -1
							var indice=$.inArray(gen,aliquote_inserite);
							if(indice==-1){
								aliquote_inserite.push(gen);
								var listavalori=diz.val;
								valori_campioni.push(listavalori);
								var indice=parseInt(aliquote_inserite.length);
								var replicati="<input type='text' id='"+gen+"' value='1' size='2' maxlength='4' />"
								var riga=tab.fnAddData( [indice, gen, barc, pos, concattuale,volattuale, replicati,null] );
								//eq mi da' l'n-esimo elemento di un insieme
								var cella=tab.$("tr").eq(riga).find("td").eq(-2);
								
								if(pos!=''){
									tab.fnSetColumnVis( 3, true );
								}
							}
							
							$("#id_aliquot").val("");
							$("#id_aliquot").focus();
							$("#prossimo").attr("disabled",false);
					    }						
					}
				}
			}
		});
	}
}

//serve a capire se la tabella con le aliq pianificate e' vuota
//o meno
function vuota(){
	var listarighe=$("#riass tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#riass tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
	else{
		return true;
	}
}

function cancella_utenti(){
	var idattuale=$("#actual_username").attr("cod");
	var lista=$("#id_utente option");
	for (var i=0;i<lista.length;i++){
		var idutente=$(lista[i]).val();
		if(idutente!=idattuale){
			$(lista[i]).remove();
		}
	}
}

//per aggiungere il valore dei replicati tecnici alla struttura dati generale
function aggiungi_replicati(){
	var tab=$("#riass").dataTable();
	var regex=/^[0-9]+$/;
	for (var i=0;i<valori_campioni.length;i++){
		var val=valori_campioni[i].split("|");
		var gen=val[0];
		//prendo l'input che ha come id il gen e leggo il valore
		var num=$("#"+gen).val();
		if(!regex.test(num)){
			return false;
		}
		else{
			valori_campioni[i]=val[0]+"|"+val[1]+"|"+val[2]+"|"+val[3]+"|"+val[4]+"|"+num;
		}
	}
	return true;
}

$(document).ready(function () {
	//per il demo. Serve a cancellare tutti gli utenti diversi da quello attuale
	//cancella_utenti();
	
	$("#id_date").attr("size",10);
	$("#id_date").datepicker({
		 //changeMonth: true,
		 //changeYear: true,
		 dateFormat: 'yy-mm-dd'
	});
	
	$('#id_date').datepicker('setDate', 'today');
	
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
	
	var tab=$("#riass").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
		"aoColumnDefs": [
  	        { "bSortable": false, "aTargets": [ 6 ] },
  	        //{ "sDefaultContent": "<input type='text' value='1' size='2' maxlength='4' />" , "aTargets": [ 6 ]},
  	      { "bSortable": false, "aTargets": [ 7 ] },
	        { "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='13px' height='13px' onclick='cancella(this.parentNode.parentNode)' style='cursor:pointer;' >" , "aTargets": [ 7 ]},
  	    ],});
	
	if(vuota()){
		$("#riass_wrapper").css("display","none");
	}
	
	//creo la finestra di popup	
	$("#file").popupWindow({
		height:500, 
		width:800, 
		top:50, 
		left:50,
		scrollbars:1,
		resizable:1,
		menubar:1
		});
	
	$("#id_notes").attr("size","30");
        $("#id_notes").keypress(validateFreeInput);
	$("#id_volu").val("");
	
	inizializza();
	
 //per l'autocompletamento
        //$("#id_aliquot").autocomplete({
        //      source:base_url+'/ajax/derived/autocomplete/'
        //});
        $("#id_aliquot").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: base_url+'/ajax/derived/autocomplete/',
                dataType: "json",
                data: {
                    term: request.term,
                    WG:WG
                },
                success: function(data) {
                    response(data);
                }
            });
        },
    });
	$("#id_aliquot").focus();
	$("#id_aliquot").val("");
	
	$("#id_aliquot").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			inserisci();
		}
	});
	
	$("#conferma1").click(inserisci);
	
	//verifico se il form e' valido, quindi sono al secondo passo ed ho gia' scelto 
	//l'esperimento
	var valid=$("#formvalido").val();
	if (valid=="True"){
		$("#inizio2").css("display","");
		var data=$("#id_dat").val();
		$("#id_date").val(data);
		var esp=$("#id_esperim").val();
		$("#id_experiment option[value="+esp+"]").attr("selected","selected");
		var utent=$("#id_ute").val();
		$("#id_utente option[value="+utent+"]").attr("selected","selected");
		var note=$("#id_note").val();
		note=note.replace(/%20/gi," ");
		$("#id_notes").val(note);
		$("#id_date,#id_experiment,#id_utente,#id_notes").attr("disabled",true);
		$("#conf").remove();
	}
	
	$("#aggiungi_file").click(function(event){
		event.preventDefault();
		var file=$("#id_file").attr("value");
		if(file==""){
			alert("Please load a file");
		}
		else{
			if(aggiungi_replicati()){
				//comunico la struttura dati al server
		    	var data = {
		    			salva:true,
		    			dati:JSON.stringify(valori_campioni),
		    			dat:$("#id_date").val(),
		    			exp:$("#id_experiment option:selected").attr("value"),
		    			operat:$("#id_utente option:selected").attr("value"),
		    			note:$("#id_notes").val(),
		    			workg:$("#idWG").val(),
			    };
		    	
		    	var url=base_url+"/decrease/micro";
				$.post(url, data, function (result) {
			    	if (result == "failure") {
			    		alert("Error");
			    	}
			    	else{
			    		$("#form_fin").append("<input type='hidden' name='aggiungi_file' />");
			    	
			    		$("#form_fin").submit();
			    	}
			    });
			}
			else{
				alert("You can only insert number. Please correct technical replicates");
			}
		}
	});
	
	$("#prossimo").click(function(event){
		event.preventDefault();
		if(vuota()){
			alert("Please insert some aliquots");
		}
		else{
			if(aggiungi_replicati()){
		    	//comunico la struttura dati al server
		    	var data = {
		    			salva:true,
		    			dati:JSON.stringify(valori_campioni),
		    			dat:$("#id_date").val(),
		    			exp:$("#id_experiment option:selected").attr("value"),
		    			operat:$("#id_utente option:selected").attr("value"),
		    			note:$("#id_notes").val(),
			    };
	
	    		var url=base_url+"/decrease/micro";
				$.post(url, data, function (result) {
			    	if (result == "failure") {
			    		alert("Error");
			    	}
			    	else{
				    	$("#form_fin").append("<input type='hidden' name='prosegui' />");
			    		$("#form_fin").submit();
			    	}
			    });
			}
			else{
				alert("You can only insert number. Please correct technical replicates");
			}
		}
	});
	
	$("#conf").click(function(event){
		if($("#id_experiment option:selected").text()=="---------"){
			alert("You have to select an experiment");
			return false;
		}
		if($("#id_utente option:selected").text()==" "){
			alert("You have to assign to someone");
			return false;
		}
	});
	
});
