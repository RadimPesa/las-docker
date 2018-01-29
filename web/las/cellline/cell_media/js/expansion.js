selectedcell = "";
var somedid = 0;
var globalIndex = 0;
var generatedList = [];
var viewCells = [];
var protocol_infos_dictionary = {};

$(document).ready(function () {
    $(".fa").css('color','#254B70');
    $(".fa").css('cursor','pointer');
    $($(".fa")[1]).css('color','#A8B7C6');
    setViewCells('genID');
    order('asc', '', 'genID');
    if (forFile.length > 0){
        console.log(forFile);
        //scarica file e poi re-dirigi utente
        var bb = new BlobBuilder();
        bb.append(forFile.toString().split(',').join('\n'));
        var blob = bb.getBlob("application/xhtml+xml;charset=" + document.characterSet);
        saveAs(blob, "aliquots.txt");
        if (bbUrl != 'err')
            window.location.href = bbUrl;
    }
    for (var c in cellsDict){
        generatedList.push(cellsDict[c]['genID']);
    }
    //imposto subito un filtro sull'utente loggato se e' presente in lista
    var utente=$("#actual_username").val();
    $("#userFilter [value='"+utente+"']").attr("selected",true);
    //vedo se e' stato impostato l'utente
    var sel=$("#userFilter option:selected");
    if(($(sel).val()!="")&&($(sel).val()!=undefined)){
    	filterUser();
    }     
});

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

function validate(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    key = String.fromCharCode( key );
    var regex = /[0-9]|\./;
    if( !regex.test(key) ) {
        theEvent.returnValue = false;
        if(theEvent.preventDefault) theEvent.preventDefault();
        return false;
    }
    return true;
}

function showInfos(conf_id){
    var url = base_url + '/api/urlProtocolInfosGetter/' + conf_id + '/';
    $.ajax({
        url: url,
        type: 'get',
        success: function(response) {    
            var protocol_infos = JSON.parse(response);
            protocol_infos_dictionary[conf_id] = protocol_infos;
            put_infos(protocol_infos);
            $( "#dialog" ).dialog({
                resizable: false,
                height:600,
                width:680,
                modal: true,
                draggable :false,
                buttons: {
                    "Ok": function() {
                        jQuery(this).dialog( "close" );
                    }
                }
            });
        }
    });
}

function checkInsert(actualQ, otherInputList){
    console.log(otherInputList);
    var total = 0;
    for (var i = 0; i<otherInputList.length; i++){
        total += parseInt(otherInputList[i]);
    }
    console.log(total); 
    console.log(actualQ);
    if (total > actualQ)
        return false;
    return true;
}

function writeDict(obj, dictKey){
    //console.log(obj);
    //console.log(cellsDict);
    var value = jQuery(obj).val();
    var typeInput = jQuery(obj).attr('name');
    console.log(typeInput, value);
    var row = jQuery(document.getElementById("firstRow"+dictKey));
    console.log(row);
    var ie = document.getElementById("inputA"+dictKey).value;
    if (ie == "") ie = 0;
    var valList = [ document.getElementById("toArchive"+dictKey).value, document.getElementById("toTrash"+dictKey).value, 
                    document.getElementById("toExperiment"+dictKey).value, ie]
                    //document.getElementById("toReset"+dictKey).value
    console.log( $(obj).closest('td') );
    console.log( $(obj).closest('tbody'));
    console.log( $(obj).closest('tbody').closest('td').find('.toReset').length );
    var resetList = $(obj).closest('tbody').closest('td').find('.toReset');
    for (var i = 0; i < resetList.length; i++){
        console.log(resetList[i].value);
        valList.push(resetList[i].value);
    }
    if (checkInsert(parseInt(jQuery(jQuery(row).children()[5]).text()), valList)){
        if (typeInput.split('_').length > 1){
            var categoryInput = typeInput.split('_')[0]; var inputT = typeInput.split('_')[1];
            var index = cellsDict[dictKey]['mods']['expansion'].length - 1;
            //cellsDict[dictKey]['mods'][typeInput.split('|')[0]][typeInput.split('|')[1]] = value;
            console.log(typeInput);
            if ( cellsDict[dictKey]['mods'][categoryInput][index]['applied'] ){
                var temp = {}
                temp[inputT] = value; temp['applied'] = false;
                if (inputT != "reduction")
                    temp['reduction'] = 1;
                cellsDict[dictKey]['mods'][categoryInput].push(temp)
            }else{
                cellsDict[dictKey]['mods'][categoryInput][index][inputT] = value;    
            }
        }else{
            if ( cellsDict[dictKey]['mods'][typeInput][cellsDict[dictKey]['mods'][typeInput].length-1]['applied'] ){
                var temp = {}
                temp['amount'] = value; temp['applied'] = false;
                cellsDict[dictKey]['mods'][typeInput].push(temp)
            }else{
                cellsDict[dictKey]['mods'][typeInput][cellsDict[dictKey]['mods'][typeInput].length-1]['amount'] = value;    
            }
        }
        console.log(cellsDict);
    }else{
        //azzerare gli input appena inseriti
        if (typeInput.split('_').length > 1){
            var categoryInput = typeInput.split('_')[0]; var inputT = typeInput.split('_')[1]; 
            try{
                var index = cellsDict[dictKey]['mods']['expansion'].length - 1;
                if (cellsDict[dictKey]['mods']['expansion'][index]['applied'])  
                    index--;
                jQuery(obj).val(cellsDict[dictKey]['mods'][categoryInput][index][inputT]);
            }
            catch(err){
                var value = 0;
                if (inputT == "reduction")
                    value = 1;
                jQuery(obj).val(value);
            }
        }else
            jQuery(obj).val(cellsDict[dictKey]['mods'][typeInput]);
            try{
                var index = cellsDict[dictKey]['mods'][typeInput].length - 1;
                if (cellsDict[dictKey]['mods'][typeInput][index]['applied'])  
                    index--;
                jQuery(obj).val(cellsDict[dictKey]['mods'][typeInput][index]['amount']);
            }
            catch(err){
                jQuery(obj).val(0);
            }
        alert("Not enough plates for this cell line.");
    }
}


