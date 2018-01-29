aliquote_inserite=new Array();
valori_campioni=[];

function cancella(riga){
	
	var tab=$("#aliquote").dataTable();
	var righe=tab.$("tr");
    var genealogy=$(righe[(riga.rowIndex)-1]).children(":nth-child(2)").text();
    //cancello il campione dalla lista finale prendendo il suo indice all'interno della lista
    var indice=$.inArray(genealogy,aliquote_inserite);
    if(indice!=-1){
    	aliquote_inserite.splice(indice,1);
    }
    //cancello il campione anche dalla lista con tutti i dati
    for (var j=0;j<valori_campioni.length;j++){
    	var valore=valori_campioni[j];
    	var val=valore.split("|");
    	//il gen e' il primo valore
    	var gen=val[0];
    	if(gen==genealogy){
    		valori_campioni.splice(j,1);
    		break;
    	}
    }
    //se la lista e' vuota allora riabilito i campi
    if(aliquote_inserite.length==0){
    	$("#id_executor,#id_date,#id_dest").attr("disabled",false);
    }
    //cancello la riga dal data table
    tab.fnDeleteRow( riga );
    if (document.getElementById('aliquote').rows.length > 1){
    	var lista=tab.$("tr").children(":first-child");
    	for (var j=0;j<lista.length;j++){
    		//$(lista[j]).text(j+1);
    		tab.fnUpdate(j+1,j,0);
    	}
    }
}

function inizializza(){
	var tab=$("#aliquote").dataTable();
	var righe=tab.$("tr");
	if(righe.length>0){
		$("#conferma,#next").attr("disabled",false);
	}
	var nascondi=true;
	for(var i=0;i<righe.length;i++){
		var gen=$(righe[i]).children(":nth-child(2)").text();
		var barc=$(righe[i]).children(":nth-child(3)").text();
		var pos=$(righe[i]).children(":nth-child(4)").text();
		if(pos!=""){
			nascondi=false;
		}
		var stringa=gen+"|"+barc+"|"+pos;
		valori_campioni.push(stringa);
		aliquote_inserite.push(gen);
	}
	if(nascondi){
		tab.fnSetColumnVis( 3, false );
	}
}

function aggiungi_aliquota(){
  if($('#id_executor option:selected').val() =='None'){
            alert('Insert a valid executor');
            return;
    }

    if($('#id_dest option:selected').val() ==''){
        alert('Insert a valid receiver');
        return;
    }

	//sono le righe della tabella dove sono visualizzate le aliquote
	var tab=$("#aliquote").dataTable();
	var righe=tab.$("tr");
	//genealogy ID dell'aliquota da rivalutare
	gen=$("#id_aliquot").attr("value");
	var r=(righe.length);
	if(gen==""){
		alert("Insert a valid genealogy ID");
	}
	else{
        $.ajaxSetup({
            beforeSend: function (request){
                request.setRequestHeader("workingGroups", WG);
            }
        });

		var codice=gen.replace(/#/g,"%23");
		url=base_url+"/api/transfer/aliquot/"+codice;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if(d.data=="inesistente"){
					alert("Aliquot doesn't exist in storage");
				}
				else if(d.data=="presente"){
					alert("Aliquot is already scheduled for transferring");
				}
				else{
					var trovato=0;
					//in d.data ho una lista con genid|barcode|posizione
					var lisvalori=d.data;
					//confronto i genid che ci sono gia' nella lista generale con quello
					//nuovo e se c'e' gia' non lo inserisco nella tabella
					for (var j=0;j<lisvalori.length;j++){		
						trovato=0;
						var val=lisvalori[j].split("|");
						var gen=val[0];
						var barc=val[1];
						var pos=val[2];
						//funzione che restituisce la posizione di un valore in una lista. Se il valore non c'è, allora restituisce -1
						if($.inArray(gen,aliquote_inserite)==-1){
							aliquote_inserite.push(gen);
							valori_campioni.push(lisvalori[j]);
							tab.fnAddData( [aliquote_inserite.length, gen, barc, pos, null] );
							if(pos!=''){
								tab.fnSetColumnVis( 3, true );
							}
						}
						$("#id_aliquot").val("");
						$("#id_aliquot").focus();
						//disabilito la possibilita' di assegnare a qualcuno
						$("#id_executor,#id_date,#id_dest").attr("disabled",true);
						
						$("#conferma,#next").attr("disabled",false);
					}
				}			
			}
		});		
	}
}

