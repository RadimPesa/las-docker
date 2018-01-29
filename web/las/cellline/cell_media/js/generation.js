var flag_presente = 0; var loadedBarcode = "";var protocol_infos_dictionary = {};
var selectedAlias = ['','']; //id, name
var listabarcgenerale=new Array();
var contatore=1; var conttab=1;
var listaappoggio=new Array();

$(document).ready(function(){
    console.log('document ready');
    //genid_alreadyselected = new Array();
    genid_alreadyselected = {};
    modified_elements = {};
    plates_alreadyloaded = {};
    to_generation = {};
    to_biobank = {};
    init_button();
    $("#button_protocol").attr('disabled', true);
    $("#vital th").attr("align","center");
    if (typeOperation == 'Thawing'){
        var oTable = jQuery('table#table_prot_info').dataTable( {
            "bProcessing": true,
            "aoColumns": [{ 
                    "sTitle": null, 
                    "sClass": "control_center", 
                    "sDefaultContent": '<img src="'+base_url+'/cell_media/img/x.png">'
                },
                { "sTitle": "Source genID" , "sClass": "genealogy" },
        		{ "sTitle": "Samples taken" },
        		{ "sTitle": "Freezer" },
        		{ "sTitle": "Rack" },
        		{ "sTitle": "Plate position" },
        		{ "sTitle": "Plate" },
        		{ "sTitle": "Position" },
        		{ "sTitle": "Barcode" },
                { "sTitle": "InternalCode" },
                { "sTitle": "Available" },
                ],
                "bAutoWidth": false ,
                //"aaSorting": [[3, 'asc'], [4, 'asc']],
                "aoColumnDefs": [{ "bSortable": false, "aTargets": [ 0 ] },
                                { "bVisible": false, "aTargets": [2,9]},
                                 ],
                "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        });
    }
    else{

        var oTable = jQuery('table#table_prot_info').dataTable( {
        	"bProcessing": true,
        	"aoColumns": [{ 
        			"sTitle": null, 
        			"sClass": "control_center", 
        			"sDefaultContent": '<img src="'+base_url+'/cell_media/img/x.png">'
        		},
        		{ "sTitle": "Source genID" , "sClass": "genealogy" },
        		{ "sTitle": "Samples taken" },
        		{ "sTitle": "Freezer" },
        		{ "sTitle": "Rack" },
        		{ "sTitle": "Plate position" },
        		{ "sTitle": "Plate" },
        		{ "sTitle": "Position" },
        		{ "sTitle": "Barcode" },
        		{ "sTitle": "InternalCode" },
        		{ "sTitle": "Available" },
        		],
        		"bAutoWidth": false ,
        		//"aaSorting": [[3, 'asc'], [4, 'asc']],
        		"aoColumnDefs": [{ "bSortable": false, "aTargets": [ 0 ] },
        		                 { "bVisible": false, "aTargets": [9]},
                                 ],
                "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        });
    }
    
    var oTable = jQuery('#table_conf_aliq').dataTable( {
    	"bProcessing": true,
    	"aoColumns": [
    	              	{ "sTitle": "N" },
			    		{ "sTitle": "Source genID" , "sClass": "genealogy" },
			    		{ "sTitle": "Samples taken" },
			    		{ "sTitle": "Freezer" },
			    		{ "sTitle": "Rack" },
			    		{ "sTitle": "Plate position" },
			    		{ "sTitle": "Plate" },
			    		{ "sTitle": "Position" },
			    		{ "sTitle": "Barcode" },    		
		    		],
		"bAutoWidth": false ,
		"aaSorting": [[0, 'asc']],
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
    
    oTableSx = jQuery("table#availableProt").dataTable( {
        "bProcessing": true,
        "bLengthChange": true, 
        "bPaginate": true,
        //"iDisplayLength":5,
        "bAutoWidth": false ,
        "aaSorting": [[2, 'desc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0, 1 ] }
        ],
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
    oSettingsSx = oTableSx.fnSettings();
    oTableDx = jQuery("table#selectedProt").dataTable( {
        "bProcessing": true,
        "bLengthChange": true, 
        "bPaginate": true,
        //"iDisplayLength":5,
        "bAutoWidth": false ,
        "aaSorting": [[2, 'desc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0, 1 ] }
        ],
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
    oSettingsDx = oTableDx.fnSettings();
    var input = oTableSx.$("tr");
    $(input).click(function(){selectLine(this)});
    var input = oTableDx.$("tr");
    $(input).click(function(){selectLine(this)});
    oTableAlias = $("table#aliasList").dataTable( {
                    "bProcessing": true,
                    "aaSorting": [[2, 'desc']],
                    "aoColumnDefs": [
                        { "bVisible": false, "aTargets": [ 0 ] }
                    ],
                    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                });
});

function selectLine(row){
    console.log('selectLine');
    $(row).toggleClass("row_selected");
}


function getInfos(img){
    console.log('getInfos');
    console.log($(img).parent().parent());
    var row = $(img).parent().parent();
    showInfos($(img).attr('protId'));
    $(row).toggleClass("row_selected");
}

function init_button(){
    console.log('init_button');
    barcode_choosen = document.getElementById("barcode");
    console.log(barcode_choosen);
    $("#load_plate").click(function() {
	    load_plate(barcode_choosen.value);
    });
    
    $("#barcode").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			load_plate(barcode_choosen.value);
		}
	});
};

function proceed(){
    console.log('proceed');
    $("#sx,#divCen").hide();
    $("#dx").css('float','left');
    $("#plating,#view_aliquots").show();
    //inserire controllo per eventuali dati ricevuti dalla biobanca e popolare la pagina
    if (data != ""){
        console.log(data);
        $("#div_conf,#conf_aliquots").show();
        
        //do il focus al campo con il barcode della provetta
    	$("#id_barcode").focus();	
    	$("#conf").click(conf_barcode);
    	
    	$("#id_barcode").keypress(function(event){
    		if ( event.which == 13 ) {
    			event.preventDefault();
    			conf_barcode();
    		}
    	});
        
        var listagen=[];
        var diztot={};
        for (d in data){
        	listagen.push(data[d]["genid"]);
        	diztot[data[d]["genid"]]={"father":data[d]['father'],"pos":data[d]['pos'],"barcode":data[d]['barcode']};        	
        }
        
        //chiamo la API per popolare le tre colonne del freezer, rack e pos piastra
        var lgen="";
		var lis_pezzi_url=[];
		var utente=$("#actual_username").val();
		var url=base_url+"/api/storage/tube/";
		for (var i=0;i<listagen.length;i++){
			//mi da' il gen attuale
			var gen=listagen[i];
			lgen=lgen+gen+"&";
			lgen = lgen.replace(/#/g, "%23");
			if (lgen.length>2000){
	            lis_pezzi_url.push(lgen);
	            lgen="";
			}
		}
		if (lgen==""){
			lgen="-";
			lis_pezzi_url.push("-");
		}
		else{
			lis_pezzi_url.push(lgen);
		}
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		for (var j=0;j<lis_pezzi_url.length;j++){
			var urlst=url+lis_pezzi_url[j]+"/"+utente;
			$.ajax({
		        async:false,
			    url: urlst,
			    type: 'GET',
			    success: function(d) {
			    	if (d.data!="errore"){
						var diz=JSON.parse(d.data);
						if(Object.size(diz)!=0){
							//scrivo nel campo apposito l'indicazione della posizione della provetta
							for (var i=0;i<listagen.length;i++){
								var gen=listagen[i];
								var listaval=diz[gen];
								if(listaval!=undefined){
									var val=listaval.split("|");
									var pospiastra=val[3];
									var rack=val[4];
									var freezer=val[5];
									var disp=val[6];
									var diziotemp=diztot[gen];
									//se sto trattando una piastra con i pozzetti lo storage mi dara' un barcode pari a None per la singola aliquota
									//invece se e' una piastra con le provette il barcode avra' il suo valore. In base a questo discrimino i due casi
									var barcapi=val[0];
									if(barcapi=="None"){
										barcapi="";
										//Carico il valore della piastra stessa
										if($.inArray(val[2].toUpperCase(),listabarcgenerale)==-1){
											listabarcgenerale.push(val[2].toUpperCase());
										}
									}
									else{
										listabarcgenerale.push(val[0].toUpperCase());
									}
									
									//solo se non e' gia' in lista lo inserisce
									if(($.inArray(val[0].toUpperCase(),listaappoggio)==-1)&&(val[0]!="None")){
										listaappoggio.push(val[0].toUpperCase());	
									}
									if(($.inArray(val[2].toUpperCase(),listaappoggio)==-1)&&(val[2]!="None")){
										listaappoggio.push(val[2].toUpperCase());
									}
									if(($.inArray(val[4].toUpperCase(),listaappoggio)==-1)&&(val[4]!="None")){
										listaappoggio.push(val[4].toUpperCase());
									}
									if(($.inArray(val[5].toUpperCase(),listaappoggio)==-1)&&(val[5]!="None")){
										listaappoggio.push(val[5].toUpperCase());
									}
									
									useInputData(gen, freezer, rack, pospiastra, diziotemp["father"], diziotemp["pos"], barcapi, disp);
								}
							}							
						}						
						//lo faccio solo una volta alla fine del ciclo generale
						if (contatore==lis_pezzi_url.length){
							trova_figli_container();
							clearTimeout(timer);
							$("body").removeClass("loading");
						}
			    	}			    	
					contatore++;
			    }
		    });
		}        
        
    }
    else{
    	//devo nascondere le colonne che non uso
    	var oTable = $('#table_prot_info').dataTable();
    	oTable.fnSetColumnVis( 3, false);
    	oTable.fnSetColumnVis( 4, false);
    	oTable.fnSetColumnVis( 5, false);
    	oTable.fnSetColumnVis( 10, false);
    }
}

function trova_figli_container(){
	var lbarc="";
	var url=base_url+"/api/check/children/";	
	for (var i=0;i<listabarcgenerale.length;i++){
		lbarc=lbarc+listabarcgenerale[i]+"&";
	}
	lbarc = lbarc.substring(0, lbarc.length - 1);
	var codice=lbarc.replace(/#/g,"%23");
	var data = {
			lbarc:codice
    };
	$.post(url, data, function (result) {
		if (result.data!="errore"){
			var lista=result.data;
			for(var i=0;i<lista.length;i++){
				if($.inArray(lista[i].toUpperCase(),listabarcgenerale)==-1){
					listabarcgenerale.push(lista[i].toUpperCase());
				}
			}			
		}
	});
}

function useInputData (genid_received, freezer, rack, pospiastra, plate, matrix_position, tube_barcode, disp){
    /*var prots = getSelectedProtocols();
    var init_value = 0;
    
    var plateeffettiva=tube_barcode;
    if(tube_barcode==""){
    	plateeffettiva=plate;
    }
    
    if (modified_elements[plateeffettiva] == undefined){
        modified_elements[plateeffettiva] = {};
        to_biobank[plateeffettiva] = {};
    }
    
    to_biobank[plateeffettiva][matrix_position]= {'iniQ':init_value, 'actualQ':init_value, 'aliquot':genid_received};*/
    $('#table_prot_info').dataTable().fnAddData(['-', genid_received, 1, freezer, rack, pospiastra, plate, matrix_position, tube_barcode, null, disp]);
    /*var temp = [];
    for (var i = 0; i < prots.length; i++){
        if ($.inArray(prots[i]['type_process'], temp) == -1){
            temp.push(prots[i]['type_process']);
        }
        outputLines(prots[i]['type_process'], loadedBarcode, matrix_position, genid_received, init_value,  tube_barcode, prots[i]['id'], prots[i]['name'], true);
    }*/
}

function getSelectedProtocols(){
    console.log('getSelectedProtocols');
    protocols = []
    for (var i = 0; i < oTableDx.fnGetNodes().length; i++){
        var data = oTableDx.fnGetData(i);
        var temp = {};
        temp['id'] = data[0]
        temp['type_process'] = data[1]
        temp['name'] = data[2]
        protocols.push(temp);
    }
    console.log(protocols);
    return protocols
}

function conf_barcode(){
	var barcorig=$("#id_barcode").val();
	var barc=barcorig.toUpperCase();
	if ($.inArray(barc,listaappoggio)!=-1){
		if ($.inArray(barc,listabarcgenerale)!=-1){
			var tabella=$("#table_prot_info").dataTable();
			var tabellasotto=$("#table_conf_aliq").dataTable();
			var aTrs = tabella.fnGetNodes();
			var oSettings = tabella.fnSettings();
			//mi da' il numero di colonne che ci sono nel data table			
			var lunghezza = (oSettings.aoColumns.length-1);
			if (typeOperation == 'Thawing'){
				lunghezza--;
			}
			// scandisce tutte le righe della tabella
			var avviso=false;
	        jQuery.each(tabella.fnGetData(), function(key, d) {
	        	if ((d[8].toUpperCase() == barc)||(d[6].toUpperCase()== barc)||(d[4].toUpperCase()==barc)||(d[3].toUpperCase()==barc)){
	        		//mi da' la riga del data table
					var riga=aTrs[key];
	        		var fi=":nth-child("+(lunghezza)+")";
	        		var dispon=$(riga).children(fi).text();
	        		if (dispon=="Yes"){
		        		var listadatitemp=[conttab,d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8]];

						var rowPos=tabellasotto.fnAddData(listadatitemp);
						
		                tabella.fnDeleteRow(riga);
		                conttab++;
		                var prots = getSelectedProtocols();
		                var init_value = 0;
		                //d[7]=pos, d[1]=gen, d[8]=tube barcode, d[6]=plate, d[1]=gen
		                var plateeffettiva=d[8];
		                if(d[8]==""){
		                	plateeffettiva=d[6];
		                }
		                
		                if (modified_elements[plateeffettiva] == undefined){
		                    modified_elements[plateeffettiva] = {};
		                    to_biobank[plateeffettiva] = {};
		                }
		                //Non metto actualQ a 0 altrimenti la biobanca mi cancellerebbe sempre il campione
		                to_biobank[plateeffettiva][d[7]]= {'iniQ':init_value, 'actualQ':null, 'aliquot':d[1]};
		                //to_biobank[plateeffettiva][d[7]]= {'iniQ':init_value, 'actualQ':init_value, 'aliquot':d[1]};
		                
		                //il loadedbarcode lo lascio ma nella funzione outputlines non viene letto se la sorgente e' la biobanca, cosi' come il d[8]
		                var nick="";
		                if(d[1] in diznickplan){
		                	nick=diznickplan[d[1]];
		                }
		                for (var i = 0; i < prots.length; i++){
		                	outputLines(prots[i]['type_process'], loadedBarcode, d[7], d[1], init_value, d[8], prots[i]['id'], prots[i]['name'], true, nick);
		                }		                
	        		}
	        		else{
	        			if(!avviso){
		        			alert("Container is not available. You can't select it.");
							$("#id_barcode").attr("value","");
							$("#id_barcode").focus();
							avviso=true;
	        			}
	        		}
	            }
	        });
			$("#id_barcode").val("");
			$("#id_barcode").focus();
			//tolgo il codice dalla lista generale
			removeBarcode(barc);			
			
		}
		else{			
			alert("You did not schedule to thaw all children's container. Please validate barcode singularly.");
			$("#id_barcode").attr("value","");
			$("#id_barcode").focus();
		}
	}
	else{
		alert("Invalid barcode");
		$("#id_barcode").attr("value","");
		$("#id_barcode").focus();
	}	
}

function removeBarcode(barcode){
    for (var i=0; i < listabarcgenerale.length; i++){
        if (listabarcgenerale[i] == barcode){
        	listabarcgenerale.splice(i,1);
        }
    }
}

function put_infos(dictionary){
    console.log('put_infos');
    var tabella = $("#protocol_infos");
    $("#protocol_infos").empty();
    var description = dictionary["description"];
    var creation_dtime = dictionary["creation_dtime"];
    var file_name = dictionary["file_name"];
    var ft_without_el_list = dictionary["ft_without_el_list"];
    for(var tuple=0; tuple<ft_without_el_list.length;tuple++){
        for(key in ft_without_el_list[tuple]){
            if (key == 'type_process')
                $("#type_process").attr("value",ft_without_el_list[tuple][key]);
            var row = $("<tr><td class='root'>"+key+"</td><td>"+ft_without_el_list[tuple][key]+"</td></tr>");
            tabella.append(row);		             
            }
    }
    var root_ft_dictionary = dictionary["root_ft_dictionary"]
    for(root in root_ft_dictionary){
        for(father in root_ft_dictionary[root]){
            var row = $("<tr><td class='root'>"+root+"</td>");
            row = row.append("<td class='father'>"+father+"</td>");
            for(var ft_index = 0; ft_index<root_ft_dictionary[root][father].length; ft_index++){
                    feature = root_ft_dictionary[root][father][ft_index];
                    row = row.append("</tr><tr><td class='col_ftname'>"+feature.name+"</td><td class='col_ftname'>"+feature.value+"</td><td class='col_ftname'>"+feature.unity_measure+"</td>");
            }
          row = row.append("</tr>");
          tabella.append(row);
        }
    }
    var row = $("<tr><td class='root'> Creation time</td><td class='col_ftname'>"+creation_dtime+"</td></tr>");
    tabella.append(row);
    if (file_name != "")
        tabella.append('</tr><tr><td class="root"> Docs </td><td><a href="'+ base_url + "/get_file/" + file_name + '"> <span class="ui-icon ui-icon-arrowthickstop-1-s"></span></a></td>');
    tabella.append("</tr><tr><td class='root'> Description </td><td class='col_ftname'>"+description+"</td></tr>");
}

function load_plate(barcode_selected) {
    console.log('load_plate');
    loadedBarcode = barcode_selected;
    var nameP = "vital";
	$("#" + nameP + " button,#confirm_all").attr("disabled", false );
	var url = base_url + '/api/urlGenerationAliquotsHandlerLoadPlate/biobank/'+barcode_selected+"/VT/";
    var data;
    if(plates_alreadyloaded.hasOwnProperty(barcode_selected)){
        $("#" + nameP).empty()
		$("#" + nameP).append(plates_alreadyloaded[barcode_selected]["data"]);
        update_plate_values(plates_alreadyloaded[barcode_selected]["diznick"]);
    }else{
    	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	    $.ajax({
	        async:false,
		    url: url,
		    type: 'GET',
		    success: function(response) {
			data = JSON.parse(response);
		    }
	    });
	    var errors_free = true;
	    if(data.data=="errore") {
	        errors_free = false;
		    alert("Plate doesn't exist");
		    $("#" + nameP + " button,#confirm_all").attr("disabled", true );
	    }
	    if(data.data=="errore_piastra") {
	        errors_free = false;
		    alert("Plate aim is not working");
		    $("#" + nameP + " button,#confirm_all").attr("disabled", true );
	    }
	    if(data.data=="errore_aliq") {
		    errors_free = false;
		    var val=$("#"+nameP+" th").text().toLowerCase();
		    alert("Plate selected is not viable");
		    $("#" + nameP + " button,#confirm_all").attr("disabled", true );
	    }
	    if(data.data=="errore_store") {
	        errors_free = false;
		    alert("Error while connecting with storage");
		    $("#" + nameP + " button,#confirm_all").attr("disabled", true );
	    }
	    if(errors_free){
	    	//chiave il gen e valore il nick della linea
	    	var diznick=data.diznick;
	        plates_alreadyloaded[barcode_selected] = {"data":data.data,"diznick":diznick};
            $("#" + nameP).empty()
		    $("#" + nameP).append(data.data);
		    update_plate_values(diznick);
	    }
	    //c'e' async false quindi posso mettere qui la cancellazione del timeout
	    clearTimeout(timer);
    	$("body").removeClass("loading");
    }
}

function update_plate_values(diznick) {
    console.log('update_plate_values');        
    $(".tooltip_em").remove();
    //var current_plate = $(document.getElementById("vital")).attr("plate");
    $("#vital th").attr("align","center");
    $('#vital button').each (function() {
        var matrix_position = $(this).attr("id").substring(2);
        var gen=$(this).attr("gen");
        if ( gen != undefined) {
            $(this).removeAttr("disabled");
            if (gen in diznick){
            	var fr="tooltip.show(\"GenID: "+gen+" nickname: "+diznick[gen]+"\")";
            	$(this).attr("nick",diznick[gen]);
            }
            else{
            	var fr="tooltip.show(\""+gen+"\")";
            }            
            $(this).attr("onmouseover",fr);
            $(this).attr("onmouseout","tooltip.hide();");
            $(this).removeAttr("title");
            if (modified_elements.hasOwnProperty(loadedBarcode)){
                console.log(matrix_position);
                if(modified_elements[loadedBarcode].hasOwnProperty(matrix_position)){
                    var valore = (this).innerHTML;
                    var decrementa = valore - modified_elements[loadedBarcode][matrix_position];
                    if(isNaN(decrementa)){
                    	decrementa="#";
                    }
                    $(this).text(decrementa);
                    if (decrementa == 0){
                        $(this).attr("disabled",true);
                        $(this).removeAttr("onmouseover");
                    }
                }
            }
            populate_tables($(this).attr("id"));
        }
        else 
            $(this).attr("disabled",true);
    });
}


function listContainers(){ //list of used containers
    var tempArray = [];
    for (barcodeP in to_biobank){
        if (Object.size(to_biobank[barcodeP]) > 0){
            tempArray.push(barcodeP);
        }
    }
    return tempArray;
}


$(document).on("click", "#button_generate_aliquots", function () {
    console.log('onclick button_generate_aliquots');
    var usedCont = listContainers();

    if (usedCont.length > 0){
    	jQuery('#plateEmptyList').empty();
        for (var i = 0; i < usedCont.length; i++){  	
            var container = jQuery('#plateEmptyList');
            var html = '<input type="checkbox" id="'+usedCont[i]+'" value="'+usedCont[i]+'" /> <label for="'+usedCont[i]+'">'+usedCont[i]+'</label><br>';
            container.append(jQuery(html));
        }
        
        jQuery( "#dialogEmpty" ).dialog({
            //autoOpen : false,
            resizable: false,
            height:250,
            width:340,
            modal: true,
            draggable :false,
            buttons: {
                "Yes": function() {
                    jQuery( this ).dialog( "close" );
                    jQuery( "#dialogConfirmEmpty" ).dialog({
                        //autoOpen : false,
                        resizable: false,
                        height:250,
                        width:340,
                        modal: true,
                        draggable :false,
                        buttons: {
                            "Yes": function() {

                                //recuperare le piastre selezionate                 
                                for (var i = 0; i < jQuery("#plateEmptyList input:checked").length;i++){
                                    //aggiornare emptyFlag nella struttura dati
                                    var bP = jQuery(jQuery("#plateEmptyList input:checked")[i]).val();
                                    console.log(bP);
                                    to_biobank[bP]['emptyFlag'] = true;
                                }
                                
                                continueGen();
                                jQuery( this ).dialog( "close" );
                            },
                            "No": function() {
                                continueGen();
                                jQuery( this ).dialog( "close" );
                            }
                        }
                    });
                },
                "No": function() {
                    continueGen();
                    jQuery( this ).dialog( "close" );
                }
            }
        });
    
    }
});


function continueGen(){

    for (newG in to_generation){
        console.log(newG);
        for (p in to_generation[newG]['prot']){
            
            var tempA = [];
            console.log(p);
            var protocol_name = to_generation[newG]['prot'][p]['name'];
            var pId = to_generation[newG]['prot'][p]['id'];
            console.log(tempA);
            console.log($.inArray(to_generation[newG]['genid_source']));
            for ( var i = 0; i < to_generation[newG]['genid_source'].length; i++){
                console.log(to_generation[newG]['genid_source'][i]);
                var aliquot = to_generation[newG]['genid_source'][i];
                if ($.inArray(aliquot, tempA) == -1){
                    tempA.push(aliquot);
                    console.log(tempA);
                
                }
            }
            var temp = "";
            for (var j=0; j < tempA.length; j++){
                if (temp == "")
                    temp = tempA[j];
                else
                    temp = temp + '\n' + tempA[j];
            }
            
            $( "#popup_list tbody" ).append( '<tr id=' + newG + '>' +
                '<td>' + newG + '</td>' +
                //'<td>' + to_generation[newG]['genid_source'] + '</td>' +
                '<td>' + temp + '</td>' +
                '<td pId="'+pId+'">' + protocol_name + '</td>' +
                '<td><img src="'+base_url+'/cell_media/img/admin/icon_addlink.gif" onclick="insertSelection(this);"/> <input type="text" id="nickname_'+newG+'_'+pId+'" value="' + to_generation[newG]['prot'][p]["nickname"] + '" aliasid="" onKeyPress=validateFreeInput(event) /></td>' +
                '<td><input type="text" id="numplates_'+newG+'_'+pId+'" pId = '+pId+' value="' + to_generation[newG]['prot'][p]["num_plates"] + '" typeInfo="plates" aliasid="" onKeyPress=validateNumber(event) /></td>' +
                '</tr>' );
            console.log("<td>"+temp+"</td>");
        }
    }
    $("#popup_list tbody input[typeInfo='plates']").spinner({min: 1, max:100});
    $("#plating,#view_aliquots,#dx,#div_conf,#conf_aliquots").hide();    
    $( "#dialog-form" ).show();
}

function validateNumber(evt) {
	var theEvent = evt || window.event;
	var key = theEvent.keyCode || theEvent.which;
	//sono le frecce a destra e a sinistra e il canc			
	if((key==39)||(key==37)||(key==46)){
		return;
	}
	key = String.fromCharCode( key ); 
	var regex = /[0-9\b]/;
	if( !regex.test(key) ) {
		theEvent.returnValue = false;
		if(theEvent.preventDefault) theEvent.preventDefault();
		alert("Unsupported character");
	}
}
      
$(document).on("click", "#table_prot_info tbody td img", function () {
    console.log('onclick table_prot_info tbody td img');
	var nTr = jQuery(this).parents('tr')[0];
	var current_row = jQuery('table#table_prot_info').dataTable().fnGetData(nTr);
	var genid_received = current_row[1];
    var amount = current_row[2];       
    var src_plate = current_row[6];
    var matrix_position = current_row[7];
    
    var internalcode = current_row[9];
    var labsplit=internalcode.split("|");
    var contpadrealiq = labsplit[0];
    var posaliq = labsplit[1];
    if ($("[pos='"+matrix_position+"']").text() != '#' && $("[pos='"+matrix_position+"']").text() != -1){
        var inc_value = parseInt($("[pos='"+matrix_position+"']").text())+1;
    }
    else{
        var inc_value = $("[pos='"+matrix_position+"']").text();
    }
    if (src_plate == loadedBarcode){
        $("[pos='"+matrix_position+"']").text(inc_value);
        $("[pos='"+matrix_position+"']").attr("disabled",false);
    }
    if (amount == 1){
	    jQuery('#table_prot_info').dataTable().fnDeleteRow( nTr );
    	//var rows = jQuery("#table_prot_info").dataTable().fnGetNodes();
	    delete modified_elements[contpadrealiq][posaliq];
    	//struttura per biobank
	    delete to_biobank[contpadrealiq][posaliq];
        for (newG in to_generation){
            for (var i = 0; i < to_generation[newG]['genid_source'].length; i++){
                if (genid_received == to_generation[newG]['genid_source'][i]){
                    console.log('SPLICEEEE');
                    to_generation[newG]['genid_source'].splice(i, 1);
                    //i--;
                    checkGenerated(newG);
                    break;
                }
            }
        }
    }else{
        for (newG in to_generation){
            for (var i = 0; i < to_generation[newG]['genid_source'].length; i++){
                if (genid_received == to_generation[newG]['genid_source'][i]){
                    to_generation[newG]['genid_source'].splice(i, 1);
                    break;
                }
            }
        }
        $("#table_prot_info").dataTable().fnUpdate(amount-1,nTr,2);
    	modified_elements[contpadrealiq][posaliq] -= 1;
    	//struttura per biobank
    	to_biobank[contpadrealiq][posaliq]['actualQ'] += 1;

    }
} );

function checkGenerated(newG){
    console.log('checkGenerated ' + newG);
    if (genid_alreadyselected.hasOwnProperty(newG)) {
        console.log('1');
        delete genid_alreadyselected[newG];
    }
    if (to_generation[newG]['genid_source'].length == 0){
        console.log('2');
        delete to_generation[newG]
        $("#id_table_result span#" + newG).remove();
        if ( $("#id_table_result span").length == 0 )
            $('#button_generate_aliquots').hide();
    }
}

function populate_tables(vitalbutton_id) {
    console.log('populate_tables');
    var vitalbutton = document.getElementById(vitalbutton_id);
    var plate = loadedBarcode;
    vitalbutton.onclick = function() {
            clickOnTube(vitalbutton, plate);
        }
}


function clickOnTube (vitalbutton, plate){
	console.log("clickOnTube");
    var prots = getSelectedProtocols();
    matrix_position = $(vitalbutton).attr("id");
    //L'id e' ad es v-C1 e questo toglie le prime due lettere
    matrix_position = matrix_position.substring(2);
    var posoriginale=matrix_position;
	var tube_barcode = $(vitalbutton).attr("barcode");
	//se il barcode e' nella forma barc|pos allora non tocco niente, se invece e' solo barc, allora vuol dire che ho 
	//caricato una piastra con le provette e devo salvare il valore del barc della provetta e non della piastra
	var tubesplit=tube_barcode.split("|")
	if(tubesplit.length==1){
		plate=tube_barcode;
		matrix_position="A1";
	}
    
    var genid_received = $(vitalbutton).attr("gen");
    console.log(genid_received);
    console.log(typeOperation);
    console.log(genid_received[9]);
    if (typeOperation == 'Thawing'){
    	//puo' succedere che il gen sia uguale a "NOT AVAILABLE" e quindi gen[9]="A", ma non va bene lo stesso 
        if ((genid_received=="NOT AVAILABLE")||(genid_received[9] != 'S' &&  genid_received[9] != 'A' &&  genid_received[9] != 'O')){
            alert('Error: Aliquot is not available for thawing.');
            return;
        }
    }
    else{
        if ((genid_received=="NOT AVAILABLE")||(genid_received[9] == 'S' ||  genid_received[9] == 'A' ||  genid_received[9] == 'O')){
            alert('Error: Aliquot is not available for generation.');
            return;
        }

    }    
    if (vitalbutton.innerHTML != '#' && vitalbutton.innerHTML != -1){
        var init_value = parseInt(vitalbutton.innerHTML);
        var value = parseInt(vitalbutton.innerHTML);

        value -= 1;
        vitalbutton.innerHTML = value;
        if (value == 0){
            vitalbutton.innerHTML = "0";
            $(vitalbutton).attr("disabled",true);
            $(vitalbutton).removeAttr("onmouseover");
            value = 0;
        }
    }
    else{
        var init_value = -1;
        var value = -1;
    }
    if (modified_elements[plate] == undefined){
        modified_elements[plate] = {};
        to_biobank[plate] = {};                
    }
    console.log('matrix_position',matrix_position);
    if(modified_elements[plate] == {}){
        console.log("piastra non presente:aggiungo")
        modified_elements[plate][matrix_position] =1;
        // struttura per biobank
        if (init_value == -1){
            to_biobank[plate][matrix_position]= {'iniQ':init_value, 'actualQ':init_value, 'aliquot':genid_received};
        }
        else{
            to_biobank[plate][matrix_position]= {'iniQ':init_value, 'actualQ':init_value-1, 'aliquot':genid_received};
        }
        if(tubesplit.length>1){
    		tube_barcode="";
    	}
        $('#table_prot_info').dataTable().fnAddData([null,genid_received,1,null,null,null,loadedBarcode,posoriginale,tube_barcode,plate+"|"+matrix_position,null]);
    }else{
        if(modified_elements[plate][matrix_position] == undefined){
            modified_elements[plate][matrix_position] =1;
            // struttura per biobank
            if (init_value == -1){
                to_biobank[plate][matrix_position]= {'iniQ':init_value, 'actualQ':init_value, 'aliquot':genid_received};
            }
            else{
                to_biobank[plate][matrix_position]= {'iniQ':init_value, 'actualQ':init_value-1, 'aliquot':genid_received};
            }
            if(tubesplit.length>1){
        		tube_barcode="";
        	}
            $('#table_prot_info').dataTable().fnAddData([null,genid_received,1,null,null,null,loadedBarcode,posoriginale,tube_barcode,plate+"|"+matrix_position,null]);
        }else{
            var rows = jQuery("#table_prot_info").dataTable().fnGetNodes();
            for (var index=0; index<rows.length; index++){
                var gen = jQuery("#table_prot_info").dataTable().fnGetData(rows[index],1);
                if (genid_received == gen){
                   modified_elements[plate][matrix_position] += 1;
                   jQuery("#table_prot_info").dataTable().fnUpdate(modified_elements[plate][matrix_position],rows[index],2);
                   // struttura per biobank
                   if (to_biobank[plate][matrix_position]['actualQ'] == -1){
                    to_biobank[plate][matrix_position]['actualQ'] = -1;
                   }
                   else{
                        to_biobank[plate][matrix_position]['actualQ'] -= 1;
                   }
                   console.log(to_biobank)
                   break;
                }
            }
        }
    }
    var temp = [];
    var nickname="";
    var nick= $(vitalbutton).attr("nick");
    if(nick!=undefined){
    	nickname=nick;
    }
    for (var i = 0; i < prots.length; i++){
        if ($.inArray(prots[i]['type_process'], temp) == -1){
            temp.push(prots[i]['type_process']);
            //outputLines(prots[i]['type_process'], vitalbutton, loadedBarcode, matrix_position, genid_received, init_value, value, tube_barcode, prots[i]['id'], prots[i]['name']);
        }
        outputLines(prots[i]['type_process'],  plate, matrix_position, genid_received, init_value, tube_barcode, prots[i]['id'], prots[i]['name'], false,nickname);
    }
}

function outputLines(type_process,  plate, matrix_position, genid_received, init_value,  tube_barcode,  idP, nameP, fromBioBank, nickname){
    console.log('outputLines');
    var genid_generated = "";
    var index_letter = type_process.indexOf('(');
    var type_process_letter = type_process.charAt(index_letter+1).toUpperCase();
    var genid_starts = genid_received.substring(0,9) + type_process_letter;
    console.log(genid_starts);
    console.log(base_url + "/api/urlGenId-generationGetter/" + genid_received + "/" + type_process_letter);
    $.ajax({
        async:false,
        url: base_url + "/api/urlGenId-generationGetter/",
        type: 'POST',
        data: {'generatedList': JSON.stringify(genid_alreadyselected), 'type_process_letter': type_process_letter, 'genid_received' : genid_received, 'protocol': idP},
        //data: {'generatedList': JSON.stringify(genid_alreadyselected), 'type_process_letter': type_process_letter, 'genid_received' : genid_received, 'typeOperation':typeOperation},
        //non metto typeOperation in quanto l'API filtra gia' sul vettore (se e' S o A e' scongelamento, H o X generazione)
        success: function(genid_fromApi){
            genid_generated = genid_fromApi;
        }
    });
    console.log(genid_generated);

    if (genid_alreadyselected.hasOwnProperty(genid_generated) == false ){
        //genid_alreadyselected.push(genid_generated);
        genid_alreadyselected[genid_generated] = {'aliquots':[], 'protocol':null};
        genid_alreadyselected[genid_generated]['aliquots'].push(genid_received.substr(0,20));
        genid_alreadyselected[genid_generated]['protocol'] = idP;
        ready_to_generation(genid_received,genid_generated);
        if (fromBioBank == false){
            if (modified_elements[plate] == undefined){
                modified_elements[plate] = {};
            }
            modified_elements[plate][matrix_position] = 1;
        }
        //if (to_biobank[plate] == undefined){
        //    to_biobank[plate] = {};
        //}
        
        //struttura dati per biobank
        //to_biobank[plate][matrix_position]= {'iniQ':init_value, 'actualQ':init_value-1, 'aliquot':genid_received}
        console.log("struttura alla prima creazione")
        console.log(to_biobank)
    }else{
        genid_alreadyselected[genid_generated]['aliquots'].push(genid_received.substr(0,20));
    }
    console.log(to_generation.hasOwnProperty(genid_generated));
    if (to_generation.hasOwnProperty(genid_generated)){
        var insert = true;
        to_generation[genid_generated]['genid_source'].push(genid_received);
        for (var i=0; i < to_generation[genid_generated]['prot'].length; i++){
            if (to_generation[genid_generated]['prot'][i]['id'] == idP )
                insert = false;
        }
        if (insert)
            to_generation[genid_generated]['prot'].push({'id':idP, 'name':nameP, 'num_plates': 1, 'nickname': nickname, 'nickid':''});
    }else{
        to_generation[genid_generated] = {'genid_source':[], 'prot': []};
        to_generation[genid_generated]['genid_source'].push(genid_received);
        to_generation[genid_generated]['prot'].push({'id':idP, 'name':nameP, 'num_plates': 1, 'nickname': nickname, 'nickid':''});
    }
}

function ready_to_generation(genid_received, genid_generated) { 
    console.log('ready_to_generation');
    var cellline_to_generation = document.createElement("span");
    cellline_to_generation.setAttribute("id", genid_generated);
    cellline_to_generation.setAttribute("name", genid_received);
    cellline_to_generation.innerHTML = genid_generated+"</br>";
    var container = document.getElementById('cell_line_list_final');
    container.appendChild(cellline_to_generation);
    $('#button_generate_aliquots').show();//  css('display', 'block');
}

function searchCells(){
    console.log('searchCells');
    var name = $("#alias").val();
    var url = base_url + '/searchCells/?name=' + name;
    $.ajax({
        async:false,
        url: url,
        type: 'GET',
        success: function(response) {
            console.log(response);
            var len = $('#aliasList').dataTable().fnGetNodes().length;
            for (var i = 0; i < len; i++ ){
                $('#aliasList').dataTable().fnDeleteRow(0);
            }
            for (var i = 0; i < response.length; i++){
                console.log(response[i]);
                var id = response[i]['id'];
                var name = response[i]['name'];
                var match = "";
                for (var k = 0; k < response[i]['match'].length; k++){
                    if (match == "")
                        match = response[i]['match'][k]
                    else
                        match = match + ', ' + response[i]['match'][k]
                }
                console.log(id, match, name);
                $('#aliasList').dataTable().fnAddData([id, match, name]);
            }
            var input = oTableAlias.$("tr");
            $(input).click(function(){selectOneLine(this)});
        }
    });
}

function selectOneLine(row){
    console.log('selectOneLine');
    $(oTableAlias.fnSettings().aoData).each(function (){
        $(this.nTr).removeClass('row_selected');
    });
    $(row).toggleClass("row_selected");
    console.log(row);
    console.log(oTableAlias.fnGetPosition(row));
    console.log(oTableAlias.fnGetData( oTableAlias.fnGetPosition(row) ) );
    selectedAlias = [oTableAlias.fnGetData( oTableAlias.fnGetPosition(row),0 ), oTableAlias.fnGetData( oTableAlias.fnGetPosition(row),2 )];

}

function insertSelection(img){
    console.log('insertSelection');
    if (selectedAlias[0] != ""){
        //get selected alias
        console.log(img);
        console.log($(img));
        console.log($(img).parent());
        console.log($(img).parent().children());
        console.log($(img).parent().children()[1]);
        //insert selected alias in the input value
        $($(img).parent().children()[1]).val(selectedAlias[1]);
        //insert alias id hidden in an attr of input
        $($(img).parent().children()[1]).attr('aliasid', selectedAlias[0]);
    }else{
        alert("Warning: to use an official cell line name, first you have to select it from the table below.");
    }
}

function newAlias(){
    console.log('newAlias');
    var name = $("#alias").val();
    $.ajax({
        async:false,
        url: base_url + '/newCell/?name=' + name,
        type: 'GET',
        success: function(response) {
            console.log(response);
        }
    });
    searchCells();
}

function save(){
    console.log('save');
    var rows = document.getElementById("popup_list_body").childNodes;
    for (var row_index = 0; row_index < rows.length; row_index++) {
        var g_id = rows[row_index].cells[0].innerHTML;
        console.log( $(rows[row_index].cells[3]).children() );
        var nickname = $($(rows[row_index].cells[3]).children()[1]).val();
        var nickid = $($(rows[row_index].cells[3]).children()[1]).attr('aliasid');
        console.log( $(rows[row_index].cells[4]).children() );
        console.log( $(rows[row_index].cells[4]).children()[1] );
        console.log( $($(rows[row_index].cells[4]).children()[0]).children() );
        var numplates = $($($(rows[row_index].cells[4]).children()[0]).children()[0]).val();
        var pId = $($(rows[row_index].cells[2])).attr('pId');
        console.log(nickname, numplates, nickid, pId);
        for (var i = 0; i < to_generation[g_id]['prot'].length; i++){
            if (to_generation[g_id]['prot'][i]['id'] == pId){
                to_generation[g_id]['prot'][i]['num_plates'] = numplates;
                to_generation[g_id]['prot'][i]['nickname'] = nickname;
                to_generation[g_id]['prot'][i]['nickid'] = nickid;
            }
        }
    }
    console.log(to_generation);

    //TODO mandare anche svuotamento piastra

    console.log(base_url + '/generation/aliquots/');
    if (typeOperation == 'Generation'){
        console.log('generation');
        $.ajax({
            url: base_url + '/generation/aliquots/',
            type: 'POST',
            data: {'to_generation':JSON.stringify(to_generation),'to_biobank':JSON.stringify(to_biobank), 'typeOperation': typeOperation, 'reqId':reqId},
            dataType: 'text',
        });
    }else if (typeOperation == 'Thawing'){
        console.log('thawing');
        $.ajax({
            url: base_url + '/generation/aliquots/',
            type: 'POST',
            data: {'to_generation':JSON.stringify(to_generation),'to_biobank':JSON.stringify(to_biobank), 'typeOperation': typeOperation, 'reqId':reqId},
            dataType: 'text',
        });
    }
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
