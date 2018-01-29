var listagen=new Array();
//dizionario con dentro tutti i valori cifrati e la relativa cifratura
var diziomasch={};
var dizgenerale={};
var dizselez={};
var dizfiltro={};
//dizionario per la maschera clinica con chiave il paziente e valore la lista delle collezioni
var dizcollezparam={}
var lastChecked;
var listamiti;
var pazselez;
//lista delle colonne visualizzate
var listacol=new Array();
//lista con una serie di true e false per ogni colonna per sapere se il relativo campo
//va cifrato o no
var listacript=new Array();
//lista con dentro dei dizionari, ognuno dei quali contiene i valori di un'aliquota selezionata,
//cioe' quella posizionata nella tabella sotto
var listaaldef=new Array();
//dizionario per la maschera clinica
diztasti={};

function cerca_gen(gen){
	for (i=0;i<listagen.length;i++){
		if (listagen[i]==gen){
			return true;
		}
	}
	return false;
}

function cambiaData(){
	var operatore=$("#confrontodata option:selected").attr("value");
	if ((operatore=="=")||(operatore=="<")){
		//disabilito l'altro campo per la data
		$("#confrontodata2,#dateto").attr("disabled",true);
	}
	else{
		$("#confrontodata2,#dateto").attr("disabled",false);
	}
}

function filtracollezione(){
	var timer = setTimeout(function(){$("body").addClass("loading");},50);
	var utente=$("#id_utente option:selected").val();
	if(utente==""){
		utente="None";
	}
	
	var ospedale=$("#id_place option:selected").val();
	if(ospedale==""){
		ospedale="None";
	}
	
	var tipo=$("#id_coll_type option:selected").val();
	if(tipo==""){
		tipo="None";
	}
	
	var aliqtipo=$("#id_aliq_type option:selected").val();
	if(aliqtipo==""){
		aliqtipo="None";
	}
	
	var datadal=$("#datefrom").val();
	if (datadal==""){
		var datatot="None";
	}
	else{
		var oper=$("#confrontodata option:selected").val();
		var datatot=oper+"_"+datadal;
	}
	
	var dataal=$("#dateto").val();
	if (dataal==""){
		dataal="None";
	}
	
	var protocol=$("#id_protocol option:selected").val();
	if(protocol==""){
		protocol="None";
	}
	
	var consenso=$("#id_infconsent").val();
	if (consenso==""){
		consenso="None";
	}

	var url=base_url+"/api/patientlist/"+utente+"/"+ospedale+"/"+tipo+"/"+aliqtipo+"/"+datatot+"/"+dataal+"/"+protocol+"/"+consenso;
	//API che mi da' la lista degli id dei pazienti, tenendo conto dei vari filtri messi dall'utente
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			$("#tabesterna,#tabaliq,#patient,#inizio2").css("display","");
			var listamasc=$("#id_mask").children();
			if (listamasc.length!=0){
				$("#inizio3").css("display","");
			}
			else{
				//metto al centro il filtro per le aliquote
				$("#inizio2").css("float","");
			}
			$("#aliq_wrapper,#alconferm_wrapper,#down,#up,#tdexport,#tabclinical").css("display","none");
			var listapaz=JSON.parse(d.data);
			
			var tab2=$("#patient").dataTable({
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"bInfo": true,
				"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
				"bAutoWidth": false,
				"bDestroy": true });
			tab2.fnClearTable();
			//$("#patient_wrapper,#aliq_wrapper").css("width","25%");
			$("#patient_filter input").attr("size","7");
			
			for(var i=0;i<listapaz.length;i++){	
				tab2.fnAddData( [(i+1), listapaz[i] ] );
			}
			if(listapaz.length!=0){
				tab2.$("tr").click(visualizza_aliquote);
			}
		}
		clearTimeout(timer);
        $("body").removeClass("loading");
	});
}

