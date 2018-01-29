var conta=0;
var barc_dupl=false;
var tipoaliquota="";
var collez = {'VT':{}, 'RL':{}, 'SF':{}, 'FF':{}, 'CH':{}, 'OF':{}, 'PL':{}, 'PX':{}, 'FR':{}, 'DNA':{}, 'RNA':{}, 'cDNA':{}, 'cRNA':{}, 'FS':{}, 'OS':{}, 'PS':{}, 'P':{}, 'LS':{}};
var contaaliq=1;
var vett_used_barc=new Array();
//per salvare i tipi di aliquota (RL, SF...) con abbreviazione e nome esteso
var tipialiq;
//dizionario in cui per ogni tipologia di aliquota inserita (cioe' il gen id fino al contatore), salvo il numero di aliquote
//gia' presenti nel DB della biobanca. Lo leggo quando devo creare il contatore per una nuova aliq 
var diz_aliq_presenti={};
//dizionario con chiave l'id del progetto e valore la lista dei local id gia' presenti per lui
var dizlocalid={};

//per fare diventare num lungo tanto quanto specificato in places anteponendo degli
//zeri all'occorrenza
function zeroPad(num, places) {
	var zero = places - num.toString().length + 1;
	return Array(+(zero > 0 && zero)).join("0") + num;
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function aggiorna(){
	var tum=$("#id_Tumor_Type option:selected").text();
	url=base_url+"/api/extern/type/"+tum;
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			$("#id_case option").not(":first").remove();
			for(i=d.data.length;i>0;i--){
				k=i-1;
				var stringa="<option value="+i+">"+d.data[k].itemCode+"</option>"
				$("#id_case option[value=\"\"]").after(stringa);
			}
		}
		else{
			alert("Select tumor type");
		}
	});
}

function aggiornaVettore(){
	var vett=$("#id_vector option:selected").val();
	$("#id_vol_linea,#id_count").parent().remove();
	if(vett=="H"){
		$("#id_mouse,#id_tissueMouse,#id_lineage,#id_passage,#id_scongcell,#id_passagecell,#id_lincell").attr("disabled",true);
		$("#id_mouse,#id_tissueMouse,#id_lineage,#id_passage,#id_scongcell,#id_passagecell,#id_lincell").parent().css("display","none");
		$("#id_mouse,#id_lineage,#id_passage").val("");
	}
	else if(vett=="X"){
		$("#id_mouse,#id_tissueMouse,#id_lineage,#id_passage").attr("disabled",false);
		$("#id_mouse,#id_tissueMouse,#id_lineage,#id_passage").parent().css("display","");
		$("#id_scongcell,#id_passagecell,#id_lincell").attr("disabled",true);
		$("#id_scongcell,#id_passagecell,#id_lincell").parent().css("display","none");
	}
	else if((vett=="S")||(vett=="A")||(vett=="O")){
		$("#id_scongcell,#id_passagecell,#id_lincell").attr("disabled",false);
		$("#id_scongcell,#id_passagecell,#id_lincell").parent().css("display","");
		$("#id_mouse,#id_tissueMouse,#id_lineage,#id_passage").attr("disabled",true);
		$("#id_mouse,#id_tissueMouse,#id_lineage,#id_passage").parent().css("display","none");
		$("#id_mouse,#id_lineage,#id_passage").val("");
		//devo impostare il tipo di aliquota su vitale perche' le linee sono sempre cosi'
		//dalla lista, che ho caricato tramite API e che contiene tutti i tipi di aliquote, passo
		//l'abbreviazione (VT) e mi faccio ridare l'id con cui poi accedo al select giusto
		/*for (var i=0;i<tipialiq.length;i++){
			if (tipialiq[i].abbreviation=="VT"){
				var idal=tipialiq[i].id;
			}
		}
		$("#id_Aliquot_Type option[value="+idal+"]").attr("selected","selected");
		
		$("#id_Pieces").attr("disabled",true);
		$("#id_Pieces").parent().css("display","none");
		$(".f p:last").after("<br id='ultimo_br' style='clear:both'/><p class='derived'><label for='id_vol_linea'>Volume (ul):</label>"+
			"<input id='id_vol_linea' type='text' maxlength='8' size='5'></p>"+
			"<p class='derived'><label for='id_count'>Count (cell/ml):</label>"+
			"<input id='id_count' type='text' maxlength='15' size='8'></p>");*/		
	}
	aggiornaAliquota();
}