function writeDictSlot(obj, dictKey){
    //console.log(obj);
    //console.log(cellsDict);
    var idcc = $(obj).closest('tbody').find('.id_cc').text().trim();
    console.log('writeDictSlot');
    console.log(idcc);
    if (idcc != ""){
        var value = jQuery(obj).val();
        var typeInput = jQuery(obj).attr('name');
        console.log(typeInput, value);
        var row = jQuery(document.getElementById("firstRow"+dictKey));
        console.log(row);
        var ie = document.getElementById("inputA"+dictKey).value;
        if (ie == "") ie = 0;
        var valList = [ document.getElementById("toArchive"+dictKey).value, document.getElementById("toTrash"+dictKey).value, 
                        document.getElementById("toExperiment"+dictKey).value, ie]
                        //document.getElementById("toReset"+dictKey).value
        var resetList = $(obj).closest('tbody').closest('td').find('.toReset');
        for (var i = 0; i < resetList.length; i++){
            console.log(resetList[i].value);
            valList.push(resetList[i].value);
        }
        

        //recuperare indice protocollo relativo allo slot selezionato
        if (typeInput == 'toReset'){ // change media
            if (checkInsert(parseInt(jQuery(jQuery(row).children()[5]).text()), valList)){
                cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] = value;
            }else{
            //azzerare gli input appena inseriti
                $(obj).val(cellsDict[dictKey]['mods']['toReset']['outputs'][idcc]);
                alert("Not enough plates for this cell line.");
            }    

        }else{
            console.log( value,  cellsDict[dictKey]['mods']['expansion']['generic']['inputA'] , cellsDict[dictKey]['mods']['expansion']['generic']['reduction']  )
            if (value <= (cellsDict[dictKey]['mods']['expansion']['generic']['inputA'] * cellsDict[dictKey]['mods']['expansion']['generic']['reduction'])){
                cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] = value;
            }
            else{
                $(obj).val(cellsDict[dictKey]['mods']['expansion']['outputs'][idcc]);
                alert("Input and dilution factor should be increased.");
            }
        }

    }else{
        $(obj).val(0)
        alert('Please, first define the culture condition.', 'Warning');
    }
}

function writeDictGenericSlot(obj, dictKey){

    var value = jQuery(obj).val();
    var typeInput = jQuery(obj).attr('id');
    console.log(typeInput);    console.log(value);
    
    var row = jQuery(document.getElementById("firstRow"+dictKey));
    var ie = document.getElementById("inputA"+dictKey).value;
    if (ie == "") ie = 0;
    var valList = [ document.getElementById("toArchive"+dictKey).value, document.getElementById("toTrash"+dictKey).value, 
                    document.getElementById("toExperiment"+dictKey).value, ie]
    var resetList = $(obj).closest('tbody').closest('td').find('.toReset');
        for (var i = 0; i < resetList.length; i++){
            console.log(resetList[i].value);
            valList.push(resetList[i].value);
        }
    
    if (typeInput.substring(0, 5) == 'input'){
        if (checkInsert(parseInt(jQuery(jQuery(row).children()[5]).text()), valList)){
            cellsDict[dictKey]['mods']['expansion']['generic']['inputA'] = value;            
        }
        else{
            $(obj).val(cellsDict[dictKey]['mods']['expansion']['generic']['inputA']);
            alert("Not enough plates for this cell line.");
        }
    }else{
        cellsDict[dictKey]['mods']['expansion']['generic']['reduction'] = value;
    }   
}

var clickedSlot;
//apre una nuova finestra per la gestione delle culturing condition
function changecc(url, namecc, obj){
    //console.log(url);
    //console.log(namecc);
    //console.log(obj);
    clickedSlot = obj;
    var row = jQuery(obj).parents('.mainRow');
    //console.log(row);
    var dictKey = row.attr('dictKey');
    //console.log(dictKey);
    selectedcell = dictKey;
    console.log(namecc);
    window.open(url+"?namecc="+namecc,"_blank",'height=' + screen.height + 'width=' + screen.width+',left=100,top=0,screenX=0,screenY=0');
}

function checkForExpansion(dictKey){
    //var index = cellsDict[dictKey]['mods']['expansion'].length - 1;
    //console.log(cellsDict[dictKey]['mods']['expansion'][index]);
    if (parseInt(cellsDict[dictKey]['mods']['expansion']['generic']['inputA']) > 0 ){
        console.log(1);
        if (parseInt(cellsDict[dictKey]['mods']['expansion']['generic']['reduction']) >= 1){
            console.log(1);
            //var size = Object.size(myArray);
            console.log(Object.size(cellsDict[dictKey]['mods']['expansion']['outputs']));
            if (Object.size(cellsDict[dictKey]['mods']['expansion']['outputs']) > 0){
                console.log(1);
                var tot = 0;
                for (idcc in cellsDict[dictKey]['mods']['expansion']['outputs']){
                    if (parseInt( cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] ))
                        tot += parseInt( cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] );
                }
                if (tot > 0 )
                    return true;
            }
        }
    }else{
        console.log(1);
        if (parseInt(cellsDict[dictKey]['mods']['expansion']['generic']['inputA']) > 0 || cellsDict[dictKey]['mods']['expansion']['outputs'].length > 0){
            console.log(1);
            return false;
        }else{
            console.log(1);
            return true;
        }
    }
}

function checkForReset(dictKey){
    console.log(dictKey);
    //var index = cellsDict[dictKey]['mods']['toReset'].length - 1;
    //console.log(cellsDict[dictKey]['mods']['expansion'][index]);
    /*var tot = 0;
    for (idcc in cellsDict[dictKey]['mods']['toReset']['outputs']){
        tot += parseInt( cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] );
    }
    console.log(tot);
    if (tot > 0 ){
        /*console.log(1);
        if (cellsDict[dictKey]['mods']['new_cc'] != ""){
            console.log(1);
            return true;
        }
        
        return false;
    }else{*/
        return true;
    /*}else
        return false;*/
}

function check_cc(dictKey){
    console.log(checkForReset(dictKey));
    //console.log(checkForExpansion(dictKey));
    return true;
    if (checkForReset(dictKey) && checkForExpansion(dictKey))
        return true;
    return false;
}

