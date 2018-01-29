var aprifiltro=false;

jQuery(document).ready(function(){
    createTemplateForm();
    downloadedSet = true;
    dataStruct = null;
    
    $("#input_label").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: base_url+'/api/labelexperiment/autocomplete/',
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function(data) {
                    response(data);
                }
            });
        },
    });
    $("#genfilter").click(filtrogenid);

});


function search(){
    if (downloadedSet == false){
        $('#submitQuery').dialog({
            resizable: false,
            modal: true,
            buttons: {
                "Yes": function() {
                    $( this ).dialog( "close" );
                    submitSearch();
                    
                },
                No: function() {
                    $( this ).dialog( "close" );
            }
        }
      });
    }
    else{
        submitSearch();
    }
}


function submitSearch(){        
    
    var timer = setTimeout(function(){$("body").addClass("loading");},100);
    var url =  base_url + '/api.loadResults';

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

    //prendo le label eventualmente scritte dall'utente
    var lislabel=$("#input_label").boxlist("getValues");
    jsonDatSub = {'search': dataSub, 'templates': templates, 'label':lislabel }
    
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
                loadAccordion(transport);
                
            },
            error: function(data) { 
                clearTimeout(timer);
                $("body").removeClass("loading");
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });

}


function loadAccordion(dataJson){
    if (Object.keys(dataJson).length === 0){
    	$('#contresults').hide();
        alert('No data found');
        return;
    }
    downloadedSet = false;
    dataStruct = dataJson;
    htmlCode = "<div class='accordionResults'> ";
    for (var sample in dataJson){
    	var label="";
    	if (dataJson[sample]["label"]!=""){
    		label=dataJson[sample]["label"]+" - ";
    	}
        htmlCode += " <div class='node'>"+label+ dataJson[sample]['genid']  + " - " + dataJson[sample]['barcode']  + " <p style='display:inline-block;margin:0px;float:right'><label>Select all</label><input style='float:right;' type='checkbox' class='pinToggles'></p></div> <div class='accordionResults node'> ";

        for (var run in dataJson[sample]['runs']){
            htmlCode += " <div class='node'>" + dataJson[sample]['runs'][run]['title'] + " - " + dataJson[sample]['runs'][run]['time_executed'] + "<p style='display:inline-block;margin:0px;float:right'><label>Select all</label><input style='float:right;' type='checkbox' class='pinToggles'></p></div> <div>";
            for (var file in dataJson[sample]['runs'][run]['files']){
                htmlCode += "<p><input style='float:left;' type='checkbox' class='pinToggles leafNode'><a class='linkfile' val='" + dataJson[sample]['runs'][run]['files'][file]['link'] +"' path='" +  sample + "|" + run +"|" + file +"' >"+ dataJson[sample]['runs'][run]['files'][file]['name'] +"</a></p>"
                //console.log(sample, run, file, dataJson[sample]['runs'][run]['files'][file])
            }
            htmlCode += " </div> ";
        }
        htmlCode += " </div> ";
    }
    htmlCode += " </div> ";

    $('#results').empty();
    $('#results').append(htmlCode);
    initAccordion();
    $('#contresults').show();

    //faccio in modo di far sentire il click anche se e' sul testo del checkbox
	$(".linkfile").click(function(){
		var check=$(this).parent().children(":checkbox");
		if($(check).is(":checked")){
			$(check).removeAttr("checked");
		}
		else{
			$(check).attr("checked","checked");
		}
	});
	
}


function initAccordion(){
    $(".accordionResults" ).accordion({
                collapsible: true,
                heightStyle: "content",
                active: false,
                //header: ".accheader"
            });

    $('.pinToggles').click(function(e) {
        if (!this.checked){
            if ($(this).hasClass('leafNode')){
                var node = $(this);
            }
            else{
                $(this).closest('div').next('div').find("input[type='checkbox']").prop('checked', this.checked);
                var node = $(this).closest('div');
            }
            recursiveCheck(node, this.checked);             
        }
        else{
            if ($(this).hasClass('leafNode') == false){
                $(this).closest('div').next('div').find("input[type='checkbox']").prop('checked', this.checked);
                $(this).prev('label').text('Unselect all');
                $(this).closest('div').next('div').find('label').text('Unselect all');
            }
        }
        e.stopPropagation();
    });
}

function recursiveCheck(el, checked){
    if (el.hasClass('leafNode')){
            var parent = $(el.closest(".node").children("[role='tab']")[0]);
            recursiveCheck(parent, checked);
    }
    else{
        el.find("input[type='checkbox']").prop('checked', checked);
        el.find('label').text('Select all');
        el.closest('div').next('div').find('label').text('Select all');
        var parent = el.parent().prev('.node');
        if (parent.length > 0){
            recursiveCheck( parent, checked);
        }
    }
   
}



function downloadFiles(){
    var selectedNodes = $('#results').find('.leafNode:checked').next('a')
    var listNode= [];
    for (var i= 0; i< selectedNodes.length; i++){
        listNode.push($(selectedNodes[i]).attr('path'));
    }
    if ( listNode.length == 0){
        alert('No file selected');
    }
    else{

        //console.log(listNode);
        downloadedSet = true;
        var url =  base_url + '/downloadResults';

        /* submit request do download the file */
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



function createTemplateForm(){
    //$('#templatediv');
    for (var i=0; i<templates.length; i++){
        for (var j=0; j<templates[i]['parameters'].length; j++){
            if (templates[i]['parameters'][j]['type'] != 7){ // exclude wg
            	var name=templates[i]['parameters'][j]['name'];
            	if(name.substring(0, 9) === "Genealogy"){
            		var htmlCode =  "<tr><td>"+ templates[i]['parameters'][j]['name'] +"</td><td> <input id='input"+ i.toString() + j.toString()+"' type='text' class='ui-autocomplete-input mdam-input' value='' autocomplete='off'  template='" + templates[i]['id'] +  "' param='"+ templates[i]['parameters'][j]['id'] +"' ></input> <button class='button add_btn' id='add_btnprot'>Add</button><br><button style='margin:0.3em 0 0.5em 0;' class='button' id='genfilter'>Extended filter</button> </td></tr>"
            	}
            	else{
            		var htmlCode =  "<tr><td>"+ templates[i]['parameters'][j]['name'] +"</td><td> <input id='input"+ i.toString() + j.toString()+"' type='text' class='ui-autocomplete-input mdam-input' value='' autocomplete='off'  template='" + templates[i]['id'] +  "' param='"+ templates[i]['parameters'][j]['id'] +"' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td></tr>"
            	}
                $('#templatetable').append(htmlCode);
                $('#input' + i.toString() + j.toString() ).boxlist();
                if (templates[i]['parameters'][j]['type'] == 5){
                    setAutoComplete ($('#input' + i.toString() + j.toString() ), mdam_url + 'api/autocomplete/', templates[i]['parameters'][j]['api_id']);
                }
            }
        }
    }
    var codhtml="<tr><td>Label</td><td> <input id='input_label' type='text' class='ui-autocomplete-input mdam-input' value='' autocomplete='off' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td></tr>";
    $('#templatetable').append(codhtml);
    $("#input_label" ).boxlist();
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
