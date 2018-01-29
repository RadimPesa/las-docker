vett_used_barc=new Array();
var collezione = {};
var listacasi=new Array();
var contaaliq=1;
var regex=/^[0-9.]+$/;
var dizposti={};
//dizionario con chiave il consenso e valore il posto. Serve per fare in modo di non lasciare inserire
//lo stesso consenso per due posti diversi
var dizconsensi={};

function controllacampi(place,dd,paz,barc,vol,conta,tipoaliq,indice){
	
	if(place=="---------"){
		alert("Please select place");
		return false;
	}
	
	//controllo la data
	if (dd==""){
		var errore="Please insert date";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	else{
		//verifico la validità della data		
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			var errore="Incorrect data format"
			if (indice!=""){
				errore+=" in line "+indice;
			}
			errore+=": it should be YYYY-MM-DD";
			alert(errore);
			return false;
		}
	}
	
	//controllo il paziente
	if (paz==""){
		var errore="Please insert Funnel ID";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	
	//e' il barcode della provetta
	if(barc==""){
		var errore="Please insert tube barcode";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	else{
		//se c'e' uno spazio nella stringa
		if(barc.indexOf(" ") !== -1){
			var errore="There is a space in barcode. Please correct";
			if (indice!=""){
				errore+=" line "+indice;
			}
			alert(errore);
			return false;
		}
	}
		
	//controllo il volume
	if(vol==""){
		var errore="Please insert volume";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	if((!regex.test(vol))){
		var errore="You can only insert number. Please correct value for volume";
		if (indice!=""){
			errore+=" in line "+indice;
		}
		alert(errore);
		return false;
	}
	
	//se e' PBMC
	if(tipoaliq=="1"){
		//controllo la conta
		if(conta==""){
			var errore="Please insert count";
			if (indice!=""){
				errore+=" in line "+indice;
			}
			alert(errore);
			return false;
		}
		if((!regex.test(conta))){
			var errore="You can only insert number. Please correct value for count";
			if (indice!=""){
				errore+=" in line "+indice;
			}
			alert(errore);
			return false;
		}
	}	
	//verifico se ho gia' usato questo consenso con un altro posto e se si' do' errore
	if (paz in dizconsensi){
		var posto=dizconsensi[paz];
		if (posto!=place){
			var errore="Funnel ID already used for another place. Please correct";
			if (indice!=""){
				errore+=" in line "+indice;
			}
			alert(errore);
			return false;
		}
	}
	else{
		dizconsensi[paz]=place;
	}
	
	return true;
}

function save() {
	var place=$("#id_Place option:selected").text();
	var dd=$("#id_date").attr("value").trim();
	var paz=$("#id_patient").attr("value").trim();
	var barc=$("#id_barcode").attr("value").trim();
	var vol=$("#id_volume").attr("value").trim();	
	var conta=$("#id_count").attr("value").trim();
	var tipoaliq=$("#id_type option:selected").attr("value");
	if(controllacampi(place,dd,paz,barc,vol,conta,tipoaliq,"")){
		controlla_barc(barc,false,{});
	}
}

function controlla_barc(barc,file,dati){
	//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
	if (cerca_barc_duplicati(barc)==false){
		var lbarc="";
		var codice=barc.replace(/#/g,"%23");
		var url=base_url+"/api/check/barcode/";
		var dati = {
				lbarc:codice
	    };
		
		$.post(url, dati, function (result) {
			if (result.data!="ok"){
				alert("Error: barcode you entered already exists");				
			}
			else{
				addAliquot( barc,file,dati);
			}
		});
	}
	else{		
		alert("Error: barcode you entered has already been used in this session");
		return false;
	}
	return true;
}

function cerca_barc_duplicati(barc){
	var trovato=0;
	for (var i=0;i<vett_used_barc.length;i++){
		if (vett_used_barc[i]==barc){
			return true;
		}
	}
	return false;
}

//per inserire i campioni
function addAliquot( barcodeT,file,diz){
    vett_used_barc.push(barcodeT);
    if(file){
    	var sorg=diz["place"];
    	var dat=diz["data"];    	
    	var paz=diz["patient"];    	
    	var vol=diz["volume"];
    	var conta=diz["conta"];
    	var tipoaliq=diz["tipo"];
    	var tipoaliqnome=diz["tiponome"];
    }
    else{
	    var sorg=$("#id_Place option:selected").text();
	    var dat=$("#id_date").attr("value");
	    var paz=$("#id_patient").attr("value").trim();
	    var vol=$("#id_volume").attr("value").trim();
	    var conta=$("#id_count").attr("value").trim();
		var tipoaliq=$("#id_type option:selected").attr("value");
		var tipoaliqnome=$("#id_type option:selected").text();
    }
    //se e' PBMC
    if(tipoaliq=="1"){
    	var oTable = $("#aliquots_table").dataTable();
		oTable.fnSetColumnVis( 7, true );
		contacell=conta;
    }
    else{
    	contacell=null;
    }
        
    $("#aliquots_table").dataTable().fnAddData( [contaaliq, sorg, dat, paz,barcodeT,tipoaliqnome,vol,contacell,null] );
    if(file){
    	var sorgid=dizposti[sorg.toLowerCase()];
    }
    else{
    	var sorgid=$("#id_Place option:selected").attr("value");
    }
    
    //salvo nella struttura dati locale
    saveInLocal(sorgid, dat, paz, barcodeT, vol, contacell, tipoaliq);
    contaaliq++;
    
}

function saveInLocal(sorgid, dat, paz, barcodeT, vol, conta, tipoaliq){
	//in questo modo per ogni chiave devo creare un nuovo genid
    var chiave=paz+"|"+dat+"|"+sorgid;
	if (!(chiave in collezione)){
    	var lista=[];
    	//lista che al momento del salvataggio sul server serve a mantenere
    	//l'ordine di inserimento dei casi
    	listacasi.push(chiave);
    }
    else{
    	var lista=collezione[chiave];
    }
    var diz={};
	diz['barcode']=barcodeT;
	diz['vol']=vol;
	diz['conta']=conta;
	diz['tipo']=tipoaliq;
	lista.push(diz);
	collezione[chiave]=lista;
	$("#id_barcode").val("");
}


/**** CANCELLAZIONE ALIQUOTE INSERITE ****/

function deleteAliquot(barc){
	for (key in collezione){
		for (var i = 0; i < collezione[key].length; i++){
			if (collezione[key][i]['barcode'] == barc){
				//ho trovato l'oggetto della lista con quel barc
				removeNotPlateBarcode(barc);
				if (collezione[key].length == 1){                       	
                	delete collezione[key];
                	//tolgo il caso dalla lista
                	removeCase(key);
                	break;
                }
				else{
                	collezione[key].splice(i,1); 
                }				
			}
		}
	} 
}

function removeCase(key){
    for (var i=0; i < listacasi.length; i++){
        if (listacasi[i] == key){
        	listacasi.splice(i,1);
        }
    }
}

function removeNotPlateBarcode(barcode){
    for (var i=0; i < vett_used_barc.length; i++){
        if (vett_used_barc[i] == barcode){
        	vett_used_barc.splice(i,1);
        }
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

function loadElements(){
	var file=$("#id_file_cont").attr("value");
	if(file==""){
		alert("Please load a file");
	}
	else{
		var val=file.split(".");
		var estens=val[val.length-1];
		if ((estens=="xls")||(estens=="xlsx")){
			alert("Please change Excel file in a tab delimited one");
		}
		else{						
			var file = document.getElementById('id_file_cont').files[0];
			//lista di dizionari in cui ognuno rappresenta un campione con i suoi dati
			var lisdati=[];
			var r = new FileReader();
			r.readAsText(file);			
		    r.onload = function(e) {
			    var contents = e.target.result;
			    var lista=contents.split("\n");
		    	var stringbarc="";
		    	//quando leggo da file mi mette in fondo un /n, quindi per avere il numero effettivo
		    	//di righe devo fare lunghezza-1
		    	if(contents[contents.length-1]=="\n"){
		    		var lung=(lista.length)-1;		    		
		    	}
		    	else{
		    		var lung=lista.length;
		    	}
		        for(var i=1;i<lung;i++){
		        	var diztemp={};
		        	//devo fare un controllo sui campi. Se ci sono tutti e se sono formattati correttamente
		        	var lisval=lista[i].trim().split("\t");
		        	if (lisval.length>3){
		        		var tipo=lisval[3].trim();
			        	if((tipo[0]=="\"")&&(tipo[tipo.length-1])=="\""){
			        		tipo=tipo.substring(1,tipo.length-1);			        		
			        	}
			        	if (tipo.toLowerCase()=='pbmc'){
			        		if (lisval.length!=7){
			        			alert("File format error. 7 fields are required: please correct line "+String(i+1));
				        		return;
			        		}
			        		else{
			        			var conta=lisval[6].trim();
			        			if((conta[0]=="\"")&&(conta[conta.length-1])=="\""){
			        				conta=conta.substring(1,conta.length-1);			        		
			        			}
			        			var tipoaliq="1";
			        			var tiponome="PBMC";
			        		}
			        	}
			        	else if (tipo.toLowerCase()=='plasma'){
			        		if (lisval.length!=6){
			        			alert("File format error. 6 fields are required: please correct line "+String(i+1));
				        		return;
			        		}
			        		else{
			        			var conta="";
			        			var tipoaliq="0";
			        			var tiponome="Plasma";
			        		}
			        	}
			        	else{
			        		alert("Sample type you inserted does not exist. Please correct line "+String(i+1));
			        		return;
			        	}
		        	}
		        	else{
		        		alert("File format error. More fields are required: please correct line "+String(i+1));
		        		return;
		        		
		        	}
		        	//Place Date PatientCode Type TubeBarcode Volume Count
		        	var place=lisval[0].trim();
		        	if((place[0]=="\"")&&(place[place.length-1])=="\""){
		        		//vuol dire che il valore e' racchiuso tra virgolette
		        		place=place.substring(1,place.length-1);			        		
		        	}
		        	var dd=lisval[1].trim();
		        	if((dd[0]=="\"")&&(dd[dd.length-1])=="\""){
		        		dd=dd.substring(1,dd.length-1);			        		
		        	}
		        	var paz=lisval[2].trim();
		        	if((paz[0]=="\"")&&(paz[paz.length-1])=="\""){
		        		paz=paz.substring(1,paz.length-1);			        		
		        	}		        	
		        	var barc=lisval[4].trim();
		        	if((barc[0]=="\"")&&(barc[barc.length-1])=="\""){
		        		barc=barc.substring(1,barc.length-1);			        		
		        	}
		        	var vol=lisval[5].trim();
		        	if((vol[0]=="\"")&&(vol[vol.length-1])=="\""){
		        		vol=vol.substring(1,vol.length-1);			        		
		        	}
		        	diztemp["place"]=place;
		        	diztemp["data"]=dd;
		        	diztemp["patient"]=paz;
		        	diztemp["barcode"]=barc;
		        	diztemp["volume"]=vol;
		        	diztemp["conta"]=conta;
		        	diztemp["tipo"]=tipoaliq;
		        	diztemp["tiponome"]=tiponome;
		        	lisdati.push(diztemp);
		        	if(!controllacampi(place,dd,paz,barc,vol,conta,tipoaliq,String(i+1))){
		        		return;
		        	}
		        	//devo controllare il posto perchè qui e' scritto a mano mentre il controllo
		        	//normale avviene sul select
		        	if (!(place.toLowerCase() in dizposti)){
		        		alert("Place you inserted does not exist. Please correct line "+String(i+1));
		        		return;
		        	}
		        	stringbarc+=barc+"&";
		        	
		        }
		        //per togliere l'ultimo &
				var stringdef=stringbarc.substring(0,(stringbarc.length)-1);
				
				var url=base_url+"/api/check/barcode/";
				var dati = {
						lbarc:stringdef
			    };
				
				$.post(url, dati, function (result) {
					if (result.data!="ok"){
						alert(result.data);
					}
					else{
						//devo verificare che nel file non ci siano due barc uguali
						var listemp=[];
						for(var i=0;i<lisdati.length;i++){
							var barc=lisdati[i]["barcode"];
							//verifico che il nuovo barcode non sia tra quelli che ho gia' inserito
							if (cerca_barc_duplicati(barc)==false){							
								for (var j=0;j<listemp.length;j++){
									if (listemp[j]==barc){
										alert("Error: barcode you entered in line "+String(i+1)+" has already been used in this session");
										return;
									}
								}
								listemp.push(barc);
							}
							else{		
								alert("Error: barcode you entered in line "+String(i+1)+" has already been used in this session");
								return;
							}
						}
						for(var i=0;i<lisdati.length;i++){
				        	var barc=lisdati[i]["barcode"];
				        	addAliquot(barc,true,lisdati[i]);
						}					
					}
				});		    		   
		    }
		}
	}
}

function cambiaTipoAliquota (){
	var aliq=$("#id_type option:selected").attr("value");
	//se e' plasma
	if(aliq=="0"){
		$("#p_count").css("display","none");
	}
	//se e' PBMC
	if(aliq=="1"){
		$("#p_count").css("display","");
	}
}

$(document).ready(function () {
	
	var lplace=$("#id_Place option");
	for (var i=1;i<lplace.length;i++){
		dizposti[$(lplace[i]).text().toLowerCase()]=$(lplace[i]).val();
	}
	
	$("#tastofile").click(function(){
		$("#id_file_cont").click();
	});
	
	//per far comparire nell'input i nomi dei file caricati
	$("#id_file_cont").change(function(){
		var files = $('#id_file_cont')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+",";
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1);
		$("#filename").val(nomfile);
		$("#conferma").attr("disabled",false);
	});
	
	var tabfin=$("#aliq");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Collection","aliq");
	}
	
	$("#crea_camp").click(save);
	
	$("#carica_file").click(loadElements);
	
	$("#id_type").change(cambiaTipoAliquota);
	
	$("#id_barcode").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			save();
		}
	});
	
	$("#id_date").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	$("#id_date").datepicker('setDate', new Date());
	
	var oTable = $("#aliquots_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            
            { "sTitle": "ID Operation" },
            { "sTitle": "Place" },
            { "sTitle": "Date" },
            { "sTitle": "Funnel ID" },
            { "sTitle": "Barcode" },
            { "sTitle": "Type" },
            { "sTitle": "Volume (ml)" },
            { "sTitle": "Count (cell/ml)", 
            	"bVisible":false,
            	"sClass": "conta", 
            },
            { 
                "sTitle": null, 
                "sClass": "control_center", 
                "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
            },
        ],
	    "bAutoWidth": false ,
	    "aoColumnDefs": [
	        { "bSortable": false, "aTargets": [ 8 ] },
	    ],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
		
	/* Add event listener for deleting row  */
    $("#aliquots_table tbody td.control_center img").live("click", function () {
        var barc= $($($(this).parents('tr')[0]).children()[4]).text();
        deleteAliquot(barc);
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
    $("#confirm_all").click(function(event){
    	event.preventDefault();
    	if(!vuota()){
    		var timer = setTimeout(function(){$("body").addClass("loading");},500);
	    	$(this).attr("disabled",true);
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(collezione),
	    			liscasi:JSON.stringify(listacasi),
		    		operatore:$("#actual_username").val(),
		    };
			var url=base_url+"/funnel/collection/save/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	$("#form_fin").append("<input type='hidden' name='final' />");
		    	$("#form_fin").submit();
		    });
    	}
    	else{
    		alert("Please insert some samples");
    	}
	});

	//riduco le dimensioni del campo per il coll event e per il cod paziente
	$("#id_barcode,#id_patient").attr("size",10);
	//riduco le dimensioni dei campi
	$("#id_date").attr("size",8);
	$("#id_volume").attr("size",5)
});
