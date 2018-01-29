vett_used_barc=new Array();
var collezione = {};
var listacasi=new Array();
var contaaliq=1;
var regex=/^[0-9.]+$/;
var dizposti={};
var motricolor=false;
var dizcontrolli={};

function controllacampi(place,dd,paz,barc,vol,note,indice){
	
	if(place=="---------"){
		alert("Please select place");
		return false;
	}
	
	//controllo la data
	if (dd==""){
		var errore="Please insert date";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	else{
		//verifico la validità della data		
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			var errore="Incorrect data format"
			if (indice!=""){
				errore+=" in line "+indice;
			}
			errore+=": it should be YYYY-MM-DD";
			alert(errore);
			return false;
		}
	}
	
	//controllo il paziente
	if (paz==""){
		var errore="Please insert patient code";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	
	//e' il barcode della provetta
	if(barc==""){
		var errore="Please insert tube barcode";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	else{
		//se c'e' uno spazio nella stringa
		if(barc.indexOf(" ") !== -1){
			var errore="There is a space in barcode. Please correct";
			if (indice!=""){
				errore+=" line "+indice;
			}
			alert(errore);
			return false;
		}
	}
		
	//controllo il volume
	if(vol==""){
		var errore="Please insert volume";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	if((!regex.test(vol))){
		var errore="You can only insert number. Please correct value for volume";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	
    var sorgid=dizposti[place.toLowerCase()];
    if(note!=""){
	    var chiave=paz+"|"+dd+"|"+sorgid;
	    //scandisco i dati che ho gia' per vedere se le note sono coerenti con quella inserita eventualmente adesso
	    if (chiave in dizcontrolli){
	    	var listacampioni=dizcontrolli[chiave];
	    	for (var i=0;i<listacampioni.length;i++){
	    		var notetemp=listacampioni[i]["note"];
	    		if ((notetemp!="")&&(notetemp!=note)){
	    			var errore="Notes are not consistent with those inserted before for this collection. Please correct";
	    			if (indice!=""){
	    				errore+=" line "+indice;
	    			}
	    			alert(errore);
	    			return false;
	    		}
	    	}
	    }
	    else{
	    	listacampioni=[];
	    }
	    var diz={};
    	diz["note"]=note;
    	listacampioni.push(diz);
    	dizcontrolli[chiave]=listacampioni;
    }	
	return true;
}

function save() {
	var place=$("#id_Place option:selected").text();
	var dd=$("#id_date").attr("value").trim();
	var paz=$("#id_patient").attr("value").trim();
	var barc=$("#id_barcode").attr("value").trim();
	var vol=$("#id_volume").attr("value").trim();
	var note="";
	if(motricolor){
		var note=$("#id_notes").attr("value").trim();
	}
	if(controllacampi(place,dd,paz,barc,vol,note,"")){
		controlla_barc(barc,false,{});
	}
}

function controlla_barc(barc,file,dati){
	//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
	if (cerca_barc_duplicati(barc)==false){
		var lbarc="";
		var codice=barc.replace(/#/g,"%23");
		var url=base_url+"/api/check/barcode/";
		var dati = {
				lbarc:codice
	    };
		
		$.post(url, dati, function (result) {
			if (result.data!="ok"){
				alert("Error: barcode you entered already exists");				
			}
			else{
				addAliquot( barc,file,dati);
			}
		});
	}
	else{
		alert("Error: barcode you entered has already been used in this session");
		return false;
	}
	return true;
}

function cerca_barc_duplicati(barc){
	var trovato=0;
	for (var i=0;i<vett_used_barc.length;i++){
		if (vett_used_barc[i]==barc){
			return true;
		}
	}
	return false;
}

//per inserire i campioni
function addAliquot( barcodeT,file,diz){
    vett_used_barc.push(barcodeT);
    if(file){
    	var sorg=diz.place.trim();
    	if((sorg[0]=="\"")&&(sorg[sorg.length-1])=="\""){
    		//vuol dire che il valore e' racchiuso tra virgolette
    		sorg=sorg.substring(1,sorg.length-1);			        		
    	}
    	var dat=diz.date.trim();
    	if((dat[0]=="\"")&&(dat[dat.length-1])=="\""){
    		dat=dat.substring(1,dat.length-1);			        		
    	}
    	var paz=diz.patient.trim();
    	if((paz[0]=="\"")&&(paz[paz.length-1])=="\""){
    		paz=paz.substring(1,paz.length-1);			        		
    	}
    	var vol=diz.vol.trim();
    	if((vol[0]=="\"")&&(vol[vol.length-1])=="\""){
    		vol=vol.substring(1,vol.length-1);			        		
    	}
    	var note=diz.note.trim();
    	if((note[0]=="\"")&&(note[note.length-1])=="\""){
    		note=note.substring(1,note.length-1);			        		
    	}
    }
    else{
	    var sorg=$("#id_Place option:selected").text();
	    var dat=$("#id_date").attr("value");
	    var paz=$("#id_patient").attr("value");
	    var vol=$("#id_volume").attr("value");
	    var note=$("#id_notes").attr("value");
    }
    
    if(file){
    	var sorgid=dizposti[sorg.toLowerCase()];
    }
    else{
    	var sorgid=$("#id_Place option:selected").attr("value");
    }
    
    if (motricolor){
    	$("#aliquots_table").dataTable().fnAddData( [contaaliq, sorg, dat, paz,barcodeT,vol,note,null] );
    }
    else{
    	$("#aliquots_table").dataTable().fnAddData( [contaaliq, sorg, dat, paz,barcodeT,vol,null] );
    }
    //salvo nella struttura dati locale
    saveInLocal(sorgid, dat, paz, barcodeT, vol,note);
    contaaliq++;
}

function saveInLocal(sorgid, dat, paz, barcodeT, vol,note){
	//in questo modo per ogni chiave devo creare un nuovo genid
    var chiave=paz+"|"+dat+"|"+sorgid;
	if (!(chiave in collezione)){
    	var lista=[];
    	//lista che al momento del salvataggio sul server serve a mantenere
    	//l'ordine di inserimento dei casi
    	listacasi.push(chiave);
    }
    else{
    	var lista=collezione[chiave];
    }
    var diz={};
	diz['barcode']=barcodeT;
	diz['vol']=vol;
	diz['note']=note;
	lista.push(diz);
	collezione[chiave]=lista;
	$("#id_barcode").val("");
}


/**** CANCELLAZIONE ALIQUOTE INSERITE ****/

function deleteAliquot(barc){
	for (key in collezione){
		for (var i = 0; i < collezione[key].length; i++){
			if (collezione[key][i]['barcode'] == barc){
				//ho trovato l'oggetto della lista con quel barc
				removeNotPlateBarcode(barc);
				if (collezione[key].length == 1){                       	
                	delete collezione[key];
                	//tolgo il caso dalla lista
                	removeCase(key);
                	//tolgo anche il caso (se c'e') dal dizionario usato per le note
                	if(key in dizcontrolli){
                		delete dizcontrolli[key];
                	}
                	break;
                }
				else{
                	collezione[key].splice(i,1); 
                }
			}
		}
	} 
}

function removeCase(key){
    for (var i=0; i < listacasi.length; i++){
        if (listacasi[i] == key){
        	listacasi.splice(i,1);
        }
    }
}

function removeNotPlateBarcode(barcode){
    for (var i=0; i < vett_used_barc.length; i++){
        if (vett_used_barc[i] == barcode){
        	vett_used_barc.splice(i,1);
        }
    }
}

//serve a capire se la tabella sotto, con le aliq, e' vuota
//o meno
function vuota(){
	var listarighe=$("#aliquots_table tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#aliquots_table tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
}

function loadElements(){
	var file=$("#id_file_cont").attr("value");
	if(file==""){
		alert("Please load a file");
	}
	else{
		var val=file.split(".");
		var estens=val[val.length-1];
		if ((estens=="xls")||(estens=="xlsx")){
			alert("Please change Excel file in a tab delimited one");
		}
		else{
			//chiave il paziente|data|sorgente e valore il valore delle note
			dizcontrolli={};
		    var formData = new FormData($('#upload_elem_file')[0]);
			$.ajax({
			    url: base_url + "/api/read/file/",
			    type: 'POST',
			    //Ajax events
			    success: function(d) {
			    	if (d.hasOwnProperty('response')){
		                alert(d['response']);
		                return;
		            }
			    	var lista=d.elements;
			    	var stringbarc="";
			        for(var i=0;i<lista.length;i++){
			        	//devo fare un controllo sui campi. Se ci sono tutti e se sono formattati correttamente
			        	var place=lista[i].place.trim();
			        	if((place[0]=="\"")&&(place[place.length-1])=="\""){
			        		//vuol dire che il valore e' racchiuso tra virgolette
			        		place=place.substring(1,place.length-1);			        		
			        	}
			        	var dd=lista[i].date.trim();
			        	if((dd[0]=="\"")&&(dd[dd.length-1])=="\""){
			        		dd=dd.substring(1,dd.length-1);			        		
			        	}
			        	var paz=lista[i].patient.trim();
			        	if((paz[0]=="\"")&&(paz[paz.length-1])=="\""){
			        		paz=paz.substring(1,paz.length-1);			        		
			        	}
			        	var barc=lista[i].barc.trim();
			        	if((barc[0]=="\"")&&(barc[barc.length-1])=="\""){
			        		barc=barc.substring(1,barc.length-1);			        		
			        	}
			        	var vol=lista[i].vol.trim();
			        	if((vol[0]=="\"")&&(vol[vol.length-1])=="\""){
			        		vol=vol.substring(1,vol.length-1);			        		
			        	}
			        	var note=lista[i].note.trim();
			        	if((note[0]=="\"")&&(note[note.length-1])=="\""){
			        		note=note.substring(1,note.length-1);			        		
			        	}
			        	if(!controllacampi(place,dd,paz,barc,vol,note,String(i+1))){
			        		return;
			        	}
			        	//devo controllare il posto perchè qui e' scritto a mano mentre il controllo
			        	//normale avviene sul select
			        	if (!(place.toLowerCase() in dizposti)){
			        		alert("Place you inserted does not exist. Please correct line "+String(i+1));
			        		return;
			        	}
			        	stringbarc+=barc+"&";
			        }
			        //per togliere l'ultimo &
					var stringdef=stringbarc.substring(0,(stringbarc.length)-1);
					
					var url=base_url+"/api/check/barcode/";
					var dati = {
							lbarc:stringdef
				    };
					
					$.post(url, dati, function (result) {
						if (result.data!="ok"){
							alert(result.data);				
						}
						else{
							//devo verificare che nel file non ci siano due barc uguali
							var listemp=[];
							for(var i=0;i<lista.length;i++){
								var barc=lista[i].barc;
								//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
								if (cerca_barc_duplicati(barc)==false){							
									for (var j=0;j<listemp.length;j++){
										if (listemp[j]==barc){
											var errore="Error: barcode you entered in line "+String(i+1)+" has already been used in this session";
											alert(errore);
											return;
										}
									}
									listemp.push(barc);
								}
								else{		
									alert("Error: barcode you entered in line "+String(i+1)+" has already been used in this session");
									return;
								}
							}
							for(var i=0;i<lista.length;i++){
					        	var barc=lista[i].barc.trim();
					        	if((barc[0]=="\"")&&(barc[barc.length-1])=="\""){
					        		//vuol dire che il valore e' racchiuso tra virgolette
					        		barc=barc.substring(1,barc.length-1);			        		
					        	}
					        	addAliquot(barc,true,lista[i]);
							}					
						}
					});		    
			    },
			
			    error: function(msg) {
			        alert(msg['response']);
			    },
			
			    // Form data
			    data: formData,
			    //Options to tell jQuery not to process data or worry about content-type.
			    cache: false,
			    contentType: false,
			    processData: false
			});
		}
	}
}

$(document).ready(function () {
	
	var tipo_prog=$("#tipo_prog").val();	
	if((tipo_prog!=undefined)&&(tipo_prog=="Motricolor")){
		motricolor=true;
		//aggiungo al titolo della schermata il nome del sottoprogetto di Motricolor (se c'e')
		var pr_esteso=$("#pr_esteso").val();
		if (pr_esteso!=""){
			var titolo=$("#homeproj").text();
			$("#homeproj").text(titolo+" "+pr_esteso);
			$("#id_notes").attr("size","30");
		}
	}
	
	var lplace=$("#id_Place option");
	for (var i=1;i<lplace.length;i++){
		dizposti[$(lplace[i]).text().toLowerCase()]=$(lplace[i]).val();
	}
	
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
	
	var tabfin=$("#aliq");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Collection","aliq");
	}
	
	$("#crea_camp").click(save);
	
	$("#carica_file").click(loadElements);
	
	$("#id_barcode").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save();
		}
	});
	
	$("#id_date").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	$("#id_date").datepicker('setDate', new Date());
	
	if(motricolor){
		var oTable = $("#aliquots_table").dataTable( {
	        "bProcessing": true,
	         "aoColumns": [
	            
	            { "sTitle": "ID Operation" },
	            { "sTitle": "Place" },
	            { "sTitle": "Date" },
	            { "sTitle": "Patient code" },
	            { "sTitle": "Barcode" },
	            { "sTitle": "Volume(ml)" },
	            { "sTitle": "Notes" },
	            { 
	                "sTitle": null, 
	                "sClass": "control_center", 
	                "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
	            },
	        ],
		    "bAutoWidth": false ,
		    "aaSorting": [[0, 'desc']],
		    "aoColumnDefs": [
		        { "bSortable": false, "aTargets": [ 7 ] },
		    ],
		    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	    });
	}
	else{
		var oTable = $("#aliquots_table").dataTable( {
	        "bProcessing": true,
	         "aoColumns": [
	            
	            { "sTitle": "ID Operation" },
	            { "sTitle": "Place" },
	            { "sTitle": "Date" },
	            { "sTitle": "Patient code" },
	            { "sTitle": "Barcode" },
	            { "sTitle": "Volume(ml)" },
	            { 
	                "sTitle": null, 
	                "sClass": "control_center", 
	                "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
	            },
	        ],
		    "bAutoWidth": false ,
		    "aaSorting": [[0, 'desc']],
		    "aoColumnDefs": [
		        { "bSortable": false, "aTargets": [ 6 ] },
		    ],
		    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	    });
	}
		
	/* Add event listener for deleting row  */
    $("#aliquots_table tbody td.control_center img").live("click", function () {
        var barc= $($($(this).parents('tr')[0]).children()[4]).text();
        deleteAliquot(barc);
        var nTr = $(this).parents('tr')[0];
        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
    } );
	/*$(document).on("click","#aliquots_table tbody td.control_center img", function () {
        var genID = $($($(this).parents('tr')[0]).children()[4]).text();
        var operaz = $($($(this).parents('tr')[0]).children()[1]).text();
        deleteAliquot(genID,operaz);
        var nTr = $(this).parents('tr')[0];
        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
    } );*/
    
    //quando clicco sul pulsante submit
    $("#confirm_all").click(function(event){
    	event.preventDefault();
    	if(!vuota()){
    		var timer = setTimeout(function(){$("body").addClass("loading");},500);
	    	$(this).attr("disabled",true);
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(collezione),
	    			liscasi:JSON.stringify(listacasi),
		    		operatore:$("#actual_username").val(),
		    };
	    	var tipo_prog=$("#tipo_prog").val();
	    	if(motricolor){
	    		var url=base_url+"/motricolor/collection/save/";
	    		data["progetto"]=$("#pr_abbr").val();
	    	}
	    	else{
	    		var url=base_url+"/symphogen/collection/save/";
	    	}
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	$("#form_fin").append("<input type='hidden' name='final' />");
		    	$("#form_fin").submit();
		    });
    	}
    	else{
    		alert("Please insert some samples");
    	}
	});

	//riduco le dimensioni del campo per il coll event e per il cod paziente
	$("#id_barcode,#id_patient").attr("size",10);
	//riduco le dimensioni dei campi
	$("#id_date").attr("size",8);
	$("#id_volume").attr("size",4);
	
});