function aggiornaAliquota(){
	var vett=$("#id_vector option:selected").val();
	$("#id_vol_linea,#id_count").parent().remove();
	$("label[for=id_Barc]").text("Tube Barcode:");
	var aliq=$("#id_Aliquot_Type option:selected").attr("value");
	$("#barcode_rna,#id_Pieces,#load_rna_plate").attr("disabled",false);
	$("#id_Pieces").parent().css("display","");
	//prendo il tipo dell'aliquota (originale,blocco,derivata)
	for (var i=0;i<tipialiq.length;i++){
		if (tipialiq[i].id==aliq){
			tipoaliquota=tipialiq[i].type;
			var abbr_aliq=tipialiq[i].abbreviation;
			break;
		}
	}
	var tessuto_sel=$("#id_Tissue_Type option:selected").text();
	if(tipoaliquota=="Block"){
		$("#id_conc,#id_vol,#id_origin,#id_pur1,#id_pur2,#id_ge,#id_vol_linea,#id_count").parent().remove();
		$("#ultimo_br").remove();
		$("#tabpiastra table tr>th").text("");
		$("#tabpiastra table button,#barcode_rna,#id_Position,#id_Barcode,#load_rna_plate").attr("disabled",true);
		$("#tabpiastra table button").css("background-color","#F9F8F2");
		//imposto a 1 il numero di pezzi e disabilito l'input
		$("#id_Pieces").attr("value","1");
		$("#id_Pieces").attr("disabled",true);
		$("label[for=id_Barc]").text("Barcode:");
		conta++;
	}
	else if(tipoaliquota=="Derived"){
		$("#id_conc,#id_vol,#id_origin,#id_pur1,#id_pur2,#id_ge,#id_vol_linea,#id_count").parent().remove();
		$("#ultimo_br").remove();
		$("#id_Pieces").attr("disabled",true);
		$("#id_Pieces").parent().css("display","none");
		if(listaerr.length==0){
			$(".f p:last").after("<br id='ultimo_br' style='clear:both'/><p class='derived'><label for='id_vol'>Volume (ul):</label>"+
					"<input id='id_vol' type='text' maxlength='8' size='5'></p>"+
					"<p class='derived'><label for='id_conc'>Conc. (ng/ul):</label>"+
					"<input id='id_conc' type='text' maxlength='8' size='5'></p>"+
					"<p class='derived'><label for='id_pur1'>Purity (260/280):</label>"+
					"<input id='id_pur1' type='text' maxlength='8' size='5'></p>"+
					"<p class='derived'><label for='id_pur2'>Purity (260/230):</label>"+
					"<input id='id_pur2' type='text' maxlength='8' size='5'></p>"+
					"<p class='derived'><label for='id_ge'>GE/Vex (GE/ml):</label>"+
					"<input id='id_ge' type='text' maxlength='8' size='5'></p>");
		}
		else{
			$(".f p.derived").css("margin-top","3em");
		}
	}
	//metto l'SF perche' indica il sangue intero
	else if ((abbr_aliq=='PL')||(abbr_aliq=='PX')||(abbr_aliq=='FR')||(abbr_aliq=='FS')||((tessuto_sel.toLowerCase()=="blood")&&(abbr_aliq=="SF"))){
		$("#id_conc,#id_vol,#id_origin,#id_pur1,#id_pur2,#id_ge,#id_vol_linea,#id_count").parent().remove();
		$("#ultimo_br").remove();
		$("#id_Pieces").attr("disabled",true);
		$("#id_Pieces").parent().css("display","none");
		$(".f p:last").after("<br id='ultimo_br' style='clear:both'/><p class='derived'><label for='id_vol'>Volume (ul):</label>"+
				"<input id='id_vol' type='text' maxlength='8' size='5'></p>");
	}
	else{
		$("#id_conc,#id_vol,#id_origin,#id_pur1,#id_pur2,#id_ge,#id_vol_linea,#id_count").parent().remove();
		$("#ultimo_br").remove();
		//se e' una linea cellulare oppure se e' sangue con VT ha senso che inserisca vol e conta perche' si tratta di PBMC		
		if((((vett=="S")||(vett=="A")||(vett=="O"))&&(abbr_aliq=="VT"))||((tessuto_sel.toLowerCase()=="blood")&&(abbr_aliq=="VT"))){
			$("#id_Pieces").attr("disabled",true);
			$("#id_Pieces").parent().css("display","none");
			$(".f p:last").after("<br id='ultimo_br' style='clear:both'/><p class='derived'><label for='id_vol_linea'>Volume (ul):</label>"+
				"<input id='id_vol_linea' type='text' maxlength='8' size='5'></p>"+
				"<p class='derived'><label for='id_count'>Count (cell/ml):</label>"+
				"<input id='id_count' type='text' maxlength='15' size='8'></p>");
		}
	}
}

function campione_piastra(){
	var contatore=1;
	var barcode=$(this).attr("barcode");
	$("#id_Barc").val(barcode)
	if(controlla_campi()){		
		var tumore=$("#id_Tumor_Type option:selected").val();
		var caso=$("#caso_fin").val();
		if (caso==undefined){
			caso=$("#id_case option:selected").text();
		}
		var tess=$("#id_Tissue_Type option:selected").val();
		var nometess=$("#id_Tissue_Type option:selected").text();
		var vett=$("#id_vector option:selected").val();
		if((vett=="S")||(vett=="A")||(vett=="O")){
			var lineage=$("#id_lincell").val().trim().toUpperCase();
			var scong=$("#id_scongcell").val().trim();
			scong=zeroPad(scong,2);
			var pass=$("#id_passagecell").val().trim();
			pass=zeroPad(pass,3);
			var centro=vett+lineage+scong+pass;
			var salvacentro=centro+"000";
			var tesstopo="None";
		}
		else{
			var lineage=$("#id_lineage").val().trim().toUpperCase();
			if (lineage==""){
				lineage="00";
			}
			var pass=$("#id_passage").val().trim();
			if (pass==""){
				pass="00";
			}
			pass=zeroPad(pass,2);
			var topo=$("#id_mouse").val().trim();
			if (topo==""){
				topo="00";
			}
			topo=zeroPad(topo,3);
			var centro=vett+lineage+pass+topo;
			var tesstopo=$("#id_tissueMouse option:selected").val();
			var nometesstopo=$("#id_tissueMouse option:selected").text();
			if((tesstopo=="")||($("#id_tissueMouse").attr("disabled"))){
				tesstopo="None";
			}
			var salvacentro=centro+nometesstopo;
		}
		var aliqtip=$("#id_Aliquot_Type option:selected").val();
		//dato l'id del tipoaliq che ho preso prima ho bisogno dell'abbreviazione
		for(var i=0;i<tipialiq.length;i++){
			if(tipialiq[i].id==aliqtip){
				var tipo=tipialiq[i].abbreviation;
				break;
			}
		}
		var pos=$(this).attr("id").split("-")[1];
		var cod_piastra=$("#barcode_rna").val();
		var counter = contatore_genid(tipo, nometess, cod_piastra, pos,salvacentro);
		var timer = setTimeout(function(){$("body").addClass("loading");},50);
		//chiamo la API che mi crea il gen
		var url=base_url+"/api/ext/newgenid/"+tumore+"/"+caso+"/"+tess+"/"+centro+"/"+tesstopo+"/"+aliqtip+"/"+counter+"/";
		var tasto=this;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				$("#id_Barc").attr("disabled",true);
				$(tasto).css("background-color","red");
				//scrivo il nuovo numero nel pulsante
				$(tasto).text("1");
				$(tasto).attr("disabled",true);
				//disabilito la scelta del tumore e del caso, cosi' quando si fa un assign to existing
				//non si puo' piu' cambiare
				$("#id_Tumor_Type,#id_case,#id_workgr").attr("disabled",true);
				//mi da' il contatore dell'aliquota come stringa
				contatore=d.cont;
				var gen=d.gen;
				diz_aliq_presenti[nometess+salvacentro+tipo]=d.presenti;
				$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, cod_piastra, pos, gen,null] );
				var vol=$("#id_vol").val();
				if (vol==undefined){
					vol="";
				}
				var conc=$("#id_conc").val();
				if (conc==undefined){
					conc="";
				}
				var pur1=$("#id_pur1").val();
				if (pur1==undefined){
					pur1="";
				}
				var pur2=$("#id_pur2").val();
				if (pur2==undefined){
					pur2="";
				}
				var ge=$("#id_ge").val();
				if (ge==undefined){
					ge="";
				}
				var vollinea=$("#id_vol_linea").val();
				if (vollinea==undefined){
					vollinea="";
				}
				var conta=$("#id_count").val();
				if (conta==undefined){
					conta="";
				}
				//salvo la nuova aliquota nella variabile locale
		        saveInLocal(tipo, nometess, pos, cod_piastra, gen, contatore,salvacentro,vol,conc,pur1,pur2,ge,vollinea,conta);
		        
				contaaliq++;
				$("#id_Barc").attr("disabled",false);
				$("#id_Barc").val("");
			}
			else{
				alert("Error");
			}
			
			clearTimeout(timer);
			$("body").removeClass("loading");
		})
		.fail(function() {
			clearTimeout(timer);
			$("body").removeClass("loading");
			alert( "Error" );
		});
	}
}