function resetInput(dictKey){
    console.log('reset input');
    console.log(dictKey);
    document.getElementById("toTrash"+dictKey).value = 0;
    document.getElementById("toArchive"+dictKey).value = 0;
    document.getElementById("inputA"+dictKey).value = 0;
    //document.getElementById("outputA"+dictKey).value = 0;
    document.getElementById("toExperiment"+dictKey).value = 0;
    //document.getElementById("toReset"+dictKey).value = 0;
    document.getElementById("reduc"+dictKey).value = 1;
}


function tempTot(dictKey){
    var tot = 0;
    var indexR = cellsDict[dictKey]['mods']['toReset'].length - 1;
    var indexT = cellsDict[dictKey]['mods']['toTrash'].length - 1;
    var indexA = cellsDict[dictKey]['mods']['toArchive'].length - 1;
    var indexExpe = cellsDict[dictKey]['mods']['toExperiment'].length - 1;
    var indexExpa = cellsDict[dictKey]['mods']['expansion'].length - 1;
    if ( cellsDict[dictKey]['mods']['toTrash'][indexT]['applied'] == false){
        tot += parseInt(cellsDict[dictKey]['mods']['toTrash'][indexT]['amount']);
        //console.log(tot);
    }
    if ( cellsDict[dictKey]['mods']['toArchive'][indexA]['applied'] == false){
        tot += parseInt(cellsDict[dictKey]['mods']['toArchive'][indexA]['amount']);
        //console.log(tot);
    }
    if ( cellsDict[dictKey]['mods']['toExperiment'][indexExpe]['applied'] == false){
        tot += parseInt(cellsDict[dictKey]['mods']['toExperiment'][indexExpe]['amount']);
        //console.log(tot);
    }
    if ( cellsDict[dictKey]['mods']['expansion']['generic']['applied'] == false){
        tot += parseInt(cellsDict[dictKey]['mods']['expansion']['generic']['inputA']);
        //console.log(tot);
    }
    if ( cellsDict[dictKey]['mods']['toReset']['generic']['applied'] == false){
        for (idcc in cellsDict[dictKey]['mods']['toReset']['outputs']){ tot += parseInt( cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] ); }
        //tot += parseInt(cellsDict[dictKey]['mods']['toReset']['generic']['amount']);
        console.log(tot);
    }
    return parseInt(tot);
}

