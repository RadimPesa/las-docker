var conta=0;
var barc_dupl=false;
var collez = {'VT':{}};
var contaaliq=1;
var vett_used_barc=new Array();
var nuov_cas=true;

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

function inizializza(){
	//questo per selezionare il giusto tumore in base alla linea cellulare scelta
	var tum=$("#tumor").val();
	if (tum!="/"){
		$("#id_Tumor_Type option[value="+tum+"]").attr("selected","selected");		
	}
	var sorg=$("#sorg").val();
	if (sorg!="/"){
		$("#id_source option[value="+sorg+"]").attr("selected","selected");
	}
	var tess=$("#tess").val();
	if (tess!="/"){
		$("#id_Tissue_Type option[value="+tess+"]").attr("selected","selected");
	}
	var vett=$("#vett").val();
	if (vett!="/"){
		$("#id_vector option[value="+vett+"]").attr("selected","selected");
	}
	var wgroup=$("#id_wgroup").val();
	if (wgroup!="/"){
		$("#id_workgr option[value="+wgroup+"]").attr("selected","selected");
	}
}

function campione_piastra(){
	var contatore=1;
	var barcode=$(this).attr("barcode");
	$("#id_barc").val(barcode)
	$("#id_barc").attr("disabled",true);
	if(controlla_campi()){
		$(this).css("background-color","red");
		//scrivo il nuovo numero nel pulsante
		$(this).text("1");
		$(this).attr("disabled",true);
		
		var tumore=$("#id_Tumor_Type option:selected").val();
		var caso=$("#caso_fin").val();
		
		var tess=$("#id_Tissue_Type option:selected").val();
		var nometess=$("#id_Tissue_Type option:selected").text();
		var vett=$("#id_vector option:selected").val();
		
		var scong=$("#id_scong").val().trim();
		
		var pass=$("#id_passage").val().trim();
		
		var pos=$(this).attr("id").split("-")[1];
		
		var cod_piastra=$("#barcode_rna").val();
		var counter = contatore_genid("VT", nometess, cod_piastra, pos,"0");
		//chiamo la API che mi crea il gen
		var url=base_url+"/api/ext/newgenid/"+tumore+"/"+caso+"/"+tess+"/"+vett+"/None/VT/"+counter+"/cell";
		$.getJSON(url,function(d){
			//mi da' il contatore dell'aliquota come stringa
			contatore=d.cont;
			var gen=d.gen;
			
			var scongorig=parseInt(d.scong);
			//var scongfin=scongorig+parseInt(scong);
			var scongfin=parseInt(scong);
			scongfin=zeroPad(String(scongfin),2);
			
			var passorig=parseInt(d.passage);
			//var passfin=passorig+parseInt(pass);
			var passfin=parseInt(pass);
			passfin=zeroPad(String(passfin),3);
			
			gen+=scongfin+passfin+"001VT"+zeroPad(contatore,2)+"00";
			$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, cod_piastra, pos, gen,null] );
			var vol=$("#id_vol").val();
			if (vol==undefined){
				vol="";
			}
			var conta=$("#id_conta").val();
			if (conta==undefined){
				conta="";
			}
			
			//salvo la nuova aliquota nella variabile locale e nel local storage
	        saveInLocal("VT", nometess, pos, cod_piastra, gen, contatore,"0",vol,conta);
	        
			contaaliq++;
			$("#id_barc").attr("disabled",false);
			$("#id_barc").val("");
			$("#id_source,#id_Tissue_Type,#id_vector,#id_scong,#id_passage").attr("disabled",true);
		});
	}
}

function caricaPiastra(){
	if ($("#barcode_rna").val() == "")
		alert("Insert the plate barcode");
	else{
		var timer = setTimeout(function(){$("body").addClass("loading");},2000);
		var nameP="tabpiastra";

	    var codice = $("#barcode_rna").val();
	    
		var barr=codice.replace(/#/g,"%23");
	    var url = base_url + "/api/generic/load/" + barr + "/VT/plate";
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
				alert("Plate selected is not viable");
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
		        $("#id_barc").attr("disabled",false);
		        piastra_ricaricata("VT",codice);
			}
	        clearTimeout(timer);
	    	$("body").removeClass("loading");
	    });    
	}
	$("body").removeClass("loading");
}

