op=false;
fr=false;
mappa=new Object();
drag=false;
tipo="";
tipooperativa=new Object();
tipoarchive=new Object();

function inizio(){
	//sezionigen=$("section");
	//tolgo la vecchia intestazione alle tabelle
	$("#operativa table tr:first,#freezer table tr:first").remove();
	//agisco sul titolo della pagina solo se sono nella seconda schermata
	/*var lista=$("#drag");
	if (lista.length!=0){
		
		if(tipo=="RL"){
			$("#cont_h1").text("You are storing RNALater aliquots");
		}
		else if(tipo=="SF"){
			$("#cont_h1").text("You are storing Snap Frozen aliquots");
		}
		else if((tipo=="VT")||(tipo=="TRANS")){
			$("#cont_h1").text("You are storing Viable aliquots");
		}
		else{
			$("#cont_h1").text("You are storing "+tipo+" aliquots");
		}
	}*/
	tipo=$("#tipo").val();
	$("#cont_h1").css("padding-bottom","0.8em");
	$("#freezer table td").attr("class","mark");
	$("#operativa table button,#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
	
}

function batch(){
	if((fr==true)&&(op==true)){
		//devo controllare che il tipo della piastra caricata sia coerente con quello dell'altra
		var trov=0;
		for (var i=0;i<tipoarchive.length;i++){
			for (var k=0;k<tipooperativa.length;k++){
				if (tipoarchive[i]==tipooperativa[k]){
					trov=1;
					break;
				}
			}
		}
		if (trov==1){
			var barcodedest=$("#barcode_freezer").val();
			var barcodesorg=$("#barcode_operative").val();
			//t e' il tipo: RL o SF
			var aliquote=$("#operativa table div.drag");
			var stringa="";
			for(i=0;i<aliquote.length;i++){
				var al=$(aliquote[i]).attr("id");
				s=al.split("-");
				stringa+=s[1]+"_";
			}
			var nobatch=false;
			url=base_url+"/api/aliquot/"+barcodedest+"/"+stringa;
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
							if(conta.tagName=="DIV"){
								nobatch=true;
								break;
							}
						}
						if(nobatch==false){
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
								//$(tastodest).children().text(pezzi);
								//$(tastodest).children().attr("disabled",true);
								$(tastodest).children().remove();
								var idt="#"+al;
								$(tastodest).append($(idt));
								$(tastodest).attr("class","mark");
								$(tastodest).children().attr("onclick","move(this,\"bot\")");
								//$(aliquote[i]).remove();
								
								var vett_stored=mappa[barcodedest];
								vett_stored[bar]=s[1]+"|"+barcodedest+"|"+bar+"|"+geneal+"|"+pezzi+"|"+al;
								mappa[barcodedest]=vett_stored;
								
								var vett_op=mappa[barcodesorg];
								vett_op[num]=num+"|"+barcodesorg;
								mappa[barcodesorg]=vett_op;
							}
							var data = {
						    		batch:true,
						    		str:stringa,
						    		barcodesorg:$("#barcode_operative").val(),
						    		barcodedest:$("#barcode_freezer").val(),
						    };
							var url=base_url+"/store/save/";
							$.post(url, data, function (result) {
			
						    	if (result == "failure") {
						    		alert("Error");
						    	}
						    });
							$("#p_confirm").attr("disabled",false);
							conta_aliquote=0;
						}
						else{
							alert("Unable to execute batch mode.");
						}
					}
				}
			});
		}
		else{
			alert("Incompatible containers. Aliquot type they can contain is not the same.");
		}
	}
	else{
		alert("First you have to load the plates");
	}
}

function carica_operativa_scelta(){
	var codice=$(this).text().trim();
	$("#barcode_operative").attr("value",codice);
	carica_piastra_operativa_effettiva(codice);
}

function carica_operativa(){
	if ($("#barcode_operative").val() == "")
		alert("Insert plate barcode in working plate");
	else{		
		var codice=$("#barcode_operative").val();
		carica_piastra_operativa_effettiva(codice);
	}
}

