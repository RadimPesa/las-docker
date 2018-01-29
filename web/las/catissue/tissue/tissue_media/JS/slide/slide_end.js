posiz=false;
vettore_posiz=[];
aliq=false;
carica=false;
lista_aliq=new Array();
lista_container_usati={};
barcode_piastra=""
var contaaliq=1;

function piastra_definitiva(nameP,codice,tipo,radio,d){
	$("#" + nameP ).replaceWith(d);
    //$("#" + nameP + " button").css("background-color","rgb(249,248,242)");
    
    carica=true;
    //faccio vedere la tabella con il riepilogo delle piastre
    $("#listapias").css("display","");
    
    //blocco i tasti della tabella
    $("#rna button").click(function(event){
		event.preventDefault();
	});
    
    //metto l'id nei td della tabella
    var listastore=$("#"+nameP+" button");
	for(i=0;i<listastore.length;i++){
		var idoriginale=$(listastore[i]).attr("id");
		var ids=idoriginale.split("-");
		$(listastore[i]).removeAttr("id");
		var idfinale="s-"+ids[1];
		$(listastore[i]).parent().attr("id",idfinale);
	}

	$("#rna button[sel=\"s\"]").text("#");
	$("#rna button[sel=\"s\"], #rna button:contains(X)").css("background-color","#E8E8E8");

	//vedo se in quella piastra avevo gia' caricato qualcosa prima e lo
	//faccio comparire nella piastra
	//prendo il valore dell'indice della serie che sto trattando
	var numero=$("#pezzi_blocco").attr("value");
	var indice=$("#indice").val();
	for (var ii=0;ii<vettore_posiz.length;ii++) {
		var valore=vettore_posiz[ii];
		valore=valore.split("|");
		//solo se la piastra a cui si riferisce l'aliq e' questa
		if (valore[1]==codice){		
			$("#s-"+valore[0]).children().addClass("posiz");
			$("#s-"+valore[0]).children().attr("sel","s");				
			$("#s-"+valore[0]).children().text(indice);
			$("#s-"+valore[0]).children().attr("disabled",true);
		}
	}

	//devo vedere se quella piastra c'e' gia' nella lista o no
	var listapias=$("#listapias td");
	var trovato=false;
	for(i=0;i<listapias.length;i++){
		var testo=$(listapias[i]).text().trim();
		var cod=testo.split(" ");
		//in cod[0] ho il codice della piastra, in cod[1] ho il tipo (DNA,RNA...)
		if (codice==cod[0]){
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
		var hidden=$("#listapias input:hidden");
		//inserisco la cella con dentro il numero d'ordine
	    var cell1 = row.insertCell(0);
	    cell1.innerHTML ="<input type='hidden' name='piastra_"+((hidden.length-1)/2)+"' value="+codice+" />"+
	    "<input type='hidden' name='tipopiastra_"+((hidden.length-1)/2)+"' value="+tipo+" />"+codice;   
	    $("#listapias td:last").click(carica_piastra_scelta);
	}
	var listabutton=$("#rna button[sel=\"s\"]");
	
	//$("#rna button[sel=\"s\"],#rna button:contains(\"X\")").css("color","GrayText");
	//mi occupo del tooltip per il genid
	for(i=0;i<listabutton.length;i++){
		var gen=$(listabutton[i]).attr("gen");
		if(gen!=undefined){
			var fr="tooltip.show(\""+gen+"\")";
			$(listabutton[i]).attr("onmouseover",fr);
			$(listabutton[i]).attr("onmouseout","tooltip.hide()");
		}
		//se il genid e' nella lista delle aliq fatte in questa serie,
		//allora coloro il tasto e metto come numero quello della serie
		
		if(lista_aliq[gen]!=undefined){
			$(listabutton[i]).css("opacity","0.6");
			$(listabutton[i]).css("-moz-opacity","0.6");
			$(listabutton[i]).css("filter","alpha(opacity=60)");
			$(listabutton[i]).text(lista_aliq[gen].toString());
		}
	}
	barcode_piastra=codice;		
	$("#rna br").remove();
	//per mettere l'onclick sulle posizioni vuote del vetrino
	//$("#rna button:contains(0)").not("[sel='s']").click(click_in_piastra);
	$("#rna button").click(click_in_piastra);
	posiziona();	
}

function posiziona(){
	//prendo il numero di colonne della piastra
	var colonne=$("#rna tr:nth-child(2) td");
	var col=parseInt(colonne.length)-1;
	//prendo il numero di righe della piastra
	var righe=$("#rna tr");
	var rig=parseInt(righe.length)-2;
	//numero di pezzi da posizionare
	var num=parseInt($("#pezzi_blocco").val());
	var spessore=$("#spessore").val();
	var trovato=false;
	if (num<=col){
		//scandisco le righe
		for(var indice=3;indice<(rig+3);indice++){
			//devo prima capire da che posto cominciare nella riga, cioe' guardo qual
			//e' il primo posto libero
			var kk=2;
			var ferma=false;		
			while(!ferma){
				var id="#piastra tr:nth-child("+indice+") td:nth-child("+String(kk)+") :button";
				if(!($(id).attr("sel"))&&(!($(id).attr("disabled")))&&(!($(id).text()=="X"))){
					ferma=true;
				}
				else{
					kk++;
				}
			}
			//kk mi dice l'indice della cella da cui devo cominciare a posizionare
			if((kk-2)<col){
				var pieno=false;
				for (var j=kk;j<(kk+num);j++){
					var id="#piastra tr:nth-child("+indice+") td:nth-child("+String(j)+") :button";
					//la prima condizione e' per vedere se cerco di referenziare un tasto che non esiste
					//perche' la piastra finisce prima, e' piu' corta
					if((($(id).length)==0)||($(id).attr("sel"))||($(id).attr("disabled"))||($(id).text()=="X")){
						pieno=true;
					}
				}
				if (pieno==false){
					for(var k=kk;k<(kk+num);k++){
						var idcella="#piastra tr:nth-child("+indice+") td:nth-child("+String(k)+")";
						var posar=$(idcella).attr("id");
						var posarrivo=posar.split("-");
						var barcode_dest=barcode_piastra;
						$(idcella).children().addClass("posiz");
						var serie=$("#indice").val();
						$(idcella).children().text(serie);
						$(idcella).children().attr("sel","s");
						trovato=true;
						$(idcella).children().attr("disabled",true);
						var pezzi=$("#pezzi_vetrino").val();
						vettore_posiz.push(posarrivo[1]+"|"+barcode_dest+"|"+spessore+"|1x"+String(parseInt(pezzi))+"|"+String(contaaliq));
						$("#aliquots_table").dataTable().fnAddData([null, contaaliq, barcode_dest, posarrivo[1], spessore]);
						contaaliq++;
					}
					//per bloccare la scansione delle righe, visto che non mi serve piu' 
					//perche' ho posizionato adesso i campioni
					break;
				}
			}
		}
	}
	//non c'e' posto in quella piastra
	//if(trovato==false){
		//alert("Slide full. Please select another one.");
	//}
	$("body").removeClass("loading");
}

function click_in_piastra(){
	var serie=$("#indice").val();
	var pos=$(this).attr("pos");
	$(this).addClass("posiz");
	$(this).text(serie);
	$(this).attr("sel","s");
	$(this).attr("disabled",true);
	var spessore=$("#spessore").val();
	var pezzi=$("#pezzi_vetrino").val();
	vettore_posiz.push(pos+"|"+barcode_piastra+"|"+spessore+"|1x"+String(parseInt(pezzi))+"|"+String(contaaliq));
	$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, barcode_piastra, pos, spessore] );
	contaaliq++;
}

