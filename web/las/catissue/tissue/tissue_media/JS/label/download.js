var aprifiltro=false;

function search(){
    if (downloadedSet == false){
        $('#submitQuery').dialog({
            resizable: false,
            modal: true,
            width: 400,
            buttons: {
                "Yes": function() {
                    $( this ).dialog( "close" );
                    submitSearch();                    
                },
                "No": function() {
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
    var url =  base_url + '/api/label/getFiles/';
    $("#galleria").hide();
    var inputPar = $('.mdam-input');
    //rimetto a Select all il tasto per selezionare tutto
    $("#label_sel").text('Select all');
    $("#sel_tutto").attr("checked",false);
    
    dataSub = {};

    for (var i=0; i<inputPar.length; i++){
        var templId = $(inputPar[i]).attr('template');
        var paramId = $(inputPar[i]).attr('param');
        if (!dataSub.hasOwnProperty(templId)){
            dataSub[templId] = {};
        }
        dataSub[templId][paramId] = $(inputPar[i]).boxlist("getValues");
    }
    
    //prendo i protocolli di colorazione eventualmente impostati
    var lisprot=$("#input_prot").boxlist("getValues");
    jsonDatSub = {'search': dataSub, 'templates': templates, 'protocol': lisprot}
    
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
        htmlCode += " <div class='node' style='border-width:0.1em;border-color: black;'><span style='margin-left:2em;'>"+ dataJson[sample]['genid']  + " - " + dataJson[sample]['barcode']  + " - "+ dataJson[sample]['exec_date'] +"</span><p style='display:inline-block;margin:0px;float:right'><label>Select all</label><input style='float:right;' type='checkbox' class='pinToggles'></p></div>  ";
        //htmlCode += "<div class='accordionResults node'>";
        for (var run in dataJson[sample]['runs']){
        	//htmlCode+="<div class='node'><span style='margin-left:2em;'>" + dataJson[sample]['runs'][run]['exec_date'] + " " + dataJson[sample]['runs'][run]['notes'] + "</span><p style='display:inline-block;margin:0px;float:right'><label>Select all</label><input style='float:right;' type='checkbox' class='pinToggles'></p></div>";
            htmlCode += "  <div class='interna'>";
            for (var file in dataJson[sample]['runs'][run]['files']){
                htmlCode += "<p><input style='float:left;' type='checkbox' class='pinToggles leafNode'><a class='linkfile' val='" + dataJson[sample]['runs'][run]['files'][file]['link'] +"' path='" +  sample + "|" + run +"|" + file +"' >"+ dataJson[sample]['runs'][run]['files'][file]['name'] +"</a></p>"
            }
            //htmlCode += " </div> ";
        }
        htmlCode += " </div> ";
    }
    htmlCode += " </div> ";

    $('#results').empty();
    $('#results').append(htmlCode);
    initAccordion();
    $(".node,.interna,.accordionResults").css("height","");
    //$(".node,.interna,.accordionResults").click(function(){
    	//$(".node,.interna,.accordionResults").css("height","");
    //});
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
    var selectedNodes = $('#results').find('.leafNode:checked').next('a');
    var listNode= [];
    for (var i= 0; i< selectedNodes.length; i++){
        listNode.push($(selectedNodes[i]).attr('path'));
    }
    if ( listNode.length == 0){
        alert("Please select some file");
    }
    else{
        downloadedSet = true;
        var url =  base_url + '/label/download/final/';
        createFrame(url,listNode);
   }
}

function deleteFiles(){
    var selectedNodes = $('#results').find('.leafNode:checked').next('a');
    var listNode= [];
    for (var i= 0; i< selectedNodes.length; i++){
        listNode.push($(selectedNodes[i]).attr('path'));
    }
    if ( listNode.length == 0){
        alert("Please select some file");
    }
    else{
    	//devo fare una POST alla vista per cancellare effettivamente i file
    	var timer = setTimeout(function(){$("body").addClass("loading");},500);	    	
    	//comunico la struttura dati al server
    	var data = {
			salva:true,
			dati:JSON.stringify(listNode),
			daticampioni:JSON.stringify(dataStruct)
	    };
		var url=base_url+"/label/delete/filefinal/";
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
}

function viewGallery(){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	var selectedNodes = $('#results').find('.leafNode:checked').next('a');
	//se non e' stato selezionato niente, allora metto tutto
	if ( selectedNodes.length == 0){
    	selectedNodes = $(".leafNode").next("a");
    }
    var listNode= [];
    for (var i= 0; i< selectedNodes.length; i++){
        listNode.push($(selectedNodes[i]).attr('path'));
    }    
	var url =  base_url + '/label/view/gallery/';
	//comunico la struttura dati al server
	var data = {
			dataStruct:JSON.stringify(dataStruct),
			selectedNodes:JSON.stringify(listNode)	
    };
	$.post(url, data, function (result) {
    	if (result == "error") {
    		alert("Error");
    		clearTimeout(timer);
	    	$("body").removeClass("loading");
    		return;
    	}
    	var dizfile=$.parseJSON(result);
    	var html="";
    	//sono i 20 px iniziali a sx della prima foto
    	var largtot=20;
    	//gli id sono quelli delle aliquote
    	for (var id in dataStruct){
    		//recupero i nomi dei file
    		var lisruns=dataStruct[id]["runs"];
    		var trovato=false;
    		//kk sono i valori dei runs. In questa schermata c'e' sempre un run 
    		for(var kk in lisruns){
	    		var lisfile=lisruns[kk]["files"];
	    		//chiave e' l'id del labelfile
	    		for (var chiave in lisfile){
	    			var nomefile=lisfile[chiave]["name"];
	    			if (nomefile in dizfile){
			    		var idaliq=dizfile[nomefile]["id"];
			    		if(id==idaliq){
			    			trovato=true;
				    		var dimens=dizfile[nomefile]["dim"];
				    		var gen=dataStruct[idaliq]["genid"];
				    		var barc=dataStruct[idaliq]["barcode"];
				    		var lismarker=dizfile[nomefile]["marker"];
				    		var tecnica=dizfile[nomefile]["tecn"];
				    		var protocollo=dizfile[nomefile]["prot"];
				    		var strmarker="";
				    		for (var i=0;i<lismarker.length;i++){
				    			strmarker+="<b>"+lismarker[i]["tipo"]+"</b>: "+lismarker[i]["nome"]+"; ";
				    		}
				    		//tolgo il ; in fondo
				    		strmarker=strmarker.substring(0,strmarker.length-2);
				    		html+="<figure style='float:left;width:400px;height:200px;' ><a style='float:left;' href='"+media_url+"/tissue_media/temp/label/"+nomefile+"' itemprop='contentUrl' data-size='"+dimens+" '>"+
				    		"<img src='"+media_url+"/tissue_media/temp/label/"+nomefile+"' style='float:left;width:400px;height:200px;' itemprop='thumbnail' /></a>"+
				    		"<figcaption itemprop='caption description' style='float:left;margin-top:0.5em;'><b>"+nomefile+"</b><br>"+gen+"-"+barc+"<br>"+strmarker+
				    		"<br><b>Protocol:</b> "+protocollo+" <b>Technique:</b> "+tecnica+"</figcaption></figure>";
				    		//400px di foto e 40 di margine e 2 di linea verticale separatrice tra le foto
				    		largtot+=442;
			    		}
	    			}
		    	}
    		}
    		if(trovato){
    			html+="<div style='float:left;border-left: 2px solid black;height:290px; '></div>";
    		}
    	}
    	$("#galleria").empty();    	
    	$("#galleria").append(html);
    	$("#galleria").css("display","");
    	//tolgo l'ultimo div che rappresenta l'ultima riga verticale
    	$("#galleria div:last").remove();
    	$("#galleria").css("width",String(largtot)+"px");
    	//per fare in modo che quando compare la galleria con le foto piccole possa scorrerla con le frecce
    	$("#gall1").focus();
    	
    	initPhotoSwipeFromDOM('.my-gallery');
    	
    	clearTimeout(timer);
    	$("body").removeClass("loading");
    });
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
                    setAutoComplete ($('#input' + i.toString() + j.toString() ), mdam_url + '/api/autocomplete/', templates[i]['parameters'][j]['api_id']);
                }
            }
        }
    }
    var codhtml="<tr><td>Label protocol</td><td> <input id='input_prot' type='text' class='ui-autocomplete-input' value='' autocomplete='off' ></input> <button class='button add_btn' id='add_btnprot'>Add</button> </td></tr>";
    $('#templatetable').append(codhtml);
    $("#input_prot" ).boxlist();
}

var initPhotoSwipeFromDOM = function(gallerySelector) {

    // parse slide data (url, title, size ...) from DOM elements 
    // (children of gallerySelector)
    var parseThumbnailElements = function(el) {
        var thumbElements = el.childNodes,
            numNodes = thumbElements.length,
            items = [],
            figureEl,
            linkEl,
            size,
            item;
        console.log("thumbElements",thumbElements)
        console.log("numnodes",numNodes)
        for(var i = 0; i < numNodes; i++) {

            figureEl = thumbElements[i]; // <figure> element

            // include only element nodes e per evitare di considerare le div che ho messo tra le figure
            if((figureEl.nodeType !== 1)||(figureEl.tagName!="FIGURE")) {
                continue;
            }
            linkEl = figureEl.children[0]; // <a> element

            size = linkEl.getAttribute('data-size').split('x');

            // create slide object
            item = {
                src: linkEl.getAttribute('href'),
                w: parseInt(size[0], 10),
                h: parseInt(size[1], 10)
            };

            if(figureEl.children.length > 1) {
                // <figcaption> content
                item.title = figureEl.children[1].innerHTML; 
            }

            if(linkEl.children.length > 0) {
                // <img> thumbnail element, retrieving thumbnail url
                item.msrc = linkEl.children[0].getAttribute('src');
            }
            item.el = figureEl; // save link to element for getThumbBoundsFn
            items.push(item);
        }
        return items;
    };

    // find nearest parent element
    var closest = function closest(el, fn) {
        return el && ( fn(el) ? el : closest(el.parentNode, fn) );
    };

    // triggers when user clicks on thumbnail
    var onThumbnailsClick = function(e) {
        e = e || window.event;
        e.preventDefault ? e.preventDefault() : e.returnValue = false;

        var eTarget = e.target || e.srcElement;

        // find root element of slide
        var clickedListItem = closest(eTarget, function(el) {
            return (el.tagName && el.tagName.toUpperCase() === 'FIGURE');
        });
        console.log("clickedlistitem",clickedListItem)
        if(!clickedListItem) {
            return;
        }

        // find index of clicked item by looping through all child nodes
        // alternatively, you may define index via data- attribute
        var clickedGallery = clickedListItem.parentNode,
            childNodes = clickedListItem.parentNode.childNodes,
            numChildNodes = childNodes.length,
            nodeIndex = 0,
            index;

        for (var i = 0; i < numChildNodes; i++) {
        	//per evitare di conteggiare anche le div che ho messo tra le figure
            if((childNodes[i].nodeType !== 1)||(childNodes[i].tagName!="FIGURE")) { 
                continue; 
            }

            if(childNodes[i] === clickedListItem) {
                index = nodeIndex;
                break;
            }
            nodeIndex++;
        }
        if(index >= 0) {
            // open PhotoSwipe if valid index found
            openPhotoSwipe( index, clickedGallery );
        }
        return false;
    };

    // parse picture index and gallery index from URL (#&pid=1&gid=2)
    var photoswipeParseHash = function() {
        var hash = window.location.hash.substring(1),
        params = {};
        console.log("hash",hash)
        if(hash.length < 5) {
            return params;
        }

        var vars = hash.split('&');
        for (var i = 0; i < vars.length; i++) {
            if(!vars[i]) {
                continue;
            }
            var pair = vars[i].split('=');  
            if(pair.length < 2) {
                continue;
            }           
            params[pair[0]] = pair[1];
        }

        if(params.gid) {
            params.gid = parseInt(params.gid, 10);
        }
        console.log ("params",params)
        return params;
    };

    var openPhotoSwipe = function(index, galleryElement, disableAnimation, fromURL) {
        var pswpElement = document.querySelectorAll('.pswp')[0],
            gallery,
            options,
            items;
        console.log("pswpelement",pswpElement)
        items = parseThumbnailElements(galleryElement);

        // define options (if needed)
        options = {

            // define gallery index (for URL)
            galleryUID: galleryElement.getAttribute('data-pswp-uid'),

            getThumbBoundsFn: function(index) {
                // See Options -> getThumbBoundsFn section of documentation for more info
                var thumbnail = items[index].el.getElementsByTagName('img')[0], // find thumbnail
                    pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
                    rect = thumbnail.getBoundingClientRect(); 

                return {x:rect.left, y:rect.top + pageYScroll, w:rect.width};
            }

        };

        // PhotoSwipe opened from URL
        if(fromURL) {
            if(options.galleryPIDs) {
                // parse real index when custom PIDs are used 
                // http://photoswipe.com/documentation/faq.html#custom-pid-in-url
                for(var j = 0; j < items.length; j++) {
                    if(items[j].pid == index) {
                        options.index = j;
                        break;
                    }
                }
            } else {
                // in URL indexes start from 1
                options.index = parseInt(index, 10) - 1;
            }
        } else {
            options.index = parseInt(index, 10);
        }

        // exit if index not found
        if( isNaN(options.index) ) {
            return;
        }

        if(disableAnimation) {
            options.showAnimationDuration = 0;
        }

        // Pass data to PhotoSwipe and initialize it
        gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
        gallery.init();
    };

    // loop through all gallery elements and bind events
    var galleryElements = document.querySelectorAll( gallerySelector );
    console.log("galleryelem",galleryElements)
    for(var i = 0, l = galleryElements.length; i < l; i++) {
        galleryElements[i].setAttribute('data-pswp-uid', i+1);
        console.log(i)
        galleryElements[i].onclick = onThumbnailsClick;
    }

    // Parse URL and open gallery if it contains #&pid=3&gid=1
    var hashData = photoswipeParseHash();
    if(hashData.pid && hashData.gid) {
    	console.log("open")
        openPhotoSwipe( hashData.pid ,  galleryElements[ hashData.gid - 1 ], true, true );
    }
};

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

$(document).ready(function(){
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Files_deleted","aliquote_fin");
    	return;
	}
	
    createTemplateForm();
    
    $("#input_prot").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: base_url+'/api/label/protocol/autocomplete/',
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
    
    downloadedSet = true;
    dataStruct = null;
    $("#submit").click(search);
    
    $("#genfilter").click(filtrogenid);
    
    $("#sel_tutto").click(function() {
    	if ($(this).is(":checked")){
    		$(".pinToggles").attr("checked",true);
    		$("#results label,#label_sel").text('Unselect all');
    	}
    	else{
    		$(".pinToggles").attr("checked",false);
    		$("#results label,#label_sel").text('Select all');
    	}    	
    });
    
    
    var pswpElement =document.querySelectorAll('.pswp')[0];
    var items = [
                 {
                     src: '/tissue_media/img/logo-arancio.png',
                     w: 600,
                     h: 400
                 },
                 {
                     src: '/tissue_media/img/n_ok.png',
                     w: 1200,
                     h: 900
                 }
             ];
    var gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items);
    //gallery.init();
});