//carica le eventuali modifiche fatte in questa sessione alla piastra che si sta caricando
function piastra_ricaricata(typeP, barcodeP){
	nameP="v";
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
	if(($("#id_source option:selected").text()=="---------")){
		alert("Select source");
		return false;
	}
	if(($("#id_Tissue_Type option:selected").text()=="---------")){
		alert("Select tissue type");
		return false;
	}
	if(($("#id_vector option:selected").text()=="---------")){
		alert("Select vector");
		return false;
	}
	//e' il barcode della provetta
	if(!($("#id_barc").attr("value"))){
		alert("Insert tube barcode");
		return false;
	}
	else{
		var barc=$("#id_barc").attr("value");
		//se c'e' uno spazio nella stringa
		if(barc.indexOf(" ") !== -1){
			alert("There is a space in barcode. Please correct.");
			return false;
		}
	}
	
	//controllo il volume
	var vol=$("#id_volume").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for volume");
			return false;
		}
	}
	
	//controllo la conta
	var vol=$("#id_conta").attr("value");
	if (vol!=undefined){
		if((!regex.test(vol))){
			alert("You can only insert number. Correct value for count");
			return false;
		}
	}
	
	//controllo il passaggio
	var pass=$("#id_passage").attr("value");
	if(!($("#id_passage").attr("disabled"))&&(pass=="")){
		alert("Insert passage");
		return false;
	}
	if((!regex.test(pass))){
		alert("You can only insert number. Correct value for passage");
		return false;
	}
	else{
		if (pass==0){
			alert("Passage cannot be 0");
			return false;
		}
	}
	
	//controllo gli scongelamenti
	var scon=$("#id_scong").attr("value");
	if(!($("#id_scong").attr("disabled"))&&(scon=="")){
		alert("Insert thaw number");
		x=1;
	}
	if((!regex.test(scon))){
		alert("You can only insert number. Correct value for thawing cycles number");
		return false;
	}
	else{
		if (scon==0){
			alert("Thawing cycles cannot be 0");
			return false;
		}
	}
	
	return true;
}


//quando si clicca sul tasto per salvare un campione
function salva_aliq(){
	var contatore=1;
		
	if(controlla_campi()){
		var tumore=$("#id_Tumor_Type option:selected").val();
		var caso=$("#caso_fin").val();
		
		var tess=$("#id_Tissue_Type option:selected").val();
		var nometess=$("#id_Tissue_Type option:selected").text();
		var vett=$("#id_vector option:selected").val();
		
		var scong=$("#id_scong").val().trim();
		
		var pass=$("#id_passage").val().trim();

		var barcode=$("#id_barc").val();
		//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
		if (cerca_barc_duplicati(barcode)==false){
			var pos = '-';
			var counter = contatore_genid("VT", nometess, barcode, pos,"0");
	
			var url=base_url+"/api/ext/newgenid/"+tumore+"/"+caso+"/"+tess+"/"+vett+"/None/VT/"+counter+"/cell";
			$.getJSON(url,function(d){
				//mi da' il contatore dell'aliquota come stringa
				contatore=d.cont;
				var gen=d.gen;	
				var lbarc="";
				var codice=barcode.replace(/#/g,"%23");
				var url=base_url+"/api/collect/singletube/"+codice+"/VT/";
				$.getJSON(url,function(f){
					if(f.data=="err_esistente"){
						alert("Error. Barcode you entered already exists");
					}
					else if(f.data=="err_tipo"){
						alert("Error. Block isn't for viable");
					}
					else{
						var scongorig=parseInt(d.scong);
						//var scongfin=scongorig+parseInt(scong);
						var scongfin=parseInt(scong);
						scongfin=zeroPad(String(scongfin),2);
						
						var passorig=parseInt(d.passage);
						//var passfin=passorig+parseInt(pass);
						var passfin=parseInt(pass);
						passfin=zeroPad(String(passfin),3);
						
						gen+=scongfin+passfin+"001VT"+zeroPad(contatore,2)+"00";
						vett_used_barc.push(barcode);
					    //localStorage.setItem('vett_used_barc', vett_used_barc.toString());
						$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, barcode, pos, gen,null] );
						var vol=$("#id_volume").val();
						if (vol==undefined){
							vol="";
						}
						var conta=$("#id_conta").val();
						if (conta==undefined){
							conta="";
						}
						//salvo la nuova aliquota nella variabile locale e nel local storage
				        saveInLocal("VT", nometess, pos, barcode, gen, contatore,"0",vol,conta);
				        
						contaaliq++;
						$("#id_barc").val("");
						$("#id_source,#id_Tissue_Type,#id_vector,#id_scong,#id_passage").attr("disabled",true);
					}
				});			
			});
		}
		else{
			alert("Error. You have already used this barcode in this session.");
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
            	if (key == barcodeP){
	                if (collez[typeA][key][i]['pos'] == pos){
	                    return collez[typeA][key][i]['counter'];
	                }	  
            	}
            	//alert(tissue);
            	//alert(collez[typeA][key][i]['tissueType']);
                if ((tissue == collez[typeA][key][i]['tissueType'])&&(salvacentro==collez[typeA][key][i]['centro'])){
                    counter++;
                }
            }         
        } 
    }
    console.log("count "+counter);
    if (check > 0)
        return check;
    return counter;
}