function carica_piastra_operativa_effettiva(codice){
	url=base_url+"/api/table/"+codice+"/"+tipo+"/";
	$.getJSON(url,function(d){
		if(d.data=="errore"){
			alert("Plate doesn't exist");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else if(d.data=="errore_piastra"){
			alert("Plate aim is not working");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else if(d.data=="errore_aliq"){
			alert("Plate selected is not for "+tipo);
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
		else if(d.data=="errore_vital"){
			alert("Plate has not wells");
			$("#operativa table div").replaceWith("<button>0</button>");
			$("#operativa table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#operativa table button").css("background-color","rgb(249,248,242)");
			op=false;
		}
		else{
			$("#plate_operative").children().replaceWith(d.data);
			$("#operativa table button[sel=\"s\"]").attr("disabled",false);
			$("#operativa table button[sel=\"s\"]").css("background-color","gray");
			//attributi per lo spostamento multiplo
			$("#operativa table button").attr("assign","-");
			$("#operativa table button").attr("prev","plateButtonOFF");
			$("#operativa table button").attr("onclick","move(this,\"top\")");
			$("#operativa table button").attr("c","plateButtonOFF");
			//mi occupo del tooltip per il genid
			listabutton=$("#operativa table button[sel=\"s\"]");
			for(i=0;i<listabutton.length;i++){
				var gen=$(listabutton[i]).attr("gen");
				var barcc=$(listabutton[i]).attr("barcode");
				var fr="tooltip.show(\""+gen+" Barcode: "+barcc+"\")";
				$(listabutton[i]).attr("onmouseover",fr);
				var id=$(listabutton[i]).attr("id");
				var barc=$(listabutton[i]).attr("barcode");
				$(listabutton[i]).replaceWith("<div class=\'drag\' align='center' id='"+id+"' num='"+i+"' onmouseover='"+fr+"' onmouseout='tooltip.hide();' gen='"+gen+"' barcode='"+barc+"' assign='"+barc+"' prev='plateButtonOFF' c='plateButtonOFF' onclick='move(this,\"top\")'>" + listabutton[i].innerHTML + '</div>');
			}
			//assegno alla variabile il tipo di aliquote che puo' contenere
			tipooperativa=d.scopo;

			//metto classe=mark nelle celle in cui non voglio che venga
			//posizionato un tasto con il drag and drop
			$("#operativa th,.intest").attr("class","mark");
			//prendo i parent dei button cioe' i td
			$("#operativa table button,#operativa .drag").parent().attr("class","mark");
			
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
		    				//per rimpiazzare i posti vuoti con altri tasti a 0
		    				//$("#operativa [num="+valore[0]+"]").replaceWith("<button>0</button>");
		    				//per lasciare i posti vuoti nella piastra operativa
		    				$("#operativa [num="+valore[0]+"]").remove();
		    			}
		    		}
		    	}
			}
			
			//devo vedere se quella piastra c'e' gia' nella lista o no
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
			    if(tipo=="well"){
				    cell1.style.borderStyle="solid";
				    cell1.style.borderColor="black";
				    cell1.style.border="4px";
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
		    op=true;
		}
	});
}

function carica_stored_scelta(){
	var codice=$(this).text().trim();
	$("#barcode_freezer").attr("value",codice);
	carica_piastra_stored_effettiva(codice);
}

function carica_stored(){
	if ($("#barcode_freezer").val() == "")
		alert("Insert plate barcode in archive plate");
	else{
		var codice=$("#barcode_freezer").val();
		carica_piastra_stored_effettiva(codice);
	}
}

function carica_piastra_stored_effettiva(codice){
	url=base_url+"/api/table/"+codice+"/"+tipo+"/stored";
	$.getJSON(url,function(d){
		if(d.data=="errore"){
			alert("Plate doesn't exist");
			$("#freezer table div").replaceWith("<button>0</button>");
			$("#freezer table td").attr("class","mark");
			$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#freezer table button").css("background-color","rgb(249,248,242)");
			fr=false;
		}
		else if(d.data=="errore_piastra"){
			if (tipo=="well"){
				alert("Plate aim is not transient");
			}
			else{
				alert("Plate aim is not archive");
			}
			$("#freezer table div").replaceWith("<button>0</button>");
			$("#freezer table td").attr("class","mark");
			$("#freezer table button,#one,#batch,#p_confirm").attr("disabled",true);
			$("#freezer table button").css("background-color","rgb(249,248,242)");
			fr=false;
		}
		else if(d.data=="errore_aliq"){
			if (tipo=="TRANS"){
				alert("Plate selected is not for VT");
			}
			else{
				alert("Plate selected is not for "+tipo);
			}
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
			//cambio gli id in modo che siano univoci
			var listastore=$("#freezer table button");
			for(i=0;i<listastore.length;i++){
				var idoriginale=$(listastore[i]).attr("id");
				var ids=idoriginale.split("-");
				$(listastore[i]).removeAttr("id");
				var idfinale="m-"+ids[1];
				$(listastore[i]).parent().attr("id",idfinale);
			}
			
			//assegno alla variabile il tipo di aliquote che puo' contenere
			tipoarchive=d.scopo;
			
			//attributi per lo spostamento multiplo
			$("#freezer table button").attr("assign","-");
			$("#freezer table button").attr("prev","plateButtonOFF");
			$("#freezer table button").attr("onclick","move(this,\"bot\")");
			$("#freezer table button").attr("c","plateButtonOFF");
			
			if(tipo!="well"){
				$("#freezer table button[sel!=\"s\"]").attr("disabled",false);
				$("#freezer table button[barcode]").attr("disabled",true);
				//prendo i parent dei button cioe' i td
				$("#freezer table button[sel=\"s\"],#freezer table button[barcode]").parent().attr("class","mark");
				$("#freezer table button[sel=\"s\"],#freezer table button[barcode]").attr("assign","pieno");
			}
			else{
				//prendo i button che non hanno l'attributo barcode
				$("#freezer table button").not("[barcode]").parent().attr("class","mark");
				//serve per lo spostamento multiplo
				$("#freezer table button").not("[barcode]").attr("assign","pieno");
			}
			//metto classe=mark nelle celle in cui non voglio che venga
			//posizionato un tasto con il drag and drop
			$("#freezer th,.intest").attr("class","mark");
			
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
			
			//devo vedere se quella piastra c'e' gia' nella lista o no
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
		    rd.myhandler_moved = cella_partenza;
		    fr=true;
		    //metto l'evento per il drop
		    //$("#freezer table button").bind("drop",invia_dati);
		    //var tar= document.getElementById ("s-A1").parentNode;
		    //alert(tar);
		    //tar.addEventListener ("drag", invia_dati, false);    
		}
	});
}

