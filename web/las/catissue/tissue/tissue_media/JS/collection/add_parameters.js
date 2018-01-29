var dizcoll={};
var aprifiltro=false;

//quando clicco sul tasto "Search collection"
function search(){        
    
    var timer = setTimeout(function(){$("body").addClass("loading");},100);
    var url =  base_url + "/api/getCollection/";

    var inputPar = $(".mdam-input");
    
    dataSub = {};
    //prendo i valori inseriti dall'utente negli input e faccio la API per avere le collezioni
    for (var i=0; i<inputPar.length; i++){
        var templId = $(inputPar[i]).attr('template');
        var paramId = $(inputPar[i]).attr('param');
        if (!dataSub.hasOwnProperty(templId)){
            dataSub[templId] = {};
        }
        dataSub[templId][paramId] = $(inputPar[i]).boxlist("getValues");
    }

    jsonDatSub = {'search': dataSub, 'templates': templates }
    jQuery.ajax({
        type: 'POST',
        url: url,
        async: true,
        data: JSON.stringify(jsonDatSub), 
        dataType: "json",
        success: function(transport) {
            //console.log(transport);
            clearTimeout(timer);
            $("body").removeClass("loading");
            fillTable(transport);
            
        },
        error: function(data) { 
            clearTimeout(timer);
            $("body").removeClass("loading");
            alert("Error! Please, try again.\n" + data.status, "Warning");
        }
    });
}

//funzione che gestisce l'apertura della pagina per inserire i parametri clinici
function apri_pagina_parametri(){
	var tumid=$(this).children().children("input.tumid").val();
	var caso=$(this).children(":nth-child(3)").text();
	if(flag.length==0){
		//se non c'e' l'input hidden vuol dire che sono nella schermata dei parametri clinici e non del fresh tissue
		//e quindi devo aprire la pagina dei parametri
		var url=base_url+"/collection/param/?reopen=Yes&tumor="+tumid+"&case="+caso;
		window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width="+screen.width+",height="+screen.height);
	}
	else{
		var ospedale=$(this).children().children("input.sourceid").val();
		var consenso=$(this).children(":nth-child(5)").text();
		var paz=$(this).children(":nth-child(6)").text();
		var prot=$(this).children().children("input.protocolid").val();
		//nelle vecchie collezioni storiche non c'e' il protocollo, ma io devo comunque passare qualcosa alla 
		//schermata dopo per fare in modo che mi riempia correttamente il menu' con gli ospedali.
		if (prot==""){
			prot="1";
		}
		window.location=base_url+"/collection/fresh/?reopen=Yes&tumor="+tumid+"&source="+ospedale+"&cons="+consenso+"&pat="+paz+"&prot="+prot+"&case="+caso;
	}
}

function fillTable(dataJson){    
	var tab=$("#coll_fin").dataTable();
    tab.fnClearTable();
    if (Object.keys(dataJson).length === 0){
        alert('No collections found');
        return;
    }
    var contatore=1;
    for (var sample in dataJson){
    	if(flag.length==0){
    		//se non c'e' l'input hidden vuol dire che sono nella schermata dei parametri clinici e non del fresh tissue
    		//e quindi devo mettere l'icona della matita nell'ultima colonna
    		tab.fnAddData( [String(contatore), dataJson[sample]["tum"]+"<input type='hidden' class='tumid' value='"+dataJson[sample]["tumid"]+"' >", dataJson[sample]["case"], dataJson[sample]["source"]+"<input type='hidden' class='sourceid' value='"+dataJson[sample]["sourceid"]+"' >", dataJson[sample]["informed"],dataJson[sample]["patient"],dataJson[sample]["protocol"]+"<input type='hidden' class='protocolid' value='"+dataJson[sample]["protocolid"]+"' >",null] );
        }
        else{
        	tab.fnAddData( [String(contatore), dataJson[sample]["tum"]+"<input type='hidden' class='tumid' value='"+dataJson[sample]["tumid"]+"' >", dataJson[sample]["case"], dataJson[sample]["source"]+"<input type='hidden' class='sourceid' value='"+dataJson[sample]["sourceid"]+"' >", dataJson[sample]["informed"],dataJson[sample]["patient"],dataJson[sample]["protocol"]+"<input type='hidden' class='protocolid' value='"+dataJson[sample]["protocolid"]+"' >"] );
        }        
        contatore++;
    }
    $('#contresults').show();
    tab.$("tr").click(apri_pagina_parametri);
    
    /* Add event listener for edit row  */
    tab.$("td span.ui-icon-pencil").click( function(event){
    	event.stopPropagation();
        var posriga = jQuery("#coll_fin").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var valoririga = jQuery("#coll_fin").dataTable().fnGetData(posriga[0]);
        var tumid= $($($(this).parents('tr')[0]).find("input.tumid")).val();
        //passo la riga
        editRow(valoririga,tumid,posriga[0]);
    });
}

