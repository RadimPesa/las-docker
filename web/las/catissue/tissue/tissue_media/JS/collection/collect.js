mappa=new Object();
vett_used_barc=new Array();
var tessuti,sezionigen;
var h,conta,load_rna,load_vital,load_snap;
//struttura dati che contiene la corrispondenza tra abbreviazione e nome esteso
//dei tessuti collezionabili
var x;
h=0;
conta=1;
load_rna=false;
load_snap=false;
load_vital=false;
var collezione = {'VT':{}, 'RL':{}, 'SF':{}, 'FF':{}, 'CH':{}, 'OF':{}, 'PL':{}, 'PX':{}, 'FR':{}, 'FS':{}};
var contaaliq=1;
var iniziogen="";
barcodeVT = ""; barcodeSF = ""; barcodeRL = "";
listKey = ['collect','collectuser', 'collecttimestamp', 'abbrtum', 'caso', 'coll_data', 'coll_ev','paz', 'ospedale','prot','tissueList','vett_used_barc','furth_info','workgr','reopen','tumid','aliqpres','cons_exists','localid','local_exists'];
var agreed = false;
var regex=/^[0-9.]+$/;
var controllo=true;
//dizionario in cui per ogni tipologia di aliquota inserita (cioe' il gen id fino al contatore), salvo il numero di aliquote
//gia' presenti nel DB della biobanca. Lo leggo quando devo creare il contatore per una nuova aliq 
var diz_aliq_presenti={};
//dizionario con chiave l'id del progetto e valore la lista dei local id gia' presenti per lui
var dizlocalid={};

function save() {
	var tipo,code;
	if (($("#barcode_rna").val() == "")&&(($(this).attr("id")).charAt(0))=="r")
		alert("Insert plate barcode in rna later");
	else if(($("#barcode_sf").val() == "")&&(($(this).attr("id")).charAt(0))=="s")
		alert("Insert plate barcode in snap frozen");
	else if(($("#barcode_vital").val() == "")&&(($(this).attr("id")).charAt(0))=="v")
		alert("Insert plate barcode in vital");
	else{
		//per identificare i tasti selezionati
		$(this).attr("sel","s");
		//salvo il valore attuale del pulsante
		var stringa=$(this).text();
		var num=parseInt(stringa);
		//incremento di 1
		num=num+1;
		//scrivo il nuovo numero nel pulsante
		$(this).text(num);
		//prendo l'id del tessuto selezionato
		var id_inp=$(tessuti[h]).attr("value");
		//id_inp="#"+id_inp;
		//prendo il colore della label(che e' il padre del check selezionato)
		var colore=$("#tissueNameList input[value='"+id_inp+"']").parent().css("color");
		//cambio il colore del tasto
		$(this).css("background-color",colore);
		var posto=$(this).attr("id");
		
		if(($(this).attr("id").charAt(0))=="r"){
			var tipo="RL";
			var code=$("#barcode_rna").val();
		}
		else if(($(this).attr("id").charAt(0))=="s"){
			var tipo="SF";
			var code=$("#barcode_sf").val();
		}
		else{
			var tipo="VT";
			var code=$("#barcode_vital").val();
		}
		var pos=$(this).attr("id").split("-")[1];
		var tissue=$("#tissueNameList input[value='"+id_inp+"']").parent().text().trim();
		var counter = contatore_genid(tipo, tissue, code, pos);
		
		if(reopencollection!="/"){
			var timer = setTimeout(function(){$("body").addClass("loading");},50);
			var tumore=$("#tumid").val();
			//chiamo la API che mi crea il gen. Reopen contiene il caso gia' con gli zeri			
			var url=base_url+"/api/ext/newgenid/"+tumore+"/"+reopencollection+"/"+id_inp+"/H0000000/None/"+tipo+"/"+counter+"/";
			var tasto=this;
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					//mi da' il contatore dell'aliquota come stringa
					var contatore=d.cont;
					diz_aliq_presenti[tissue+tipo]=d.presenti;
					localStorage.setItem('aliqpres', JSON.stringify(diz_aliq_presenti));
					save2(contatore,code,pos,tipo,tissue,tasto);
				}
				else{
					alert("Error");
					var num = parseInt($(tasto).text());
				    if(num > 1){
				        num = num - 1;
				        $(tasto).text(num);
				    }
				    else{
				        $(tasto).css("background-color","rgb(249,248,242)");
				        $(tasto).text(0);
				        $(tasto).removeAttr('sel');
				        $(tasto).attr("disabled", false );
				    }
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
			save2(counter,code,pos,tipo,tissue,this);
		}
	}
}

function save2(contatore,code,pos,tipo,tissue,obj){
	if (parseInt(contatore)<10){
		var countgen="0"+String(contatore);
	}
	else{
		countgen=contatore;
	}
	//creo il genid
	var gen=iniziogen+"H0000000000"+tipo+String(countgen)+"00";
	$(obj).attr("onmouseover","tooltip.show('"+gen+"')");
	$(obj).attr("onmouseout","tooltip.hide();");
	
	$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, code, pos, gen,null] );
	//salvo la nuova aliquota nella variabile locale e nel local storage
	//salvo nella struttura dati locale e lo salvo anche nel local_storage
    saveInLocal(tipo, tissue, pos, code, gen, contatore,"","");
    
	contaaliq++;
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

//per inserire nuovi blocchetti di ff o per le aliquote del sangue
function addAliquot(typeA, tissue, barcodeT){
	//USA IL COLORE PER LA SCRITTA DEL NUOVO GENID
    var id = "";
    var volume="";
    var conta="";
    if (typeA == 'FF'){
        id = '#f-output';
        $("#inputf0").val("");
    }
    else if (typeA == 'CH'){
        id = '#c-output';
        $("#inputc0").val("");
    }
    else if (typeA == 'OF'){
        id = '#o-output';
        $("#inputo0").val("");
    }
    else if (typeA == 'PL'){
        id = '#plasoutput';
        volume=$("#volplas").val();
        $("#barcplas").val("");
    }
    else if (typeA == 'SF'){
        id = '#whooutput';
        volume=$("#volwho").val();
        $("#barcwho").val("");
    }
    else if (typeA == 'PX'){
        id = '#paxoutput';
        volume=$("#volpax").val();
        $("#barcpax").val("");
    }
    else if (typeA == 'VT'){
        id = '#pbmcoutput';
        volume=$("#volpbmc").val();
        conta=$("#contapbmc").val();
        $("#barcpbmc").val("");
    }
    else if (typeA == 'FR'){
        id = '#urioutput';
        volume=$("#voluri").val();
        $("#barcuri").val("");
    }
    else if (typeA == 'FS'){
        id = '#sedimoutput';
        volume=$("#volsedim").val();
        $("#barcsedim").val("");
    }
    var pos = '-';
    barcodeT=barcodeT.trim();
    var counter = contatore_genid(typeA, tissue, barcodeT, pos);
    
    if(reopencollection!="/"){
    	var timer = setTimeout(function(){$("body").addClass("loading");},50);
		var tumore=$("#tumid").val();
		var id_tess = $(tessuti[h]).attr("value");
		//chiamo la API che mi crea il gen. Reopen contiene il caso gia' con gli zeri			
		var url=base_url+"/api/ext/newgenid/"+tumore+"/"+reopencollection+"/"+id_tess+"/H0000000/None/"+typeA+"/"+counter+"/";
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				//mi da' il contatore dell'aliquota come stringa
				var contatore=d.cont;
				diz_aliq_presenti[tissue+typeA]=d.presenti;
				localStorage.setItem('aliqpres', JSON.stringify(diz_aliq_presenti));
				addAliquot2(contatore,barcodeT,typeA,volume,conta,pos,tissue,id);
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
    	addAliquot2(counter,barcodeT,typeA,volume,conta,pos,tissue,id);
    }
}

function addAliquot2(contatore,barcodeT,typeA,volume,conta,pos,tissue,id){
	if (parseInt(contatore)<10){
		contatore="0"+String(contatore);
	}
	var gen=iniziogen+"H0000000000"+typeA+String(contatore)+"00";
    
    vett_used_barc.push(barcodeT);
    localStorage.setItem('vett_used_barc', vett_used_barc.toString());
    if ((typeA=="PL")||(typeA=="PX")||(typeA=="VT")||(typeA=="SF")||(typeA=="FR")||(typeA=="FS")){
    	var oTable = $('#aliquots_table').dataTable();
		oTable.fnSetColumnVis( 5, true );
    	var vol="Volume: "+volume.toString()+"ml";
    	if (conta!=""){
    		vol=vol+" Count: "+conta+"cell/ml";
    	}
		//var immagine='<img src="/tissue_media/img/admin/icon-unknown.gif" width="15px" height="15px" >';
    	$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, barcodeT, pos, gen,vol] );
    	
    }
    else{
    	$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, barcodeT, pos, gen,null] );
    }
    //salvo nella struttura dati locale e lo salvo anche nel local_storage
    saveInLocal(typeA, tissue, pos, barcodeT, gen, contatore,volume,conta);
    
    contaaliq++;
    var id_inp =$(tessuti[h]).attr("value");
    var color = $("#tissueNameList input[value='"+id_inp+"']").parent().css("color");
    
    $(id).text(gen);
    $(id).css('color', color);
}

