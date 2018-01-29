//e' un dizionario che contiene le gerarchie dei container (padre, figlio)
var diztemp={};
//e' una lista di dizionari, in cui ogni diz e' un container nuovo
var listagen=[];
//lista di dizionari, in cui ogni diz e' un container gia' presente nel DB
var lista2=[];
var contacont=1;

function selpadri(){
	if ($(this).attr("sel")=="s"){
		$(this).val("Select all roots");
		$(".divinterna .checkest:checkbox").removeAttr("checked");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all roots");
		$(".divinterna .checkest:checkbox").attr("checked","checked");
		$(this).attr("sel","s");
		//devo deselezionare tutti i figli
		$(".figliint .checkint").removeAttr("checked");
		$("#selfigli").val("Select all leaves");
		$("#selfigli").removeAttr("sel");
	}
}

function selfigli(){
	var listarighe=[];
	if ($(this).attr("sel")=="s"){	
		$(this).val("Select all leaves");
		$(".figliint .checkint").removeAttr("checked");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all leaves");
		$(".figliint .checkint").attr("checked","checked");
		$(this).attr("sel","s");
		//devo deselezionare tutti i padri
		$("#selpadri").val("Select all roots");
		$(".checkest:checkbox").removeAttr("checked");
		$("#selpadri").removeAttr("sel");
	}
}

function selezionatutto(){
	if ($(this).attr("sel")=="s"){
		$(this).val("Select all");
		$("#id_Aliquot_Type option").removeAttr("selected");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all");
		$("#id_Aliquot_Type option").attr("selected","selected");
		$(this).attr("sel","s");
	}
}

function seltuttifigli(){
	if ($(this).attr("sel")=="s"){
		$(this).val("Select all");
		var barc=$(this).attr("barc");
		$(".checkint[fath='"+barc+"']").removeAttr("checked");
		var classe=".divint"+barc;
		//prendo le div figlie di quel container
		var lista=$(classe).children(".checkest").removeAttr("checked");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all");
		var barc=$(this).attr("barc");
		$(".checkint[fath='"+barc+"']").attr("checked","checked");
		var classe=".divint"+barc;
		//prendo le div figlie di quel container
		var lista=$(classe).children(".checkest").attr("checked","checked");
		$(this).attr("sel","s");
	}
}

function aggiorna_tipi_cont(){
	var tipo_generico=$("#id_generic option:selected").val();
	if(tipo_generico!=""){
		var url=base_url+"/api/generic/type/"+tipo_generico+"/";
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				$("#id_tipi option").not(":first").remove();
				var lista=d.data;
				for(var i=lista.length-1;i>=0;i--){
					//mi occupo della geometria
					var geom=lista[i].idGeometry.toString();
					var geo=geom.split("x");
					var righe=geo[0];
					var col=geo[1];
					var oneUse=lista[i].oneUse.toString();
					var stringa="<option value="+lista[i].id+" rows="+righe+" col="+col+" oneuse="+oneUse+" >"+lista[i].actualName+"</option>"
					$("#id_tipi option[value=\"\"]").after(stringa);
				}
			}
		});
	}
}

function assegna_geometria(){
	var tip=$("#id_tipi option:selected").val();
	//faccio comparire la giusta geometria
	var righ=$("#id_tipi option:selected").attr("rows");
	var col=$("#id_tipi option:selected").attr("col");
	$("#id_row").val(righ);
	$("#id_col").val(col);
	//seleziono o meno il check del oneuse
	var oneuse=$("#id_tipi option:selected").attr("oneuse");
	if (oneuse=="True"){
		$("#id_use").attr("checked",true);
	}
	else{
		$("#id_use").attr("checked",false);
	}
}