function checkForMissingCounter( typeA, tissue, barcodeP, pos,salvacentro){
    var found = false;    
    for (var i = 1; i <= contaaliq; i++) {
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
            return i;       
    }
    return -1;
}

function saveInLocal(tipo, tissue, pos, barcodeP, newG, counter,salvacentro,vol,conta){
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
        	return;
        }else{
            index = (collez[tipo][barcodeP]).length;
        }
    }else{
        collez[tipo][barcodeP] = [];
    }

    console.log(parseInt(counter));
    collez[tipo][barcodeP][index] = {}
    
    collez[tipo][barcodeP][index]['qty'] = "-";
    collez[tipo][barcodeP][index]['genID'] = newG;
    collez[tipo][barcodeP][index]['pos'] = pos;
    collez[tipo][barcodeP][index]['tissueType'] = tissue;
    collez[tipo][barcodeP][index]['counter'] = parseInt(counter);
    collez[tipo][barcodeP][index]['centro'] = salvacentro;
    if (vol!=""){
    	collez[tipo][barcodeP][index]['volume']=vol;
    }
    if (conta!=""){
    	collez[tipo][barcodeP][index]['conta']=conta;
    }
    
    collez[tipo][barcodeP][index]['list'] = [];
    collez[tipo][barcodeP][index]['list'].push(contaaliq);
    
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

function isNumber(n) { return /^-?[\d.]+(?:e-?\d+)?$/.test(n); }

function nuovo_caso(){
	var linea=$("#cellid").val();
	var sorgorig=$("#sorg").val();
	//solo se esiste gia' la linea nel DB delle annotazioni, altrimenti il caso che mi e' stato dato va bene
	if((linea!="-1")&&(sorgorig!="/")){
		$("#tess").val("/");
		var sorgattuale=$("#id_source option:selected").val();
		if (sorgorig==sorgattuale){
			var casoorig=$("#caso_iniz").val();
			$("#caso_fin").val(casoorig);
		}
		else{
			//se non ho gia' preso un nuovo caso
			//if(!nuov_cas){
				var tumore=$("#id_Tumor_Type option:selected").val();
				var cellid=$("#cellid").val();
				var casoorig=$("#caso_iniz").val();
				//devo vedere se e' casuale o no
				var numero="False";
				if (isNumber(parseInt(casoorig))){
					numero="True";
				}
				var url = base_url + "/api/cell/new_case/" + tumore+"/"+sorgattuale+"/"+cellid+"/"+numero+"/"+nuov_cas;
				var timer = setTimeout(function(){$("body").addClass("loading");},500);
				$.ajax({
					  url: url,
					  dataType: 'json',
					  async: true,
					  success: function(d) {
						  nuov_cas=false;
				    	  if(d.caso!=""){
				    		  if(d.nuovo==true){
				    			  $("#caso_nuovo").val(d.caso);
				    		  }
					    	  $("#caso_fin").val(d.caso);
				    	  }
				    	  clearTimeout(timer);
				    	  $("body").removeClass("loading");
					 }
				});
				/*$.getJSON(url,function(d){
			    	nuov_cas=false;
			    	if(d.caso!=""){
			    		if(d.nuovo==true){
			    			$("#caso_nuovo").val(d.caso);
			    		}
				    	$("#caso_fin").val(d.caso);
			    	}
			    });*/
			//}
			var casoorig=$("#caso_nuovo").val();
			$("#caso_fin").val(casoorig);
		}
	}
}

