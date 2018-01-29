posiz=false;
blocca=false;
vettore_posiz={};
calcola=false;
aliq=false;
carica=false;
lista_aliq=new Array();
lista_container_usati={};
barcode_piastra=""

//serve per aggiungere tante caselle quante sono le aliquote che si vogliono creare
function aggiungi_campi_tabella(){
	numero=$("#id_number_aliquots").attr("value");
	if(numero!=""){
		aliq=true;
		if (carica==true){
        	$("#pos,#vert_pos").attr("disabled",false);
        }
		var celle=$("#aliq tr>th");
		//celle e' il numero attuale di celle della tabella
		var numcelle=(celle.length);
		var num=numero-numcelle+2;
		if(num>=0){
			$("#id_aliquot").attr("onFocus","$(\"#nuova_aliquota\").attr(\"disabled\",false);");
			for(i=0;i<num;i++){
				$("#aliq tr>th:last").after("<th>Aliquot "+(i+numcelle-1)+"</th>");
				$("#aliq tr>td:last").after("<td align=\"center\" style=\" padding: 8px;border-width:1px;\">"+
				"<div><label for=\"volume_"+(i+numcelle-2)+"\" >Volume(ul):</label>"+
				"<input id=\"volume_"+(i+numcelle-2)+"\"onFocus='calcola=false;' type=\"text\" size=\"4\" name=\"volume_"+(i+numcelle-2)+"\" maxlength='7'>"+
				"<label for=\"concentration_"+(i+numcelle-2)+"\" '>Concentration<br>(ng/ul):</label>"+
				"<input id=\"concentration_"+(i+numcelle-2)+"\"onFocus='calcola=false;' type='text' size='4' name=\"conc_"+(i+numcelle-2)+"\" maxlength='7'>"+
				"<label for=\"moth_"+(i+numcelle-2)+"\" >Mother(ul):</label>"+
				"<input id=\"moth_"+(i+numcelle-2)+"\"onFocus='calcola=false;' readonly='readonly' type=\"text\" size=\"4\" name=\"vol_madre_"+(i+numcelle-2)+"\" maxlength='7'>"+
				"<label for=\"h2o_"+(i+numcelle-2)+"\" '>H2O(ul):</label>"+
				"<input id=\"h2o_"+(i+numcelle-2)+"\"onFocus='calcola=false;' readonly='readonly' type='text' size='4' name=\"acqua_"+(i+numcelle-2)+"\" maxlength='7'>"+
				"</div>"+
				"</td>")
			}
			$("#aliq tr>th").css("background-color","silver");
			$("#aliq tr>th:first").css("background-color","#E8E8E8");
			//coloro l'aliquota madre di rosso
			$("#aliq tr>th:nth-child(2)").css("background-color","#E8E8E8");
			
			//creo le aliq da posizionare
			crea_aliquote(numero);
		}
		else{
			if(numero<1){
				alert("Value has to be at least 1");
			}
			else{
				val=numcelle-numero-2;
				for(i=0;i<val;i++){
					$("#aliq tr>th:last").remove();
					$("#aliq tr>td:last").remove();
				}
	
				crea_aliquote(numero);
				copia_valori_ricalcola();
			}
		}
	}
	else{
		alert("Insert aliquots number");
	}
}

function copia_vecchi_valori(){
	//vedo il numero di aliq nel campo nascosto. Se � 0 vuol dire che sono al primo
	//passaggio nella schermata di split e quindi non devo copiare niente. Altrimenti
	//metto i valori di vol e conc della sessione passata
	var num_al=parseInt($("#tot_ali").val());
	if (num_al!=0){
		for (var i=0;i<num_al;i++){
			var vol_temp=$("#vol_"+i).val();
			var conc_temp=$("#con_"+i).val();
			$("#volume_"+i).val(vol_temp);
			$("#concentration_"+i).val(conc_temp);
		}
	}
}

