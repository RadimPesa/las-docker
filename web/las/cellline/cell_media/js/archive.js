aliquots = {}; modified_elements = {};
tissue = 'TUM'; idoperation = 0; barcodeLoaded = ""; typeASelected = ""; 
selectedLine = ["",""]; //genID linea e id evento archivio
selectedRow = null; //variabile per salvare la riga di datatable selezionata
initPlate = null

$(document).ready(function() {
	//per adesso impedisco di fare derivati da questa schermata
	$("#typeAliquot option[value=DNA]").hide();
	$("#typeAliquot option[value=RNA]").hide();
	$("#typeAliquot option[value=cDNA]").hide();
	$("#typeAliquot option[value=cRNA]").hide();
	$("#typeAliquot option[value=P]").hide();
	initData();
	$("#barcode").keypress(function(event){
	    if ( event.which == 13 ) {
	        event.preventDefault();
	        carica_piastra();
	    }
	});

	$("#typeAliquot").change(function(){
		//alert('change aliquot type');
		$("#divContainer table").replaceWith(initPlate);
		$('#barcode').val('');
	});

	oTableOutput = $('table#archived').dataTable( {
		"bProcessing": true,
		"aoColumns": [
				{ 
					"sTitle": null, 
					"sClass": "center", 
					"sDefaultContent": '<img src="/cell_media/img/admin/icon_deletelink.gif" onclick="deleteAliquotRow(this);">'
				},
				{ "sTitle": "ID Operation" },
				{ "sTitle": "Genealogy ID" },
				{ "sTitle": "Plate's Barcode" },
				{ "sTitle": "Position" },
				{ "sTitle": "Volume[ml]" },
				{ "sTitle": "Count[cell/ml]" },
			],
		"bAutoWidth": false ,
		"aaSorting": [[1, 'desc']],
		"aoColumnDefs": [
			{ "bSortable": false, "aTargets": [ 0 ] },
		],
	});
	oTableInput = $('table#toArchive').dataTable( {
		"bProcessing": true,
		"bAutoWidth": false ,
		"aaSorting": [[1, 'desc']],
		"aoColumnDefs": [
			{ "bVisible": false, "aTargets": [ 0 ] },
			{ "bSortable": false, "aTargets": [ 6 ] },
		],
	});
	$("table#toArchive tbody").click(function(event) {

		if ($(event.target).hasClass('ui-icon-trash')){
			return;
		}

		$(oTableInput.fnSettings().aoData).each(function (){
			$(this.nTr).removeClass('row_selected');
		});
		$(event.target.parentNode).addClass('row_selected');
		selectedRow = event.target.parentNode;
		refreshPlate(selectedRow);

	});

	$("table#toArchive span.ui-icon-trash").on('click', function(event){
		selectedRow = event.target.parentNode.parentNode;
		trashPlates(selectedRow);

	});

});

function initData(){
	initPlate = $("#divContainer table");
	$("#typeAliquot option").each( function () {
		var type = $(this).text();
		aliquots[type] = {};
	});
	
	$("#id_date").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	$("#id_date").datepicker('setDate', new Date());
}

function carica_piastra(){
    if ($("#barcode").val() == ""){
        alert("Insert plate barcode");
    }else{
        var radio=$('input:radio[name="choose"]:checked');
        if (radio.length==0){
            alert("Choose if you want to load a tube or a plate");
        }else{
            load_rna=true;
	        carica_provetta($("#typeAliquot").val());
        }
    }
}

function carica_provetta(typeP){
	console.log(typeP);
    var barcode = $("#barcode").val();
    var radio = $('input:radio[name="choose"]:checked').val();
    var url = base_url + "/api/archive_loadplate/" + barcode + "/" + typeP + "/" +radio + '/';
    console.log(url);
    $.ajax({
        url: url,
        type: 'get',
        success: function(response) {
        	var result = JSON.parse(response);
        	if (result['data'].substr(0,3) != 'err'){
            	$("#divContainer table").replaceWith(result['data']);
            	typeASelected = $("#typeAliquot").val();
            	barcodeLoaded = barcode;
            	//add click event
			    $('#divContainer table button').each (function() {
					$(this).click( function() {
						putInPlate(this);
					});
			    });
			    update_plate_values(result["diznick"]);
			    refreshPlate(selectedRow);
	        }else{
			    if(result['data']=="errore") {
				    alert("The plate doesn't exist.");
			    }
			    if(result['data']=="errore_piastra") {
				    alert("Plate aim is not working.");
			    }
			    if(result['data']=="errore_aliq") {
				    alert("Plate selected is not "+typeP+".");
			    }
			    if(result['data']=="errore_store") {
				    alert("Error while connecting with storag.e");
			    }
			    if(result['data']=="err_esistente") {
				    alert("Container already exists.");
			    }
	        }
        }
    });
}