$(document).ready(function () {
	$("#id_date").datepicker({
		 dateFormat: 'yy-mm-dd',
	});
	$("#id_date").datepicker('setDate', new Date());
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
    	generate_result_table("Collection","aliquote_fin");
	}
	else{
		//per popolare la lista con dentro i wg
		var lisworkgr=$("#id_workgr");
		if(lisworkgr.length!=0){
			var liswg=workingGroups.split(",");
			for (var i=0;i<liswg.length;i++){
				$("#id_workgr").append("<option value="+liswg[i]+">"+liswg[i]+"</option>");
			}
		}
		inizializza();
	}
	
	$("#id_name").autocomplete({
		source:base_url+'/api/cell/autocomplete/'
	});
	
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
	
	$("#rna button").css("background-color","lightgrey");

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
	
	//codice per il caricamento dei due file
	$("#tastosheet").click(function(){
		$("#id_file_datasheet").click();
	});
	
	$("#id_file_datasheet").change(function(){
		var files = $('#id_file_datasheet')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filesheet").val(nomfile);
	});
	
	$("#tastoinvoice").click(function(){
		$("#id_file_invoice").click();
	});
	
	$("#id_file_invoice").change(function(){
		var files = $('#id_file_invoice')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#fileinvoice").val(nomfile);
	});
	
	$("#id_randomize").css("margin-top","0.6em");
	$("#id_randomize").css("margin-left","2.7em");
	//se c'e' il campo per il genid, vuol dire che ho fatto comparire anche il secondo form e quindi
	//devo disabilitare i campi del primo
	var genid=$("#gen_id");
	if (genid.length!=0){
		$("#form1 select,#form1 input").attr("disabled",true);
	}
	//per diminuire la dimensione degli input
	$("#form1 input,#form2 input").not(":#id_name").attr("size","10");
	$("#id_date").parent().after("<br style='clear:both;' />");
	$("#id_scong").parent().after("<br style='clear:both;' />");
	
	//per la tabella delle posizioni
	//tolgo la vecchia intestazione alle tabelle
	$("#tabpiastra table tr>th").text("");
	
	//disabilito tutti i pulsanti all'inizio
	$("#rna button").attr("disabled",true);
	
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
	
	$("#id_source").change(nuovo_caso);
	
	$("#barcode_rna").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			caricaPiastra();
		}
	});
	
	$("#conf_aliq").click(salva_aliq);
	
	$("#id_barc").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			salva_aliq();
		}
	});
	
	$("#conferma2").click(function(event){		
		//verifico la validita' della data
		var dd=$("#id_date").val().trim();
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			alert("Incorrect data format: it should be YYYY-MM-DD");
			event.preventDefault();
		}
	});
	
	//quando clicco sul pulsante submit
    $("#conferma_finale").click(function(event){
		event.preventDefault();
		if(!vuota()){
			var timer = setTimeout(function(){$("body").addClass("loading");},500);
			//per sapere se devo creare una nuova collezione, guardo il campo nascosto con id "tess", se e' compilato 
			//o se ha "/"
			var tess=$("#tess").val();
			if (tess=="/"){
				var crea=true;
			}
			else{
				var crea=false;
			}
			//comunico la struttura dati al server
			var data = {
					salva_nuova:true,
					dati:JSON.stringify(collez),
		    		operatore:$("#actual_username").val(),
		    		tum:$("#id_Tumor_Type option:selected").val(),
		    		itemcode:$("#caso_fin").val(),
		    		sorg:$("#id_source").val(),
		    		dat:$("#id_date").val(),
		    		linea:$("#nomlinea").val(),
		    		crea:crea,
		    		cellid:$("#cellid").val(),
		    		wg:$("#id_wgroup").val(),
		    };
			var url=base_url+"/line/save/";
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
});