function setAutoComplete (el, autocomplete_api_url, api_id){
    var url = autocomplete_api_url + "?id=" + api_id;
    $(el).autocomplete({
        source: (function(u) {
            return function(request, response) {
                $.ajax({
                    url: u,
                    dataType: "jsonp",
                    data: {
                        term: request.term
                    },
                    success: function(data) {
                        response(data)
                    }
                });
            }
        }) (url)
    });
}

//per popolare il fieldset a sinistra con gli input in cui scrivere i criteri per la ricerca
function createTemplateForm(){
    for (var i=0; i<templates.length; i++){
        for (var j=0; j<templates[i]['parameters'].length; j++){
            if (templates[i]['parameters'][j]['type'] != 7){ // exclude wg
            	var name=templates[i]['parameters'][j]['name'];
            	if(name.substring(0, 9) === "Genealogy"){
            		var htmlCode = "<tr><td>"+ templates[i]['parameters'][j]['name'] +"</td><td> <input id='input"+ i.toString() + j.toString()+"' type='text' class='ui-autocomplete-input mdam-input' value='' autocomplete='off'  template='" + templates[i]['id'] +  "' param='"+ templates[i]['parameters'][j]['id'] +"' ></input> <button class='button add_btn' id='add_btnprot'>Add</button><br><button style='margin:0.3em 0 0.5em 0;' class='button' id='genfilter'>Extended filter</button> </td></tr>";
            	}
            	else{
            		var htmlCode = "<tr><td>"+ templates[i]['parameters'][j]['name'] +"</td><td> <input id='input"+ i.toString() + j.toString()+"' type='text' class='ui-autocomplete-input mdam-input' value='' autocomplete='off'  template='" + templates[i]['id'] +  "' param='"+ templates[i]['parameters'][j]['id'] +"' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td></tr>";
            	}
            	$('#templatetable').append(htmlCode);
                $('#input' + i.toString() + j.toString() ).boxlist();
                if (templates[i]['parameters'][j]['type'] == 5){
                    setAutoComplete ($('#input' + i.toString() + j.toString() ), mdam_url + '/api/autocomplete/', templates[i]['parameters'][j]['api_id']);
                }
            }            
        }
    }
}

//fa comparire la dialog box e permette di salvare nuovi valori per il paziente e il consenso
function editRow(valoririga,tumid,posizioneriga){
	var paz=valoririga[5];
	var cons=valoririga[4];
	var caso=valoririga[2];
	if(paz==null){
		paz="";
	}
	if(cons==null){
		cons="";
	}
    jQuery("#dialogpaz").find("input[name=paz]").attr("value",paz);
    jQuery("#dialogpaz").find("input[name=cons]").attr("value",cons);
    
    jQuery( "#dialogpaz" ).dialog({
        resizable: false,                   
        width: 400,
        modal: true,
        draggable: true,
        buttons: {
            "Ok": function(){
                // prendo i valori
	            var paziente= jQuery("#dialogpaz").find('input[name=paz]').val();
	            var consenso= jQuery("#dialogpaz").find('input[name=cons]').val();
	            //aggiorno il dizionario
	            dizcoll[tumid+"|"+caso]={"paziente":paziente,"consenso":consenso};
	            // aggiorno la riga con i nuovi valori	
	            jQuery("#coll_fin").dataTable().fnUpdate(paziente,posizioneriga,5);
	            jQuery("#coll_fin").dataTable().fnUpdate(consenso,posizioneriga,4);
                jQuery(this).dialog("close");
                
            },
            "Cancel": function(){
		        jQuery(this).dialog("close");
	        }                                        
        }                      
    });    
}

