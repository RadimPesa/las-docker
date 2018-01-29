var table_name = "#listTable";
implants = {} //struttura dati locale
mouseFlag = false;
aliquotFlag = false; //quando entrambi questi due flag sono settati a true, vengono inseriti i valori dell'impianto nella datatable
dictG = {};
implantCounter = 0;
barcodeP = ""; //per salvare temporaneamente la piastra caricata
site = "";
bad_quality_flag = false;
genID = ""; //variabile temporanea per salvare il genID generato dall'ultima aliquota selezionata dalla piastra
list_key = ['implant', 'implanttimestamp', 'implantuser', 'implDate', 'implNotes', 'implProt', 'dictG'];

jQuery(document).ready(function () {
    generate_table();
    checkStorage(list_key, "a");
    jQuery("#id_date").attr('disabled', true);
    
});

function restoreData(listKey, a){
    //restoring session data
    implants = JSON.parse(localStorage.getItem(listKey[0]));
    dictG = JSON.parse(localStorage.getItem('dictG'));
    jQuery("#id_date").val(localStorage.getItem('implDate'));
    jQuery("#id_notes").val(localStorage.getItem('implNotes'));
    jQuery("#id_scope_detail").val(localStorage.getItem('implProt'));
    var emptyFlag = false;
    for (barcodeP in implants){
        for (key in implants[barcodeP]){
            if (key !=  'emptyFlag'){
                for (var i = 0; i < implants[barcodeP][key]['listMice'].length; i++){
                    var barcodeM = implants[barcodeP][key]['listMice'][i]['barcode']
                    var newG = implants[barcodeP][key]['listMice'][i]['newGenID']
                    var tempCounter = implants[barcodeP][key]['listMice'][i]['implantCounter']
                    var badFlag = implants[barcodeP][key]['listMice'][i]['badflag']
                    var site = implants[barcodeP][key]['listMice'][i]['site']
                    if (tempCounter >= implantCounter)
                        implantCounter = tempCounter + 1;
                    jQuery(table_name).dataTable().fnAddData( [null, newG, tempCounter, barcodeM, site, badFlag, null, barcodeP, key ] );
                }
            }/*else{
                emptyFlag = implants[barcodeP][key];
            }*/
        }
    }
    jQuery("#start").children().attr('disabled',true);
    jQuery("#confirmI").attr("disabled",false);
    jQuery("#secondPhase").show();
    jQuery("#set").attr('value', "Edit");
    jQuery("#set").attr('typeAction', "e");
    jQuery("#set").attr('disabled', false);



}

function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    var oTable = jQuery(table_name).dataTable({
	    "bProcessing": true,
	     "aoColumns": [
                { 
                   "sTitle": null, 
                   "sClass": "control center", 
                   //"sDefaultContent": '<img src="' + base_url + '/xeno_media/img/admin/icon_deletelink.gif">'
                   "sDefaultContent": '<img src="/xeno_media/img/admin/icon_deletelink.gif">'
                },
                { "sTitle": "New GenID" },
                { "sTitle": "ID Operation" },
                { "sTitle": "Mouse Barcode" },
                { "sTitle": "Site" },
                { "sTitle": "Bad Flag" },
                { "sTitle": "Barcode" },
                { "sTitle": "Pos." },
                { "sTitle": "Plate" }                
            ],
        "bAutoWidth": false ,
        "aaSorting": [[2, 'desc']],
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] },
        ],
    });
    /* Add event listener to delete row  */
   jQuery(table_name+' tbody td img').live('click', function () {
        var id_gen = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[1]).text();
        var barcodeM = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[3]).text();
        var barcodeTube = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[6]).text();
        var barcodePlate = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[8]).text();
        var pos = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[7]).text();
        deleteRow(id_gen, barcodePlate, pos, barcodeM, barcodeTube);
        var nTr = jQuery(this).parents('tr')[0];
	    jQuery(table_name).dataTable().fnDeleteRow( nTr );
    } );
}

