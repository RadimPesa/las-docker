var dizlabindici=[];
var lislabel=[];
var indicetab=1;
var codiceload_banca="";
//ha la lista dei gen caricati dalla biobanca. Per evitare di caricare due volte lo stesso gen
var lisgencaricati=[];
//chiave la label e valore la descrizione
var dizdescription={};

//parte quando si clicca sul tasto per aggiungere un campione 
function add_sample(){
	var regex=/^[0-9]+$/;
	var regexnumeri=/^[0-9.]+$/;
	var diztemp={};	
	
	var origin=$("#origin option:selected").val();
	if(origin==""){
		alert("Please select origin");
		return;
	}
	diztemp["Origin"]=origin;
	var tissue=$("#tissue option:selected").val();
	if(tissue==""){
		alert("Please select primary tissue");
		return;
	}
	diztemp["tissue"]=tissue;
	diztemp["Primary tissue"]=$("#tissue option:selected").text();
	var label=origin+"_"+tissue;
	//indica se e' PR o metastasi e non e' obbligatorio
	var stage=$("#stage option:selected").val();
	if(stage!=""){
		label+="_"+stage;
	}
	diztemp["stage"]=stage;
	diztemp["Tumor stage"]=$("#stage option:selected").text();
	//e' il tessuto metastatico e non e' obbligatorio
	var mettissue=$("#met_loc option:selected").val();
	if(mettissue!=""){
		label+="_"+mettissue;
	}
	diztemp["mettissue"]=mettissue;
	diztemp["Metastasis tissue"]=$("#met_loc option:selected").text();
	
	var barc=$("#name").val().trim();
	barc = barc.replace(/ /g, '_');
	if(barc==""){
		alert("Please insert sample name (max. 8 characters)");
		return;
	}
	label+="_"+barc;
	diztemp["Sample name"]=barc;
	//e' un duplicato ma lo metto perche' nel template del report non posso accedere ad un campo il cui nome ha uno spazio
	diztemp["barc"]=barc;
	/*
	//e' il numero di vial per la biopsia liquida e non e' obbligatorio
	var vial=$("#vial").val().trim();
	vial = vial.replace(/ /g, '_');
	if(vial!=""){
		label+="_"+vial;
	}
	diztemp["vial"]=vial;*/
	
	var feat=$("#feature option:selected").val();
	if(feat==""){
		alert("Please select a feature");
		return;
	}
	label+="_"+feat;
	diztemp["feat"]=feat;
	diztemp["Feature"]=$("#feature option:selected").text();
	
	var featnum=$("#feat_number").val().trim();
	if((featnum!="")&&(!regex.test(featnum))){
		alert("You can only insert integer number. Please correct value for feature number");
		return;
	}
	if(featnum!=""){
		//non metto il _ perche' questo e' il numero della feature e lo concateno direttamente
		label+=featnum;
	}
	diztemp["Feature number"]=featnum;
	
	var drug=$("#drug").val().trim();
	drug = drug.replace(/ /g, '_');
	if(drug!=""){
		label+="_"+drug;
	}
	diztemp["Drug"]=drug;
	
	var clone=$("#clone").val().trim();
	if((clone!="")&&(!regex.test(clone))){
		alert("You can only insert integer number. Please correct value for clone");
		return;
	}
	if(clone!=""){
		label+="_CL"+clone;
	}
	diztemp["Clone"]=clone;
	
	var utente=$("#user").val().trim();
	if(utente==""){
		alert("Please insert user");
		return;
	}
	utente= utente.replace(/ /g, '_');
	diztemp["user"]=utente;
	
	var dd=$("#date_extr").val().trim();
	if(dd==""){
		alert("Please insert value for extraction date");
		return;
	}
	else{
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			alert("Incorrect format for extraction date: it should be YYYY-MM-DD");
			return;
		}
	}
	diztemp["Extraction date"]=dd;
	//mi dice se e' DNA o RNA
	var tipo=$("#tipo option:selected").val();
	diztemp["tipo"]=tipo;
	
	var source=$("#source option:selected").val();
	if((source=="")&&(!($("#source").is(":disabled")))){
		alert("Please select source");
		return;
	}
	diztemp["source"]=source;
	diztemp["Source"]=$("#source option:selected").text();;
	//e' una serie di input con valori numerici come il volume o la purezza e li controllo tutti insieme
	var lisvalnum=$(".numvalue");
	for (var i=0;i<lisvalnum.length;i++){
        var numero=$(lisvalnum[i]).val().trim();
		if(!($(lisvalnum[i]).is(":disabled"))){
			var id=$(lisvalnum[i]).attr("id");
			var nomelabel=$("label[for="+id+"]").text();
			var labfin=nomelabel.substr(0,nomelabel.length-2).toLowerCase();
			if(numero==""){
				alert("Please insert value for "+labfin);
				return;
			}
			else{
				if(!regexnumeri.test(numero)){
					alert("You can only insert number. Please correct value for "+labfin);
					return;
				}
			}
		}
        var nome=$(lisvalnum[i]).attr("name");
        diztemp[nome]=numero;
	}
	
	var elution=$("#elution").val().trim();
	if(elution==""){
		alert("Please insert elution buffer");
		return;
	}
	diztemp["Elution buffer"]=elution;
	
	var capture=$("#capture option:selected").val();
	if(capture==""){
		alert("Please select capture type");
		return;
	}
	diztemp["capture"]=capture;
	
	var description=$("#id_descr").val().trim();
	if(description==""){
		alert("Please insert a description");
		return;
	}	
	diztemp["description"]=description;
	
	//non faccio il controllo sull'univocita' del nome del campione perche' tanto nella biobanca avro' un mio id univoco
	//Ma faccio il controllo sull'univocita' della label aggiungendo in fondo un _numprogressivo
	var labtemp=label;
	if (label in dizlabindici){
		var numfinale=dizlabindici[label];		
		label+="_"+String(numfinale);
		numfinale+=1;
		dizlabindici[labtemp]=numfinale;
	}
	else{
		var numfinale=2;
		dizlabindici[label]=numfinale;
	}
	var oTable=$("#tab_insert").dataTable();
	if(codiceload_banca!=""){
		oTable.fnSetColumnVis( 3, true );
		lisgencaricati.push(codiceload_banca);
	}
	oTable.fnAddData( [indicetab, label, barc,codiceload_banca, null,labtemp+"|"+String(numfinale)] );
	diztemp["label"]=label;
	diztemp["indice"]=indicetab;
	diztemp["genealogy"]=codiceload_banca;
	lislabel.push(diztemp);
	dizdescription[label]=description;
	$("#nano,#pur280,#pur230,#tipo,#fluo,#date_extr,#source,#met_loc,#stage,#tissue,#user,#origin").attr("disabled",false);
	
	var stage=$("#stage option:selected").val();
	if(stage=="PR"){
		$("#met_loc").attr("disabled",true);
		$("#met_loc option[value='']").attr("selected","selected");
	}
	
	//cancello i dati inseriti per il campione precedente
	$("#basic .da_canc,#extra .da_canc").val("");
	$("#basic,#extra").find("select option[value='']").attr("selected","selected");
	
	indicetab+=1;
	codiceload_banca="";
}