function caricaPiastra(){
	if ($("#barcode_rna").val() == "")
		alert("Insert the plate barcode");
	else if(($("#id_Aliquot_Type option:selected").text()=="---------")){
		alert("Select aliquot type");
	}
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},2000);
		var nameP="tabpiastra";

	    var codice = $("#barcode_rna").val();
	    //$("#id_Barcode").attr("value",codice);
	    var aliqtip=$("#id_Aliquot_Type option:selected").val();
		//dato l'id del tipoaliq che ho preso prima ho bisogno dell'abbreviazione
		for(var i=0;i<tipialiq.length;i++){
			if(tipialiq[i].id==aliqtip){
				var tipo=tipialiq[i].abbreviation;
				break;
			}
		}
		var barr=codice.replace(/#/g,"%23");
	    var url = base_url + "/api/generic/load/" + barr + "/" + tipo + "/plate";
	    $.getJSON(url,function(d){
	        if(d.data=="errore"){
				alert("Plate doesn't exist");
				$("#" + nameP + " button,#confirm_all").attr("disabled", true );
				$("#" + nameP + " button").css("background-color","#F9F8F2");
			}
			else if(d.data=="errore_piastra"){
				alert("Plate aim is not working");
				$("#" + nameP + " button,#confirm_all").attr("disabled", true );
				$("#" + nameP + " button").css("background-color","#F9F8F2");
			}
			else if(d.data=="errore_aliq"){
				alert("Plate selected is not "+tipo);
				$("#" + nameP + " button,#confirm_all").attr("disabled", true );
				$("#" + nameP + " button").css("background-color","#F9F8F2");
			}
			else if(d.data=="errore_store"){
				alert("Error while connecting with storage");
				$("#" + nameP + " button,#confirm_all").attr("disabled", true );
				$("#" + nameP + " button").css("background-color","#F9F8F2");
			}
			else{
		        $("#" + nameP+" table" ).replaceWith(d.data);
		        $("#" + nameP + " button").css("background-color","rgb(249,248,242)");
		        //prendo i button che non hanno l'attributo sel e li abilito
				//$("#" + nameP + " button").not("[sel]").attr("disabled",false);
		        $("#" + nameP + " button").click(campione_piastra);
		        $("#id_Barc").attr("disabled",false);
				//$("#id_Barcode").attr("disabled",true);
		        piastra_ricaricata(tipo,codice);
			}
	        clearTimeout(timer);
	    	$("body").removeClass("loading");
	    });    
	}
	$("body").removeClass("loading");
}

//carica le eventuali modifiche fatte in questa sessione alla piastra che si sta caricando
function piastra_ricaricata(typeP, barcodeP){
	if (typeP=="VT"){
		nameP="v";
	}
	else if(typeP=="SF"){
		nameP="s";
	}
	else if(typeP=="PL"){
		nameP="l";
	}
	else if(typeP=="PX"){
		nameP="x";
	}
	else if(typeP=="FR"){
		nameP="f";
	}
	else{
		nameP="r";
	}
    for (barcode in collez[typeP]){
        if (barcode == barcodeP){
            for (var i = 0; i < collez[typeP][barcode].length; i++){
                var pos = collez[typeP][barcode][i]['pos'];
                var genID = collez[typeP][barcode][i]['genID'];

                var id_tube = "#" + nameP + "-" + pos;
                
                $(id_tube).text("1");

                $(id_tube).attr('sel', 's');
                
                $(id_tube).attr("onmouseover","tooltip.show('"+genID+"')");
        		$(id_tube).attr("onmouseout","tooltip.hide();");
                $(id_tube).css("background-color","red");	
            }
        }
    }
    $("#tabpiastra button[sel='s']").attr("disabled", true );
}