//visualizza all'utente nella tabella le modifiche applicate alla riga in questione
function applyActions(dictKey){
    console.log('lastRow'+dictKey);
    var r = document.getElementById("firstRow"+dictKey);  //uso questo e non jQuery per permettermi i caratteri speciali in dictKey
    var row = jQuery(r);
    var r = document.getElementById('lastRow'+dictKey); 
    var lastRow = jQuery(r);
    //console.log(parseInt(cellsDict[dictKey]['mods']['toTrash'])+parseInt(cellsDict[dictKey]['mods']['toArchive'])+parseInt(cellsDict[dictKey]['mods']['toExperiment'])+parseInt(cellsDict[dictKey]['mods']['expansion']['inputA']));
    var initQ = parseInt( $($(row).children()[5]).text() );
    var indexR = cellsDict[dictKey]['mods']['toReset']['outputs'].length - 1;
    var indexT = cellsDict[dictKey]['mods']['toTrash'].length - 1;
    var indexA = cellsDict[dictKey]['mods']['toArchive'].length - 1;
    var indexExpe = cellsDict[dictKey]['mods']['toExperiment'].length - 1;
    var indexExpa = cellsDict[dictKey]['mods']['expansion']['outputs'].length - 1;

    console.log(initQ);
    console.log(tempTot(dictKey));
    if (initQ >= tempTot(dictKey) ){
        //console.log(check_cc(dictKey));
        if (check_cc(dictKey)){
            resetInput(dictKey);
            //reset = change media
            
            console.log('###############################');
            //if (!cellsDict[dictKey]['mods']['toReset'][indexR]['applied'] ){
            console.log(cellsDict[dictKey]['mods']['toReset']['generic']['applied']);
            if (!cellsDict[dictKey]['mods']['toReset']['generic']['applied'] ){
                var tot = 0;
                for (idcc in cellsDict[dictKey]['mods']['toReset']['outputs']){
                    console.log(idcc, parseInt( cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] ));
                    tot += parseInt( cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] ); 
                }

                //if (parseInt(cellsDict[dictKey]['mods']['toReset'][indexR]['amount']) > 0){
                console.log(initQ, tot, initQ-tot);
                if (tot > 0 ){
                    //var newQ = initQ - parseInt(cellsDict[dictKey]['mods']['toReset'][indexR]['amount']);
                    console.log('----------reset');
                    var newQ = initQ - tot;
                    cellsDict[dictKey]['mods']['toReset']['generic']['applied'] = true;
                    cellsDict[dictKey]['mods']['toReset']['generic']['toSave'] = true;
                    jQuery(jQuery(row).children()[5]).text(newQ);
                    initQ = newQ;

                    var genID =  cellsDict[dictKey]['genID'];
                    //var protocol =  document.getElementById("changedcc"+dictKey).innerText;
                    var date = 'today';
                    var plateType = document.getElementById("typePlate"+dictKey).innerText;

                    var typeInput = "toReset";
                    //cellsDict[dictKey]['mods'][typeInput][indexR]['cc'] = protocol;
                    var nick = cellsDict[dictKey]['nickname']
                    //UNA RIGA PER OGNI RESET
                    for (idcc in cellsDict[dictKey]['mods']['toReset']['outputs']){ 
                        var protocol = infocc[idcc]['name'];
                        var nPlates = cellsDict[dictKey]['mods']['toReset']['outputs'][idcc];
                        console.log(nick); console.log(genID);
                        if (nPlates > 0){
                        	var par=$(".slot"+dictKey).find("p:contains('"+protocol+"')");
                            var tipopias =$(par).siblings(".typePlate").text();
                            if(tipopias!=""){
                            	//vuol dire che ho cambiato le condizioni di coltura
                            	plateType = tipopias;
                            }
                        	
                            var newRow = $(addRow(nick, genID, protocol, date, plateType, nPlates, typeInput, dictKey, indexR, idcc));
                            console.log(genID);
                            console.log(protocol);
                            console.log(date);
                            console.log(plateType);
                            console.log(nPlates);
                            jQuery(lastRow).after(newRow);
                            jQuery('#table_exp tr.newRow input,select,textarea').attr('disabled','disabled');
                            jQuery('#table_exp tr.newRowHead input,select,textarea').attr('disabled','disabled');
                            jQuery('.deleteButtons').removeAttr('disabled');
                            somedid +=1;
                        }
                    }
                    //somedid -= 1;

                }
            }
            if (!cellsDict[dictKey]['mods']['toTrash'][indexT]['applied'] ){
                if (parseInt(cellsDict[dictKey]['mods']['toTrash'][indexT]['amount']) > 0){
                    var newQ = initQ - parseInt(cellsDict[dictKey]['mods']['toTrash'][indexT]['amount']);
                    cellsDict[dictKey]['mods']['toTrash'][indexT]['applied'] = true;
                    jQuery(jQuery(row).children()[5]).text(newQ);
                    initQ = newQ;
                    somedid += 1;
                }
            }
            if (!cellsDict[dictKey]['mods']['toArchive'][indexA]['applied'] ){
                if (parseInt(cellsDict[dictKey]['mods']['toArchive'][indexA]['amount']) > 0){
                    var newQ = initQ - parseInt(cellsDict[dictKey]['mods']['toArchive'][indexA]['amount']);
                    cellsDict[dictKey]['mods']['toArchive'][indexA]['applied'] = true;
                    jQuery(jQuery(row).children()[5]).text(newQ);
                    initQ = newQ;
                    somedid += 1;
                }
            }       
            if (!cellsDict[dictKey]['mods']['toExperiment'][indexExpe]['applied'] ){
                if (parseInt(cellsDict[dictKey]['mods']['toExperiment'][indexExpe]['amount']) > 0){
                    var newQ = initQ - parseInt(cellsDict[dictKey]['mods']['toExperiment'][indexExpe]['amount']);
                    cellsDict[dictKey]['mods']['toExperiment'][indexExpe]['applied'] = true;
                    jQuery(jQuery(row).children()[5]).text(newQ);
                    initQ = newQ;
                    somedid += 1;
                }
            }
            //if (!cellsDict[dictKey]['mods']['expansion'][indexExpa]['applied'] ){
            if (!cellsDict[dictKey]['mods']['expansion']['generic']['applied'] ){

                var totOutputs = 0;
                for (idcc in cellsDict[dictKey]['mods']['expansion']['outputs']){ 
                    if (parseInt( cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] ))
                        totOutputs += parseInt( cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] ); 
                }
                
                //var output = parseInt(cellsDict[dictKey]['mods']['expansion'][indexExpa]['outputA'])
                var input = parseInt(cellsDict[dictKey]['mods']['expansion']['generic']['inputA'])
                var reduction = parseInt(cellsDict[dictKey]['mods']['expansion']['generic']['reduction'])
                console.log(totOutputs); console.log(input); console.log(reduction);

                if ( ( totOutputs> 0) && (input > 0) && (reduction > 0) ){
                    /*console.log(output);
                    console.log(input);
                    console.log(reduction);
                    console.log(input * reduction * (1/1));*/
                    if(totOutputs <= input*reduction*(1/1) ){
                        console.log(dictKey);
                        //console.log(cellsDict[dictKey]['mods']['expansion'][indexExpa]['inputA']);
                        console.log(initQ);
                        var newQ = initQ - input;
                        cellsDict[dictKey]['mods']['expansion']['generic']['applied'] = true;
                        cellsDict[dictKey]['mods']['expansion']['generic']['toSave'] = true;
                        initQ = newQ;
                        console.log(newQ);
                        jQuery(jQuery(row).children()[5]).text(newQ);
                        //var cc_id = cellsDict[dictKey]['mods']['new_ccID'];
                        console.log(dictKey);
                        var oldG = cellsDict[dictKey]['genID'];
                        for (idcc in cellsDict[dictKey]['mods']['expansion']['outputs']){ 
                            if ( !/genid/.test(idcc) ){
                                if ( parseInt(cellsDict[dictKey]['mods']['expansion']['outputs'][idcc]) > 0){
                                    var url = base_url +'/api/expansion_genID/'// + oldG + '/' + idcc + '/';
                                    var data_to_send = {'oldG':oldG, 'id_cc':idcc, 'generatedList':JSON.stringify(generatedList)};
                                    console.log(url);
                                    jQuery.ajax({
                                        async:false,
                                        url: url,
                                        type: 'POST',
                                        data: data_to_send,
                                        dataType: 'json',
                                        success: function(transport) {
                                            console.log('success ajax');
                                            cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] = 0;
                                            var genID =  transport;
                                            console.log(idcc); console.log(infocc);
                                            var protocol = infocc[idcc]['name'];
                                            var date = 'today';                                            
                                            var par=$(".slot"+dictKey).find("p:contains('"+protocol+"')");
                                            var plateType =$(par).siblings(".typePlate").text();
                                            if(plateType==""){
                                            	//vuol dire che non ho cambiato le condizioni di coltura
                                            	plateType = document.getElementById("typePlate"+dictKey).innerText;
                                            }
                                            var nPlates = parseInt(cellsDict[dictKey]['mods']['expansion']['outputs'][idcc]);
                                            cellsDict[dictKey]['mods']['expansion']['outputs'][idcc + 'genid'] = genID;
                                            generatedList.push(genID);
                                            //cellsDict[dictKey]['mods']['expansion'][indexExpa]['cc'] = protocol;
                                            var nick = cellsDict[dictKey]['nickname']
                                            console.log('addrow');
                                            var newRow = jQuery(addRow(nick, genID, protocol, date, plateType, nPlates, 'expansion',dictKey, indexExpa, idcc));
                                            //cellsDict[dictKey]['mods']['expansion'][indexExpa]['rowID'] = globalIndex;
                                            console.log(genID);
                                            console.log(plateType);
                                            jQuery(lastRow).after(newRow);
                                            jQuery('#table_exp tr.newRow input,select,textarea').attr('disabled','disabled');
                                            jQuery('#table_exp tr.newRowHead input,select,textarea').attr('disabled','disabled');
                                            jQuery('.deleteButtons').removeAttr('disabled');
                                            somedid += 1;
                                        }
                                    });
                                }
                            }
                        }
                    }else{
                        alert("Expansion: check the value of input, dilution and/or output.");
                    }
                }
            }
            //guardo se per caso e' stata pianificata o tolta un'azione
            //cellsDict[dictKey]["plan"][tipoplan]["toSave"]=true;
            var dictazioni=cellsDict[dictKey]["plan"];
            for (var azione in dictazioni){
            	var check=$("#tab_plan"+dictKey).find("input[key='"+azione+"']");
            	var azionepassata=cellsDict[dictKey]["plan"][azione]["now"];
            	//se adesso l'ho selezionata e prima non lo era, allora devo salvare che ho fatto qualcosa
            	if (($(check).is(':checked'))&&(azionepassata==false)) {
            		cellsDict[dictKey]["plan"][azione]["toSave"]=true;
            		somedid += 1;
            	}
            	//se adesso l'ho deselezionata e prima era selezionata, allora devo salvare che ho fatto qualcosa
            	else if (!($(check).is(':checked'))&&(azionepassata==true)){
            		cellsDict[dictKey]["plan"][azione]["toSave"]=false;
            		somedid += 1;
            	}
            	//vuol dire che sto cambiando nella schermata aperta i check che ho messo prima. Cioe' se deseleziono un'azione che ho
            	//selezionato poco prima, oppure se riseleziono un'azione che avevo deselezionato poco prima nella stessa sessione
            	else{
            		//tolgo la chiave toSave
            		delete cellsDict[dictKey]["plan"][azione]["toSave"];
            	}
            }           
        } else{
            alert("Expansion/change media: fill all inputs. (Have you selected the culture condition?)");
        }
    }else{
        alert("Not enough plates for this cell line.");
    }
    console.log(cellsDict);
}

