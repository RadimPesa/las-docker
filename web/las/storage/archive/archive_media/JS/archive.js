var mappa_aggiunti={};
mappa_tolti={};
drag=false;
lista_container_usati={};
cont_sorg="";
cont_dest="";
lisrapporti=[];
//tasto da selezionare nel caso della visualizzazione itself
tasto_sel_dest="";
tasto_sel_sorg="";
modo_sorg="";
modo_dest="";
tipospost="";
tipospost_dest="";
foglia_sorg="";
foglia_dest="";
pos_multiplo=false;
dati_server={};
//dizionario con chiave il tipo aliq e valore la lista dei cont ancora da posizionare di quel tipo
vettore_posiz={};
//dizionario con chiave il barcode e valore la riga del datatable cancellata perche' il cont e' stato posizionato
diz_righe_tolte={}
//per memorizzare il tipo di aliq che sto vedendo adesso nel data table
tipoaliqvisualiz="";
//per il tasto undo per fotografare la situazione delle mappe prima di eseguire uno spostamento
dizundo={};
//per avere il codice html della tabella temp
temptable="";

function inizio(){
	//chiamo la API che mi da' le relazioni riguardanti le gerarchie tra i cont type
	var url=base_url+"/api/info/relationship/";
	$.getJSON(url,function(d){
		lisrapporti=d;
	});
}

/*function batch_all(){
	if((cont_sorg!="")&&(cont_dest!="")){
		//devo controllare che il tipo della piastra caricata sia coerente con quello dell'altra
		//creo la lista sorgente e dest
		var aliquote=$("#operativa table div.drag");		
		var listasorg=[];
		var listadest=[];
		var k=2;
		for(var i=0;i<aliquote.length;i++){
			var al=$(aliquote[i]).attr("id");
			listasorg[k]=al;
			var col=$(aliquote[i]).attr("col");
			var row=$(aliquote[i]).attr("row");
			var lbuttondest=$("#freezer table button[col='"+col+"'][row='"+row+"'],#freezer table div[col='"+col+"'][row='"+row+"']");
			if (lbuttondest.length==0){
				alert("Unable to execute batch mode.");
				return;
			}
			listadest[k]=$(lbuttondest[0]).parent().attr("id");
			k++;
		}
		if((listasorg.length==0)||(listadest.length==0)){
			alert("Unable to execute batch mode.");
			return;
		}
		save_bottom(null, listasorg, listadest,true);
	}
	else{
		alert("First you have to load the containers");
	}
}*/

function batch_aliquot(){
	if((cont_sorg!="")&&(cont_dest!="")){
		//devo controllare che il tipo della piastra caricata sia coerente con quello dell'altra
		//creo la lista sorgente e dest
		var aliquote=$("#operativa table div.drag[c='pb_highlight']");
		if(aliquote.length!=0){
			var listasorg=[];
			var listadest=[];
			var k=2;
			for(var i=0;i<aliquote.length;i++){
				var al=$(aliquote[i]).attr("id");
				listasorg[k]=al;
				var col=$(aliquote[i]).attr("col");
				var row=$(aliquote[i]).attr("row");
				var lbuttondest=$("#freezer table button[col='"+col+"'][row='"+row+"'],#freezer table div[col='"+col+"'][row='"+row+"']");
				if (lbuttondest.length==0){
					alert("Unable to execute batch mode.");
					return;
				}
				listadest[k]=$(lbuttondest[0]).parent().attr("id");
				k++;
			}
			if((listasorg.length==0)||(listadest.length==0)){
				alert("Unable to execute batch mode.");
				return;
			}
			save_bottom(null, listasorg, listadest,true);
		}
		else{
			alert("Please click on 'Select' to highlight some containers");
		}
	}
	else{
		alert("First you have to load the containers");
	}
}

/*function batch_aliquot(){
	if((cont_sorg!="")&&(cont_dest!="")){
		//devo controllare che il tipo della piastra caricata sia coerente con quello dell'altra
		//creo la lista sorgente e dest
		var aliquote=$("#operativa table div.drag[c='pb_highlight']");
		if(aliquote.length!=0){
			var al=$(aliquote[i]).attr("id");
			listasorg[k]=al;
			var col=$(aliquote[i]).attr("col");
			var row=$(aliquote[i]).attr("row");
			var lbuttondest=$("#freezer table button[col='"+col+"'][row='"+row+"'],#freezer table div[col='"+col+"'][row='"+row+"']");
			if (lbuttondest.length==0){
				var frase="Unable to execute batch mode.";
				return [frase,listasorg,listadest];
			}
			listadest[k]=$(lbuttondest[0]).parent().attr("id");
			k++;
			
			if((listasorg.length==0)||(listadest.length==0)){
				alert("Unable to execute batch mode.");
				return;
			}
			save_bottom(null, listasorg, listadest,true);
		}
		else{
			alert("Please click on 'Select' to highlight some containers");
		}
	}
	else{
		alert("First you have to load the containers");
	}
}*/

function select_container(){
	//cancello tutte le cose fatte prima
	selected_phase = "-";
	flag = "-";
	bi = "-";
	bf = "-";
	$("#operativa table div.drag").attr("c","plateButtonOFF");
	var sel=$("#id_selez option:selected").val();
	var aliquote=$("#operativa table div.drag");
	for(var i=0;i<aliquote.length;i++){
		var pieno=$(aliquote[i]).attr("pieno");
		if(sel=="all"){
			$(aliquote[i]).attr("c","pb_highlight");
		}
		else if(sel=="full"){
			if(pieno=="True"){
				$(aliquote[i]).attr("c","pb_highlight");
			}
		}
		else if(sel=="empty"){
			if(pieno=="False"){
				$(aliquote[i]).attr("c","pb_highlight");
			}
		}
	}
}

function pos_automatico(){
	if(cont_dest!=""){
		//scandisco a partire dalla pos 0,0 il cont dest fino a trovare una pos libera
		var aliquote=$("#operativa table div.drag");		
		var listasorg=[];
		var listadest=[];
		var colcont=$("#freezer table").attr("col");
		var rowcont=$("#freezer table").attr("row");
		for(var i=0;i<aliquote.length;i++){
			var al=$(aliquote[i]).attr("id");
			listasorg[2]=al;
			var ris="";
			var col=0;
			var row=0;
			while (ris!="ok"){
				var lbuttondest=$("#freezer table button[col='"+String(col)+"'][row='"+String(row)+"'],#freezer table div[col='"+String(col)+"'][row='"+String(row)+"']");
				if (lbuttondest.length==0){
					continue;
				}
				listadest[2]=$(lbuttondest[0]).parent().attr("id");
				ris=save_bottom(null, listasorg, listadest,false);
				col++;
				if(col==colcont){
					row++;
					col=0;
				}
				//se sono arrivato alla fine del cont senza trovare uno spazio vuoto
				if(row==rowcont){
					break;
				}
			}
		}						
	}
}

function evidenzia(tabella,cont){
	//devo evidenziare il cont che prima era visualizzato per esteso e adesso risulta all'interno del padre
	var val="div";
	var foglia=foglia_sorg;
	if(tabella=="freezer"){
		val="button";
		foglia=foglia_dest;
	}
	var div=$("#"+tabella+" table "+val).filter(function(){
		if(foglia=="present"){
			var barc=$(this).attr("gen");
		}
		else{
			var barc=$(this).attr("barcode");
		}
		if(barc!=undefined){
			if(barc.toLowerCase()==cont.toLowerCase()){			 
				return this;
			}
			//puo' essere che il cont sia in un cassetto e che quindi il barc da evidenziare
			//contiene lui e altri oggetti separati da &
			var lbarc=barc.split("&");
			for(var i=0;i<lbarc.length;i++){
				if (lbarc[i].toLowerCase()==cont.toLowerCase()){
					return this;
				}
			}
			//puo' essere che debba togliere il |A1 finale per fare il confronto
			var btemp=barc.split("|");
			if(btemp[0].toLowerCase()==cont.toLowerCase()){			 
				return this;
			}
		}
	});
	if(tabella=="freezer"){
		foglia_dest="";
	}
	else{
		foglia_sorg="";
	}	
	return div;
}

function errore_piastra(tab){
	$("#"+tab+" table div,#"+tab+" table button").replaceWith("<button>0</button>");
	$("#"+tab+" table button").attr("disabled",true);
	$("#"+tab+" table button").css("background-color","rgb(249,248,242)");
	$("#"+tab+" table th").text("");
}

function carica_operativa_scelta(){
	var codice=$(this).text().trim();	
	var sel=$("#view_sorg").is(':checked');
	if (sel){
		var tipocaricamento="children";
	}
	else{
		var tipocaricamento="itself";
	}
	tipospost="simple";
	carica_piastra_operativa_effettiva(codice,tipocaricamento,false,true);
}

function carica_operativa(){
	if ($("#barcode_operative").val() == "")
		alert("Insert barcode in source container");
	else{
		var codice=$("#barcode_operative").val().trim();
		if(codice.indexOf("|")>-1){
			alert("Please note that barcodes with '|' are not supported");
		}		
		else{
			//devo vedere se e' stato scelto di caricare il container o i figli
			var sel=$("#view_sorg").is(':checked');
			if (sel){
				var tipocaricamento="children";
			}
			else{
				var tipocaricamento="itself";
			}			
			tipospost="simple";
			carica_piastra_operativa_effettiva(codice,tipocaricamento,false,true);
		}
	}
}

function carica_piastra_operativa_effettiva(codice,tipocaricamento,zoom,automatico){
	var codspl=codice.split("|");
	codice=codspl[0];
	//devo verificare di non vedere lo stesso cont a destra e a sinistra
	var barcodecont=$("#freezer table").attr("barcode");
	if((codice==cont_dest)||((barcodecont!=undefined)&&(codice==barcodecont))){
		alert("Error: you cannot have same container as source and destination");
		return;
	}
	modo_sorg=tipocaricamento;
	var chiave=codice+"|"+tipocaricamento;
	var cont_partenza=cont_sorg;
	if (chiave in lista_container_usati){
		d=lista_container_usati[chiave];
		var controllo=piastra_definitiva_operativa(d,codice,automatico);
		if(!controllo){
			errore_piastra("operativa");
			return;
		}
		//solo se ho cliccato su zoom -
		if(zoom){
			//devo evidenziare il cont che prima era visualizzato per esteso e adesso risulta all'interno del padre
			var div=evidenzia("operativa", cont_partenza);
			$(div).attr("c","pb_highlight");
			var bb=$(div).attr("barcode");
			if ((bb=="")||(bb==undefined)){
				tasto_sel_sorg=cont_partenza;
			}
			else{
				tasto_sel_sorg=bb;
			}
		}
	}
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		var codiceurl=codice.replace(/#/g,"%23");
		var url=base_url+"/api/table/"+codiceurl+"/"+tipocaricamento+"/"+tipospost+"/";
		$.getJSON(url,function(d){
			if(d.data=="errore"){
				alert("Container does not exist");
				errore_piastra("operativa");
			}
			else if(d.data=="errore_banca"){
				alert("Error while connecting with biobank");
				errore_piastra("operativa");
			}
			else{
				lista_container_usati[codice+"|"+tipocaricamento]=d;			
				var controllo=piastra_definitiva_operativa(d,codice,automatico);
				if(!controllo){
					clearTimeout(timer);
			    	$("body").removeClass("loading");
			    	errore_piastra("operativa");
					return;
				}			
				//solo se ho cliccato su zoom -
				if(zoom){
					//devo evidenziare il cont che prima era visualizzato per esteso e adesso risulta all'interno del padre
					var div=evidenzia("operativa", cont_partenza);
					$(div).attr("c","pb_highlight");
					var bb=$(div).attr("barcode");
					if ((bb=="")||(bb==undefined)){
						tasto_sel_sorg=cont_partenza;
					}
					else{
						tasto_sel_sorg=bb;
					}
				}
			}
			clearTimeout(timer);
	    	$("body").removeClass("loading");
		});
	}
}