function controlla_campi(){
	var regex=/^[0-9.]*$/;
	var regex2=/^[0-9]+$/;
	
	if(($("#id_Tumor_Type option:selected").text()=="---------")){
		alert("Select tumor type");
		return false;
	}
	var caso=$("#caso_fin").val();
	//vuol dire che sto facendo un assign to existing quindi devo controllare se e' stato scelto il caso
	if (caso==undefined){
		if(($("#id_case option:selected").text()=="---------")){
			alert("Select case");
			return false;
		}
	}
	if(($("#id_Tissue_Type option:selected").text()=="---------")){
		alert("Select tissue type");
		return false;
	}
	if(($("#id_vector option:selected").text()=="---------")){
		alert("Select vector");
		return false;
	}
	if(($("#id_Aliquot_Type option:selected").text()=="---------")){
		alert("Select aliquot type");
		return false;
	}
	//e' il barcode della provetta
	if(!($("#id_Barc").attr("value"))){
		alert("Insert Tube Barcode");
		return false;
	}
	else{
		var barc=$("#id_Barc").attr("value");
		//se c'e' uno spazio nella stringa
		if(barc.indexOf(" ") !== -1){
			alert("There is a space in barcode. Please correct.");
			return false;
		}
	}
	
	//controllo il numero di pezzi
	if(!($("#id_Pieces").attr("disabled"))&&!($("#id_Pieces").attr("value"))){
		alert("Insert number of pieces");
		return false;
	}
	if(!($("#id_Pieces").attr("disabled"))){
		var numero=$("#id_Pieces").attr("value");
		if((!regex2.test(numero))){
			alert("You can only insert number. Correct number of pieces");
			return false;
		}
	}
	//controllo la concentrazione per i derivati
	var conc=$("#id_conc").attr("value");
	if (conc!=undefined){
		if((!regex.test(conc))){
			alert("You can only insert number. Correct value for concentration");
			return false;
		}
	}
	
	//controllo il volume per i derivati
	var vol=$("#id_vol").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for volume");
			return false;
		}
	}
	
	//controllo la purezza1 per i derivati
	var vol=$("#id_pur1").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for purity (260/280)");
			return false;
		}
	}
	
	//controllo la purezza2 per i derivati
	var vol=$("#id_pur2").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for purity (260/230)");
			return false;
		}
	}
	
	//controllo i GE per i derivati
	var vol=$("#id_ge").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for GE/Vex");
			return false;
		}
	}
	
	//controllo il volume per le linee
	var vol=$("#id_vol_linea").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for volume");
			return false;
		}
	}
	
	//controllo la conta per le linee
	var vol=$("#id_count").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for count");
			return false;
		}
	}
	
	//controllo il passaggio per il topo
	var pass=$("#id_passage").attr("value");
	if(!($("#id_passage").attr("disabled"))&&(pass=="")){
		alert("Insert passage");
		return false;
	}
	if((!regex.test(pass))){
		alert("You can only insert number. Correct value for passage");
		return false;
	}
	
	//controllo il topo
	var topo=$("#id_mouse").attr("value");
	if(!($("#id_mouse").attr("disabled"))&&(topo=="")){
		alert("Insert mouse");
		return false;
	}
	if((!regex.test(topo))){
		alert("You can only insert number. Correct value for mouse");
		return false;
	}
	
	//controllo il tessuto del topo
	if(($("#id_tissueMouse option:selected").text()=="---------")&&(!($("#id_tissueMouse").attr("disabled")))){
		alert("Select mouse tissue");
		return false;
	}
	
	//controllo che nel lineage ci siano lettere o numeri
	var lineage=$("#id_lineage").attr("value");
	var regex=/^[a-zA-Z0-9]{2}$/;
	if(!($("#id_lineage").attr("disabled"))&&(!regex.test(lineage))){
		alert("Lineage field only allows letters or numbers and has to have 2 characters");
		return false;
	}
	
	//controllo che nel lineage delle linee ci siano lettere o numeri
	var lineage=$("#id_lincell").attr("value");
	var regex=/^[a-zA-Z0-9]{2}$/;
	if(!($("#id_lincell").attr("disabled"))&&(!regex.test(lineage))){
		alert("Lineage field only allows letters or numbers and has to have 2 characters");
		return false;
	}
	
	var regex3=/^[0-9]*$/;
	//controllo gli scongelamenti per le linee
	var scong=$("#id_scongcell").attr("value");
	if(!($("#id_scongcell").attr("disabled"))&&(scong=="")){
		alert("Insert thawing cycles");
		return false;
	}
	if((!regex3.test(scong))){
		alert("You can only insert number. Correct value for thawing cycles");
		return false;
	}
	
	//controllo i passaggi per le linee
	var pass=$("#id_passagecell").attr("value");
	if(!($("#id_passagecell").attr("disabled"))&&(pass=="")){
		alert("Insert passage");
		return false;
	}
	if((!regex3.test(pass))){
		alert("You can only insert number. Correct value for passage");
		return false;
	}
	
	return true;
}


//quando si clicca sul tasto per salvare un campione
function salva_aliq(){
	var contatore=1;
		
	if(controlla_campi()){
		var tumore=$("#id_Tumor_Type option:selected").val();
		var caso=$("#caso_fin").val();
		if (caso==undefined){
			caso=$("#id_case option:selected").text();
		}
		var tess=$("#id_Tissue_Type option:selected").val();
		var nometess=$("#id_Tissue_Type option:selected").text();
		var vett=$("#id_vector option:selected").val();
		if((vett=="S")||(vett=="A")||(vett=="O")){
			var lineage=$("#id_lincell").val().trim().toUpperCase();
			var scong=$("#id_scongcell").val().trim();
			scong=zeroPad(scong,2);
			var pass=$("#id_passagecell").val().trim();
			pass=zeroPad(pass,3);
			var centro=vett+lineage+scong+pass;
			var salvacentro=centro+"001";
			var tesstopo="None";
		}
		else{
			var lineage=$("#id_lineage").val().trim().toUpperCase();
			if (lineage==""){
				lineage="00";
			}
			var pass=$("#id_passage").val().trim();
			if (pass==""){
				pass="00";
			}
			pass=zeroPad(pass,2);
			var topo=$("#id_mouse").val().trim();
			if (topo==""){
				topo="00";
			}
			topo=zeroPad(topo,3);
			var centro=vett+lineage+pass+topo;
			var tesstopo=$("#id_tissueMouse option:selected").val();
			var nometesstopo=$("#id_tissueMouse option:selected").text();
			if((tesstopo=="")||($("#id_tissueMouse").attr("disabled"))){
				tesstopo="None";
			}
			var salvacentro=centro+nometesstopo;
		}		
		var aliqtip=$("#id_Aliquot_Type option:selected").val();
		//dato l'id del tipoaliq che ho preso prima ho bisogno dell'abbreviazione
		for(var i=0;i<tipialiq.length;i++){
			if(tipialiq[i].id==aliqtip){
				var tipo=tipialiq[i].abbreviation;
				break;
			}
		}
		
		var barcode=$("#id_Barc").val();
		//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
		if (cerca_barc_duplicati(barcode)==false){
			var pos = '-';			
			var counter = contatore_genid(tipo, nometess, barcode, pos,salvacentro);
			var vett=$("#id_vector option:selected").val();
			var timer = setTimeout(function(){$("body").addClass("loading");},50);
			var url=base_url+"/api/ext/newgenid/"+tumore+"/"+caso+"/"+tess+"/"+centro+"/"+tesstopo+"/"+aliqtip+"/"+counter+"/";
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					//mi da' il contatore dell'aliquota come stringa
					contatore=d.cont;
					var gen=d.gen;
					diz_aliq_presenti[nometess+salvacentro+tipo]=d.presenti;
					var lbarc="";
					var codice=barcode.replace(/#/g,"%23");
					var url=base_url+"/api/collect/singletube/"+codice+"/"+tipo+"/";
					$.getJSON(url,function(d){
						if(d.data=="err_esistente"){
							alert("Error. Barcode you entered already exists");
						}
						else if(d.data=="err_tipo"){
							alert("Error. Block isn't for "+tipo);
						}
						else{						
							//disabilito la scelta del tumore e del caso, cosi' quando si fa un assign to existing
							//non si puo' piu' cambiare
							$("#id_Tumor_Type,#id_case,#id_workgr").attr("disabled",true);
							vett_used_barc.push(barcode);
						    //localStorage.setItem('vett_used_barc', vett_used_barc.toString());
							$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, barcode, pos, gen,null] );
							var vol=$("#id_vol").val();
							if (vol==undefined){
								vol="";
							}
							var conc=$("#id_conc").val();
							if (conc==undefined){
								conc="";
							}
							var pur1=$("#id_pur1").val();
							if (pur1==undefined){
								pur1="";
							}
							var pur2=$("#id_pur2").val();
							if (pur2==undefined){
								pur2="";
							}
							var ge=$("#id_ge").val();
							if (ge==undefined){
								ge="";
							}
							var vollinea=$("#id_vol_linea").val();
							if (vollinea==undefined){
								vollinea="";
							}
							var conta=$("#id_count").val();
							if (conta==undefined){
								conta="";
							}
							
							//salvo la nuova aliquota nella variabile locale e nel local storage
					        saveInLocal(tipo, nometess, pos, barcode, gen, contatore,salvacentro,vol,conc,pur1,pur2,ge,vollinea,conta);
					        
							contaaliq++;
							$("#id_Barc").val("");
						}
					});
				}
				else{
					alert("Error");
				}
				
				clearTimeout(timer);
				$("body").removeClass("loading");
			})
			.fail(function() {
				clearTimeout(timer);
				$("body").removeClass("loading");
				alert( "Error" );
			});
		}
		else{
			alert("Error. You have already used this barcode in this session.");
		}		
	}
}