function previousInsert(outputA, inputA, reduction, genID, protocol, dictKey, type){
    console.log('pi');
    //test also on 'toSave'
    console.log(outputA);console.log(inputA);console.log(reduction);console.log(genID);console.log(protocol);console.log(type);
    if (type =='expansion'){
        for (var i=0; i < cellsDict[dictKey]['mods']['expansion'].length; i++){
            if ( cellsDict[dictKey]['mods']['expansion'][i]['reduction'] == reduction &&
                 cellsDict[dictKey]['mods']['expansion'][i]['newGenID'] == genID &&
                 cellsDict[dictKey]['mods']['expansion'][i]['cc'] == protocol &&
                 cellsDict[dictKey]['mods']['expansion'][i]['toSave'] == true &&
                 (1/1) == (1/1) ) 
                return i;
        }
        return -1;
    }
    if (type == 'reset'){
        for (var i=0; i < cellsDict[dictKey]['mods']['toReset'].length; i++){
            if ( cellsDict[dictKey]['mods']['toReset'][i]['cc'] == protocol &&
                 cellsDict[dictKey]['mods']['toReset'][i]['toSave'] == true ) 
                return i;
        }
        return -1;
    }
}

function addRow(nick, genID, protocol, date, plateType, nPlates, typeInput, dictKey, arrayIndex, idcc){
    console.log(dictKey);
    //var index = cellsDict[dictKey]['mods'][typeInput].length - 1;
    //console.log(index);
    if (typeInput == 'expansion' || typeInput == 'toReset')
        cellsDict[dictKey]['mods'][typeInput]['generic']['rowID'] = globalIndex;
    else
        cellsDict[dictKey]['mods'][typeInput][arrayIndex]['rowID'] = globalIndex;
    console.log('ADDING ROW');
    //console.log(cellsDict[dictKey]['mods'][typeInput][arrayIndex]['rowID']);
    var rowKey = dictKey + globalIndex;
    console.log(rowKey);
    console.log(globalIndex);
    //console.log(cellsDict[dictKey]['mods'][typeInput][arrayIndex]['rowID']);
    globalIndex++;
    //console.log(cellsDict[dictKey]['mods'][typeInput][arrayIndex]['rowID']);
    console.log('------------------------------------------');

    var dictKeyV = "'" + dictKey + "'";
    typeInput = "'" + typeInput + "'";
    return '<tr id="firstRow'+rowKey+'" class="newRowHead"><td style="display:none;">-</td><td rowspan="3">'+nick+'<br/><br/>'+genID+'</td><td rowspan="3">'+protocol+'</td><td rowspan="3">'+date+'</td><td rowspan="3">'+plateType+'</td><td rowspan="3">'+nPlates+'</td><td rowspan="3"></td><td>Trash: <input type="text" value="0" size="3"></td><td><input type="button" value="Configure culture condition"><br><p class="id_cc" style="display:none;">' + idcc + '</p><p style="color:red;"></p></td><td rowspan="3"><input type="button" class="deleteButtons" value="Delete Row" onclick="deleteRow(this, '+typeInput+', '+dictKeyV+' );"></td></tr><tr id="'+rowKey+'" class="newRow"><td>To archive:  <input type="text" class="toArchive" name="toArchive" value="0" size="3"></td><td><table><tr id="'+rowKey+'">Expansion:</tr><tr id="'+rowKey+'" class="newRow"><td>Input: <input type="text" value="0" size="3"/></td><td>Dilution[1:X]: <input type="text" value="0" size="3"/></td><td>Output: <input type="text" value="0" size="3"/></td></tr></table></td></tr><tr id="'+rowKey+'" class="newRow"><td>To experiment: <input type="text" value="0" size="3"></td><td>Change Media: <input type="text" value="0" size="3"></td></tr>'
}