function piastra_definitiva_operativa(d,codice,automatico){
	if(tipospost=="simple"){
		$("#barcode_operative").attr("value",codice);
	}
	else if (tipospost=="list"){
		$("#barcode_operative").attr("value","");
	}
	$("#plate_operative").children().replaceWith(d.data);
	$("#operativa table button[sel=\"s\"]").attr("disabled",false);
	$("#operativa table button[sel=\"s\"]").css("background-color","gray");
	//attributi per lo spostamento multiplo
	$("#operativa table button").attr("assign","-");
	$("#operativa table button").attr("prev","plateButtonOFF");
	$("#operativa table button").attr("onclick","move(this,\"bot\")");
	$("#operativa table button").attr("c","plateButtonOFF");
	//mi occupo del tooltip per il genid
	var listabutton=$("#operativa table button[sel=\"s\"]");
	//per sapere quanti container possono stare all'interno di un posto di questo cont
	var posmax=$("#operativa table").attr("posmax");
	//e' True se sto vedendo lo zoom in un cassetto ad es, ma qui sono nel padre e quindi e' a false
	var mult=$("#operativa table").attr("mult");
	//e' itself se sto vedendo un cont da solo senza padre
	var itselfcontsorg=$("#operativa table").attr("itself");
	//prendo il barcode effettivo di quello che sto vedendo. Non posso basarmi su "codice"
	var barcodecont=$("#operativa table").attr("barcode").toLowerCase();
	//devo verificare di non vedere lo stesso cont a destra e a sinistra
	var barcodecontdest=$("#freezer table").attr("barcode");
	if((barcodecontdest!=undefined)&&(barcodecontdest==barcodecont)){
		alert("Error: you cannot have same container as source and destination");
		return false;
	}
	//riscrivo i figli della piastra per trasformarli da button a div
	for(var i=0;i<listabutton.length;i++){
		var gen=$(listabutton[i]).attr("gen");
		if (gen==undefined){
			gen="";
		}
		var barcc=$(listabutton[i]).attr("barcode");
		var classealiq=$(listabutton[i]).attr("class");
		var itself=$(listabutton[i]).attr("itself");
		var lbarcfinale=[];
		var lgenfinale=[];
		var numcont=0;
		if (posmax!="1"){
			var lisbarc=barcc.split("&");
			var lisgen=gen.split("&");
			var fr="tooltip.show(\"";		
			for(var kk=0;kk<lisbarc.length;kk++){
				esegui=true;
				var barcodeff=lisbarc[kk].split("|");
				if(mult=="False"){
					//devo cancellare i cont se sono presenti nella mappa
					if(barcodecont in mappa_tolti){
						var vettore_posiz=mappa_tolti[barcodecont];
						for(var j=0;j<vettore_posiz.length;j++){
							//nel caso in cui sono nei cassetti, devo togliere il |A1 finale che ho nella chiave della mappa
							//per poterlo confrontare con il lisbarc[kk] che non ha il |
							var vettsplit=vettore_posiz[j].split("|");
							if((itself==undefined)&&(gen!="&")&&(lisgen[kk]!="")&&((lisbarc[kk].toLowerCase()==vettore_posiz[j].toLowerCase())||(lisgen[kk].toLowerCase()==vettore_posiz[j].toLowerCase())||(lisbarc[kk].toLowerCase()==vettsplit[0].toLowerCase()))){
								esegui=false;
								//se sono in una foglia vuol dire che vedo il numero di pezzi del campione e non il numero di figli
								if((classealiq!=undefined)&&(classealiq.indexOf("foglia")>-1)){
									var tst=listabutton[i].innerHTML;
									if(isNaN(tst)){
										numcont++;
									}
									else{
										numcont+=tst;
									}
								}
								else{
									numcont++;
								}
							}
						}
					}
				}
				if(esegui){					
					if (lisgen[kk]==""){
						fr+=barcodeff[0]+"<br>";
					}
					else{
						if((classealiq!=undefined)&&(classealiq.indexOf("aliqclass")>-1)){
							//sono in un'aliquota, che ne puo' anche avere dentro piu' di una.
							//In ogni caso nel tooltip metto solo il gen
							//Anche il gen puo' essere multiplo
							var gentemp=lisgen[kk].split("&");
							var genfin="";
							for(var jj=0;jj<gentemp.length;jj++){
								genfin+=gentemp[jj]+"<br>";
							}
							var gfin=genfin.substring(0,genfin.length-4);
							fr+=gfin+"<br>";
						}
						else{
							if(lisgen[kk]!="notdefined"){
								//Anche il gen puo' essere multiplo
								var gentemp=lisgen[kk].split("&");
								if(mult=="True"){
									//sono in un cassetto che potrebbe contenere piu' aliquote in ogni blocchetto
									//quindi faccio vedere barc e poi i gen contenuti
									var gentemp=gen.split("&");
								}															
								var genfin="";
								for(var jj=0;jj<gentemp.length;jj++){
									genfin+=gentemp[jj]+"<br>";
								}
								var gfin=genfin.substring(0,genfin.length-4);
								fr+=barcodeff[0]+"--"+gfin+"<br>";
							}
							else{
								fr+=barcodeff[0]+"<br>";
							}
						}
					}
					lbarcfinale.push(lisbarc[kk]);
					lgenfinale.push(lisgen[kk]);
				}
			}
			fr+="\")";
		}
		else{
			var barcodeff=barcc.split("|");
			if((classealiq!=undefined)&&(classealiq.indexOf("aliqclass")>-1)){
				//sono in un'aliquota, che ne puo' anche avere dentro piu' di una.
				//In ogni caso nel tooltip metto solo il gen
				//Anche il gen puo' essere multiplo
				var gentemp=gen.split("&");
				var genfin="";
				for(var jj=0;jj<gentemp.length;jj++){
					genfin+=gentemp[jj]+"<br>";
				}
				var gfin=genfin.substring(0,genfin.length-4);
				var fr="tooltip.show(\""+gfin+"\")";
			}
			else{
				if((gen!="")&&(gen!="notdefined")){
					//Anche il gen puo' essere multiplo
					var gentemp=gen.split("&");
					var genfin="";
					for(var jj=0;jj<gentemp.length;jj++){
						genfin+=gentemp[jj]+"<br>";
					}
					var gfin=genfin.substring(0,genfin.length-4);
					var fr="tooltip.show(\""+barcodeff[0]+" GenID: "+gfin+"\")";
				}
				else{
					var fr="tooltip.show(\""+barcodeff[0]+"\")";
				}
			}
		}
		$(listabutton[i]).attr("onmouseover",fr);
		var id=$(listabutton[i]).attr("id");
		var barc=$(listabutton[i]).attr("barcode");
		var quant=listabutton[i].innerHTML;
		if(numcont!=0){
			var strbarc="";
			var strgen="";
			for(var zz=0;zz<lbarcfinale.length;zz++){
				strbarc+=lbarcfinale[zz]+"&";
				strgen+=lgenfinale[zz]+"&";
			}
			barc=strbarc.substring(0,strbarc.length-1);
			gen=strgen.substring(0,strgen.length-1);
			quant=quant-numcont;			
			if((quant<=0)||(isNaN(quant))){
				//inserisco il blocchetto in toto nella mappa cosi' da cancellarlo completamente nel pezzo di codice dopo
				if(barcodecont in mappa_tolti){
					var vettore_posiz=mappa_tolti[barcodecont];
					if($.inArray(barc, vettore_posiz) == -1){
						vettore_posiz.push(barc);
					}
					mappa_tolti[barcodecont]=vettore_posiz;					
				}
			}
		}
		var tipoaliq=$(listabutton[i]).attr("tipo");
		var tipocont=$(listabutton[i]).attr("cont");
		var classetasto=$(listabutton[i]).attr("class");
		var rowtasto=$(listabutton[i]).attr("row");
		var coltasto=$(listabutton[i]).attr("col");
		var aliq=$(listabutton[i]).attr("aliq");
		var itself=$(listabutton[i]).attr("itself");
		var pieno=$(listabutton[i]).attr("pieno");
		if(classetasto==undefined){
			classetasto="";
		}
		$(listabutton[i]).replaceWith("<div class=\'drag\ "+classetasto+"' align='center' id='"+id+"' onmouseover='"+fr+"' onmouseout='tooltip.hide();' gen='"+gen+"' barcode='"+barc+"' aliq='"+aliq+"' assign='"+barc+"' pieno='"+pieno+"' tipo='"+tipoaliq+"' itself='"+itself+"' cont='"+tipocont+"' row='"+rowtasto+"' col='"+coltasto+"' prev='plateButtonOFF' c='plateButtonOFF' onclick='move(this,\"top\")'>" + quant + '</div>');
	}		

	//metto classe=mark nelle celle in cui non voglio che venga
	//posizionato un tasto con il drag and drop
	$("#operativa th,.intest").attr("class","mark");
	//prendo i parent dei button cioe' i td
	//$("#operativa table button,#operativa .drag").parent().attr("class","mark");
	if(posmax=="1"){
		$("#operativa table div[gen]").parent().attr("class","mark");
	}
	$("#operativa table button[sel!='s']").attr("disabled",false);
	
	//assegno una larghezza fissa alle celle della tabella per fare in
	//modo che durante lo spostamento le colonne rimaste vuote
	//non si rimpiccioliscano
	var listd=$("#operativa table td");
	if (listd.length==1){
		$(listd).attr("width","32px");
		$(listd).attr("height","30px");
	}
	else{
		$(listd).not(":first-child").attr("width","32px");
		$(listd).not(":first-child").attr("height","30px");
		//tolgo l'attributo dell'altezza alla prima riga della tabella
		//quella con l'intestazione delle colonne
		$("#operativa table tr:nth-child(2) td").removeAttr("height");
	}	
	//faccio vedere la tabella con il riepilogo delle piastre
    $("#listapias1").css("display","");
	var vettore=new Array();

	//mi occupo di quello che avevo tolto gia' prima dal container
	var costar=$("#operativa table").attr("costar");
	if(barcodecont in mappa_tolti){
		var vettore_posiz=mappa_tolti[barcodecont];
    	//vedo se in quella piastra avevo gia' tolto qualcosa prima e lo
    	//tolgo dalla piastra
		var listatogliere=[];
    	for(var i=0;i<vettore_posiz.length;i++){
			var valore=vettore_posiz[i];
			//aggiungo a listatogliere solo se non l'ho messo anche nella lista aggiunti
			var trovato=false;
			if(barcodecont in mappa_aggiunti){
				var vettore_posiztemp=mappa_aggiunti[barcodecont];
				for (var idcella in vettore_posiztemp){
					var lisbarcagg=vettore_posiztemp[idcella];					
					for(var barcc in lisbarcagg){
						if(barcc==valore){
							trovato=true;
							break;
						}
					}
				}
			}
			if(!trovato){
				listatogliere.push(valore);
			}
			var ldiv=$("#operativa table div").filter(function(){
				var barc=$(this).attr("barcode");
				if(barc.toLowerCase()==valore.toLowerCase()){			 
					return this;
				}
			});
			for(var j=0;j<ldiv.length;j++){
				//per rimpiazzare i posti vuoti con altri tasti a 0 o X
				var quant="X";
				if(costar=="True"){					
					quant="0";
					//guardo se il barc del padre coincide con quello del figlio. Se sì vuol dire che
					//e' una provetta e quindi devo mettere la X anche se e' costar
					if((barcodecont.toLowerCase()==valore.toLowerCase())||(mult=="True")){
						quant="X";
					}
				}
				//imposto nel div spostato il giusto valore di righe e colonne
				var colvecchia=$(ldiv[j]).attr("col");
				var rigavecchia=$(ldiv[j]).attr("row");
				var id=$(ldiv[j]).attr("id");
				var tdcella=$(ldiv[j]).parent();
				$(tdcella).html("<button align='center' id='"+id+"' col='"+colvecchia+"' row='"+rigavecchia+"' type='submit' class='disp' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>"+quant+"</button>");
				$(tdcella).removeClass("mark");
				//$(ldiv[j]).remove();
			}			
    	}
    	//se sono ad es. nella lista di FF devo andare a modificare il barcode della piastra sorg per fare in modo
		//che poi quando faccio lo zoom- mi venga evidenziato il cont stesso
    	if(mult=="True"){
	    	var tmp_sorg=$("#operativa table").attr("barcode");
	    	var barcpiassorg=tmp_sorg.split("&");
			var barcnuovo="";
			var lisfin=[];
			for(var kk=0;kk<barcpiassorg.length;kk++){
				trovato=false;
				for (var zz=0;zz<listatogliere.length;zz++){
					var barctemp=listatogliere[zz].split("|");				
					if(barcpiassorg[kk]==barctemp[0]){
						trovato=true;
						break;
					}
				}
				if(!trovato){
					lisfin.push(barcpiassorg[kk]);
				}
			}
			for(var h=0;h<lisfin.length;h++){
				barcnuovo+=lisfin[h]+"&";
			}
			var barcfin=barcnuovo.substring(0,barcnuovo.length-1);
			$("#operativa table").attr("barcode",barcfin);
    	}
	}
	//mi occupo di quello che avevo messo gia' prima nel container
	if(barcodecont in mappa_aggiunti){
		var vettore_posiz=mappa_aggiunti[barcodecont];
		for (var idcella in vettore_posiz){
			var lishtml=vettore_posiz[idcella];
			var htmltot="";
			for(var html in lishtml){
				htmltot+=lishtml[html];
			}
			//se l'idcella comincia con m non va bene, allora lo trasformo e metto la h
			if(idcella[0]=="m"){
				var idtmp=idcella.split("-");
				idcella="h-"+idtmp[1];
			}
			$("#"+idcella).append(htmltot);
			if(posmax=="1"){
				$("#"+idcella).addClass("mark");
			}
			//devo vedere se nella cella ci sono dei button e se si' li cancello. 
			//I button sono quelli che hanno X o 0, mentre i div sono quelli spostabili e devo lasciarli
			$("#"+idcella+" button").remove();
		}
	}

	//se sono in itself e sto vedendo il padre, allora devo evidenziare il figlio
	if(d.itself){
		var div=evidenzia("operativa", codice);
		$(div).attr("c","pb_highlight");
		tasto_sel_sorg=$(div).attr("barcode");
	}
	else{
		tasto_sel_sorg="";
	}
	
	//devo vedere se quella piastra c'e' gia' nella lista o no
	var listapias=$("#listapias1 td");
	var trovato=false;
	for(i=0;i<listapias.length;i++){
		var cod=$(listapias[i]).text().trim();
		if (codice.toLowerCase()==cod.toLowerCase()){
			trovato=true;		
		}
	}
	//se non l'ho trovato e se non sto facendo una lista di figli
	if ((trovato==false)&&(tipospost=="simple")){
		var tabella = document.getElementById("listapias1");
		//prendo il numero di righe della tabella
		var rowCount = tabella.rows.length;
		var row = tabella.insertRow(rowCount);
		//per centrare la td
		row.align="center";
		//inserisco la cella con dentro il numero d'ordine
	    var cell1 = row.insertCell(0);
	    cell1.innerHTML =codice;
	    $("#listapias1 td:last").click(carica_operativa_scelta);
	}
	
	//vedo se disabilitare o meno lo zoom-
	var codpadre=$("#operativa table").attr("father");
	$("#sorgmeno").attr("disabled",false);
	if((codpadre=="")&&(modo_sorg=="itself")){
		$("#sorgmeno").attr("disabled",true);
	}
	
	// reference to the REDIPS.drag library
    var rd = REDIPS.drag;
    // initialization
    rd.init();
    // set hover color
    rd.hover.color_td = '#E7C7B2';
    //if(posmax=="1"){
    	//rd.drop_option = 'overwrite';
    //}
    //else{
    rd.drop_option = 'multiple';
    //}
    // set shift mode to vertical2
    rd.shift_option = 'vertical2';
    // enable animation on shifted elements
    rd.animation_shift = true;
    // set animation loop pause
    rd.animation_pause = 20;
    rd.myhandler_dropped = invia_dati;
    rd.myhandler_moved = cella_partenza;
    
    cont_sorg=codice;
    
    var colcont=$("#operativa table").attr("col");
	var rowcont=$("#operativa table").attr("row");
	//automatico e' per dire o no di fare questa operazione. Ad es. quando faccio undo non voglio questa azione
	if((colcont=="1")&&(rowcont=="1")&&(automatico)){
		pos_automatico();
	}
	//per cambiare colore ai container vuoti
	//$("#operativa table div.drag[pieno=False]").css("background-color","#D2DBDC");
	$("#operativa table div.drag[pieno=False]").css("background-color","white");
    return true;
}