function refreshPlate(row){
	//console.log(row);
	if (row == null)
		return;
	//enable/disable cells
	var index = oTableInput.fnGetPosition(row);
	selectedLine[0] = oTableInput.fnGetData( index, 1 );
	selectedLine[1] = oTableInput.fnGetData( index, 0 );
	console.log(selectedLine);
	//$("#divContainer table tr td button").attr('disabled','disabled');
	//$("#divContainer table tr td button:not([inputLine])").removeAttr('disabled');
	$("#divContainer table tr td button[used]").attr('disabled','disabled');
	$("#divContainer table tr td button[sel]").attr('disabled','disabled');
	//$("#divContainer table tr td button[inputLine='" + selectedLine[1] + "']").removeAttr('disabled');
	console.log("#divContainer table tr td button[inputLine='" + selectedLine[1] + "']");
}

function putInPlate(cell){
	console.log('putInPlate');
	if (selectedLine[0] == ""){
		alert("Warning: first, you have to select a cell line.");
	}else{
		var dd=$("#id_date").val().trim();
		if(dd==""){
			alert("Please insert archive date");
			return;
		}
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			alert("Incorrect format for archive date: it should be YYYY-MM-DD");
			return;
		}
		
        if (modified_elements[barcodeLoaded] == undefined){
            modified_elements[barcodeLoaded] = {};
        }
		var volume = $("#volume").val(); 
		var count = $("#conta").val(); 
		var pos = $(cell).attr('pos');

		var counter = countAliquots(aliquots, typeASelected, selectedLine[0], tissue, barcodeLoaded, pos, idoperation );
	    var url = base_url + '/api/newGenID/' + selectedLine[0] + '/' + typeASelected + '/' + counter + '/' + tissue +'/';
	    console.log(url);
		var regex=/^[0-9.]+$/;
	    if (volume == ""){
	    	volume = "-";
	    }else{
			if((!regex.test(volume))){
		        alert("You can only insert number. Please correct value for volume.");
		        return false;
		    }
	    }
	    if (count == ""){
	    	count = "-";
    	}else{
			if((!regex.test(count))){
		        alert("You can only insert number. Please correct value for count.");
		        return false;
		    }
	    }
	    $.ajax({
	        async:false,
	        url: url,
	        type: 'GET',
	        success: function(response) {
	            var newG = response;
	            oTableOutput.fnAddData([null, idoperation, newG, barcodeLoaded, pos, volume, count]);
	            saveInLocal(typeASelected, selectedLine[0], pos, barcodeLoaded, aliquots, newG, counter, tissue, selectedLine[1], volume, count )
	            var oldQty = parseInt($(cell).text());
	            $(cell).text(oldQty + 1);
	            //put inputLine class
	            $(cell).attr('inputLine', selectedLine[1]);
	            if(modified_elements[barcodeLoaded][pos] == undefined){
		            modified_elements[barcodeLoaded][pos] = {};
		            modified_elements[barcodeLoaded][pos]['placed'] = 1;
		            modified_elements[barcodeLoaded][pos]['inputLine'] = selectedLine[1];
		            $(cell).attr('disabled', true);
	                console.log("struttura a piastra gia usata posizione nuova")
	            }else{
	            	modified_elements[barcodeLoaded][pos]['placed'] += 1;
	            }
	            //disabilito la data per impedire all'utente di cambiarla ad ogni linea archiviata
	            $("#id_date").attr("disabled",true);
	        }
	    });
		idoperation++;
	}
}