function isInteger(x) {
    return x % 1 === 0;
}

function verifica_coll_event(){
	var coll=$("#id_barcode_Operation").val();
	if (coll==""){
		alert("Please insert informed consent");
	}
	else{
		
		var cc=coll.split("_");
        if (isInteger(cc[(cc.length)-1])){
            coll=cc[0]+'_';
            for (var jj=1;jj<(cc.length)-1;jj++){
            	coll+=cc[jj]+'_';
            }
            coll=coll.substring(0,coll.length-1);
        }
        //dopo averlo eventualmente manipolato riassegno il cons all'input box
        $("#id_barcode_Operation").val(coll);
		
		var ospe=$("#id_Hospital option:selected").val();
		if(ospe!=""){
			var paz=$("#id_patient").val();
			if (paz==""){
				paz="None";
			}
			var prot=$("#id_protocol option:selected").val();
			if(prot!=""){
				//devo prendere la lista dei localid chiesta al modulo clinico e verificare se
				//quello inserito dall'utente si trova all'interno
				var lislocal=dizlocalid[prot];
				if (lislocal.indexOf(paz)>-1){
					$("#local_exists").val("True");
				}
				else{
					$("#local_exists").val("False");
				}
				
				var url=base_url+"/api/check/patient/"+coll+"/"+paz+"/"+ospe+"/"+prot;
				$.getJSON(url,function(d){
					var eve=d.event;
					var localid=d.idgrafo;
					//il consenso esiste gia' e la API mi ha dato il cod paziente
					if (eve=="ci_exists"){
						var paziente=d.paz;
						//se il paziente dato dalla API e' uguale a quello inserito dall'utente
						if(paziente==paz){
							jQuery("#dialogMess").html("Informed consent already present. Do you want to proceed anyway?");
						}
						else{
							jQuery("#dialogMess").html("Informed consent already present and it is related to patient code '"+paziente+"'. Do you want to proceed anyway?");
						}
						jQuery("#dia").dialog({
				            resizable: false,
				            height:200,
				            width:450,
				            modal: true,
				            draggable :false,
				            buttons: {
				                "Yes": function() {
				                    jQuery( this ).dialog( "close" );
				                    $("#id_patient").val(paziente);
				                    //imposto nel campo nascosto che il cons esiste gia'
				                    $("#cons_exists").val("True");
				                    $("#localid").val(localid);
				                    $("#primo_form").submit();
				                },
				                "No": function() {
				                    jQuery( this ).dialog( "close" );
				                }
				            },
				        });
					}
					//il consenso esiste gia' e dalla API e' risultato che non ha un cod paziente (alias)
					else if (eve=="alias_exists"){
						if(paz=="None"){
							jQuery("#dialogMess").html("Informed consent already present. Do you want to proceed anyway?");
						}
						else{
							jQuery("#dialogMess").html("Informed consent already present for this patient. Do you want to proceed anyway?");
						}
				        jQuery("#dia").dialog({
				            resizable: false,
				            height:200,
				            width:450,
				            modal: true,
				            draggable :false,
				            buttons: {
				                "Yes": function() {
				                    jQuery( this ).dialog( "close" );
				                    //non annullo piu' il valore del paziente, ma lascio quello che ha scritto (o non scritto) l'utente
				                    //$("#id_patient").val("");
				                    //imposto nel campo nascosto che il cons esiste gia'
				                    $("#cons_exists").val("True");
				                    $("#localid").val(localid);
				                    $("#primo_form").submit();
				                },
				                "No": function() {
				                    jQuery( this ).dialog( "close" );
				                }
				            },
				        });
					}
					else if (eve=="new"){
						//imposto nel campo nascosto che il cons non esiste
	                    $("#cons_exists").val("False");
	                    $("#localid").val("None");
						$("#primo_form").submit();
					}
				});
			}
			else{
				alert("Please select study protocol");
			}
		}
		else{
			alert("Please select hospital");
		}
	}
}

/**** CANCELLAZIONE ALIQUOTE INSERITE ****/

function deleteAliquot(genID,idoperaz){
    var pos = ""; 
    console.log(genID);
    for (typeA in collez){
        for (barcode in collez[typeA]){
            for (var i = 0; i < collez[typeA][barcode].length; i++){
                if (collez[typeA][barcode][i]['genID'] == genID){
                    console.log('trovato genid');
                    pos = collez[typeA][barcode][i]['pos'];
                    //if ((collez[typeA][barcode][i]['qty'] == 1)||collez[typeA][barcode][i]['qty'] == "-"){
                    	//vedo se ci sono altri campioni che afferiscono a quella piastra
                        if (collez[typeA][barcode].length == 1){                       	
                        	delete collez[typeA][barcode];
                        }else{
                        	collez[typeA][barcode].splice(i,1); 
                        }                       
                    /*}else{
                    	collez[typeA][barcode][i]['qty']--;
                    	//cancello anche gli id dell'operazione nella lista 
                    	var lista=collez[typeA][barcode][i]['list'];
                    	for (var j=0;j<lista.length;j++){
                    		if (lista[j]==idoperaz){
                    			lista.splice(j,1);
                    			break;
                    		}
                    	}
                    	collez[typeA][barcode][i]['list']=lista;
                    }*/
                    
                    deleteInPlate(typeA, barcode, pos, genID);
                    //storageIt('collect', JSON.stringify(collez));
                    console.log(collez);
                    return;
                }
            }
        }
    }
}