function block_procedure(timer){
	$("#nano,#pur280,#pur230,#tipo,#fluo,#date_extr,#source").attr("disabled",false);
	//tolgo i valori inseriti dall'utente per il campione
	$("#vial,#name,#fluo,#nano,#pur280,#pur230").val("");
	clearTimeout(timer);
	$("body").removeClass("loading");
}

function load_sample_biobank(){
	var gen=$("#vial").val().trim();
	if(gen==""){
		alert("Please insert a valid genealogy ID or barcode");
		return;		
	}
	var user=$("#actual_username").val();
	var url =  base_url + "/api.insertsample/loadfrombiobank/" + gen+"/"+user+"/";
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
    jQuery.ajax({
        type: 'GET',
        url: url, 
        success: function(transport) {            
            var res=transport["data"];
            if(res!="errore"){
            	var r=JSON.parse(res);
	            var diz=r[gen];            
	            if(diz["exists"]=="no"){
	            	alert(gen+ " does not exist in LAS");
	            	block_procedure(timer);
	            	return;
	            }
	            if(diz["available"]=="no"){
	            	alert(gen+ " is not available because it owns to another user");
	            	block_procedure(timer);
	            	return;
	            }
	            if((diz["type"]!="DNA")&&(diz["type"]!="RNA")){
	            	alert(gen+ " is not DNA or RNA");
	            	block_procedure(timer);
	            	return;
	            }
	            if($.inArray(diz["genealogy"], lisgencaricati)!=-1){
	            	alert(gen+ " has already been loaded");
	            	block_procedure(timer);
	            	return;
	            }
	            $("#nano,#pur280,#pur230,#origin,#user").attr("disabled",false);
	            $("#origin option[value='']").attr("selected","selected");
	            //il volume e' quello usato e non quello di partenza del campione, quindi non e' da preimpostare ma deve essere inserito dall'utente
	            //$("#volume").val(diz["vol"]);
	            if ("conc" in diz){
	            	$("#nano").val(diz["conc"]);
	            	$("#nano").attr("disabled",true);
	            }
	            else{
	            	$("#nano").val("");
	            }
	            if ("pur280" in diz){
	            	$("#pur280").val(diz["pur280"]);
	            	$("#pur280").attr("disabled",true);
	            }
	            else{
	            	$("#pur280").val("");
	            }
	            if ("pur230" in diz){
	            	$("#pur230").val(diz["pur230"]);
	            	$("#pur230").attr("disabled",true);
	            }
	            else{
	            	$("#pur230").val("");
	            }
	            if ("date" in diz){
	            	$("#date_extr").val(diz["date"]);
	            }
	            else{
	            	$("#date_extr").val("");
	            }
	            if ("source" in diz){
	            	$("#source option[value='"+diz["source"]+"']").attr("selected",true);
	            }
	            else{
	            	$("#source option[value='']").attr("selected",true);
	            }
	            //utente che ha estratto il DNA
	            if(diz["user"]!="None"){
	            	$("#user").val(diz["user"]);
	            	$("#user").attr("disabled",true);
	            }
	            //mi occupo della sorgente
	            var mothertype=diz["mothertype"];
	            var vector=diz["mothervector"];
	            if(mothertype=="PL"){
	            	$("#origin option[value='cfDNA']").attr("selected",true);
	            	$("#origin").attr("disabled",true);
	            }
	            //ipotizzo che il VT sia PBMC perche' di solito non si estrae DNA dal VT classico
	            else if(mothertype=="VT"){
	            	$("#origin option[value='PBMC']").attr("selected",true);
	            	$("#origin").attr("disabled",true);
	            }
	            else if(mothertype=="FF"){
	            	$("#origin option[value='FFPE']").attr("selected",true);
	            	$("#origin").attr("disabled",true);
	            }
	            
	            if(vector=="X"){
	            	$("#origin option[value='Xeno']").attr("selected",true);
	            	$("#origin").attr("disabled",true);
	            }
	            else if(vector=="S"){
	            	$("#origin option[value='Sph']").attr("selected",true);
	            	$("#origin").attr("disabled",true);
	            }
	            //seleziono il tumore
	            var listum=$("#tissue option[value='"+diz["tumor"]+"']");
	            if(listum.length!=0){
	            	$("#tissue option[value='"+diz["tumor"]+"']").attr("selected",true);
	            	$("#tissue").attr("disabled",true);
	            }
	            else{
	            	$("#tissue").attr("disabled",false);
	            }
	            //seleziono il tipo di tessuto
	            if(diz["tissue"]=="PR"){
	            	$("#stage option[value='"+diz["tissue"]+"']").attr("selected",true);
	            	$("#met_loc,#stage").attr("disabled",true);
	    			$("#met_loc option[value='']").attr("selected","selected");
	            }
	            else{
	            	var lismet=$("#met_loc option[value='"+diz["tissue"]+"']");
	            	if(lismet.length!=0){
	            		$("#stage option[value='MET']").attr("selected",true);
	            		$("#met_loc option[value='"+diz["tissue"]+"']").attr("selected",true);
	            		$("#met_loc,#stage").attr("disabled",true);
	            	}
	            	else{
	            		$("#met_loc,#stage").attr("disabled",false);
	            		$("#met_loc option[value=''],#stage option[value='']").attr("selected",true);
	            	}
	            }
	            //preimposto il tipo di campione a DNA o RNA
	            $("#tipo option[value='"+diz["type"]+"']").attr("selected",true);
	            //assegno al codice globale il gen che ho caricato adesso
	            codiceload_banca=diz["genealogy"];
	            $("#tipo,#date_extr,#source").attr("disabled",true);	            
            }
            else{
            	alert("Error in loading data from biobank");
            }
            clearTimeout(timer);
	    	$("body").removeClass("loading");
        },  
        error: function(data) { 
            alert("Error! Please, try again.\n" + data.status, "Warning");
            clearTimeout(timer);
	    	$("body").removeClass("loading");
        }
    });
}