function save_biocas(barc,tipo){
	//verifico se la stringa contiene degli spazi
	if (barc.indexOf(" ") == -1){
		var radio=$('input:radio[name="cho_'+tipo+'"]:checked').val();
		//se ho selezionato il caricamento di una provetta, come nella maggior parte dei casi
		if ((radio=="tube")||(radio==undefined)){
			//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
			if (cerca_barc_duplicati(barc)==false){
				
				var lbarc="";
				var codice=barc.replace(/#/g,"%23");
				var url=base_url+"/api/collect/singletube/"+codice+"/"+tipo+"/";
				$.getJSON(url,function(d){
					if(d.data=="err_esistente"){
						alert("Error. Barcode you entered already exists");
					}
					else if((d.data=="err_tipo")||(d.data=="errore_aliq")){
						alert("Error. Block isn't for "+tipo);
					}
					else{
                        var id = $(tessuti[h]).attr("value");
                        var tissue=$("#tissueNameList input[value='"+id+"']").parent().text().trim();
                        addAliquot(tipo, tissue, barc);
						//per identificare i tasti selezionati
						$("#confirm_all").attr("disabled",false);
					}
				});
			}
			else{
				alert("Error. You have already used this barcode in this session.");
			}
		}
		else if (radio=="plate"){
			carica_piastra_sangue(barc,tipo);
		}
	}
	else{
		alert("Error. There is a space in barcode");
	}
}

function carica_piastra_sangue(codice,tipo){
	var timer = setTimeout(function(){$("body").addClass("loading");},2000);
	//sto caricando una piastra per le urine
	if ((tipo=="FR")||(tipo=="FS")){
		var nameP="tabella3 table:first";
	}
	else{
		var nameP="tabella2 table:first";
	}

    $("#" + nameP + " button,#confirm_all").attr("disabled", false );

    var nom="cho_"+tipo;
    var radio=$('input:radio[name="'+nom+'"]:checked').val();
    var barr=codice.replace(/#/g,"%23");
    var url = base_url + "/api/generic/load/" + barr + "/" + tipo + "/" +radio;
    $.getJSON(url,function(d){
        if(d.data=="errore"){
			alert("Plate doesn't exist");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
		}
		else if(d.data=="errore_piastra"){
			alert("Plate aim is not working");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
			$("#" + nameP + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="errore_aliq"){
			var val=$("#"+nameP+" th").text().toLowerCase();
			alert("Plate selected is not "+val+" ");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
			$("#" + nameP + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="errore_store"){
			alert("Error while connecting with storage");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
			$("#" + nameP + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="err_tipo"){
			alert("Error. Block isn't for "+typeP);
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
			$("#" + nameP + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="err_esistente"){
			alert("Error. Barcode you entered already exists");
			$("#" + nameP + " button,#confirm_all").attr("disabled", true );
			$("#" + nameP + " button").css("background-color","#F9F8F2");
		}
		else{
	        $("#" + nameP ).replaceWith(d.data);
	        if((tipo=="FR")||(tipo=="FS")){
	        	//faccio apparire il barcode nel campo sotto la piastra per le urine
	        	$("#barcode_uri_plate").val(codice);
	        	var selected = $("#tabs").tabs( "option", "selected" );
	        	var selectedTabTitle = $($("#tabs li")[selected]).text();
	        	$("#urine th").text(selectedTabTitle);
	        }
	        else{
	        	//faccio apparire il barcode nel campo sotto la piastra per il sangue
	        	$("#barcode_blood_plate").val(codice);
	        }
	        $("#" + nameP + " button").css("background-color","rgb(249,248,242)");
	        $("#" + nameP + " button").click(salva_sangue);
	        
	        //mi occupo dei posti gia' selezionati in precedenza, nel caso questo sia un 
	        //ricaricamento della stessa piastra
	        var nome=tipo[0].toLowerCase();
	        if (tipo=="PL"){
	        	nome='l';
	        }
	        else if(tipo=="PX"){
	        	nome="x";
	        }
	        else if(tipo=="FR"){
	        	nome="f";
	        }
	        else if(tipo=="FS"){
	        	nome="e";
	        }
	        sangue=true;
	        piastra_ricaricata(tipo,nome,codice,sangue);
	        
		}
        clearTimeout(timer);
    	$("body").removeClass("loading");
    });
    $("body").removeClass("loading");
}

function salva_sangue() {
	var volume="";
	var conta="";
	
	if(($(this).attr("id").charAt(0))=="v"){
		var tipo="VT";
		var code=$("#barcpbmc").val();
		volume=$("#volpbmc").val();
        conta=$("#contapbmc").val();
	}
	else if(($(this).attr("id").charAt(0))=="s"){
		var tipo="SF";
		var code=$("#barcwho").val();
		volume=$("#volwho").val();
	}
	else if(($(this).attr("id").charAt(0))=="l"){
		var tipo="PL";
		var code=$("#barcplas").val();
		volume=$("#volplas").val();
	}
	else if(($(this).attr("id").charAt(0))=="x"){
		var tipo="PX";
		var code=$("#barcpax").val();
		volume=$("#volpax").val();
	}
	else if(($(this).attr("id").charAt(0))=="f"){
		var tipo="FR";
		var code=$("#barcuri").val();
		volume=$("#voluri").val();
	}
	else if(($(this).attr("id").charAt(0))=="e"){
		var tipo="FS";
		var code=$("#barcsedim").val();
		volume=$("#volsedim").val();
	}
	
	if((!regex.test(volume))||((!regex.test(conta))&&(conta!=""))){
		alert("You can only insert number. Please correct.");
	}
	else{
		//per identificare i tasti selezionati
		$(this).attr("sel","s");

		//scrivo il nuovo numero nel pulsante
		$(this).text("1");
		//prendo l'id del tessuto selezionato
		var id_inp=$(tessuti[h]).attr("value");
		//prendo il colore della label(che e' il padre del check selezionato)
		var colore=$("#tissueNameList input[value='"+id_inp+"']").parent().css("color");
		//cambio il colore del tasto
		$(this).css("background-color",colore);
		var posto=$(this).attr("id");
		//lo disabilito perche' non si possa mettere piu' niente li' dentro
		$(this).attr("disabled",true);
		
		var pos=$(this).attr("id").split("-")[1];
		var tissue=$("#tissueNameList input[value='"+id_inp+"']").parent().text().trim();
		var counter = contatore_genid(tipo, tissue, code, pos);
		
		if(reopencollection!="/"){
			var timer = setTimeout(function(){$("body").addClass("loading");},50);
			var tumore=$("#tumid").val();
			//chiamo la API che mi crea il gen. Reopen contiene il caso gia' con gli zeri			
			var url=base_url+"/api/ext/newgenid/"+tumore+"/"+reopencollection+"/"+id_inp+"/H0000000/None/"+tipo+"/"+counter+"/";
			var tasto=this;
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					//mi da' il contatore dell'aliquota come stringa
					var contatore=d.cont;
					diz_aliq_presenti[tissue+tipo]=d.presenti;
					localStorage.setItem('aliqpres', JSON.stringify(diz_aliq_presenti));
					salva_sangue2(contatore,volume,conta,code,pos,tipo,tissue,tasto);
				}
				else{
					alert("Error");
					var num = parseInt($(tasto).text());
				    if(num > 1){
				        num = num - 1;
				        $(tasto).text(num);
				    }
				    else{
				        $(tasto).css("background-color","rgb(249,248,242)");
				        $(tasto).text(0);
				        $(tasto).removeAttr('sel');
				        $(tasto).attr("disabled", false );
				    }
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
			salva_sangue2(counter,volume,conta,code,pos,tipo,tissue,this);
		}
	}
}

function salva_sangue2(contatore,volume,conta,code,pos,tipo,tissue,obj){
	if (parseInt(contatore)<10){
		var countgen="0"+String(contatore);
	}
	else{
		var countgen=contatore;
	}
	//creo il genid
	var gen=iniziogen+"H0000000000"+tipo+String(countgen)+"00";
	$(obj).attr("onmouseover","tooltip.show('"+gen+"')");
	$(obj).attr("onmouseout","tooltip.hide();");
	
	var oTable = $('#aliquots_table').dataTable();
	oTable.fnSetColumnVis( 5, true );
	var vol="Volume: "+volume.toString()+"ml";
	if (conta!=""){
		vol=vol+" Count: "+conta+"cell/ml";
	}
	oTable.fnAddData( [null, contaaliq, code, pos, gen,vol] );
	
	//salvo la nuova aliquota nella variabile locale e nel local storage
	//salvo nella struttura dati locale e lo salvo anche nel local_storage
    saveInLocal(tipo, tissue, pos, code, gen, contatore,volume,conta);
    
	contaaliq++;
}

function save_ffpe() {
	var inputid="#inputf0";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		var barc=$(inputid).val();
		save_biocas(barc,"FF");
	}
}

function save_oct() {
	var inputid="#inputo0";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		var barc=$(inputid).val();
		save_biocas(barc,"OF");
	}
}

function save_cb() {
	var inputid="#inputc0";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		var barc=$(inputid).val();
		save_biocas(barc,"CH");
	}
}

function save_plasma() {
	var inputid="#barcplas";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		if($("#volplas").val()==""){
			alert("Insert volume");
		}
		else{
			var numero=$("#volplas").val();
			if((!regex.test(numero))){
				alert("You can only insert number. Please correct volume");
			}
			else{
				//devo vedere se e' stato scelto di caricare una piastra o una provetta
				var radio=$('input:radio[name="cho_PL"]:checked');
				if (radio.length==0){
					alert("Choose if you want to load a tube or a plate");
				}
				else{
					var barc=$(inputid).val();
					save_biocas(barc,"PL");
				}
			}
		}
	}
}

function save_whole() {
	var inputid="#barcwho";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		if($("#volwho").val()==""){
			alert("Insert volume");
		}
		else{
			var numero=$("#volwho").val();
			if((!regex.test(numero))){
				alert("You can only insert number. Please correct volume");
			}
			else{
				//devo vedere se e' stato scelto di caricare una piastra o una provetta
				var radio=$('input:radio[name="cho_SF"]:checked');
				if (radio.length==0){
					alert("Choose if you want to load a tube or a plate");
				}
				else{
					var barc=$(inputid).val();
					save_biocas(barc,"SF");
				}
			}
		}
	}
}

function save_pax() {
	var inputid="#barcpax";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		if($("#volpax").val()==""){
			alert("Insert volume");
		}
		else{
			var numero=$("#volpax").val();
			if((!regex.test(numero))){
				alert("You can only insert number. Please correct volume");
			}
			else{
				//devo vedere se e' stato scelto di caricare una piastra o una provetta
				var radio=$('input:radio[name="cho_PX"]:checked');
				if (radio.length==0){
					alert("Choose if you want to load a tube or a plate");
				}
				else{
					var barc=$(inputid).val();
					save_biocas(barc,"PX");
				}
			}
		}
	}
}