function visualizza_aliquote(event){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	
	var tab=$("#patient").dataTable();
	$(tab.fnSettings().aoData).each(function (){
		$(this.nTr).removeClass('row_selected');
	});
	$(event.target.parentNode).addClass('row_selected');
	var anSelected = fnGetSelected( tab );
	//prendo il codice del paziente
	var codpaz=$(anSelected[0]).children(":nth-child(2)").text();
	pazselez=codpaz;
	
	var aliqtipo=$("#id_aliq_type option:selected").val();
	if(aliqtipo==""){
		aliqtipo="None";
	}
	
	var tesstipo=$("#id_tissue_type option:selected").val();
	if(tesstipo==""){
		tesstipo="None";
	}
	
	var vett=$("#id_vector option:selected").val();
	if(vett==""){
		vett="None";
	}
	var maschera=$("#id_mask option:selected").val();
	var nomemaschera=$("#id_mask option:selected").text();
	if (maschera==undefined){
		maschera="None";
	}
	
	//devo vedere se richiamare la API o no. La chiamo solo se non c'e' quel cod paziente nel dizionario
	//e se sono cambiati i parametri di filtro sulle aliquote
	if (!(dizgenerale.hasOwnProperty(pazselez))){
		var diztemp={}
		diztemp['aliqtipo']=aliqtipo;
		diztemp['tesstipo']=tesstipo;
		diztemp['vettore']=vett;
		diztemp['masc']=maschera;
		dizfiltro[pazselez]=diztemp;
	}
	else{
		var aliqtipogene=dizfiltro[pazselez]['aliqtipo'];
		var tesstipogene=dizfiltro[pazselez]['tesstipo'];
		var vettgene=dizfiltro[pazselez]['vettore'];
		var mascgene=dizfiltro[pazselez]['masc'];
	}
	if (!(dizgenerale.hasOwnProperty(pazselez))||((aliqtipogene!=aliqtipo)||(tesstipogene!=tesstipo)||(vettgene!=vett)||(mascgene!=maschera))){
		if(nomemaschera!="Clinical"){
			var diztemp={}
			diztemp['aliqtipo']=aliqtipo;
			diztemp['tesstipo']=tesstipo;
			diztemp['vettore']=vett;
			diztemp['masc']=maschera;
			dizfiltro[pazselez]=diztemp;
			var utente=$("#actual_username").val();
			var url=base_url+"/api/patientaliqinfo/"+codpaz+"/"+aliqtipo+"/"+tesstipo+"/"+vett+"/"+maschera+"/"+utente;
			//API che mi da' la lista dei campioni di un certo paziente, tenendo conto dei filtri impostati dall'utente
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					
					$("#down,#up").css("display","inline");
					
					//prendo quello che c'era nella tabella di sotto se non era vuota
					var listavuota=$("#alconferm tbody tr td.dataTables_empty");
					if (listavuota.length==0){
						var listatr=$("#alconferm tbody tr");
						//se e' la prima volta in assoluto che entra qui
						if (listatr.length==0){
							var dativecchi=$("#alconferm tbody").html();
						}
						else{
							//ci sono gia' delle righe nel data table
							var tabtt=$("#alconferm").dataTable();
							var listatr=tabtt.$("tr");
							var dativecchi="";
							for (var i=0;i<listatr.length;i++){
								dativecchi+="<tr>"+$(listatr[i]).html()+"</tr>";
							}
						}
					}
					else{
						var dativecchi="";
					}
	
					//cancello le vecchie tabelle
					$("#tdaliq,#tdalconferm").children().remove();
					$("#tdaliq").append("<table id='aliq' border='1px' style='display:none;'><thead></thead><tbody></tbody></table>");
					$("#tdalconferm").append("<table id='alconferm' border='1px' style='display:none;'><thead></thead><tbody>"+dativecchi+"</tbody></table>");
					
					
					//aggiungo le colonne delle tabelle
					listacol=JSON.parse(d.colonne);
					
					var listacolfin=new Array();
					var strtemp="";
					for (var k=0;k<listacol.length;k++){
						strtemp+="<th>"+listacol[k]+"</th>";
						var dizcol=new Array();
						dizcol["sTitle"]=listacol[k];
						//dizcol["aTargets"]=[k];
						listacolfin.push(dizcol);
					}
					
					//Queste due righe non servono perche' definisco le colonne gia' con aoColumns.
					//Se le mettessi non mi farebbe piu' ordinare i dati nella tabella
					//$("#aliq thead,#alconferm thead").children().remove();
					//$("#aliq thead,#alconferm thead").append(strtemp);
					
					$("#tabesterna,#tabaliq,#aliq,#alconferm,#tdexport").css("display","");
					$("#tabclinical").css("display","None");
					
					listacript=JSON.parse(d.cript);
					//oTable.fnReloadAjax();
					var tab=$("#aliq,#alconferm").dataTable({
						"bPaginate": true,
						"bLengthChange": true,
						"bFilter": true,
						"bSort": true,
						"aaSorting": [[ 7, "asc" ]],
						"bInfo": true,
						"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
						"bAutoWidth": false,
						"bDestroy": true,
						"aoColumns": listacolfin});
					//tab.fnClearTable();
					var tt=$("#alconferm").dataTable();
					tt.$("tr").click( function() {
				        $(this).toggleClass('row_selected');
				    });
					
					var listaaliq=JSON.parse(d.data);
					dizgenerale[pazselez]=listaaliq;
									
					//inserisco i dati nella tabella sopra
					for (aliq in listaaliq){
						var genid=listaaliq[aliq]['genid'];
						var paz=listaaliq[aliq]['patient'];
						//se il campione non e' gia' stato inserito nella tabella sotto, allora lo posso inserire
						//nella tabella sopra
						if(!cerca_gen(genid)){
							
							//carico in una lista tutti i valori di quell'aliquota e poi do' la lista al data table
							var listavalfin=new Array();
							for (var k=0;k<listacol.length;k++){
								var valore=listaaliq[aliq][listacol[k]];
								//in listacript ho una serie di True e False che mi dicono se quel campo va criptato o no
								if ((listacript[k]==true)&&(valore!="")){
									var valfinale=creamaschera(valore);
								}
								else{
									var valfinale=valore;
								}					
								if (k==0){
									valfinale+="<input type='hidden' value='"+genid+"' />";
								}
								if (k==1){
									valfinale+="<input type='hidden' value='"+paz+"' />";
								}							
								listavalfin.push(valfinale);
							}
							
							$("#aliq").dataTable().fnAddData( listavalfin /*[tipocoll+"<input type='hidden' value='"+genid+"' />", cas+"<input type='hidden' value='"+paz+"' />",tess,tipoal,alid,info,dat,barc,avail ]*/ );
						}
					}
					
					tab.$("tr").click(  function(event) {
						//$(this).toggleClass('row_selected');
						 if(!lastChecked) {
						        lastChecked = this;
						    }
						     
					    if(event.shiftKey) {
					        var start = $('#aliq tbody tr').index(this);
					        var end = $('#aliq tbody tr').index(lastChecked);
					 
					        for(i=Math.min(start,end);i<=Math.max(start,end);i++) {
					            if (!$('#aliq tbody tr').eq(i).hasClass('row_selected')){
					                $('#aliq tbody tr').eq(i).addClass("row_selected");
					            }
					        }
					         
					        // Clear browser text selection mask
					        if (window.getSelection) {
					            if (window.getSelection().empty) {  // Chrome
					                window.getSelection().empty();
					            } else if (window.getSelection().removeAllRanges) {  // Firefox
					                window.getSelection().removeAllRanges();
					            }
					        } else if (document.selection) {  // IE?
					            document.selection.empty();
					        }
					    } else if ((event.metaKey || event.ctrlKey)){
					        $(this).toggleClass('row_selected');
					    } else {
					        $(this).toggleClass('row_selected');  
					    }
					     
					    lastChecked = this;
						
				    });
				}
				clearTimeout(timer);
				$("body").removeClass("loading");
			});
		}
		//se la maschera e' quella per i dati clinici
		else{
			var diztemp={}
			diztemp['aliqtipo']=aliqtipo;
			diztemp['tesstipo']=tesstipo;
			diztemp['vettore']=vett;
			diztemp['masc']=maschera;
			dizfiltro[pazselez]=diztemp;
			var url=base_url+"/api/patientclinical/"+codpaz+"/"+aliqtipo+"/"+tesstipo+"/"+vett+"/";
			//API che mi da' la lista dei campioni di un certo paziente, tenendo conto dei filtri impostati dall'utente
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					//in d.data ho il dizionario con dentro i dati effettivi, in liscoll ho la lista delle collezioni ordinate
					//che devo seguire per popolare le tabelle
					var dizdati=JSON.parse(d.data);
					var liscoll=JSON.parse(d.liscoll);					
					maschera_clinica(dizdati,liscoll);
					
					dizgenerale[pazselez]=dizdati;
					dizcollezparam[pazselez]=liscoll;
				}
			});
			
			clearTimeout(timer);
			$("body").removeClass("loading");
		}
	}
	else{
		if(nomemaschera!="Clinical"){
			$("#tabesterna,#tabaliq,#aliq,#alconferm").css("display","");
			$("#tabclinical").css("display","None");
			$("#down,#up").css("display","inline");
			
			var listacolfin=new Array();
			for (var k=0;k<listacol.length;k++){
				var dizcol=new Array();
				
				dizcol["sTitle"]=listacol[k];
				listacolfin.push(dizcol);
			}
			
			var tab=$("#aliq,#alconferm").dataTable({
				"bPaginate": true,
				"bLengthChange": true,
				"bFilter": true,
				"bSort": true,
				"aaSorting": [[ 7, "asc" ]],
				"bInfo": true,
				"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
				"bAutoWidth": false,
				"bDestroy": true,
				"aoColumns": listacolfin });
			tab.fnClearTable();
			var listaaliq=dizgenerale[pazselez];
			//inserisco i dati nella tabella sopra
			for (aliq in listaaliq){
				var genid=listaaliq[aliq]['genid'];
				var paz=listaaliq[aliq]['patient'];
				//se il campione non e' gia' stato inserito nella tabella sotto, allora lo posso inserire
				//nella tabella sopra
				if(!cerca_gen(genid)){
					//mi occupo dei mascheramenti 
					//maschero la data
					var datareale=listaaliq[aliq]['date'];
					if ((maschera=='date')||(maschera=='case')){
						var datafin=creamaschera(datareale);
					}
					else{
						var datafin=datareale;
					}
					
					var caso=listaaliq[aliq]['case'];
					if (maschera=='case'){
						var casofin=creamaschera(caso);
					}
					else{
						var casofin=caso;
					}
					
					//carico in una lista tutti i valori di quell'aliquota e poi do' la lista al data table
					var listavalfin=new Array();
					for (var k=0;k<listacol.length;k++){
						var valore=listaaliq[aliq][listacol[k]];
						//in listacript ho una serie di True e False che mi dicono se quel campo va criptato o no
						if ((listacript[k]==true)&&(valore!="")){
							var valfinale=creamaschera(valore);
						}
						else{
							var valfinale=valore;
						}				
						if (k==0){
							valfinale+="<input type='hidden' value='"+genid+"' />";
						}
						if (k==1){
							valfinale+="<input type='hidden' value='"+paz+"' />";
						}
						
						listavalfin.push(valfinale);
					}
					
					$("#aliq").dataTable().fnAddData(listavalfin );
				}
			}
			tab.$("tr").click(  function(event) {
				//$(this).toggleClass('row_selected');
				 if(!lastChecked) {
				        lastChecked = this;
				    }
				     
			    if(event.shiftKey) {
			        var start = $('#aliq tbody tr').index(this);
			        var end = $('#aliq tbody tr').index(lastChecked);
			 
			        for(i=Math.min(start,end);i<=Math.max(start,end);i++) {
			            if (!$('#aliq tbody tr').eq(i).hasClass('row_selected')){
			                $('#aliq tbody tr').eq(i).addClass("row_selected");
			            }
			        }
			         
			        // Clear browser text selection mask
			        if (window.getSelection) {
			            if (window.getSelection().empty) {  // Chrome
			                window.getSelection().empty();
			            } else if (window.getSelection().removeAllRanges) {  // Firefox
			                window.getSelection().removeAllRanges();
			            }
			        } else if (document.selection) {  // IE?
			            document.selection.empty();
			        }
			    } else if ((event.metaKey || event.ctrlKey)){
			        $(this).toggleClass('row_selected');
			    } else {
			        $(this).toggleClass('row_selected');  
			    }
			     
			    lastChecked = this;
				
		    });
			
		}
		//se la maschera e' quella per i dati clinici
		else{
			var dizdati=dizgenerale[pazselez];
			var liscoll=dizcollezparam[pazselez];
			maschera_clinica(dizdati,liscoll);			
		}
		clearTimeout(timer);
		$("body").removeClass("loading");
	}	
}

