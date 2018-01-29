posiz=false;
blocca=false;
vettore_posiz={};
lista_aliq=new Array();
lista_container_usati={};
var vol=new Array();
var conce=new Array();
var moth=new Array();
var acqua=new Array();
//vettore al cui interno vengono segnate le aliquote il cui valore di volume preso dalla 
//madre e di acqua di diluizione non devono essere modificate. Perche' quei valori sono 
//gia' stati calcolati prima singolarmente. Il tutto vale quando si clicca il tasto per
//il ricalcolo dei valori
var prov_bloccate=new Array();

//richiamata dalla funzione calcola_regole_n_aliq()
/*function calcola_valori(numero,volume,conc,tot,vol_aliq,percentuale,concentr,perc){
	var vol=new Array();
	var conce=new Array();*/

	/*if(numero>=4){
		var perc=10.0;
		var calc_w_h2o=11.0;
		var percentualeinpiu=percentuale+(percentuale*perc/100.0);
	}
	else{*/
	//serve per calcolare il volume da togliere dalla provetta madre per creare i 
	//derivati
	/*var calc_w_h2o=vol_aliq+(vol_aliq*perc/100.0);
	var percentualeinpiu=percentuale+(percentuale*perc/100.0);
	//}
	if (conc>=concentr){
			
		//se ho abbastanza materiale per seguire le regole di derivazione normali
		//o se devo dividere semplicemente il materiale tra le aliquote
		if (tot>=(percentualeinpiu*numero)){
    		for(i=0;i<numero-1;i++){
    			vol[i]=vol_aliq;
    			conce[i]=concentr;
    		}
    		if(numero>1){
    			vol[numero-1]=(tot-(percentualeinpiu*(numero-1)))/(conc/1000); //(ug tot - x ug presi)/conc originaria in ug/uL
    			w_sol=volume-vol[numero-1];
                w_h2o=(calc_w_h2o*(numero-1))-w_sol;
    		}
    		else{
    			vol[0]=volume-(volume*perc/100.0);
                w_h2o=0.0;
    		}
            conce[numero-1]=conc;
            
            b_h2o=0.0;
            b_sol=vol[numero-1];
        }
		else{
			//divido il volume nelle aliquote togliendo prima la percentuale per lo spipettamento
    		v=volume-(volume*perc/100.0);
			for(i=0;i<numero;i++){
    			vol[i]=v/numero;
    			conce[i]=conc;
			}
			b_sol=0.0;//vol[numero-1];
			w_sol=volume;//-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
            	
		}
	}
	else{
		//divido il volume nelle aliquote togliendo prima la percentuale per lo spipettamento
		v=volume-(volume*perc/100.0);
		for(i=0;i<numero;i++){
			vol[i]=v/numero;
			conce[i]=conc;
		}
		b_sol=0.0;//vol[numero-1];
		w_sol=volume;//-b_sol;
    	w_h2o=0.0;
    	b_h2o=0.0;
		
	}
	if(numero==1){
		w_sol=0.0;
	}
	for(i=0;i<numero;i++){
    	//creo il nome dell'input
    	volu="#volume_"+i;
    	concen="#concentration_"+i;
    	volum=parseFloat(vol[i]);
    	vol[i]=volum.toFixed(2);
    	$(volu).attr("value",vol[i]);
    	$(concen).attr("value",conce[i]);
    }
    ws=parseFloat(w_sol);
    w_sol=ws.toFixed(2);
    wh=parseFloat(w_h2o);
    w_h2o=wh.toFixed(2);
    bs=parseFloat(b_sol);
    b_sol=bs.toFixed(2);
    bh=parseFloat(b_h2o);
    b_h2o=bh.toFixed(2);
    if (w_sol==0.00)
    	w_sol="";
    if (w_h2o==0.00)
    	w_h2o="";
    if (b_h2o==0.00)
    	b_h2o="";
    if (b_sol==0.00)
    	b_sol="";
    $("#id_work_al_sol").attr("value",w_sol);
    $("#id_work_al_h2o").attr("value",w_h2o);
    $("#id_back_al_sol").attr("value",b_sol);
    $("#id_back_h2o").attr("value",b_h2o);
}*/

/*function calcola_regole_n_aliq(numero){
	
	var protocollo=$("#proto").attr("value");
	var volume=$("#id_vol_tot").attr("value");
	var conc=$("#id_conc_tot").attr("value");
	//conc e' in ng/L vol e' in uL
    tot=volume*(conc/1000);
    var vol_aliq=$("#volume_aliq").attr("value");
    var conc_aliq=$("#conc_aliq").attr("value");
    var numero_aliq=$("#numero_aliq_spip").attr("value");

    if(numero<=parseInt(numero_aliq)){
    	var perc_spip=$("#perc_spip_inf").attr("value");
    }
    else{
    	var perc_spip=$("#perc_spip_sup").attr("value");
    }*/
    //if (protocollo=="DNA"){
    	//calcola_valori(numero,volume,conc,tot,10.0,1000.0);
    //calcola_valori(numero,volume,conc,tot,parseFloat(vol_aliq),(parseFloat(conc_aliq)/1000.0)*parseFloat(vol_aliq),parseFloat(conc_aliq),parseFloat(perc_spip));
    	/*if (conc>=1000.0){
    		//se ho abbastanza materiale per seguire le regole di derivazione normali
    		//o se devo dividere semplicemente il materiale tra le aliquote
    		if (tot>=(11.0*numero)){
        		for(i=0;i<numero-1;i++){
        			vol[i]=10.0;
        			conce[i]=1000.0;
        		}
                vol[numero-1]=(tot-(11.0*(numero-1)))/(conc/1000); //(ug tot - x ug presi)/conc originaria in ug/uL
                conce[numero-1]=conc;
                w_sol=volume-vol[numero-1];
                w_h2o=(11.0*(numero-1))-w_sol;
                b_h2o=0.0;
                b_sol=vol[numero-1];
            }
    		else{
    			//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
    			for(i=0;i<numero;i++){
        			vol[i]=v/numero;
        			conce[i]=conc;
        			w_sol=volume;
                	w_h2o=0.0;
                	b_h2o=0.0;
                	b_sol=0.0;
        		}
    		}
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
			for(i=0;i<numero;i++){
    			vol[i]=v/numero;
    			conce[i]=conc;
    			w_sol=volume;
            	w_h2o=0.0;
            	b_h2o=0.0;
            	b_sol=0.0;
    		}
    	}*/
    //}
    //if (protocollo=="RNA"){
    	//calcola_valori(numero,volume,conc,tot,5.0,500.0);
    	/*if (conc>=500.0){
    		if (tot>=(5.5*numero)){
        		for(i=0;i<numero-1;i++){
        			vol[i]=10.0;
        			conce[i]=500.0;
        		}
                vol[numero-1]=(tot-(5.5*(numero-1)))/(conc/1000); //(ug tot - x ug presi)/conc originaria in ug/uL
                conce[numero-1]=conc;
                w_sol=volume-vol[numero-1];
                w_h2o=(11.0*(numero-1))-w_sol;
                b_h2o=0.0;
                b_sol=vol[numero-1];
            }
    		else{
    			//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
    			for(i=0;i<numero;i++){
        			vol[i]=v/numero;
        			conce[i]=conc;
        			w_sol=volume;
                	w_h2o=0.0;
                	b_h2o=0.0;
                	b_sol=0.0;
        		}
    		}
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
			for(i=0;i<numero;i++){
    			vol[i]=v/numero;
    			conce[i]=conc;
    			w_sol=volume;
            	w_h2o=0.0;
            	b_h2o=0.0;
            	b_sol=0.0;
    		}
    	}   */	
    //}
    //if (protocollo=="cRNA"){
    	//calcola_valori(numero,volume,conc,tot,2.5,250.0);
    	/*if (conc>=250.0){
    		if (tot>=(2.75*numero)){
        		for(i=0;i<numero-1;i++){
        			vol[i]=10.0;
        			conce[i]=250.0;
        		}
                vol[numero-1]=(tot-(2.75*(numero-1)))/(conc/1000); //(ug tot - x ug presi)/conc originaria in ug/uL
                conce[numero-1]=conc;
                w_sol=volume-vol[numero-1];
                w_h2o=(11.0*(numero-1))-w_sol;
                b_h2o=0.0;
                b_sol=vol[numero-1];
            }
    		else{
    			//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
    			for(i=0;i<numero;i++){
        			vol[i]=v/numero;
        			conce[i]=conc;
        			w_sol=volume;
                	w_h2o=0.0;
                	b_h2o=0.0;
                	b_sol=0.0;
        		}
    		}
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
			for(i=0;i<numero;i++){
    			vol[i]=v/numero;
    			conce[i]=conc;
    			w_sol=volume;
            	w_h2o=0.0;
            	b_h2o=0.0;
            	b_sol=0.0;
    		}
    	}  */ 	
    //}
    //if (protocollo=="cDNA"){
    	//calcola_valori(numero,volume,conc,tot,3.0,300.0);
    	/*if (conc>=300.0){
    		if (tot>=(3.3*numero)){
        		for(i=0;i<numero-1;i++){
        			vol[i]=10.0;
        			conce[i]=300.0;
        		}
                vol[numero-1]=(tot-(3.3*(numero-1)))/(conc/1000); //(ug tot - x ug presi)/conc originaria in ug/uL
                conce[numero-1]=conc;
                w_sol=volume-vol[numero-1];
                w_h2o=(11.0*(numero-1))-w_sol;
                b_h2o=0.0;
                b_sol=vol[numero-1];
            }
    		else{
    			//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
    			for(i=0;i<numero;i++){
        			vol[i]=v/numero;
        			conce[i]=conc;
        			w_sol=volume;
                	w_h2o=0.0;
                	b_h2o=0.0;
                	b_sol=0.0;
        		}
    		}
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
			for(i=0;i<numero;i++){
    			vol[i]=v/numero;
    			conce[i]=conc;
    			w_sol=volume;
            	w_h2o=0.0;
            	b_h2o=0.0;
            	b_sol=0.0;
    		}
    	}*/   	
    //}
    
//}