function save_pbmc() {
	var inputid="#barcpbmc";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		if($("#volpbmc").val()==""){
			alert("Insert volume");
		}
		else{
			//if($("#contapbmc").val()==""){
			//	alert("Insert count");
			//}
			//else{
				var vol=$("#volpbmc").val();
				var conta=$("#contapbmc").val();
                                if((!regex.test(vol))||((!regex.test(conta))&&(conta!=""))){
					alert("You can only insert number. Please correct.");
				}
				else{
					//devo vedere se e' stato scelto di caricare una piastra o una provetta
					var radio=$('input:radio[name="cho_VT"]:checked');
					if (radio.length==0){
						alert("Choose if you want to load a tube or a plate");
					}
					else{
						var barc=$(inputid).val();
						save_biocas(barc,"VT");
					}
				}
		//	}
		}
	}
}

function save_uri() {
	var inputid="#barcuri";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		if($("#voluri").val()==""){
			alert("Insert volume");
		}
		else{
			var numero=$("#voluri").val();
			if((!regex.test(numero))){
				alert("You can only insert number. Please correct volume");
			}
			else{
				//devo vedere se e' stato scelto di caricare una piastra o una provetta
				var radio=$('input:radio[name="cho_FR"]:checked');
				if (radio.length==0){
					alert("Choose if you want to load a tube or a plate");
				}
				else{
					var barc=$(inputid).val();
					save_biocas(barc,"FR");
				}
			}
		}
	}
}

function save_sedim() {
	var inputid="#barcsedim";
	if($(inputid).val()=="")
		alert("Insert barcode");
	else{
		if($("#volsedim").val()==""){
			alert("Insert volume");
		}
		else{
			var numero=$("#volsedim").val();
			if((!regex.test(numero))){
				alert("You can only insert number. Please correct volume");
			}
			else{
				//devo vedere se e' stato scelto di caricare una piastra o una provetta
				var radio=$('input:radio[name="cho_FS"]:checked');
				if (radio.length==0){
					alert("Choose if you want to load a tube or a plate");
				}
				else{
					var barc=$(inputid).val();
					save_biocas(barc,"FS");
				}
			}
		}
	}
}

function conferma_tutto(){
	var id=$(tessuti[h]).attr("value");
	//disabilito il vecchio checkbox
	$("#tissueNameList input[value='"+id+"']").removeAttr("checked");
	//modifico lo stile del vecchio checkbox
	$("#tissueNameList input[value='"+id+"']").parent().css("border-style","none");
	h=h+1;
	if(h==tessuti.length){
		$("#sf button,#rna button,#vital button,#f-0,#o-0,#c-0,input").attr("disabled", true );
		$("input[name=\"csrfmiddlewaretoken\"]").removeAttr("disabled");
		$("#confirm").attr("disabled",false);

		$("#titolo").text("Finished");
	}
	else{
		//$("#sf button,#rna button,#vital button,#ffpe button").attr("disabled", true );
		//disabilito i tasti con delle aliquote gia' dentro
		$("#sf button[sel=\"s\"],#rna button[sel=\"s\"],#vital button[sel=\"s\"]").attr("disabled", true );
		var id=$(tessuti[h]).attr("value");
		//abilito quel checkbox
		$("#tissueNameList input[value='"+id+"']").attr("checked","checked");
		//modifico lo stile del checkbox abilitato
		$("#tissueNameList input[value='"+id+"']").parent().css("border-style","solid");
		//modifico la scritta per il tipo di tessuto collezionato
		var testo=$("#tissueNameList input[value='"+id+"']").parent().text();
		var n;
		url=base_url+"/api/tissue/";

		testo=testo[1]+testo[2];
		for(i=0;i<x.data.length;i++){
			if(x.data[i].abbreviation==testo){
				n=x.data[i].longName;
				break;
			}
		}
		//intervengo sui tab
		if(n=="Blood"){
			$("#tabs").tabs("enable",1);			
			$("#tabs").tabs("select",1);
			$("#tabs").tabs({ disabled: [2,3,4] });
		}
		else if (n=="Urine"){
			var listab=$("#tabs-3").children();
			//se il tab 3 e' vuoto
			if (listab.length==0){
				var listab4=$("#tabs-4").children();
				if (listab4.length!=0){
					$("#tabs-3").append($("#tabs-4").children());
				}
				else{
					var listab5=$("#tabs-5").children();
					if (listab5.length!=0){
						$("#tabs-3").append($("#tabs-5").children());
					}
				}
			}			
			$("#tabs").tabs("enable",2);			
			$("#tabs-4,#tabs-5").children().remove();
			$("#tabs").tabs("select",2);
			$("#tabs").tabs({ disabled: [1,3,4] });
		}
		else if (n=="Ascitic Fluid"){
			var listab=$("#tabs-4").children();
			//se il tab 4 e' vuoto
			if (listab.length==0){
				var listab3=$("#tabs-3").children();
				if (listab3.length!=0){
					$("#tabs-4").append($("#tabs-3").children());
				}
				else{
					var listab5=$("#tabs-5").children();
					if (listab5.length!=0){
						$("#tabs-4").append($("#tabs-5").children());
					}
				}
			}			
			$("#tabs").tabs("enable",3);
			$("#tabs-3,#tabs-5").children().remove();			
			$("#tabs").tabs("select",3);
			$("#tabs").tabs({ disabled: [1,2,4] });
		}
		else if (n=="Liquor"){
			var listab=$("#tabs-5").children();
			//se il tab 5 e' vuoto
			if (listab.length==0){
				var listab3=$("#tabs-3").children();
				if (listab3.length!=0){
					$("#tabs-5").append($("#tabs-3").children());
				}
				else{
					var listab4=$("#tabs-4").children();
					if (listab4.length!=0){
						$("#tabs-5").append($("#tabs-4").children());
					}
				}
			}			
			$("#tabs").tabs("enable",4);
			$("#tabs-3,#tabs-4").children().remove();
			$("#tabs").tabs("select",4);
			$("#tabs").tabs({ disabled: [1,2,3] });
		}
		else{
			$("#tabs").tabs("select",0);
			$("#tabs").tabs({ disabled: [1,2,3,4] });
		}
		
		var selected = $("#tabs").tabs( "option", "selected" );
    	var selectedTabTitle = $($("#tabs li")[selected]).text();
    	//la tabella assume id pari ad "urine" solo quando e' caricata, quindi se non c'e' una piastra caricata,
    	//non viene toccato niente
    	$("#urine th").text(selectedTabTitle);				
		
		$("#titolo").text("You are collecting "+n);
			
		//mi occupo del genealogy ID
		var tessuto=$("#tissueNameList input[value='"+id+"']").parent().text();
		//tolgo lo spazio iniziale che mi mette l'html
		tessuto=tessuto[1]+tessuto[2];
		var tumore=$("#tum").val();
		var caso=$("#caso").val();
		iniziogen=tumore+caso+tessuto;
		$("#gen_id").val(iniziogen);		
	}
}