//serve a capire se la tabella con le aliq pianificate e' vuota
//o meno
function vuota(){
	var listarighe=$("#aliquote tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#aliquote tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
}

function cancella_utenti(){
	var idattuale=$("#actual_username").attr("cod");
	var lista=$("#id_executor option,#id_dest option");
	for (var i=0;i<lista.length;i++){
		var idutente=$(lista[i]).val();
		if(idutente!=idattuale){
			$(lista[i]).remove();
		}
	}
	
}

function assegna_valori(){
	//do' il nuovo valore al campo risultato
	var esec=$("#exec").attr("value");
	var seleziona="#id_executor option[value='"+esec+"']";
	$(seleziona).attr("selected","selected");
	//copio la data
	var data=$("#dat").val();
	$("#id_date").val(data);
	//do' il nuovo valore all'utente
	var u=$("#address_to").attr("value");
	var seleziona="#id_dest option[value='"+u+"']";
	$(seleziona).attr("selected","selected");
	if(!(vuota())){
		$("#id_executor,#id_date,#id_dest").attr("disabled",true);
	}
}

$(document).ready(function () {
		
    //per il demo. Serve a cancellare tutti gli utenti diversi da quello attuale
    //cancella_utenti();

    $("#id_aliquot").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: base_url+'/ajax/derived/autocomplete/',
                dataType: "json",
                data: {
                    term: request.term,
                    WG:WG
                },
                success: function(data) {
                    response(data);
                }
            });
        },
    });
	
	$("#tastofile").click(function(){
		$("#id_file").click();
	});
		
	$("#id_file").change(function(){
		var files = $('#id_file')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
	});
	
	$("#aliquote").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
		"aoColumnDefs": [
  	        { "bSortable": false, "aTargets": [ 4 ] },
  	        { "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='13px' height='13px' onclick='cancella(this.parentNode.parentNode)' >" , "aTargets": [ 4 ]},
  	    ],});
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
    	generate_result_table("Transfer","aliquote_fin");
	}
	else{
		inizializza();
		assegna_valori();
		var option = $('#id_executor').find('option:selected').attr('wg');
	    if (option != undefined)
	        WG=option;
	    else{
	    	//vuol dire che non scelgo l'esecutore, ma assegno la procedura a tutti quelli di quel wg, quindi
	    	//come wg per l'autocompletamento prendo quello dell'utente pianificatore
	        WG=workingGroups.split(",")[0];
	    }
	}
	
	$("#id_date").attr("size",10);
	$("#id_date").datepicker({
		 //changeMonth: true,
		 //changeYear: true,
		 dateFormat: 'yy-mm-dd',
		 minDate: 0
	});

	$("#nuova_aliquota").attr("disabled",true);
	$("#id_aliquot").attr("size","32");
	
	//aggiungo il tasto Add_file e il collegamento al file che spiega come deve essere
	//fatto il file con la lista delle aliquote
	url=media_url+"/tissue_media/File_Format/Aliquot.txt";
	$("#addfile").after("<br><a id='file' href="+url+" class='anchor' >File Format</a>");
	//creo la finestra di popup
	$(".anchor").popupWindow({ 
		height:500, 
		width:800, 
		top:50, 
		left:50,
		scrollbars:1,
		resizable:1,
		menubar:1
		}); 
	$("#id_aliquot").attr("onFocus","$(\"#nuova_aliquota\").attr(\"disabled\",false);");
	
	$("#nuova_aliquota").click(aggiungi_aliquota);
	$("#id_aliquot").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_aliquota();
		}
	});
	
	$("#addfile").click(function(event){
		event.preventDefault();

        if($('#id_executor option:selected').val() =='None'){
            alert('Insert a valid executor');
            return;
        }

        if($('#id_dest option:selected').val() ==''){
            alert('Insert a valid receiver');
            return;
        }

       if($('#filename').val() ==''){
            alert('Insert a valid file name');
            return;
        }

    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(valori_campioni),
    			exec:$("#id_executor option:selected").attr("value"),
    			dat:$("#id_date").val(),
    			addr:$("#id_dest option:selected").attr("value")
	    };
    	
    	var url=base_url+"/transfer/insert/";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	else{
	    		$("#form_file").append("<input type='hidden' name='aggiungi_file' />");
	    	
	    		$("#form_file").submit();
	    	}
	    });
	});

      $('#id_executor').change(function()
        {
                var option = $(this).find('option:selected').attr('wg');
                if (option != undefined)
                    WG=option;
                else
                    WG='';
        });
	
	$("#conferma,#next").click(function(event){
		event.preventDefault();
		//per capire su quale tasto ho cliccato
		var id=$(this).attr("id");
		if(vuota()){
			alert("Please insert some aliquots");
		}
		else{
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(valori_campioni),
	    			exec:$("#id_executor option:selected").attr("value"),
	    			dat:$("#id_date").val(),
	    			addr:$("#id_dest option:selected").attr("value")
		    };

    		var url=base_url+"/transfer/insert/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	else{
		    		if (id=="conferma"){
			    		$("#form_fin").append("<input type='hidden' name='final' />");
			    	}
			    	else{
			    		$("#form_fin").append("<input type='hidden' name='next' />");
			    	}
		    	
		    		$("#form_fin").submit();
		    	}
		    });
		}
	});

});