//serve per aggiungere caselle nella tabella che riepiloga le aliquote derivate
function aggiungi_campi_tabella(cancella){
	//cancella serve per sapere se cancellare o meno il diz che contiene i cambiamenti puntuali fatti	
	//a vol e conc delle aliquote figlie. E' da cancellare nel caso in cui clicco sul tasto che reimposta il 
	//numero di figlie. Invece se chiamo questa funzione all'inizio per popolare la schermata non devo cancellare
	//il diz perche' dovro' accedervi subito dopo per impostare i cambiamenti fatti per l'aliquota madre precedente
	if (cancella){
		for (var k in dizcambiati){
  			delete dizcambiati[k];
  		}
	}
	var numero=$("#id_number_aliquots").attr("value");
	if(isInt(numero)){
		celle=$("#aliq tr>th");
		//celle e' il numero attuale di celle della tabella
		numcelle=(celle.length);
		num=numero-numcelle+1;
		/*if(numero==1){
			$("#ricalcola").attr("disabled",true);
		}
		else{
			$("#ricalcola").attr("disabled",false);
		}*/
		var unitamis=$("#scelta_conc").children(":selected").attr("unit");
		if(unitamis==undefined){
			unitamis="";
		}
		var num_aliquote=$("#numero_aliq_tot").attr("value");
		if(num>=0){
			for(i=0;i<num;i++){
				$("#aliq tr>th:last").after("<th>Aliquot "+(i+numcelle)+"</th>");
				$("#aliq tr>td:last").after("<td align=\"center\" style=\" padding: 8px;border-width:1px;\">"+
				"<div><label for=\"volume_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;'>Volume(ul):</label>"+
				"<input id=\"volume_"+(i+numcelle-1)+"\" type=\"text\" size=\"4\" name=\"volume_"+(i+numcelle-1)+"\" maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'>"+
				"<label for=\"concentration_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;' class='label_conc' >Concentration<br>("+unitamis+"):</label>"+
				"<input id=\"concentration_"+(i+numcelle-1)+"\" type='text' size='4' name=\"conc_"+(i+numcelle-1)+"\" maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'>"+
				"<label for=\"moth_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;margin-top:5px;'>Mother(ul):</label>"+
				"<input id=\"moth_"+(i+numcelle-1)+"\" type=\"text\" size=\"4\" maxlength='7' readonly='readonly' style='margin-top: 5px; margin-bottom: 5px;'>"+
				"<label for=\"h2o_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;'>H2O(ul):</label>"+
				"<input id=\"h2o_"+(i+numcelle-1)+"\" type='text' size='4' maxlength='7' readonly='readonly' style='margin-top: 5px;'>"+
				"</div>"+
				"</td>");
			}
			//$("#aliq tr>th").css("background-color","#FFD199");
			$("#aliq tr>th").css("background-color","#EEDCD6");
			$("#aliq tr>th:first").css("background-color","#FF9A45");
			$("#aliq tr>th:last").css("background-color","silver");
	
			calcola_regole_iniziali(numero);	
			crea_aliquote(numero);
	
		}
		else{
			if(numero<1){
				alert("Value has to be at least 1");
			}
			else{
				val=numcelle-numero-1;
				for(i=0;i<val;i++){
					$("#aliq tr>th:last").remove();
					$("#aliq tr>td:last").remove();
				}
				
				$("#aliq tr>th").css("background-color","#EEDCD6");
				$("#aliq tr>th:first").css("background-color","#FF9A45");
				$("#aliq tr>th:last").css("background-color","silver");
				
				calcola_regole_iniziali(numero);	
				crea_aliquote(numero);
	
			}
		}
		//se il cambiamento del numero di aliquote avviene quando le ho gia' posizionate, devo cancellare
		//tutti i dati di prima
		if(Object.size(vettore_posiz)!=0){
			for (var k in vettore_posiz){
				delete vettore_posiz[k];
			}
			//ricarico le piastre visualizzate cosi' da cancellare i campioni posizionati 
			var barc1=$("#barcode_plate").val();
			if(barc1!=""){
				carica_effettiva(barc1,"",false,null);
			}
			var barc2=$("#barcode_plate2").val();
			if(barc2!=""){
				carica_effettiva(barc2,"2",false,null);
			}
		}
	}
	else{
		alert("Please insert an integer number");
	}
}

