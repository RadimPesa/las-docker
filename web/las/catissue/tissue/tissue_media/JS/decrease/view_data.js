var dataStruct = null;
var aprifiltro=false;

function submitSearch(){    
    var timer = setTimeout(function(){$("body").addClass("loading");},100);
    var url =  base_url + "/api/experiment/viewdata/"+tipofile+"/";
    var inputPar = $('.mdam-input');

    dataSub = {};

    for (var i=0; i<inputPar.length; i++){
        var templId = $(inputPar[i]).attr('template');
        var paramId = $(inputPar[i]).attr('param');
        if (!dataSub.hasOwnProperty(templId)){
            dataSub[templId] = {};
        }
        dataSub[templId][paramId] = $(inputPar[i]).boxlist("getValues");
    }
    if(tipofile=="None"){
    	//prendo gli esperimenti eventualmente impostati
    	var lisexp=$("#input_exp").boxlist("getValues");
    }
    //se sono in Symphogen imposto a priori che l'esperimento deve essere quello
    else{
    	var expe=$("#exp_name").val();
    	var lisexp=[expe];
    }
    //prendo gli operatori
    var lisoper=$("#input_oper").boxlist("getValues");
    //prendo le date
    var datadal=$("#datefrom").val();
	if (datadal==""){
		var datatot="";
	}
	else{
		var oper=$("#confrontodata option:selected").val();
		var datatot=oper+"_"+datadal;
	}
	
	var dataal=$("#dateto").val();
	if (dataal==""){
		dataal="";
	}
    jsonDatSub = {'search': dataSub, 'templates': templates, 'experiment': lisexp, 'operator': lisoper,'datatot':datatot,'dataal':dataal}
    
    //console.log(url)
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
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
}

function fillTable(dataJson){
    if (dataJson.length == 0){
    	$('#contresults').hide();
        alert('No data found');        
        return;
    }
    dataStruct = dataJson;
    var tab=$("#exp_fin").dataTable();
    tab.fnClearTable();
    var contatore=1;   
    for (var i=0;i<dataJson.length;i++){
    	var diz=dataJson[i];
    	var listatab=[String(contatore), diz["gen"],diz["barcode"],diz["availability"],diz["patient"],diz["informed"],diz["experiment"],diz["volume"],diz["operator"],diz["date"],diz["notes"] ];
    	//se ho dei file salvati per quell'esperimento
    	var html="";
    	if("file" in diz){
    		var listafile=diz["file"];
    		html+="<div style='margin-bottom:0.5em;'><input class='sel_all' type='checkbox' style='float:left;margin-top:0px;'><label class='label_sel' >All</label><br style='clear:both'></div>";
    		for (var j=0;j<listafile.length;j++){
    			html+="<div><input type='checkbox' class='check_file' style='float:left;margin-top:0px;'><a class='linkfile' path='"+diz["idaliq"]+"|"+listafile[j]["id"]+"'>"+listafile[j]["nome"]+"</a><br style='clear:left;'></div>";
    		}    		
    	}
    	listatab.push(html);
        tab.fnAddData(listatab);      
        contatore++;
    }    
    $('#contresults').show();
    
    //faccio in modo di far sentire il click anche se e' sul testo del checkbox
	tab.$(".linkfile").click(function(){
		var check=$(this).parent().children(":checkbox");
		if($(check).is(":checked")){
			$(check).removeAttr("checked");
		}
		else{
			$(check).attr("checked","checked");
		}
	});
	
	tab.$(".label_sel").click(function(){
		var check=$(this).parent().children(":checkbox");
		if($(check).is(":checked")){
			$(check).removeAttr("checked");
			$(check).parent().parent().find(".check_file").removeAttr("checked");
		}
		else{
			$(check).attr("checked","checked");
			$(check).parent().parent().find(".check_file").attr("checked","checked");
		}
	});
	
	tab.$(".sel_all").click(function(){
		if($(this).is(":checked")){			
			$(this).parent().parent().find(".check_file").attr("checked","checked");
		}
		else{
			$(this).parent().parent().find(".check_file").removeAttr("checked");
		}
	});
}

function createFrame(url,listNode){
	/* submit request to download the file */
    nIFrame = document.createElement('iframe');
    nIFrame.setAttribute( 'id', 'RemotingIFrame' );
    nIFrame.style.border='0px';
    nIFrame.style.width='0px';
    nIFrame.style.height='0px';
         
    document.body.appendChild( nIFrame );
    var nContentWindow = nIFrame.contentWindow;
    nContentWindow.document.open();
    nContentWindow.document.close();
     
    var nForm = nContentWindow.document.createElement( 'form' );
    nForm.setAttribute( 'method', 'post' );
    
    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'selectedNodes' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify(listNode);
     
    nForm.appendChild( nInput );

    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'dataStruct' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify(dataStruct);
     
    nForm.appendChild( nInput );
    
    nForm.setAttribute( 'action', url);
     
    /* Add the form and the iframe */
    nContentWindow.document.body.appendChild( nForm );
     
    /* Send the request */
    nForm.submit();
}

function downloadFiles(){
	var tab=$("#exp_fin").dataTable();
	//prende tutti gli a che vengono dopo un check selezionato
    var selectedNodes = tab.$(".check_file:checked").next("a");
    var listNode= [];
    for (var i= 0; i< selectedNodes.length; i++){
        listNode.push($(selectedNodes[i]).attr("path"));
    }
    if ( listNode.length == 0){
        alert("Please select at least a file");
        return;
    }
    else{
        downloadedSet = true;
        var url =  base_url + '/decrease/download/final/';
        createFrame(url,listNode);
   }
}