function deleteRow(id_gen, barcodePlate, pos, barcodeM, barcodeTube){
    console.log(barcodePlate, pos);
    var id = barcodeTube;
    console.log(jQuery("#vital button[barcode='"+id+"']").text())
    var qty = parseInt(jQuery("#vital button[barcode='"+id+"']").text());
    console.log(qty);
    if (qty >= 0){
        jQuery("#vital button[barcode='"+id+"']").text(qty + 1);
    }
    jQuery("#vital button[barcode='"+id+"']").attr('status', '0');
    console.log(dictG)
    console.log(id_gen)
    delete dictG[id_gen]
    //dictG[id_gen]['genID'] = dictG[id_gen]['genID'].replaceAt(0, "F");
    localStorage.setItem('dictG', JSON.stringify(dictG));
    //dictG[idGen][0] = replaceAt(dictG[id_gen][0], 0, 'F');
    console.log(dictG);
    
    if (Object.size(implants[barcodePlate]) == 2){ //2 perche' c'e' sia il dizionario sulle posizioni, sia per il flag emptyplate
        if (implants[barcodePlate][pos]['listMice'].length == 1){
            delete implants[barcodePlate];
            storageIt('implant', JSON.stringify(implants));
            return;
        }
    }
    var qty = parseInt(implants[barcodePlate][pos]['actualQ']);
    var startQ = parseInt(implants[barcodePlate][pos]['initQ']);
    console.log(qty)
    if (qty >= 0){
        if (startQ == qty + 1){
            delete implants[barcodePlate][pos];    
        }else{
            implants[barcodePlate][pos]['actualQ'] = qty + 1;
            if (implants[barcodePlate]['emptyFlag'] == true)
                implants[barcodePlate]['emptyFlag'] = false;
            for (var i=0; i < implants[barcodePlate][pos]['listMice'].length; i++){
                if (implants[barcodePlate][pos]['listMice'][i]['barcode'] == barcodeM){
                    implants[barcodePlate][pos]['listMice'].splice(i, 1);
                    return;
                }
            }
        }
    }
    else{
        for (var i=0; i < implants[barcodePlate][pos]['listMice'].length; i++){
            if (implants[barcodePlate][pos]['listMice'][i]['barcode'] == barcodeM){
                implants[barcodePlate][pos]['listMice'].splice(i, 1);
                return;
            }
        }
        if (implants[barcodePlate][pos]['listMice'].length == 0){
            delete implants[barcodePlate][pos];
        }
    }
    storageIt('implant', JSON.stringify(implants));
}

//mostra e nasconde la parte sotto della schermata
function checkSerie(){
    if (jQuery("#set").attr('typeAction') == 's'){
        jQuery("#start").children().attr('disabled',true);
        jQuery("#secondPhase").show();
        jQuery("#set").attr('value', "Edit");
        jQuery("#set").attr('typeAction', "e");
        jQuery("#set").attr('disabled', false);
        localStorage.setItem('implNotes', jQuery("#id_notes").val());
        localStorage.setItem('implDate', jQuery("#id_date").val());
        localStorage.setItem('implProt', jQuery("#id_scope_detail").val());
        
    }else if (jQuery("#set").attr('typeAction') == 'e'){
        jQuery("#start").children().attr('disabled',false);
        jQuery("#id_date").attr('disabled', true);
        jQuery("#secondPhase").hide();
        jQuery("#set").attr('value', "Set");
        jQuery("#set").attr('typeAction', "s");
    }
}

function loadPlate(){
    var barcode = jQuery("#barcodeP").val();
    //var typeC = jQuery('input:radio[name="choose_vital"]:checked').val();
    var url = base_url + "/api.explTable/" + barcode + "/VT/plate";
    jQuery.getJSON(url, function(transport){
        if (transport.data == 'err'){
            alert("Plate doesn't exist");
            //jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if (transport.data == '403'){
            window.location.href = "/forbidden";
        }else{
            console.log(transport.data);
            if (transport.data == 'errore'){
                alert("Warning: this plate doesn't exist.");
            }
            else if (transport.data == 'errore_aliq'){
                alert("Warning: this plate doesn't contain viable aliquots.");
            }
            else{
                barcodeP = barcode;
                jQuery("#vital" ).replaceWith(transport.data);
                jQuery("#vital button").attr('disabled',false);
                jQuery("#vital button").click(selectAliquot);  //---> azione associata al click sulla cella
                jQuery(jQuery('#vital tr')[0]).css('display','none');
                for (var i=0; i < jQuery("#vital button").length; i++){
                    jQuery(jQuery("#vital button")[i]).css('font-weight','bold');
                    if ( (jQuery(jQuery("#vital button")[i]).text() == '0') || (jQuery(jQuery("#vital button")[i]).text() == 'X') ){
                        jQuery(jQuery("#vital button")[i]).attr("disabled",true);
                        jQuery(jQuery("#vital button")[i]).attr("status",1);
                    }else{
                        jQuery(jQuery("#vital button")[i]).attr("status",0);
                    }
                }
            }
        }
        loadPreviousChange(barcodeP);
    });
}