function piastra_definitiva(nameP,codice,tipo,radio,d,duefinale,ricaricata,pias2caricare){
	var codattuale=$("#barcode_plate").val();
	$("#barcode_plate"+duefinale).attr("value",codice);
	$("#" + nameP ).replaceWith(d);
	$("#rigaorizz"+duefinale).css("display","");
    $("#" + nameP + " button").css("background-color","rgb(249,248,242)");
    $("#" + nameP + " td br").remove();
    //ingrandisco la dimensione del titolo della tabella
    //$("#" + nameP + " th").css("font-size","1.5em");
    //metto il codice della piastra nel titolo della tabella, prima del tipo di aliquota
    var titolo=$("#" + nameP + " th").text();
    $("#" + nameP + " th").text(codice+" - "+titolo);
    
    if (posiz==false){
    	$("#pos"+duefinale+",#vert_pos"+duefinale).attr("disabled",false);
    }
    
    //blocco i tasti della tabella
    $("#" + nameP+" button").click(function(event){
		event.preventDefault();
	});
    
    var nompias=nameP.toString().split(" ");
    //metto l'id nei td della tabella
    var listastore=$("#"+nameP+" button");
	for(i=0;i<listastore.length;i++){
		var idoriginale=$(listastore[i]).attr("id");
		var ids=idoriginale.split("-");
		$(listastore[i]).removeAttr("id");
		var idfinale=nompias[0]+"-"+ids[1];
		$(listastore[i]).parent().attr("id",idfinale);
	}
    //metto classe=mark nelle celle in cui non voglio che venga
	//posizionato un tasto con il drag and drop
	$("#" + nameP+" th,.intest").attr("class","mark");
	$("#" + nameP+" button[sel=\"s\"]").parent().attr("class","mark");
	$("#" + nameP+" button:contains(X)").parent().attr("class","mark");
	
	$("#" + nameP+" button[sel=\"s\"]").text("#");
	$("#" + nameP+" button[sel=\"s\"], #" + nameP+" button:contains(X)").css("background-color","#E8E8E8");
	
	//per bloccare la cella in alto a sinistra solo se e' una piastra e non una provetta
	var colonne=$("#" + nameP+" tr:nth-child(2) td");
	var col=parseInt(colonne.length)-1;
	//prendo il numero di righe della piastra
	var righe=$("#" + nameP+" tr");
	var rig=parseInt(righe.length)-2;
	//se sto trattando una provetta singola che non ha la colonna di intestazione, col viene zero.
	if((col!=0)&&(rig!=0)){
		$("#" + nameP+" tr:nth-child(2)").children(":first-child").attr("class","mark");
	}
    
	var numero=$("#id_number_aliquots").attr("value");
	//vedo se in quella piastra avevo gia' caricato qualcosa prima e lo
	//faccio comparire nella piastra
	//prendo il valore dell'indice della serie che sto derivando
	var indice=$("#indice").val();
	
	for(i=1;i<(numero+1);i++){
		if(vettore_posiz[i]!=undefined){
			//$("#pos").attr("disabled",true);
			var valore=vettore_posiz[i];
			valore=valore.split("|");
			//solo se la piastra a cui si riferisce l'aliq e' questa
			if (valore[1]==codice){	
				if (i==numero){
					$("#"+nompias[0]+"-"+valore[0]).children().replaceWith("<div class='drag' num='"+i+"' align='center'>"+indice+"</div>");
				}
				else{
					var colore=$("#aliq tr>th:nth-child("+(i+1)+")").css("background-color");
					
					$("#"+nompias[0]+"-"+valore[0]).children().replaceWith("<div class='drag' style='background-color:"+colore+";' num='"+i+"' align='center'>"+indice+"</div>");	
				}
				$("#"+nompias[0]+"-"+valore[0]).addClass("mark");
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
		//per visualizzare la tabella con le aliquote inserite
		$("#listapias").css("display","");
		var tabella = document.getElementById("listapias");
		//prendo il numero di righe della tabella
		var rowCount = tabella.rows.length;
		var row = tabella.insertRow(rowCount);
		//per centrare la td
		row.align="center";
		//vedo quanti td nuovi ho, cioe' quelli con l'input hidden
		var hidden=$("#listapias input:hidden");
		//inserisco la cella con dentro il numero d'ordine
	    var cell1 = row.insertCell(0);
	    var tipoest=$("#tipoesteso").attr("value");
	    cell1.innerHTML ="<input type='hidden' name='piastra_"+((hidden.length-1)/2)+"' value="+codice+" />"+
	    "<input type='hidden' name='tipopiastra_"+((hidden.length-1)/2)+"' value="+tipoest+" />"+codice+" "+tipo;   
	    $("#listapias td:last").click(carica_piastra_scelta);
	}
	
	var listabutton=$("#" + nameP+" button[sel=\"s\"]");
	$("#" + nameP+" button").attr("disabled",false);
	$("#" + nameP+" button[sel=\"s\"],#" + nameP+" button:contains(\"X\")").css("color","GrayText");
	//mi occupo del tooltip per il genid
	
	for(i=0;i<listabutton.length;i++){
		var gen=$(listabutton[i]).attr("gen");
		var fr="tooltip.show(\""+gen+"\")";
		$(listabutton[i]).parent().attr("onmouseover",fr);
		$(listabutton[i]).parent().attr("onmouseout","tooltip.hide()");
		//se il genid e' nella lista delle aliq fatte in questa serie,
		//allora coloro il tasto e metto come numero quello della serie
		if(lista_aliq[gen]!=undefined){
			$(listabutton[i]).css("opacity","0.6");
			$(listabutton[i]).css("-moz-opacity","0.6");
			$(listabutton[i]).css("filter","alpha(opacity=60)");
			$(listabutton[i]).text(lista_aliq[gen].toString());
		}
	}
	
	//se la piastra e' stata ricaricata devo caricare nella piastra destra quella che c'era nella sinistra
	if ((ricaricata)&&(codattuale!="")&&(codattuale!=codice)){
		carica_effettiva(codattuale,"2",false,null);
	}
	if($("#autpos"+duefinale).is(":checked")){
		var celle=$("#aliq_posiz div.drag");
		var numdaposiz=$("#id_pospezzi"+duefinale).val();
		if(numdaposiz==""){
			numdaposiz=celle.length;
		}		
		var numtot=(celle.length);
		if((isInt(numdaposiz))&&(parseInt(numdaposiz)<=parseInt(numtot))){
			var radio=$("input:radio[name='vertoriz"+duefinale+"']:checked").val();
			if (radio=="vert"){
				posiziona_vert("vert_pos"+duefinale,parseInt(numdaposiz));
			}
			else if(radio=="oriz"){
				posiziona_orizz("pos"+duefinale,parseInt(numdaposiz));
			}
		}
	}
	if(pias2caricare!=null){
		carica_effettiva(pias2caricare, "2", false, null);
	}
	
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

function isInt(n) {
	return n % 1 === 0;
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

function piastra_errata(nameP,duefinale){
	$("#"+nameP+" div").replaceWith("<button>0</button>");
	$("#"+nameP+" td").attr("class","mark");
	$("#"+nameP+" td").removeAttr("onmouseover");
	$("#"+nameP+" td").removeAttr("onmouseout");
	$("#"+nameP+" button").attr("disabled", true );
	$("#"+nameP+" button").css("background-color","rgb(249,248,242)");
	$("#"+nameP+" th").text("");
	$("#barcode_plate"+duefinale).val("");
}

function carica_effettiva(codice,duefinale,ricaricata,pias2caricare){
	$("#piastra"+duefinale+" button").css("background-color","rgb(249,248,242)");
	$("#piastra"+duefinale+" button").attr("disabled", false );	
	var tipo=$("#proto").attr("value");
	var tipoest=$("#tipoesteso").attr("value");
	var tipoesteso=tipoest.replace(/%20/g," ");
	var nameP="piastra"+duefinale+" table";
	var radio=$("input:radio[name='choose"+duefinale+"']:checked").val();
	if(ricaricata){
		radio="plate";
	}
	if (cerca_container_usati(codice)){		
		dati=lista_container_usati[codice];
		piastra_definitiva(nameP,codice,tipoesteso,radio,dati,duefinale,ricaricata,pias2caricare);
	}
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		var codiceurl=codice.replace(/#/g,"%23");
	    var url = base_url + "/api/generic/load/" + codiceurl + "/" + tipo+ "/" + radio;
	    $.getJSON(url,function(d){
	        if(d.data=="errore"){
				alert("Plate doesn't exist");
				piastra_errata(nameP,duefinale);
			}
			else if(d.data=="errore_piastra"){
				alert("Plate aim is not working");
				piastra_errata(nameP,duefinale);
			}
			else if(d.data=="errore_aliq"){
				var val=$("#"+nameP+" th").text().toLowerCase();
				alert("Plate selected is not for "+tipoesteso);
				piastra_errata(nameP,duefinale);
			}
			else if(d.data=="errore_store"){
				alert("Error while connecting with storage");
				piastra_errata(nameP,duefinale);
			}
			else if(d.data=="err_tipo"){
				alert("Error. Block isn't for "+tipoesteso);
				piastra_errata(nameP,duefinale);
			}
			else if(d.data=="err_esistente"){
				alert("Error. Barcode you entered already exists");
				piastra_errata(nameP,duefinale);
			}
			else{
				lista_container_usati[codice]=d.data;
				piastra_definitiva(nameP,codice,tipoesteso,radio,d.data,duefinale,ricaricata,pias2caricare);
			}
	        clearTimeout(timer);
	    	$("body").removeClass("loading");
	    });
	}
}

function caricaPiastra(){
	tasti=$("#piastra table button");
	for(var j=0;j<tasti.length;j++){
		$(tasti[j]).removeAttr("sel");
		$(tasti[j]).removeAttr("posiz");
	}
	if ($("#barc_plate").val() == "")
		alert("Insert barcode");

	else{
		//devo vedere se e' stato scelto di caricare la piastra o la provetta
		var radio=$('input:radio[name="choose"]:checked');
		if (radio.length==0){
			alert("Choose if you want to load a tube or a plate");
		}
		else{
			var codice=$("#barc_plate").val();
			$("#barcode_plate").val(codice);
			$("#barc_plate").val("");
			carica_effettiva(codice,"",false,null);
		}
	}
}

function caricaPiastra2(){
	tasti=$("#piastra2 table button");
	for(j=0;j<tasti.length;j++){
		$(tasti[j]).removeAttr("sel");
		$(tasti[j]).removeAttr("posiz");
	}
	if ($("#barc_plate2").val() == "")
		alert("Insert barcode");

	else{
		//devo vedere se e' stato scelto di caricare la piastra o la provetta
		var radio=$('input:radio[name="choose2"]:checked');
		if (radio.length==0){
			alert("Choose if you want to load a tube or a plate");
		}
		else{
			var codice=$("#barc_plate2").val();
			$("#barcode_plate2").val(codice);
			$("#barc_plate2").val("");
			carica_effettiva(codice,"2",false,null);
		}
	}
}

function invia_dati(){
	//$("#pos").attr("disabled",true);
	
	//metto class=mark nella td di dest cosi' non posso mettere altri tasti li'
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
		
		var posarrivo=idarrivo.split("-");
		if (posarrivo[0]=="piastra"){
			var barcode_dest=$("#barcode_plate").val();
		}
		else if (posarrivo[0]=="piastra2"){
			var barcode_dest=$("#barcode_plate2").val();
		}
		vettore_posiz[num]=posarrivo[1]+"|"+barcode_dest;
		//riempio le variabili da trasmettere con la post		
		/*var data = {
	    		posizione:true,
	    		numero:num,
	    		posnuova:posarrivo[1],
	    		barcodedest:barcode_dest
	    };
		
		var url=base_url+"/derived/execute/last/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	clearTimeout(timer);
	    	$("#conf_all,#finish").attr("disabled",false);
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
	//$("#barcode_plate").attr("value",codice);
	//devo vedere se e' stato scelto di caricare la piastra o la provetta
	carica_effettiva(codice,"",true,null);
	/*var radio=$('input:radio[name="choose"]:checked');
	
	if (radio.length==0){
		alert("Choose if you want to load a tube or a plate");
	}
	else{
		//passo anche true per capire che questa piastra la sto ricaricando
		
	}*/
}

function posiziona_orizz(tasto,num){
	if (tasto=="pos"){
		var piastra="#piastra table";
		var duefinale="";
	}
	else if (tasto=="pos2"){
		var piastra="#piastra2 table";
		var duefinale="2";
	}
	//posiz=true;
	
	$("body").addClass("loading");
	
	//impedisco all'utente di cambiare il numero di aliq create bloccando il
	//pulsante
	//$("#cambia_aliquote").attr("disabled",true);
	//coloro i futuri posti in cui andranno le nuove aliquote
	//e' il numero di aliquote da posizionare nella piastra
	var celle=$("#aliq_posiz div.drag");	
	//var num=(celle.length);
	
	//prendo il numero di colonne della piastra
	var colonne=$(piastra+" tr:nth-child(2) td");
	var col=parseInt(colonne.length)-1;
	var sottr=0;
	//se sto trattando una provetta singola che non ha la colonna di intestazione, col viene zero.
	//Allora lo metto a 1
	if(col==0){
		col=1;
		sottr=1;
	}
	//prendo il numero di righe della piastra
	var righe=$(piastra+" tr");
	var rig=parseInt(righe.length)-2;
	//se sto trattando una provetta singola che non ha la riga di intestazione, rig viene zero.
	//Allora lo metto a 1
	if(rig==0){
		rig=1;
	}
	
	var indiniz=3-sottr;	
	var delta=2-sottr;

	trovato=false;
	if (num<=col){
		for(var indice=indiniz;indice<(rig+indiniz);indice++){
			//devo prima capire da che posto cominciare nella riga, cioe' guardo qual
			//e' il primo posto libero
			var ferma=false;
			var kk=2-sottr;
			while((!ferma)&&((kk-delta)<col)){
				var id=piastra+" tr:nth-child("+indice+") td:nth-child("+String(kk)+") :button";
				//alert($(id).length)
				if(!($(id).attr("sel"))&&(!($(id).attr("disabled")))&&(!($(id).text()=="X"))&&(($(id).length)!=0)){
					ferma=true;
				}
				else{
					kk++;
				}
			}
			//kk mi dice l'indice della cella da cui devo cominciare a posizionare
			if((kk-delta)<col){
				pieno=false;
				for (var j=kk;j<(num+kk);j++){
					var id=piastra+" tr:nth-child("+indice+") td:nth-child("+j+") :button";
					//il .length per vedere se nel td c'e' ancora un button. Perche' se ho gia' posizionato a mano
					//un blocchetto non c'e' piu' un button ma un div e quindi il .length e' 0 e li' non devo
					//posizionare niente
					if($(id).attr("sel")||($(id).attr("disabled"))||($(id).text()=="X")||($(id).length)==0){
						pieno=true;
					}
				}
				if (pieno==false){
					var k=kk;
					for(var i=0;i<num;i++){
						var idcella=piastra+" tr:nth-child("+indice+") td:nth-child("+k+")";
						//var tasto="div.drag[num="+(k-1)+"]";
						var tasto=celle[i];
						//tolgo il mark nelle celle di partenza
						$(tasto).parent().removeAttr("class");
						$(idcella).children().remove();
						$(idcella).append($(tasto));
						$(idcella).attr("class","mark");
						var posar=$(idcella).attr("id");
						var posarrivo=posar.split("-");
						var barcode_dest=$("#barcode_plate"+duefinale).val();
						var numero=parseInt($(tasto).attr("num"));
						vettore_posiz[numero]=posarrivo[1]+"|"+barcode_dest;
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
		alert("Container full. Please select another one.");
		$("#conf_all,#finish").attr("disabled",false);
	}
	else{
		//$("#pos"+duefinale+",#vert_pos"+duefinale).attr("disabled",true);
		//prendo l'id dei tasti in cui ho messo le aliquote
		var s="";
		var posti=$(piastra+" div.drag");
		for(i=0;i<posti.length;i++){
			id=$(posti[i]).parent().attr("id");
			p=id.split("-");
			var numer=$(posti[i]).attr("num")
			s=s+numer+":"+p[1]+"-";
		}
	}
	$("body").removeClass("loading");
}

function posiziona_vert(tasto,num){
	if (tasto=="vert_pos"){
		var piastra="#piastra table";
		var duefinale="";
	}
	else if (tasto=="vert_pos2"){
		var piastra="#piastra2 table";
		var duefinale="2";
	}
	
	$("body").addClass("loading");
	//posiz=true;
	//impedisco all'utente di cambiare il numero di aliq create bloccando il
	//pulsante
	//$("#cambia_aliquote").attr("disabled",true);
	
	//var timer = setTimeout(function(){$("body").addClass("loading");},500);
		
	var celle=$("#aliq_posiz div.drag");
	
	//prendo il numero di colonne della piastra
	var colonne=$(piastra+" tr:nth-child(2) td");
	var col=parseInt(colonne.length)-1;
	var sottr=0;
	//se sto trattando una provetta singola che non ha la colonna di intestazione, col viene zero.
	//Allora lo metto a 1
	if(col==0){
		col=1;
		sottr=1;
	}
	//prendo il numero di righe della piastra
	var righe=$(piastra+" tr");
	var rig=parseInt(righe.length)-2;
	//se sto trattando una provetta singola che non ha la riga di intestazione, rig viene zero.
	//Allora lo metto a 1
	if(rig==0){
		rig=1;
	}
	
	var indiniz=2-sottr;	
	var delta=3-sottr;
	
	trovato=false;
	if (num<=rig){
		//scandisco le colonne
		for(var kk=indiniz;kk<(col+indiniz);kk++){
		//for (j=2;j<(col+2);j++){
			//devo prima capire da che posto cominciare nella colonna, cioe' guardo qual
			//e' il primo posto libero
			var ferma=false;
			var indice=3-sottr;
			while((!ferma)&&((indice-delta)<rig)){
				var id=piastra+" tr:nth-child("+indice+") td:nth-child("+String(kk)+") :button";
				//alert($(id).length)
				if(!($(id).attr("sel"))&&(!($(id).attr("disabled")))&&(!($(id).text()=="X"))&&(($(id).length)!=0)){
					ferma=true;
				}
				else{
					indice++;
				}
			}
			//kk mi dice l'indice della cella da cui devo cominciare a posizionare
			if((indice-delta)<rig){
				pieno=false;
				for (var j=indice;j<(num+indice);j++){
					var id=piastra+" tr:nth-child("+j+") td:nth-child("+kk+") :button";
					//il .length per vedere se nel td c'e' ancora un button. Perche' se ho gia' posizionato a mano
					//un blocchetto non c'e' piu' un button ma un div e quindi il .length e' 0 e li' non devo
					//posizionare niente
					if($(id).attr("sel")||($(id).attr("disabled"))||($(id).text()=="X")||($(id).length)==0){
						pieno=true;
					}
				}
	
				if (pieno==false){
					var k=indice;
					for(var i=0;i<num;i++){
						var idcella=piastra+" tr:nth-child("+k+") td:nth-child("+kk+")";
						//var tasto="div.drag[num="+(k-1)+"]";
						var tasto=celle[i];
						//tolgo il mark nelle celle di partenza
						$(tasto).parent().removeAttr("class");
						$(idcella).children().remove();
						$(idcella).append($(tasto));
						$(idcella).attr("class","mark");
						var posar=$(idcella).attr("id");
						var posarrivo=posar.split("-");
						var barcode_dest=$("#barcode_plate"+duefinale).val();
						var numero=parseInt($(tasto).attr("num"));
						vettore_posiz[numero]=posarrivo[1]+"|"+barcode_dest;
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
		alert("Container full. Please select another one.");
		$("#conf_all,#finish").attr("disabled",false);
	}
	//faccio una post in cui comunico il posto di ogni aliquota
	else{
		//$("#pos"+duefinale+",#vert_pos"+duefinale).attr("disabled",true);
		//prendo l'id dei tasti in cui ho messo le aliquote
		var s="";
		var posti=$(piastra+" div.drag");
		for(i=0;i<posti.length;i++){
			id=$(posti[i]).parent().attr("id");
			p=id.split("-");
			var numer=$(posti[i]).attr("num")
			s=s+numer+":"+p[1]+"-";
		}
	}
	$("body").removeClass("loading");
}

function calcola_inizio(n_aliq,volume,conc,tot,vol_aliq,concentr,val1,val2,percent,concnuova,perc_spip){
	//i commenti riguardano il caso dell'RNA

	if ((conc>=concentr)&&(conc!=0)){
        //vol1=vol2=vol3=vol4=vol5=10.0; //uL
        //conc1=conc2=conc3=conc4=conc5=concentr; //ng/uL
		for(i=0;i<n_aliq-1;i++){
			vol[i]=vol_aliq;
			conce[i]=concentr;
		}
        if (tot>=val1){
        	$("th:contains(Working aliquots)").css("color","black");
        	$("th:contains(Aliquot preparation)").text("Back up aliquot preparation");
        	$("#aliq tr>th").css("background-color","#EEDCD6");
    		$("#aliq tr>th:first").css("background-color","#E8E8E8");
    		$("#aliq tr>th:last").css("background-color","silver");
    		//per colorare i quadratini da posizionare nella piastra
            $("#aliq_posiz div").css("background-color","#EEDCD6");
            $("#aliq_posiz div:last").css("background-color","silver");
            vol[n_aliq-1]=(tot-percent)/(conc/1000); //27.5 e' 25 maggiorato del 10% (ug tot - 27.5 ug presi)/conc originaria in ug/uL
            conce[n_aliq-1]=conc;
            w_sol=volume-vol[n_aliq-1];
            //calcolo il volume totale per creare i derivati a cui aggiungo la perc per
            //lo spipettamento
            var volparz=(vol_aliq*(n_aliq-1));
            var voltot=volparz+(volparz*(perc_spip/100.0));
            //w_h2o=44.0-w_sol;
            w_h2o=voltot-w_sol;
            b_h2o=0.0;
            b_sol=vol[n_aliq-1];
            //devo calcolare i valori da prelevare dalla madre e l'acqua con cui diluire
            //la singola provetta
            for(j=0;j<n_aliq-1;j++){
            	//ugr di una singola provetta
            	var ugrsingoli=vol[j]*(conce[j]/1000.0);
            	//aggiungo la perc per lo spipettamento
            	var ugreffettivi=ugrsingoli+(ugrsingoli*(perc_spip/100.0));
            	//vol da prelevare dalla madre
            	moth[j]=ugreffettivi/(conc/1000.0);
            	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
            	//della madre e quella della singola provetta
            	acqua[j]=(moth[j]*conc/conce[j])-moth[j];
            }
            moth[n_aliq-1]=vol[n_aliq-1];
            acqua[n_aliq-1]=0.0;
            if(n_aliq==1){
            	vol[0]=volume-(volume*perc_spip/100.0);
            	w_h2o=0.0;
            	b_sol=0.0;
            	moth[0]=volume;
            }
            
        }
        else if ((tot<=val1) && (tot>=val2)){
        	vol[n_aliq-1]=(tot-percent)/(concnuova); //(ug tot-27.5ug presi)/la concentrazione, che qui e' 0.5 ug/ul
        	conce[n_aliq-1]=concentr;
            co=conc/concentr;
            volu=volume*co;
            b_h2o=volu-volume//0.0;
            b_sol=volume//vol[n_aliq-1];
            w_sol=0.0//volume;
            w_h2o=0.0//volu-volume;
            
            for(j=0;j<n_aliq-1;j++){
            	moth[j]=vol[j]+(vol[j]*perc_spip/100.0);
            	acqua[j]=0.0;
            }
            moth[n_aliq-1]=vol[n_aliq-1];
            acqua[n_aliq-1]=0.0;
            
            //tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#EEDCD6");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            
            $("#aliq tr>th").css("background-color","silver");
            //per colorare i quadratini da posizionare nella piastra
            $("#aliq_posiz div").css("background-color","silver");
            if(n_aliq==1){
            	vol[0]=volume-(volume*perc_spip/100.0);
            	conce[0]=conc;
            	w_sol=0.0;
            	w_h2o=0.0;
            	b_sol=0.0;
            	moth[0]=volume;
            }
        }
        else{
        	//divido il volume nelle aliquote togliendo prima la percentuale per lo
        	//spipettamento
    		//v=volume-(volume*perc_spip/100.0);
        	v=volume
        	for(i=0;i<n_aliq;i++){
    			//vol[i]=v/n_aliq;
    			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
        		vol[i]=(v/n_aliq)-(v/n_aliq*perc_spip/100.0);
        		conce[i]=conc;
    			//moth[i]=vol[i];
        		moth[i]=v/n_aliq;
            	acqua[i]=0.0;
    		}
        	b_sol=volume//moth[n_aliq-1];
        	//calcolo la somma dei volumi delle aliq in verde
        	w=0.0;
        	for(i=0;i<(n_aliq-1);i++){
        		w=w+moth[i];
        	}
			w_sol=0.0//w;
        	w_h2o=0.0;
        	b_h2o=0.0;
        	if(n_aliq==1){
        		b_sol=0.0;
        	}
        	//tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#EEDCD6");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            
            $("#aliq tr>th").css("background-color","silver");
            //per colorare i quadratini da posizionare nella piastra
            $("#aliq_posiz div").css("background-color","silver");
        }
        
	}
	else{
		//divido il volume nelle aliquote togliendo prima la perc. per lo spipettamento
		//v=volume-(volume*perc_spip/100.0);
		v=volume;
    	for(i=0;i<n_aliq;i++){
    		//vol[i]=v/n_aliq;
			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
    		vol[i]=(v/n_aliq)-(v/n_aliq*perc_spip/100.0);
    		conce[i]=conc;
			//moth[i]=vol[i];
    		moth[i]=v/n_aliq;
        	acqua[i]=0.0;
		}
    	b_sol=volume//moth[n_aliq-1];
    	//calcolo la somma dei volumi delle aliq in verde
    	w=0.0;
    	for(i=0;i<(n_aliq-1);i++){
    		w=w+moth[i];
    	}
		w_sol=0.0//w;
    	w_h2o=0.0;
    	b_h2o=0.0;
    	if(n_aliq==1){
    		b_sol=0.0;
    	}
    	//tolgo il titolo a working aliquots preparation
        $("th:contains(Working aliquots)").css("color","#EEDCD6");
        $("th:contains(Working aliquots)").css("border-color","black");
        $("th:contains(Back up aliquot)").text("Aliquot preparation");
        
        $("#aliq tr>th").css("background-color","silver");
        //per colorare i quadratini da posizionare nella piastra
        $("#aliq_posiz div").css("background-color","silver");
	}
	
	/*v1=parseFloat(vol1);
    vol1=v1.toFixed(2);
    v2=parseFloat(vol2);
    vol2=v2.toFixed(2);
    v3=parseFloat(vol3);
    vol3=v3.toFixed(2);
    v4=parseFloat(vol4);
    vol4=v4.toFixed(2);
    v5=parseFloat(vol5);
    vol5=v5.toFixed(2);
    v6=parseFloat(vol6);
    vol6=v6.toFixed(2);
    $("#volume_0").attr("value",vol1);
    $("#volume_1").attr("value",vol2);
    $("#volume_2").attr("value",vol3);
    $("#volume_3").attr("value",vol4);
    $("#volume_4").attr("value",vol5);
    $("#volume_5").attr("value",vol6);
    $("#concentration_0").attr("value",conc1);
    $("#concentration_1").attr("value",conc2);
    $("#concentration_2").attr("value",conc3);
    $("#concentration_3").attr("value",conc4);
    $("#concentration_4").attr("value",conc5);
    $("#concentration_5").attr("value",conc6);*/
	for(i=0;i<n_aliq;i++){
	    	//creo il nome dell'input
	    	volu="#volume_"+i;
	    	concen="#concentration_"+i;
	    	var madre="#moth_"+i;
	    	var acq="#h2o_"+i;
	    	vol[i]=parseFloat(vol[i]).toFixed(2);
	    	conce[i]=parseFloat(conce[i]).toFixed(2);
			moth[i]=parseFloat(moth[i]).toFixed(2);
			acqua[i]=parseFloat(acqua[i]).toFixed(2);
	    	$(volu).attr("value",vol[i]);
	    	$(concen).attr("value",conce[i]);
	    	$(madre).attr("value",moth[i]);
	    	$(acq).attr("value",acqua[i]);
    }
    ws=parseFloat(w_sol);
    w_sol=ws.toFixed(2);
    wh=parseFloat(w_h2o);
    w_h2o=wh.toFixed(2);
    bs=parseFloat(b_sol);
    b_sol=bs.toFixed(2);
    bh=parseFloat(b_h2o);
    b_h2o=bh.toFixed(2);
    if (w_sol==0.00)
    	w_sol="";
    if (w_h2o==0.00)
    	w_h2o="";
    if (b_h2o==0.00)
    	b_h2o="";
    if (b_sol==0.00)
    	b_sol="";
    $("#id_work_al_sol").attr("value",w_sol);
    $("#id_work_al_h2o").attr("value",w_h2o);
    $("#id_back_al_sol").attr("value",b_sol);
    $("#id_back_h2o").attr("value",b_h2o);
}

//per calcolare i valori iniziali delle aliq derivate con i tre tipi di regole in base alla 
//quantit� di materiale prodotto
function calcola_regole_iniziali(n_aliq){
	protocollo=$("#proto").attr("value");
	volume=$("#id_vol_tot").attr("value");
	conc=$("#id_conc_tot").attr("value");
	if(conc==""){
		conc=0.0;
	}
	//conc e' in ng/L, vol e' in uL
    tot=volume*(conc/1000)
    var vol_aliq=$("#volume_aliq").attr("value");
    var conc_aliq=$("#conc_aliq").attr("value");
    var num_aliquote=$("#id_number_aliquots").attr("value");
    var estremo_inf=parseInt(num_aliquote)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0)
    var estremo_sup=(parseInt(num_aliquote)+4)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0)

    //informazioni per lo spipettamento
    var numero_ali=$("#numero_aliq_spip").attr("value");

    if(n_aliq<=parseInt(numero_ali)){
    	var perc_spip=$("#perc_spip_inf").attr("value");
    }
    else{
    	var perc_spip=$("#perc_spip_sup").attr("value");
    }
    //calcolo i ugr che rappresentano quelli utilizzati per creare le aliq con in piu'
    //i ugr per lo spipettamento. Questi ugr vengono poi tolti dalla soluzione totale
    //contenuta nella provetta madre
    //calcolo i ugr per creare le n aliq
    var ugr_parz=(parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000))*(n_aliq-1);
    //aggiungo la percentuale per lo spipettamento
    var ugrtot=ugr_parz+(ugr_parz*perc_spip/100);

    //concentrazione della singola aliq derivata/1000
    var concnuova=conc_aliq/1000.0;
    
    //if (protocollo=="DNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,1000.0,100,60,55,1);
    	//calcola_inizio(n_aliq,volume,conc,tot,100.0,10,6,5.5,0.1);
    calcola_inizio(n_aliq,volume,conc,parseFloat(tot),parseFloat(vol_aliq),parseFloat(conc_aliq),parseFloat(estremo_sup),parseFloat(estremo_inf),ugrtot,concnuova,perc_spip);
    	/*if (conc>=1000.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=1000.0; //ng/uL
            if (tot>=100){
                vol6=(tot-55)/(conc/1000); //(ug tot - 55 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_sol=vol6;
                b_h2o=0.0;
            }
            else if ((tot<=100) && (tot>=60)){
                vol6=(tot-55); //(ug tot-55ug presi)/la concentrazione, che pero' qui e' 1 ug/ul
                conc6=1000.0;
                co=conc/1000.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
                //divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
            	v=volume-(volume/10.0);
            	vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    //if (protocollo=="RNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,500.0,50,30,27.5,0.5);
    	//calcola_inizio(n_aliq,volume,conc,tot,500.0,50,30,22.0,0.5);
    	/*if (conc>=500.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=500.0; //ng/uL
            if (tot>=50){
                vol6=(tot-27.5)/(conc/1000); //27.5 e' 25 maggiorato del 10% (ug tot - 27.5 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_h2o=0.0;
                b_sol=vol6;
            }
            else if ((tot<=50) && (tot>=30)){
                vol6=(tot-27.5)/(0.5); //(ug tot-27.5ug presi)/la concentrazione, che qui e' 0.5 ug/ul
                conc6=500.0;
                co=conc/500.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
            	//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
        		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    //if (protocollo=="cRNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,250.0,25,15,13.75,0.25);
    	//calcola_inizio(n_aliq,volume,conc,tot,250.0,25,15,11.0,0.25);
    	/*if (conc>=250.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=250.0; //ng/uL
            if (tot>=25){
                vol6=(tot-13.75)/(conc/1000); //(ug tot - 13.75 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_h2o=0.0;
                b_sol=vol6;
            }
            else if ((tot<=25) && (tot>=15)){
                vol6=(tot-13.75)/(0.25); //(ug tot-13.75ug presi)/la concentrazione, che qui e' 0.25 ug/ul
                conc6=250.0;
                co=conc/250.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
            	//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
        		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    //if (protocollo=="cDNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,300.0,30,18,16.5,0.3);
    	//calcola_inizio(n_aliq,volume,conc,tot,300.0,30,18,13.2,0.3);
    	/*if (conc>=300.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=300.0; //ng/uL
            if (tot>=30){
                vol6=(tot-16.5)/(conc/1000); //(ug tot - 16.5 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_h2o=0.0;
                b_sol=vol6;
            }
            else if ((tot<=30) && (tot>=18)){
                vol6=(tot-16.5)/(0.3); //(ug tot-16.5ug presi)/la concentrazione, che qui e' 0.3 ug/ul
                conc6=300.0;
                co=conc/300.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
            	//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
        		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    
}

//richiamata dalla funzione copia_valori_ricalcola()
function copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,conc_aliq,val1,val2,ugr,c_ultima,perc,volback,cback,vett_vol,vett_conc,n_aliq){
	var moth=new Array();
	var acqua=new Array();
	//var concc=new Array();
	//var voll=new Array();
	var celle=$("#aliq tr>th");
	//e' il numero delle aliquote totali
	var n_aliq_effettivo=(celle.length)-1;
	//invece n_aliq � il numero di aliq compreso quella di riserva che non sono state 
	//modificate manualmente
	w_sol=0.0;
	w_h2o=0.0;
	//totg=tot_generale-(tot_generale*perc/100.0);
	volume=tot_generale/(conc/1000);
	if (conc==0){
		var volume=tot_generale;
	}
	var vol_aliq=$("#volume_aliq").attr("value");
    //calcolo i ugr che rappresentano quelli utilizzati per creare le aliq con in piu'
    //i ugr per lo spipettamento. Questi ugr vengono poi tolti dalla soluzione totale
    //contenuta nella provetta madre
    //calcolo i ugr per creare le n aliq
    var ugr_parz=(parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000))*(n_aliq-1);
    //aggiungo la percentuale per lo spipettamento
    var ugrtot=ugr_parz+(ugr_parz*perc/100);
    //il primo elemento della lista non � fra i th voluti, quindi lo salto sempre
	var lista_th=$("#aliq tr:first th");
	
	var lista_div=$("#aliq_posiz div");

	if ((conc>=conc_aliq)&&(conc!=0)){
		for(i=0;i<n_aliq_effettivo-1;i++){
			vol[i]=vol_aliq;
			conce[i]=conc_aliq;
		}
		if (tot_generale>=val1){
			
			$("th:contains(Working aliquots)").css("color","black");
            
			vol[n_aliq_effettivo-1]=(tot_generale-ugrtot)/(conc/1000); //27.5 e' 25 maggiorato del 10% (ug tot - 27.5 ug presi)/conc originaria in ug/uL
            conce[n_aliq_effettivo-1]=conc;

            w_sol=volume-vol[n_aliq_effettivo-1];
            //calcolo il volume totale per creare i derivati a cui aggiungo la perc per
            //lo spipettamento
            //uso n_aliq che e' il numero di aliquote non modificate manualmente
            var volparz=(vol_aliq*(n_aliq-1));
            var voltot=volparz+(volparz*(perc/100.0));
            //w_h2o=44.0-w_sol;
            w_h2o=voltot-w_sol;
            b_h2o=0.0;
            b_sol=vol[n_aliq_effettivo-1];
            //devo calcolare i valori da prelevare dalla madre e l'acqua con cui diluire
            //la singola provetta
            for(j=0;j<n_aliq_effettivo-1;j++){
            	//ugr di una singola provetta
            	var ugrsingoli=vol[j]*(conce[j]/1000.0);
            	//aggiungo la perc per lo spipettamento
            	var ugreffettivi=ugrsingoli+(ugrsingoli*(perc/100.0));
            	//vol da prelevare dalla madre
            	moth[j]=ugreffettivi/(conc/1000.0);
            	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
            	//della madre e quella della singola provetta
            	acqua[j]=(moth[j]*conc/conce[j])-moth[j];
            }
            if(n_aliq_effettivo==1){
            	vol[0]=volume-(volume*perc/100.0);
            	w_h2o=0.0;
            	b_sol=0.0;
            }
            moth[n_aliq_effettivo-1]=vol[n_aliq_effettivo-1];
            acqua[n_aliq_effettivo-1]=0.0;
            /*b_h2o=0.0;
            //devo calcolare i valori da prelevare dalla madre e l'acqua con cui diluire
            //la singola provetta
            for(j=0;j<n_aliq-1;j++){
            	//ugr di una singola provetta
            	var ugrsingoli=vett_vol[j]*(vett_conc[j]/1000.0);
            	//aggiungo la perc per lo spipettamento
            	var ugreffettivi=ugrsingoli+(ugrsingoli*(perc/100.0));
            	//vol da prelevare dalla madre
            	moth[j]=ugreffettivi/(conc/1000.0);
            	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
            	//della madre e quella della singola provetta
            	acqua[j]=(moth[j]*conc/vett_conc[j])-moth[j];
            	w_sol+=parseFloat(moth[j]);
        		w_h2o+=parseFloat(acqua[j]);*/
        }
		else if ((tot_generale<=val1) && (tot_generale>=val2)){
			//concentrazione della singola aliq derivata/1000
		    var concnuova=conc_aliq/1000.0;
			vol[n_aliq_effettivo-1]=(tot_generale-ugrtot)/(concnuova); //(ug tot-27.5ug presi)/la concentrazione, che qui e' 0.5 ug/ul
        	conce[n_aliq_effettivo-1]=conc_aliq;
            co=conc/conc_aliq;
            volu=volume*co;
            b_h2o=volu-volume//0.0;
            b_sol=volume//vol[n_aliq-1];
            w_sol=0.0//volume;
            w_h2o=0.0//volu-volume;
            if(n_aliq==1){
            	vol[0]=volume-(volume*perc/100.0);
            	conce[0]=conc;
            	w_sol=0.0;
            	w_h2o=0.0;
            }

            for(j=0;j<n_aliq_effettivo-1;j++){
            	moth[j]=parseFloat(vol[j])+(vol[j]*perc/100.0);
            	acqua[j]=0.0;
            }
            moth[n_aliq_effettivo-1]=vol[n_aliq_effettivo-1];
            acqua[n_aliq_effettivo-1]=0.0;
            //tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#EEDCD6");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");

            for (kk=1;kk<lista_th.length;kk++){
            	if (prov_bloccate[kk-1]!=1){
            		$(lista_th[kk]).css("background-color","silver");
            		$(lista_div[kk-1]).css("background-color","silver");           		
            	}
            }            
			/*c="#concentration_"+(num_aliq);
			var conc6=$(c).attr("value");
			//b_h2o=(b_sol*(conc/conc6))-b_sol;
			//volback=b_h2o+b_sol;
			b_sol=0.0;
			w_sol=$("#id_work_al_sol").attr("value");
			w_h2o=$("#id_work_al_h2o").attr("value");
			//e' la concentrazione nominale della singola aliquota (ad es 100 ng/ul)
			//per il DNA
			var conc_aliq=$("#conc_aliq").val();
			//ho gi� portato tutta la conc della madre al valore voluto (ad es 100 ng/ul
			//per il DNA). Devo solo vedere se bisogna diluire di pi� una provetta
			//perch� magari � stata diminuita manualmente la concentrazione
			for(j=0;j<n_aliq-1;j++){

				acqua[j]=(vett_vol[j]*conc_aliq/vett_conc[j])-vett_vol[j];
				moth[j]=vett_vol[j];
			}*/
			
        }
		else{
    		//v=volume-(volume*perc/100.0);
    		v=volume;
			//il ciclo � lungo come tutte le aliquote effettive (5 ad es) per salvare
    		//in ogni posto del vettore vol[i] il nuovo valore del volume per le aliq
    		//non modificate manualmente. Per� la divisione del v totale avviene in base
    		//alle aliq effettivamente non modificate.
        	for(i=0;i<n_aliq_effettivo;i++){
        		//vol[i]=v/n_aliq;
    			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
        		vol[i]=(v/n_aliq)-(v/n_aliq*perc/100.0);
        		conce[i]=conc;
    			//moth[i]=vol[i];
        		moth[i]=v/n_aliq;
            	acqua[i]=0.0;
    		}
        	b_sol=volume//moth[n_aliq-1];
        	//calcolo la somma dei volumi delle aliq in verde
        	w=0.0;
        	for(i=0;i<(n_aliq-1);i++){
        		w=w+moth[i];
        	}
			w_sol=0.0//w;
        	w_h2o=0.0;
        	b_h2o=0.0;
        	//tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#EEDCD6");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            for (kk=1;kk<lista_th.length;kk++){
            	if (prov_bloccate[kk-1]!=1){
            		$(lista_th[kk]).css("background-color","silver");
            		$(lista_div[kk-1]).css("background-color","silver");
            	}
            }
            
			/*b_h2o=0.0;
			b_sol=0.0;
			//tolgo la percentuale per lo spipettamento dal totale generale
			var tot=tot_generale-(tot_generale*perc/100.0) 
			//var ugrfinali=ugr+(ugr*perc/100.0);
			var volback=(tot-ugr)/(c_ultima/1000); //(ug tot - ug presi)/conc originaria in ug/uL
			
			for(j=0;j<n_aliq-1;j++){
				acqua[j]=(vett_vol[j]*conc/vett_conc[j])-vett_vol[j];
				moth[j]=vett_vol[j];
				w_sol+=parseFloat(moth[j]);
        		w_h2o+=parseFloat(acqua[j]);
			}
			
	        //w_sol=volume-volback;
	        //w_h2o=(w_sol*(conc/conc0))-w_sol;
	        b_sol=volback;
			//volback=volume0;
			//cback=conc0;*/
		}
	}
	else{
		//v=volume-(volume*perc/100.0);
		v=volume;
		//il ciclo � lungo come tutte le aliquote effettive (5 ad es) per salvare
		//in ogni posto del vettore vol[i] il nuovo valore del volume per le aliq
		//non modificate manualmente. Per� la divisione del v totale avviene in base
		//alle aliq effettivamente non modificate.
		for(i=0;i<n_aliq_effettivo;i++){
    		//vol[i]=v/n_aliq;
			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
    		vol[i]=(v/n_aliq)-(v/n_aliq*perc/100.0);
    		conce[i]=conc;
			//moth[i]=vol[i];
    		moth[i]=v/n_aliq;
        	acqua[i]=0.0;
		}
		
    	
    	b_sol=volume//moth[n_aliq-1];
    	//calcolo la somma dei volumi delle aliq in verde
    	w=0.0;
    	for(i=0;i<(n_aliq-1);i++){
    		w=w+moth[i];
    	}
		w_sol=0.0//w;
    	w_h2o=0.0;
    	b_h2o=0.0;
    	//tolgo il titolo a working aliquots preparation
        $("th:contains(Working aliquots)").css("color","#EEDCD6");
        $("th:contains(Working aliquots)").css("border-color","black");
        $("th:contains(Back up aliquot)").text("Aliquot preparation");

        for (kk=1;kk<lista_th.length;kk++){
        	if (prov_bloccate[kk-1]!=1){
        		$(lista_th[kk]).css("background-color","silver");
        		$(lista_div[kk-1]).css("background-color","silver");
        	}
        }           
        
		/*b_h2o=0.0;
		b_sol=0.0;
		//tolgo la percentuale per lo spipettamento dal totale generale
		var tot=tot_generale-(tot_generale*perc/100.0) 
		var volback=(tot-ugr)/(c_ultima/1000); //(ug tot - ug presi)/conc originaria in ug/uL

		for(j=0;j<n_aliq-1;j++){
			acqua[j]=(vett_vol[j]*conc/vett_conc[j])-vett_vol[j];
			
			moth[j]=vett_vol[j];
			w_sol+=parseFloat(moth[j]);
    		w_h2o+=parseFloat(acqua[j]);
		}
		
		//var ugrfinali=ugr+(ugr*perc/100.0);  
		
        //w_sol=volume-volback;
        //w_h2o=(w_sol*(conc/conc0))-w_sol;
        b_sol=volback;
		//volback=volume0;
		//cback=conc0;*/
	}
	
	if(n_aliq==1){
		moth[n_aliq-1]=parseFloat(vett_vol[0])+(vett_vol[0]*perc/100.0);
		acqua[0]=(vett_vol[0]*conc/vett_conc[0])-vett_vol[0];
	}
	/*else{
		moth[n_aliq-1]=volback;
		acqua[n_aliq-1]=0.0;
	}*/

	
	vsei=parseFloat(volback);
	volback=vsei.toFixed(2);
	csei=parseFloat(cback);
	cback=csei.toFixed(1);
	ws=parseFloat(w_sol);
    w_sol=ws.toFixed(2);
    wh=parseFloat(w_h2o);
    w_h2o=wh.toFixed(2);
    bs=parseFloat(b_sol);
    b_sol=bs.toFixed(2);
    bh=parseFloat(b_h2o);
    b_h2o=bh.toFixed(2);
    if (w_sol==0.00)
    	w_sol="";
    if (w_h2o==0.00)
    	w_h2o="";
    if (b_h2o==0.00)
    	b_h2o="";
    if (b_sol==0.00)
    	b_sol="";
    var numero=$("#id_number_aliquots").attr("value");
    
    //var j=0;

    for (i=0;i<numero;i++){
    	if (prov_bloccate[i]!=1){
    		var volu="#volume_"+i;
	    	var concen="#concentration_"+i;
		    var madre="#moth_"+i;
			var acq="#h2o_"+i;
			vol[i]=parseFloat(vol[i]).toFixed(2);
	    	conce[i]=parseFloat(conce[i]).toFixed(2);
			moth[i]=parseFloat(moth[i]).toFixed(2);
			acqua[i]=parseFloat(acqua[i]).toFixed(2);
			//if(n_aliq>1){
			$(volu).attr("value",vol[i]);
		    $(concen).attr("value",conce[i]);
			//}
	    	$(madre).attr("value",moth[i]);
			$(acq).attr("value",acqua[i]);
			//j=j+1;
    	}
    }
	
    
    if(numero==1){
    	$("#id_back_al_sol").attr("value","");
    }
    //solo se il numero di aliq prodotte e' diverso da 1
    if(numero!=1){
	    $("#id_work_al_sol").attr("value",w_sol);
	    $("#id_work_al_h2o").attr("value",w_h2o);
	    $("#id_back_h2o").attr("value",b_h2o);
	    $("#id_back_al_sol").attr("value",b_sol);
		volu="#volume_"+(num_aliq);
		//$(volu).attr("value",volback);  
		cc="#concentration_"+(num_aliq);
		//$(cc).attr("value",cback);
    }
}

//per ricalcolare l'acqua da diluire e la quantita' di soluzione da prendere nel caso l'utente
//cambi i valori di conc o volume nelle aliq
function copia_valori_ricalcola(){
	blocca=false;
	var volume0=$("#volume_0").attr("value");
	var conc0=$("#concentration_0").attr("value");
	var vett_vol=new Array();
	var vett_conc=new Array();
	var celle=$("#aliq tr>th");
	var vol_aliq=$("#volume_aliq").attr("value");
	var conc_aliq=$("#conc_aliq").attr("value");
	//e' il numero delle working aliquot
	num_aliq=(celle.length)-2;
	//controllo che siano stati inseriti solo numeri
	var regex=/^[0-9.]+$/;

	for(j=0;j<num_aliq;j++){
		//prendo i valori di vol e conc delle aliq
		var nome_vol="#volume_"+j;
		var nome_conc="#concentration_"+j;
		vett_vol[j]=$(nome_vol).val();
		vett_conc[j]=$(nome_conc).val();
		if((!regex.test(vett_vol[j]))||(!regex.test(vett_conc[j]))){
			alert("You can only insert number. Please correct.");
			return;
		}
	}
		
	var protocollo=$("#proto").attr("value");
	var volume=$("#id_vol_tot").attr("value");
	var conc=$("#id_conc_tot").attr("value");
	if(conc==""){
		conc=0.0;
	}
	//conc e' in ng/uL, vol e' in uL
	var tot_generale=volume*(conc/1000);
	//nel caso non abbia la concentrazione
	if(conc==0){
		tot_generale=parseFloat(volume);
	}
	var tot_presunto=0.0;
	for(j=0;j<num_aliq;j++){
		tot_aliq=vett_vol[j]*(vett_conc[j]/1000);
		//nel caso non abbia la concentrazione
		if(parseFloat(vett_conc[j])==0){
			tot_aliq=parseFloat(vett_vol[j]);
		}
		//calcolo i ugr totali
		tot_presunto=tot_presunto+tot_aliq;
	}

	//se creo solo un'aliquota
	if (num_aliq==0){
		tot_presunto=volume0*(conc0/1000);
		//nel caso non abbia la concentrazione
		if(parseFloat(conc0)==0){
			tot_presunto=parseFloat(volume0);
		}
		if (tot_presunto>tot_generale){
			blocca=true;
		}
		vett_vol[0]=volume0;
		vett_conc[0]=conc0;
	}
	//informazioni per lo spipettamento
    var numero_ali=$("#numero_aliq_spip").attr("value");

    if((num_aliq+1)<=parseInt(numero_ali)){
    	var perc=$("#perc_spip_inf").attr("value");
    }
    else{
    	var perc=$("#perc_spip_sup").attr("value");
    }

    var num_aliquote=$("#id_number_aliquots").attr("value");
  	//il primo elemento della lista non � fra i th voluti, quindi lo salto sempre
  	var lista_th=$("#aliq tr:first th");
  	//� la lista delle aliq da posizionare sulla piastra
  	var quadrati_da_posiz=$("#aliq_posiz div.drag");	

  	for(i=0;i<num_aliq;i++){
  		vol[i]=parseFloat(vol[i]).toFixed(2);
	    conce[i]=parseFloat(conce[i]).toFixed(2);

      	if ((parseFloat(vett_vol[i])!=parseFloat(vol[i]))||(parseFloat(vett_conc[i])!=parseFloat(conce[i]))){        		
      		//calcolo i ugr di quel campione
      		var ugr_singola_prov=vett_vol[i]*(vett_conc[i]/1000);
      		//nel caso non abbia la concentrazione
    		if(parseFloat(vett_conc[i])==0){
    			ugr_singola_prov=parseFloat(vett_vol[i]);
    		}
      		//aggiungo lo spipettamento
      		var ugr_effett=ugr_singola_prov+(ugr_singola_prov*perc/100.0);
      		
      		tot_generale=tot_generale-ugr_effett;
      		//sottraggo i ugr al totale da calcolare
      		tot_presunto=tot_presunto-ugr_effett;
      		//diminuisco il numero delle aliq da creare perch� una � gia'
      		//sistemata
      		num_aliquote=parseInt(num_aliquote)-1;      		
      	}
      	
  	}
  	var estremo_inf=parseInt(num_aliquote)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0);
    var estremo_sup=(parseInt(num_aliquote)+4)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0);
    var tot_presunto_finale=tot_presunto+(tot_presunto*perc/100.0);
  	if ((conc>=conc_aliq)&&(conc!=0)){
  		if (tot_generale>=estremo_inf){
		    if (tot_presunto_finale>tot_generale){
		    	blocca=true;
		    }
  		}
  		else{
			if (tot_generale<0){
				blocca=true;
			}
  		}
  	}
  	else{
  		if (tot_generale<0){
  			blocca=true;
		}
  	}
  	
  	if (blocca==true){
  		alert("Unable to recalculate values. You haven't enough material to create these aliquots.");
  	}
  	else{
  		for (var k in dizcambiati){
  			delete dizcambiati[k];
  		}
  		for(i=0;i<num_aliq;i++){
      		vol[i]=parseFloat(vol[i]).toFixed(2);
  	    	conce[i]=parseFloat(conce[i]).toFixed(2);
          	if ((parseFloat(vett_vol[i])!=parseFloat(vol[i]))||(parseFloat(vett_conc[i])!=parseFloat(conce[i]))){
          		//calcolo i ugr di quel campione
          		var ugr_singola_prov=vett_vol[i]*(vett_conc[i]/1000);
          		//nel caso non abbia la concentrazione
        		if(parseFloat(vett_conc[i])==0){
        			ugr_singola_prov=parseFloat(vett_vol[i]);
        		}
          		//aggiungo lo spipettamento
          		var ugr_effett=ugr_singola_prov+(ugr_singola_prov*perc/100.0);
          		//cambio il colore dell'aliquota perche' e' stata modificata a mano
          		//cambio il colore anche del quadratino da posizionare
          		if (i==0){
        			$(lista_th[i+1]).css("background-color","red");
        			$("div.drag[num="+String(i+1)+"]").css("background-color","red");
        			//$(quadrati_da_posiz[i]).css("background-color","red");
        		}
        		else if(i==1){
        			$(lista_th[i+1]).css("background-color","#00CCFF");
        			$("div.drag[num="+String(i+1)+"]").css("background-color","#00CCFF");
        			//$(quadrati_da_posiz[i]).css("background-color","#00CCFF");
        		}
        		else if(i==2){
        			$(lista_th[i+1]).css("background-color","#936EB8");
        			$("div.drag[num="+String(i+1)+"]").css("background-color","#936EB8");
        			//$(quadrati_da_posiz[i]).css("background-color","#936EB8");
        		}
        		else if(i==3){
        			$(lista_th[i+1]).css("background-color","yellow");
        			$("div.drag[num="+String(i+1)+"]").css("background-color","yellow");
        			//$(quadrati_da_posiz[i]).css("background-color","yellow");
        		}
        		else{
        			$(lista_th[i+1]).css("background-color","#FF6666");
        			$("div.drag[num="+String(i+1)+"]").css("background-color","#FF6666");
        			//$(quadrati_da_posiz[i]).css("background-color","#FF6666");
        		}
          		dizcambiati[i]=String(vett_vol[i])+"|"+String(vett_conc[i]);

          		//devo vedere il volume che devo prendere dalla madre per avere
          		//questi ugr
          		var volu_m=ugr_effett/(conc/1000.0);
          		//calcolo la quantita' di acqua per la diluizione
          		var acqu=(conc/vett_conc[i]*volu_m)-volu_m;
          		//nel caso non abbia la concentrazione
        		if(parseFloat(conc)==0){
        			volu_m=parseFloat(ugr_effett);
        			acqu=0;
        		}
        		var madre="#moth_"+i;
        		var acq="#h2o_"+i;
        		volu_m=parseFloat(volu_m).toFixed(2);
    			acqu=parseFloat(acqu).toFixed(2);
        		$(madre).attr("value",volu_m);
        		$(acq).attr("value",acqu);
        		//azzero il valore dei vettori per fare in modo che nei calcoli 
        		//successivi questa aliquota non venga considerata
        		vett_vol[i]=0.0;
        		//vett_conc[i]=0.0;
        		prov_bloccate[i]=1;
          	}
          	else{
          		//rimetto il colore verde all'aliquota
          		var stringa_al="Aliquot "+String(i+1);
          		$(lista_th[i+1]).css("background-color","#EEDCD6");
          		$("div.drag[num="+String(i+1)+"]").css("background-color","#EEDCD6");
          		//$(quadrati_da_posiz[i]).css("background-color","#EEDCD6");
          		prov_bloccate[i]=0;
          	}
  		}
    	//prendo la concentrazione dell'ultima aliquota che fa da riserva
    	var conc_ultima="#concentration_"+(num_aliq);
        var c_ultima=$(conc_ultima).attr("value");
        //sono i ugrammi che ho nelle aliq create a cui devo sommare la percentuale
		var ugr=tot_presunto;
		var ugrfinali=ugr+(ugr*perc/100.0);  
		//tot sono i ugr totali della sol madre
		var volback=(tot-ugrfinali)/(c_ultima/1000); //(ug tot - ug presi)/conc originaria in ug/uL
		//w_sol=volume-volback;
        //w_h2o=(w_sol*(conc/conc0))-w_sol;
        b_sol=volback;
        b_h2o=0.0;
        var cback=c_ultima;

        //var estremo_sup=$("#interv_sup").attr("value");
        //var estremo_inf=$("#interv_inf").attr("value");
        //if (protocollo=="DNA"){
			
			//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,1000.0,100,60,ugr,c_ultima,perc,volback,cback);
        if (num_aliq!=0){
        	copia_e_ricalcola(conc,volume,volume0,conc0,parseFloat(tot_generale),parseFloat(conc_aliq),parseFloat(estremo_sup),parseFloat(estremo_inf),ugr,c_ultima,perc,volback,cback,vett_vol,vett_conc,num_aliquote);
        }
        else{
        	//calcolo i ugr di quel campione
    		var ugr_singola_prov=vett_vol[i]*(vett_conc[i]/1000);
    		//nel caso non abbia la concentrazione
    		if(parseFloat(vett_conc[i])==0){
    			ugr_singola_prov=parseFloat(vett_vol[i]);
    		}
    		//aggiungo lo spipettamento
    		var ugr_effett=ugr_singola_prov+(ugr_singola_prov*perc/100.0);
    		
    		//devo vedere il volume che devo prendere dalla madre per avere
    		//questi ugr
    		var volu_m=ugr_effett/(conc/1000.0);
    		//calcolo la quantita' di acqua per la diluizione
    		var acqu=(conc/vett_conc[i]*volu_m)-volu_m;
    		//nel caso non abbia la concentrazione
    		if(parseFloat(conc)==0){
    			volu_m=parseFloat(vett_vol[i]);
    			acqu=0;
    		}
    		var madre="#moth_"+i;
    		var acq="#h2o_"+i;
    		volu_m=parseFloat(volu_m).toFixed(2);
			acqu=parseFloat(acqu).toFixed(2);
    		$(madre).attr("value",volu_m);
    		$(acq).attr("value",acqu);	        		
        }
        //calcola_inizio(num_aliquote,volume,conc,parseFloat(tot_generale),parseFloat(vol_aliq),parseFloat(conc_aliq),parseFloat(estremo_sup),parseFloat(estremo_inf),ugrtot,concnuova,perc);
        	/*if (conc>=1000.0){
        		if (tot_generale>=100){
                    b_h2o=0.0;
                }
        		else if ((tot_generale<=100) && (tot_generale>=60)){
        			c="#concentration_"+(num_aliq);
        			var conc6=$(c).attr("value");
        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
        			//volback=b_h2o+b_sol;
        			b_sol=0.0;
        			w_sol=$("#id_work_al_sol").attr("value");
        			w_h2o=$("#id_work_al_h2o").attr("value");
                }
        		else{
        			b_h2o=0.0;
        			b_sol=0.0;
        			w_sol=volume;
        			w_h2o=0.0;
        			volback=volume0;
        			cback=conc0;
        		}
        	}
        	else{
        		b_h2o=0.0;
        		b_sol=0.0;
        		w_sol=volume;
        		w_h2o=0.0;
        		volback=volume0;
        		cback=conc0;
        	}*/
    	//}
		//if (protocollo=="RNA"){
			//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,500.0,50,30,ugr,c_ultima,perc,volback,cback);
			/*if (conc>=500.0){
        		if ((tot_generale<=50) && (tot_generale>=30)){
        			c="#concentration_"+(num_aliq);
        			var conc6=$(c).attr("value");
        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
        			//volback=b_h2o+b_sol;
        			b_sol=0.0;
        			w_sol=$("#id_work_al_sol").attr("value");
        			w_h2o=$("#id_work_al_h2o").attr("value");
                }
        		else if(tot_generale<30){
        			b_h2o=0.0;
        			b_sol=0.0;
        			w_sol=volume;
        			w_h2o=0.0;
        			volback=volume0;
        			cback=conc0;
        		}
        	}
        	else{
        		b_h2o=0.0;
        		b_sol=0.0;
        		w_sol=volume;
        		w_h2o=0.0;
        		volback=volume0;
        		cback=conc0;
        	}*/
    	//}
		//if (protocollo=="cRNA"){
			//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,250.0,25,15,ugr,c_ultima,perc,volback,cback);
			/*if (conc>=250.0){
        		if ((tot_generale<=25) && (tot_generale>=15)){
        			c="#concentration_"+(num_aliq);
        			var conc6=$(c).attr("value");
        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
        			//volback=b_h2o+b_sol;
        			b_sol=0.0;
        			w_sol=$("#id_work_al_sol").attr("value");
        			w_h2o=$("#id_work_al_h2o").attr("value");
                }	
        		else if(tot_generale<15){
        			b_h2o=0.0;
        			b_sol=0.0;
        			w_sol=volume;
        			w_h2o=0.0;
        			//volback=volume0;
        			//cback=conc0;
        		}
        	}
        	else{
        		b_h2o=0.0;
        		b_sol=0.0;
        		w_sol=volume;
        		w_h2o=0.0;
        		//volback=volume0;
        		//cback=conc0;
        	}*/
    	//}
		//if (protocollo=="cDNA"){
			//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,300.0,30,18,ugr,c_ultima,perc,volback,cback);
			/*if (conc>=300.0){
        		if ((tot_generale<=30) && (tot_generale>=18)){
        			c="#concentration_"+(num_aliq);
        			var conc6=$(c).attr("value");
        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
        			//volback=b_h2o+b_sol;
        			b_sol=0.0;
        			w_sol=$("#id_work_al_sol").attr("value");
        			w_h2o=$("#id_work_al_h2o").attr("value");
                }	
        		else if(tot_generale<18){
        			b_h2o=0.0;
        			b_sol=0.0;
        			w_sol=volume;
        			w_h2o=0.0;
        			volback=volume0;
        			cback=conc0;
        		}
        	}
        	else{
        		b_h2o=0.0;
        		b_sol=0.0;
        		w_sol=volume;
        		w_h2o=0.0;
        		volback=volume0;
        		cback=conc0;
        	}*/
    	//}
	    	
  	}
}

function cambia_conc(cancella){
	//cancella serve per sapere se cancellare o meno il diz che contiene i cambiamenti puntuali fatti	
	//a vol e conc delle aliquote figlie. E' da cancellare nel caso in cui cambio la conc selezionando dal menu' a tendina.
	//Invece se chiamo questa funzione all'inizio per popolare la schermata non devo cancellare
	//il diz perche' dovro' accedervi subito dopo per impostare i cambiamenti fatti per l'aliquota madre precedente
	if (cancella){
		for (var k in dizcambiati){
  			delete dizcambiati[k];
  		}
	}
	var nomeconc=$("#scelta_conc").children(":selected").text();
	nom=nomeconc.split(" ");
	$("#id_conc_tot").attr("value",nom[0]);
	var numero=$("#id_number_aliquots").attr("value");
	var num_aliquote=$("#numero_aliq_tot").attr("value");
	var unitamis=$("#scelta_conc").children(":selected").attr("unit");
	if(unitamis==undefined){
		unitamis="";
	}
	$("label[for=id_conc_tot]").text("Total concentration("+unitamis+")");
	$(".label_conc").html("Concentration<br>("+unitamis+")");
	if (numero==num_aliquote){
		calcola_regole_iniziali(numero);
	}
	else{
		//calcola_regole_n_aliq(numero);
		calcola_regole_iniziali(numero);
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
	for (var i=0;i<num;i++){
		//prendo il numero di righe della tabella
		var rowCount = tabella.rows.length;
		var row = tabella.insertRow(rowCount);
		//inserisco la cella con dentro il numero d'ordine
	    var cell1 = row.insertCell(0);
	    if(i==num-1){
	    	cell1.innerHTML ="<div class='drag' num='"+(i+1)+"' align='center'>"+indice+"</div>";
	    }
	    else{
	    	var colore=$("#aliq tr>th:nth-child("+(i+2)+")").css("background-color");
	    	cell1.innerHTML ="<div class='drag' style='background-color:"+colore+";' num='"+(i+1)+"' align='center'>"+indice+"</div>";
	    }
	    
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
	            		var tab=$("#lis_aliqder").dataTable();
	            		var lista_barc=tab.$(".lista_barc");
	            		var lis_indici=tab.$(".lista_indici");
	            		var lis_gen=$(".lis_gen");
	            		var trovato=false;
	            		var indice="";
	            		var gen="";
	            		for(var i=0;i<lista_barc.length;i++){
	            			var codice=$(lista_barc[i]).text();
	            			if(codice.toLowerCase()==barcreale.toLowerCase()){
	            				trovato=true;
	            				indice=$(lis_indici[i]).text();
	            				gen=$(lis_gen[i]).text();
	            				break;
	            			}
	            		}
	            		if(trovato){
	            			if (indice=="1"){
	            				jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br>GenID: "+gen+"<br><br>Aliquot and barcode match, you can execute the procedure");
	            			}
	            			else{
	            				jQuery("#dialogMess2").html("Barcode: "+barcreale+"<br>GenID: "+gen+"<br>"+indice+"° sample in this session"+"<br><br>Barcode DOES NOT match, please change tube");
	            			}
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

//per impostare nelle aliquote figlie di questa sessione i cambiamenti fatti a volume o concentrazione
//dei campioni della sessione precedente
function imposta_cambiamenti_prec(){
	for (var k in dizcambiati){
		//la chiave e' un numero che fa da indice per capire quale aliquota e' stata cambiata
		var valori=dizcambiati[k];
		var vv=valori.split("|");
		$("#volume_"+k).val(vv[0]);
		$("#concentration_"+k).val(vv[1]);
	}
	copia_valori_ricalcola();
}

//per impostare in questa sessione i parametri dell'auto posizionamento e del caricamento
//del container impostati nella sessione precedente
function parametriposautomatico(){
	if(Object.size(dizautopos)!=0){
		for(var jj=0;jj<2;jj++){
			diztemp=dizautopos[jj];
			duefinale="";
	        if (jj==1){
	        	duefinale="2";
	        }
			if (diztemp["automatic"]=="Yes"){
				$("#autpos"+duefinale).attr("checked","checked");
				$("#id_pospezzi"+duefinale).val(diztemp["pospezzi"]);
				var vertoriz=diztemp["vertoriz"];
				$("#"+vertoriz+duefinale).attr("checked","checked");
				blocca_campi("autpos"+duefinale);
			}
			//solo se avevo caricato prima una piastra la ricarico anche adesso
			if (diztemp["choose"]=="plate"){
				$("#plate"+duefinale).attr("checked","checked");
				$("#barc_plate"+duefinale+",#barcode_plate"+duefinale).val(diztemp["barcode"]);
				/*if(diztemp["barcode"]!=""){
					if(jj==0){
						caricaPiastra();
					}
					else{
						//devo ritardare questa funzione perche' altrimenti rischio che finendo prima questa
						//i campioni vengono posizionati in automatico prima sulla seconda piastra rispetto alla prima
						window.setTimeout(caricaPiastra2,7000);
					}
				}*/
			}
		}
		var diz1=dizautopos[0];
		var diz2=dizautopos[1];
		if((diz1["choose"]=="plate")&&(diz1["barcode"]!="")&&(diz2["choose"]=="plate")&&(diz2["barcode"]!="")){
			carica_effettiva(diz1["barcode"],"",false,diz2["barcode"]);
		}
		else if((diz1["choose"]=="plate")&&(diz1["barcode"]!="")&&(diz2["barcode"]=="")){
			carica_effettiva(diz1["barcode"],"",false,null);
		}
		else if((diz1["barcode"]=="")&&(diz2["choose"]=="plate")&&(diz2["barcode"]!="")){
			carica_effettiva(diz2["barcode"],"2",false,null);
		}
	}
}

function blocca_campi(id){
	var duefinale="";
	if(id=="autpos2"){
		duefinale="2";
	}
	if($("#"+id).is(":checked")){
		$("#id_pospezzi"+duefinale).attr("disabled",false);
		$('input:radio[name="vertoriz'+duefinale+'"]').attr("disabled",false);
	}
	else{
		$("#id_pospezzi"+duefinale).attr("disabled",true);
		$('input:radio[name="vertoriz'+duefinale+'"]').attr("disabled",true);
	}
}

function post_server(tasto){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	//riempio le variabili da trasmettere con la post
	var data = {
			posizione:true,
    		diz:JSON.stringify(vettore_posiz),
    		misconc:$("#scelta_conc").children(":selected").attr("unit"),
    		dizcambiati:JSON.stringify(dizcambiati)
    };
	var url=base_url+"/derived/execute/last/";
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
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Derivation","aliquote_fin");
	}
	$("#id_date_exec").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	$("#id_date_exec").datepicker('setDate', new Date());
	var tablista=$("#lis_aliqder");
	//vuol dire che sono nell'ultima pagina con il report della derivazione e non devo fare tutte le inizializzazioni successive
	if(tablista.length==0){
		return
	}
	var tab=$("#lis_aliqder").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": false,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });
	
	//faccio comparire i dati del prossimo campione da derivare
	//prendo i td da eseguire
	var listaeseguire=tab.$(".da_eseguire");
	if (listaeseguire.length>1){
		var gen=$(listaeseguire[1]).siblings(".lis_gen").text();
		var barc=$(listaeseguire[1]).siblings(".lista_barc").text();
		$("#prossima").append("<b>Genealogy</b>: "+gen+" <b>Barcode</b>: "+barc);
	}
	else{
		$("#prossima").css("border-style","none");
	}
	
	//devo assegnare ad ogni campo nascosto il suo valore per il calcolo effettivo delle
	//regole di derivazione
	var r_tot=$("#riga_tot").attr("value");
	if(r_tot!=undefined){
		var stringa=r_tot.split(";");
		$("#proto").attr("value",stringa[0]);
		$("#id_number_aliquots").attr("value",stringa[1]);
		$("#numero_aliq_tot").attr("value",stringa[1]);
		$("#volume_aliq").attr("value",stringa[2]);
		$("#conc_aliq").attr("value",stringa[3]);
		//$("#interv_sup").attr("value",stringa[4]);
		//$("#interv_inf").attr("value",stringa[5]);
		$("#numero_aliq_spip").attr("value",stringa[4]);
		$("#perc_spip_sup").attr("value",stringa[5]);
		$("#perc_spip_inf").attr("value",stringa[6]);
	}
	
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
	
	//se c'e' qualcosa nella tabella delle piastre, la visualizzo, altrimenti la 
	//lascio a display:none
	var listarighe=$("#listapias tr");
	if(listarighe.length>1){
		$("#listapias").css("display","inline");
	}
	
	var listapias=$("#listapias td");
	for(i=0;i<listapias.length;i++){
		var testo=$(listapias[i]).text().trim();
		$(listapias[i]).text(testo);
	}
	
	//per nascondere la colonna con le posizioni
	var righe=tab.$("tr");
	var nascondi=true;
	for(var i=0;i<righe.length;i++){
		var pos=$(righe[i]).children(".lista_pos").text();
		if(pos!=""){
			nascondi=false;
		}
	}
	if(nascondi){
		tab.fnSetColumnVis( 3, false );
	}
	
	//se nel campo della posizione c'e' "/", allora la pos non c'e', devo far scomparire il campo
	//e mettere il padding nel div dopo che riguarda l'aliquota esaurita
	var pos=$("#pos_campione").val();
	if (pos=="/"){
		$("#spanposiz").css("display","none");
	}
	
	//abilito il pulsante per cambiare il numero di aliquote
	$("#cambia_aliquote").attr("disabled",false);
	
	//stringa[1] contiene il numero di aliquote da creare all'inizio
	if (stringa!=undefined){
		crea_aliquote(stringa[1]);
	}
	$("#rna td,#rna th").attr("class","mark");
    
	//faccio comparire giusto il nome del prot di derivazione
	var tip=$("#id_der_prot_aliq").attr("value");
	if (tip!=undefined){
		tip=tip.replace(/%20/g," ");
		$("#id_der_prot_aliq").attr("value",tip);
	}
	
	$("#load_plate,#load_plate2,#pos,#vert_pos,#pos2,#vert_pos2").click(function(event){
		event.preventDefault();
	});
	
	$("#rna button").css("background-color","lightgrey");
	//disabilito il tasto per posizionare le aliquote sulla piastra
	$("#pos,#vert_pos,#pos2,#vert_pos2").attr("disabled",true);
	//tolgo la vecchia intestazione alle tabelle
	$("#piastra table tr>th,#piastra2 table tr>th").text("");
	//disabilito i pulsanti della tabella
	$("#piastra button,#piastra2 button").attr("disabled",true);
	
	$("#piastra table td br,#piastra2 table td br").remove();
	//per togliere i pulsanti iniziali
	$("#piastra table td button,#piastra2 table td button").remove();
	
	$("#load_plate").click(caricaPiastra);
	$("#load_plate2").click(caricaPiastra2);
	$("#pos,#pos2").click(function(event){
		var celle=$("#aliq_posiz div.drag");	
		var num=(celle.length);
		posiziona_orizz($(this).attr("id"),num);
	});
	$("#vert_pos,#vert_pos2").click(function(event){
		var celle=$("#aliq_posiz div.drag");	
		var num=(celle.length);
		posiziona_vert($(this).attr("id"),num);
	});
	
	$("#listapias td").click(carica_piastra_scelta);
		
	$("#cambia_aliquote").click(function(event){
		event.preventDefault();
		aggiungi_campi_tabella(true);
	});
	
	$("#ricalcola").click(function(event){
		event.preventDefault();
		copia_valori_ricalcola();
	});

	$(".f label").after("<br>");
	$(".f label").css("font-size","1.4em");
	$(".f label").css("margin-left","20px");
	
	$("#barc_plate").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			caricaPiastra();
		}
	});
	
	$("#barc_plate2").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			caricaPiastra2();
		}
	});
	
	$("#autpos,#autpos2").click(function(event){
		blocca_campi($(this).attr("id"));
	});
	
	aggiungi_campi_tabella(false);
	
	//solo se sono nella schermata dei dettagli mi calcola le regole
	if($("#proto").attr("value")){
		aggiungi_campi_tabella(false);
		//prendo la prima concentrazione della lista
		var testo=$("#scelta_conc option:first").text();
		//if(testo!=""){
			var concentr=testo.split(" ");
			$("#id_conc_tot").attr("value",concentr[0]);
			//stringa[1] contiene il numero di aliquote da creare all'inizio
			calcola_regole_iniziali(stringa[1]);
			$("#cambia_aliquote,#ricalcola").attr("disabled",false);
		/*}
		else{
			$("#id_number_aliquots").attr("value",1);
			aggiungi_campi_tabella(false);
			var vol_tot=$("#id_vol_tot").val();
			$("#volume_0").val(vol_tot);
			$("#cambia_aliquote,#ricalcola").attr("disabled",true);
		}*/
		//chiamo la API per riempire il dizionario che ha come chiave i genid delle
		//aliq derivate gia' create nella sessione e come valore il numero della
		//sessione
		var url = base_url + "/api/derived/finalsession/";
	    $.getJSON(url,function(d){
	    	var strin=d.data;
	    	var st=strin.split("|");
	    	for(i=0;i<st.length;i++){
	    		var val=st[i].split(":");
	    		//in val[0] ho il genid, in val[1] ho il numero della serie
	    		lista_aliq[val[0]]=val[1];
	    	}
	    });
	}
	
	$("#scelta_conc").change(function(event){
		cambia_conc(true);
	})
	cambia_conc(false);
	var num_create=parseInt($("#id_number_aliquots").val());
	if((Object.size(dizcambiati)!=0)&&(num_create>1)){
		imposta_cambiamenti_prec();
	}
	
	parametriposautomatico();
	
	$("#conf_all,#finish").click(function(event){
		event.preventDefault();
		//salvo il numero delle nuove piastre che ho inserito nella schermata
		var nasc=$("#listapias input:hidden");
		var inputeffettivi=(nasc.length-1)/2;
		$("#numnuovepi").attr("value",inputeffettivi);
		
		if ($("#barcode_plate").val() == ""){
			alert("Insert barcode");
			return;
		}
		
		if (blocca==true){
			alert("You haven't enough material to create these aliquots. Please correct value in aliquot.");
			return;
		}
		
		//controllo che tutte le aliq siano state posizionate
		var aliq=$("#aliq_posiz div");
		if (aliq.length!=0){
			alert("You have to position all aliquots");
			return;
		}
		
		//verifico la validita' della data
		var dd=$("#id_date_exec").attr("value");
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			alert("Correct \"Execution date\" format");
			return;
		}
		
		var num_aliq=$("#id_number_aliquots").attr("value");
		var regex=/^[0-9.]+$/;
		for(i=0;i<num_aliq;i++){
			//costruisco l'identificativo per il volume
			idvol="#volume_"+i;
			if($(idvol).val()== ""){
				alert("Insert volume in aliquot "+(i+1));
				return;
			}
			else{
				var numero=$(idvol).attr("value");
				if(!regex.test(numero)){
					alert("You can only insert number. Correct volume in aliquot "+(i+1));
					return;
				}
			}
			idconc="#concentration_"+i;
			if($(idconc).val()==""){
				alert("Insert concentration in aliquot "+(i+1));
				return;
			}
			else{
				var numero=$(idconc).attr("value");
				if(!regex.test(numero)){
					//la concentrazione della figlia e' NaN se non ho inserito la concentrazione della madre al passo prima
					if(numero!="NaN"){
						alert("You can only insert number. Correct concentration in aliquot "+(i+1));
						return;
					}
				}
			}
		}
		post_server(this);
		//per bloccare il doppio click
		//if(bloccato==false){
			//$("#conf_all").attr("disabled",true);
		//}
	});
});

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