function carica_stored_scelta(){
	var codice=$(this).text().trim();
	var sel=$("#view_dest").is(':checked');
	if (sel){
		var tipocaricamento="children";
	}
	else{
		var tipocaricamento="itself";
	}
	tipospost_dest="simple";
	carica_piastra_stored_effettiva(codice,tipocaricamento,false);
}

function carica_stored(){
	if ($("#barcode_freezer").val() == "")
		alert("Insert barcode in destination container");
	else{
		var codice=$("#barcode_freezer").val().trim();
		if(codice.indexOf("|")>-1){
			alert("Please note that barcodes with '|' are not supported");
		}
		else{
			var sel=$("#view_dest").is(':checked');
			if (sel){
				var tipocaricamento="children";
			}
			else{
				var tipocaricamento="itself";
			}
			tipospost_dest="simple";
			carica_piastra_stored_effettiva(codice,tipocaricamento,false);
		}
	}
}

function carica_piastra_stored_effettiva(codice,tipocaricamento,zoom){
	var codspl=codice.split("|");
	codice=codspl[0];
	//devo verificare di non vedere lo stesso cont a destra e a sinistra
	var barcodecont=$("#operativa table").attr("barcode");
	if((codice==cont_sorg)||((barcodecont!=undefined)&&(codice==barcodecont))){
		alert("Error: you cannot have same container as source and destination");
		return;
	}
	//devo vedere se e' stato scelto di caricare il container o i figli
	var cont_partenza=cont_dest;
	modo_dest=tipocaricamento;
	var chiave=codice+"|"+tipocaricamento;
	if (chiave in lista_container_usati){
		d=lista_container_usati[chiave];
		var controllo=piastra_def_stored(d,codice);
		if(!controllo){
			errore_piastra("freezer");
			return;
		}
		if(zoom){			
			var div=evidenzia("freezer", cont_partenza);
			$(div).addClass("selezionato");
			var bb=$(div).attr("barcode");
			if ((bb=="")||(bb==undefined)){
				tasto_sel_dest=cont_partenza;
			}
			else{
				tasto_sel_dest=bb;
			}
		}
	}
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		var codiceurl=codice.replace(/#/g,"%23");
		var url=base_url+"/api/table/"+codiceurl+"/"+tipocaricamento+"/"+tipospost_dest+"/";
		$.getJSON(url,function(d){
			if(d.data=="errore"){
				alert("Container does not exist");
				$("#freezer table td").attr("class","mark");
				errore_piastra("freezer");
			}					
			else if(d.data=="errore_banca"){
				alert("Error while connecting with biobank");
				$("#freezer table td").attr("class","mark");
				errore_piastra("freezer");
			}
			else{
				lista_container_usati[codice+"|"+tipocaricamento]=d;			
				var controllo=piastra_def_stored(d,codice);
				if(!controllo){
					clearTimeout(timer);
			    	$("body").removeClass("loading");
			    	errore_piastra("freezer");
					return;
				}
				if(zoom){					
					var div=evidenzia("freezer", cont_partenza);
					$(div).addClass("selezionato");
					var bb=$(div).attr("barcode");
					if ((bb=="")||(bb==undefined)){
						tasto_sel_dest=cont_partenza;
					}
					else{
						tasto_sel_dest=bb;
					}
				}
			}
			clearTimeout(timer);
	    	$("body").removeClass("loading");
		});
	}
}

function seleziona_tasto(){
	if(!pos_multiplo){
		var oggetto=(".selezionato");
		var idpadrevecchio=$(oggetto).parent().attr("id");
		var idpadrenuovo=$(this).parent().attr("id");
		if (idpadrevecchio!=idpadrenuovo){
			$(oggetto).removeClass("selezionato");
			$(this).addClass("selezionato");
			tasto_sel_dest=$(this).attr("barcode");
		}
		else{
			$(oggetto).removeClass("selezionato");
			tasto_sel_dest="";
		}
	}
}