function filtrogenid(){
	if(!aprifiltro){
		$("#fullgenid").boxlist({
	        bMultiValuedInput: true,
	        oBtnEl: $("#add_gid2"),
	        oContainerEl: $("#genidlist"),
	        fnEachParseInput: function(v) {
	            v = v.trim();
	            if (v.length == 0) {
	                return v;
	            } else if (v.length < 26) {
	                v = v + new Array(26 - v.length + 1).join("-");
	            } else if (v.length > 26) {
	                v = v.substr(0, 26);
	            }
	            return v.toUpperCase();
	        },
	        fnValidateInput: function(val) {
	            var ok;
	            console.log(val);
	            for (var t in genid) {
	                var fields = genid[t].fields;
	                ok = true;
	                for (var j = 0; j < fields.length && ok; ++j) {
	                    var f = fields[j];
	                    var x = val.substring(f.start, f.end + 1);
	                    if (x == (new Array(f.end-f.start+2).join("-")) ||
	                        x == (new Array(f.end-f.start+2).join("0")) ) {
	                        ok = true;
	                        //console.log(t, f.name, "--");
	                        continue;
	                    }
	                    switch (f.ftype) {
	                        case 1: // predefined list
                                    ok = f.values.indexOf(x) != -1;
	                            //e' per gestire le linee che hanno un contatore al posto del TUM e se non metto questo if
	                            //mi danno errore in caso scriva il loro gen per intero
	                            if(!(ok)&&(f.name=="Tissue type")){
	                            	// numeric
	                            	ok = /^[0-9]+$/.test(x);
	                            }
	                            break;
	                        case 2: // alphabetic
	                            ok = /^[a-zA-Z]+$/.test(x);
	                            break;
	                        case 3: // numeric
	                            ok = /^[0-9]+$/.test(x);
	                            break;
	                        case 4: // alphanumeric
	                            ok = /^[a-zA-Z0-9]+$/.test(x);
	                            break;
	                    }
	                    //console.log(t, f.name, ok?"OK":"error");
	                }
	                //if (ok && val.substr(f.end+1,26) == (new Array(26-f.end+1).join("-"))) break;
	                // if genid validated AND (last field reaches end of genealogy OR remaining characters are '-' or '0')
	                if (ok && (f.end == 25 || /^[\-0]+$/.test(val.substr(f.end+1,26)))) {
	                    console.log("Detected type:", t);
	                    break;
	                }
	
	            }
	            console.log("[validate genid]", ok);
	            return ok;
	        },
	
	        aoAltInput: [
	            {
	                oBtnEl: $("#add_gid"),
	                fnParseInput: genIdFromForm
	            }
	        ]
	    });
		aprifiltro=true;
	}

	$("#genidfile").change(function() {
        var r = new FileReader();
        r.onload = function(evt) {
            $("#fullgenid").val(evt.target.result);
            $("#add_gid2").click();
            $("#genidfrm")[0].reset();
        }
        r.readAsText($("#genidfile")[0].files[0]);
    });
	
	$("#selgenidtype").change(function() {
        var t = $(this).val();        
        try {
            var fields = genid[t].fields;
        }
        catch(err) {
            return;
        }
        $("table#genid th.field,table#genid td.field").remove();
        for (var j = 0; j < fields.length; ++j) {
            $('<th class="field">' + fields[j].name + '</th>').insertBefore("table#genid th.add");
            if (fields[j].ftype == 1) {
                var x = '<td class="field"><select class="genidpar" maxlength="' + (fields[j].end - fields[j].start + 1)+'">';
                x += '<option></option>';
                for (var k = 0; k < fields[j].values.length; ++k) {
                    x += '<option>' + fields[j].values[k] + '</option>';
                }
                x += '</select></td>';
            } else

            if (fields[j].ftype == 2 || fields[j].ftype == 3 || fields[j].ftype == 4) {
                var x = '<td class="field"><input type="text" class="genidpar" maxlength="' + (fields[j].end - fields[j].start + 1)+ '" onkeypress="validate3(event)"></td>';
            }
            $(x).insertBefore("table#genid td.add");
        }
    });
	//qui viene inizializzato il riquadro del genid con il filtro su "Aliquot"
    $("#selgenidtype").prop("selectedIndex", 0).change();
    
	jQuery("#dialog").dialog({
        resizable: false,
        height:500,
        width:930,
        modal: true,
        draggable :true,
        buttons: {
            "Ok": function() {
            	var listafiltrigen=$("#fullgenid").boxlist("getValues");
            	//prendo l'input vicino al tasto "extended filter" per il genid
            	var tasto=$("#genfilter").siblings(":button");
            	var input=$("#genfilter").siblings(":input.mdam-input");
            	for(var i=0;i<listafiltrigen.length;i++){
            		$(input).val(listafiltrigen[i]);
            		$(tasto).click();
            	}
                jQuery( this ).dialog( "close" );                
            },
            "Cancel": function() {
                jQuery( this ).dialog( "close" );
            }
        },
    });
}