//per aggiungere i container gia' presenti nel DB al dizionario che invio con la POST
//salvo solo padre e posizione perche' le altre informazioni le ho gia' nel DB
function aggiungi_cont(){
	var liscon=$(".contpres");
	//devo trovare il padre
	for (var i=0;i<liscon.length;i++){
		var padre=$(liscon[i]).attr("fath");
		var pos=$(liscon[i]).attr("pos");
		//se sto trattando un figlio allora ho gia' i valori salvati nelle due variabili, altrimenti
		//devo andare a prendere il padre io navigando nell'albero DOM
		if(padre=="undefined"){
			padre=$(liscon[i]).parent().parent().attr("id");
			//se il padre e' la radice
			if (padre==undefined){
				padre="";
				pos=""
			}
		}
		//creo il dizionario con i dati dentro
		var diz={};
		var barc=$(liscon[i]).attr("barc");
		diz['barcode']=barc;
		diz['conttipo']="";
		diz['geometry']="";
		diz['padre']=padre;
		diz['pos']=pos;		
		diz['aliq']="";		
		lista2.push(diz);
	}
}

//per spostare i container uno dentro l'altro e creare così la gerarchia
function crea_figli(){
	var listapadri=$(".barcpadri");
	var rapporti=$(".rapporti");
	//riempio un dizionario con le corrispondenze tra padri e figli
	for (var i=0;i<rapporti.length;i++){
		var padre=$(rapporti[i]).attr("padre");
		var figlio=$(rapporti[i]).attr("figlio");
		var pos=$(rapporti[i]).attr("pos");
		diztemp[figlio]=padre+"|"+pos;
	}
	for (var i=0;i<listapadri.length;i++){
		var barc=$(listapadri[i]).attr("fath");
		//se il container in questione non e' figlio di nessuno, non lo considero
		if (diztemp[barc]!=undefined){
			var val=diztemp[barc].split("|");
			var padre=val[0];
			var pos=val[1];
			//cambio la classe al figlio 
			$(listapadri[i]).parent().attr("class","divint"+padre);
			var testodiv=$(listapadri[i]).text();
			var testofin=testodiv+" in "+pos;
			$(listapadri[i]).text(testofin);
			$(listapadri[i]).siblings(".checkest").attr("position",pos);
			//prendo il codice html di tutta la div, cosi' da spostarlo in toto all'interno 
			//del giusto padre
			var divgroup=$(listapadri[i]).parent().parent().html();
			var id="#"+padre;
			var divpadre=$(id);
			$(divpadre).prepend(divgroup);
			$(listapadri[i]).parent().parent().remove();
		}
	}
}

//per disabilitare tutte le foglie in modo che l'accordion non si apra
function blocca_padri_figli(){
	var lisvuoti=$(".vuoti");
	for (var i=0;i<lisvuoti.length;i++){
		var barc=$(lisvuoti[i]).val();
		var divinterna=$(".barcpadri[fath='"+barc+"']").parent();
		$(divinterna).addClass("ui-state-disabled");
		$(divinterna).children("span").attr("class","");
	}
	//disabilito tutti i cont senza figli
	$(".figliint").addClass("ui-state-disabled");
	$(".figliint").children("span.ui-accordion-header-icon").attr("class","");
}

//per togliere il checkbox e mettere l'icona info nei container gia' presenti nel DB
function trova_presenti(){
	var listapresenti=$(".presenti");
	for (var i=0;i<listapresenti.length;i++){
		var barcode=$(listapresenti[i]).val();
		var tipocont=$(listapresenti[i]).attr("padre");
		var padrecheck=$(".checkint[barc='"+barcode+"'], .checkest[fath='"+barcode+"']").parent();
		var barcpadre=$(".checkint[barc='"+barcode+"']").attr("fath");
		var posfiglio=$(".checkint[barc='"+barcode+"']").attr("position");
		if (posfiglio==undefined){
			posfiglio=$(".checkest[fath='"+barcode+"']").attr("position");
		}
		//var padrecheckest=$(".checkest[fath='"+barcode+"']").parent();
		$(".checkint[barc='"+barcode+"'], .checkest[fath='"+barcode+"']").remove();
		if (padrecheck.length!=0){
			$(padrecheck).children(".brclear").remove();
			//$(padrecheckint).append("<img src='/archive_media/img/ok2.png' width='15' height='15' class='contpres' barc='"+barcode+"' >");
			$(padrecheck).append("<span class='contpres' style='float:right;margin-right:0.5em;' barc='"+barcode+"' fath='"+barcpadre+"' pos='"+posfiglio+"' >?</span><h2 class='h2tipo' style='float:right;margin:0em 1.5em 0 0;padding:0;'>"+tipocont+"</h2>");
		}
	}
}