function piastra_def_stored(d,codice){
	if(tipospost_dest=="simple"){
		$("#barcode_freezer").attr("value",codice);
	}
	else if(tipospost_dest=="list"){
		$("#barcode_freezer").attr("value","");
	}
	$("#plate_stored").children().replaceWith(d.data);
	//prendo il barcode effettivo di quello che sto vedendo. Non posso basarmi su "codice"
	var barcodecont=$("#freezer table").attr("barcode").toLowerCase();
	
	var barcodecontsorg=$("#operativa table").attr("barcode");
	if((barcodecontsorg!=undefined)&&(barcodecontsorg==barcodecont)){
		alert("Error: you cannot have same container as source and destination");
		return false;
	}
	
	//e' itself se sto vedendo un cont da solo senza padre
	var itselfcontdest=$("#freezer table").attr("itself");
	
	//cambio gli id in modo che siano univoci
	var listastore=$("#freezer table button");
	for(i=0;i<listastore.length;i++){
		var idoriginale=$(listastore[i]).attr("id");
		var ids=idoriginale.split("-");
		$(listastore[i]).removeAttr("id");
		if(ids[0]=="o"){
			var idfinale="o-"+ids[1];
		}
		else{
			var idfinale="m-"+ids[1];
		}
		$(listastore[i]).parent().attr("id",idfinale);
	}
	
	//per sapere quanti container possono stare all'interno di un singolo posto di questo cont
	var posmax=$("#freezer table").attr("posmax");
	
	//attributi per lo spostamento multiplo
	$("#freezer table button").attr("assign","-");
	$("#freezer table button").attr("prev","plateButtonOFF");
	
	$("#freezer table button").attr("c","plateButtonOFF");

	//$("#freezer table button[sel!='s']").attr("disabled",false);
	//$("#freezer table button[gen]").attr("disabled",true);
	$("#freezer table button").attr("disabled",false);
	//$("#freezer table button[gen]").addClass("disable");
	//$("#freezer table button").not("[gen]").attr("disabled",false);
		
	//se non ci puo' stare piu' di un cont in una pos, allora blocco lo spostamento multiplo
	if(posmax=="1"){
		//$("#freezer table button[gen]").attr("assign","pieno");
		$("#freezer table button").not("[sel]").attr("onclick","move(this,\"bot\")");
		//prendo i parent dei button cioe' i td
		$("#freezer table button[sel]").parent().attr("class","mark");
		$("#freezer table button").attr("onclick","move(this,\"bot\")");
	}
	else{
		$("#freezer table button").attr("onclick","move(this,\"bot\")");
	}
	
	$("#freezer table button[sel='s']").click(seleziona_tasto);
	//$("#freezer table button").not("[gen]").parent().removeClass("mark");
	//$("#freezer table button").not("[gen]").attr("assign","-");
	
	//metto classe=mark nelle celle in cui non voglio che venga
	//posizionato un tasto con il drag and drop
	$("#freezer th,.intest").attr("class","mark");
	
	$("#freezer table td").not(":first-child").attr("width","33px");
	$("#freezer table td").not(":first-child").attr("height","30px");
	//tolgo l'attributo dell'altezza alla prima riga della tabella
	//quella con l'intestazione delle colonne
	$("#freezer table tr:nth-child(2) td").removeAttr("height");
	
	//metto il tooltip sui container
	var listabutton=$("#freezer table button[sel=\"s\"]");
	//e' True se sto vedendo lo zoom in un cassetto ad es, ma qui sono nel padre e quindi e' a false
	var mult=$("#freezer table").attr("mult");
	
	for(var i=0;i<listabutton.length;i++){
		var gen=$(listabutton[i]).attr("gen");
		if (gen==undefined){
			gen="";
		}
		var barcc=$(listabutton[i]).attr("barcode");
		var classealiq=$(listabutton[i]).attr("class");
		var itself=$(listabutton[i]).attr("itself");
		var lbarcfinale=[];
		var lgenfinale=[];
		var numcont=0;
		if (posmax!="1"){
			var lisbarc=barcc.split("&");
			var lisgen=gen.split("&");		
			var fr="tooltip.show(\"";
			for(var kk=0;kk<lisbarc.length;kk++){
				esegui=true;
				if(mult=="False"){
					//devo cancellare i cont se sono presenti nella mappa
					if(barcodecont in mappa_tolti){
						var vettore_posiz=mappa_tolti[barcodecont];
						for(var j=0;j<vettore_posiz.length;j++){
							//nel caso in cui sono nei cassetti, devo togliere il |A1 finale che ho nella chiave della mappa
							//per poterlo confrontare con il lisbarc[kk] che non ha il |
							var vettsplit=vettore_posiz[j].split("|");
							if((itself==undefined)&&(gen!="&")&&(lisgen[kk]!="")&&((lisbarc[kk].toLowerCase()==vettore_posiz[j].toLowerCase())||(lisgen[kk].toLowerCase()==vettore_posiz[j].toLowerCase())||(lisbarc[kk].toLowerCase()==vettsplit[0].toLowerCase()))){
								esegui=false;
								//se sono in una foglia vuol dire che vedo il numero di pezzi del campione e non il numero di figli
								if((classealiq!=undefined)&&(classealiq.indexOf("foglia")>-1)){
									var tst=listabutton[i].innerHTML;
									if(isNaN(tst)){
										numcont++;
									}
									else{
										numcont+=tst;
									}
								}
								else{
									numcont++;
								}
							}
						}
					}
				}
				if(esegui){
					var barcodeff=lisbarc[kk].split("|");
					if (lisgen[kk]==""){
						fr+=barcodeff[0]+"<br>";
					}
					else{
						if((classealiq!=undefined)&&(classealiq.indexOf("aliqclass")>-1)){
							//sono in un'aliquota, che ne puo' anche avere dentro piu' di una.
							//In ogni caso nel tooltip metto solo il gen
							//Anche il gen puo' essere multiplo
							var gentemp=lisgen[kk].split("&");
							var genfin="";
							for(var jj=0;jj<gentemp.length;jj++){
								genfin+=gentemp[jj]+"<br>";
							}
							var gfin=genfin.substring(0,genfin.length-4);
							fr+=gfin+"<br>";
						}
						else{
							if(lisgen[kk]!="notdefined"){
								//Anche il gen puo' essere multiplo
								var gentemp=lisgen[kk].split("&");
								if(mult=="True"){
									//sono in un cassetto che potrebbe contenere piuì aliquote in ogni blocchetto
									//quindi faccio vedere barc e poi i gen contenuti
									var gentemp=gen.split("&");
								}
								var genfin="";
								for(var jj=0;jj<gentemp.length;jj++){
									genfin+=gentemp[jj]+"<br>";
								}
								var gfin=genfin.substring(0,genfin.length-4);
								fr+=barcodeff[0]+"--"+gfin+"<br>";
							}
							else{
								fr+=barcodeff[0]+"<br>";
							}
						}
					}
					lbarcfinale.push(lisbarc[kk]);
					lgenfinale.push(lisgen[kk]);
				}
			}
			fr+="\")";
		}
		else{
			var barcodeff=barcc.split("|");
			if((classealiq!=undefined)&&(classealiq.indexOf("aliqclass")>-1)){
				//sono in un'aliquota, che ne puo' anche avere dentro piu' di una.
				//In ogni caso nel tooltip metto solo il gen
				//Anche il gen puo' essere multiplo
				var gentemp=gen.split("&");
				var genfin="";
				for(var jj=0;jj<gentemp.length;jj++){
					genfin+=gentemp[jj]+"<br>";
				}
				var gfin=genfin.substring(0,genfin.length-4);
				var fr="tooltip.show(\""+gfin+"\")";
			}
			else{
				if((gen!="")&&(gen!="notdefined")){
					//Anche il gen puo' essere multiplo
					var gentemp=gen.split("&");
					var genfin="";
					for(var jj=0;jj<gentemp.length;jj++){
						genfin+=gentemp[jj]+"<br>";
					}
					var gfin=genfin.substring(0,genfin.length-4);
					var fr="tooltip.show(\""+barcodeff[0]+" GenID: "+gfin+"\")";
				}
				else{
					var fr="tooltip.show(\""+barcodeff[0]+"\")";
				}
			}
		}
		var quant=$(listabutton[i]).text();
		if(numcont!=0){
			var strbarc="";
			var strgen="";
			for(var zz=0;zz<lbarcfinale.length;zz++){
				strbarc+=lbarcfinale[zz]+"&";
				strgen+=lgenfinale[zz]+"&";
			}
			barc=strbarc.substring(0,strbarc.length-1);
			gen=strgen.substring(0,strgen.length-1);
			quant=quant-numcont;
			if((quant<=0)||(isNaN(quant))){
				//inserisco il blocchetto in toto nella mappa cosi' da cancellarlo completamente nel pezzo di codice dopo
				if(barcodecont in mappa_tolti){
					var vettore_posiz=mappa_tolti[barcodecont];
					if($.inArray(barc, vettore_posiz) == -1){
						vettore_posiz.push(barc);
					}
					mappa_tolti[barcodecont]=vettore_posiz;					
				}
			}
			$(listabutton[i]).attr("gen",gen);
			$(listabutton[i]).attr("barcode",barc);
			$(listabutton[i]).text(quant);
		}
		
		$(listabutton[i]).attr("onmouseover",fr);
		$(listabutton[i]).attr("onmouseout","tooltip.hide();");
	}		
	
	//faccio vedere la tabella con il riepilogo delle piastre
    $("#listapias2").css("display","");
    //if(itselfcontdest==undefined){
    //mi occupo di quello che avevo tolto gia' prima dal container
	var costar=$("#freezer table").attr("costar");
	if(barcodecont in mappa_tolti){
		var vettore_posiz=mappa_tolti[barcodecont];
		var listatogliere=[];
    	//vedo se in quella piastra avevo gia' tolto qualcosa prima e lo
    	//tolgo dalla piastra
    	for(var i=0;i<vettore_posiz.length;i++){
			var valore=vettore_posiz[i];
			//aggiungo a listatogliere solo se non l'ho messo anche nella lista aggiunti
			var trovato=false;
			if(barcodecont in mappa_aggiunti){
				var vettore_posiztemp=mappa_aggiunti[barcodecont];
				for (var idcella in vettore_posiztemp){
					var lisbarcagg=vettore_posiztemp[idcella];					
					for(var barcc in lisbarcagg){
						if(barcc==valore){
							trovato=true;
							break;
						}
					}
				}
			}
			if(!trovato){
				listatogliere.push(valore);
			}
			var ldiv=$("#freezer table button[barcode]").filter(function(){ 
				var barc=$(this).attr("barcode");
				if(barc.toLowerCase()==valore.toLowerCase()){			 
					return this;
				}
			});
			for(var j=0;j<ldiv.length;j++){
				//per rimpiazzare i posti vuoti con altri tasti a 0 o X
				var quant="X";
				if(costar=="True"){
					var quant="0";
					//guardo se il barc del padre coincide con quello del figlio. Se sì vuol dire che
					//e' una provetta e quindi devo mettere la X anche se e' costar
					if((barcodecont.toLowerCase()==valore.toLowerCase())||(mult=="True")){
						quant="X";
					}
				}
				//imposto nel div spostato il giusto valore di righe e colonne
				var colvecchia=$(ldiv[j]).attr("col");
				var rigavecchia=$(ldiv[j]).attr("row");
				var id=$(ldiv[j]).attr("id");
				var tdcella=$(ldiv[j]).parent();
				$(tdcella).html("<button align='center' id='"+id+"' col='"+colvecchia+"' row='"+rigavecchia+"' type='submit' assign='-' class='disp' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>"+quant+"</button>");
				$(tdcella).removeClass("mark");
				//$(ldiv[j]).remove();
			}			
    	}
    	
    	//se sono ad es. nella lista di FF devo andare a modificare il barcode della piastra sorg per fare in modo
		//che poi quando faccio lo zoom- mi venga evidenziato il cont stesso
    	if(mult=="True"){
	    	var tmp_sorg=$("#freezer table").attr("barcode");
	    	var barcpiassorg=tmp_sorg.split("&");
			var barcnuovo="";
			var lisfin=[];
			for(var kk=0;kk<barcpiassorg.length;kk++){
				trovato=false;
				for (var zz=0;zz<listatogliere.length;zz++){
					var barctemp=listatogliere[zz].split("|");				
					if(barcpiassorg[kk]==barctemp[0]){
						trovato=true;
						break;
					}
				}
				if(!trovato){
					lisfin.push(barcpiassorg[kk]);
				}
			}
			for(var h=0;h<lisfin.length;h++){
				barcnuovo+=lisfin[h]+"&";
			}
			var barcfin=barcnuovo.substring(0,barcnuovo.length-1);
			$("#freezer table").attr("barcode",barcfin);
    	}
	}
    
    //mi occupo di quello che avevo messo gia' prima nel container
	if(barcodecont in mappa_aggiunti){
		var vettore_posiz=mappa_aggiunti[barcodecont];
		for (var idcella in vettore_posiz){
			var lishtml=vettore_posiz[idcella];
			var htmltot="";
			for(var html in lishtml){
				htmltot+=lishtml[html];
			}
			//se l'idcella comincia con h non va bene, allora lo trasformo e metto la m
			var idtmp=idcella.split("-");
			if(idcella[0]=="h"){				
				idcella="m-"+idtmp[1];
			}
			//questo e' nel caso della visione itself di un container.
			else if(idcella[0]=="a"){				
				idcella="o-"+idtmp[1];
			}
			$("#"+idcella).append(htmltot);
			if(posmax=="1"){
				$("#"+idcella).addClass("mark");
			}
			//devo vedere se nella cella ci sono dei button che abbiano X o 0 e se si' li cancello
			$("#"+idcella+" button").not("[gen]").remove();
			var lisbutt=$("#"+idcella+" button");
			for(var j=0;j<lisbutt.length;j++){
				var testo=$(lisbutt[j]).text();
				if(testo=="0"){
					$(lisbutt[j]).remove();
				}
			}
		}
	}
    //}
	
	//se sono in itself e sto vedendo il padre, allora devo evidenziare il figlio
	if(d.itself){
		var button=evidenzia("freezer", codice);
		var oggetto=(".selezionato");
		$(oggetto).removeClass("selezionato");
		$(button).addClass("selezionato");
		tasto_sel_dest=codice;
	}
	else{
		tasto_sel_dest="";
	}
	
	//devo vedere se quella piastra c'e' gia' nella lista o no
	var listapias=$("#listapias2 td");
	var trovato=false;
	for(i=0;i<listapias.length;i++){
		var cod=$(listapias[i]).text().trim();
		if (codice.toLowerCase()==cod.toLowerCase()){
			trovato=true;		
		}
	}
	if ((trovato==false)&&(tipospost_dest=="simple")){
		var tabella = document.getElementById("listapias2");
		//prendo il numero di righe della tabella
		var rowCount = tabella.rows.length;
		var row = tabella.insertRow(rowCount);
		//per centrare la td
		row.align="center";
		//inserisco la cella con dentro il numero d'ordine
	    var cell1 = row.insertCell(0);
	    cell1.innerHTML =codice;
	    cell1.className="mark";
	    $("#listapias2 td:last").click(carica_stored_scelta);
	}
	
	//vedo se disabilitare o meno lo zoom-
	var codpadre=$("#freezer table").attr("father");
	$("#destmeno").attr("disabled",false);
	if((codpadre=="")&&(modo_dest=="itself")){
		$("#destmeno").attr("disabled",true);
	}
	
	// reference to the REDIPS.drag library
    var rd = REDIPS.drag;
    // initialization
    rd.init();
    // set hover color
    rd.hover.color_td = '#E7C7B2';
    rd.drop_option = 'multiple';

    // set shift mode to vertical2
    rd.shift_option = 'vertical2';
    // enable animation on shifted elements
    rd.animation_shift = true;
    // set animation loop pause
    rd.animation_pause = 20;
    rd.myhandler_dropped = invia_dati;
    rd.myhandler_moved = cella_partenza;
    //metto l'evento per il drop
    //$("#freezer table button").bind("drop",invia_dati);
    //var tar= document.getElementById ("s-A1").parentNode;
    //alert(tar);
    //tar.addEventListener ("drag", invia_dati, false);
    cont_dest=codice;
    $("#freezer table button[pieno=False]").css("background-color","white");
    //$("#freezer table button[pieno=True]").css("background-color","gray");
    return true;
}