//per popolare la tabella nel caso sia stata scelta la maschera clinica. Viene chiamata sia quando seleziono un nuovo
//paziente, sia quando l'ho gia' selezionato.
function maschera_clinica(dizdati,liscoll){
	$("#tdaccordion").children().remove();
	var stringa="<div id='accordion'>";
	for (var k=0;k<liscoll.length;k++){
		stringa+="<div class='divinterna' style='border-width:0.1em;border-color: black;'><h2 style='display:inline;font-size:1.2em;margin-left:2em;'>"+liscoll[k]+"</h2></div>"+
		"<div class='divtabelle'><table class='collection' border='1px'><thead><th>Father parameter</th><th>Parameter</th><th>Value</th><th>Operator</th><th>Date</th></thead><tbody>";
		
		var daticaso=dizdati[liscoll[k]];						
		for (var j=0;j<daticaso.length;j++){
			//devo vedere se c'e' un'unita' di misura
			var mis=daticaso[j]["unit"];
			var unita="";
			if(mis!=""){
				unita="("+mis+")";
			}
			stringa+="<tr><td>"+daticaso[j]["padre"]+"</td><td>"+daticaso[j]["feat"]+"</td><td>"+daticaso[j]["value"]+unita+"</td><td>"+daticaso[j]["operat"]+"</td><td>"+daticaso[j]["date"]+"</td></tr>";
		}
		stringa+="</tbody></table></div>";
	}
	if(liscoll.length==0){
		stringa+="<div class='divinterna' style='border-width:0.1em;border-color: black;'><h2 style='display:inline;font-size:1.2em;margin-left:2em;'>No data available</h2></div>"
	}
	stringa+="</div>";
	$("#tdaccordion").append(stringa);
	
	$( "#accordion" ).accordion({
	      header: ".divinterna",
	      heightStyle: "content",
	      collapsible: true,
	      active:false
	    });
	
	var tab2=$(".collection").dataTable({
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });	
	
	$(".divtabelle").css("height","");
	$("#tabaliq").css("display","None");
	$("#tabclinical").css("display","");
}