function piastra_definitiva(nameP,codice,tipo,radio,d){
	$("#" + nameP ).replaceWith(d);
    $("#" + nameP + " button").css("background-color","rgb(249,248,242)");
    
    if ((posiz==false)&&(aliq==true)){
    	$("#pos,#vert_pos").attr("disabled",false);
    }
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
    //metto classe=mark nelle celle in cui non voglio che venga
	//posizionato un tasto con il drag and drop
	$("#rna th,.intest").attr("class","mark");
	$("#rna button[sel=\"s\"]").parent().attr("class","mark");
	$("#rna button[sel=\"s\"]").text("#");
	$("#rna button[sel=\"s\"], #rna button:contains(X)").css("background-color","#E8E8E8");
	$("#rna button:contains(X)").parent().attr("class","mark");
	//per bloccare la cella in alto a sinistra solo se e' una piastra e non una provetta
	if (radio=="plate"){
		$("#rna tr:nth-child(2)").children(":first-child").attr("class","mark");
	}
    
	var numero=$("#id_number_aliquots").attr("value");
	//vedo se in quella piastra avevo gia' caricato qualcosa prima e lo
	//faccio comparire nella piastra
	//prendo il valore dell'indice della serie che sto derivando
	var indice=$("#indice").val();
	for(i=1;i<(numero+1);i++){
		if(vettore_posiz[i]!=undefined){
			//se ho gia' caricato qualcosa nella piastra non posso piu' 
			//fare il posizionamento automatico
			$("#pos,#vert_pos").attr("disabled",true);
			var valore=vettore_posiz[i];
			valore=valore.split("|");
			//solo se la piastra a cui si riferisce l'aliq e' questa
			if (valore[1]==codice){		
				$("#s-"+valore[0]).children().replaceWith("<div class='drag' num='"+i+"' align='center'>"+indice+"</div>");
			}
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
	    "<input type='hidden' name='tipopiastra_"+((hidden.length-1)/2)+"' value="+tipo+" />"+codice+" "+tipo;   
	    $("#listapias td:last").click(carica_piastra_scelta);
	}
	$("#rna br").remove();
	var listabutton=$("#rna button[sel=\"s\"]");
	$("#rna button").attr("disabled",false);
	//$("#rna button[sel=\"s\"]").css("opacity","0.6");
	//$("#rna button[sel=\"s\"]").css("-moz-opacity","0.6");
	//$("#rna button[sel=\"s\"]").css("filter","alpha(opacity=60)");
	$("#rna button[sel=\"s\"],#rna button:contains(\"X\")").css("color","GrayText");
	//mi occupo del tooltip per il genid
	for(i=0;i<listabutton.length;i++){
		var gen=$(listabutton[i]).attr("gen");
		var fr="tooltip.show(\""+gen+"\")";
		$(listabutton[i]).parent().attr("onmouseover",fr);
		$(listabutton[i]).parent().attr("onmouseout","tooltip.hide()");
		//se il genid � nella lista delle aliq fatte in questa serie,
		//allora coloro il tasto e metto come numero quello della serie
		
		if(lista_aliq[gen]!=undefined){
			$(listabutton[i]).css("opacity","0.6");
			$(listabutton[i]).css("-moz-opacity","0.6");
			$(listabutton[i]).css("filter","alpha(opacity=60)");
			$(listabutton[i]).text(lista_aliq[gen].toString());
		}
	}
	barcode_piastra=codice;
	
	// reference to the REDIPS.drag library
    var rd = REDIPS.drag;
    // initialization
    rd.init();
    // set hover color
    rd.hover.color_td = '#826756';
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
	$("#rna td").removeAttr("onmouseover");
	$("#rna td").removeAttr("onmouseout");
	$("#" + nameP + " button").attr("disabled", true );
}

function carica_effettiva(codice){
	$("#piastra button").css("background-color","rgb(249,248,242)");
	$("#piastra button").attr("disabled", false );	
	var tipo=$("#proto").attr("value");
	var nameP="rna";
	var radio=$('input:radio[name="choose"]:checked').val();
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
				alert("Plate doesn't exist");
				errore_cont(nameP);
			}
			else if(d.data=="errore_piastra"){
				alert("Plate aim is not working");
				errore_cont(nameP);
			}
			else if(d.data=="errore_aliq"){
				var val=$("#"+nameP+" th").text().toLowerCase();
				alert("Plate selected is not for "+tipo);
				errore_cont(nameP);
			}
			else if(d.data=="errore_store"){
				alert("Error while connecting with storage");
				errore_cont(nameP);
			}
			else if(d.data=="err_tipo"){
				alert("Error. Block isn't for "+tipo);
				errore_cont(nameP);
			}
			else if(d.data=="err_esistente"){
				alert("Error. Barcode you entered already exists");
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
	tasti=$("#rna button");
	for(j=0;j<tasti.length;j++){
		$(tasti[j]).removeAttr("sel");
		$(tasti[j]).removeAttr("posiz");
	}
	if ($("#barcode_plate").val() == "")
		alert("Insert the plate barcode");

	else{//devo vedere se e' stato scelto di caricare la piastra o la provetta
		var radio=$('input:radio[name="choose"]:checked');
		if (radio.length==0){
			alert("Choose if you want to load a tube or a plate");
		}
		else{
			var codice=$("#barcode_plate").val();
			carica_effettiva(codice);
		}
	}
}

function invia_dati(){
	$("#pos,#vert_pos").attr("disabled",true);
	//impedisco all'utente di cambiare il numero di aliq create bloccando il
	//pulsante
	$("#cambia_aliquote").attr("disabled",true);
	//metto class=mark nella td di dest cos� non posso mettere altri tasti li'
	REDIPS.drag.target_cell.className="mark";
	
	//ho l'id della cella di partenza da dove sono partito per fare il drag and drop
	var partenza=REDIPS.drag.source_cell;
	//tolgo il class=mark nella td di partenza
	partenza.removeAttribute("class");
	var piastrapartenz=partenza.parentNode.parentNode.parentNode.id;
	//abilito il tasto per confermare
	$("#p_confirm").attr("disabled",false);
	//mi da' l'id della div mossa
	var idpartenza=REDIPS.drag.source_cell.id;
	var idarrivo=REDIPS.drag.target_cell.id;
	if ((piastrapartenz=="rna")&&(idpartenza!=idarrivo)){
		partenza.innerHTML="<button align='center' type='submit'>0</button>";
		
	}
	//se metto un'aliq nella tabella di partenza sulla sinistra non devo fare la 
	//post
	var piastraarrivo=REDIPS.drag.target_cell.parentNode.parentNode.parentNode.id;
	var num=REDIPS.drag.target_cell.childNodes[0].getAttribute("num");
	if(piastraarrivo!="aliq_posiz"){
		//$("#conf_all").attr("disabled",true);
		
		var posarrivo=idarrivo.split("-");
		
		var barcode_dest=barcode_piastra;
		vettore_posiz[num]=posarrivo[1]+"|"+barcode_dest;
		//riempio le variabili da trasmettere con la post		
		/*var data = {
	    		posizione:true,
	    		numero:num,
	    		posnuova:posarrivo[1],
	    		barcodedest:barcode_dest
	    };
		
		var url=base_url+"/split/execute/last/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	clearTimeout(timer);
	    	$("#conf_all").attr("disabled",false);
	    	$("body").removeClass("loading");
	    });	*/
	}
	else{
		//cancello la posizione nel vettore
		vettore_posiz[num]=undefined;
	}
}

function carica_piastra_scelta(){
	var val=$(this).text().trim();
	var cod=val.split(" ");
	var codice=cod[0];
	$("#barcode_plate").attr("value",codice);
	carica_effettiva(codice);
}

function posiziona_orizz(){
	posiz=true;
	//impedisco all'utente di cambiare il numero di aliq create bloccando il
	//pulsante
	$("#cambia_aliquote").attr("disabled",true);
	
	$("body").addClass("loading");
	//coloro i futuri posti in cui andranno le nuove aliquote
	//e' il numero di aliquote da posizionare nella piastra
	celle=$("#aliq_posiz div.drag");	
	var num=(celle.length)-1;
	//var num=$("#id_number_aliquots").attr("value");
	num=(parseInt(num))+1;
	
	//prendo il numero di colonne della piastra
	var colonne=$("#rna tr:nth-child(2) td");
	var col=parseInt(colonne.length)-1;
	//prendo il numero di righe della piastra
	var righe=$("#rna tr");
	var rig=parseInt(righe.length)-2;

	trovato=false;
	if (num<=col){
		//scandisco le righe analizzando la prima meta' della tabella
		for(indice=3;indice<(rig+3);indice++){
			pieno=false;
			for (j=2;j<(num+2);j++){
				id="#piastra tr:nth-child("+indice+") td:nth-child("+j+") :button";
				if($(id).attr("sel")||($(id).attr("disabled"))||($(id).text()=="X")){
					pieno=true;
				}
			}
			if (pieno==false){
				var k=2;
				for(i=0;i<num;i++){
					idcella="#piastra tr:nth-child("+indice+") td:nth-child("+k+")";
					//var tasto="div.drag[num="+(k-1)+"]";
					var tasto=celle[i];
					//tolgo il mark nelle celle di partenza
					$(tasto).parent().removeAttr("class");
					$(idcella).children().remove();
					$(idcella).append($(tasto));
					$(idcella).attr("class","mark");
					var posar=$(idcella).attr("id");
					var posarrivo=posar.split("-");
					var barcode_dest=barcode_piastra;
					var numero=parseInt($(tasto).attr("num"));
					vettore_posiz[numero]=posarrivo[1]+"|"+barcode_dest;
					/*$(idbutton).attr("posiz","s");
					$(idbutton).text(1);
					$(idbutton).css("background-color","red");*/
					trovato=true;
					k++;
				}
				break;
			}
		}
		//scandisco le righe guardando la seconda meta' della tabella
		//devo partire dalla colonna che si trova a meta' della tabella
		var inizio=Math.ceil(col/2);
		if((num<=inizio)&&(trovato==false)){
			for(indice=3;indice<(rig+3);indice++){
				pieno=false;
				//si parte da j=8 per le piastre classiche
				for (j=(inizio+2);j<(num+inizio+2);j++){
					id="#piastra tr:nth-child("+indice+") td:nth-child("+j+") :button";
					if($(id).attr("sel")||($(id).attr("disabled"))||($(id).text()=="X")){
						pieno=true;
					}
				}
				if (pieno==false){
					var k=(inizio+2);
					//for(k=8;k<8+num-1;k++){
					for(i=0;i<num;i++){
						idcella="#piastra tr:nth-child("+indice+") td:nth-child("+k+")";
						//var tasto="div.drag[num="+(k-7)+"]";
						var tasto=celle[i];
						//tolgo il mark nelle celle di partenza
						$(tasto).parent().removeAttr("class");
						$(idcella).children().remove();
						$(idcella).append($(tasto));
						$(idcella).attr("class","mark");
						var posar=$(idcella).attr("id");
						var posarrivo=posar.split("-");
						var barcode_dest=barcode_piastra;
						var numero=parseInt($(tasto).attr("num"));
						vettore_posiz[numero]=posarrivo[1]+"|"+barcode_dest;
						/*$(idbutton).attr("posiz","s");
						$(idbutton).text(1);
						$(idbutton).css("background-color","red");*/
						trovato=true;
						k++;
					}
					break;
				}
			}
		}
	}
	//non c'e' posto in quella piastra
	if(trovato==false){
		alert("Plate full. Please select another one.");
	}
	//faccio una post in cui comunico il posto di ogni aliquota
	else{
		$("#pos,#vert_pos").attr("disabled",true);
		//prendo l'id dei tasti in cui ho messo le aliquote
		var s="";
		var posti=$("#rna div.drag");
		for(i=0;i<posti.length;i++){
			id=$(posti[i]).parent().attr("id");
			p=id.split("-");
			var numer=$(posti[i]).attr("num")
			s=s+numer+":"+p[1]+"-";
		}
		//riempio le variabili da trasmettere con la post
		/*var data = {
	    		barcode: $("#barcode_plate").val(),
	    		posti: s,
	    		batch: true
	    };
		var url=base_url+"/split/execute/last/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	$("#conf_all").attr("disabled",false);
	    	$("body").removeClass("loading");
	    });*/
	}
	$("body").removeClass("loading");
}

function posiziona_vert(){
	$("body").addClass("loading");
	
	posiz=true;
	//impedisco all'utente di cambiare il numero di aliq create bloccando il
	//pulsante
	$("#cambia_aliquote").attr("disabled",true);

	var celle=$("#aliq_posiz div.drag");	
	var num=(celle.length);
	
	//prendo il numero di colonne della piastra
	var colonne=$("#rna tr:nth-child(2) td");
	var col=parseInt(colonne.length)-1;
	//prendo il numero di righe della piastra
	var righe=$("#rna tr");
	var rig=parseInt(righe.length)-2;
	
	trovato=false;
	if (num<=rig){
		//scandisco le colonne analizzando la prima meta' della tabella
		for (j=2;j<(col+2);j++){
			pieno=false;			
			for(indice=3;indice<(num+3);indice++){
				id="#piastra tr:nth-child("+indice+") td:nth-child("+j+") :button";
				if($(id).attr("sel")||($(id).attr("disabled"))||($(id).text()=="X")){
					pieno=true;
				}
			}	
			if (pieno==false){
				var k=3;
				for(i=0;i<num;i++){
					idcella="#piastra tr:nth-child("+k+") td:nth-child("+j+")";
					//var tasto="div.drag[num="+(k-1)+"]";
					var tasto=celle[i];
					//tolgo il mark nelle celle di partenza
					$(tasto).parent().removeAttr("class");
					$(idcella).children().remove();
					$(idcella).append($(tasto));
					$(idcella).attr("class","mark");
					var posar=$(idcella).attr("id");
					var posarrivo=posar.split("-");
					var barcode_dest=barcode_piastra;
					var numero=parseInt($(tasto).attr("num"));
					vettore_posiz[numero]=posarrivo[1]+"|"+barcode_dest;
					/*$(idbutton).attr("posiz","s");
					$(idbutton).text(1);
					$(idbutton).css("background-color","red");*/
					trovato=true;
					k++;
				}
				break;
			}
		}
		//scandisco le colonne guardando la seconda meta' della tabella
		//devo partire dalla riga che si trova a met� della tabella
		var inizio=Math.ceil(rig/2);
		if((num<=inizio)&&(trovato==false)){
			for (j=2;j<(col+2);j++){
				pieno=false;
				for(indice=(inizio+3);indice<(num+inizio+3);indice++){
					id="#piastra tr:nth-child("+indice+") td:nth-child("+j+") :button";
					if($(id).attr("sel")||($(id).attr("disabled"))||($(id).text()=="X")){
						pieno=true;
					}
				}
				if (pieno==false){
					var k=(inizio+3);
					//for(k=8;k<8+num-1;k++){
					for(i=0;i<num;i++){
						idcella="#piastra tr:nth-child("+k+") td:nth-child("+j+")";
						//var tasto="div.drag[num="+(k-7)+"]";
						var tasto=celle[i];
						//tolgo il mark nelle celle di partenza
						$(tasto).parent().removeAttr("class");
						$(idcella).children().remove();
						$(idcella).append($(tasto));
						$(idcella).attr("class","mark");
						var posar=$(idcella).attr("id");
						var posarrivo=posar.split("-");
						var barcode_dest=barcode_piastra;
						var numero=parseInt($(tasto).attr("num"));
						vettore_posiz[numero]=posarrivo[1]+"|"+barcode_dest;
						/*$(idbutton).attr("posiz","s");
						$(idbutton).text(1);
						$(idbutton).css("background-color","red");*/
						trovato=true;
						k++;
					}
					break;
				}
			}
		}
	}
	//non c'e' posto in quella piastra
	if(trovato==false){
		alert("Plate full. Please select another one.");
	}
	//faccio una post in cui comunico il posto di ogni aliquota
	else{
		$("#pos,#vert_pos").attr("disabled",true);
		//prendo l'id dei tasti in cui ho messo le aliquote
		var s="";
		var posti=$("#rna div.drag");
		for(i=0;i<posti.length;i++){
			id=$(posti[i]).parent().attr("id");
			p=id.split("-");
			var numer=$(posti[i]).attr("num")
			s=s+numer+":"+p[1]+"-";
		}
		//riempio le variabili da trasmettere con la post
		/*var data = {
	    		barcode: $("#barcode_plate").val(),
	    		posti: s,
	    		batch: true
	    };
		var url=base_url+"/split/execute/last/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	$("#conf_all").attr("disabled",false);
	    	$("body").removeClass("loading");
	    });*/
	}
	$("body").removeClass("loading");
}

/*function posiziona(){
	posiz=true;
	//impedisco all'utente di cambiare il numero di aliq create bloccando il
	//pulsante
	$("#cambia_aliquote").attr("disabled",true);
	//coloro i futuri posti in cui andranno le nuove aliquote
	//e' il numero di aliquote da posizionare nella piastra
	celle=$("#aliq tr>th");	
	var num=(celle.length)-2;
	//var num=$("#id_number_aliquots").attr("value");
	num=(parseInt(num))+1;
	trovato=false;
	//scandisco le righe analizzando la prima meta' della tabella
	for(indice=3;indice<=10;indice++){
		pieno=false;
		for (j=2;j<=num;j++){
			id="#piastra tr:nth-child("+indice+") td:nth-child("+j+") :button";
			if($(id).attr("sel")||($(id).attr("disabled"))){
				pieno=true;
			}
		}	
		if (pieno==false){
			for(k=2;k<=num;k++){
				idcella="#piastra tr:nth-child("+indice+") td:nth-child("+k+")";
				var tasto="div.drag[num="+(k-1)+"]";
				//tolgo il mark nelle celle di partenza
				$(tasto).parent().removeAttr("class");
				$(idcella).children().remove();
				$(idcella).append($(tasto));
				$(idcella).attr("class","mark");
				var posar=$(idcella).attr("id");
				var posarrivo=posar.split("-");
				var barcode_dest=$("#barcode_plate").val();
				vettore_posiz[k-1]=posarrivo[1]+"|"+barcode_dest;
				trovato=true;
			}
			break;
		}
	}
	//scandisco le righe guardando la seconda meta' della tabella
	if((num<=7)&&(trovato==false)){
		for(indice=3;indice<=10;indice++){
			pieno=false;
			for (j=8;j<=13;j++){
				id="#piastra tr:nth-child("+indice+") td:nth-child("+j+") :button";
				if($(id).attr("sel")||($(id).attr("disabled"))){
					pieno=true;
				}
			}
			if (pieno==false){
				for(k=8;k<8+num-1;k++){
					idcella="#piastra tr:nth-child("+indice+") td:nth-child("+k+")";
					var tasto="div.drag[num="+(k-7)+"]";
					//tolgo il mark nelle celle di partenza
					$(tasto).parent().removeAttr("class");
					$(idcella).children().remove();
					$(idcella).append($(tasto));
					$(idcella).attr("class","mark");
					var posar=$(idcella).attr("id");
					var posarrivo=posar.split("-");
					var barcode_dest=$("#barcode_plate").val();
					vettore_posiz[k-7]=posarrivo[1]+"|"+barcode_dest;
					trovato=true;
				}
				break;
			}
		}
	}
	//non c'e' posto in quella piastra
	if(trovato==false){
		alert("Plate full. Select another plate.");
	}
	//faccio una post in cui comunico il posto di ogni aliquota
	else{
		$("#pos,#vert_pos").attr("disabled",true);
		//prendo l'id dei tasti in cui ho messo le aliquote
		var s="";
		var posti=$("#rna div.drag");
		for(i=0;i<posti.length;i++){
			id=$(posti[i]).parent().attr("id");
			p=id.split("-");
			s=s+p[1]+"-";
		}
		//riempio le variabili da trasmettere con la post
		var data = {
	    		barcode: $("#barcode_plate").val(),
	    		posti: s,
	    		batch: true
	    };
		var url=base_url+"/split/execute/last/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    });
	}
}*/

//per calcolare i nuovi valori di volume e conc per l'aliq madre
function copia_valori_ricalcola(){
	var volume0=$("#vol_orig").attr("value");
	var conc0=$("#concentration_madre").attr("value");
	var moth=new Array();
	var acqua=new Array();
	var vol_tot=0.0;
	var h2o_tot=0.0;
	//controllo che siano stati inseriti solo numeri
	var num_ali=$("#aliq tr>th");
	var num_aliq=num_ali.length-2;
	var regex=/^[0-9.]+$/;
	for(i=0;i<num_aliq;i++){
		//costruisco l'identificativo per il volume
		idvol="#volume_"+i;
		if($(idvol).val()== ""){
			frase="Insert volume in aliquot "+(i+1);
			alert(frase);
			return;
		}
		else{
			numero=$(idvol).attr("value");
			if(!regex.test(numero)){
			frase="You can only insert number. Correct volume in aliquot "+(i+1);
			alert(frase);
			return;
			}
		}
		idconc="#concentration_"+i;
		if($(idconc).val()==""){
			frase="Insert concentration in aliquot "+(i+1);
			alert(frase);
			return;
		}
		else{
			numero=$(idconc).attr("value");
			if(!regex.test(numero)){
			frase="You can only insert number. Correct concentration in aliquot "+(i+1);
			alert(frase);
			return;
			}
		}
	}

	var protocollo=$("#proto").attr("value");
	//ug della madre
	tot_madre=volume0*(conc0/1000);
	//ug di tutte le aliquote potenziali create
	var tot_presunto=0.0;
	
	var numero_ali=$("#numero_aliq_spip").attr("value");
	
    if((num_aliq+1)<=parseInt(numero_ali)){
    	var perc=$("#perc_spip_inf").attr("value");
    }
    else{
    	var perc=$("#perc_spip_sup").attr("value");
    }

	for(i=0;i<num_aliq;i++){
		idvol="#volume_"+i;
		idconc="#concentration_"+i;
		var volu=$(idvol).attr("value");
		var concen=$(idconc).attr("value");
		var volr=parseFloat(volu);
        var volrimanente=volr.toFixed(2);
    	$(idvol).attr("value",volrimanente);
    	var concr=parseFloat(concen);
        var concrimanente=concr.toFixed(1);
    	$(idconc).attr("value",concrimanente);
		var ugrprovetta=parseFloat(volu)*(parseFloat(concen)/1000);
		tot_presunto+=ugrprovetta;
		//aggiungo la perc per lo spipettamento
    	var ugreffettivi=ugrprovetta+(ugrprovetta*(perc/100.0));
    	//vol da prelevare dalla madre
    	moth[i]=ugreffettivi/(conc0/1000.0);
    	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
    	//della madre e quella della singola provetta
    	acqua[i]=(moth[i]*conc0/concen)-moth[i];
    	vol_tot+=moth[i];
    	h2o_tot+=acqua[i];
	}
			
    tot_presunto=tot_presunto+(tot_presunto*perc/100.0);
	
    if (tot_presunto>tot_madre){
    	alert("Unable to calculate values. You haven't enough material to create these aliquots.");
    	blocca=true;
    }
    else{
    	blocca=false;
    	var vv=parseFloat(volume0);
    	var volum0=vv.toFixed(2);
    	var cc=parseFloat(conc0);
    	var con0=cc.toFixed(1);
    	//ugr rimanenti nella madre
    	var rimanente=tot_madre-tot_presunto;
    	//vol rimanente nella madre
    	var volrimanente=rimanente/(con0/1000);
    	var volr=parseFloat(volrimanente);
        volrimanente=volr.toFixed(2);
    	$("#volume_madre,#vol_temp").attr("value",volrimanente);
    	
    	for (i=0;i<num_aliq;i++){
    	    var madre="#moth_"+i;
    		var acq="#h2o_"+i;
    		moth[i]=parseFloat(moth[i]).toFixed(2);
    		acqua[i]=parseFloat(acqua[i]).toFixed(2);
    		$(madre).attr("value",moth[i]);
    		$(acq).attr("value",acqua[i]);
        }
    	vol_tot=parseFloat(vol_tot).toFixed(2);
    	h2o_tot=parseFloat(h2o_tot).toFixed(2);
    	$("#id_work_al_sol").attr("value",vol_tot);
    	$("#id_work_al_h2o").attr("value",h2o_tot);
    }
}


//funzione per aggiungere alla tabella le aliq da posizionare
function crea_aliquote(num){
	var tabella = document.getElementById("aliq_posiz");
	//per eliminare tuti i figli della tabella
	while (tabella.firstChild) {
	    tabella.removeChild(tabella.firstChild);
	}
	//prendo il valore dell'indice della serie che sto derivando
	var indice=$("#indice").val();
	for (i=0;i<num;i++){
		//prendo il numero di righe della tabella
		var rowCount = tabella.rows.length;
		var row = tabella.insertRow(rowCount);
		//inserisco la cella con dentro il numero d'ordine
	    var cell1 = row.insertCell(0);
	    cell1.innerHTML ="<div class='drag' num='"+(i+1)+"' align='center'>"+indice+"</div>";
	    cell1.className="mark";
	}
	//assegno una larghezza fissa alle celle della tabella per fare in
	//modo che durante lo spostamento le colonne rimaste vuote
	//non si rimpiccioliscano
	$("#aliq_posiz td").attr("width","20em");
	$("#aliq_posiz td").attr("height","20em");
	
	// reference to the REDIPS.drag library
    var rd = REDIPS.drag;
    // initialization
    rd.init();
    // set hover color
    rd.hover.color_td = '#826756';
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
	            			jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br>"+indice+"° sample in this session"+"<br><br>Barcode DOES NOT match, please change tube");
	            			//alert("Barcode: "+barcreale+"\nGenID: "+val[3]+"\n"+indice+"° sample in this session"+"\n\nBarcode DOES NOT match, please change tube");
	            			
	            		}
	            		else{
	            			jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br><br>Barcode DOES NOT match, please change tube");
	            			//alert("Barcode: "+barcreale+"\nGenID: "+val[3]+"\n\nBarcode DOES NOT match, please change tube");
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
	            	//alert("Barcode: "+barcreale+"\nContainer is empty or does not exist");
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
	//riempio le variabili da trasmettere con la post
	var data = {
			posizione:true,
    		diz:JSON.stringify(vettore_posiz)
    };
	var url=base_url+"/split/execute/last/";
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
    	generate_result_table("Split","aliquote_fin");
    	$("td").css("border-width","1px");
	}
	
	//se nel campo della posizione c'e' "/", allora la pos non c'e', devo far scomparire il campo
	//e mettere il padding nel div dopo che riguarda l'aliquota esaurita
	var pos=$("#pos_campione").val();
	if (pos=="/"){
		$("#spanposiz").css("display","none");
		$("#aliq_esaur").css("padding-top","1em");
	}
	
	//devo assegnare ad ogni campo nascosto il suo valore per il calcolo effettivo delle
	//regole di derivazione
	var r_tot=$("#riga_tot").attr("value");
	var stringa=r_tot.split(";");

	$("#numero_aliq_spip").attr("value",stringa[0]);
	$("#perc_spip_sup").attr("value",stringa[1]);
	$("#perc_spip_inf").attr("value",stringa[2]);
	
	var tab=$("#lis_aliqder").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": false,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });
	
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
	
	var listapias=$("#listapias td");
	//faccio vedere la tabella con il riepilogo delle piastre, se c'e' qualcosa
	if(listapias.length!=0){
		$("#listapias").css("display","");
	}
	
	//abilito il pulsante per cambiare il numero di aliquote
	$("#cambia_aliquote").attr("disabled",false);
	
	$("#rna td,#rna th").attr("class","mark");
	
	$("#rna button").css("background-color","lightgrey");
	$("#rna br").remove();
	//disabilito il tasto per posizionare le aliquote sulla piastra
	$("#pos,#vert_pos").attr("disabled",true);
	//tolgo la vecchia intestazione alle tabelle
	$("#piastra table tr>th").text("");
	//disabilito i pulsanti della tabella
	$("#piastra button").attr("disabled",true);
	$("#load_plate").click(caricaPiastra);
	$("#pos").click(posiziona_orizz);
	$("#vert_pos").click(posiziona_vert);
	
	$("#listapias td").click(carica_piastra_scelta);
		
	//vedo il numero di aliq nel campo nascosto. Se � 0 vuol dire che sono al primo
	//passaggio nella schermata di split e quindi non devo copiare niente. Altrimenti
	//metto i valori di vol e conc della sessione passata
	var num_al=parseInt($("#tot_ali").val());
	if (num_al==0){
		$("#id_number_aliquots").attr("value","1");
		aggiungi_campi_tabella();
	}
	else{
		$("#id_number_aliquots").attr("value",num_al);
		aggiungi_campi_tabella();
		copia_vecchi_valori();
		calcola=true;
		copia_valori_ricalcola();
	}
	
	
	$("#cambia_aliquote").click(function(event){
		event.preventDefault();
		aggiungi_campi_tabella();
	});
	
	$("#id_number_aliquots").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_campi_tabella();
		}
	});
	
	$("#load_plate,#pos,#vert_pos").click(function(event){
		event.preventDefault();
	});
	
	$("#ricalcola").click(function(event){
		event.preventDefault();
		calcola=true;
		copia_valori_ricalcola();
	});

	$(".f label").after("<br>");
	$(".f label").css("font-size","1.4em");
	$(".f label").css("margin-left","20px");
	
	$("#barcode_plate").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			caricaPiastra();
		}
	});
	
	//chiamo la API per riempire il dizionario che ha come chiave i genid delle
	//aliq gi� create nella sessione e come valore il numero della
	//sessione
	var url = base_url + "/api/split/final/";
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
		
		if (blocca==true){
			alert("You haven't enough material to create these aliquots. Please correct value in aliquots.");			
			return;
		}
		
		//controllo che l'utente abbia premuto il tasto per ricalcolare 
		//i valori dell'aliq madre
		if (calcola==false){
			alert("You have to click 'Calculate values'");
			return;
		}
		//controllo che siano state create delle aliquote
		var celle=$("#aliq_posiz td");
		if(celle.length==0){
			alert("You have to insert number of aliquots you want to create");
			return;
		}
		
		//controllo che tutte le aliq siano state posizionate
		var aliq=$("#aliq_posiz div");
		if (aliq.length!=0){
			alert("You have to position all aliquots");
			return;
		}
		
		var num_ali=$("#aliq tr>th");
		num_aliq=num_ali.length-2;
		var regex=/^[0-9.]+$/;
		for(i=0;i<num_aliq;i++){
			//costruisco l'identificativo per il volume
			idvol="#volume_"+i;
			if($(idvol).val()== ""){
				frase="Insert volume in aliquot "+(i+1);
				alert(frase);
				return;
			}
			else{
				numero=$(idvol).attr("value");
				if(!regex.test(numero)){
				frase="You can only insert number. Correct volume in aliquot "+(i+1);
				alert(frase);
				return;
				}
			}
			idconc="#concentration_"+i;
			if($(idconc).val()==""){
				frase="Insert concentration in aliquot "+(i+1);
				alert(frase);
				return;
			}
			else{
				numero=$(idconc).attr("value");
				if(!regex.test(numero)){
				frase="You can only insert number. Correct concentration in aliquot "+(i+1);
				alert(frase);
				return;
				}
			}
		}
		//se il volume rimanente nell'aliq madre � zero, allora chiedo all'utente
		//se vuole inserire un nuovo volume per quel campione
		var vol_madre=$("#vol_temp").val();
		if(parseFloat(vol_madre)<=0.0){
			var idesausto="#exh";
			var esausto=$(idesausto).attr("checked");
			if (esausto!="checked"){
				event.preventDefault();
				val=prompt("Mother aliquot volume is 0 ul. Please insert new volume value (in ul) or check 'Aliquot Exhausted'");
				if ((val!=null)&&(val!="")){
					$("#vol_temp").attr("value",val);				
					//faccio la post e comunico alla vista il nuovo valore del volume per
					//l'aliq
					var genid=$("#gen").attr("value");
					var data = {
				    		gen:genid,
				    		valore:val,
				    };
					var url=base_url+"/derived/changevolume/";
					$.post(url, data, function (result) {
	
				    	if (result == "failure") {
				    		alert("Error");
				    	}
				    	else{
				    		setTimeout("post_server(this);",500);
				    		return;
				    	}
				    });
				}
				else{
					post_server(this);
				}
			}
			else{
				post_server(this);
			}
		}
		else{
			post_server(this);
		}
	});
});