function cella_partenza(){
	//nel momento in cui sposto un blocchetto vedo se e' un'aliq e metto o tolgo il mark
	var classitasto=REDIPS.drag.obj.getAttribute("class");
	var posmax=$("#freezer table").attr("posmax");
	var costar=$("#freezer table").attr("costar");
	//se e' un'aliquota
	if(classitasto.indexOf("aliqclass")>-1){
		if((posmax!="1")||(costar=="False")){
			$("#freezer table button[sel]").parent().removeClass("mark");
		}
		$("#freezer table button:contains('X')").parent().addClass("mark");
		$("#freezer table button[gen]").attr("assign","-");
	}
	else{
		$("#freezer table button[gen]").attr("assign","pieno");
		$("#freezer table button").not("[sel]").attr("onclick","move(this,\"bot\")");
		//prendo i parent dei button cioe' i td
		if(posmax=="1"){
			$("#freezer table button[sel]").parent().attr("class","mark");		
		}
		$("#freezer table button:contains('X')").parent().removeClass("mark");
	}
	/*var idpartenza=REDIPS.drag.previous_cell.id;
	var pospartenza=idpartenza.split("-");
	//riempio le variabili da trasmettere con la post
	var data = {
    		partenza:true,
    		pos:pospartenza[1]
    };
	
	var url=base_url+"/store/save/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    });*/
}

function controlla_rapporti_cont(figlio,padre){
	var contaliqmossa=figlio.getAttribute("cont");
	
	var strdest=padre.getAttribute("cont");
	//se sia il padre che il figlio hanno l'attr itself, allora va bene, perche'
	//sono nel caso in cui ho spostato il cont singolo in visuale itself e sto cercando 
	//di rimetterlo al suo posto originale
	var itspadre=padre.getAttribute("itself");
	var itsfiglio=figlio.getAttribute("itself");
	if((itspadre!=undefined)&&(itsfiglio!=undefined)){
		return true;
	}
	//se sono nel caso in cui sto rimettendo un blocchetto di FF al suo posto nella visualizzazione lista
	//vedo se i barc della td e del cont coincidono e se si' lo lascio fare
	var barccella=REDIPS.drag.target_cell.getAttribute("barcode");
	var barcfiglio=figlio.getAttribute("barcode");
	if((barccella!=undefined)&&(barccella==barcfiglio)){
		return true;
	}
	for (var j=0;j<lisrapporti.length;j++){
		if (lisrapporti[j].figlio==contaliqmossa){
			if (lisrapporti[j].padre==strdest){
				return true;
			}
		}
	}
	
	return false;
}

//per vedere se nel posto di dest possa starci un'aliquota
function controlla_rapporti_aliq(drag){
	var aliq=drag.target_cell.getAttribute("aliq");
	if(aliq=="True"){
		return true;
	}
	return false;
}

function conta_figli(figli){
	var numfigli=0;
	for(var i=0;i<figli.length;i++){
		var tag=$(figli[i]).prop("tagName");
		if((tag=="DIV")||(tag=="BUTTON")){
			var testo=$(figli[i]).text();
			//per capire se e' un numero o una stringa. Ad es. nel caso del #
			if (isNaN(testo)){
				numfigli+=1;
			}
			else{
				var testo=parseInt(testo);
				var gen=$(figli[i]).attr("gen");
				if(testo==1){
					//devo vedere se il cont e' pieno e per capirlo guardo se ha l'attributo gen					
					if((gen!=undefined)&&(gen!="&")){
						numfigli+=1;
					}
				}
				else{
					if((gen!=undefined)&&(gen.indexOf("&")>-1)){
						//vuol dire che il tasto contiene piu' di un'aliquota e quindi il numero del tasto indica il numero di
						//aliq presenti
						numfigli+=testo;
					}
					else{
						numfigli+=1;
					}
				}
			}
		}
	}
	return numfigli;
}

function aggiorna_mappe_cont(piastra_sorg,bar,mult,padre,piastra_dest,idcella,idcellasorg,htmlsorg,padredest){
	if (piastra_sorg!=null){
		piastra_sorg=piastra_sorg.toLowerCase();
		if(piastra_sorg in mappa_tolti){
			var vett_sorg=mappa_tolti[piastra_sorg];						
		}
		else{
			var vett_sorg=[];
		}
		//metto in una lista i barc dei div da togliere, in quanto sono stati spostati da li'
		if($.inArray(bar, vett_sorg) == -1){
			vett_sorg.push(bar);
		}
		mappa_tolti[piastra_sorg]=vett_sorg;
	}
	//nel caso in cui sto vedendo lo zoom su un cassetto ad es, devo inserire i tolti anche
	//nel dizionario del padre cosi' quando lo guardero' vedro' l'assenza dei blocchetti spostati.
	//Questo solo se sto posizionando nella dest, se rimetto nella sorg invece devo cancellare dalla mappa il cont
	//Per capire se sono in questo caso	
	if((idcella==null)||(idcella[0]=="m")||(idcella[0]=="o")){
		if(mult=="True"){
			//vuol dire che ho spostato il cont nella dest
			padre=padre.toLowerCase();
			if(padre in mappa_tolti){
				var vett_sorg=mappa_tolti[padre];
			}
			else{
				var vett_sorg=[];
			}
			//metto in una lista i barc dei div da togliere, in quanto sono stati spostati da li'
			if($.inArray(bar, vett_sorg) == -1){
				vett_sorg.push(bar);
			}
			mappa_tolti[padre]=vett_sorg;
			//devo inserire il fatto che ho spostato il cont anche in mappa tolti con chiave composta da il cont stesso insieme a tutti i suoi 
			//altri cont che erano in quella posizione all'inizio. Fra le chiavi che contengono il cont scelgo quella piu' lunga
			var max=0;
			var chiavefin="";
			for(chiave in mappa_tolti){
				var chtmp=chiave.split("&");
				if($.inArray(bar,chtmp)){
					if(chtmp.length>max){
						max=chtmp.length;
						chiavefin=chiave;
					}
				}
			}
			if(chiavefin!=""){
				var vett_s=mappa_tolti[chiavefin];
				if($.inArray(bar, vett_s) == -1){
					vett_s.push(bar);
				}
				mappa_tolti[chiavefin]=vett_s;
			}
			//se sono ad es. nella lista di FF devo andare a modificare il barcode della piastra sorg per fare in modo
			//che poi quando faccio lo zoom- mi venga evidenziato il cont stesso
			var barcpiassorg=piastra_sorg.split("&");
			var barcnuovo="";
			var lisfin=[];
			for(var kk=0;kk<barcpiassorg.length;kk++){
				trovato=false;
				for (var zz=0;zz<vett_sorg.length;zz++){
					var barctemp=vett_sorg[zz].split("|");				
					if(barcpiassorg[kk]==barctemp[0]){
						trovato=true;
						break;
					}
				}
				if(!trovato){
					lisfin.push(barcpiassorg[kk]);
				}
			}
			for(var h=0;h<lisfin.length;h++){
				barcnuovo+=lisfin[h]+"&";
			}
			var barcfin=barcnuovo.substring(0,barcnuovo.length-1);
			$("#operativa table").attr("barcode",barcfin);
		}
	}
	else if((idcella[0]=="h")||(idcella[0]=="a")){
		//solo se sono nel caso del cassetto
		var barctddest=$("#"+idcella).attr("barcode");
		if((barctddest!=undefined)&&(barctddest==bar)){
			//vuol dire che ho spostato il cont nella sorg
			//prendo il padre della piastra dest
			if(padredest in mappa_tolti){			
				var vett_sorg=mappa_tolti[padredest];
				for (var j=0;j<vett_sorg.length;j++){
            		if (vett_sorg[j]==bar){
            			vett_sorg.splice(j,1);
            			break;
            		}
            	}
				mappa_tolti[padredest]=vett_sorg;
				//se sono ad es. nella lista di FF devo andare a modificare il barcode della piastra dest per fare in modo
				//che poi quando faccio lo zoom- mi venga evidenziato il cont stesso
				//devo riscrivere la sequenza dei barc nello stesso ordine di prima se no non me li riconosce
				//piastra_dest e' il riferimento
				var barcfin="";
				var barctemp=bar.split("|");
				var barcattuale=$("#operativa table").attr("barcode");
				var barcatt=barcattuale.split("&");
				var barcrif=piastra_dest.split("&");
				for(var jj=0;jj<barcrif.length;jj++){
					if($.inArray(barcrif[jj], barcatt)>-1){
						barcfin+=barcrif[jj]+"&";
					}
					else{
						if(barcrif[jj]==barctemp[0]){
							barcfin+=barctemp[0]+"&";
						}
					}
				}
				var barcfin=barcfin.substr(0,barcfin.length-1);
				$("#operativa table").attr("barcode",barcfin);
			}
		}
	}
	
	if (piastra_dest!=null){
		piastra_dest=piastra_dest.toLowerCase();
		if(piastra_dest in mappa_aggiunti){
			var vett_dest=mappa_aggiunti[piastra_dest];
			if(idcella in vett_dest){
				var html=vett_dest[idcella];
			}
			else{
				var html={};
			}
			html[bar]=htmlsorg;
			vett_dest[idcella]=html;
		}
		else{
			var vett_dest={};
			vett_dest[idcella]={};
			vett_dest[idcella][bar]=htmlsorg;
		}
		//metto tutto l'html del div da aggiungere in quella posizione
		mappa_aggiunti[piastra_dest]=vett_dest;
	}
	//devo togliere dalla mappa aggiunti il cont spostato, nel caso sia stato spostato piu' volte
	if(piastra_sorg in mappa_aggiunti){
		var vett_vecchio=mappa_aggiunti[piastra_sorg];
		for(idcellas in vett_vecchio){
			//in modo da non cancellarlo dalla cella dove l'ho appena messo
			if(idcellas!=idcella){
				for(bb in vett_vecchio[idcellas]){
					if (bb.toLowerCase()==bar.toLowerCase()){
						delete vett_vecchio[idcellas][bb];
					}
				}
				var html=vett_vecchio[idcellas];
				if(Object.keys(html).length==0){
					delete vett_vecchio[idcellas];
				}
			}
		}
	}
	//solo se sto spostando da temp a dest sulla destra un blocchetto di FF
	if((idcella!=null)&&((idcella[0]=="m")||(idcella[0]=="o"))){
		if(piastra_sorg==null){
			if(mult==null){
				if(padredest in mappa_tolti){
					var vett_sorg=mappa_tolti[padredest];
					var indice=$.inArray(bar, vett_sorg);
					vett_sorg.splice(indice,1);
					mappa_tolti[padre]=vett_sorg;
					
					//se sono ad es. nella lista di FF devo andare a modificare il barcode della piastra dest per fare in modo
					//che poi quando faccio lo zoom- mi venga evidenziato il cont stesso
					//devo riscrivere la sequenza dei barc nello stesso ordine di prima se no non me li riconosce
					//piastra_dest e' il riferimento
					var barcfin="";
					var barctemp=bar.split("|");
					var barcattuale=$("#freezer table").attr("barcode");
					var barcatt=barcattuale.split("&");
					var barcrif=piastra_dest.split("&");
					for(var jj=0;jj<barcrif.length;jj++){
						if($.inArray(barcrif[jj], barcatt)>-1){
							barcfin+=barcrif[jj]+"&";
						}
						else{
							if(barcrif[jj]==barctemp[0]){
								barcfin+=barctemp[0]+"&";
							}
						}
					}
					var barcfin=barcfin.substr(0,barcfin.length-1);
					$("#freezer table").attr("barcode",barcfin);
				}
			}
		}
	}
	//cancello il codice del cont sorg una volta effettuato il posizionamento
	$("#barcode_operative").val("");
}