function creamaschera(chiave){
	if (diziomasch.hasOwnProperty(chiave)){
		return diziomasch[chiave];
	}
	else{
		var trovato=false;
        while (!trovato){
        	var lung=listamiti.length;
            var numero=Math.floor(Math.random()*lung);
            var mito=listamiti[numero].trim();
            //se quel valore non e' gia' tra i valori del dizionario
            var presente=false;
            for (var key in diziomasch){
            	if (diziomasch[key]==mito){
            		presente=true;
            		break;
            	}
            }
            if (!presente){
            	trovato=true;
            }
        }
        diziomasch[chiave]=mito;
        return mito;
	}
}

function inseriscidatisotto(){
	var tab=$("#aliq").dataTable();
	var tabsotto=$("#alconferm").dataTable();
	//ho un vettore con le righe selezionate dall'utente
	var selezionati = fnGetSelected( tab );
	if (selezionati.length==0){
		alert("Please select some aliquots");
	}
	else{
		//impedisco il cambiamento del tipo di maschera
		$("#id_mask").attr("disabled",true);
		for(var j=0;j<selezionati.length;j++){
			//aggiungo questo campione alla lista dei gen gia' selezionati e posizionati nella tabella sotto
			var gen=$(selezionati[j]).children(":nth-child(1)").children("input").val();
			listagen.push(gen);
			
			var listadatitemp=new Array();
			var listmp=new Array();
			for (var k=0;k<listacol.length;k++){
				var figlio=":nth-child("+(k+1)+")";
				var dato=$(selezionati[j]).children(figlio).html();
				listadatitemp.push(dato);
				var valore=$(selezionati[j]).children(figlio).text();
				listmp.push(valore);
			}
			//aggiungo i valori della riga nella tabella sotto
			/*var rowPos=tabsotto.fnAddData([$(selezionati[j]).children(":nth-child(1)").html(),$(selezionati[j]).children(":nth-child(2)").html(),
				               $(selezionati[j]).children(":nth-child(3)").html(),$(selezionati[j]).children(":nth-child(4)").html(),
				               $(selezionati[j]).children(":nth-child(5)").html(),$(selezionati[j]).children(":nth-child(6)").html(),
				               $(selezionati[j]).children(":nth-child(7)").html(),$(selezionati[j]).children(":nth-child(8)").html(),
				               $(selezionati[j]).children(":nth-child(9)").html()]);*/
			var rowPos=tabsotto.fnAddData(listadatitemp);
			var tableRowElement = tabsotto.fnGetNodes(rowPos[0]);
			//aggiungo l'evento click solo alla nuova riga
			$(tableRowElement).click( function() {
		        $(this).toggleClass('row_selected');
		    });
			//tolgo la riga dalla tabella sopra
			tab.fnDeleteRow( selezionati[j] );
			//aggiungo questa aliquota a quelle definitive
			var dizfinale={};
			dizfinale[gen]=listmp
			listaaldef.push(dizfinale);
			//abilito i tasti per il pdf e il csv
			$("#salvapdf,#salvacsv,#export,#id_exp").attr("disabled",false);
		}
	}
}