function carica_piastra(){
	var e=0;
	if(($(this).attr("id"))=="load_rna_plate"){
		if ($("#barcode_rna").val() == "")
			alert("Insert plate barcode in rna later");
		else{
			//devo vedere se e' stato scelto di caricare una piastra o una provetta
			var radio=$('input:radio[name="choose_rna"]:checked');
			if (radio.length==0){
				alert("Choose if you want to load a tube or a plate");
			}
			else{
				load_rna=true;
				barcodeRL = $("#barcode_rna").val();
				carica_provetta("RL", "rna");
			}
		}
	}
	else if (($(this).attr("id"))=="load_sf_plate"){
		if ($("#barcode_sf").val() == "")
			alert("Insert plate barcode in snap frozen");
		else{
			//devo vedere se e' stato scelto di caricare una piastra o una provetta
			var radio=$('input:radio[name="choose_sf"]:checked');
			if (radio.length==0){
				alert("Choose if you want to load a tube or a plate");
			}
			else{
				load_snap=true;
				barcodeSF = $("#barcode_sf").val();
				carica_provetta("SF", "sf");
			}
		}
	}
	else if (($(this).attr("id"))=="load_vital_plate"){
		if ($("#barcode_vital").val() == "")
			alert("Insert plate barcode in vital");
		else{	
			//devo vedere se e' stato scelto di caricare una piastra o una provetta
			var radio=$('input:radio[name="choose_vital"]:checked');
			if (radio.length==0){
				alert("Choose if you want to load a tube or a plate");
			}
			else{
				load_vital=true;
				barcodeVT = $("#barcode_vital").val();
				carica_provetta("VT", "vital");
			}
		}
	}
}

function carica_piastra_vitale(){
	if ($("#barcode_vital").val() == "")
		alert("Insert plate barcode in vital");
	else{
		//devo vedere se e' stato scelto di caricare una piastra o una provetta
		var radio=$('input:radio[name="choose_vital"]:checked');
		if (radio.length==0){
			alert("Choose if you want to load a tube or a plate");
		}
		else{
		load_vital=true;
		barcodeVT = $("#barcode_vital").val();
		carica_provetta("VT", "vital");
		}
	}
}

function carica_piastra_rna(){
	if ($("#barcode_rna").val() == "")
		alert("Insert plate barcode in rna later");
	else{
		//devo vedere se e' stato scelto di caricare una piastra o una provetta
		var radio=$('input:radio[name="choose_rna"]:checked');
		if (radio.length==0){
			alert("Choose if you want to load a tube or a plate");
		}
		else{
			load_rna=true;
			barcodeRL = $("#barcode_rna").val();
			carica_provetta("RL", "rna");
		}
	}
}

function carica_piastra_snap(){
	if ($("#barcode_sf").val() == "")
		alert("Insert plate barcode in snap frozen");
	else{
		//devo vedere se e' stato scelto di caricare una piastra o una provetta
		var radio=$('input:radio[name="choose_sf"]:checked');
		if (radio.length==0){
			alert("Choose if you want to load a tube or a plate");
		}
		else{
			load_snap=true;
			barcodeSF = $("#barcode_sf").val();
			carica_provetta("SF", "sf");
		}
	}
}