function aggiorna_diz_generale(bar,piastra_sorg,piastra_dest,aliq,idcella,costardest,testo){
	//Mi occupo del dizionario generale da passare poi al server
	if(bar in dati_server){
		var diztemp=dati_server[bar];
	}
	else{
		var diztemp={};
		diztemp["barcsorg"]=piastra_sorg;						
	}
	diztemp["barcdest"]=piastra_dest;
	diztemp["aliq"]=aliq;
	var tmp=idcella.split("-");
	diztemp["posdest"]=tmp[1];
	//devo vedere se il barc e' multiplo cioe' se contiene una lista di barc separati da &
	var multiplo=false;
	if((testo!="1")&&(bar.indexOf("&")>-1)){
		multiplo=true;
	}
	diztemp["multiplo"]=multiplo;
	var cosdest=false;
	if (costardest=="True"){
		cosdest=true;
	}
	diztemp["costardest"]=cosdest;
	dati_server[bar]=diztemp;
}

function invia_dati(){
	drag=true;
	//per fotografare la situazione iniziale in caso di undo
	var sovrascrivi=true;
	//extend e' per copiare il contenuto di un diz in un altro, true permette di eseguire una copia approfondita di tutto
	//quello che c'e' nel diz originale, quindi anche degli altri diz eventualmente contenuti
	var mapp_agg_tmp=$.extend(true,{},mappa_aggiunti);
	var mapp_tolti_tmp=$.extend(true,{},mappa_tolti);	
	var dizrigh_tmp=$.extend(true,{},diz_righe_tolte);	
	var dizgentemp=$.extend(true,{},dati_server);
	
	var piassorgtmp=$("#operativa table").html();
	var piasdesttmp=$("#freezer table").html();

	//devo vedere se ho messo un container nella tabella temporanea
	var piastra_dest=REDIPS.drag.target_cell.parentNode.parentNode.parentNode;
	var piastra_sorg=REDIPS.drag.source_cell.parentNode.parentNode.parentNode;
	var classitasto=REDIPS.drag.obj.getAttribute("class");
	
	var mult=piastra_sorg.getAttribute("mult");
	var padre=piastra_sorg.getAttribute("father");
	var padredest=piastra_dest.getAttribute("father");
	var costardest=piastra_dest.getAttribute("costar");
	var multdest=piastra_dest.getAttribute("mult");
	//barc del cont che sto effettivamente vedendo, non quello caricato
	var barcodedestattuale=$("#freezer table").attr("barcode");
	var barcodesorgattuale=$("#operativa table").attr("barcode");
	
	var contpadre=piastra_dest.parentNode.parentNode.parentNode.parentNode.getAttribute("id");
	if(contpadre=="operativa"){
		if(mult=="True"){
			var barcodedest=cont_sorg;
		}
		else{
			var barcodedest=barcodesorgattuale;
		}
	}
	else if(contpadre=="freezer"){
		if(multdest=="True"){
			var barcodedest=cont_dest;
		}
		else{
			var barcodedest=barcodedestattuale;
		}
	}
	else{
		var barcodedest=null;
	}
	
	var contpadresorg=piastra_sorg.parentNode.parentNode.parentNode.parentNode.getAttribute("id");
	if(contpadresorg=="operativa"){
		if(mult=="True"){
			var barcodesorg=cont_sorg;
		}
		else{
			var barcodesorg=barcodesorgattuale;
		}
	}
	else if(contpadresorg=="freezer"){
		if(multdest=="True"){
			var barcodesorg=cont_dest;
		}
		else{
			var barcodesorg=barcodedestattuale;
		}
	}
	else{
		var barcodesorg=null;
	}
	var aliq=false;
	//se e' un'aliquota
	if((classitasto!=undefined)&&(classitasto.indexOf("aliqclass")>-1)){
		aliq=true;
	}
	//ho l'id della cella di partenza da dove sono partito per fare il drag and drop
	var partenza=REDIPS.drag.source_cell;
	if (piastra_dest.id!="temp"){
		//devo vedere se la cella dest e' disponibile, nel senso se non e' not available
		var aliqdisp=REDIPS.drag.target_cell.getAttribute("notavailable");
		if(aliqdisp!="True"){
			//devo controllare che l'aliq del cont spostato sia coerente con il cont di destinazione
			var tipoaliqmossa=REDIPS.drag.obj.getAttribute("tipo");
			var listatipialiqfiglio=tipoaliqmossa.split("&");
			var strdest=piastra_dest.getAttribute("tipo");
			var tipodest=strdest.split("&");
			//per capire se sono nella visualizzazione itself dell'oggetto
			var itself=REDIPS.drag.obj.getAttribute("itself");
			//per sapere se ho posizionato il cont nella tabella temp nel caso in cui abbia fatto lo zoom+
			//nella dest perche' la pos dest non era univoca
			var postemp=false;
			//serve per vedere se l'insieme dei tipi aliq del cont spostato e' un sottoinsieme di quello del padre
			var ris = listatipialiqfiglio.every(function(val) { return tipodest.indexOf(val) >= 0; });
	
			if (ris){		
				if(aliq){
					var secondo=controlla_rapporti_aliq(REDIPS.drag);
				}
				else{
					var secondo=controlla_rapporti_cont(REDIPS.drag.obj,piastra_dest);
				}
				if (secondo){
					if(REDIPS.drag.source_cell!=REDIPS.drag.target_cell){				
						var arrivo=REDIPS.drag.target_cell;
						//tolgo il class=mark nella td di partenza
						partenza.classList.remove("mark");
						if(aliq){
							var posmaxd=arrivo.getAttribute("posmax");
							//devo vedere se nel td dest c'e' solo un blocco con lo 0. Se si' lo cancello.
							//childNodes[0] e' il cont che gia' c'era.
							var figli=arrivo.childNodes;
							for(var i=0;i<figli.length;i++){
								var tag=$(figli[i]).prop("tagName");
								if((tag=="DIV")||(tag=="BUTTON")){
									var testo=$(figli[i]).text();
									var col=$(figli[i]).attr("col");
									var row=$(figli[i]).attr("row");
									if(testo=="0"){
										var htmlfiglio=$(figli[i])[0].outerHTML;
										$(figli[i]).remove();
									}
									break;
								}
							}
							
							if((posmaxd=="1")&&(itself=="undefined")){
								//devo vedere se bloccare il tutto perche' il numero di aliq accettabili e' stato raggiunto
								//tra i figli c'e' gia' anche quello posizionato adesso
								var numfigli=conta_figli(figli);
								if(numfigli>1){
									alert("Error: maximum number of containers for this position has been exceeded");
									//sposta la div spostata nella cella di partenza
									REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
									//devo aggiungere il figlio che avevo tolto dalla cella di dest
									if(testo=="0"){
										REDIPS.drag.target_cell.innerHTML=htmlfiglio;
									}
									sovrascrivi=false;
									return;
								}
								//metto class=mark nella td di dest cosi' non posso mettere altri tasti li'
								arrivo.className="mark";																					
							}
							else{						
								if((posmaxd!="None")&&(itself=="undefined")){
									var posint=parseInt(posmaxd);
									
									var numfigli=conta_figli(figli);
									if(numfigli>posint){
										alert("Error: maximum number of containers for this position has been exceeded");
										REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
										//devo aggiungere il figlio che avevo tolto dalla cella di dest
										if(testo=="0"){
											REDIPS.drag.target_cell.innerHTML=htmlfiglio;
										}
										sovrascrivi=false;
										return;
									}								
								}	
								//devo vedere se il figlio presente nella cella contiene piu' di un container. Allora faccio zoom+ sul 
								//cont in questione e metto il cont spostato nella tabella temp
								for(var i=0;i<figli.length;i++){
									var tag=$(figli[i]).prop("tagName");
									if((tag=="DIV")||(tag=="BUTTON")){
										var classedest=$(figli[i]).attr("class");
										//se non e' un'aliquota
										if((classedest!=undefined)&&(classedest.indexOf("aliqclass")==-1)){
											var testodest=$(figli[i]).text();
											if(testodest!="1"){
												var barc=$(figli[i]).attr("barcode");
												tipospost_dest="list";											
												//lo devo posizionare nella tabella temp
												var tdvuote=$("#temp td:empty");
												postemp=true;
												if(tdvuote.length==0){
													alert('Error: "Temporary place" is full');
													REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
													sovrascrivi=false;
												}
												else{
													//metto il div spostato nella prima cella vuota
													tdvuote[0].appendChild(REDIPS.drag.obj);
													var bar=REDIPS.drag.obj.getAttribute("barcode");		
													var htmlsorg=REDIPS.drag.obj.outerHTML;
													var idcellasorg=REDIPS.drag.source_cell.getAttribute("id");
													var idobj=REDIPS.drag.obj.getAttribute("id");
													aggiorna_mappe_cont(barcodesorg,bar,mult,padre,null,null,idcellasorg,htmlsorg,padredest);
													carica_piastra_stored_effettiva(barc,"children",false);
												}
												break;
											}
										}
									}
								}
							}
							var quant="0";
							//nella cella di partenza devo fare questo solo se non c'e' niente altro, altrimenti non tocco niente
							var figlipartenza=partenza.childNodes;
							var conta=0;
							for(var i=0;i<figlipartenza.length;i++){
								var tag=$(figlipartenza[i]).prop("tagName");
								if((tag=="DIV")||(tag=="BUTTON")){
									conta+=1;
									break
								}
							}
							if((conta==0)&&(piastra_sorg.id!="temp")){
								//imposto nel nuovo button il giusto valore di righe e colonne
								var colvecchia=REDIPS.drag.obj.getAttribute("col");
								var rigavecchia=REDIPS.drag.obj.getAttribute("row");
								var idnuovo=partenza.getAttribute("id");
								var pos=idnuovo.split("-")[1];
								partenza.innerHTML="<button align='center' id='r-"+pos+"' col='"+colvecchia+"' row='"+rigavecchia+"' type='submit' class='disp' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>"+quant+"</button>";
							}
						}
						//se non e' un'aliquota
						else{
							var posmaxd=piastra_dest.getAttribute("posmax");
							//devo vedere se nel td dest c'e' solo un blocco con la x. Se si' lo cancello
							//childNodes[0] e' il cont che gia' c'era.
							var figli=REDIPS.drag.target_cell.childNodes;
							for(var i=0;i<figli.length;i++){
								var tag=$(figli[i]).prop("tagName");
								if((tag=="DIV")||(tag=="BUTTON")){
									var testo=$(figli[i]).text();
									var col=$(figli[i]).attr("col");
									var row=$(figli[i]).attr("row");
									if(testo=="X"){
										var htmlfiglio=$(figli[i])[0].outerHTML;
										$(figli[i]).remove();
									}
									break;
								}
							}
							
							if(posmaxd=="1"){
								//metto class=mark nella td di dest cosi' non posso mettere altri tasti li'
								REDIPS.drag.target_cell.className="mark";
							}				
							if((posmaxd!="None")&&(itself=="undefined")){
								var posint=parseInt(posmaxd);
								var figli=REDIPS.drag.target_cell.childNodes;
								var conta=0;
								for(var i=0;i<figli.length;i++){
									var tag=$(figli[i]).prop("tagName");
									if((tag=="DIV")||(tag=="BUTTON")){
										var pezzi=parseInt($(figli[i]).text());
										//nel caso in cui ci sia il cont vuoto che viene spostato. Devo comunque
										//contarlo come uno
										if(pezzi==0){
											pezzi=1;
										}
										conta+=pezzi;
									}							
								}							
								if(conta>posint){
									alert("Error: maximum number of containers for this position has been exceeded");
									REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
									//devo aggiungere il figlio che avevo tolto dalla cella di dest
									if(testo=="X"){
										REDIPS.drag.target_cell.innerHTML=htmlfiglio;
									}
									sovrascrivi=false;
									return;
								}
							}
							var quant="X";
							//nella cella di partenza devo fare questo solo se non c'e' niente altro, altrimenti non tocco niente
							var figlipartenza=partenza.childNodes;
							var conta=0;
							for(var i=0;i<figlipartenza.length;i++){
								var tag=$(figlipartenza[i]).prop("tagName");
								if((tag=="DIV")||(tag=="BUTTON")){
									conta+=1;
									break
								}
							}
							if((conta==0)&&(piastra_sorg.id!="temp")){
								//imposto nel nuovo button il giusto valore di righe e colonne
								var colvecchia=REDIPS.drag.obj.getAttribute("col");
								var rigavecchia=REDIPS.drag.obj.getAttribute("row");
								var idnuovo=partenza.getAttribute("id");
								var pos=idnuovo.split("-")[1];
								partenza.innerHTML="<button align='center' id='r-"+pos+"' col='"+colvecchia+"' row='"+rigavecchia+"' type='submit' class='disp' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>"+quant+"</button>";
							}
						}
						
						if (!postemp){
							//imposto nel div spostato il giusto valore di righe e colonne
							REDIPS.drag.obj.setAttribute("col", col);
							REDIPS.drag.obj.setAttribute("row", row);
							var idcella=REDIPS.drag.target_cell.getAttribute("id");
							var idcellasorg=REDIPS.drag.source_cell.getAttribute("id");
							var idtmp=idcella.split("-");
							
							var canctab=false;
							var tipaltemp="";
							var bar=REDIPS.drag.obj.getAttribute("barcode");
							var tipoaliq=REDIPS.drag.obj.getAttribute("tipo");
							if((idcella[0]=="m")||(idcella[0]=="o")){
								REDIPS.drag.obj.setAttribute("id", "b-"+idtmp[1]);
								canc_da_tabella([bar]);
								canctab=true;						
								var tipaliq=tipoaliq.split("&");
								tipaltemp=tipaliq[0];
							}
							else if((idcella[0]=="h")||(idcella[0]=="a")){
								REDIPS.drag.obj.setAttribute("id", "r-"+idtmp[1]);
								var tipaliq=tipoaliq.split("&");
								aggiungi_in_tabella([bar],tipaliq[0]);
							}
							
							//reimposto allo stato iniziale il tasto per togliere il conflitto tra l'evento
							//on click e il drag and drop.
							var previous = REDIPS.drag.obj.getAttribute("prev");
							REDIPS.drag.obj.setAttribute("c", previous);
							flag = "-";
														
							var htmlsorg=REDIPS.drag.obj.outerHTML;
							var idobj=REDIPS.drag.obj.getAttribute("id");
							if(sovrascrivi){
								prepara_per_undo(mapp_agg_tmp,mapp_tolti_tmp,dizrigh_tmp,dizgentemp,piassorgtmp,piasdesttmp,canctab,bar,tipaltemp,cont_sorg,cont_dest);
							}
							
							aggiorna_mappe_cont(barcodesorg,bar,mult,padre,barcodedest,idcella,idcellasorg,htmlsorg,padredest);
							//se ho la dest sotto forma di lista di cont (ad es. stessa posizione in un cassetto) 
							if(multdest=="True"){
								var barctmp=REDIPS.drag.target_cell.getAttribute("barcode");								
								//sono nel caso in cui sto vedendo una lista di aliquote
								if(barctmp==undefined){
									barcodedest=padredest;
								}
								else{
									barcodedest=barctmp.split("|")[0];
								}
								idcella="-";
							}
							var testo=REDIPS.drag.obj.innerHTML;
							aggiorna_diz_generale(bar,barcodesorg,barcodedest,aliq,idcella,costardest,testo);
							//per il tasto undo
							temptable=$("#temp").html();
						}
					}
				}
				else{
					alert("Incompatible containers. Destination container type cannot contain container you moved");
					REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
				}
			}
			else{
				alert("Incompatible containers. Aliquot type they can contain is not the same.");
				REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
			}
		}
		else{
			alert("Unable to move: destination container is not available.");
			REDIPS.drag.source_cell.appendChild(REDIPS.drag.obj);
		}
	}
	else{
		if(aliq){
			var quant="0";			
		}
		else{
			var quant="X";
		}
		
		partenza.classList.remove("mark");
		var idobj=REDIPS.drag.obj.getAttribute("id");
		//cancello l'id del div messo nel temp, per evitare sovrapposizioni
		REDIPS.drag.obj.setAttribute("id","");
		//nella cella di partenza devo fare questo solo se non c'e' niente altro, altrimenti non tocco niente
		var figlipartenza=partenza.childNodes;
		var conta=0;
		for(var i=0;i<figlipartenza.length;i++){
			var tag=$(figlipartenza[i]).prop("tagName");
			if((tag=="DIV")||(tag=="BUTTON")){
				conta+=1;
				break
			}
		}
		if(conta==0){
			//imposto nel nuovo button il giusto valore di righe e colonne
			var colvecchia=REDIPS.drag.obj.getAttribute("col");
			var rigavecchia=REDIPS.drag.obj.getAttribute("row");
			var idnuovo=partenza.getAttribute("id");
			var pos=idnuovo.split("-")[1];
			partenza.innerHTML="<button align='center' id='r-"+pos+"' col='"+colvecchia+"' row='"+rigavecchia+"' type='submit' class='disp' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>"+quant+"</button>";
		}
		
		var bar=REDIPS.drag.obj.getAttribute("barcode");		
		var htmlsorg=REDIPS.drag.obj.outerHTML;
		var idcellasorg=REDIPS.drag.source_cell.getAttribute("id");
		
		if(sovrascrivi){
			prepara_per_undo(mapp_agg_tmp,mapp_tolti_tmp,dizrigh_tmp,dizgentemp,piassorgtmp,piasdesttmp,canctab,bar,tipaltemp,cont_sorg,cont_dest);
		}
		aggiorna_mappe_cont(barcodesorg,bar,mult,padre,null,null,idcellasorg,htmlsorg,padredest);
		temptable=$("#temp").html();
	}
}