function inseriscidatisopra(){
	var tab=$("#aliq").dataTable();
	var tabsotto=$("#alconferm").dataTable();
	//ho un vettore con le righe selezionate dall'utente nella tabella sotto
	var selezionati = fnGetSelected( tabsotto );
	if (selezionati.length==0){
		alert("Please select some aliquots");
	}
	else{
		for(var j=0;j<selezionati.length;j++){
			//devo togliere questo campione dalla lista dei gen gia' selezionati e posizionati nella tabella sotto
			var gen=$(selezionati[j]).children(":nth-child(1)").children("input").val();
			for (var i=0; i < listagen.length; i++){
		        if (listagen[i] == gen){
		        	listagen.splice(i,1);
		        }
		    }
			//devo togliere questo campione dalla lista delle aliquote confermate per l'esportazione
			for (var i=0;i<listaaldef.length;i++){
				//se la chiave del dizionario e' proprio questo gen, allora tolgo l'elemento dalla lista
		        if (gen in listaaldef[i]){
		        	listaaldef.splice(i,1);
		        	break;
		        }
		    }

			//aggiungo i valori della riga nella tabella sopra solo se il paziente selezionato e' coerente
			var paz=$(selezionati[j]).children(":nth-child(2)").children("input").val();
			if (paz==pazselez){
				var listadatitemp=new Array();
				for (var k=0;k<listacol.length;k++){
					var figlio=":nth-child("+(k+1)+")";
					var dato=$(selezionati[j]).children(figlio).html();
					listadatitemp.push(dato);
				}
				/*var rowPos=tab.fnAddData([$(selezionati[j]).children(":nth-child(1)").html(),$(selezionati[j]).children(":nth-child(2)").html(),
					               $(selezionati[j]).children(":nth-child(3)").html(),$(selezionati[j]).children(":nth-child(4)").html(),
					               $(selezionati[j]).children(":nth-child(5)").html(),$(selezionati[j]).children(":nth-child(6)").html(),
					               $(selezionati[j]).children(":nth-child(7)").html(),$(selezionati[j]).children(":nth-child(8)").html(),
					               $(selezionati[j]).children(":nth-child(9)").html()]);*/
				var rowPos=tab.fnAddData(listadatitemp);
				var tableRowElement = tab.fnGetNodes(rowPos[0]);
				//aggiungo l'evento click solo alla nuova riga
				$(tableRowElement).click( function() {
			        $(this).toggleClass('row_selected');
			    });
			}
			//tolgo la riga dalla tabella sotto
			tabsotto.fnDeleteRow( selezionati[j] );
		}
		//se la tabella sotto e' vuota riabilito la modifica della maschera
		var listavuota=$("#alconferm tbody tr td.dataTables_empty");
		if (listavuota.length!=0){
			$("#id_mask").attr("disabled",false);
			//disabilito i tasti per il pdf e il csv
			$("#salvapdf,#salvacsv,#export,#id_exp").attr("disabled",true);
		}
	}
}