//autocompletamento per i campi su cui effettuare la ricerca. Ad es. genealogy, barcode, cod paziente...
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
	$('#templatetable').append("<tr></tr>");
    for (var i=0; i<templates.length; i++){
        for (var j=0; j<templates[i]['parameters'].length; j++){
            if (templates[i]['parameters'][j]['type'] != 7){ // exclude wg
            	var name=templates[i]['parameters'][j]['name'];
            	
            	if(name.substring(0, 9) === "Genealogy"){
            		var htmlCode =  "<td>"+ templates[i]['parameters'][j]['name'] +":<br> <input id='input"+ i.toString() + j.toString()+"' type='text' size='15' class='ui-autocomplete-input mdam-input' value='' autocomplete='off'  template='" + templates[i]['id'] +  "' param='"+ templates[i]['parameters'][j]['id'] +"' ></input> <button class='button add_btn' id='add_btnprot'>Add</button><button class='button' id='genfilter'>Extended filter</button> </td>";
            	}
            	else{
            		var htmlCode =  "<td>"+ templates[i]['parameters'][j]['name'] +":<br> <input id='input"+ i.toString() + j.toString()+"' type='text' size='15' class='ui-autocomplete-input mdam-input' value='' autocomplete='off'  template='" + templates[i]['id'] +  "' param='"+ templates[i]['parameters'][j]['id'] +"' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td>";
            	}
            	if(tipofile!='None'){
            		//sono nella schermata specifica per Symphogen in cui prendo solo i file RAS ed ECD, quindi non faccio vedere
            		//i filtri sul consenso e sul protocollo che tanto e' sempre Symphogen
            		if((name=="Informed consent")||(name=="Collection protocol")){
            			htmlCode="";
            		}
            	}
                $('#templatetable tr').append(htmlCode);
                $('#input' + i.toString() + j.toString() ).boxlist();
                if (templates[i]['parameters'][j]['type'] == 5){
                    setAutoComplete ($('#input' + i.toString() + j.toString() ), mdam_url + '/api/autocomplete/', templates[i]['parameters'][j]['api_id']);
                }
            }
        }
    }
    if(tipofile=='None'){
	    var codhtml="<td>Experiment type:<br> <input id='input_exp' type='text' size='15' class='ui-autocomplete-input' value='' autocomplete='off' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td>";
	    $('#templatetable tr').append(codhtml);
	    $("#input_exp" ).boxlist();
	    setAutoComplete ($('#input_exp'), mdam_url + '/api/autocomplete/', 34);
    }
    
    var codhtml="<td>Operator:<br> <input id='input_oper' type='text' size='15' class='ui-autocomplete-input' value='' autocomplete='off' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td>";
    $('#templatetable tr').append(codhtml);
    $("#input_oper" ).boxlist();
    //25 e' l'id nella tabella AutoCompleteAPI del MDAM per l'autocompletamento in base all'operatore
    setAutoComplete ($('#input_oper'), mdam_url + '/api/autocomplete/', 25);
    
    var codhtml="<td style='width:16em;'><label for='confrontodata'> From: </label><br><select id='confrontodata' style='float:left;' onchange='cambiaData()'><option value='>'> ≥ </option><option value='eq'> = </option>"+
    "<option value='<'> ≤ </option></select><input id='datefrom' type='text' style='float:left;' size='8' value=''><br style='clear:left;'><br>"+
    "<label style='display:block;' for='confrontodata2'> To: </label><select id='confrontodata2' style='float:left;'><option value='<'> ≤ </option>"+
    "</select><input id='dateto' type='text' style='float:left;' size='8' value=''></td>";
    $('#templatetable tr').append(codhtml);
    $("#datefrom,#dateto").datepicker({
		 dateFormat: 'yy-mm-dd'
	});
}

function cambiaData(){
	var operatore=$("#confrontodata option:selected").attr("value");
	if ((operatore=="=")||(operatore=="<")){
		//disabilito l'altro campo per la data
		$("#confrontodata2,#dateto").attr("disabled",true);
	}
	else{
		$("#confrontodata2,#dateto").attr("disabled",false);
	}
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
        width:900,
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

$(document).ready(function(){
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Files_deleted","aliquote_fin");
    	return;
	}
	//e' giusto che sia una variabile globale perche' serve in varie funzioni
	tipofile=$("#exp_type").val();
	
    createTemplateForm();

    downloadedSet = true;
    
    $("#submit").click(submitSearch);
    $("#download_file").click(downloadFiles);
    $("#genfilter").click(filtrogenid);
    
    var oTable = $("#exp_fin").dataTable( {
        "bProcessing": true,         
	    "bAutoWidth": false ,	    
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	    "aoColumns": [
          { "sTitle": "N" },
          { "sTitle": "GenealogyID" },
          { "sTitle": "Barcode" },
          { "sTitle": "Availability" },
          { "sTitle": "Patient code" },
          { "sTitle": "Informed consent" },          
          { "sTitle": "Experiment" },
          { "sTitle": "Used volume" },
          { "sTitle": "Operator" },
          { "sTitle": "Date" },
          { "sTitle": "Notes" },
          { "sTitle": "All <input id='sel_tutto' type='checkbox' >" },
        ],
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 11 ] }
        ], 
    });
    
    if(tipofile!="None"){
    	oTable.fnSetColumnVis( 3, false);
    	oTable.fnSetColumnVis( 5, false);
    	oTable.fnSetColumnVis( 6, false);
    	oTable.fnSetColumnVis( 7, false);
    	oTable.fnSetColumnVis( 10, false);
    }
    
    $("#sel_tutto").click(function() {
    	if ($(this).is(":checked")){
    		oTable.$(".check_file, .sel_all").attr("checked",true);
    	}
    	else{
    		oTable.$(".check_file, .sel_all").attr("checked",false);
    	}    	
    });
    
});