function prepara_per_undo(mapp_agg_tm,mapp_tolti_tmp,dizrigh_tmp,dizgentemp,piassorgtmp,piasdesttmp,canctab,bar,tipaltemp,barcodesorg,barcodedest){
	//alert(Object.keys(mapp_tolti_tmp))
	dizundo["mapp_agg_tmp"]=$.extend(true,{},mapp_agg_tm);
	dizundo["mapp_tolti_tmp"]=$.extend(true,{},mapp_tolti_tmp);
	dizundo["dizrigh_tmp"]=$.extend(true,{},dizrigh_tmp);
	dizundo["dizgentemp"]=$.extend(true,{},dizgentemp);
	dizundo["piassorgtmp"]=piassorgtmp;
	dizundo["piasdesttmp"]=piasdesttmp;
	dizundo["barcsorg"]=barcodesorg;
	dizundo["barcdest"]=barcodedest;
	dizundo["temptable"]=temptable;
	dizundo["canctab"]=canctab;
	dizundo["bar"]=bar;
	dizundo["tipaltemp"]=tipaltemp;
}

//per cancellare l'ultima azione fatta
function undo(){
	if (Object.keys(dizundo).length!=0){		
		mappa_aggiunti=$.extend(true,{},dizundo["mapp_agg_tmp"]);
		mappa_tolti=$.extend(true,{},dizundo["mapp_tolti_tmp"]);
		dati_server=$.extend(true,{},dizundo["dizgentemp"]);
		
		var barcsorg=dizundo["barcsorg"];
		if(barcsorg==cont_sorg){
			var piassorghtml=dizundo["piassorgtmp"];
			$("#operativa table").html(piassorghtml);
			if(cont_sorg!=""){
				carica_piastra_operativa_effettiva(cont_sorg,modo_sorg,false,false);
			}
		}
		var barcdest=dizundo["barcdest"];
		if(barcdest==cont_dest){
			var piasdesthtml=dizundo["piasdesttmp"];
			$("#freezer table").html(piasdesthtml);
			if(cont_dest!=""){
				carica_piastra_stored_effettiva(cont_dest,modo_dest,false);
			}
		}
		var temptablehtml=dizundo["temptable"];
		$("#temp").html(temptablehtml);
		$("#temp td").attr("width","28px");
		$("#temp td").attr("height","30px");
		// reference to the REDIPS.drag library
	    var rd = REDIPS.drag;
	    // initialization
	    rd.init();
	    rd.hover.color_td = '#E7C7B2';
	    rd.drop_option = 'multiple';
	    rd.shift_option = 'vertical2';
	    rd.animation_shift = true;
	    rd.animation_pause = 20;
	    rd.myhandler_dropped = invia_dati;
	    rd.myhandler_moved = cella_partenza;
	    temptable=temptablehtml;
		//mi occupo della tabella di sotto
		var canctab=dizundo["canctab"];
		var barc=dizundo["bar"];
		//se ho cancellato, allora devo aggiungere
		if(canctab){
			var tipoaliq=dizundo["tipaltemp"];
			aggiungi_in_tabella([barc], tipoaliq);
		}
		else{
			canc_da_tabella([barc]);		
		}
		diz_righe_tolte=$.extend(true,{},dizundo["dizrigh_tmp"]);
	}
}

function zoom_piu_sorg(){
	if(tasto_sel_sorg==""){
		alert("Please select a button in source container");
	}
	else{		
		var div=evidenzia("operativa", tasto_sel_sorg);
		var classealiq=$(div).attr("class");
		var figli=$(div).text();
		//Tramite la classe associata, vedo se il tasto cliccato come base per lo zoom e' un'aliquota.
		//Se si' blocco lo zoom
		//devo anche controllare che il campione non contenga piu' aliquote. In tal caso devo lasciar fare lo zoom
		if((classealiq.indexOf("aliqclass")>-1)&&(figli=="1")){			
			alert("You are in a leaf node");
		}
		else{
			if(classealiq.indexOf("foglia")>-1){			
				alert("You are in a leaf node");
			}
			else{
				if((figli=="1")||(figli=="#")||(figli=="0")){
					tipospost="simple";
				}
				else{
					//se sto trattando aliquote
					if (classealiq.indexOf("aliqclass")>-1){
						tipospost="aliquot";
						tasto_sel_sorg=$(div).attr("gen");
					}
					//sto trattando dei cont con dentro altri cont nella stessa posizone 
					else{
						tipospost="list";
					}
				}	
				carica_piastra_operativa_effettiva(tasto_sel_sorg,"children",false,true);
			}
		}
		tasto_sel_sorg="";
		selected_phase = "-";
		flag = "-";
		selected_plate = "-";
		bi = "-";
		bf = "-";
	}
}