/* Get the rows which are currently selected */
function fnGetSelected( oTableLocal )
{
	var aReturn = new Array();
	var aTrs = oTableLocal.fnGetNodes();
	
	for ( var i=0 ; i<aTrs.length ; i++ )
	{
		if ( $(aTrs[i]).hasClass('row_selected') )
		{
			aReturn.push( aTrs[i] );
		}
	}
	return aReturn;
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
	//per cancellare beaming dagli scopi dell'esportazione
	var beam=$("#id_exp option:contains('Beaming results')").remove();	
}

//e' usata nella maschera clinica, quando clicco su una categoria
function loadInfo(idtasto,nometasto){
    if (diztasti.hasOwnProperty(idtasto)){
        //gia' caricato precedentemente dal server
        crea_elementi(diztasti[idtasto],nometasto);
    }else{
    	var tum=window.opener.$("#id_Tumor_Type option:selected").val();
    	//se tum non c'e' vuol dire che ho aperto la pagina dei parametri passando dalla schermata
    	//per riaprire una collezione. Quindi tum lo trovo nei parametri della URL
    	if(tum==undefined){
    		tum = getUrlParameter("tumor");
    	}
        //da caricare dal server
        jQuery.ajax({
            url: base_url + "/api/getClinicalFeature/" + idtasto + "/"+tum+ "/",
                type: 'get',
                success: function(d) {
                	if (d.data!="err"){
                		crea_elementi(d,nometasto);
                		diztasti[idtasto]=d;
                	}                    
                    else{
                    	alert("Error in server API");
                    }
                }
        });
    }
}