function deleteInPlate(typeA, barcode, pos, genID){
	//se pos è uguale a "-", allora ho caricato una provetta singola. Altrimenti ho posizionato il campione in una piastra.
	if(pos=="-"){
		removeNotPlateBarcode(barcode);
	}
	else{
		var barc_pias_attuale=$("#barcode_rna").val();
		if (typeA == 'VT'){
			if (barc_pias_attuale == barcode){
				canc("v-"+pos);
			}
		}
	    else if (typeA == 'SF'){
	        if (barc_pias_attuale == barcode){
	            canc('s-' + pos);
	        }
	    }
	    else if (typeA == 'PL'){
	    	if (barc_pias_attuale == barcode){
	            canc('l-' + pos);
	        }
	    }
	    else if (typeA == 'PX'){
	    	if (barc_pias_attuale == barcode){
	            canc('x-' + pos);
	        }
	    }
	    else if (typeA == 'FR'){
	    	if (barc_pias_attuale == barcode){
	            canc('f-' + pos);
	        }
	    }
	    else {
	    	if (barc_pias_attuale == barcode){
	            canc('r-' + pos);
	        }  
	    }   
	}
    
}

//per cancellare l'inserimento in una piastra (RNA, SNAP, VITAL)
function canc(id_tube){
    id_tube = "#" + id_tube;
    var num = parseInt($(id_tube).text());
    if(num > 1){
        num = num - 1;
        $(id_tube).text(num);
    }
    else{
        $(id_tube).css("background-color","rgb(249,248,242)");
        $(id_tube).text(0);
        $(id_tube).removeAttr('sel');
        $(id_tube).removeAttr('onmouseover');
        $(id_tube).removeAttr('onmouseout');
        $(id_tube).attr("disabled", false );
    }
}

function removeNotPlateBarcode(barcode){
    for (var i=0; i < vett_used_barc.length; i++){
        if (vett_used_barc[i] == barcode){
        	vett_used_barc.splice(i,1);
        }
    }
    //localStorage.setItem('vett_used_barc', vett_used_barc.toString());
}

function contatore_genid(typeA,tissue, barcodeP, pos, salvacentro){
    var counter = 1;
    if (Object.size(collez[typeA]) > 0){
    	var check = checkForMissingCounter(typeA, tissue, barcodeP, pos,salvacentro);
        for (key in collez[typeA]){
            //key e' il codice della piastra
            for (var i = 0; i < collez[typeA][key].length; i++) {
            	//entra qui solo se clicco due volte sulla stessa posizione: Quindi non devo incrementare il contatore, ma
            	//prendere quello che c'e' gia'
            	if (key == barcodeP){
	                if (collez[typeA][key][i]['pos'] == pos){
	                    return collez[typeA][key][i]['counter'];
	                }
            	}
            	//normalmente entra qui e mi fa salire il contatore nel caso inserisca piu' campioni con le stesse caratteristiche
                if ((tissue == collez[typeA][key][i]['tissueType'])&&(salvacentro==collez[typeA][key][i]['centro'])){
                    counter++;
                }
            }
        }
    }
    console.log("count "+counter);
    console.log("check "+check);
    //se il contatore che guarda i buchi vuoti nella serie di campioni uguali inseriti e' >0, allora uso lui
    if ((check > 0)&&(check<=counter))
        return check;
    return counter;
}

//serve a trovare il primo contatore libero, quindi in caso di cancellazioni nella schermata riesce a coprire i buchi
//lasciati dall'eliminazione dei campioni
function checkForMissingCounter( typeA, tissue, barcodeP, pos,salvacentro){
    var found = false;
    //guardo quante aliq sono gia' presenti nel DB e questo e' salvato nel diz. Se non c'e' ancora la
    //chiave inizializzo a zero la variabile
    if(tissue+salvacentro+typeA in diz_aliq_presenti){
    	var aliq_presenti=diz_aliq_presenti[tissue+salvacentro+typeA];
    }
    else{
    	var aliq_presenti=0;
    }
    for (var i = aliq_presenti+1; i <= contaaliq+aliq_presenti; i++) {
        found = false;
        for (key in collez[typeA]){    
            for (var j = 0; j < collez[typeA][key].length; j++) {
                if ((parseInt(collez[typeA][key][j]['counter']) == i)&&(collez[typeA][key][j]['tissueType']==tissue)&&(collez[typeA][key][j]['centro']==salvacentro)){
                    found = true;
                    console.log(found);
                }
            }
        }
        if (found == false)
            return i-aliq_presenti;
    }
    return -1;
}

function saveInLocal(tipo, tissue, pos, barcodeP, newG, counter,salvacentro,vol,conc,pur1,pur2,ge,vollinea,conta){
    var index = 0;
    if (collez[tipo][barcodeP]){
        var found = false;
        for (var i = 0; i < collez[tipo][barcodeP].length; i++) {
            if (pos == collez[tipo][barcodeP][i]['pos']){
            	collez[tipo][barcodeP][i]['qty']++;
            	collez[tipo][barcodeP][i]['list'].push(contaaliq);
                found = true;
            }
        }
        if (found == true){
        	console.log("trovato");
            //storageIt('collect', JSON.stringify(collez));
        	return;
        }else{
            index = (collez[tipo][barcodeP]).length;
        }
    }
    else{
        collez[tipo][barcodeP] = [];
    }

    console.log(parseInt(counter));
    collez[tipo][barcodeP][index] = {}
    if(!($("#id_Pieces").attr("disabled"))){
		var numero=$("#id_Pieces").attr("value");
	}
    else{
    	var numero="-";
    }
    collez[tipo][barcodeP][index]['qty'] = numero;
    collez[tipo][barcodeP][index]['genID'] = newG;
    collez[tipo][barcodeP][index]['pos'] = pos;
    collez[tipo][barcodeP][index]['tissueType'] = tissue;
    collez[tipo][barcodeP][index]['counter'] = parseInt(counter);
    collez[tipo][barcodeP][index]['centro'] = salvacentro;
    if (vol!=""){
    	collez[tipo][barcodeP][index]['volume']=vol;
    }
    if (conc!=""){
    	collez[tipo][barcodeP][index]['conc']=conc;
    }
    if (pur1!=""){
    	collez[tipo][barcodeP][index]['pur1']=pur1;
    }
    if (pur2!=""){
    	collez[tipo][barcodeP][index]['pur2']=pur2;
    }
    if (ge!=""){
    	collez[tipo][barcodeP][index]['ge']=ge;
    }
    if (vollinea!=""){
    	collez[tipo][barcodeP][index]['vollinea']=vollinea;
    }
    if (conta!=""){
    	collez[tipo][barcodeP][index]['conta']=conta;
    }
    collez[tipo][barcodeP][index]['list'] = [];
    collez[tipo][barcodeP][index]['list'].push(contaaliq);
    
    console.log(collez);
    //storageIt('collect', JSON.stringify(collez));    
}