//annulla l'ultima operazione eseguita dall'utente (solo per toexperiment, toarchive, totrash)
function undo(dictKey, typeInput){
console.log(dictKey);
console.log(typeInput);
    var arrayIndex = cellsDict[dictKey]['mods'][typeInput].length - 1;
    var r = document.getElementById("firstRow"+dictKey);  //uso questo e non jQuery per permettermi i caratteri speciali in dictKey
    var row = jQuery(r);
    if (cellsDict[dictKey]['mods'][typeInput][arrayIndex]['applied']){
        var amount = parseInt(cellsDict[dictKey]['mods'][typeInput][arrayIndex]['amount']);
        var actualQ = parseInt(jQuery(jQuery(row).children()[5]).text());
        jQuery(jQuery(row).children()[5]).text(actualQ + amount);
        somedid -= 1;
    }
    cellsDict[dictKey]['mods'][typeInput].splice(arrayIndex,1);
    document.getElementById(typeInput+dictKey).value = 0;
    if (cellsDict[dictKey]['mods'][typeInput].length == 0)
        cellsDict[dictKey]['mods'][typeInput].push({'amount': 0, 'applied':false});
}

//deleteRow(this, 'expansion', '2' );
function deleteRow(obj, typeAction, dictKey){
    console.log('deleting');
    console.log(obj);
    console.log($($(obj).parent().parent().children()[5]).text());
    var r = document.getElementById("firstRow"+dictKey);  //uso questo e non jQuery per permettermi i caratteri speciali in dictKey
    var row = jQuery(r);
    console.log('------------------');
    console.log(typeAction);
    //console.log(index);
    console.log(dictKey);
    //index = parseInt(index);
    var actualQ = parseInt(jQuery(jQuery(row).children()[5]).text());
    console.log(typeAction);
    //console.log(index);
    var undoQ = 0;
    if (typeAction == 'expansion')
        undoQ = parseInt(cellsDict[dictKey]['mods'][typeAction]['generic']['inputA']);
    else if (typeAction == 'toReset')
        //for (idcc in cellsDict[dictKey]['mods']['toReset']['outputs']){ undoQ += parseInt( cellsDict[dictKey]['mods']['toReset']['outputs'][idcc] ); }
        //undoQ = parseInt(cellsDict[dictKey]['mods'][typeAction][index]['amount']); //RIPRENDERE DA QUI....... 
        undoQ = parseInt($($(obj).parent().parent().children()[5]).text());
    console.log(actualQ);
    console.log(undoQ);
    jQuery(jQuery(row).children()[5]).text(actualQ + undoQ);
    //cancella la riga (composta da 3 righe) e annulla l'azione nella struttura dati
    jQuery(obj).closest('tr.newRowHead').next().remove()
    jQuery(obj).closest('tr.newRowHead').next().remove()
    jQuery(obj).closest('tr.newRowHead').remove();
    somedid -= 1;


    console.log(typeAction)
    console.log(idcc);
    //console.log((Object.size(cellsDict[dictKey]['mods']['expansion']['outputs']) + Object.size(cellsDict[dictKey]['mods']['toReset']['outputs'])));
    
    var totOutputs = 0;
    for (idcc in cellsDict[dictKey]['mods']['expansion']['outputs']){ 
        if (parseInt( cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] ))
            totOutputs += parseInt( cellsDict[dictKey]['mods']['expansion']['outputs'][idcc] ); 
    }    
    console.log('outputs to reset ' , Object.size(cellsDict[dictKey]['mods']['toReset']['outputs']));
    console.log('totOutputs ',  totOutputs);
    
    //else
    var idcc = $($(obj).parent().parent().find('.id_cc')).text();
    console.log(idcc);
    var genid = cellsDict[dictKey]['mods'][typeAction]['outputs'][idcc +'genid'];
    console.log(genid);
    for (var index = 0; index < generatedList.length; ++index) {
        if (generatedList[index] === genid) {
            generatedList.splice(index, 1);
            index--;
        }
    }
    
    delete cellsDict[dictKey]['mods'][typeAction]['outputs'][idcc + 'genid'];
    
    
    cellsDict[dictKey]['mods'][typeAction]['generic']['applied'] = false;
    $('#inputA' + dictKey).val(cellsDict[dictKey]['mods']['expansion']['generic']['inputA']);
    $('#reduc' + dictKey).val(cellsDict[dictKey]['mods']['expansion']['generic']['reduction']);
    $("tr[dictkey='" + dictKey +  "']").find('.toReset').val('');
    
}

function applyAll(){
    //applica tutte le azioni ancora non applicate (per change media ed expansion, deve aggiungere le relative righe)
    console.log('##############################');
    //somedid = true;
    for (dictKey in cellsDict){
        console.log(dictKey);
        applyActions(dictKey);
    }

}

function saveActions(){
    //applyAll();
    if (somedid > 0){
        //mandare al server la struttura dati
        var url = base_url + '/expansion/';
        //console.log(cellsDict);
        //console.log('adsfdsngkjbfskjgbnfskjbdnfs');
        jQuery.ajax({
            url: url,
            type: 'POST',
            data: {'cellsDict':JSON.stringify(cellsDict) },
            dataType: 'text',
        });
    }else{
        alert("You haven't applied any actions.", 'Warning info:')
    }
}


function addslot(key){
    console.log('addslot');
    console.log( "$( $(.slot" + key+").first() ).clone().appeinsertAfterndTo( $($(#firstRow" + key + " .slot + key).last()) )" );
    var newSlot = $( $(".slot" + key).first() ).clone();
    $(newSlot).find('.toReset').val(0);
    $(newSlot).find('*[class^="expansion"]').val('');
    $(newSlot).find('.name_cc').text('');
    $(newSlot).find('.id_cc').text('');
    $(newSlot).insertAfter( $($("#firstRow" + key + " .slot" + key).last()) );

}

function deleteSlot(key, obj){
    console.log(obj);
    console.log( $(obj).parent().parent().parent().parent() );
    var ccid = $(obj).attr('ccid');
    if ($(obj).parent().parent().parent().parent().parent().children().length > 3){
        var ccid = $(obj).attr('ccid');
        $(obj).parent().parent().parent().parent().remove();
    }else{
        $($(obj).closest('tbody').find('*[class^="expansion"]')).val('');
        $($(obj).closest('tbody').find('.toReset')).val(0);
        $($(obj).closest('tbody').find('.name_cc')).text('');
        $($(obj).closest('tbody').find('.id_cc')).text('');
    }
    console.log(ccid);
    if (ccid != ''){
        console.log('deleting dict');
        console.log(ccid);
        delete cellsDict[key]['mods']['expansion']['outputs'][ccid];
        delete cellsDict[key]['mods']['toReset']['outputs'][ccid];
    }    

}