function inserisci_container(){
	
	//devo vedere se sono stati inseriti tutti i dati
	var regex=/^[0-9]+$/;
	var bloccato=false;
	var tab=$("#cont_table").dataTable();
	
	var tipi=$("#id_tipi option:selected").val();
	var nometipo=$("#id_tipi option:selected").text();
	if(tipi==""){
		alert("Select container type");
		bloccato=true;
	}
	
	var lisaliq=$("#id_Aliquot_Type option:selected");
	if (lisaliq.length==0){
		alert("Select biological content");
		bloccato=true;
	}
	//guardo se sono state inserite le colonne
	var colo=$("#id_col").val();
	if(colo==""){
		alert("Insert columns number");
		bloccato=true;
	}
	else{
		if((!regex.test(colo))||(colo=="0")){
			alert("You can only insert number. Please correct columns value");
			bloccato=true;
		}
	}
	//guardo se sono state inserite le righe
	var rig=$("#id_row").val();
	if(rig==""){
		alert("Insert rows number");
		bloccato=true;
	}
	else{
		if((!regex.test(rig))||(rig=="0")){
			alert("You can only insert number. Please correct rows value");
			bloccato=true;
		}
	}
	//guardo se sono stati selezionati dei container
	var liscont=$(".checkest:checked, .checkint:checked");
	if (liscont.length==0){
		alert("Please select some containers");
		bloccato=true;
	}
	
	if(!bloccato){
		var timer = setTimeout(function(){$("body").addClass("loading");},1000);
		var geom=rig+"x"+colo;
		var lisaliq=$("#id_Aliquot_Type option:selected");
		var tipialiq="";
		for(var i=0;i<lisaliq.length;i++){
			var id=$(lisaliq[i]).val();
			tipialiq+=id+"&";
		}
		tipialiq = tipialiq.substring(0, tipialiq.length - 1);
		var diziobarc={};
		for (var j=0;j<liscont.length;j++){
			var barc=$(liscont[j]).attr("barc");
			var pos=$(liscont[j]).attr("position");
			//ho bisogno del padre del container
			if($(liscont[j]).attr("class")=="checkint"){
				var padre=$(liscont[j]).attr("fath");
			}
			else if($(liscont[j]).attr("class")=="checkest"){
				//devo prendere l'id del nonno, che contiene il barc del padre del container
				var padre=$(liscont[j]).parent().parent().attr("id");
				//devo vedere se sto trattando una radice della gerarchia
				if(padre==undefined){
					padre="";
					pos="";
				}
			}
			diziobarc[barc]=padre+"|"+pos;
		}
		//mi occupo dei dati da inviare alla API per effettuare il controllo
		//comunico la struttura dati al server
    	var data = {
    			dizbarc:JSON.stringify(diziobarc),
    			tipo:tipi,
    			geom:geom,
    			aliq:tipialiq
	    };
		var url=base_url+"/api/validate/container";
		
		$.ajax({
			  type: 'POST',
			  url: url,
			  data: data,
			  success: function (result) {
			    	if (result == "failure") {
			    		alert("Error in sending data");
			    	}
			    	else{
			    		if (result.data!="ok"){
			    			//faccio vedere il messaggio di errore
			    			alert(result.data);
			    		}
			    		else{
			    			
			    			for (var k=0;k<liscont.length;k++){
			    				var barc=$(liscont[k]).attr("barc");
			    				var dati=diziobarc[barc].toString().split("|");
			    				//var pos=$(liscont[k]).attr("position");
			    				var padre=dati[0];
			    				var pos=dati[1];
			    				if (pos==undefined){
			    					pos="";
			    				}
			    				//devo verificare se questo barcode non l'ho gia' inserito nella lista di dizionari
			    				for (var j=0;j<listagen.length;j++){
			    					var barcnuovo=listagen[j]['barcode'];
			    					if (barcnuovo==barc){
			    						//var indice=listagen[j]['indice'];
			    						var listatd = tab.$(".barctabellafin");
			    						for (var i=0;i<listatd.length;i++){
			    							var barctabella=$(listatd[i]).text();
			    							if (barctabella==barc){
			    								var nTr = $(listatd[i]).parents('tr')[0];
			    								tab.fnDeleteRow( nTr );
			    							}
			    						}
			    						listagen.splice(j,1);
			    						break;
			    					}
			    				}
			    				var posriga=tab.fnAddData( [contacont,barc, nometipo,geom,padre,pos ] );
			    				
			    				var usosingolo="n";
			    				if($("#id_use").is(":checked")){
			    					usosingolo="s";
			    				}
				    			
			    				//creo il dizionario con i dati dentro
				    			var diz={};
				    			diz['barcode']=barc;
				    			diz['conttipo']=tipi;
				    			diz['geometry']=geom;
				    			diz['padre']=padre;
				    			diz['pos']=pos;
				    			diz['uso']=usosingolo;
				    			
				    			diz['aliq']=tipialiq;

				    			listagen.push(diz);
				    			//console.log(listagen);
				    			contacont++;
			    			}
			    			var lischecktot=$(".checkest, .checkint, .contpres");
			    			$(liscont).removeAttr("checked");
			    			//per cancellare i nomi gia' presenti del tipo di container
			    			$(liscont).siblings(".h2tipo").remove();
			    			$(liscont).after("<h2 class='h2tipo' style='float:right;margin:0.1em 1em 0 0;padding:0;'>"+nometipo+"</h2>");
			    			$(liscont).attr("inserito","s");
			    			var listafatti=$(":checkbox[inserito='s'], .contpres");
			    			if(listafatti.length==lischecktot.length){
			    				$("#confermafinale").attr("disabled",false);
			    			}
			    		}
			    	}
			    	clearTimeout(timer);
					$("body").removeClass("loading");
					
			  },
			  //async:false
			});
	}
}