function zoom_meno_sorg(){
	var ff=$("#operativa table").attr("leaf");
	foglia_sorg="";
	if (ff!=undefined){
		foglia_sorg="present";
	}
	//devo prendere il padre, che si trova nell'intestazione della tabella, del cont attualmente visualizzato
	var codpadre=$("#operativa table").attr("father");
	if(codpadre==""){
		//se non c'e' un padre puo' pero' voler dire che devo visualizzare il cont stesso in visualizzazione itself
		if((modo_sorg=="children")){
			modo_sorg="itself";
			tipospost="simple";
			carica_piastra_operativa_effettiva(cont_sorg,modo_sorg,true,true);
		}
		else if(modo_sorg=="itself"){
			alert("Container visualized has not a father to show");
		}
	}
	else{
		//devo trattare il caso in cui il padre e' una lista di cont. Vedi lista di 
		//blocchetti di paraffina
		var multiplo=$("#operativa table").attr("multiplo");
		if((multiplo!="")&&(multiplo!=undefined)){
			tipospost="list";
		}
		else{
			if(tipospost=="aliquot"){
				tipospost="simple";
			}
		}
		var mod="children";
		var codtemp=codpadre;
		//codice del cont attualmente visualizzato, che non e' il cont_sorg, ma il barcode che compare nel th della tabella
		var codattuale=$("#operativa table").attr("barcode");
		if((modo_sorg=="itself")&&(codattuale.toLowerCase()==codpadre.toLowerCase())){
			mod="itself";
		}
		cont_sorg=codattuale;
		carica_piastra_operativa_effettiva(codtemp,mod,true,true);
	}
}

function zoom_piu_dest(){
	if(tasto_sel_dest==""){
		alert("Please select a button in destination container");
	}
	else{		
		var div=evidenzia("freezer", tasto_sel_dest);
		var classealiq=$(div).attr("class");
		var figli=$(div).text();
		//Tramite la classe associata, vedo se il tasto cliccato come base per lo zoom e' un'aliquota.
		//Se si' blocco lo zoom
		//Non l'ha trovata
		if((classealiq.indexOf("aliqclass")>-1)&&(figli=="1")){
			alert("You are in a leaf node");
		}
		else{
			if(classealiq.indexOf("foglia")>-1){			
				alert("You are in a leaf node");
			}
			else{
				if((figli=="1")||(figli=="#")||(figli=="0")){
					tipospost_dest="simple";				
				}
				else{
					tipospost_dest="list";
				}
				//se sto trattando aliquote
				if (classealiq.indexOf("aliqclass")>-1){
					tipospost_dest="aliquot";
					tasto_sel_dest=$(div).attr("gen");
				}
				carica_piastra_stored_effettiva(tasto_sel_dest,"children",false);
			}
		}
		tasto_sel_dest="";
		selected_phase = "-";
		flag = "-";
		selected_plate = "-";
		bi = "-";
		bf = "-";
	}
}

function zoom_meno_dest(){
	var ff=$("#freezer table").attr("leaf");
	foglia_dest="";
	if (ff!=undefined){
		foglia_dest="present";
	}
	//devo prendere il padre, che si trova nell'intestazione della tabella, del cont attualmente visualizzato
	var codpadre=$("#freezer table").attr("father");
	if(codpadre==""){
		//se non c'e' un padre puo' pero' voler dire che devo visualizzare il cont stesso in visualizzazione itself
		if(modo_dest=="children"){
			modo_dest="itself";
			tipospost_dest="simple";
			carica_piastra_stored_effettiva(cont_dest,modo_dest,true);					
		}
		else if(modo_dest=="itself"){
			alert("Container visualized has not a father to show");
		}
	}
	else{
		//devo trattare il caso in cui il padre e' una lista di cont. Vedi lista di 
		//blocchetti di paraffina
		var multiplo=$("#freezer table").attr("multiplo");
		if((multiplo!="")&&(multiplo!=undefined)){
			tipospost_dest="list";
		}
		else{
			if(tipospost_dest=="aliquot"){
				tipospost_dest="simple";
			}
		}
		//codice del cont attualmente visualizzato, che non e' il cont_sorg, ma il barcode che compare nel th della tabella
		var codattuale=$("#freezer table").attr("barcode");
		cont_dest=codattuale;
		var mod="children";
		if((modo_dest=="itself")&&(codattuale.toLowerCase()==codpadre.toLowerCase())){
			mod="itself";
		}
		carica_piastra_stored_effettiva(codpadre,mod,true);		
	}
}

function canc_cont_dest(){
	errore_piastra("freezer");
	cont_dest="";
	$("#barcode_freezer").val("");
	$("#freezer table").attr("barcode","");
}

function carica_lista_provette(){
	//prendo il tipo di aliquota che devo caricare
	var tipo=$("#id_tipi option:selected").val();
	if(tipo in vettore_posiz){
		popola_tabella(vettore_posiz[tipo]);
		tipoaliqvisualiz=tipo;
	}
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		var url=base_url+"/api/freecontainer/"+tipo+"/";
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				popola_tabella(d.data);
				vettore_posiz[tipo]=d.data;
				tipoaliqvisualiz=tipo;
			}
			clearTimeout(timer);
	    	$("body").removeClass("loading");
		});
	}
}

function popola_tabella(diz){
	$("#fieldtabella").css("display","");
	$("#tab_riass").dataTable({
		"bDestroy": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });
	//$("#tab_riass_wrapper").css("width","77%");
	//cancello tutte le righe della tabella
	var oSettings = $("#tab_riass").dataTable().fnSettings();
	var iTotalRecords = oSettings.fnRecordsTotal();
	for (var i=0;i<=iTotalRecords;i++) {
		$("#tab_riass").dataTable().fnDeleteRow(0,null,true);
	}
	//ho il dizionario con gen:{barcode,data,operatore}
	var j=1;
	for(var key in diz){
		var barcode=diz[key]['barcode'];
		var operatore=diz[key]['operator'];
    	var data=diz[key]['data'];
		//metto quel cont nel data table solo se non l'ho gia' posizionato
		if (!(barcode in diz_righe_tolte)){	    	
	    	$("#tab_riass").dataTable().fnAddData( [j, key, barcode,operatore,data] );
	    	j++;
		}
		else{
			//se c'e' nel diz puo' essere stato posizionato quando ancora non era stata caricata la data table, quindi devo riempire
			//la lista che avevo lasciato vuota
			var lis=diz_righe_tolte[barcode];
			if(lis.length==0){
				lis.push(String(j));
				lis.push(key);
				lis.push(barcode);
				lis.push(operatore);
				lis.push(data);
				diz_righe_tolte[barcode]=lis;
			}
		}
	}
}

//nel caso in cui posiziono un cont devo cancellare la riga dal data table
function canc_da_tabella(lisbarc){
	//cancello dalla tabella riassuntiva i pezzi posizionati solo se e' visibile
	if (($("#fieldtabella").css("display"))!="none"){
		var tab=$("#tab_riass").dataTable();
		//prendo il valore del barcode per il pezzo posizionato
		var lista=tab.$("tr").children(":nth-child(3)");
		var k=1;
		var nodes = tab.$("tr");
		for(var j=0;j<lisbarc.length;j++){
			var trovato=false;
			for(var i=0;i<lista.length;i++){
				var barcode=$(lista[i]).text();
				//se il barcode coincide, allora devo togliere la riga
				if (barcode==lisbarc[j]){
					var listd=$(nodes[i]).children();
					var listadatitemp=[];
					for(var ii=0;ii<listd.length;ii++){
						var figlio=":nth-child("+(ii+1)+")";
						var dato=$(nodes[i]).children(figlio).html();
						listadatitemp.push(dato);
					}																					
					diz_righe_tolte[barcode]=listadatitemp;
					tab.fnDeleteRow(nodes[i]);
					trovato=true;
					break;
				}
			}			
			if(!trovato){
				//se non sto vedendo la data table per quel tipo di aliq, devo comunque inserire la chiave nel diz
				diz_righe_tolte[lisbarc[j]]=[];
			}
		}
		var listab=tab.$("tr");
		for(i=0;i<listab.length;i++){
			//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
    		tab.fnUpdate(k,i,0);
			k=k+1;
		}
	}
	//se non e' ancora stata caricata la data table metto comunque nel diz il fatto che quel cont
	//e' stato posizionato cosi' da non scriverlo quando verra' caricata la data table
	else{
		for(var j=0;j<lisbarc.length;j++){
			diz_righe_tolte[lisbarc[j]]=[];
		}
	}
}

//nel caso in cui elimino il posizionamento di un cont devo far riapparire la riga nel data table
function aggiungi_in_tabella(lisbarc,tipoaliq){
	if (($("#fieldtabella").css("display"))!="none"){
		if(tipoaliqvisualiz==tipoaliq){
			var tab=$("#tab_riass").dataTable();
			var k=1;
			var nodes = tab.$("tr");		
			for(var j=0;j<lisbarc.length;j++){
				if(lisbarc[j] in diz_righe_tolte){
					var listadatitemp=diz_righe_tolte[lisbarc[j]];
					//comunico alla funzione il numero di riga in cui si trova il pezzo
					tab.fnAddData(listadatitemp);
				}
			}
			var lista=tab.$("tr").children(":nth-child(3)");
			for(i=0;i<lista.length;i++){
				tab.fnUpdate(k,i,0);
				k=k+1;
			}
		}
	}
	//in ogni caso cancello la chiave dal diz
	for(var z=0;z<lisbarc.length;z++){
		delete diz_righe_tolte[lisbarc[z]];
	}
}

function esegui_post(cont){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	var data = {
		salva:true,
		dati:JSON.stringify(dati_server),
		contcanc:cont
    };
	var url=base_url+"/archive/";
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

$(document).ready(function () {
	inizio();
	temptable=$("#temp").html();
	$("#load_sorg").click(carica_operativa);
	$("#load_dest").click(carica_stored);
	$("#select").click(function() {
		  select_container();
	});
	$("#esegui_batch").click(batch_aliquot);
	$("#undo").click(undo);
	$("#sorgpiu").click(zoom_piu_sorg);
	$("#sorgmeno").click(zoom_meno_sorg);
	$("#destpiu").click(zoom_piu_dest);
	$("#destmeno").click(zoom_meno_dest);
	$("#delete_plate").click(canc_cont_dest);
	$("#l_aliquote").click(carica_lista_provette);
	
	$("#barcode_operative").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_operativa();
		}
	});
	
	$("#barcode_freezer").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_stored();
		}
	});
	
	$("#temp td").attr("width","28px");
	$("#temp td").attr("height","30px");
	
	$("#conf_all").click(function(event){
		event.preventDefault();
		//se la piastra e' costar ed e' piu' grande di 1x1, allora chiedo se si vuole cancellare tutto
		var costar=$("#operativa table").attr("costar");
		var colcont=$("#operativa table").attr("col");
		var rowcont=$("#operativa table").attr("row");
		if((costar=="True")&&(colcont!="1")&&(rowcont!="1")){
			//conto le aliquote che rimangono nella piastra operativa
			var listaaliq=$("#operativa table div.drag");
			var conta_aliquote=listaaliq.length;
			if(conta_aliquote!=0){
				$( "#dialog-confirm" ).dialog({
					resizable: false,
					height:140,
					modal: true,
					buttons: {
						"Yes": function() {
							$( this ).dialog( "close" );
							$( "#dialog-last" ).dialog({
								resizable: false,
								height:140,
								modal: true,
								buttons: {
									"Yes": function() {
										$( this ).dialog( "close" );
										esegui_post(cont_sorg);
									},
									"No": function() {
										$( this ).dialog( "close" );
									}
								}	
							});
						},
						"No": function() {							
							$( this ).dialog( "close" );
							esegui_post(null);
						}
					}
				});		
			}
			else{
				esegui_post(null);
			}
		}
		else{
			esegui_post(null);
		}
	});
});