////LOCAL STORAGE FUNCTIONS
function storageIt(key, value){
    localStorage.setItem(key, value);
    localStorage.setItem(key + 'timestamp', new Date().getTime());
    localStorage.setItem(key + 'user', $("#actual_username").val());
}

function cerca_barc_duplicati(barc){
	var trovato=0;
	for (i=0;i<vett_used_barc.length;i++){
		if (vett_used_barc[i]==barc){
			return true;
		}
	}
	return false;
}

//funzione che gestisce l'apertura della pagina per inserire i parametri clinici
function apri_pagina_parametri(){
	var valtum=$("#id_Tumor_Type option:selected").val();
	if(valtum==""){
		alert("Please first select Tumor type");
	}
	else{
		var url=base_url+"/collection/param/";
		window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width="+screen.width+",height="+screen.height);
	}
}

//serve a capire se la tabella sotto, con le aliq, e' vuota
//o meno
function vuota(){
	var listarighe=$("#aliquots_table tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#aliquots_table tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
}

//dato un protocollo selezionato dall'utente, carica dal modulo clinico
//tutti i posti collegati a quel progetto
function carica_ospedali(){
	var prot=$("#id_protocol option:selected").val();
	var url=base_url+"/api/getHospital/"+prot+"/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			$("#id_Hospital option").not(":first").remove();
			for(var i=d.data.length;i>0;i--){
				var stringa="<option value="+d.data[i-1][0]+">"+d.data[i-1][1]+"</option>"
				$("#id_Hospital option[value=\"\"]").after(stringa);
			}
			//chiamo la API per avere la lista dei local id possibili solo se non e' gia' in memoria
			if (prot in dizlocalid){
				var lislocalid=dizlocalid[prot];
				$( "#id_patient" ).autocomplete({
			      source: function(request, response) {
			          var results = $.ui.autocomplete.filter(lislocalid, request.term);

			          response(results.slice(0, 10));
			      }
			    });
			}
			else{
				var url=base_url+"/api/localID/list/"+prot+"/";
				$.getJSON(url,function(ris){
					//ris e' un dizionario con chiave l'id del prot e valore la lista di localid
					dizlocalid[prot]=ris[prot];
					$( "#id_patient" ).autocomplete({
				      source: function(request, response) {
				          var results = $.ui.autocomplete.filter(ris[prot], request.term);

				          response(results.slice(0, 10));
				      }
				    });
				});
			}
		}
		else{
			alert("Select study protocol");
		}
	});
}