jQuery(document).ready(function(){
	$("#date_extr").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	
	var spinner = $("#clone,#feat_number").spinner(
	{
		min:1,
		max:100
	});
	
	$("#vial").autocomplete({
		source:base_url+'/api.insertsample/autocomplete/'
	});
	
	var oTable = $("#tab_insert").dataTable( {
        "bProcessing": true,
        "aoColumns": [
			{ "sTitle": "N" ,"sClass": "indexclass"},
			{ "sTitle": "Label","sClass": "labelclass" },
			{ "sTitle": "Sample name","sClass": "barcodeclass" },
			{ "sTitle": "Genealogy ID", "sClass": "genclasstable"},
			{ "sTitle": "Delete",
			"sClass": "control_center", 
			"sDefaultContent": '<span style="text-align:center;" class="ui-icon ui-icon-closethick"></span>',
			"sWidth": "5%"},
			{ "sTitle": "LabHidden","sClass": "labelhiddenclass"}
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[0, 'desc']],
	    "aoColumnDefs": [
	        { "bVisible": false, "aTargets": [ 3,5 ] },
	        { "bSortable": false, "aTargets": [ 3 ] },
	    ],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
	
	$("#insert").click(add_sample);
	$("#loadgen").click(load_sample_biobank);
	
	$("#stage").change(function(event){
		var stage=$("#stage option:selected").val();
		if(stage=="PR"){
			$("#met_loc").attr("disabled",true);
			$("#met_loc option[value='']").attr("selected","selected");
		}
		else if(stage=="MET"){
			$("#met_loc").attr("disabled",false);
		}
	});
	
	$("#vial").keypress(function(event){
		if ( event.which == 13 ) {
			load_sample_biobank();
		}
	});
	
	//quando si cancella una riga dal datatable
	$(document).on("click","#tab_insert tbody td.control_center span", function () {
		var indice=$($($(this).parents('tr')[0]).children(".indexclass")).text().trim();
		var label=$($($(this).parents('tr')[0]).children(".labelclass")).text().trim();
		var barc=$($($(this).parents('tr')[0]).children(".barcodeclass")).text().trim();
		var gen=$($($(this).parents('tr')[0]).children(".genclasstable")).text().trim();
		var labnascosta=$($($(this).parents('tr')[0]).children(".labelhiddenclass")).text().trim();
		
		//riporto indietro il contatore della label cancellata, cosi' alla prossima creazione riutilizzo lo stesso indice cancellato
		var labsplit=labnascosta.split("|");
		//in [0] c'e' la label originaria in [1] c'e' il contatore
		var contattuale=dizlabindici[labsplit[0]];
		
		//vuol dire che ho cancellato l'ultima label inserita quindi devo riportare indietro di 1 il contatore
		//se non e' l'ultima label non faccio niente
		if((contattuale)==parseInt(labsplit[1])){
			dizlabindici[labsplit[0]]=contattuale-1;
		}
		//guardo quante righe ci sono ancora con quella label
		var oTable = $("#tab_insert").dataTable();
		var righe=oTable.$(".labelhiddenclass");
		var conta=0;
		for (var i=0;i<righe.length;i++){
			var testo=$(righe[i]).text().trim();
			var tsplit=testo.split("|");
			if (tsplit[0]==labsplit[0]){
				conta++;
			}
		}
		if(conta==1){
			delete dizlabindici[labsplit[0]];
		}
		
		//devo togliere i dati da lislabel
		for (var i=0; i < lislabel.length; i++){
			if ((lislabel[i]["label"] == label)&&(lislabel[i]["indice"] == parseInt(indice))){
				lislabel.splice(i,1);
			}
		}
		
		//devo togliere il gen (se c'e') dalla lista dei caricati dalla biobanca
		for (var i=0; i < lisgencaricati.length; i++){
			if (lisgencaricati[i] == gen){
				lisgencaricati.splice(i,1);
			}
		}
        var nTr = $(this).parents('tr')[0];
        $("#tab_insert").dataTable().fnDeleteRow( nTr );
	});
	
	//Quando si clicca per confermare tutto parte la POST al server
	$("#save").click(function(event){
		event.preventDefault();
		//vuol dire che la lista delle aliquote sotto e' vuota
		if(lislabel.length==0){
			alert("Please insert at least a sample");
		}
		else{
			//devo creare il titolo
			var utente=$("#user").val().trim();
			
			var today = new Date();
			var dd = today.getDate();
			var mm = today.getMonth()+1; //January is 0!
			var yyyy = today.getFullYear();
			if(dd<10) {
			    dd='0'+dd;
			}
			if(mm<10) {
			    mm='0'+mm;
			}

			today = yyyy+'-'+mm+'-'+dd;
			var titolo=utente+"_"+today+"_"+String(lislabel.length);
			var campioni="-samples";
			if(lislabel.length==1){
				campioni="-sample";
			}
			titolo+=campioni;
			$("#titolodialog").val(titolo);
			$("#id_notes").val("");
			$("#id_notes").focus();
			jQuery( "#dialogTitle" ).dialog({
	            resizable: false,
	            height:320,
	            width:380,
	            modal: true,
	            draggable :false,
	            buttons: {
	                "OK": function() {
	                	var description=$("#id_notes").val().trim();
	                    jQuery( this ).dialog( "close" );
	        			var timer = setTimeout(function(){$("body").addClass("loading");},500);
	        			//comunico la struttura dati al server
	        	    	var data = {
	        	    			salva:true,
	        	    			sample:JSON.stringify(lislabel),
	        	    			//prendo direttamente dal dialog il valore del titolo
	        	    			titlereq:$("#titolodialog").val(),
	        	    			//e' la descrizione generica della richiesta
	        	    			description:description,
	        	    			dizdescr:JSON.stringify(dizdescription)
	        		    };
	        	    	
	        	    	var url=base_url+"/insert_sample/";
	        			$.post(url, data, function (result) {
	        				var res=JSON.parse(result);
	        		    	if (res["data"] == "errore") {
	        		    		alert("Error in saving data");
	        		    		clearTimeout(timer);
	        			    	$("body").removeClass("loading");
	        		    	}
	        		    	else{
	        		    		clearTimeout(timer);
	        			    	$("body").removeClass("loading");
	        		    		$("#form_conf").append("<input type='hidden' name='conferma' />");	    	
	        		    		$("#form_conf").submit();
	        		    	}
	        			});
	                },
	                "Cancel": function() {
	                    jQuery( this ).dialog( "close" );
	                }
	            }
	        });
			
		}
	});
});
