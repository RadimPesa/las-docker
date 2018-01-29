op=false;
fr=false;
mappa=new Object();
drag=false;

function inizio(){
	sezionigen=$("section");
	//tolgo la vecchia intestazione alle tabelle
	$("#operativa table tr:first,#freezer table tr:first").remove();
	//agisco sul titolo della pagina solo se sono nella seconda schermata
	var lista=$("#drag");
	if (lista.length!=0){
		tipo=$("#tipo").val();
		
		$("#cont_h1").css("padding-bottom","10px");
	}
	$("#freezer table td").attr("class","mark");
	$("#operativa table button,#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
	
}

function batch(){
	var errore=false;
	if((fr==true)&&(op==true)){
		var barcode_dest=$("#barcode_freezer").val();
		var barcode_sorg=$("#barcode_operative").val();
		//t e' il tipo: RL o SF
		var aliquote=$("#operativa table div.drag");
		var stringa="";
		for(i=0;i<aliquote.length;i++){
			var al=$(aliquote[i]).attr("id");
			s=al.split("-");
			stringa+=s[1]+"_";
		}
		var nobatch=false;
		url=base_url+"/api/aliquot/"+barcode_dest+"/"+stringa;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if(d.data==true){
					alert("Unable to execute batch mode.");
				}
				else{
					//devo vedere se qualche posto e' gia' occupato da una provetta
					//messa li' con il drag and drop
					for(i=0;i<aliquote.length;i++){
						var al=$(aliquote[i]).attr("id");
						var posto=al.split("-")[1];
						//se il figlio della cella e' un button, allora il posto e'
						//libero, se e' una div no
						var conta=$("#m-"+posto).children().get(0);
						if((conta==undefined)||(conta.tagName=="DIV")){
							nobatch=true;
							break;
						}
					}
					if(nobatch==false){
						for(i=0;i<aliquote.length;i++){
							var al=$(aliquote[i]).attr("id");
							s=al.split("-");
							//prendo la cella della tabella						
							var tastodest="#m-"+s[1];
							//solo se il tasto non ha l'attributo barcode vuol dire che
							//c'e' un posto vuoto e allora posso mettere le altre provette
							if (($(tastodest).children().attr("barcode"))){
								errore=true;
								alert("Unable to execute batch mode.");
								break;
							}
						}
						if(errore==false){
							for(i=0;i<aliquote.length;i++){
								var al=$(aliquote[i]).attr("id");
								var num=$(aliquote[i]).attr("num");
								var bar=$(aliquote[i]).attr("barcode");
								var geneal=$(aliquote[i]).attr("gen");
								var pezzi=$(aliquote[i]).text();
								s=al.split("-");
								//prendo la cella della tabella						
								var tastodest="#m-"+s[1];
								var pezzi=$(aliquote[i]).text();
								$(tastodest).children().remove();
								var idt="#"+al;
								$(tastodest).append($(idt));
								$(tastodest).attr("class","mark");
								$(tastodest).children().attr("onclick","move(this,\"bot\")");
								
								var vett_stored=mappa[barcode_dest];
								vett_stored[bar]=s[1]+"|"+barcode_dest+"|"+bar+"|"+geneal+"|"+pezzi+"|"+al;
								mappa[barcode_dest]=vett_stored;
								
								var vett_op=mappa[barcode_sorg];
								vett_op[num]=num+"|"+barcode_sorg;
								mappa[barcode_sorg]=vett_op;
								
							}
							var data = {
						    		batch:true,
						    		str:stringa,
						    		barcodesorg:$("#barcode_operative").val(),
						    		barcodedest:$("#barcode_freezer").val(),
						    };
							var url=base_url+"/move/save/";
							$.post(url, data, function (result) {
			
						    	if (result == "failure") {
						    		alert("Error");
						    	}
						    });
							$("#p_confirm").attr("disabled",false);
							conta_aliquote=0;
						}						
					}
					else{
						alert("Unable to execute batch mode.");
					}
				}
			}
		});
	}
	else{
		alert("First you have to load the containers");
	}
}