function loadPreviousChange(barcodeP){
    if (implants[barcodeP]){
        if (implants[barcodeP]['emptyFlag'] == true){
            //svuota direttamente tutti i tubini
            jQuery("#vital button[status!= 1]").attr('status', '2');
            jQuery("#vital button[status!= 1]").text('0');
        }else{
            //aggiorna i tubini usati
            for (key in implants[barcodeP]){
                if (key != "emptyFlag"){
                    //var pos = key;
                    //console.log(key);
                    jQuery("#v-"+ key).text(implants[barcodeP][key]["actualQ"]);
                    if (implants[barcodeP][key]["actualQ"] == 0){
                        jQuery("#v-"+ key).attr('status', '2');
                    }
                }
            }
        }
    }
}


function selectAliquot(){//status usati: 0 -> aliquota disponibile; 1 -> cella della piastra vuota; 2 -> aliquota finita; 3 -> aliquota selezionata
    if (mouseFlag == true){
        var button = this;
    	var buttons = jQuery("#vital button");
    	for (var i=0; i < buttons.length; i++){
    	    if (jQuery(buttons[i]).attr('status') == '3'){
    	        jQuery(buttons[i]).attr('status', '0')
    	    }
    	}
        if (jQuery(button).attr('status') == '1')
            alert("This cell of the plate is empty.");
        if (jQuery(button).attr('status') == '2')
            alert("The aliquot in this cell is finished.");
        //se ho cliccato su una aliquota gia' cliccata, la deseleziona
        if (jQuery(button).attr("status") == '3'){
            jQuery(button).attr("status", '0');
        }
        if (jQuery(button).attr('status') == '0'){
            var site = jQuery("#id_site option:selected").attr('value');

            var barcode = jQuery("#selectedMouse").text();
            console.log(button);
    	    var idGen = jQuery(button).attr('gen');
    	    //var url = base_url +'/api.newGenID/' + idGen + '/' + listG;
    	    if (sizeDict(dictG) == 0)
    		    var url = base_url +'/api.newGenID/'// + idGen + '/' + JSON.stringify({}) + '/' + barcode  + '/' + site;
    	    else
    		    var url = base_url +'/api.newGenID/'// + idGen + '/' + JSON.stringify(dictG) + '/' + barcode  + '/' + site;
    	    var n = 0;
    	    jQuery.ajax({
    	        async:false,
    	        url: url,
    		    type: 'post',
                data: {'oldG':idGen, 'listG':JSON.stringify(dictG), 'barcode':barcode, 'site':site},
                datatype: 'json',
    		    success: function(transport) {
                    if (transport['status'] == 'err')
                        alert(transport['message']);
                    else{
        		        genID = transport['genID'];
        			    jQuery(button).attr('status', '3');
        			    aliquotFlag = true;
        		        checkForInsert();
                    }
    		    }
    	    });
        }
    }else{
        alert("First, you have to select the mouse.");
    }

}

//controlla se un topo e' gia' stato impiantato in questa sessione
function isNewMouse(barcode){
    var rows = jQuery("#listTable").dataTable().fnGetNodes();
    for (var i=0; i<rows.length; i++){
        // Get HTML of 3rd column (for example)
        if (barcode == jQuery(rows[i]).find("td:eq(3)").html())
            return false;
    }
    return true;
}

function isNewSite(barcode, site){
    var rows = jQuery("#listTable").dataTable().fnGetNodes();
    for (var i = 0; i < rows.length; i++){
        if ( barcode == jQuery(rows[i]).find("td:eq(3)").html() && site == jQuery(rows[i]).find("td:eq(4)").html() ) 
            return false;
    }
    return true;    
}