function order(typeOrder, obj, index){
    console.log(typeOrder);
    console.log(index);
    if (somedid == 0){

        i = index.split('&');
        var tempArray = new Array();
        for (c in viewCells){
            key = viewCells[c]['key'];
            var elem = "";
            if (i.length == 1)
                elem = cellsDict[key][i[0]];
            else{
                var temp = cellsDict[key];
                for (j = 0; j < i.length; j++){
                    temp = temp[i[j]];    
                }
                elem = temp;
            }
            //console.log(elem);
            tempArray.push({'key':key, 'val':elem});
        }

        if (typeOrder == 'asc'){
            tempArray.sort(function(a,b) {
                if (a.val < b.val)
                    return -1
                else if (a.val > b.val)
                    return 1;
                else
                    return 0;
            });
        }else{
            tempArray.sort(function(a,b) {
                if (a.val > b.val)
                    return -1
                else if (a.val < b.val)
                    return 1;
                else
                    return 0;
            });
        }
        viewCells = tempArray;
        drawTable();
        $(".fa").css('color','#A8B7C6'); //#254B70
        if (obj != "")
            $(obj).css('color','#FFFFFF');  //#A8B7C6
        else
            $($(".fa")[1]).css('color','#FFFFFF'); //#A8B7C6
    }else{
        alert("Warning: you have already applied some actions, you can't sort the table.", "Warning");
    }
}



function drawTable(){
    var string = "";
    $('#table_exp tbody').empty();
    for (i in viewCells){
        //console.log(viewCells[i]['key']);
        var key = viewCells[i]['key'];
        //console.log(cellsDict[key]);
        var temp = "";
        
        string += "<tr class='mainRow' id='firstRow" + key + "' dictKey ='" + key + "'>";
        string += "<td style='display:none;'>"+ cellsDict[key]['id'] + "</td>";
        string += "<td rowspan='3'><p  id='nick" + key + "' style='float:left;'>" + cellsDict[key]['nickname'] + "</p><p style='float:left;margin-left:1em;'><i class='fa fa-pencil-square-o' onclick='editNick(" + key + ");' style='float:left;cursor:pointer;font-size:1.4em;' title='Edit nickname'></i></p><br style='clear:left;'>"+ cellsDict[key]['genID'] + "</td>";
        string += "<td rowspan='3' ccId = '" + cellsDict[key]['cc']['id'] + "'><p style='margin-right:1.5em;float:left;' >" + cellsDict[key]['cc']['conf_name'] + "</p><p style='float:left;' ><img src='"+ base_url + "/cell_media/img/info_icon.png' title='Show info' onclick='showInfos(" + cellsDict[key]['cc']['id'] + ");' style='cursor:pointer;'></p> </td>";
        string += "<td rowspan='3'>" + cellsDict[key]['startDate'] + "</td>";
		string += "<td rowspan='3' id='typePlate" + key + "'>" + cellsDict[key]['cc']['typeP'] + "</td>";
		string += "<td rowspan='3'>" + cellsDict[key]['nPlates'] + "</td>";
		
		//creo i campi per le azioni da pianificare, selezionando gia' i check se e' il caso
		string += "<td rowspan='3' align='center'><table id='tab_plan"+key+"' key='"+key+"' >";
		//se non c'e' Archive non mi mette il checkbox
		if ("Archive" in cellsDict[key]["plan"]){
			var archivio="";
			var now=cellsDict[key]["plan"]["Archive"]["now"];
			if(now){
				archivio="checked='checked'";
			}
			string+="<tr><td>To archive</td><td><input type='checkbox' "+archivio+" class='to_archive' key='Archive' ></td></tr>";
		}
		if ("Expansion" in cellsDict[key]["plan"]){
			var expans="";
			var now=cellsDict[key]["plan"]["Expansion"]["now"];
			if(now){
				expans="checked='checked'";
			}
			string+="<tr><td>To expansion</td><td><input type='checkbox' "+expans+" class='to_expansion' key='Expansion' ></td></tr>";
		}
		string+="</table></td>";
		
		temp = "onkeyup = 'writeDict(this," + '"' + key + '"' + ");'"
        string += "<td>Trash: <input type='text' id='toTrash" + key + "' class='toTrash' name='toTrash' value='" + cellsDict[key]['mods']['toTrash'][0]['amount'] + "' size='1' onkeypress='validate(event);' " + temp + "/><img src='" + base_url + "/cell_media/img/go-back-icon.png'";
        temp = "onclick = 'undo(" + '"' + key + '"' + ',"toTrash"' + ");'";
        string += " title='Undo' " + temp + " style='cursor:pointer;'></td>";
        string += "<td align='center'>";
        temp = "onclick = 'addslot(" + '"' + key + '"' + ");'";
        string += "<input type='button' value='Add slot' "+temp+"/><br/>";
        for (c in cellsDict[key]['mods']['expansion']['outputs']){
            var value = cellsDict[key]['mods']['expansion']['outputs'][c];
            string += "<table class='slot"+key+"' border='0' cellpadding='0' cellspacing='0' style='border:1px solid #254B70' class='cc_output'>";
            temp = "onclick = 'changecc(" + '"' + urlWindow + '", "' + cellsDict[key]['cc']['id'] + '"' + ", this);'";     
            string += "<tr><td align='center'><input type='button' value='Define culture condition' " + temp + "/></td><td>";
            temp = "onclick = 'deleteSlot(" + '"' + key + '"' + ",this );'";
            string += "<img src='"+ base_url +"/cell_media//img/x.png' " + temp + "class='deleteIcon' width='16' ccid = '"+ c +"'></td></tr>";
            string += "<tr><td align='center'><p class='typePlate' style='display:none;' ></p>";
            var ccName = "<p class='name_cc' style='color:red;' ></p><p class='id_cc' style='display:none;' >  </p></td></tr><tr><td>";
            if (Object.size(infocc) > 0){
                if (c != "")
                    if (isFinite(c))
                        ccName = "<p class='name_cc' style='color:red;' >" + infocc[c]['name'] + "</p> <p class='id_cc' style='display:none;' >" + c + "</p></td></tr><tr><td>";
            }
            string += ccName;
            //string += "<p class='id_cc' style='display:none;' >  </p></td></tr><tr><td>";
            temp = "onkeyup = 'writeDictSlot(this," + '"' + key + '"' + ");'"
            string += "Expansion output: <input type='text' class='expansion_outputA' name='expansion_outputA' value='" + cellsDict[key]['mods']['expansion']['outputs'][c] + "' size='1' onkeypress='validate(event);' " + temp + "/>";
            temp = "onkeyup = 'writeDictSlot(this," + '"' + key + '"' + ");'"
			string += "Change Media: <input type='text' class='toReset' name='toReset' value='0' size='1' onkeypress='validate(event);' " + temp + "/></td></tr></table>";
        }    
        temp = "onclick = 'applyActions(" + '"' + key + '"' + ");'";
        string += "</td><td rowspan='3'><input type='button' value='Apply Actions' "+ temp +" /></td></tr>";
        string += "<tr class='mainRow' dictKey='"+key+"'>";
        temp = "onkeyup = 'writeDict(this," + '"' + key + '"' + ");'"
        string += "<td>To archive:  <input type='text' id='toArchive"+key+"' class='toArchive' name='toArchive' value='"+cellsDict[key]['mods']['toArchive'][0]['amount'] + "' size='1' onkeypress='validate(event);' " + temp + "/><img src='"+ base_url + "/cell_media/img/go-back-icon.png'";
        temp = "onclick = 'undo(" + '"' + key + '"' + ',"toArchive"' + ");'";
        string +=  " title='Undo' " + temp + " style='cursor:pointer;'></td>";
        string += "<td rowspan=2><table><tr>Expansion:</tr><tr class='mainRow' dictKey='"+key+"'>";
        temp = "onkeyup = 'writeDictGenericSlot(this," + '"' + key + '"' + ");'"
        string += "<td>Input: <input type='text' id='inputA"+key+"' class='expansion_inputA' name='expansion_inputA' value='"+ cellsDict[key]['mods']['expansion']['generic']['inputA'] + "' size='1' onkeypress='validate(event);' " + temp + "/></td>";
        temp = "onkeyup = 'writeDictGenericSlot(this," + '"' + key + '"' + ");'"
        string += "<td>Dilution[1:X]: <input type='text' id='reduc"+key+"' class='expansion_reduction' name='expansion_reduction' value='"+ cellsDict[key]['mods']['expansion']['generic']['reduction'] +"' size='1' onkeypress='validate(event);' "+temp+"/></td>";
        string += "</tr></table></td></tr><tr class='mainRow' id='lastRow"+key+"' dictKey='"+key+"'>";
        temp = "onkeyup = 'writeDict(this," + '"' + key + '"' + ");'"
        string += "<td>To experiment: <input type='text' id='toExperiment"+key+"' class='toExperiment' name='toExperiment' value='"+cellsDict[key]['mods']['toExperiment'][0]['amount']+"' size='1' onkeypress='validate(event);' "+temp+"/><img src='"+ base_url + "/cell_media/img/go-back-icon.png'";
        temp = "onclick = 'undo(" + '"' + key + '"' + ',"toExperiment"' + ");'";
        string+= " title='Undo' " + temp + " style='cursor:pointer;'></td></tr>";
            
    }
    $('#table_exp tbody').append(string);
}