function carica_operativa_scelta(){
	var codice=$(this).text().trim();
	var cod_op=$("#barcode_freezer").val();
	//devo vedere se quella piastra c'e' gia' nella lista o no
	var listapias=$("#listapias2 td");
	var trovato=false;
	for(i=0;i<listapias.length;i++){
		var cod=$(listapias[i]).text().trim();
		if (codice==cod){
			trovato=true;		
		}
	}
	if(((cod_op!=undefined)&&(cod_op==codice))||(trovato==true)){
		alert("You can't have same barcode for the two containers");
		$("#operativa table div").replaceWith("<button>0</button>");
		$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
		$("#operativa table button").css("background-color","rgb(249,248,242)");
		op=false;
	}
	else{
		$("#barcode_operative").attr("value",codice);
		carica_piastra_operativa_effettiva(codice);
	}
}

function carica_operativa(){
	var cod_op=$("#barcode_freezer").val();
	if ($("#barcode_operative").val() == "")
		alert("Insert barcode in source container");
	else{
		var codice=$("#barcode_operative").val();
		//devo vedere se quella piastra c'e' gia' nella lista o no
		var listapias=$("#listapias2 td");
		var trovato=false;
		for(i=0;i<listapias.length;i++){
			var cod=$(listapias[i]).text().trim();
			if (codice==cod){
				trovato=true;		
			}
		}
		if(((cod_op!=undefined)&&(cod_op==codice))||(trovato==true)){
			alert("You can't have same barcode for the two containers");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else{
			carica_piastra_operativa_effettiva(codice);
		}
	}
}

function carica_piastra_operativa_effettiva(codice){
	tipo=$("#tipo").val();
	var una=$("#modo").attr("value");
	var cod_stored=$("#barcode_freezer").val();
	if ((cod_stored=="")||(cod_stored==undefined)){
		url=base_url+"/api/move/"+codice+"/"+tipo+"/"+codice+"/";
	}
	else{
		url=base_url+"/api/move/"+codice+"/"+tipo+"/"+cod_stored+"/stored";
	}
	$.getJSON(url,function(d){
		if(d.data=="errore"){
			alert("Container doesn't exist");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else if(d.data=="err_tipo"){
			alert("Container is not of type you chose");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else if(d.data=="err_destination"){
			alert("Destination container can't support container type of source container");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else if(d.data=="errore_banca"){
			alert("Error while connecting with biobank");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else if(d.data=="errore_store"){
			alert("Error. Probably there is a space in barcode");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else{
			$("#plate_operative").children().replaceWith(d.data);
			//metto nel titolo della piastra anche lo scopo della piastra
			var titolo=$("#plate_operative table th").text();
			var sc=d.scopo;
			if (sc=="Operative"){
				sc="Working";
			}
			if(sc=="Stored"){
				sc="Archive";
			}
			var nuovo_tit=titolo+" "+sc.toUpperCase();
			$("#plate_operative table th").text(nuovo_tit);
			if(una=="True"){
				var listastore=$("#operativa table button");
				for(i=0;i<listastore.length;i++){
					var idoriginale=$(listastore[i]).attr("id");
					var ids=idoriginale.split("-");
					//$(listastore[i]).removeAttr("id");
					var idfinale="a-"+ids[1];
					$(listastore[i]).parent().attr("id",idfinale);
				}
			}
			$("#operativa table button[sel=\"s\"]").attr("disabled",false);
			$("#operativa table button[sel=\"s\"]").css("background-color","gray");
			//attributi per lo spostamento multiplo
			$("#operativa table button").attr("assign","-");
			$("#operativa table button").attr("prev","plateButtonOFF");
			
			$("#operativa table button").attr("c","plateButtonOFF");
			//mi occupo del tooltip per il genid
			listabutton=$("#operativa table button[sel=\"s\"]");
			
			if (una=="True"){
				var click="bot";
			}
			else{
				var click="top"
			}
			$("#operativa table button").attr("onclick","move(this,\""+click+"\")");
			
			for(i=0;i<listabutton.length;i++){
				var gen=$(listabutton[i]).attr("gen");
				var barcc=$(listabutton[i]).attr("barcode");
				var fr="tooltip.show(\""+gen+" Barcode: "+barcc+"\")";
				$(listabutton[i]).attr("onmouseover",fr);
				var id=$(listabutton[i]).attr("id");
				var barc=$(listabutton[i]).attr("barcode");
				
				$(listabutton[i]).replaceWith("<div class=\'drag\' align='center' id='"+id+"' num='"+i+"' onmouseover='"+fr+"' onmouseout='tooltip.hide();' gen='"+gen+"' barcode='"+barc+"'  assign='"+barc+"' prev='plateButtonOFF' c='plateButtonOFF' onclick='move(this,\""+click+"\")'>" + listabutton[i].innerHTML + "</div>");
			}
			//metto classe=mark nelle celle in cui non voglio che venga
			//posizionato un tasto con il drag and drop
			$("#operativa th,.intest").attr("class","mark");
			//prendo i parent dei button cioe' i td
			$("#operativa table button,#operativa .drag").parent().attr("class","mark");
			
			//se sto muovendo le provette all'interno della stessa piastra
			if(una=="True"){
				$("#operativa table button").not("[barcode]").parent().removeAttr("class");
				$("#operativa table button").attr("disabled",true);
				$("#operativa table button").not("[barcode]").attr("disabled",false);
			}
			
			//assegno una larghezza fissa alle celle della tabella per fare in
			//modo che durante lo spostamento le colonne rimaste vuote
			//non si rimpiccioliscano
			$("#operativa table td").not(":first-child").attr("width","35px");
			$("#operativa table td").not(":first-child").attr("height","38px");
			//tolgo l'attributo dell'altezza alla prima riga della tabella
			//quella con l'intestazione delle colonne
			$("#operativa table tr:nth-child(2) td").removeAttr("height");
			
			//faccio vedere la tabella con il riepilogo delle piastre
	        $("#listapias1").css("display","");
			var vettore=new Array();
			//aggiorno la mappa inserendo un vettore nella posizione che corrisponde
			//al codice della piastra. Lo faccio solo se non c'e' gia'
			if (mappa[codice]==undefined)
				mappa[codice]=vettore;
			else{
				var vettore_posiz=mappa[codice];
		    	//vedo se in quella piastra avevo gia' tolto qualcosa prima e lo
		    	//tolgo dalla piastra
		    	for(i=0;i<vettore_posiz.length;i++){
		    		if(vettore_posiz[i]!=undefined){
		    			var valore=vettore_posiz[i];
		    			valore=valore.split("|");
		    			//solo se la piastra a cui si riferisce l'aliq e' questa
		    			if (valore[1]==codice){		
		    				if(una=="True"){
		    					//per rimpiazzare i posti vuoti con altri tasti con la X
		    					$("#operativa [num="+valore[0]+"]").replaceWith("<button assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>X</button>");
		    					$("#a-"+valore[5]).children().replaceWith("<div id="+valore[6]+" class='drag' num='"+i+"' align='center' gen='"+valore[3]+"' barcode='"+valore[2]+"' onmouseover='tooltip.show(\""+valore[3]+" Barcode: "+valore[2]+"\");' onmouseout='tooltip.hide();'  assign='"+valore[2]+"' prev='plateButtonOFF' c='plateButtonOFF' onclick='move(this,\"bot\")'>"+valore[4]+"</div>");
		    				}
		    				else{
		    					//per lasciare i posti vuoti nella piastra operativa
		    					$("#operativa [num="+valore[0]+"]").remove();
		    				}
		    			}
		    		}
		    	}
			}
			
			//devo vedere se quel container c'e' gia' nella lista o no
			var listapias=$("#listapias1 td");
			var trovato=false;
			for(i=0;i<listapias.length;i++){
				var cod=$(listapias[i]).text().trim();
				if (codice==cod){
					trovato=true;		
				}
			}
			if (trovato==false){
				var tabella = document.getElementById("listapias1");
				//prendo il numero di righe della tabella
				var rowCount = tabella.rows.length;
				var row = tabella.insertRow(rowCount);
				//per centrare la td
				row.align="center";
				//inserisco la cella con dentro il numero d'ordine
			    var cell1 = row.insertCell(0);
			    cell1.innerHTML =codice;  
			    if(tipo=="VT"){
				    cell1.style.borderStyle="none";
				    cell1.style.borderRight="4px";
				    cell1.style.fontSize="1.3em";
				    cell1.style.padding="6px";
			    }
			    $("#listapias1 td:last").click(carica_operativa_scelta);
			}
			// reference to the REDIPS.drag library
		    var rd = REDIPS.drag;
		    // initialization
		    rd.init();
		    // set hover color
		    rd.hover.color_td = '#E7C7B2';
		    // set drop option to 'shift'
		    //rd.drop_option = 'shift';
		    rd.drop_option = 'overwrite';
		    // set shift mode to vertical2
		    rd.shift_option = 'vertical2';
		    // enable animation on shifted elements
		    rd.animation_shift = true;
		    // set animation loop pause
		    rd.animation_pause = 20;
		    if(una=="True"){
		    	rd.myhandler_dropped = invia_dati;
		    	//rd.myhandler_moved = cella_partenza;
		    }
		    op=true;
		}
	});
}

function carica_stored_scelta(){
	var codice=$(this).text().trim();
	var cod_op=$("#barcode_operative").val();
	//devo vedere se quella piastra c'e' gia' nella lista o no
	var listapias=$("#listapias1 td");
	var trovato=false;
	for(i=0;i<listapias.length;i++){
		var cod=$(listapias[i]).text().trim();
		if (codice==cod){
			trovato=true;		
		}
	}
	if(((cod_op!=undefined)&&(cod_op==codice))||(trovato==true)){
		alert("You can't have same barcode for the two containers");
		$("#freezer table div").replaceWith("<button>0</button>");
		$("#freezer table td").attr("class","mark");
		$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
		$("#freezer table button").css("background-color","rgb(249,248,242)");
		fr=false;
	}
	else{
		carica_piastra_stored_effettiva(codice);
		$("#barcode_freezer").attr("value",codice);
	}
}

function carica_stored(){
	var cod_op=$("#barcode_operative").val();
	if ($("#barcode_freezer").val() == "")
		alert("Insert barcode in destination container");
	else{
		var codice=$("#barcode_freezer").val();
		//devo vedere se quella piastra c'e' gia' nella lista o no
		var listapias=$("#listapias1 td");
		var trovato=false;
		for(i=0;i<listapias.length;i++){
			var cod=$(listapias[i]).text().trim();
			if (codice==cod){
				trovato=true;		
			}
		}
		if(((cod_op!=undefined)&&(cod_op==codice))||(trovato==true)){
			alert("You can't have same barcode for the two containers");
			$("#freezer table div").replaceWith("<button>0</button>");
			$("#freezer table td").attr("class","mark");
			$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#freezer table button").css("background-color","rgb(249,248,242)");
			fr=false;
		}
		else{
			carica_piastra_stored_effettiva(codice);
		}
	}
}

function carica_piastra_stored_effettiva(codice){
	if ($("#barcode_operative").val() == "")
		alert("Insert barcode in source container");
	else{
		var sorg=$("#barcode_operative").val();
		url=base_url+"/api/move/"+codice+"/"+tipo+"/"+sorg+"/stored";
		//url=base_url+"/api/geometry/create/16";
		$.getJSON(url,function(d){
			if(d.data=="errore"){
				alert("Container doesn't exist");
				$("#freezer table div").replaceWith("<button>0</button>");
				$("#freezer table td").attr("class","mark");
				$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
				$("#freezer table button").css("background-color","rgb(249,248,242)");
				fr=false;
			}
			else if(d.data=="err_tipo"){
				alert("Container is not of type you chose");
				$("#freezer table div").replaceWith("<button>0</button>");
				$("#freezer table td").attr("class","mark");
				$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
				$("#freezer table button").css("background-color","rgb(249,248,242)");
				fr=false;
			}
			else if(d.data=="err_destination"){
				alert("Destination container can't support container type of source container");
				$("#freezer table div").replaceWith("<button>0</button>");
				$("#freezer table td").attr("class","mark");
				$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
				$("#freezer table button").css("background-color","rgb(249,248,242)");
				fr=false;
			}
			else if(d.data=="errore_banca"){
				alert("Error while connecting with biobank");
				$("#freezer table div").replaceWith("<button>0</button>");
				$("#freezer table td").attr("class","mark");
				$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
				$("#freezer table button").css("background-color","rgb(249,248,242)");
				fr=false;
			}
			else if(d.data=="errore_store"){
				alert("Error. Probably there is a space in barcode");
				$("#freezer table div").replaceWith("<button>0</button>");
				$("#freezer table td").attr("class","mark");
				$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
				$("#freezer table button").css("background-color","rgb(249,248,242)");
				fr=false;
			}
			else{
				$("#plate_stored").children().replaceWith(d.data);
				//metto nel titolo della piastra anche lo scopo della piastra
				var titolo=$("#plate_stored table th").text();
				var sc=d.scopo;
				if (sc=="Operative"){
					sc="Working";
				}
				if(sc=="Stored"){
					sc="Archive";
				}
				var nuovo_tit=titolo+" "+sc.toUpperCase();
				$("#plate_stored table th").text(nuovo_tit);
				//cambio gli id in modo che siano univoci
				var listastore=$("#freezer table button");
				for(i=0;i<listastore.length;i++){
					var idoriginale=$(listastore[i]).attr("id");
					var ids=idoriginale.split("-");
					$(listastore[i]).removeAttr("id");
					var idfinale="m-"+ids[1];
					$(listastore[i]).parent().attr("id",idfinale);
				}
				
				//attributi per lo spostamento multiplo
				$("#freezer table button").attr("assign","-");
				$("#freezer table button").attr("prev","plateButtonOFF");
				$("#freezer table button").attr("onclick","move(this,\"bot\")");
				$("#freezer table button").attr("c","plateButtonOFF");
				
				$("#freezer table button[sel!=\"s\"]").attr("disabled",false);
				$("#freezer table button[barcode]").attr("disabled",true);
				//prendo i parent dei button cioe' i td
				$("#freezer table button[sel=\"s\"]").parent().attr("class","mark");
				//prendo i button che hanno l'attributo barcode
				$("#freezer table button[barcode]").parent().attr("class","mark");
				
				//metto classe=mark nelle celle in cui non voglio che venga
				//posizionato un tasto con il drag and drop
				$("#freezer th,.intest").attr("class","mark");
				
				//serve per lo spostamento multiplo
				$("#freezer table button[barcode]").attr("assign","pieno");
				
				//faccio vedere la tabella con il riepilogo delle piastre
		        $("#listapias2").css("display","");
				var vettore=new Array();
				//aggiorno la mappa inserendo un vettore nella posizione che corrisponde
				//al codice della piastra. Lo faccio solo se non c'e' gia'
				if (mappa[codice]==undefined)
					mappa[codice]=vettore;
				else{
					var vettore_posiz=mappa[codice];
			    	//vedo se in quella piastra avevo gia' messo qualcosa prima e lo
			    	//metto anche adesso
					for (var i in vettore_posiz){
		    			var valore=vettore_posiz[i];
		    			valore=valore.split("|");
		    			//solo se la piastra a cui si riferisce l'aliq e' questa
		    			if (valore[1]==codice){		
		    				$("#m-"+valore[0]).children().replaceWith("<div id='"+valore[5]+"' class='drag' num='"+i+"' align='center' gen='"+valore[3]+"' barcode='"+valore[2]+"' onmouseover='tooltip.show(\""+valore[3]+" Barcode: "+valore[2]+"\");' onmouseout='tooltip.hide();' assign='"+valore[2]+"' prev='plateButtonOFF' c='plateButtonOFF' onclick='move(this,\"bot\")'>"+valore[4]+"</div>");
		    				$("#m-"+valore[0]).attr("class","mark");
		    			}
			    	}
				}
				
				//devo vedere se quel container c'e' gia' nella lista o no
				var listapias=$("#listapias2 td");
				var trovato=false;
				for(i=0;i<listapias.length;i++){
					var cod=$(listapias[i]).text().trim();
					if (codice==cod){
						trovato=true;		
					}
				}
				if (trovato==false){
					var tabella = document.getElementById("listapias2");
					//prendo il numero di righe della tabella
					var rowCount = tabella.rows.length;
					var row = tabella.insertRow(rowCount);
					//per centrare la td
					row.align="center";
					//inserisco la cella con dentro il numero d'ordine
				    var cell1 = row.insertCell(0);
				    cell1.innerHTML =codice;   
				    $("#listapias2 td:last").click(carica_stored_scelta);
				}
				
				// reference to the REDIPS.drag library
			    var rd = REDIPS.drag;
			    // initialization
			    rd.init();
			    // set hover color
			    rd.hover.color_td = '#E7C7B2';
			    // set drop option to 'shift'
			    //rd.drop_option = 'shift';
			    rd.drop_option = 'overwrite';
			    // set shift mode to vertical2
			    rd.shift_option = 'vertical2';
			    // enable animation on shifted elements
			    rd.animation_shift = true;
			    // set animation loop pause
			    rd.animation_pause = 20;
			    rd.myhandler_dropped = invia_dati;
			    //rd.myhandler_moved = cella_partenza;
			    fr=true;
			    //metto l'evento per il drop
			    //$("#freezer table button").bind("drop",invia_dati);
			    //var tar= document.getElementById ("s-A1").parentNode;
			    //alert(tar);
			    //tar.addEventListener ("drag", invia_dati, false);
			}
		});
	}
}

function invia_dati(){
	drag=true;
	//metto class=mark nella td di dest cos� non posso mettere altri tasti li'
	REDIPS.drag.target_cell.className="mark";
	var una=$("#modo").attr("value");
	//ho l'id della cella di partenza da dove sono partito per fare il drag and drop
	var partenza=REDIPS.drag.source_cell;
	var idarrivo=REDIPS.drag.target_cell.id;
	//vado a vedere se la piastra padre del pulsante e' operativa o stored
	var piastra=partenza.parentNode.parentNode.parentNode.parentNode.id;
	if ((piastra=="plate_stored")&&(partenza.id!=idarrivo)){
		//tolgo il class=mark nella td di partenza solo se e' nella piastra stored
		partenza.removeAttribute("class");
		partenza.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>X</button>";
	}
	//se muovo le provette nella stessa piastra
	if((una=="True")&&(partenza.id!=idarrivo)){
		//tolgo il class=mark nella td di partenza solo se e' nella piastra stored
		partenza.removeAttribute("class");
		partenza.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>X</button>";
	}
	//vado a vedere se la piastra dest del pulsante e' operativa o stored
	var piastra_dest=REDIPS.drag.target_cell.parentNode.parentNode.parentNode.parentNode.id;
	//solo se la dest e' operativa faccio tutto il resto
	if((piastra_dest=="plate_stored")||(una=="True")){
		var barcode_dest=$("#barcode_freezer").val();
		var barcode_sorg=$("#barcode_operative").val();
		
		//abilito il tasto per confermare
		$("#p_confirm").attr("disabled",false);
		//mi da' l'id della div mossa
		var idpartenza=REDIPS.drag.target_cell.childNodes[0].id;
		var pospartenza=idpartenza.split("-");
		
		var posarrivo=idarrivo.split("-");
		var pezzi=REDIPS.drag.target_cell.childNodes[0].innerHTML;
		var bar=REDIPS.drag.target_cell.childNodes[0].getAttribute("barcode");
		var num=REDIPS.drag.target_cell.childNodes[0].getAttribute("num");
		var geneal=REDIPS.drag.target_cell.childNodes[0].getAttribute("gen");
		var id=REDIPS.drag.target_cell.childNodes[0].getAttribute("id");
		
		//reimposto allo stato iniziale il tasto per togliere il conflitto tra l'evento
		//on click e il drag and drop.
		var previous = REDIPS.drag.target_cell.childNodes[0].getAttribute("prev");
		REDIPS.drag.target_cell.childNodes[0].setAttribute("c", previous);
		REDIPS.drag.target_cell.childNodes[0].setAttribute("onclick", "move(this,\"bot\")");
		flag = "-";
		
		if(una!="True"){
			var vett_stored=mappa[barcode_dest];
			vett_stored[bar]=posarrivo[1]+"|"+barcode_dest+"|"+bar+"|"+geneal+"|"+pezzi+"|"+id;
			mappa[barcode_dest]=vett_stored;
			
			var vett_op=mappa[barcode_sorg];
			vett_op[num]=num+"|"+barcode_sorg;
			mappa[barcode_sorg]=vett_op;
		}
		else{
			var vett_op=mappa[barcode_sorg];
			vett_op[num]=num+"|"+barcode_sorg+"|"+bar+"|"+geneal+"|"+pezzi+"|"+posarrivo[1]+"|"+id;
			mappa[barcode_sorg]=vett_op;
			barcode_dest=barcode_sorg;
		}
		
		//riempio le variabili da trasmettere con la post
		var data = {
	    		carica:true,
	    		ti:tipo,
	    		barcode:bar,
	    		//parti:pezzi,
	    		pos:pospartenza[1],
	    		posnuova:posarrivo[1],
	    		barcodesorg:barcode_sorg,
	    		barcodedest:barcode_dest
	    };
		
		var url=base_url+"/move/save/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    });
	}
}

$(document).ready(function () {
	inizio();
		
	$("#load_operative_plate").click(carica_operativa);
	$("#load_freezer_plate").click(carica_stored);
	$("#esegui_batch").click(batch);
	
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
	
	/*$("#p_confirm").click(function(event){
		//conto le aliquote che rimangono nella piastra operativa
		var listaaliq=$("#operativa table div.drag");
		var conta_aliquote=listaaliq.length;
	});*/
});