function crea_elementi(d,nometasto){
	var lis = JSON.parse(d.data);
	
	var lisdiv=$("div.princ");
	//se ho cliccato su un valore della lista principale a sinistra, livello varra' 2
	var livello=parseInt(d.livello);		
	//elimino le div piu' a destra di quella attuale
	for(var i=(livello-1);i<lisdiv.length;i++){
		lisdiv[i].remove();
	}
	//devo scrivere dopo l'ultima div presente
	var lisdiv=$("div.princ");
	//se ho una lista di altri parametri clinici generali che fanno da madre ad altre categorie
	if(d.listamadri){
		var codhtml="<div class='princ' style='float:left;width:20%;margin-left:1em;'><fieldset class='fieldset'><legend>"+nometasto+
		"</legend><div><table style='margin-left: auto;margin-right: auto;'><tbody>";
		for(var j=0;j<lis.length;j++){
			var diz=lis[j];
			codhtml+="<tr><td><button class='button' style='width:100%;' onclick ='loadInfo(\""+diz["id"]+"\",\""+diz["name"]+"\");'>"+diz["name"]+"</button></td></tr>";  
		}
		codhtml+="</tbody></table></div></fieldset></div>";		
	}
	else{
		var codhtml="<div class='princ' style='float:left;width:20%;margin-left:1em;'><fieldset class='fieldset'><legend>"+nometasto+
		"</legend><div><table border='1px' style='margin-left: auto;margin-right: auto;width:100%;'><tbody>";
		//se ho una lista di parametri foglie	
		for(var j=0;j<lis.length;j++){
			var diz=lis[j];
			var listemp=diz["lisval"];
			dizvalpredef[diz["id"]]=listemp;
			var checked="";
			//serve nel caso clicchi di nuovo su quel tasto, allora devo vedere i checkbox gia' selezionati
			for (var k=0;k<lisfin.length;k++){
				var diztemp=lisfin[k];
				if(diztemp["idfeat"]==diz["id"]){
					checked="checked='checked'";
					break;
				}
			}
			var classespan="span_feat";
			var disabled="";
			if((diz["type"]=="List")&&(listemp.length==0)){
				disabled="disabled='disabled'";
				classespan="";
			}
			//se il parametro e' di tipo TextTumor e la lista e' vuota non lo faccio vedere perche' vuol dire che quel parametro ha senso
			//per un altro tumore
			var blocca=false;
			if((diz["type"]=="TextTumor")&&(listemp.length==0)){
				blocca=true;
			}
			if(!(blocca)){
				codhtml+="<tr><td><input type='checkbox' class='check_feat' "+checked+" "+disabled+" idfeat='"+diz["id"]+"' tipo='"+diz["type"]+"' unit='"+diz["unit"]+"' value='"+diz["name"]+"'><span class='"+classespan+"' >"+diz["name"]+"</span></td></tr>";
			}
		}
		codhtml+="</tbody></table></div></fieldset></div>";
		if(lis.length==0){
			codhtml="";
		}
	}
	$(lisdiv[lisdiv.length-1]).after(codhtml);
	$(":checkbox.check_feat").click(function(){valori_checkbox(this);});
	//faccio in modo di far sentire il click anche se e' sul testo del checkbox
	$(".span_feat").click(function(){
		var check=$(this).parent().children(":checkbox");
		if($(check).is(":checked")){
			$(check).removeAttr("checked");
		}
		else{
			$(check).attr("checked","checked");
		}
		valori_checkbox(check);
	});
}

