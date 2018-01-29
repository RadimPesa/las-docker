vettore_posiz={};
barcode_piastra=""

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
	var nameP="operativa";
    var url = base_url + "/api/table/" + codice + "/VT/" ;
    $.getJSON(url,function(d){
        if(d.data=="errore"){
			alert("Plate doesn't exist");
			$("#" + nameP + " div.drag").replaceWith("<button>0</button>");
			$("#" + nameP + " td").attr("class","mark");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else if(d.data=="errore_piastra"){
			alert("Plate aim is not working");
			$("#" + nameP + " div.drag").replaceWith("<button>0</button>");
			$("#" + nameP + " td").attr("class","mark");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else if(d.data=="errore_aliq"){
			var val=$("#"+nameP+" th").text().toLowerCase();
			alert("Plate selected is not "+val+" ");
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
	        $("#vital" ).replaceWith(d.data);
	        $("#" + nameP + " button").css("background-color","rgb(249,248,242)");

			var listastore=$("#"+nameP+" table button");
			for(i=0;i<listastore.length;i++){
				var idoriginale=$(listastore[i]).attr("id");
				var ids=idoriginale.split("-");
				$(listastore[i]).removeAttr("id");
				var idfinale="s-"+ids[1];
				$(listastore[i]).parent().attr("id",idfinale);
			}
			$("#" + nameP + " table button[sel!=\"s\"]").attr("disabled",false);
			//prendo i parent dei button cioe' i td
			$("#" + nameP + " table button[sel='s']").parent().attr("class","mark");
			$("#" + nameP + " table button[sel='s'],"+"#" + nameP + " table button:contains('X')").css("color","GrayText");
			
			$("#"+nameP+" br").remove();
			//metto classe=mark nelle celle in cui non voglio che venga
			//posizionato un tasto con il drag and drop
			$("#"+nameP+" th,.intest").attr("class","mark");
			$("#"+nameP+" table button:contains(X)").parent().attr("class","mark");
			//per bloccare la cella in alto a sinistra
	    	$("#"+nameP+" tr:nth-child(2)").children(":first-child").attr("class","mark");
			
	    	var numero=$("#aliq_tot").attr("value");
	    	//vedo se in quella piastra avevo gia' caricato qualcosa prima e lo
	    	//faccio comparire nella piastra
	    	for(i=1;i<(numero+1);i++){
	    		if(vettore_posiz[i]!=undefined){
	    			var valore=vettore_posiz[i];
	    			valore=valore.split("|");
	    			//solo se la piastra a cui si riferisce l'aliq e' questa
	    			if (valore[1]==codice){	
	    				//in valore[2] ho il numero di pezzi e in valore[3] il genid
	    				$("#s-"+valore[0]).children().replaceWith("<div class='drag' num='"+i+"' align='center' gen='"+valore[3]+"' onmouseover='tooltip.show(\""+valore[3]+"\");' onmouseout='tooltip.hide();' >"+valore[2]+"</div>");
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
				//vedo quanti td nuovi ho cioe' quelli con l'input hidden
				//var hidden=$("#listapias input:hidden");
				//inserisco la cella con dentro il numero d'ordine
			    var cell1 = row.insertCell(0);
			    cell1.innerHTML =codice;   
			    $("#listapias td:last").click(carica_piastra_scelta);
			}
			
			barcode_piastra=codice;
	    	
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
		}
	});
}


function invia_dati(){
	//metto class=mark nella td di dest cos� non posso mettere altri tasti li'
	REDIPS.drag.target_cell.className="mark";
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
	if ((piastra=="plate_operative")&&(idpartenza!=idarrivo)){
		partenza.innerHTML="<button align='center' type='submit'>0</button>";
		//tolgo il class=mark nella td di partenza solo se e' nella piastra stored
		partenza.removeAttribute("class");
	}
	var num=REDIPS.drag.target_cell.childNodes[0].getAttribute("num");
	var posarrivo=idarrivo.split("-");
	var barcode_dest=barcode_piastra;
	var pezzi=REDIPS.drag.target_cell.childNodes[0].innerHTML;
	var geneal=REDIPS.drag.target_cell.childNodes[0].getAttribute("gen");
	vettore_posiz[num]=posarrivo[1]+"|"+barcode_dest+"|"+pezzi+"|"+geneal;
	//riempio le variabili da trasmettere con la post
	/*var data = {
    		carica:true,
    		gen:geneal,
    		posnuova:posarrivo[1],
    		barcodedest:barcode_dest
    };
	
	var url=base_url+"/vital/execute/confirm_details/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    });*/
}

function convalida_aliquota(){
	var barcreale=$("#id_valid_barc").val();
	if(barcreale!=""){
		var url = base_url + "/api/tubes/" + barcreale+"&&" ;
	    $.getJSON(url,function(d){ 	
	        if(d.data!="errore"){
	        	var dat=d.data.toString();
	        	var val=dat.split(",");
	            //in val[0] ho il barcode del campione, in val[3] ho il genid
	            //se e' lungo 5 vuol dire che la provetta non e' vuota
	        	$("#da_posiz tr").css("background-color","#E8E8E8");
	            if (val.length==5){
	        		//devo vedere se il codice e' all'interno della lista di quelli da trattare in questa sessione
	        		//o se proprio non c'entra niente con questa schermata
	        		//var lista_barc=$("td[val=lis_barcode]");
	        		var lista_gen=$("td[val=lis_gen]");
	        		var lis_indici=$("td[val=lis_indici]");
	        		var trovato=false;
	        		var indice="";
	        		for(var i=0;i<lista_gen.length;i++){
	        			var codice=$(lista_gen[i]).text();
	        			if(codice.toLowerCase()==val[3].toLowerCase()){
	        				trovato=true;
	        				indice=$(lis_indici[i]).text();
	        				break;
	        			}
	        		}      		
	        		if(trovato){
	        			jQuery("#dialogMess").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br>"+indice+"° sample in this working session");
	        			var riga=$(lis_indici[indice-1]).parent();
	        			$(riga).css("background-color","#B6B5B5");
	        		}
	        		else{
	        			jQuery("#dialogMess").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br><br>Aliquot IS NOT in this working session, please change tube");
	        		}   	
	            }
	            //vuol dire che la provetta e' vuota
	            else{
	            	jQuery("#dialogMess").html("Barcode: "+barcreale+"<br><br>Container is empty or does not exist");
	            	
	            }   
	            jQuery("#dia1").dialog({
		            resizable: false,
		            height:200,
		            width:450,
		            modal: true,
		            draggable :false,
		            buttons: {
		                "Ok": function() {
		                    jQuery( this ).dialog( "close" );
		                    $("#id_valid_barc").focus();
		                },
		            },
		        });
	        }
	        
	        $("#id_valid_barc").val("");
	    });
	}
	else{
		alert("Please insert barcode");
	}
}

$(document).ready(function () {
    $("#validate_barc").click(function(event){
		event.preventDefault();
		convalida_aliquota();
	});
	
	$("#id_valid_barc").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			convalida_aliquota();
		}
	});
    
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Retrieve","aliquote_fin");
    	$("td").css("border-width","1px");
	}
	else{
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
	}
	
	//per nascondere la colonna con le posizioni
	var righe=$("#da_posiz tr");
	var nascondi=true;
	//da 1 per togliere la riga di intestazione
	for(var i=1;i<righe.length;i++){
		var pos=$(righe[i]).children(":nth-child(4)").text();
		if(pos!=""){
			nascondi=false;
		}
	}
	if(nascondi){
		for(var i=0;i<righe.length;i++){
			$(righe[i]).children(":nth-child(4)").css("display","none");
		}
	}
	
	$("#operativa table td,#operativa table th,.intest").attr("class","mark");
	$("#operativa button").css("background-color","lightgrey");
    $("#p_confirm").attr("disabled",true);
    
    //assegno una larghezza fissa alle celle della tabella per fare in
	//modo che durante lo spostamento le colonne rimaste vuote
	//non si rimpiccioliscano
	$("#da_posiz td").attr("width","30em");
	$("#da_posiz td").attr("height","35em");
	
	$("#operativa br").remove();
    
	$("#load_plate").click(carica_piastra);
	
	$("#barcode_plate").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_piastra();
		}
	});
	
	$("#p_confirm").click(function(event){
		event.preventDefault();
		var aliq=$("#da_posiz div.drag");
		if(aliq.length!=0){
			input_box=confirm("There are still some aliquots to position. Do you really want to finish?")
			//se l'utente dice di sì allora posso sottomettere il form
			if (input_box!=true){
				return;
			}
		}
		//riempio le variabili da trasmettere con la post
		var data = {
				carica:true,
				diz:JSON.stringify(vettore_posiz)
	    };
		var url=base_url+"/vital/execute/confirm_details/";
		$.post(url, data, function (result) {

	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	$("#form_fin").append("<input type='hidden' name='salva' />");
	    	
			$("#form_fin").submit();
	    });
	});
});