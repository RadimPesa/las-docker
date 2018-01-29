aliquote_inserite=new Array();
valori_campioni=[];

function inizializza(){
	var tab=$("#riass").dataTable();
	var righe=tab.$("tr");

	if(righe.length>0){
		$("#c_all,#prossimo").attr("disabled",false);
	}
	var nascondi=true;
	for(var i=0;i<righe.length;i++){
		var gen=$(righe[i]).children(":nth-child(2)").text();
		var barc=$(righe[i]).children(":nth-child(3)").text();
		var pos=$(righe[i]).children(":nth-child(4)").text();
		var concattuale=$(righe[i]).children(":nth-child(5)").text();
		var volattuale=$(righe[i]).children(":nth-child(6)").text();
		var volpreso=$(righe[i]).children(":nth-child(7)").text();
		var quantpresa=$(righe[i]).children(":nth-child(8)").text();
		var volfin=$(righe[i]).children(":nth-child(9)").text();
		if(pos!=""){
			nascondi=false;
		}
		var stringa=gen+"|"+barc+"|"+pos+"|"+concattuale+"|"+volattuale+"|"+volpreso+"|"+quantpresa+"|"+volfin;
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

function inserisci(){
	//genealogy ID o barcode dell'aliquota inserita
	var gen=$("#id_aliquot").attr("value");
	//esperimento scelto
	var esp=$("#id_experiment option:selected").attr("value");
	//devo vedere se e' stato inserito il volume o la quantita' presa
	var volum=$("#id_volume").val();
	var quantit=$("#id_quant").val();
	var regex=/^[0-9.]+$/;
	
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
						var volu=volum;
						var quant=quantit;
						var diz=lisgen[i];
						
						//devo vedere se e' un derivato
						var deriv=diz.derivato;
						if (deriv==true){
							if ((volum=="")&&(quantit=="")){
								alert("Please insert volume or quantity taken");
								break;
							}
							else if ((volum!="")&&(quantit!="")){
								alert("You can insert either volume or quantity taken");
								break;
							}
							else if(((!regex.test(volum))&&(volum!=""))||((!regex.test(quantit))&&(quantit!=""))){
								alert("You can only insert number. Please correct");
								break;
							}
						}
						else{
							volu="";
							quant="";
						}
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
							
							if (volu!=""){
						    	vol_finale=parseFloat(volattuale)-parseFloat(volu);					    	
						    }
						    else if ((quant!="")&&(concattuale!="")){
						    	var vol_temp=parseFloat(quant)/parseFloat(concattuale/1000);
						    	vol_finale=parseFloat(volattuale)-vol_temp;
						    }
						    else if ((quant!="")&&(concattuale=="")){
						    	alert("Aliquot has not a concentration. Please insert volume taken");
						    	break;
						    }

						    if (deriv==true){
						    	vol_finale=String(vol_finale.toFixed(2));
						    }
						    else{
						    	vol_finale="";
						    }
						    var negativo=false;
							if(vol_finale<0){
								negativo=true;
							}
							
							//funzione che restituisce la posizione di un valore in una lista. Se il valore non c'è, allora restituisce -1
							var indice=$.inArray(gen,aliquote_inserite);
							if(indice==-1){
								aliquote_inserite.push(gen);
								var listavalori=diz.val+"|"+volu+"|"+quant+"|"+vol_finale;
								valori_campioni.push(listavalori);
								var indice=parseInt(aliquote_inserite.length);
								var riga=tab.fnAddData( [indice, gen, barc, pos, concattuale,volattuale,volu,quant,vol_finale,null] );
								//eq mi da' l'n-esimo elemento di un insieme
								var cella=tab.$("tr").eq(riga).find("td").eq(-2);
								
								if(pos!=''){
									tab.fnSetColumnVis( 3, true );
								}
							}
							else{
								//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
								tab.fnUpdate(volu,indice,6);
								tab.fnUpdate(quant,indice,7);
					    		tab.fnUpdate(vol_finale,indice,8);
					    		//eq mi da' l'n-esimo elemento di un insieme
								var cella=tab.$("tr").eq(indice).find("td").eq(-2);
								
							}
							if(negativo){
								$(cella).css("color","red");
								$(cella).css("font-weight","bold");
							}
							else{
								$(cella).css("color","black");
								$(cella).css("font-weight","normal");
							}
							
							$("#id_aliquot").val("");
							$("#id_aliquot").focus();
							//se l'esperimento e' beaming allora blocco la possibilita' di terminare qui la procedura
							var esperim=$("#id_experiment option:selected").text();
							if((esperim=="Beaming")||(esperim=="RealTimePCR")||(esperim=="SangerSequencing")||(esperim=="DigitalPCR")||(esperim=="Sequenom")||(esperim=="CellLineGeneration")||(esperim=="CellLineThawing")||(esperim=="NextGenerationSequencing")){
								$("#prossimo").attr("disabled",false);
							}
							else{
								$("#c_all,#prossimo").attr("disabled",false);
							}							
					    }						
					}
				}
			}
		});
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
  	        { "bSortable": false, "aTargets": [ 9 ] },
  	        { "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='13px' height='13px' onclick='cancella(this.parentNode.parentNode)' style='cursor:pointer;' >" , "aTargets": [ 9 ]},
  	    ],});
	
	if(vuota()){
		$("#riass_wrapper").css("display","none");
	}
	else{
		//guardo le celle con il volume finale e metto in rosso i numeri negativi
		var lisrighe=tab.$("tr");
		for (var i=0;i<lisrighe.length;i++){
			var cella=$(lisrighe[i]).find("td").eq(-2);
			var valore=parseFloat($(cella).text());
			if(valore<0){
				$(cella).css("color","red");
				$(cella).css("font-weight","bold");
			}
		}
	}
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){	
    	generate_result_table("Experiment","aliquote_fin");
	}
	else{
		inizializza();
	}
	
	$("#id_notes").attr("size","30");
        $("#id_notes").keypress(validateFreeInput);
	$("#id_volu").val("");
	
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
	
	$("#aggiungi_file").click(function(event){
		event.preventDefault();
		var file=$("#id_file").attr("value");
		if(file==""){
			alert("Please load a file");
		}
		else{
			var val=file.split(".");
			var estens=val[val.length-1];
			if (estens!="las"){
				alert("Please load a .las file (tab delimited)");
			}
			else{
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
		    	
		    	var url=base_url+"/decrease/";
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
		}
	});
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
		
		//se l'esperimento e' beaming o altri allora blocco la possibilita' di terminare qui la procedura
		var esperim=$("#id_experiment option:selected").text();
		if((esperim=="Beaming")||(esperim=="RealTimePCR")||(esperim=="SangerSequencing")||(esperim=="DigitalPCR")||(esperim=="Sequenom")||(esperim=="CellLineGeneration")||(esperim=="CellLineThawing")||(esperim=="NextGenerationSequencing")){
			$("#c_all").attr("disabled",true);
		}
	}
	
	$("#c_all,#prossimo").click(function(event){
		event.preventDefault();
		//per capire su quale tasto ho cliccato
		var id=$(this).attr("id");
		if(vuota()){
			alert("Please insert some aliquots");
		}
		else{
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(valori_campioni),
	    			dat:$("#id_date").val(),
	    			exp:$("#id_experiment option:selected").attr("value"),
	    			operat:$("#id_utente option:selected").attr("value"),
	    			note:$("#id_notes").val(),
		    };

    		var url=base_url+"/decrease/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	else{
		    		if (id=="c_all"){
			    		$("#form_fin").append("<input type='hidden' name='conf_tutto' />");
			    	}
			    	else{
			    		$("#form_fin").append("<input type='hidden' name='prosegui' />");
			    	}
		    	        
		    		$("#form_fin").submit();
		    	}
		    });
		}
	});
	
	$("#conf").click(function(event){
		if($("#id_experiment option:selected").text()=="---------"){
			alert("You have to select an experiment");
			return false;
		}
		/*if($("#id_utente option:selected").text()==" "){
			alert("You have to assign to someone");
			return false;
		}*/
		$('#idWG').val($('#id_utente option:selected').attr('id'));
	});

});

