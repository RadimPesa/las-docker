//var protocol_infos_dictionary = {};
var typePlate = "";

$(document).ready(function(){
    oTable = $("table#availableProt").dataTable( {
        "bProcessing": true,
        "bLengthChange": false, 
        "iDisplayLength": 5,
        "bAutoWidth": false ,
        "aaSorting": [[2, 'desc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0, 1, 4 ] }
        ], 
    });
    $("table#availableProt tbody").click(function(event) {
        $(oTable.fnSettings().aoData).each(function (){
            $(this.nTr).removeClass('row_selected');
        });
        $(event.target.parentNode).addClass('row_selected');
        //selectedRow = event.target.parentNode;
        //refreshPlate(selectedRow);
        selectCC(event.target.parentNode);
    });
});

function getInfos(img){
    console.log('getInfos');
    console.log($(img).parent().parent());
    var row = $(img).parent().parent();
    var conf_id = $(img).attr('protId');
    $(row).toggleClass("row_selected");
    var url = base_url + '/api/urlProtocolInfosGetter/' + conf_id + '/';
    console.log(url);
    $.ajax({
        url: url,
        type: 'get',
        success: function(response) {    
            var protocol_infos = JSON.parse(response);
            //protocol_infos_dictionary[conf_id] = protocol_infos;
            put_infos(protocol_infos);
            $( "#dialog_selectP" ).dialog({
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
    //var file = "file_namez('"+file_name+"')"
    if (file_name != "")
        tabella.append('</tr><tr><td class="root"> Docs </td><td><a href="'+ base_url + "/get_file/" + file_name + '"> <span class="ui-icon ui-icon-arrowthickstop-1-s"></span></a></td>');
    //tabella.append('</tr><tr><td class="root"> File name</td><td> <p onclick='+file+'>'+file_name+'</p></td>');
    tabella.append("</tr><tr><td class='root'> Description </td><td class='col_ftname'>"+description+"</td></tr>");
}

function findTypeP(dictList){
    console.log(dictList);
    for (var i = 0; i < dictList.length; i++){
        for (k in dictList[i]){
            console.log(k);
            if (k == 'type_plate'){
                return dictList[i][k];
            }
        }
    }
}

$(document).ready(function() {
    console.log(namecc);
    console.log(cc_id);
    $("#prot_list_select_id").change(function() {
        var protocol_id = $("#prot_list_select_id option:selected").attr('protocol_id');
        if (protocol_infos_dictionary.hasOwnProperty(protocol_id)){
            put_infos(protocol_infos_dictionary[protocol_id]);
            typePlate = findTypeP(protocol_infos_dictionary[protocol_id]['ft_without_el_list']);
        }else{
            var url = base_url + '/api/urlProtocolInfosGetter/' + protocol_id + '/';
            console.log(url);
            $.ajax({
                url: url,
                type: 'get',
                success: function(response) {    
                    var protocol_infos = JSON.parse(response);
                    //console.log(protocol_infos);
                    typePlate = findTypeP(protocol_infos['ft_without_el_list']);
                    protocol_infos_dictionary[protocol_id] = protocol_infos;
                    put_infos(protocol_infos);
                }
            });
        }
    });
});

function selecting(){
    $('#actions').css('display', 'none');
    $('#selecting').css('display', 'block');
}

function modding(){
    $('#actions').css('display', 'none');
    $('#modding').css('display', 'block');
    // chiamare API per caricare le condizioni di coltura da modificare
    var url = base_url +'/api/cc_details/' + cc_id + '/';
    console.log(url);
    $.ajax({
        //async:false,
        url: url,
        type: 'get',
        success: function(transport) {
            console.log(transport);
            elementsDict['selected'] = JSON.parse(transport)
            console.log(elementsDict);
            //$(lastRow).after(newRow);
            //$('#table_exp tr.newRow input,select,textarea').attr('disabled','disabled');
            for (nameE in elementsDict['selected']){
                console.log(nameE);
                writeSelected(nameE)
            } 
        }
    });
}

function selectCC(row){
    console.log(row);
    var index = oTable.fnGetPosition(row);
    var ccid = oTable.fnGetData( index, 0 );
    var ccname = oTable.fnGetData( index, 2 );
    var plate= oTable.fnGetData( index, 4 );
    console.log(ccname, ccid);
    writeWindow(ccname, ccid, plate);
}

function saveMods(){
    //alert('doing');
    var url = base_url + "/expansion/save_mods_cc/";
    console.log(url);
    $.ajax({
        url: url,
        type: 'POST',
        data: {'elementsDict':JSON.stringify(elementsDict['selected']), 'protocolName':namecc },
        dataType: 'text',
        success: function(response) {
            console.log(response);
            if (response == 'err'){
                alert("Error. Please, try again.");
            }else{
                //scrivere nella window opener i dati del nuovo cc
                console.log(response.split('|'))
                typePlate = response.split('|')[2];
                writeWindow(response.split('|')[1], response.split('|')[0],response.split('|')[2]);
            }
        }
    });
}

function writeWindow(ccname, ccid, plate){
    var cellLine = window.opener.selectedcell;
    console.log('writeWindow');
    console.log(cellLine);
    console.log('ccname', ccname);
    console.log($(window.opener.clickedSlot).closest('tbody').find('.name_cc'));
    $($(window.opener.clickedSlot).closest('tbody').find('.name_cc')).text(ccname);
    $($(window.opener.clickedSlot).closest('tbody').find('.typePlate')).text(plate);
    //console.log( $($(window.opener.clickedSlot).closest('tbody').find('.id_cc')).text() );
    if ($($(window.opener.clickedSlot).closest('tbody').find('.id_cc')).text() != ""){
        var oldcc = $($(window.opener.clickedSlot).closest('tbody').find('.id_cc')).text();
        console.log(oldcc);
        delete window.opener.cellsDict[cellLine]['mods']['toReset']['outputs'][oldcc];
        delete window.opener.cellsDict[cellLine]['mods']['expansion']['outputs'][oldcc];
        if ( window.opener.cellsDict[cellLine]['mods']['expansion']['outputs'].hasOwnProperty(oldcc + 'genid'))
            delete window.opener.cellsDict[cellLine]['mods']['expansion']['outputs'][oldcc + 'genid'];
        delete window.opener.infocc[oldcc]
        //delete window.opener.cellsDict[cellLine]['mods']['toReset']['outputs'][oldcc]
    }
    window.opener.cellsDict[cellLine]['mods']['expansion']['outputs'][ccid] = 0;
    //window.opener.cellsDict[cellLine]['mods']['expansion']['outputs'][ccid + 'genid'] = '';
    //window.opener.cellsDict[cellLine]['mods']['toReset']['outputs'][ccid] = 0;
    $($(window.opener.clickedSlot).closest('tbody').find('.id_cc')).text(ccid);
    $($(window.opener.clickedSlot).closest('tbody').find('.deleteIcon')).attr('ccid', ccid);
    $($(window.opener.clickedSlot).closest('tbody').find('input[type="text"]')).val(0);
    console.log(ccid);
    if (!window.opener.infocc.hasOwnProperty('ccid')){
        window.opener.infocc[ccid] = {};    
        window.opener.infocc[ccid]['name'] = ccname;
        console.log(window.opener.infocc);
    }
    console.log('end');
    window.close();
}