function deleteAliquot(idoperaz){
	for (var j=0;j<vettore_posiz.length;j++){
		var val =vettore_posiz[j];
		var valore=val.split("|");
		if(parseInt(valore[4])==parseInt(idoperaz)){
			//solo se la piastra a cui si riferisce l'aliq e' questa
			if (valore[1]==barcode_piastra){		
				$("#s-"+valore[0]).children().removeClass("posiz");
				$("#s-"+valore[0]).children().removeAttr("sel");
				$("#s-"+valore[0]).children().text("0");
				$("#s-"+valore[0]).children().css("color","");
				$("#s-"+valore[0]).children().attr("disabled",false);
			}
			vettore_posiz.splice(j,1);
		}
	}
}

function cerca_container_usati(barc){
	var trovato=0;
	for (barcode in lista_container_usati){
		if (barcode==barc){
			return true;
		}
	}
	return false;
}

function errore_cont(nameP){
	$("#rna div").replaceWith("<button>0</button>");
	$("#rna td").attr("class","mark");
	$("#rna td button").removeAttr("onmouseover");
	$("#rna td button").removeAttr("onmouseout");
	$("#" + nameP + " button").attr("disabled", true );
}

function carica_effettiva(codice){
	var tipo=$("#proto").attr("value");
	var regex=/^[0-9.]+$/;
	var regex2=/^[0-9]+$/;
	var nameP="rna";
	var radio="plate";
	
	var spessore=$("#spessore").val().trim();
	var pezzi=$("#pezzi_vetrino").val().trim();
	var pezziblocco=$("#pezzi_blocco").val().trim();
	if(!regex.test(spessore)){
		alert("\"Thickness\" has to be a number");
		errore_cont(nameP);
		return;
	}
	else if (!regex2.test(pezzi)){
		alert("\"N° of sections per slide\" has to be an integer number");
		errore_cont(nameP);
		return;
	}
	else if (parseInt(pezzi)<1){
		alert("\"N° of sections per slide\" has to be greater than 0");
		errore_cont(nameP);
		return;
	}
	else if (!regex2.test(pezziblocco)){
		alert("\"N° of sections per block\" has to be an integer number");
		errore_cont(nameP);
		return;
	}
	
	if (cerca_container_usati(codice)){
		dati=lista_container_usati[codice];
		piastra_definitiva(nameP,codice,tipo,radio,dati);
	}
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		var codiceurl=codice.replace(/#/g,"%23");
		var url = base_url + "/api/generic/load/" + codiceurl + "/" + tipo+ "/" + radio;
	    $.getJSON(url,function(d){
	        if(d.data=="errore"){
	        	radio="tube";
        		var tipocont=$("#tipocont").val();
	        	var tip=tipocont.replace(/%20/g," ");
	        	var url = base_url + "/api/slide/load/" + codiceurl + "/" + tipo+ "/"+ tip+ "/"+ String(parseInt(pezzi))+ "/";
	    	    $.getJSON(url,function(ris){
	    	    	if((ris.data=="err_tipo")||(ris.data=="errore")){
	    				alert("Error while connecting with storage");
	    				errore_cont(nameP);
	    			}
	    	    	else if(ris.data=="err_esistente"){
	    				alert("Error: barcode you entered already exists");
	    				errore_cont(nameP);
	    			}
	    	    	else if(ris.data=="err_cont"){
	    				alert("Unknown slide type. Please insert it in storage module");
	    				errore_cont(nameP);
	    			}
	    	    	else{
	    	    		lista_container_usati[codice]=ris.data;
	    				piastra_definitiva(nameP,codice,tipo,radio,ris.data);
	    	    	}
	    	    });		        	
			}
			else if(d.data=="errore_aliq"){
				var val=$("#"+nameP+" th").text().toLowerCase();
				alert("Slide is not for "+tipo);
				errore_cont(nameP);
			}
			else if(d.data=="errore_store"){
				alert("Error while connecting with storage");
				errore_cont(nameP);
			}
			else{
				lista_container_usati[codice]=d.data;
				piastra_definitiva(nameP,codice,tipo,radio,d.data);
			}
	        clearTimeout(timer);
	    	$("body").removeClass("loading");
	    });
	}
}

