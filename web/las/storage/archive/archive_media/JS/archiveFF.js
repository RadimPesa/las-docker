vettore_posiz=new Array();
tipopiastra="";
tipoblocco="";
multipl=false;

function carica_piastra_scelta(){
	var val=$(this).text().trim();
	var cod=val.split(" ");
	var codice=cod[0];
	$("#barcode_plate").attr("value",codice);
	carica_effettiva(codice);
}

function carica_piastra(){
	if ($("#barcode_plate").val() == "")
		alert("Insert plate barcode");
	else{
		var codice=$("#barcode_plate").val();
		carica_effettiva(codice);
	}
}

function carica_effettiva(codice){
	var timer = setTimeout(function(){$("body").addClass("loading");},2000);
	
	var nameP="operativa";
    var url = base_url + "/api/draw/" + codice ;
    $.getJSON(url,function(d){
        if(d.data=="errore"){
			alert("Container doesn't exist");
			$("#" + nameP + " div.drag").replaceWith("<button>0</button>");
			$("#" + nameP + " td").attr("class","mark");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else if(d.data=="errore_piastra"){
			alert("Plate is not for archive");
			$("#" + nameP + " div.drag").replaceWith("<button>0</button>");
			$("#" + nameP + " td").attr("class","mark");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else if(d.data=="errore_aliq"){
			alert("Container selected is not a drawer");
			$("#" + nameP + " div.drag").replaceWith("<button>0</button>");
			$("#" + nameP + " td").attr("class","mark");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else if(d.data=="errore_store"){
			alert("Error while connecting with storage");
			$("#" + nameP + " div.drag").replaceWith("<button>0</button>");
			$("#" + nameP + " td").attr("class","mark");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else{
	        $("#rna").replaceWith(d.data);
	        $("#" + nameP + " button").css("background-color","rgb(249,248,242)");
	        //salvo il tipo della piastra in questa var globale per poter poi fare i
	        //controlli
	        tipopiastra=d.tipo;

			var listastore=$("#"+nameP+" table button");
			for(i=0;i<listastore.length;i++){
				var idoriginale=$(listastore[i]).attr("id");
				var ids=idoriginale.split("-");
				//$(listastore[i]).removeAttr("id");
				var idfinale="s-"+ids[1];
				$(listastore[i]).parent().attr("id",idfinale);
			}
			$("#" + nameP + " table button[sel!=\"s\"]").attr("disabled",false);
			//se il container non supporta piu' figli nelle stesse posizioni, allora
			//blocco i td con il mark
			multipl=d.multiplo;
			if(multipl==false){
			//prendo i parent dei button cioe' i td
			$("#" + nameP + " table button[sel=\"s\"]").parent().attr("class","mark");
			}
			
			//metto classe=mark nelle celle in cui non voglio che venga
			//posizionato un tasto con il drag and drop
			$("#"+nameP+" th,.intest").attr("class","mark");
			//per bloccare la cella in alto a sinistra
	    	$("#"+nameP+" tr:nth-child(2)").children(":first-child").attr("class","mark");
			
	    	var listabutton=$("#plate_operative table button[gen]");
	    	for(i=0;i<listabutton.length;i++){
				var gen=$(listabutton[i]).attr("gen");
				if (gen!=""){
					var fr="tooltip.show('"+gen+"');";
					$(listabutton[i]).attr("onmouseover",fr);
					$(listabutton[i]).attr("onmouseout","tooltip.hide();");
					$(listabutton[i]).removeAttr("gen");
				}
	    	}
	    	
	    	var numero=$("#aliq_tot").attr("value");
	    	//vedo se in quel cassetto avevo gia' caricato qualcosa prima e lo
	    	//faccio comparire
	    	//for(i=1;i<(numero+1);i++){
	    	for (var i in vettore_posiz){
    			var valore=vettore_posiz[i];
    			valore=valore.split("|");
    			//solo se il cassetto a cui si riferisce l'aliq e' questa
    			if (valore[1]==codice){	
    				//in valore[2] ho il barcode e in valore[3] il genid
    				var toolt="tooltip.show(\"Barcode: "+valore[2]+"\\nGenID:"+valore[3]+"\")";
    				//prendo l'ultimo figlio di quella cella della tabella
    				var tasto=$("#s-"+valore[0]).children(":last-child");
    				if(tasto.text()=='X'){
    					tasto.replaceWith("<div class='drag' num='"+i+"' align='center' barc='"+valore[2]+"' gen='"+valore[3]+"' onmouseover='"+toolt+"' onmouseout='tooltip.hide();' >1</div>");
    				}
    				else{
    					tasto.after("<div class='drag' num='"+i+"' align='center' barc='"+valore[2]+"' gen='"+valore[3]+"' onmouseover='"+toolt+"' onmouseout='tooltip.hide();' >1</div>");
    				}
    			}
	    	}
	    	
	    	//faccio vedere la tabella con il riepilogo delle piastre
	        $("#listapias").css("display","");
	    	//devo vedere se quella piastra c'e' gia' nella lista o no
			var listapias=$("#listapias td");
			var trovato=false;
			for(i=0;i<listapias.length;i++){
				var testo=$(listapias[i]).text().trim();
				if (codice==testo){
					trovato=true;		
				}
			}
			if (trovato==false){
				var tabella = document.getElementById("listapias");
				//prendo il numero di righe della tabella
				var rowCount = tabella.rows.length;
				var row = tabella.insertRow(rowCount);
				//per centrare la td
				row.align="center";
				//vedo quanti td nuovi ho, cioe' quelli con l'input hidden
				//var hidden=$("#listapias input:hidden");
				//inserisco la cella con dentro il numero d'ordine
			    var cell1 = row.insertCell(0);
			    cell1.innerHTML =codice;   
			    $("#listapias td:last").click(carica_piastra_scelta);
			}
	    	
			// reference to the REDIPS.drag library
		    var rd = REDIPS.drag;
		    // initialization
		    rd.init();
		    // set hover color
		    rd.hover.color_td = '#E7C7B2';
		    // set drop option to 'shift'
		    rd.drop_option = 'multiple';
		    //rd.drop_option = 'overwrite';
		    // set shift mode to vertical2
		    rd.shift_option = 'vertical2';
		    // enable animation on shifted elements
		    rd.animation_shift = true;
		    // set animation loop pause
		    rd.animation_pause = 20;
		    rd.myhandler_dropped = invia_dati;
		}
        
        clearTimeout(timer);
    	$("body").removeClass("loading");
    	
	});
}

function carica_FF(){
	if ($("#barcode_pieces").val() == "")
		alert("Insert container barcode");
	else{
		var codice=$("#barcode_pieces").val();
		var codiceurl=codice.replace(/#/g,"%23");
		//alert(codice)
		//chiamo la API per avere il genid dato il barcode del pezzo
		url1=base_url+"/api/return/"+codiceurl+"&&/";
		
		$.getJSON(url1,function(d){
			var x=d.data[0];
			var listab=x.split(",");
			if(listab.length>3){
				var url2=base_url+"/api/biocassette/"+codiceurl+"/FF/archive";
				$.getJSON(url2,function(d){
					if(d.data=="ok"){
						//vedo se questo pezzo non l'avevo gia' posizionato 
						//prima
						if(vettore_posiz[listab[3]]==undefined){
							var geneal=listab[3];
							$("#td_gen").text(geneal);
							$("#tab_gen").css("display","");
							$("#tab_gen td").css("font-size","1.3em");
							
							//elimino gli eventuali tasti gia' presenti
							$("#td_tasto").children().remove();
							var toolt="tooltip.show(\"Barc: "+codice+"\\nGenID: "+geneal+"\")";
							$("#td_tasto").append("<div class='drag' align='center' barc='"+codice+"' gen='"+geneal+"' onmouseover='"+toolt+"' onmouseout='tooltip.hide();' >1</div>");
							//salvo il tipo del blocchetto in questa var globale per poter poi fare i
					        //controlli
							if(d.tipo==""){
								tipoblocco=geneal[20]+geneal[21];
							}
							else{
								tipoblocco=d.tipo;
							}

							// reference to the REDIPS.drag library
						    var rd = REDIPS.drag;
						    // initialization
						    rd.init();
						    // set hover color
						    rd.hover.color_td = '#E7C7B2';
						    // set drop option to 'shift'
						    //rd.drop_option = 'shift';
						    rd.drop_option = 'multiple';
						    // set shift mode to vertical2
						    rd.shift_option = 'vertical2';
						    // enable animation on shifted elements
						    rd.animation_shift = true;
						    // set animation loop pause
						    rd.animation_pause = 20;
						    rd.myhandler_dropped = invia_dati;
						}
						else{
							alert("Container already positioned in this working session");
							$("#tab_gen").css("display","none");
						}
					}
					else if(d.data=="posiz"){
						alert("Container already positioned");
						$("#tab_gen").css("display","none");
					}
				});
			}
			else{
				alert("Container doesn't exist or is empty");
				$("#tab_gen").css("display","none");
			}
		});
	}
}

function carica_lista_provette(){
	var timer = setTimeout(function(){$("body").addClass("loading");},2000);
	//prendo il tipo di aliquota che devo caricare
	var tipo=$("#id_tipi option:selected").val();
	var url=base_url+"/api/freecontainer/"+tipo+"/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			$("#tab_riass").css("display","");
			$("#tab_riass").dataTable({
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"bInfo": true,
				"bDestroy": true,
				"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
				"bAutoWidth": false });
			$("#tab_riass_wrapper").css("float","left");
			$("#tab_riass_wrapper").css("width","77%");
			//cancello tutte le righe della tabella
			var oSettings = $("#tab_riass").dataTable().fnSettings();
			var iTotalRecords = oSettings.fnRecordsTotal();
			for (i=0;i<=iTotalRecords;i++) {
			$("#tab_riass").dataTable().fnDeleteRow(0,null,true);
			}
			//ho il dizionario con gen:barcode
			var diz=d.data;
			var j=1;
			for(var key in diz){
			    if(diz.hasOwnProperty(key)){
			    	var trovato=false;
			    	for (var k in vettore_posiz){
		    			var valore=vettore_posiz[k];
		    			valore=valore.split("|");
		    			//in valore[2] ho il barcode e in valore[3] il genid
		    			if(valore[2]==diz[key]){
		    				trovato=true;
		    				break;
		    			}
			    	}
			    	if (trovato==false){
			    		$("#tab_riass").dataTable().fnAddData( [j, key, diz[key]] );
			    	}
			    	j++;
			    }
			}
		}
		clearTimeout(timer);
    	$("body").removeClass("loading");
	});
}

function invia_dati(){
	if(tipopiastra==tipoblocco){
		//metto class=mark nella td di dest cos� non posso mettere altri tasti li'
		//solo se non e' un cassetto
		if(multipl==false){
			REDIPS.drag.target_cell.className="mark";
		}
		//ho l'id della cella di partenza da dove sono partito per fare il drag and drop
		var partenza=REDIPS.drag.source_cell;
		//vado a vedere se la piastra padre del pulsante e' operativa (quella di destra)
		//o se e' quella che si trova a sinistra nella schermata
		var piastra=partenza.parentNode.parentNode.parentNode.parentNode.id;
		//abilito il tasto per confermare
		$("#p_confirm").attr("disabled",false);
		//mi da' l'id della div mossa
		var idpartenza=REDIPS.drag.source_cell.id;
		var idarrivo=REDIPS.drag.target_cell.id;
		if ((piastra=="plate_operative")&&(idpartenza!=idarrivo)&&(partenza.childNodes.length==0)){
			partenza.innerHTML="<button align='center' type='submit'>X</button>";
			//tolgo il class=mark nella td di partenza solo se e' nella piastra stored
			partenza.removeAttribute("class");
		}
		var cass_dest=REDIPS.drag.target_cell.parentNode.parentNode.parentNode.parentNode.id;
		if(cass_dest=="plate_operative"){
			//var num=REDIPS.drag.target_cell.childNodes[0].getAttribute("num");
			var posarrivo=idarrivo.split("-");
			
			var barcode_dest=$("#barcode_plate").val();
			//var pezzi=REDIPS.drag.target_cell.childNodes[0].innerHTML;
			var barc=REDIPS.drag.obj.getAttribute("barc");
			var gen=REDIPS.drag.obj.getAttribute("gen");
	
			//se la cella dest contiene un tasto con X come testo, lo devo togliere
			var numparti=REDIPS.drag.target_cell.childNodes[0].innerHTML;
			var tasto=REDIPS.drag.target_cell.childNodes[0];
			if (numparti=="X"){
				REDIPS.drag.target_cell.removeChild(tasto);
			}
			
			vettore_posiz[gen]=posarrivo[1]+"|"+barcode_dest+"|"+barc+"|"+gen;
			
			//cancello dalla tabella riassuntiva i pezzi posizionati solo se e' visibile
			if (($("#tab_riass").css("display"))!="none"){
				var tab=$("#tab_riass").dataTable();
				//prendo il valore del barcode per il pezzo posizionato
				var lista=tab.$("tr").children(":nth-child(3)");
				var k=1;
				var nodes = tab.$("tr");
				var oid = [];
				var ii=0;
				$(nodes).filter('tr').each( function() {
					oid[ii] = ii;//$(this).attr('id'); 
					ii++;
				});
				for(i=0;i<lista.length;i++){
					var barcode=$(lista[i]).text();
					//se il barcode coincide, allora devo togliere la riga
					if (barcode==barc){
						//$(lista[i]).parent().hide();
						//var pos = tab.fnGetPosition($("#" + oid[i]).get(0));
						//var po=oid[i].split("_");
						//var pos=po[1];
						//comunico alla funzione il numero di riga in cui si trova il pezzo
						//di FF
						tab.fnDeleteRow(oid[i],null,true);
						break;
					}
				}
				var lista=tab.$("tr").children(":nth-child(3)");
				for(i=0;i<lista.length;i++){
					$(lista[i]).parent().children(":nth-child(1)").text(k);
					k=k+1;
				}
			}
			
			//riempio le variabili da trasmettere con la post
			var data = {
		    		carica:true,
		    		barcode:barc,
		    		posnuova:posarrivo[1],
		    		barcodedest:barcode_dest
		    };
			
			var url=base_url+"/store/cassette/";
			$.post(url, data, function (result) {
		
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    });
			$("#barcode_pieces").val("");
		}
	}
	else{
		alert("Incompatible containers. Aliquot type they can contain is not the same.");
		carica_FF();
		//per cancellare la div che ho spostato
		REDIPS.drag.obj.parentNode.removeChild(REDIPS.drag.obj);
	}
}

$(document).ready(function () {
	// reference to the REDIPS.drag library
    var rd = REDIPS.drag;
    // initialization
    rd.init();
    // set hover color
    rd.hover.color_td = '#E7C7B2';
    // set drop option to 'shift'
    //rd.drop_option = 'shift';
    rd.drop_option = 'multiple';
    // set shift mode to vertical2
    rd.shift_option = 'vertical2';
    // enable animation on shifted elements
    rd.animation_shift = true;
    // set animation loop pause
    rd.animation_pause = 20;
    rd.myhandler_dropped = invia_dati;
    
    /*$("#tab_riass").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });
	$("#tab_riass_wrapper").css("float","left");
	$("#tab_riass_wrapper").css("width","77%");*/
    
    $("#operativa table td,#operativa table th,.intest").attr("class","mark");
    $("#p_confirm").attr("disabled",true);
    
    //assegno una larghezza fissa alle celle della tabella per fare in
	//modo che durante lo spostamento le colonne rimaste vuote
	//non si rimpiccioliscano
	$("#tab_gen td").attr("width","50px");
	$("#tab_gen td").attr("height","50px");
	$("#tab_gen td,#tab_gen th").css("border-color","black");
    
	$("#load_plate").click(carica_piastra);
	
	$("#barcode_plate").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_piastra();
		}
	});
	
	$("#load_barc").click(carica_FF);
	
	$("#l_aliquote").click(carica_lista_provette);
	
	$("#barcode_pieces").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_FF();
		}
	});
	
	/*$("#p_confirm").click(function(event){
		var aliq=$("#da_posiz div.drag");
		if(aliq.length!=0){
			input_box=confirm("There are still some aliquots to position. Do you really want to finish?")
			if (input_box!=true){ 
				//se l'utente dice di no alla domanda, blocco la sottomissione del form e faccio vedere sempre la stessa pagina
				event.preventDefault();
			}
		}
	});*/
});