//funzione utilizzata per parametrizzare l'inserimento delle varie provette nella rispettiva piastra
function carica_provetta(typeP, nameP){
	var timer = setTimeout(function(){$("body").addClass("loading");},2000);
	var tabella="tabs-1 table[id='"+nameP+"']";
	//$("#" + nameP + " button").css("background-color","rgb(249,248,242)");
    $("#" + tabella + " button,#confirm_all").attr("disabled", false );
    //$("#" + nameP + " button").text("0");
    codice = $("#barcode_" + nameP).val();
    var nom="choose_"+nameP;
    var radio=$('input:radio[name="'+nom+'"]:checked').val();
    var barr=codice.replace(/#/g,"%23");
    var url = base_url + "/api/generic/load/" + barr + "/" + typeP + "/" +radio;
    $.getJSON(url,function(d){
        if(d.data=="errore"){
			alert("Plate doesn't exist");
			$("#" + tabella + " button,#confirm_all").attr("disabled", true );
			$("#" + tabella + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="errore_piastra"){
			alert("Plate aim is not working");
			$("#" + tabella + " button,#confirm_all").attr("disabled", true );
			$("#" + tabella + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="errore_aliq"){
			var val=$("#"+tabella+" th").text().toLowerCase();
			alert("Plate selected is not for "+val+" ");
			$("#" + tabella + " button,#confirm_all").attr("disabled", true );
			$("#" + tabella + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="errore_store"){
			alert("Error while connecting with storage");
			$("#" + tabella + " button,#confirm_all").attr("disabled", true );
			$("#" + tabella + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="err_tipo"){
			alert("Error. Block isn't for "+typeP);
			$("#" + tabella + " button,#confirm_all").attr("disabled", true );
			$("#" + tabella + " button").css("background-color","#F9F8F2");
		}
		else if(d.data=="err_esistente"){
			alert("Error. Barcode you entered already exists");
			$("#" + tabella + " button,#confirm_all").attr("disabled", true );
			$("#" + tabella + " button").css("background-color","#F9F8F2");
		}
		else{
	        $("#" + tabella ).replaceWith(d.data);
	        $("#" + tabella + " button").css("background-color","rgb(249,248,242)");
	        $("#" + tabella + " button").click(save);
	        $("#load_" + nameP + "_plate").attr("load", "1");
	        $("#"+nameP+"_confirm").attr("disabled",false);
	        
	        //mi occupo dei posti gia' selezionati in precedenza, nel caso questo sia un 
	        //ricaricamento della stessa piastra
	        sangue=false
	        piastra_ricaricata(typeP,nameP,codice,sangue);
	        
		}
        clearTimeout(timer);
    	$("body").removeClass("loading");
    });
    $("body").removeClass("loading");
}

//carica le eventuali modifiche fatte in questa sessione alla piastra che si sta caricando
function piastra_ricaricata(typeP, nameP, barcodeP,sangue){
    for (barcode in collezione[typeP]){
        if (barcode == barcodeP){
            for (var i = 0; i < collezione[typeP][barcode].length; i++){
                var pos = collezione[typeP][barcode][i]['pos'];
                var qty = collezione[typeP][barcode][i]['qty'];
                var tissue = collezione[typeP][barcode][i]['tissueType'];
                var genID = collezione[typeP][barcode][i]['genID'];
                //devo vedere se e' un'aliquota del sangue o no
                if(sangue){
                	if ((typeP=="FR")||(typeP=="FS")){
                		var id_tube = "#tabella3 table:first button[id='"+nameP[0]+"-"+pos+"']";
                	}
                	else{
                		var id_tube = "#tabella2 table:first button[id='"+nameP[0]+"-"+pos+"']";
                	}
                }
                else{
                	var id_tube = "#" + nameP[0] + "-" + pos;
                }
                $(id_tube).text(qty);

                $(id_tube).attr('sel', 's');
                
                $(id_tube).attr("onmouseover","tooltip.show('"+genID+"')");
        		$(id_tube).attr("onmouseout","tooltip.hide();");
        		
                for (var j = 0; j < $("#tissueNameList ul label").length; j++){
                    var label = $("#tissueNameList ul label")[j];
                    if ( $.trim( $(label).text() ) == tissue ){
                        var color = $(label).css("color");
                        $(id_tube).css("background-color",color);
                    }
                }
            }
        }
    }
    $("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s'],#tabella2 table:first button[sel='s'],#tabella3 table:first button[sel='s']").attr("disabled", true );
    $("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s'],#tabella2 table:first button[sel='s'],#tabella3 table:first button[sel='s'],#sf button:contains('X'),#rna button:contains('X'),#vital button:contains('X'),#tabella2 table:first button:contains('X'),#tabella3 table:first button:contains('X')").css("color","GrayText");
}

function suggerimento(nome){
	nome=nome.trim();
	for(i=0;i<x.data.length;i++){
		if(x.data[i].abbreviation==nome){
			n=x.data[i].longName;
			break;
		}
	}
	tooltip.show(n);	
}

function contatore_genid(typeA,tissue, barcodeP, pos){
    var counter = 1;
    //guardo quante aliq sono gia' presenti nel DB e questo e' salvato nel diz. Se non c'e' ancora la
    //chiave inizializzo a zero la variabile
    if(tissue+typeA in diz_aliq_presenti){
    	var aliq_presenti=diz_aliq_presenti[tissue+typeA];
    }
    else{
    	var aliq_presenti=0;
    }
    if (Object.size(collezione[typeA]) > 0){
    	var check = checkForMissingCounter(typeA, tissue, barcodeP, pos);
        for (key in collezione[typeA]){
            //key e' il codice della piastra           
            for (var i = 0; i < collezione[typeA][key].length; i++) {
            	//entra qui solo se clicco due volte sulla stessa posizione: Quindi non devo incrementare il contatore, ma
            	//prendere quello che c'e' gia'
            	if (key == barcodeP){
	                if (collezione[typeA][key][i]['pos'] == pos){
	                    return parseInt(collezione[typeA][key][i]['counter'])-aliq_presenti;
	                }	  
            	}
            	//normalmente entra qui e mi fa salire il contatore nel caso inserisca piu' campioni con le stesse caratteristiche
                if (tissue == collezione[typeA][key][i]['tissueType']){
                    counter++;
                }
            } 
            
        } 
    }
    console.log ("counter:",counter);
    console.log ("check:",check);
    //se il contatore che guarda i buchi vuoti nella serie di campioni uguali inseriti e' >0, allora uso lui
    if ((check > 0)&&(check<=counter))
        return check;
    return counter;
}

//serve a trovare il primo contatore libero, quindi in caso di cancellazioni nella schermata riesce a coprire i buchi
//lasciati dall'eliminazione dei campioni
function checkForMissingCounter( typeA, tissue, barcodeP, pos){
    var found = false;
    //guardo quante aliq sono gia' presenti nel DB e questo e' salvato nel diz. Se non c'e' ancora la
    //chiave inizializzo a zero la variabile
    if(tissue+typeA in diz_aliq_presenti){
    	var aliq_presenti=diz_aliq_presenti[tissue+typeA];
    }
    else{
    	var aliq_presenti=0;
    }
    for (var i = aliq_presenti+1; i <= contaaliq+aliq_presenti; i++) {
        found = false;
        for (key in collezione[typeA]){           
            for (var j = 0; j < collezione[typeA][key].length; j++) {
                if ((parseInt(collezione[typeA][key][j]['counter']) == i)&&(collezione[typeA][key][j]['tissueType']==tissue)){
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

function saveInLocal(tipo, tissue, pos, barcodeP, newG, counter,volume,conta){
    var index = 0;
    if (collezione[tipo][barcodeP]){
        var found = false;
        for (var i = 0; i < collezione[tipo][barcodeP].length; i++) {
            if (pos == collezione[tipo][barcodeP][i]['pos']){
            	collezione[tipo][barcodeP][i]['qty']++;
            	collezione[tipo][barcodeP][i]['list'].push(contaaliq);
                found = true;
            }
        }
        if (found == true){
        	console.log("trovato");
            storageIt('collect', JSON.stringify(collezione));
        	return;
        }else{
            index = (collezione[tipo][barcodeP]).length;
        }
    }else{
        collezione[tipo][barcodeP] = [];
    }
    console.log(parseInt(counter));
    collezione[tipo][barcodeP][index] = {}
    collezione[tipo][barcodeP][index]['qty'] = 1;
    collezione[tipo][barcodeP][index]['genID'] = newG;
    collezione[tipo][barcodeP][index]['pos'] = pos;
    collezione[tipo][barcodeP][index]['tissueType'] = tissue;
    collezione[tipo][barcodeP][index]['counter'] = parseInt(counter);
    if (volume!=""){
    	collezione[tipo][barcodeP][index]['volume']=volume;
    	if (conta!=""){
    		collezione[tipo][barcodeP][index]['cellcount']=conta;
    	}
    	localStorage.setItem("furth_info", true);
    }
    collezione[tipo][barcodeP][index]['list'] = [];
    collezione[tipo][barcodeP][index]['list'].push(contaaliq);
    
    console.log(collezione);
    storageIt('collect', JSON.stringify(collezione));    
    localStorage.setItem('aliqpres', JSON.stringify(diz_aliq_presenti));
}

////LOCAL STORAGE FUNCTIONS
function storageIt(key, value){
    localStorage.setItem(key, value);
    localStorage.setItem(key + 'timestamp', new Date().getTime());
    localStorage.setItem(key + 'user', $("#actual_username").val());
}

/**** CANCELLAZIONE ALIQUOTE INSERITE ****/

function deleteAliquot(genID,idoperaz){
    var pos = ""; 
    var sang=false;
    console.log(genID);
    for (typeA in collezione){
        for (barcode in collezione[typeA]){
            for (var i = 0; i < collezione[typeA][barcode].length; i++){
                if (collezione[typeA][barcode][i]['genID'] == genID){
                    console.log('trovato genid');
                    pos = collezione[typeA][barcode][i]['pos'];
                    if (collezione[typeA][barcode][i]['qty'] == 1){
                    	//devo vedere se e' un'aliquota del sangue o no
                        if((collezione[typeA][barcode][i]['volume'])!=undefined){
                        	sang=true;
                        }
                    	//vedo se ci sono altri campioni che afferiscono a quella piastra
                        if (collezione[typeA][barcode].length == 1){                       	
                        	delete collezione[typeA][barcode];
                        }else{
                        	collezione[typeA][barcode].splice(i,1); 
                        }                       
                    }else{
                    	collezione[typeA][barcode][i]['qty']--;
                    	//cancello anche gli id dell'operazione nella lista 
                    	var lista=collezione[typeA][barcode][i]['list'];
                    	for (var j=0;j<lista.length;j++){
                    		if (lista[j]==idoperaz){
                    			lista.splice(j,1);
                    			break;
                    		}
                    	}
                    	collezione[typeA][barcode][i]['list']=lista;
                    }
                    
                    deleteInPlate(typeA, barcode, pos, genID,sang);
                    storageIt('collect', JSON.stringify(collezione));
                    console.log(collezione);
                    return;
                }
            }
        }
    }
}

function deleteInPlate(typeA, barcode, pos, genID,sang){
	if (typeA == 'VT'){
    	if (sang==true){
    		removeNotPlateBarcode(barcode);
    		if (genID == $("#pbmcoutput").text()){
                $("#pbmcoutput").text("Deleted");
    		}
    		var barcpias=$("#barcode_blood_plate").val();
            if (barcpias==barcode){
            	canc("tabella2 table:first button[id='v-" + pos+"']");
            }
    	}
    	else{
	        if (barcodeVT == barcode){
	        	canc("tabs-1 table[id='vital'] button[id='v-"+pos+"']");
	        }
    	}
    }else if (typeA == 'RL'){
        if (barcodeRL == barcode){
            canc('r-' + pos);
        }    
    }else if (typeA == 'SF'){
    	if (sang){
    		removeNotPlateBarcode(barcode);
    		if (genID == $("#whooutput").text()){
                $("#whooutput").text("Deleted");
    		}
    		var barcpias=$("#barcode_blood_plate").val();
            if (barcpias==barcode){
            	canc("tabella2 table:first button[id='s-" + pos+"']");
            }
    	}
    	else{
	        if (barcodeSF == barcode){   	
	        	canc("tabs-1 table[id='sf'] button[id='s-"+pos+"']");
	        }
    	}
    }else if (typeA == 'FF'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#f-output").text())
            $("#f-output").text("Deleted");
    }else if (typeA == 'OF'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#o-output").text())
            $("#o-output").text("Deleted");
    }else if (typeA == 'CH'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#c-output").text())
            $("#c-output").text("Deleted");
    }else if (typeA == 'PL'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#plasoutput").text())
            $("#plasoutput").text("Deleted");
        var barcpias=$("#barcode_blood_plate").val();
        if (barcpias==barcode){
        	canc('l-' + pos);
        }
    }else if (typeA == 'PX'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#paxoutput").text())
            $("#paxoutput").text("Deleted");
        var barcpias=$("#barcode_blood_plate").val();
        if (barcpias==barcode){
        	canc('x-' + pos);
        }
    }
    else if (typeA == 'FR'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#urioutput").text())
            $("#urioutput").text("Deleted");
        var barcpias=$("#barcode_uri_plate").val();
        if (barcpias==barcode){
        	canc('f-' + pos);
        }
    }
    else if (typeA == 'FS'){
        removeNotPlateBarcode(barcode);
        if (genID == $("#sedimoutput").text())
            $("#sedimoutput").text("Deleted");
        var barcpias=$("#barcode_uri_plate").val();
        if (barcpias==barcode){
        	canc('e-' + pos);
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
    localStorage.setItem('vett_used_barc', vett_used_barc.toString());
}

function checkStorage(){
    if (localStorage.getItem("collect")){
        //console.log('user');
    	var urlvoluta=base_url+"/collection/save/";

    	if (window.location.pathname!=urlvoluta){
    		window.location=base_url+"/collection/save/";
    	}
        var username = localStorage.getItem('collectuser');
        var timestamp = localStorage.getItem('collecttimestamp');
        var d = new Date(timestamp*1);
        var datacompleta=d.getDate()+"/"+(d.getMonth()+1)+"/"+d.getFullYear()+" at "+d.toLocaleTimeString()
        jQuery("#dialogMessage").text("Something bad happened, but we saved data (actions made by "+username+" on "+datacompleta+"). What do you want to do?");
        jQuery( "#dialog" ).dialog({
            resizable: false,
            height:200,
            width:340,
            modal: true,
            closeText:"gggg",
            draggable :false,
            buttons: {
                "Restore Old Data": function() {
                    restoreData();
                    agreed = true; 
                    jQuery( this ).dialog( "close" );
                },
                "Delete Old Data": function() {
                    clearStorage();
                    agreed = true; 
                    jQuery( this ).dialog( "close" );
                }
            },
            beforeclose : function() { return agreed; },
        });
    }
}

function restoreData(){
    collezione = JSON.parse(localStorage.getItem("collect"));
    console.log(collezione);
    //rimette le righe nella tabella riassuntiva
    for (typeA in collezione){
        for (barcode in collezione[typeA]){
            for (var i = 0; i < collezione[typeA][barcode].length; i++){
                var pos = collezione[typeA][barcode][i]['pos']
                var genID = collezione[typeA][barcode][i]['genID']
                for (var j = 0; j < collezione[typeA][barcode][i]['list'].length; j++){
                    var tempCounter = collezione[typeA][barcode][i]['list'][j]
                    if (tempCounter >= contaaliq)
                    	contaaliq = tempCounter + 1;
                    //devo vedere se e' un'aliquota del sangue o no
                    if(collezione[typeA][barcode][i]['volume']){
                    	var oTable = $('#aliquots_table').dataTable();
        				oTable.fnSetColumnVis( 5, true );
        				var volume=collezione[typeA][barcode][i]['volume'];
        				var vol="Volume: "+volume.toString()+"ml";
        		    	if (collezione[typeA][barcode][i]['cellcount']){
        		    		var conta=collezione[typeA][barcode][i]['cellcount']
        		    		vol=vol+" Count: "+conta;
        		    	}
                    	//var immagine='<img src="/tissue_media/img/admin/icon-unknown.gif" width="15px" height="15px" >';
                    	$("#aliquots_table").dataTable().fnAddData( [null, tempCounter, barcode, pos, genID,vol ] );
                    }
                    else{
                    	$("#aliquots_table").dataTable().fnAddData( [null, tempCounter, barcode, pos, genID,null ] );
                    }
                    
                }
            }
        }
    }

    var listatess=localStorage.getItem('tissueList');
    //ho una lista separata da virgola con i val dei tess
    var lis=listatess.split(",");
    for (var j=0;j<lis.length;j++){
    	$("#formtessnascosto").append("<input type='hidden' value='"+lis[j]+"' id=tissue name='tissueH' >");
    }
    var tumo=localStorage.getItem('abbrtum');
    $("#tum").val(tumo);
    var cas=localStorage.getItem('caso');
    $("#caso").val(cas);
    var osped=localStorage.getItem('ospedale');
    $("#posto").val(osped);
    var datacoll=localStorage.getItem('coll_data');
    $("#coll_data").val(datacoll);
    var coll_ev=localStorage.getItem('coll_ev');
    $("#coll_ev").val(coll_ev);
    var pazie=localStorage.getItem('paz');
    $("#paziente").val(pazie);
    var prot=localStorage.getItem('prot');
    $("#prot_study").val(prot);
    var wg=localStorage.getItem('workgr');
    $("#wg_pag2").val(wg);
    var reop=localStorage.getItem('reopen');
    $("#reopen").val(reop);
    reopencollection=reop;
    var tumorid=localStorage.getItem('tumid');
    $("#tumid").val(tumorid);
    var consexists=localStorage.getItem('cons_exists');
    $("#ic_exists").val(consexists);
    var local=localStorage.getItem('localid');
    $("#local_id").val(local);
    var localexists=localStorage.getItem('local_exists');
    $("#local_exists").val(localexists);
    diz_aliq_presenti= JSON.parse(localStorage.getItem("aliqpres"));
    
    $(".t p > label[for=\"id_tissue_0\"]").after("<br>");
	
	//serve per eliminare le selezioni dei tessuti da asportare
	$(".t input:checked").removeAttr("checked");	
	//serve per disabilitare il checkbox dei tessuti
	$(".t input").attr("disabled","disabled");
	
	//serve per nascondere tutti i tessuti con le loro label e checkbox
	$(".t input").hide();
   	$(".t label").hide();
   	$(".t li").hide();
    
    //serve per far ricomparire solo i tessuti selezionati da asportare durante questa collezione
    var selectedTissue = 1;
    if (document.hiddenTissuesForm.tissueH.length!=undefined){
	    selectedTissue = document.hiddenTissuesForm.tissueH.length;
	    for (i=0; i < selectedTissue; i++)
	    {
	    	for (var j=0; j < document.tissueNameList.tissue.length; j++){
	    		if( document.tissueNameList.tissue[j].value == document.hiddenTissuesForm.tissueH[i].value ){
	            	var idT = 'id_tissue_'+j
                	$("label[for='"+idT+"']").parent().show();
                    $("label[for='"+idT+"']").show();
                    $("#id_tissue_"+j).show();
	            }
	        }
	    }
    }
    else{
    	var idT = $("#tissue").val();
	    var n = idT[idT.length-1];
	    $("#tissueNameList input[value='"+idT+"']").parent().parent().show();
	    $("#tissueNameList input[value='"+idT+"']").parent().show();
	    $("#tissueNameList input[value='"+idT+"']").show();
    }
   	
    $(".t p label[for=id_tissue_0]").show();
    
    //per il tooltip
    tessuti=$(".s input[type=\"hidden\"]");
	url=base_url+"/api/tissue/";
	$.getJSON(url,function(d){
		x=d;
		//modifico la scritta per il tipo di tessuto collezionato
		var id=$(tessuti[0]).attr("value");
		var testo=$("#tissueNameList input[value='"+id+"']").parent().text();
		var n;
		var url=base_url+"/api/tissue/";
		testo=testo[1]+testo[2];
		for(i=0;i<x.data.length;i++){
			if(x.data[i].abbreviation==testo){
				n=x.data[i].longName;
				break;
			}
		}
		
		//intervengo sui tab
		if(n=="Blood"){
			$("#tabs").tabs("enable",1);
			$("#tabs").tabs({ disabled: [2,3,4] });
			$("#tabs").tabs("select",1);
		}
		else if (n=="Urine"){
			$("#tabs").tabs("enable",2);
			$("#tabs").tabs({ disabled: [1,3,4] });
			var listab=$("#tabs-3").children();
			//se il tab 3 e' vuoto
			if (listab.length==0){
				var listab4=$("#tabs-4").children();
				if (listab4.length!=0){
					$("#tabs-3").append($("#tabs-4").children());
				}
				else{
					var listab5=$("#tabs-5").children();
					if (listab5.length!=0){
						$("#tabs-3").append($("#tabs-5").children());
					}
				}
			}		
			$("#tabs-4,#tabs-5").children().remove();			
			$("#tabs").tabs("select",2);
		}
		else if (n=="Ascitic Fluid"){
			$("#tabs").tabs("enable",3);
			$("#tabs").tabs({ disabled: [1,2,4] });
			var listab=$("#tabs-4").children();
			//se il tab 4 e' vuoto
			if (listab.length==0){
				var listab3=$("#tabs-3").children();
				if (listab3.length!=0){
					$("#tabs-4").append($("#tabs-3").children());
				}
				else{
					var listab5=$("#tabs-5").children();
					if (listab5.length!=0){
						$("#tabs-4").append($("#tabs-5").children());
					}
				}
			}		
			$("#tabs-3,#tabs-5").children().remove();			
			$("#tabs").tabs("select",3);
		}
		else if (n=="Liquor"){
			$("#tabs").tabs("enable",4);
			$("#tabs").tabs({ disabled: [1,2,3] });
			var listab=$("#tabs-5").children();
			//se il tab 5 e' vuoto
			if (listab.length==0){
				var listab3=$("#tabs-3").children();
				if (listab3.length!=0){
					$("#tabs-5").append($("#tabs-3").children());
				}
				else{
					var listab4=$("#tabs-4").children();
					if (listab4.length!=0){
						$("#tabs-5").append($("#tabs-4").children());
					}
				}
			}		
			$("#tabs-3,#tabs-4").children().remove();
			$("#tabs").tabs("select",4);
		}
		else{
			$("#tabs").tabs({ disabled: [1,2,3,4] });
		}
		
		$("#titolo").text("You are collecting "+n);
	});	
	
	$("ul>li>label").attr("onmouseover","suggerimento($(this).text())");
	$("ul>li>label").attr("onmouseout","tooltip.hide();");
	
	//prendo il valore del campo hidden che contiene l'id del checkbox da abilitare
	var id=$("#tissue").val();
	var select="#tissueNameList input[value='"+id+"']";
	//abilito quel checkbox
	$(select).attr("checked","checked");
	//modifico lo stile del checkbox abilitato
	$(select).parent().css("border-style","solid");
	
	//mi occupo del genealogy ID
	var tessuto=$(select).parent().text();
	//tolgo lo spazio iniziale che mi mette l'html
	tessuto=tessuto[1]+tessuto[2];
	var tumore=$("#tum").val();
	var caso=$("#caso").val();
	iniziogen=tumore+caso+tessuto;
	$("#gen_id").val(iniziogen);
	
    var stringArray = localStorage.getItem('vett_used_barc');
    //entra qui solo se esiste almeno un elemento da inserire nella lista
    if (stringArray){ 
        var splitted = stringArray.split(',');
        for (var i=0; i < stringArray.split(',').length; i++){
        	vett_used_barc.push(splitted[i]);
        }
    }
    
    $("#confirm").removeAttr('disabled');
    
    //devo vedere se l'utente aveva inserito dei clinical feature
    var diz=JSON.parse(localStorage.getItem('clinicalfeat'));
    if (diz != undefined){
    	var data={
    			dati:JSON.stringify(diz),
    			salva:true
    	};
    	var url=base_url+"/collection/param/";
    	$.post(url, data, function (result) {
        	if (result == "failure") {
        		alert("Error");
        	}
        });
    	/*var data={};
    	for(key in diz){
    		data[key]=diz[key];
    	}
    	var url=base_url+"/collection/param/";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    });*/
    }
}

function clearStorage(){
    for (var i = 0; i < listKey.length; i++){
        localStorage.removeItem(listKey[i]);
    }
    localStorage.removeItem("clinicalfeat");
    window.location.href = base_url + "/collection/";
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

function isInteger(x) {
    return x % 1 === 0;
}

function verifica_coll_event(){
	var coll=$("#id_barcode").val();
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
        $("#id_barcode").val(coll);
        
		var ospe=$("#id_Place option:selected").val();
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
					/*if (eve=="duplic"){
						alert("Informed consent already present. Please change it.");
					}
					else{ 
						if((eve!="")){
							jQuery("#dialogMess").html("Patient code already present. It is suggested to use \""+eve+"\" for informed consent field. Do you agree? <br /> (If you choose \"No\", informed consent you wrote will be maintained)");
					        jQuery("#dia").dialog({
					            resizable: false,
					            height:200,
					            width:450,
					            modal: true,
					            draggable :false,
					            buttons: {
					                "Yes": function() {
					                	$("#id_barcode").val(eve);
					                    jQuery( this ).dialog( "close" );
					                    $("#primo_form").submit();
					                },
					                "No": function() { 
					                    jQuery( this ).dialog( "close" );
					                    $("#primo_form").submit();
					                }
					            },
					        });
						}
						else{
							if (coll!="None"){							
								$("#primo_form").submit();
							}
						}
					}*/
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

function sottometti_form_prima_pag(){
	var tess=$(".t ul>li input:checked");
	if(tess.length==0){
		alert("Please select at least a tissue to collect");
	}
	else{
		$("#id_Tumor_Type,#id_Place,#id_barcode,#id_patient,#id_protocol,#id_randomize,#id_workgr").attr("disabled",false);
		$("#primo_form").submit();
	}
}

//dato il nome di un parametro presente nella URL, restituisce il suo valore
function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) 
        {
            return sParameterName[1];
        }
    }
    return null;
}

//dato un protocollo selezionato dall'utente, carica dal modulo clinico
//tutti i posti collegati a quel progetto
function carica_ospedali(){
	var prot=$("#id_protocol option:selected").val();
	var url=base_url+"/api/getHospital/"+prot+"/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			$("#id_Place option").not(":first").remove();
			for(var i=d.data.length;i>0;i--){
				var stringa="<option value="+d.data[i-1][0]+">"+d.data[i-1][1]+"</option>"
				$("#id_Place option[value=\"\"]").after(stringa);
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
	
	var tabfin=$("#aliq");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Collection","aliq");
	}
	//se ho piu' tessuti selezionati mi da una stringa separata da spazio
	var tesssplit=$("input[name=tissue]:checked").parent().text().trim().split(" ");	
	var abbrtess=tesssplit[0];
	//intervengo sui tab
	if(abbrtess=="BL"){
		$("#tabs").tabs("enable",1);
		$("#tabs").tabs({ disabled: [2,3,4] });
		//cancello comunque gli altri tab in modo da averne sempre uno solo
		$("#tabs-4,#tabs-5").children().remove();
		$("#tabs").tabs("select",1);
	}
	else if (abbrtess=="UR"){
		$("#tabs").tabs("enable",2);
		$("#tabs-4,#tabs-5").children().remove();
		$("#tabs").tabs({ disabled: [1,3,4] });
		$("#tabs").tabs("select",2);		
	}
	else if (abbrtess=="AF"){
		$("#tabs").tabs("enable",3);
		$("#tabs-3,#tabs-5").children().remove();
		$("#tabs").tabs({ disabled: [1,2,4] });
		$("#tabs").tabs("select",3);		
	}
	else if (abbrtess=="LQ"){
		$("#tabs").tabs("enable",4);
		$("#tabs-3,#tabs-4").children().remove();
		$("#tabs").tabs({ disabled: [1,2,3] });
		$("#tabs").tabs("select",4);		
	}
	else{
		//cancello comunque gli altri tab in modo da averne sempre uno solo
		$("#tabs-4,#tabs-5").children().remove();
		$("#tabs").tabs("select",0);
		$("#tabs").tabs({ disabled: [1,2,3,4] });
	}
	
	//per popolare la lista con dentro i wg
	var lisworkgr=$("#id_workgr");
	if(lisworkgr.length!=0){
		var liswg=workingGroups.split(",");
		for (var i=0;i<liswg.length;i++){
			$("#id_workgr").append("<option value="+liswg[i]+">"+liswg[i]+"</option>");
		}
	}
	
	$("#tabs").tabs();
	$(".ui-tabs-panel").css("padding","0");
	tessuti=$(".s input[type=\"hidden\"]");
	$("#sf button,#rna button,#vital button").click(save);

	//$("#ffpe_plate").click(nuova_piastra);
	$("#load_rna_plate,#load_sf_plate,#load_vital_plate").click(carica_piastra);
	//per abilitare tutti i tasti dell'ffpe
	$("#f-0").attr("disabled", false );
	$("#f-0").click(save_ffpe);
	$("#o-0").click(save_oct);
	$("#c-0").click(save_cb);
	$("#plas").click(save_plasma);
	$("#who").click(save_whole);
	$("#pax").click(save_pax);
	$("#pbmc").click(save_pbmc);
	$("#uri").click(save_uri);
	$("#sedim").click(save_sedim);
	$("#confirm_all").click(conferma_tutto);

	//per abilitare tutti i pulsanti all'inizio
	$("input").attr("disabled", false );
	$("#sf button,#rna button,#vital button").attr("disabled", true );
	$("#sf button,#rna button,#vital button").css("background-color","lightgrey");
	$("#confirm_all,#confirm").attr("disabled",true);
	
	//per togliere l'intestazione alla tabella del secondo tab, quello per il sangue e anche alla terza
	$("#tabella2 table tr:first,#tabella3 table tr:first").remove();
	//per cambiare l'id della tabella
	$("#tabella2 table:first").attr("id","pias_blood");
	$("#tabella3 table:first").attr("id","pias_uri");
	
	var oTable = $("#aliquots_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
               //"sDefaultContent": '<img src="/tissue_media/img/x.png" width="16px" height="16px" >'
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
	
	checkStorage();
	
	//metto i controlli sui barcode in modo che quando l'utente preme invio parta il
	//caricamento della piastra
	$("#barcode_vital").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_piastra_vitale();
		}
	});
	
	$("#barcode_rna").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_piastra_rna();
		}
	});
	
	$("#barcode_sf").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			carica_piastra_snap();
		}
	});
	
	$("#inputf0").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_ffpe();
		}
	});
	
	$("#inputo0").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_oct();
		}
	});
	
	$("#inputc0").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_cb();
		}
	});
	
	$("#barcplas").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_plasma();
		}
	});
	
	$("#barcwho").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_whole();
		}
	});
	
	$("#barcpax").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_pax();
		}
	});
	
	$("#barcpbmc").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_pbmc();
		}
	});
	
	$("#barcuri").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_uri();
		}
	});
	
	$("#barcsedim").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save_sedim();
		}
	});
	
	$("ul>li>label").attr("onmouseover","suggerimento($(this).text())");
	$("ul>li>label").attr("onmouseout","tooltip.hide();");
	
	//per il tooltip
	url=base_url+"/api/tissue/";
	$.getJSON(url,function(d){
		x=d;
		//modifico la scritta per il tipo di tessuto collezionato
		var id=$(tessuti[0]).attr("value");
		var testo=$("#tissueNameList input[value='"+id+"']").parent().text().trim();
		var n;
		var url=base_url+"/api/tissue/";
		
		for(var i=0;i<x.data.length;i++){
			if(x.data[i].abbreviation==testo){
				n=x.data[i].longName;
				break;
			}
		}		
		
		$("#titolo").text("You are collecting "+n);
	});	
	
	//guardo se sono nella seconda pagina, quella con tutte le piastre
	var tum_input=$("#tum");
	if (tum_input.length!=0){
		if (!(localStorage.getItem("collect"))){
			var temp = [];
		    tessuti = $(".s input[type='hidden']");
		    for (var i = 0; i < tessuti.length; i++){
		        temp.push($(tessuti[i]).attr('value'));
		    }
		    localStorage.setItem('tissueList', temp.toString());
		    localStorage.setItem('abbrtum', $("#tum").val());
		    localStorage.setItem('caso', $("#caso").val());
		    localStorage.setItem('ospedale', $("#posto").val());
		    localStorage.setItem('coll_data', $("#coll_data").val());
		    localStorage.setItem('coll_ev', $("#coll_ev").val());
		    localStorage.setItem('paz', $("#paziente").val());
		    localStorage.setItem('prot', $("#prot_study").val());
		    localStorage.setItem('workgr', $("#wg_pag2").val());
		    localStorage.setItem('reopen', $("#reopen").val());
		    localStorage.setItem('tumid', $("#tumid").val());		    
		    localStorage.setItem('cons_exists', $("#ic_exists").val());
		    localStorage.setItem('localid', $("#local_id").val());
		    localStorage.setItem('local_exists', $("#local_exists").val());
		    
		    $(".t p > label[for=\"id_tissue_0\"]").after("<br>");
			
			//serve per eliminare le selezioni dei tessuti da asportare
			$(".t input:checked").removeAttr("checked");	
			//serve per disabilitare il checkbox dei tessuti
			$(".t input").attr("disabled","disabled");
			
			//serve per nascondere tutti i tessuti con le loro label e checkbox
			$(".t input").hide();
	       	$(".t label").hide();
	       	$(".t li").hide();
		    
			//serve per far ricomparire solo i tessuti selezionati da asportare durante questa collezione
		    var selectedTissue = 1;
		    if (document.hiddenTissuesForm.tissueH.length!=undefined){
			    selectedTissue = document.hiddenTissuesForm.tissueH.length;		
			    for (i=0; i < selectedTissue; i++)
			    {			    	
			    	for (var j=0; j < document.tissueNameList.tissue.length; j++){		
			    		if( document.tissueNameList.tissue[j].value == document.hiddenTissuesForm.tissueH[i].value ){
			            	var idT = 'id_tissue_'+j
		                	$("label[for='"+idT+"']").parent().show();
		                    $("label[for='"+idT+"']").show();
		                    $("#id_tissue_"+j).show();
			            }
			        }
			    }
		    }
		    else{
			    var idT = $("#tissue").val();
			    var n = idT[idT.length-1];
			    $("#tissueNameList input[value='"+idT+"']").parent().parent().show();
			    $("#tissueNameList input[value='"+idT+"']").parent().show();
			    $("#tissueNameList input[value='"+idT+"']").show();			    
		    }
	       	
		    $(".t p label[for=id_tissue_0]").show();
    	}
		
		reopencollection=$("#reopen").val();
		//prendo il valore del campo hidden che contiene l'id del checkbox da abilitare
		var id=$("#tissue").val();
		var select="#tissueNameList input[value='"+id+"']";
		//abilito quel checkbox
		$(select).attr("checked","checked");
		//modifico lo stile del checkbox abilitato
		$(select).parent().css("border-style","solid");
		
		//mi occupo del genealogy ID
		var tessuto=$(select).parent().text().trim();
		var tumore=$("#tum").val();
		var caso=$("#caso").val();
		iniziogen=tumore+caso+tessuto;
		$("#gen_id").val(iniziogen);
		
		/* Add event listener for deleting row  */
	    $("#aliquots_table tbody td.control_center img").live("click", function () {
	        var genID = $($($(this).parents('tr')[0]).children()[4]).text();
	        var operaz = $($($(this).parents('tr')[0]).children()[1]).text();
	        deleteAliquot(genID,operaz);
	        var nTr = $(this).parents('tr')[0];
	        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
	    } );
		/*$(document).on("click","#aliquots_table tbody td.control_center img", function () {
	        var genID = $($($(this).parents('tr')[0]).children()[4]).text();
	        var operaz = $($($(this).parents('tr')[0]).children()[1]).text();
	        deleteAliquot(genID,operaz);
	        var nTr = $(this).parents('tr')[0];
	        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
	    } );*/
	    
	    //quando clicco sul pulsante submit
	    $("#confirm").click(function(event){
	    	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	    	event.preventDefault();
	    	$(this).attr("disabled",true);
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(collezione),
		    		operatore:$("#actual_username").val(),
		    		tum:$("#tum").val(),
		    		itemcode:$("#caso").val(),
		    		ospedale:$("#posto").val(),
		    		dat:$("#coll_data").val(),
		    		collectevent:$("#coll_ev").val(),
		    		paziente:$("#paziente").val(),
		    		protoc:$("#prot_study").val(),
		    		wg:$("#wg_pag2").val(),
		    		cons_exists:$("#ic_exists").val(),
		    		local_id:$("#local_id").val(),
		    		local_exists:$("#local_exists").val(),
		    };
			var url=base_url+"/collection/save/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	$("#form_fin").append("<input type='hidden' name='final' />");
		    	$("#form_fin").submit();
		    });
		});	   
	}
	//se sono nella prima pagina
	else{
		//riduco le dimensioni del campo per il coll event e per il cod paziente
		$("#id_barcode,#id_patient").attr("size",10);
		//riduco le dimensioni del campo data
		$("#id_date").attr("size",8);
		
		$("#id_date").datepicker({
			 dateFormat: 'yy-mm-dd'
		});
		$("#id_date").datepicker('setDate', new Date());
		
		$("#id_randomize").css("margin-top","0.6em");
		$("#id_randomize").css("margin-left","2.7em");
		//metto nel select dei posti la solita riga vuota iniziale
		var stringa="<option value=''>---------</option>"
		$("#id_Place").append(stringa);
		
		$("#verifica_coll").attr("disabled",true);
		
		$("#param").click(apri_pagina_parametri);
		//scatta quando viene scelto un protocollo e carica dal modulo clinico i posti
		//collegati a quel protocollo
		$("#id_protocol").change(carica_ospedali);
		//$("#verifica_coll").click(verifica_coll_event);
		
		//se nel form mancano dei dati
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
		
		//se sono arrivato a questa pagina perche' ho riaperto una collezione devo precompilare i campi del form
		//con i dati che prendo dai parametri della url
		var reopen=getUrlParameter("reopen");
		//se sono nella schermata di riapertura della collezione
		if (reopen=="Yes"){
			var tumore=getUrlParameter("tumor");
			$("#id_Tumor_Type option[value="+tumore+"]").attr("selected","selected");			
			var prot=getUrlParameter("prot");
			$("#id_protocol option[value="+prot+"]").attr("selected","selected");
			var url=base_url+"/api/getHospital/"+prot+"/";
			//una volta che ho il protocollo, prendo tutti i centri collegati e li visualizzo nel select.
			//Dopo seleziono quello relativo alla collezione in questione.
			$.getJSON(url,function(d){
				if(d.data!="errore"){
					$("#id_Place option").not(":first").remove();
					for(var i=d.data.length;i>0;i--){
						var stringa="<option value="+d.data[i-1][0]+">"+d.data[i-1][1]+"</option>"
						$("#id_Place option[value=\"\"]").after(stringa);						
					}
					var ospedale=getUrlParameter("source");
					$("#id_Place option[value="+ospedale+"]").attr("selected","selected");
				}
				else{
					alert("Select tumor type");
				}
			});
						
			var cons=getUrlParameter("cons");
			$("#id_barcode").val(cons);
			var paz=getUrlParameter("pat");
			$("#id_patient").val(paz);			
			var caso=getUrlParameter("case");
			$("#caso_reopen").val(caso);
			$("#id_Tumor_Type,#id_Place,#id_barcode,#id_patient,#id_protocol,#id_randomize,#id_workgr,#param").attr("disabled",true);
		}
		
		$("#conferma").click(function(event){
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
				//se sono nella schermata di riapertura della collezione
				if (reopen=="Yes"){
					sottometti_form_prima_pag();
				}
				else{
					verifica_coll_event();
				}
			}
		});
	}
});

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