$(document).ready(function () {
	
	var oTable = $("#aliquots_table").dataTable( {
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
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Further Info", 
            	"bVisible":false,
            	"sClass": "furth_info", 
            },
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[1, 'desc']],
	    "aoColumnDefs": [
	        { "bSortable": false, "aTargets": [ 0 ] },
	    ],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
	
	var tabfin=$("#aliq");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Collection","aliq");
	}
	
	//per popolare la lista con dentro i wg
	var lisworkgr=$("#id_workgr");
	if(lisworkgr.length!=0){
		var liswg=workingGroups.split(",");
		for (var i=0;i<liswg.length;i++){
			$("#id_workgr").append("<option value="+liswg[i]+">"+liswg[i]+"</option>");
		}
	}
	
	$("#rna button").css("background-color","lightgrey");
	var url = base_url + "/api/ext/aliquottype/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			tipialiq=d.data;
		}
	});
	listaerr=$(".errorlist");
	//solo se mancano dei dati nel form
	if(listaerr.length!=0){
		//$(".f p").prepend("<br><br>");
		//inserisco a tutti i p un margine sopra
		$(".f p").attr("style","margin-top:3em");
		//prendo tutti gli ul, che sono i messaggi di errore
		var lista=$(".f ul");
		for(i=0;i<lista.length;i++){
			//prendo il p che segue un messaggio di errore
			var paragrafo=$(lista[i]).next();
			//$(paragrafo).attr("id",i);
			//var str="#"+i+" br";
			//$(str).remove();
			$(paragrafo).removeAttr("style");
			//metto dentro al p il messaggio di errore
			$(paragrafo).prepend($(listaerr[i]));
		}
	}
	//leggo il valore del campo hidden per capire di che tipo e' il form
	tipo=$("#tipo_collezione").attr("value");
	//per aggiornare la pagina
	//location.reload(true);
	if(tipo==1){
		/*if(listaerr.length==0){
			//per far comparire il campo per il caso
			$(".f p:first").after("<p><label for=\"id_case\">Case:</label>"+
				"<select id=\"id_case\" name=\"case\" style=\"overflow: auto;\"><option selected=\"selected\" value=\"\">---------</option>"+
				"</select></p>");
		}
		else{
			//per far comparire il campo per il caso
			$(".f p:first").after("<p style='margin-top:3em;'><label for=\"id_case\">Case:</label>"+
				"<select id=\"id_case\" name=\"case\" style=\"overflow: auto;\"><option selected=\"selected\" value=\"\">---------</option>"+
				"</select></p>");
		}*/
		//per far andare a capo i campi del form
		//$(".f p:nth-child(4)").after("<br style=\"clear:left\"/>");
		//$(".f p:nth-child(7)").after("<br style=\"clear:both\"/>");
		//$(".f p:nth-child(11)").after("<br style=\"clear:left\"/>");
		//$(".f p:nth-child(15)").after("<br style=\"clear:left\"/>");
		$("#id_Tumor_Type").change(aggiorna);
		$("#cont_h1").text("Assign aliquot to existing collection");
		$("#id_case option").not(":first").remove();
		
		$("#id_date").datepicker({
			 dateFormat: 'yy-mm-dd'
		});
		$("#id_date").datepicker('setDate', new Date());
	}
	else if (tipo==0){
		//per far andare a capo i campi del form
		//$("#form1 p:nth-child(4)").after("<br style=\"clear:both\"/>");
		//$(".f p:nth-child(9)").after("<br style=\"clear:both\"/><br>");
		//$("#form2 p:nth-child(5)").after("<br style=\"clear:both\"/>");
		$("#cont_h1").text("Assign aliquot to new collection");	
		$("#param").click(apri_pagina_parametri);
		//metto nel select dei posti la solita riga vuota iniziale
		var stringa="<option value=''>---------</option>"
		$("#id_Hospital").append(stringa);
		//scatta quando viene scelto un protocollo e carica dal modulo clinico i posti
		//collegati a quel protocollo
		$("#id_protocol").change(carica_ospedali);
		
		$("#id_randomize").css("margin-top","0.6em");
		$("#id_randomize").css("margin-left","2.7em");
		//se c'e' il campo per il genid, vuol dire che ho fatto comparire anche il secondo form e quindi
		//devo disabilitare i campi del primo
		var genid=$("#gen_id");
		if (genid.length!=0){
			var listacampi=$("#form1 select,#form1 input,#id_workgr").attr("disabled",true);
			//per prendere il valore del wg dal campo nascosto e popolare la lista
			var ww=$("#id_wgroup").val();
			if(ww!="/"){
				$("#id_workgr option[value="+ww+"]").attr("selected","selected");
			}
			//in base al protocollo mi faccio restituire gli ospedali e poi seleziono quello che era stato
			//scelto nel form iniziale
			var prot=$("#id_protocol option:selected").val();
			var url=base_url+"/api/getHospital/"+prot+"/";
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					$("#id_Hospital option").not(":first").remove();
					for(var i=d.data.length;i>0;i--){
						var stringa="<option value="+d.data[i-1][0]+">"+d.data[i-1][1]+"</option>"
						$("#id_Hospital option[value=\"\"]").after(stringa);
					}
					//da un campo nascosto prendo il posto scelto prima 
					var idposto=$("#posto").val();
					$("#id_Hospital option[value="+idposto+"]").attr("selected","selected");
				}
			});			
		}
		else{
			//faccio comparire la data di oggi solo se e' presente solo il primo form, altrimenti
			//quando ricarica la pagina per far comparire il secondo form, mi rimette la data odierna
			//anche se prima l'ho cambiata
			$("#id_date").datepicker({
				 dateFormat: 'yy-mm-dd'
			});
			$("#id_date").datepicker('setDate', new Date());
		}
	}
	
	$("#id_scongcell,#id_passagecell,#id_lincell").attr("disabled",true);
	$("#id_scongcell,#id_passagecell,#id_lincell").parent().css("display","none");
	
	//per diminuire la dimensione degli input
	$(".f input").attr("size","7");
	$("#id_lineage").attr("size","2");
	$("#id_Barcode,#id_Barc,#id_barcode_Operation,#gen_id").attr("size","10");
	
	//per la tabella delle posizioni
	//tolgo la vecchia intestazione alle tabelle
	$("#tabpiastra table tr>th").text("");
	
	//disabilito tutti i pulsanti all'inizio
	$("#rna button,#id_Barcode,#id_Position").attr("disabled",true);
	
	/* Add event listener for deleting row  */
    $("#aliquots_table tbody td.control_center img").live("click", function () {
        var genID = $($($(this).parents('tr')[0]).children()[4]).text();
        var operaz = $($($(this).parents('tr')[0]).children()[1]).text();
        deleteAliquot(genID,operaz);
        var nTr = $(this).parents('tr')[0];
        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
    });
    
	$("#load_rna_plate").click(caricaPiastra);
	$("#rna button").click(campione_piastra);
	$("#id_vector").change(aggiornaVettore);

	$("#id_Aliquot_Type").change(aggiornaAliquota);
	
	$("#barcode_rna").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			caricaPiastra();
		}
	});
	
	$("#conf_aliq").click(salva_aliq);
	
	$("#id_Barc").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			salva_aliq();
		}
	});		
	
	//quando clicco sul pulsante submit
    $("#conferma_finale").click(function(event){
    	event.preventDefault();
    	if(!vuota()){
	    	var timer = setTimeout(function(){$("body").addClass("loading");},500);		
			var wg_temp=$("#id_wgroup").val();
			var wg_fin="";
			if(wg_temp!="/"){
				wg_fin=wg_temp;
			}
			//comunico la struttura dati al server
			var data = {
					salva_nuova:true,
					dati:JSON.stringify(collez),
		    		operatore:$("#actual_username").val(),
		    		tum:$("#id_Tumor_Type option:selected").val(),
		    		itemcode:$("#caso_fin").val(),
		    		ospedale:$("#id_Hospital option:selected").val(),
		    		dat:$("#id_date").val(),
		    		collectevent:$("#id_barcode_Operation").val(),
		    		paziente:$("#id_patient").val(),
		    		protoc:$("#id_protocol option:selected").val(),
		    		wg:wg_fin,
		    		cons_exists:$("#cons_exists").val(),
		    		local_id:$("#localid").val(),
		    		local_exists:$("#local_exists").val()
		    };
			var url=base_url+"/extern/save/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	$("#secondo_form").append("<input type='hidden' name='final' />");
		    	$("#secondo_form").submit();
		    });
    	}
    	else{
			alert("Please insert some aliquots");
		}
    });
    
    //quando clicco sul pulsante submit
    $("#conferma_esistente").click(function(event){    	
		event.preventDefault();
		if(!vuota()){
			var timer = setTimeout(function(){$("body").addClass("loading");},500);
			var wg_fin=$("#id_workgr option:selected").val();
			//comunico la struttura dati al server
			var data = {
					esistente:true,
					dati:JSON.stringify(collez),
		    		operatore:$("#actual_username").val(),
		    		tum:$("#id_Tumor_Type option:selected").val(),
		    		itemcode:$("#id_case option:selected").text(),
		    		dat:$("#id_date").val(),
		    		wg:wg_fin
		    };
			var url=base_url+"/extern/save/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	$("#secondo_form").append("<input type='hidden' name='final' />");
		    	$("#secondo_form").submit();
		    });
		}
    	else{
			alert("Please insert some aliquots");
		}
    });
    
    $("#conferma2").click(function(event){
		event.preventDefault();
		//verifico la validita' della data
		var dd=$("#id_date").val().trim();
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			alert("Incorrect data format: it should be YYYY-MM-DD");
		}
		else{
			verifica_coll_event();
		}
	});	
});