function checkKey(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        filter();
}


function filterUser(){
    if (somedid == 0){
        var filterValue = $("#userFilter").val();
        if (filterValue != ""){
            var tempArray = new Array();

            for (key in cellsDict){
                var elem = cellsDict[key]['username'];
                if (elem == filterValue)
                    tempArray.push({'key':key, 'val':elem});
            }
            if (Object.size(tempArray) > 0){
                viewCells = tempArray;
                //drawTable();
                order('asc', '', 'genID');
            }
            else
                alert("No results for your filter.", "Warning");
        }
        else{
            setViewCells('genID')
            order('asc', '', 'genID');           
        }
    }
    else{
        alert("Warning: you have already applied some actions, you can't filter the table.", "Warning" );
    }
}

function filter(){
    if (somedid == 0){
        var filterValue = $("#inputFilter").val();
        if (filterValue != ""){
            var re = new RegExp('^' + filterValue);
            var tempArray = new Array();

            for (key in cellsDict){
                var elem = cellsDict[key]['genID'];
                console.log(elem, elem.search(filterValue));
                console.log(elem, re.test(elem));
                if (re.test(elem))
                //if (elem.search(filterValue) >= 0)
                    tempArray.push({'key':key, 'val':elem});
            }
            if (Object.size(tempArray) > 0){
                viewCells = tempArray;
                drawTable();
                order('asc', '', 'genID');
            }
            else
                alert("No results for your filter.", "Warning");
        }else{
            setViewCells('genID')
            order('asc', '', 'genID');           
        }

    }else{
        alert("Warning: you have already applied some actions, you can't filter the table.", "Warning" );
    }
}


function setViewCells(field){
    viewCells = [];
    for (key in cellsDict){
         viewCells.push({'key':key, 'val':cellsDict[key][field]});
    }
}


function editNick(key){
    //if (somedid == 0){
    	$("#newNick").val("");
        jQuery( "#dialog2" ).dialog({
            resizable: false,
            height:200,
            width:340,
            modal: true,
            draggable :false,
            buttons: {
                "OK": function() {
                    //call API
                	//non calcolo il cambio di nome come una modifica di cui tenere conto
                    //somedid += 1;
                    var newNick = $("#newNick").val();
                    var url = base_url + '/expansion/edit_nickname/';
                    console.log(url);
                    $.ajax({
                        url: url,
                        type: 'post',
                        data: {'nick':newNick, 'cell_id':key },
                        success: function(response) {  
                            if (response == 'ok'){
                                $("#nick"+key).text(newNick);
                            	cellsDict[key]["nickname"]=newNick;
                            }
                            else{
                                alert('Error while saving the new nickname.','Error');
                            }
                        }
                    });                    
                    jQuery( this ).dialog( "close" );
                },
                "Cancel": function() {
                    jQuery( this ).dialog( "close" );
                }
            }
        });
    //}else{
    //    alert("Warning: you have already applied some actions, you can't edit any nicknames.", "Warning" );
    //}
}