jQuery(document).ready(function(){
	flag=$("#reopen");
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Collection_update","aliquote_fin");
	}
	else{
		//guardo se sono nella pagina dei parametri o nella pagina prima, quella in cui scegliere se fare una nuova 
		//collezione o assegnare a collezione esistente. Questo se uso questa schermata nel fresh tissue e non nell'
		//add clinical parameters
		var tabella=$("#templatetable");
		if(tabella.length!=0){
		    createTemplateForm();
		    //se non c'e' l'input hidden vuol dire che sono nella schermata dei parametri clinici e non del fresh tissue 
		    if(flag.length==0){
			    var oTable = $("#coll_fin").dataTable( {
			        "bProcessing": true,         
				    "bAutoWidth": false ,	    
				    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
				    "aoColumns": [
			          { "sTitle": "N" },
			          { "sTitle": "Tumor" },
			          { "sTitle": "Case" },
			          { "sTitle": "Source" },
			          { "sTitle": "Informed consent" },
			          { "sTitle": "Patient code" },
			          { "sTitle": "Protocol" },
			          { "sTitle": null, 
			            "sDefaultContent": "<span class ='ui-icon ui-icon-pencil'></span>",
			          },
			        ],
			    });
		    }
		    else{
		    	var oTable = $("#coll_fin").dataTable( {
			        "bProcessing": true,         
				    "bAutoWidth": false ,	    
				    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
				    "aoColumns": [
			          { "sTitle": "N" },
			          { "sTitle": "Tumor" },
			          { "sTitle": "Case" },
			          { "sTitle": "Source" },
			          { "sTitle": "Informed consent" },
			          { "sTitle": "Patient code" },
			          { "sTitle": "Protocol" },
			        ],
			    });
		    }
		}
	    
	    $("#submit").click(search);
	    $("#genfilter").click(filtrogenid);
	    //quando clicco sul pulsante save&finish
	    $("#conf_all").click(function(event){
	    	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	    	event.preventDefault();
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(dizcoll),		    		
		    };
			var url=base_url+"/parameters/save/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	$("#form_conf").append("<input type='hidden' name='final' />");
		    	$("#form_conf").submit();
		    });
		});
	}
});