function cella_partenza(){
	var idpartenza=REDIPS.drag.previous_cell.id;
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
    });
}

function invia_dati(){
	//devo controllare che il tipo della piastra caricata sia coerente con quello dell'altra
	var trov=0;
	for (var i=0;i<tipoarchive.length;i++){
		for (var k=0;k<tipooperativa.length;k++){
			if (tipoarchive[i]==tipooperativa[k]){
				trov=1;
				break;
			}
		}
	}
	if (trov==1){
		drag=true;
		//metto class=mark nella td di dest cos� non posso mettere altri tasti li'
		REDIPS.drag.target_cell.className="mark";
		
		//ho l'id della cella di partenza da dove sono partito per fare il drag and drop
		var partenza=REDIPS.drag.source_cell;
		var idarrivo=REDIPS.drag.target_cell.id;
		//vado a vedere se la piastra padre del pulsante e' operativa o stored
		var piastra=partenza.parentNode.parentNode.parentNode.parentNode.id;
		if ((piastra=="plate_stored")&&(partenza.id!=idarrivo)){
			//tolgo il class=mark nella td di partenza solo se e' nella piastra stored
			partenza.removeAttribute("class");
			if (tipo=="VT"){
				partenza.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>0</button>";
			}
			else{
				partenza.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>X</button>";
			}
		}
		//vado a vedere se la piastra dest del pulsante e' operativa o stored
		var piastra_dest=REDIPS.drag.target_cell.parentNode.parentNode.parentNode.parentNode.id;
		//solo se la dest e' operativa faccio tutto il resto
		if(piastra_dest=="plate_stored"){
			var barcode_dest=$("#barcode_freezer").val();
			var barcode_sorg=$("#barcode_operative").val();
			
			//abilito il tasto per confermare
			$("#p_confirm").attr("disabled",false);
			//mi da' l'id della div mossa
			var idpartenza=REDIPS.drag.target_cell.childNodes[0].id;
			var pospartenza=idpartenza.split("-");
			
			var idarrivo=REDIPS.drag.target_cell.id;
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
					
			var vett_stored=mappa[barcode_dest];
			vett_stored[bar]=posarrivo[1]+"|"+barcode_dest+"|"+bar+"|"+geneal+"|"+pezzi+"|"+id;
			mappa[barcode_dest]=vett_stored;
			
			var vett_op=mappa[barcode_sorg];
			vett_op[num]=num+"|"+barcode_sorg;
			mappa[barcode_sorg]=vett_op;
			
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
			
			var url=base_url+"/store/save/";
			$.post(url, data, function (result) {
		
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    });
		}
	}
	else{
		alert("Incompatible containers. Aliquot type they can contain is not the same.");
		REDIPS.drag.obj.parentNode.removeChild(REDIPS.drag.obj);
		carica_operativa();
		carica_stored();
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
	
	$("#p_confirm").click(function(event){
		//conto le aliquote che rimangono nella piastra operativa
		var listaaliq=$("#operativa table div.drag");
		var conta_aliquote=listaaliq.length;
		if(tipo!="well"){
			if(conta_aliquote!=0){
				input_box=confirm("Working plate still contains some aliquots. Do you really want to finish?")
				if (input_box!=true){ 
					//se l'utente dice di no alla domanda, blocco la sottomissione del form e faccio vedere sempre la stessa pagina
					event.preventDefault();
				}
				else{
					$("#cancellavitale").remove();
				}
			}
			else{
				$("#cancellavitale").remove();
			}
		}
		else{
			if(conta_aliquote!=0){
				event.preventDefault();
				//$.alerts.okButton = ' Yes ';
				//$.alerts.cancelButton = ' No ';
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
										barc=$("#barcode_operative").val();
										$("#cancellavitale").attr("value",barc);
										$( this ).dialog( "close" );
										$("#form_conferma").submit();
									},
									"No": function() {
										$("#cancellavitale").attr("value","00");
										$( this ).dialog( "close" );
									}
								}	
							});
						},
						"No": function() {
							$("#cancellavitale").attr("value","00");
							$( this ).dialog( "close" );
							$("#form_conferma").submit();
						}
					}
				});
				
			}
		}
	});
});