//per selezionare il mouse da impiantare
function selectMouse() {
	if(document.getElementById('id_barcode_of_mouse')){
		barcode = document.getElementById('id_barcode_of_mouse').value.toUpperCase();
		var e = document.getElementById("id_site");
		site = e.options[e.selectedIndex].text;
		bad_quality_flag = false;
		var chkbox = document.getElementById("id_bad_quality_flag");
		if(null != chkbox && true == chkbox.checked) {
			bad_quality_flag = true;
		}
		var url = base_url + "/api.status/" + barcode;
		jQuery.ajax({
			type: 'get',
			url:url,
			success: function(transport) {
                if ((transport == "newbarcode")||(transport=="otherwg")){
                    alert("The mouse " + barcode + " doesn't exist.");
                }else{
                    status = transport[0][barcode];
                    if (status != undefined){
                        for (genID in transport[0])
                            status = transport[0][genID];
                    }

                    //if (status == 'experimental' || status == 'transferred' ){
    				if (status == 'experimental' || status == 'transferred' || status == 'implanted'){
                        //if (isNewMouse(barcode)){
                        if (isNewSite(barcode, site)){
        			        jQuery("#selectedMouse").text(barcode);
                            jQuery("#selectedSite").text(site);
        			        document.getElementById('id_barcode_of_mouse').value = "";
        			        mouseFlag = true;
        			        checkForInsert();
                        }else
                            alert("You have already implanted this mouse in this site.");
                        //}else
                        //    alert("You have already implanted this mouse in this session.");
    				}else{
                        var s = "";
                        for (bioM in transport){
                            for (id in transport[bioM]){
                                s = transport[bioM][id];
                            }
                        }
    					alert("You can't implant this mouse; its actual status is " + s + ".");
                    }
                }
			}
		});
	}else{
		alert("You've insert a blank barcode.");	
	}
}

function checkForInsert(){
    if ( (mouseFlag == true) && (aliquotFlag == true) ){
        addRow();

        implantCounter++;
        mouseFlag = false;
        aliquotFlag = false;
        jQuery("#selectedMouse").text("");
        jQuery("#selectedSite").text("");
    }
    
}

function addRow(){
    //newG, contatore, barcodeM, site of implant, bad flag, barcodeP, position
    var barcode = jQuery("#selectedMouse").text();
    var tube = jQuery("#vital button[status=3]");
    var pos = jQuery(tube).attr('pos');
    console.log(pos)
    var barcodeTube = jQuery(tube).attr('barcode');
    jQuery(table_name).dataTable().fnAddData( [null, genID ,implantCounter, barcode, site,bad_quality_flag, barcodeTube, pos, barcodeP ] );
    dictG[genID] = {};
    //dictG[genID]['genID'] = 'T' + jQuery(tube).attr('gen'); //'T': flag impostato a true
    dictG[genID]['genID'] = jQuery(tube).attr('gen'); 
    dictG[genID]['barcode'] = barcode;
    localStorage.setItem('dictG', JSON.stringify(dictG));
    if (implants[barcodeP]){
        if (implants[barcodeP][pos]){
            //piastra e tubo gia' selezionati precedentemente
            implants[barcodeP][pos]['actualQ'] = parseInt(implants[barcodeP][pos]['actualQ']) - 1;
            implants[barcodeP][pos]['listMice'].push({'barcode': barcode, 'newGenID':genID, 'implantCounter':implantCounter, 'badflag':bad_quality_flag, 'site':site});
        }else{
            //piastra gia' usata ma tubo non ancora selezioanto in precedenza 
            implants[barcodeP][pos] = {};
            implants[barcodeP][pos]['initQ'] = jQuery(tube).text();
            implants[barcodeP][pos]['actualQ'] = parseInt(jQuery(tube).text()) - 1;
            implants[barcodeP][pos]['aliquot'] = jQuery(tube).attr('gen');
            implants[barcodeP][pos]['listMice'] = [];
            implants[barcodeP][pos]['listMice'].push({'barcode': barcode, 'newGenID':genID, 'implantCounter':implantCounter, 'badflag':bad_quality_flag, 'site':site});
        }
    }else{
        //piastra e tubo 'nuovi'
        implants[barcodeP] = {}
        implants[barcodeP]['emptyFlag'] = false;
        implants[barcodeP][pos] = {};
        implants[barcodeP][pos]['initQ'] = jQuery(tube).text();
        implants[barcodeP][pos]['actualQ'] = parseInt(jQuery(tube).text()) - 1;
        implants[barcodeP][pos]['aliquot'] = jQuery(tube).attr('gen');
        implants[barcodeP][pos]['listMice'] = [];
        implants[barcodeP][pos]['listMice'].push({'barcode': barcode, 'newGenID':genID, 'implantCounter':implantCounter, 'badflag':bad_quality_flag, 'site':site});
    }

    
    
    var qty = parseInt(jQuery("#vital button[status=3]").text());
    if (qty > 0){
        jQuery("#vital button[status=3]").text(qty-1);
        if (qty > 1)
            jQuery("#vital button[status=3]").attr('status', '0');
        else
            jQuery("#vital button[status=3]").attr('status', '2');
    }else{
        jQuery("#vital button[status=3]").attr('status', '0');
    }
    
    
    
    if (isFull(barcodeP) == true){
        console.log('IFFF');
        implants[barcodeP]["emptyFlag"] = true;
    }
    storageIt('implant', JSON.stringify(implants));
}