function infobox(span){
	var codice=$(span).attr("barc");
	//chiamo la api per recuperare le informazioni del container
	var url=base_url+"/api/info/container/"+codice+"/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			var testobox="Container type: "+d.tipo+"<br>Geometry: "+d.geom+"<br>Biological content: "+d.tipialiquote;
			$.fancybox(testobox,{height:"auto"});
		}
	});   
}

$(document).ready(function () {
	crea_figli();
	trova_presenti();
	aggiungi_cont();
	$('.contpres').click(function(event){
    	event.stopPropagation();
        infobox(this);
    });

	$(".anchor").popupWindow({ 
		height:500, 
		width:800, 
		top:50, 
		left:50,
		scrollbars:1,
		resizable:1,
		menubar:1
	}); 
	
	$("#tastofile").click(function(){
		$("#id_file_cont").click();
	});
	
	//per far comparire nell'input i nomi dei file caricati
	$("#id_file_cont").change(function(){
		var files = $('#id_file_cont')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
		$("#conferma").attr("disabled",false);
	});
	
	$( "#accordion" ).accordion({
      header: ".divinterna",
      heightStyle: "content",
      collapsible: true,
      active:false
    })
    .sortable({
      axis: "y",
      handle: ".divinterna",
      stop: function( event, ui ) {
        ui.item.children( ".divinterna" ).triggerHandler( "focusout" );
      }
    });
	
	for (var k in diztemp){
		var val=diztemp[k].split("|");
		var padre=val[0];
		var id="#"+padre;
		var head=".divint"+padre;
		$( id ).accordion({
		      header: head,
		      heightStyle: "content",
		      collapsible: true,
		      active:false
		    })
		    .sortable({
		      axis: "y",
		      handle: head,
		      stop: function( event, ui ) {
		        ui.item.children( head ).triggerHandler( "focusout" );
		      }
		    });
	}	
	
	var idaccordion2=".acc";
	var head2=".figliint";
	$( idaccordion2 ).accordion({
	      header: head2,
	      heightStyle: "content",
	      collapsible: true,
	      active:false
	    })
	    .sortable({
	      axis: "y",
	      handle: head2,
	      stop: function( event, ui ) {
	        ui.item.children( head2 ).triggerHandler( "focusout" );
	      }
	    });
	
	blocca_padri_figli();
	
	$(".checkest").click(function(event){
		event.stopPropagation();
	});
	
	$(".checkfigli").click(function(event){
		event.stopPropagation();
		var tab=$(this).parent().parent().parent().parent().dataTable();
		var righetab=tab.$("tr");
		//seleziono anche tutti i check interni a questo container
		var selez=$(this).is(':checked');
		if(selez){
			$(righetab).find(".checkint").attr("checked","checked");
		}
		else{
			$(righetab).find(".checkint").removeAttr("checked");
		}
	});
	
	//spostarighe_figli();
	
	$(".tabcont").dataTable({
		
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
	});
	
	/*$("#tabpadri").dataTable({
		
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": false,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
		"iDisplayLength": -1,
	});*/
	
	/*$('#tabpadri').dataTable().rowGrouping({
		bExpandableGrouping: true,
		bExpandableGrouping2: true,
		bExpandSingleGroup: false,
        iExpandGroupOffset: -1,
		asExpandedGroups: [""],
		fnOnGrouped: function( aoGroups ) { 
			spostarighe_figli();
		}
	});*/
	
	
	//$('#tabpadri').dataTable().rowGroupingWithColapsableSecondLevel({  "iGroupingColumnIndex2": 1 , "bExpandableGrouping": true, asExpandedGroups: [""] });
	
	var oTable = $("#cont_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "ID Operation"},
            { "sTitle": "Barcode",
              "sClass": "barctabellafin"},
            { "sTitle": "Type" },
            { "sTitle": "Geometry" },
            { "sTitle": "Father" },
            { "sTitle": "Position" },
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[0, 'desc']],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
	
	$("#selpadri").click(selpadri);
	$("#selfigli").click(selfigli);
	
	var spinner = $("#id_col,#id_row").spinner(
	{
		min:1,
		max:1000
	});
	
	//per il tasto che seleziona tutti i tipi di aliquota
	$("#seltutto").click(selezionatutto);
	//per aggiornare i tipi di container
	$("#id_generic").change(aggiorna_tipi_cont);
	//per l'autocompletamento sul container padre
	$("#id_tipi").change(assegna_geometria);
	
	$("#insert").click(inserisci_container);
	//per selezionare tutti i figli di un singolo contenitore
	$(".seleztutto").click(seltuttifigli);
	
	//quando clicco sul pulsante submit
    $("#confermafinale").click(function(event){
    	//var timer = setTimeout(function(){$("body").addClass("loading");},1000);
    	$("body").addClass("loading");
    	//devo vedere che siano state inserite tutte le informazioni per i vari container
    	event.preventDefault();
    	var lischecktot=$(".checkest, .checkint, .contpres");
    	var listafatti=$(":checkbox[inserito='s'], .contpres");
		if(listafatti.length!=lischecktot.length){
			alert("Please insert information for all containers")
		}
		else{
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			batch:true,
	    			dati:JSON.stringify(listagen),
	    			lista2:JSON.stringify(lista2),
		    };
			var url=base_url+"/container/insert/";
			
			$.ajax({
				type: 'POST',
				url: url,
				data: data,
				success: function (result) {
				  	if (result == "failure") {
				  		alert("Error in sending data");
				   	}
				  	$("body").removeClass("loading");
				   	$("#form_fin").append("<input type='hidden' name='final' />");
				   	$("#form_fin").submit();
				},
				async:false
			});
		}
	});
	
});
