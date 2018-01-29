//lista in cui salvare i gen delle aliquote delle pianificazioni da eliminare 
lista_canc=new Array();
var contatore=1;
//contatore per contare le righe inserite nella tabella sotto
var kkk=0;
var listaappoggio=new Array();
var listabarcgenerale=new Array();
var lgenletti=new Array();

function removeBarcode(barcode){
    for (var i=0; i < listabarcgenerale.length; i++){
        if (listabarcgenerale[i] == barcode){
        	listabarcgenerale.splice(i,1);
        }
    }
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

//serve a capire se la tabella sotto, con le aliq da rivalutare effettivamente, e' vuota
//o meno
function vuota(){
	var listarighe=$("#aliq_definitive tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#aliq_definitive tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
}


function aggiorna_dati(){
	//solo se nella tabella di sopra ho delle aliquote
	var listarighe=$("#aliq_definitive tr");
	var righesopra=$("#aliq_originali tr");
	if ((righesopra.length>1)||(listarighe.length>1)){
		var lbarc="";
		var lgen="";
		var lis_pezzi_url=[];
		var utente=$("#actual_username").val();
		var url=base_url+"/api/storage/tube/";
		var listagen=$("#aliq_originali tr").children(":nth-child(2)").not("th");
		//prendo i barcode della tabella di sopra
		//rispetto ai derivati il barcode e' nella colonna 8
		listabarc=$("#aliq_originali tr").children(":nth-child(8)").not("th");
		//prendo i campi relativi alla piastra della tabella di sopra
		//rispetto ai derivati la piastra e' nella colonna 6
		listapias=$("#aliq_originali tr").children(":nth-child(6)").not("th");
		//prendo i campi relativi alla posizione della provetta della tabella di sopra
		//rispetto ai derivati la posizione e' nella colonna 7
		listapos=$("#aliq_originali tr").children(":nth-child(7)").not("th");
		//prendo i campi relativi alla posizione della piastra della tabella di sopra
		listapospiastra=$("#aliq_originali tr").children(":nth-child(5)").not("th");
		//prendo i campi relativi al rack della tabella di sopra
		listarack=$("#aliq_originali tr").children(":nth-child(4)").not("th");
		//prendo i campi relativi alla posizione della tabella di sopra
		listafreezer=$("#aliq_originali tr").children(":nth-child(3)").not("th");
		//prendo i campi relativi alla disponibilita' della prima tabella
		listadisp=$("#aliq_originali tr").children(":nth-child(9)").not("th");
		
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
								
								if(val[0]!="None"){
									listabarcgenerale.push(val[0].toUpperCase());
								}
								//questo e' per le piastre con i pozzetti che non hanno le provette con barcode.
								//Carico quindi il valore della piastra stessa
								else{
									if($.inArray(val[2].toUpperCase(),listabarcgenerale)==-1){
										listabarcgenerale.push(val[2].toUpperCase());
									}
								}
								//solo se non e' gia' in lista lo inserisce
								if(($.inArray(val[0].toUpperCase(),listaappoggio)==-1)&&(val[0]!="None")){
									listaappoggio.push(val[0].toUpperCase());	
								}
								if(($.inArray(val[2].toUpperCase(),listaappoggio)==-1)&&(val[2]!="None")){
									listaappoggio.push(val[2].toUpperCase());
								}
								if(($.inArray(val[4].toUpperCase(),listaappoggio)==-1)&&(val[4]!="None")){
									listaappoggio.push(val[4].toUpperCase());
								}
								if(($.inArray(val[5].toUpperCase(),listaappoggio)==-1)&&(val[5]!="None")){
									listaappoggio.push(val[5].toUpperCase());
								}
								
								$(listabarc[i]).text(val[0]);
								$(listapos[i]).text(val[1]);
								$(listapias[i]).text(val[2]);
								$(listapospiastra[i]).text(val[3]);
								$(listarack[i]).text(val[4]);
								$(listafreezer[i]).text(val[5]);
								$(listadisp[i]).text(val[6]);
							}
						}
					}
					//lo faccio solo una volta alla fine del ciclo generale
					if (contatore==lis_pezzi_url.length){
						var oTable= $("#aliq_originali,#aliq_definitive").dataTable({
							"bPaginate": true,
							"bLengthChange": true,
							"bFilter": true,
							"bSort": true,
							"bInfo": true,
							"bAutoWidth": false, 
							"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
							
							'fnDrawCallback': function () {
					            jQuery('#aliq_originali td.notes,#aliq_definitive tr td:nth-child(12)').editable(
					                function(value, settings) {					                	
					                    return(value);
						            },
					            	{
						            	//numero massimo di caratteri accettabili nella td
						            	maxlength:150,
						            	//per fare in modo che quando l'input perde il focus viene salvato comunque quello che e' stato scritto
						            	onblur:'submit'
						            }
						            /*{
						            	"callback": function( sValue, y ) {
						                var aPos = oTable.fnGetPosition( this );
						                aliquot_warnings = 0;
						                //oTable.fnUpdate( sValue, aPos[0], aPos[2] ); 
							            },
							            //"height": "0.8em",
							            //"width": "4em"
						            }*/
					            )
					        }
						
						});
						//$("#aliq_originali_wrapper").css("float","left");
						//$("#aliq_originali_wrapper,#aliq_definitive_wrapper").css("width","85%");
						
						trova_figli_container();
						clearTimeout(timer);
						$("body").removeClass("loading");
					}
					
				}
				else{
					alert("Problems while interacting with storage");
				}
				contatore++;
			});
			//per evidenziare condizioni di errore
			//.error(function() { 
			//	alert("Problems while interacting with storage"); 
			//});
		}
	}
	else{
		$("#aliq_originali,#aliq_definitive").dataTable({
			"bPaginate": true,
			"bLengthChange": true,
			"bFilter": true,
			"bSort": true,
			"bInfo": true,
			"bAutoWidth": false, 
			"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]});
	}
}

function trova_figli_container(){
	var lbarc="";
	var url=base_url+"/api/transfer/listbarcode/";	
	for (var i=0;i<listabarcgenerale.length;i++){
		lbarc=lbarc+listabarcgenerale[i]+"&";
	}
	lbarc = lbarc.substring(0, lbarc.length - 1)
	var codice=lbarc.replace(/#/g,"%23");
	//var urlst=url+codice;
	var data = {
			lbarc:codice
    };
	$.post(url, data, function (result) {
		if (result.data!="errore"){
			var lista=result.data;
			for(var i=0;i<lista.length;i++){
				listabarcgenerale.push(lista[i].toUpperCase());
			}
			
		}
	});
}

//viene eseguita quando si clicca su un abort qualsiasi
function elimina_pianificazione(){
	var tab=$("#aliq_originali").dataTable();
	var righetab=tab.$(".check_canc:checked");
	//conto quante sono le aliquote selezionate nella colonna abort
	var listaabort=$(righetab);
	//se c'e' qualcosa di selezionato disabilito i tasti per confermare il barc
	if (listaabort.length!=0){
		$("#conf,#id_barcode,#conf_all,#insert_file,#cancel").attr("disabled",true);
		$("#canc_sel").attr("disabled",false);
	}
	else{
		$("#conf,#id_barcode,#conf_all,#insert_file,#cancel").attr("disabled",false);
		$("#canc_sel").attr("disabled",true);
	}
	var selez=$(this).is(':checked');
	var genid=$(this).attr("gen");
	if(selez){
		//chiave il gen e valore le note
		var diztemp={};
		var tdnote=$(this).parent().parent().children("td.notes");
		var note=$(tdnote).text();
		diztemp[genid]=note
		lista_canc.push(diztemp);
	}
	else{
		//se l'utente ha deselezionato il select, tolgo quest'ultimo dalla lista
		for (var i=0; i < lista_canc.length; i++){
	        if (lista_canc[i] == genid){
	        	lista_canc.splice(i,1);
	        }
		}
	}
}

function conf_barcode(){
	var barcorig=$("#id_barcode").attr("value");
	var barc=barcorig.toUpperCase();
	if ($.inArray(barc,listaappoggio)!=-1){
		
		if ($.inArray(barc,listabarcgenerale)!=-1){
			var tabella=$("#aliq_originali").dataTable();
			var tabellasotto=$("#aliq_definitive").dataTable();
			var aTrs = tabella.fnGetNodes();
			var oSettings = tabella.fnSettings();
			//mi da' il numero di colonne che ci sono nel data table
			var lunghezza = (oSettings.aoColumns.length-1);
			var contat=0;
			// scandisce tutte le righe della tabella
			var avviso=false;
	        jQuery.each(tabella.fnGetData(), function(key, d) {
	        	if ((d[7].toUpperCase() == barc)||(d[5].toUpperCase()== barc)||(d[3].toUpperCase()==barc)||(d[2].toUpperCase()==barc)){
	        		//mi da' la riga del data table
					var riga=aTrs[key];
	        		var dispon=d[8];
	        		if (dispon=="Yes"){
		        		var listadatitemp=new Array();
			        	
						//prendo i valori dal genid fino al barcode
						for (var k=1;k<9;k++){
							var figlio=":nth-child("+(k)+")";
							var dato=$(riga).children(figlio).html();
							listadatitemp.push(dato);
						}
						//prendo la concentrazione
						var dato=$(riga).children(":nth-child(10)").html();
						listadatitemp.push(dato);
						//volume preso
						var volu=$(riga).children(":nth-child(11)").text().trim();
						if (volu!=""){
							listadatitemp.push("<input id='takevol_"+String(kkk)+"' maxlength='7' type='text' value='"+volu+"' size=5 />");
						}
						else{
							listadatitemp.push(null);
						}
						//prendo il vol rimanente
						var dato=$(riga).children(":nth-child(12)").html();
						listadatitemp.push(dato);
						//prendo le note
						var note=$(riga).children("td.notes").html();
						listadatitemp.push(note);
						//campo per l'esaurito
						listadatitemp.push("<input id='exhausted_"+String(kkk)+"' type='checkbox' />");
						kkk++;
						
						var rowPos=tabellasotto.fnAddData(listadatitemp);
						
		                tabella.fnDeleteRow(riga);
		                contat++;

	                	//d[1] e' il genid della riga
	                	lgenletti.push(d[1]);
	        		}
	        		else{
	        			if(!avviso){
		        			alert("Container is not available. You can't select it.");
							$("#id_barcode").attr("value","");
							$("#id_barcode").focus();
							avviso=true;
	        			}
	        		}
	            }
	        });
			$("#id_barcode").attr("value","");
			$("#id_barcode").focus();
			//tolgo il codice dalla lista generale
			removeBarcode(barc);
			//aggiorno la scritta con il numero di provette confermate
			if (contat==1){
				$("#contatore").text("You validated "+String(contat)+" aliquot");
			}
			else{
				$("#contatore").text("You validated "+String(contat)+" aliquots");
			}
			
			//per rimettere a posto la numerazione della tabella sopra e sotto
			var lista=tabella.$("tr").children(":first-child");
	    	for (var j=0;j<lista.length;j++){
	    		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna), il false e' 
	    		//per fare in modo che la tabella non si riaggiorni scombinando così gli ordinamenti dell'utente
	    		tabella.fnUpdate(j+1,j,0,false,true);
	    	}
	    	var lista=tabellasotto.$("tr").children(":first-child");
	    	for (var j=0;j<lista.length;j++){
	    		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
	    		tabellasotto.fnUpdate(j+1,j,0,false,true);
	    	}
	    	tabellasotto.fnDraw();
			$("#inferio").css("display","inline");
		}
		else{
			alert("You did not schedule to execute experiment on all children's container. Please validate barcode singularly.");
			$("#id_barcode").attr("value","");
			$("#id_barcode").focus();
		}
	}
	else{
		alert("Invalid barcode");
		$("#id_barcode").attr("value","");
		$("#id_barcode").focus();
	}	
}

function selez_deselez_tutte(){
	var oTable= $("#aliq_definitive").dataTable();
	if ($(this).attr("sel")=="s"){
		$(this).val("Set all aliquots exhausted");
		oTable.$(":checkbox").removeAttr("checked");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all aliquots exhausted");
		oTable.$(":checkbox").attr("checked","checked");
		$(this).attr("sel","s");
	}
}

$(document).ready(function () {
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Experiment","aliquote_fin");
	}
	else{
		aggiorna_dati();
	}

	//do il focus al campo con il barcode della provetta
	$("#id_barcode").focus(); 
	
	$("#conf").click(conf_barcode);
	
	$("#id_barcode").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			conf_barcode();
		}
	});
	
	$(".check_canc").click(elimina_pianificazione);
	
	$("#seltutte").click(selez_deselez_tutte);
	
	//metto un controllo per capire se l'utente clicca per confermare tutto senza 
	//riempire la lista
	$("#conf_all,#insert_file").click(function(event){
		event.preventDefault();
		var idtasto=$(this).attr("id");
		//vuol dire che la lista delle aliquote sopra e' vuota
		if(vuota()){
			alert("You have to add some aliquots to the list");
		}
		else{
			var tabellasotto=$("#aliq_definitive").dataTable();
			var listaf=[];
			var regex=/^[0-9.]+$/;
			var aTrs = tabellasotto.fnGetNodes();
			var errore=false;
			//scandisco la tabella per memorizzare le informazioni: gen, vol preso e esaurito
			//lo faccio adesso perche' l'utente, finche' non clicca su conferma, puo' sempre modificare
			jQuery.each(tabellasotto.fnGetData(), function(key, d) {
				var diz={};
				var riga=aTrs[key];
				diz["gen"]=d[1].trim();
				var input=$(riga).children(":nth-child(10)").children();
				var volpreso=$(input).attr("value");
				if ((!regex.test(volpreso))&&(volpreso!=undefined)){
					alert("You can only insert number. Please correct value in line "+d[0]);
					errore=true;
				}
				if(volpreso==undefined){
					volpreso=-1;
				}
				diz["volpreso"]=volpreso;
				var note=$(riga).children(":nth-child(12)").text().trim();
				diz["note"]=note;
				var checkbox=$(riga).children(":nth-child(13)").children();
				if($(checkbox).is(":checked")){
					diz["esaurito"]=1;
				}
				else{
					diz["esaurito"]=0;
				}
				listaf.push(diz);
			});
			if(!errore){
				//comunico la struttura dati al server
		    	var data = {
		    			salva:true,
		    			lgen:JSON.stringify(listaf)
			    };
	
		    	var url=base_url+"/decrease/final";
				$.post(url, data, function (result) {
			    	if (result == "failure") {
			    		alert("Error");
			    	}
			    	else{
			        	if(idtasto=="conf_all"){
			        		$("#form_conf").append("<input type='hidden' name='conferma' />");
			        	}
			        	else{
			        		$("#form_conf").append("<input type='hidden' name='file' />");
			        	}
			    		$("#form_conf").submit();
			    	}
				});
			}
		}
	});
	
	//quando clicco sul pulsante per cancellare le pianificazioni
    $("#canc_sel").click(function(event){
    	event.preventDefault();
    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(lista_canc),
	    };
    	var url=base_url+"/decrease/canc";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	
	    	$("#form_fin").append("<input type='hidden' name='final' />");
	    	$("#form_fin").submit();
	    });
	});
	
});