$(document).ready(function () {
	$("#datefrom,#dateto").datepicker({
		 //changeMonth: true,
		 //changeYear: true,
		 dateFormat: 'yy-mm-dd'
	});
	
	//per il demo. Serve a cancellare tutti gli utenti diversi da quello attuale
	//cancella_utenti();
	
	$("#id_infconsent").attr("size","10");
	$("#id_infconsent").parent().after("<br>");
	
	$( "#id_infconsent" ).autocomplete({
      source: function(request, response) {
          var results = $.ui.autocomplete.filter(lisconsensi, request.term);

          response(results.slice(0, 10));
      }
    });
	
	//devo chiamare la API che mi dia il valore di mascheramento
	var url=base_url+"/api/mask/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			listamiti=JSON.parse(d.data);
		}
	});
	
	$("#filtercoll").click(filtracollezione);
	$("#down").click(inseriscidatisotto);
	$("#up").click(inseriscidatisopra);
	$("#salvapdf,#salvacsv,#export,#id_exp").attr("disabled",true);
	$("#id_mask").attr("disabled",false);
	
	//quando clicco sul pulsante del pdf
    $("#salvapdf").click(function(event){
    	event.preventDefault();
    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(listaaldef),
    			colonne:JSON.stringify(listacol),
	    };
		var url=base_url+"/patient/createPDF";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	
	    	$("#form_pdf").append("<input type='hidden' name='final' />");
	    	$("#form_pdf").submit();
	    });
	});
    
  //quando clicco sul pulsante del csv
    $("#salvacsv").click(function(event){
    	event.preventDefault();
    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(listaaldef),
    			colonne:JSON.stringify(listacol),
	    };
		var url=base_url+"/patient/createCSV";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	
	    	$("#form_csv").append("<input type='hidden' name='final' />");
	    	$("#form_csv").submit();
	    });
	});
    
  //quando clicco sul pulsante per esportare
    $("#export").click(function(event){
    	event.preventDefault();
    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(listaaldef),
    			colonne:JSON.stringify(listacol),
	    };
		var url=base_url+"/patient/export";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	
	    	$("#form_exp").append("<input type='hidden' name='final' />");
	    	$("#form_exp").submit();
	    });
	});
});