function caricaPiastra(){
	if ($("#barcode_plate").val() == ""){
		alert("Please insert barcode");
	}
	else{
		var codice=$("#barcode_plate").val().trim();
		carica_effettiva(codice);
	}
}

function carica_piastra_scelta(){
	var val=$(this).text().trim();
	var cod=val.split(" ");
	var codice=cod[0];
	$("#barcode_plate").attr("value",codice);
	carica_effettiva(codice);
}

function convalida_aliquota(){
	var barcreale=$("#id_valid_barc").val().trim();
	if(barcreale!=""){
		var barcteorico=$("#barc_campione").val().trim();
		var url = base_url + "/api/tubes/" + barcreale+"&&" ;
	    $.getJSON(url,function(d){
	    	
	        if(d.data!="errore"){
	        	var dat=d.data.toString();
	        	var val=dat.split(",");
	            //in val[0] ho il barcode del campione, in val[3] ho il genid
	            //se e' lungo 5 vuol dire che la provetta non e' vuota
	        	var genaliq=$("#gen").val().trim();
	            if (val.length==5){
	            	if((barcreale.toLowerCase()==barcteorico.toLowerCase())&&(genaliq==val[3])){
	            		jQuery("#dialogMess").html("Barcode: "+barcreale+"<br>GenID: "+genaliq+"<br><br>Aliquot and barcode match, you can execute the procedure");
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
	            		//alert("Barcode: "+barcreale+"\nGenID: "+val[3]+"\n\nAliquot and barcode match, you can execute the procedure");
	            	}
	            	else{
	            		//devo vedere se il codice e' all'interno della lista di quelli da trattare in questa sessione
	            		//o se proprio non c'entra niente con questa schermata
	            		//var lista_barc=$(".lista_barc");
	            		var lista_gen=$(".lista_gen");
	            		var lis_indici=$(".lista_indici");
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
	            			jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br>"+indice+"° sample in this session"+"<br><br>Barcode DOES NOT match, please change source aliquot");	            			
	            		}
	            		else{
	            			jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br><br>Barcode DOES NOT match, please change source aliquot");
	            		}
	            		
				        jQuery("#dia2").dialog({
				            resizable: false,
				            height:220,
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
	            }
	            //vuol dire che la provetta e' vuota
	            else{
	            	jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br><br>Container is empty or does not exist");
	            	jQuery("#dia2").dialog({
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
	        }
	        $("#id_valid_barc").val("");    
	    });
	}
	else{
		alert("Please insert barcode");
	}
}

function post_server(tasto){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	//riempio le variabili da trasmettere con la post
	var data = {
			posizione:true,
    		diz:JSON.stringify(vettore_posiz)
    };
	var url=base_url+"/slide/execute/last/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    	var idtasto=$(tasto).attr("id");
    	if(idtasto=="conf_all"){
    		$("#form_fin").append("<input type='hidden' name='conf' />");
    	}
    	else{
    		$("#form_fin").append("<input type='hidden' name='finish' />");
    	}
    	$("#form_fin").submit();
    	//clearTimeout(timer);
    	//$("body").removeClass("loading");
    });
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
    	generate_result_table("Slide_preparation","aliquote_fin");
    	$("td").css("border-width","1px");
	}
	else{
		var tab=$("#lis_aliqder").dataTable({
			"bPaginate": true,
			"bLengthChange": true,
			"bFilter": true,
			"bSort": false,
			"bInfo": true,
			"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
			"bAutoWidth": false });
		
		var oTable = $("#aliquots_table").dataTable({
	        "bProcessing": true,
	         "aoColumns": [
	            { 
	               "sTitle": null, 
	               "sClass": "control_center", 
	               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"               
	            },
	            { "sTitle": "ID Operation" },
	            { "sTitle": "Barcode" },
	            { "sTitle": "Position" },
	            { "sTitle": "Thickness" },
	        ],
		    "bAutoWidth": false ,
		    "aaSorting": [[1, 'desc']],
		    "aoColumnDefs": [
		        { "bSortable": false, "aTargets": [ 0 ] },
		    ],
		    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	    });
	
		//per nascondere la colonna con le posizioni
		var righe=tab.$("tr");
		var nascondi=true;
		for(var i=0;i<righe.length;i++){
			var pos=$(righe[i]).children(":nth-child(4)").text();
			if(pos!=""){
				nascondi=false;
			}
		}
		if(nascondi){
			tab.fnSetColumnVis( 3, false );
		}
	}
	
	//se nel campo della posizione c'e' "/", allora la pos non c'e', devo far scomparire il campo
	//e mettere il padding nel div dopo che riguarda l'aliquota esaurita
	var pos=$("#pos_campione").val();
	if (pos=="/"){
		$("#spanposiz").css("display","none");
		$("#aliq_esaur").css("padding-top","1em");
	}
	
	var listapias=$("#listapias td");
	//faccio vedere la tabella con il riepilogo delle piastre, se c'e' qualcosa
	if(listapias.length!=0){
		$("#listapias").css("display","");
	}
		
	$("#load_plate").click(caricaPiastra);
	
	$("#listapias td").click(carica_piastra_scelta);	
	
	$("#barcode_plate").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			caricaPiastra();
		}
	});
	
	$("#load_plate").click(function(event){
		event.preventDefault();
	});
	
	$("#aliquots_table tbody td.control_center img").live("click", function () {
        var genID = $($($(this).parents('tr')[0]).children()[4]).text();
        var operaz = $($($(this).parents('tr')[0]).children()[1]).text();
        deleteAliquot(operaz);
        var nTr = $(this).parents('tr')[0];
        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
    });
	
	//chiamo la API per riempire il dizionario che ha come chiave i genid delle
	//aliq gia' create nella sessione e come valore il numero della sessione
	var url = base_url + "/api/slide/final/";
    $.getJSON(url,function(d){
    	var strin=d.data;
    	var st=strin.split("|");
    	for(i=0;i<st.length;i++){
    		var val=st[i].split(":");
    		//in val[0] ho il genid, in val[1] ho il numero della serie
    		lista_aliq[val[0]]=val[1];
    	}
    });
	
	$("#conf_all,#finish").click(function(event){
		event.preventDefault();
		//salvo il numero delle nuove piastre che ho inserito nella schermata
		var nasc=$("#listapias input:hidden");
		var inputeffettivi=(nasc.length-1)/2;
		$("#numnuovepi").attr("value",inputeffettivi);
		
		if ($("#barcode_plate").val() == ""){
			alert("Insert plate barcode");
			return;
		}
		//guardo che sia stato creato almeno un campione
		if(vettore_posiz.length==0){
			alert("Please create at least one section");
			return;
		}
		post_server(this);		
	});
});