function update_plate_values(diznick) {
    console.log('update_plate_values');
    $(".tooltip_em").remove();
    $('#divContainer button').each (function() {
        var matrix_position = $(this).attr("id").substring(2);
        var gen=$(this).attr("gen");
        if (gen == undefined && $(this).text() != 'X') {
            $(this).removeAttr("disabled");
            if (modified_elements.hasOwnProperty(barcodeLoaded)){
                if(modified_elements[barcodeLoaded].hasOwnProperty(matrix_position)){
                    //var valore = (this).innerHTML;
                    //var decrementa = valore - modified_elements[barcodeLoaded][matrix_position];
                    $(this).text(modified_elements[barcodeLoaded][matrix_position]['placed']);
                    $(this).attr('inputline', modified_elements[barcodeLoaded][matrix_position]['inputLine']);
                    $(this).attr('used', 'used');
                }
            }
        }
        else{
        	if(gen!=undefined){
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
	            $(this).attr("disabled",true);
        	}
        }
    });
}

function deleteAliquotRow(img){
	var genID = $($($($(img).parent()).parent()).children()[2]).text();
	var row = img.parentNode.parentNode;
	oTableOutput.fnDeleteRow(oTableOutput.fnGetPosition(row));
	var tempArray = deleteAliquot(genID, aliquots);
	var barcodeP = tempArray[0];
	var position = tempArray[1];
	console.log(barcodeP);
	console.log(position);
	delete modified_elements[barcodeP][position];
	if (barcodeP == barcodeLoaded){
		//remove class cell line
		$("#divContainer table tr td [pos='" + position + "']").removeAttr('inputLine');
		$("#divContainer table tr td [pos='" + position + "']").removeAttr('disabled');
		$("#divContainer table tr td [pos='" + position + "']").text('0');
	}
	//se non c'e' niente nel dizionario con le aliquote, allora riabilito la data
	nAl = 0
	for (var k in aliquots){ 
		nAl += Object.keys(aliquots[k]).length;
	}
	if(nAl == 0){		
        $("#id_date").attr("disabled",false);
	}
}

function saveSession(){
	$("#save").attr('disabled', 'disabled');
	nAl = 0
	for (var k in aliquots){ 
		nAl += Object.keys(aliquots[k]).length;
	}
	if (nAl > 0){
	    $.ajax({
	        url: base_url + '/archive/',
	        type: 'POST',
	        data: {'aliquots':JSON.stringify(aliquots),'date':$("#id_date").val().trim()},
	        dataType: 'text',
	    });
	}
	else{
		alert("Please archive at least a cell line");
		$("#save").removeAttr('disabled');
	}
}


function trashPlates(selectedRow){
	if (selectedRow == null)
		return;
	//enable/disable cells
	var index = oTableInput.fnGetPosition(selectedRow);
	var selectedEvent = oTableInput.fnGetData( index, 0 );
	var nPlatesToTrash = oTableInput.fnGetData( index, 2 );

	$("#trashCell").text(oTableInput.fnGetData( index, 1 ));

	$("#platesTrash").spinner({
		"min": 1,
		"max": nPlatesToTrash
	});
	$("#platesTrash").spinner("value", nPlatesToTrash);
	$('#trashdialog').dialog({
        autoOpen: false,
        modal: true,
        width: 500,
        resizable: false,
        buttons:
        [
            {
                text: "OK",
                click: function() {
                	var toTrash = $("#platesTrash").spinner("value");
                	console.log(selectedEvent, toTrash);
                	// TODO send to server and create a new eliminated_details event
                	// from server receive if I should delete the row or update the #plates value
                	console.log(nPlatesToTrash -toTrash);
                	var formData = new FormData($('#trashform')[0]);
                	formData.append("action", "trashCell");
                	formData.append("idEvent", selectedEvent);
                	formData.append("nTrash", toTrash);

					$.ajax({
	        			url: './',
	        			data: formData,
				        type: 'POST',				        
				        success: function(transport) {
            				data = JSON.parse(transport);
            				console.log(data);
            				if (nPlatesToTrash -toTrash > 0){
		                		oTableInput.fnUpdate(nPlatesToTrash -toTrash, selectedRow, 2);
		                	}
		                	else{
		                		oTableInput.fnDeleteRow(selectedRow);	
		                	}
		                },
		                error: function(data) {
				            alert(data.responseText, 'Error');
				        },
				        cache: false,
		                contentType: false,
		                processData: false
				    });


          	        $(this).dialog("close");
                }
            },
            {
                text: "Cancel",
                click: function() {
                    $(this).dialog("close");
                }
            }
        ]
     }).dialog("open");
    
}