//controlla se la piastra si e' svuotata dopo l'ultimo prelievo di aliquota
function isFull(barcodeP){
    var tubes = jQuery("#vital button[status!=1]"); //prendo le piastre che in origine avevano almeno un'aliquota al loro interno
    for (var i = 0; i < tubes.length; i++){
        if ( jQuery(tubes[i]).attr('status') != '2'){
            return false; //piastra non vuota
        }
    }
    return true; //piastra vuota
}

//restituisce il barcode della provetta attualmente selezionata nella piastra
function getBarcode(){
    return jQuery('#vital button[status=3]').attr('barcode');
}

function checkKey(evt){
	var charCode = (evt.which) ? evt.which : event.keyCode
	if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
		selectMouse();
}

function checkKeyP(evt){
	var charCode = (evt.which) ? evt.which : event.keyCode
	if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
		loadPlate();
}

function checkPlates(){ //usata per verificare se, alla fine della serie di impianti, c'e' ancora del materiale nelle piastre
    var tempArray = [];
    for (barcodeP in implants){
        if (implants[barcodeP]['emptyFlag'] == false){
            tempArray.push(barcodeP);
        }
    }
    return tempArray;
}

function submitImplant(){
	jQuery("#confirmI").attr("disabled",true);
	var plates = checkPlates();
	console.log(plates);
	var implData = {};
	implData['prot'] = jQuery("#id_scope_detail").val(); //jQuery("#id_scope_detail option:selected").text();
	implData['notes'] =  jQuery("#id_notes").val()
	implData['date'] = jQuery("#id_date").val()
    if (plates.length > 0){
        for (var i = 0; i < plates.length; i++){
           var container = jQuery('#plateList');
           var html = '<input type="checkbox" id="'+plates[i]+'" value="'+plates[i]+'" /> <label for="'+plates[i]+'">'+plates[i]+'</label>';
           container.append(jQuery(html));
        }
        
        jQuery( "#dialog_empty" ).dialog({
            //autoOpen : false,
            resizable: false,
            height:200,
            width:340,
            modal: true,
            draggable :false,
            buttons: {
	            "Yes": function() {
                    jQuery( this ).dialog( "close" );
                    jQuery( "#dialog2" ).dialog({
                        //autoOpen : false,
                        resizable: false,
                        height:200,
                        width:340,
                        modal: true,
                        draggable :false,
                        buttons: {
	                        "Yes": function() {

                                //recuperare le piastre selezionate
                                jQuery("#plateList input")
                                
                                for (var i = 0; i < jQuery("#plateList input:checked").length;i++){
                                    //aggiornare emptyFlag nella struttura dati
                                    var bP = jQuery(jQuery("#plateList input:checked")[i]).val();
                                    console.log(bP);
                                    implants[bP]['emptyFlag'] = true;
                                }
                                
                                //send to server JSON.stringify(implants)
                                jQuery.ajax({
		                            //url: base_url + '/xenopatients/implants/start',
		                            url: base_url + '/implants/rGroups',
		                            type: 'POST',
		                            data: {'implants':JSON.stringify(implants), 'implData':JSON.stringify(implData)},
		                            dataType: 'text',
	                            })
		                        jQuery( this ).dialog( "close" );
	                        },
	                        "No": function() {
                                jQuery("#confirmI").attr("disabled",false);
		                        jQuery( this ).dialog( "close" );
	                        }
                        }
                    });
	            },
	            "No": function() {
		            empty = "0";
                    jQuery.ajax({
		                //url: base_url + '/xenopatients/implants/start',
		                url: base_url + '/implants/rGroups',
		                type: 'POST',
		                data: {'implants':JSON.stringify(implants), 'implData':JSON.stringify(implData)},
		                dataType: 'text',
	                })
		            jQuery( this ).dialog( "close" );
		            
	            }
            }
        });
    
    }
    else{
        //alert('No mouse implanted');
        jQuery("#confirmI").prop("disabled",false);
        
	    jQuery.ajax({
		    //url: base_url + '/xenopatients/implants/start',
		    url: base_url + '/implants/rGroups',
		    type: 'POST',
		    data: {'implants':JSON.stringify(implants), 'implData':JSON.stringify(implData)},
		    dataType: 'text',
	    }); 
        
	}



}
