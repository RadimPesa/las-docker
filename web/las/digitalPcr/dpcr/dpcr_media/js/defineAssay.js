targets_selected = {};
selected_target_data = null;
edit_assay_name = null;

jQuery(document).ready(function(){
    // CRFS TOKEN   
    jQuery('html').ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    initTabAssay();
    initSearchGene();
    generate_table_mut();
    generate_table_assay_targets();

    jQuery('#search_target').click(function(event){
        searchMut();
    });

    jQuery('#select_target').click(function(event){
        selectTarget();
    });

    jQuery('#saveAssay').click(function(event){
        saveAssay();
    });

});


function initTabAssay(){

    jQuery("table#assayTab").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Label" },
            { "sTitle": "Name" },
            { "sTitle": "Edit",
               "mDataProp": null, 
               "sWidth": "20px", 
               "sDefaultContent": '<span class="ui-icon ui-icon-pencil" style="float:right"></span>', 
                "bSortable": false
            },
            { "sTitle": "Delete",
               "mDataProp": null, 
               "sWidth": "20px", 
               "sDefaultContent": '<span class="ui-icon ui-icon-trash" style="float:right"></span>', 
                "bSortable": false
            },                                        
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] }],
    });


    
    jQuery( document ).on('click',"#assayTab tbody td span.ui-icon-pencil", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var adt = jQuery("#assayTab").dataTable();
        var pos = adt.fnGetPosition(jQuery(this).parents('td')[0]);
        var assay = adt.fnGetData(nTr);
        jQuery.ajax({
            type: 'GET',
            data: {'assayLabel': assay[0]},
            url: './',
            success: function(transport) {
                console.log(transport)
                var tdt = jQuery("#targetAssayTab").dataTable();
                tdt.fnClearTable();
                targets_selected = {}
                data = JSON.parse(transport);
                $('#nameAssay').val( assay[1] );
                $("input.exptype").prop("checked", false);
                $.each(data['assayTypes'], function(i, el) { $("input.exptype[value='" + el + "']").prop("checked", true); });
                edit_assay_name = assay[1];
                for (var i = 0; i < data['targets'].length; i++){
                    console.log(data['targets'][i]);
                    targets_selected[data['targets'][i]['uuid']] = data['targets'][i];
                    tdt.fnAddData(data['targets'][i]);
                }
            }, 
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
    
    });

    jQuery( document ).on('click',"#assayTab tbody td span.ui-icon-trash", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var adt = jQuery("#assayTab").dataTable();
        var pos = adt.fnGetPosition(jQuery(this).parents('td')[0]);
        var assay = adt.fnGetData(nTr);
        console.log(assay[1]);
        
        $('#deldialog').dialog({
            autoOpen: false,
            modal: true,
            width: 320,
            resizable: false,
            buttons:
            [
                {
                    text: "OK",
                    click: function() {
                        jQuery.ajax({
                            type: 'POST',
                            data: {'action':'delAssay', 'assayName': assay[0]}, // insert data for the assay (name, list of amplicons)
                            url: './',
                            success: function(transport) {
                                console.log(transport);
                                jQuery("#assayTab").dataTable().fnDeleteRow(pos[0]);
                                infoBox('Deleted');                    
                            }, 
                            error: function(data) { 
                                console.log(data.responseText);
                                alert(data.responseText, "Error");
                            }
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


        
    
    });

}



function initSearchGene(){
    $("#search_gene").select2({
        width: 'resolve',
        placeholder: 'Start typing a gene symbol...',
        ajax: {
            url: urlAnnot + "newapi/geneInfo/",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term // search term
                };
            },
            processResults: function (data, page) {
            // parse the results into the format expected by Select2.
            // since we are using custom formatting functions we do not need to
            // alter the remote JSON data
                console.log(data);
                return {results: data};
            },
        },
        minimumInputLength: 1,
        templateResult: function(item) {
            if (item.loading) return item.text;

            return $('<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>');
        },
        templateSelection: function(item) {
            if (item.id != "")
                return $('<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>');
            else
                return item.text;
        }
    });
    
}


// generate and manage table of available targets
function generate_table_mut(){
    jQuery("#table_mut").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "mut Id", "mData": "uuid" },
            { "sTitle": "Chrom", "mData": "chrom" },
            { "sTitle": "Start", "mData": "start" }, 
            { "sTitle": "End", "mData": "end" }, 
            { "sTitle": "Transcript", "mData": "tx_ac" },
            { "sTitle": "HGVS.g", "mData": "hgvs_g" },
            { "sTitle": "HGVS.c", "mData": "hgvs_c" },
            { "sTitle": "HGVS.p", "mData": "hgvs_p" }, 
            { "sTitle": "Ext. ID", "mData": "x_ref" } 
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aaSorting": [[1, 'desc']],
     "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
        nRow.className += " mut_el";
        return nRow;
        }
    });
    
    // click on one row
    jQuery("#table_mut tbody").click(function(event) {
        jQuery(jQuery('#table_mut').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
        });
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.mut_el")){
            var pos = jQuery("#table_mut").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
            var data = jQuery("#table_mut").dataTable().fnGetData(pos);
            selected_target_data = data;
            if (targets_selected.hasOwnProperty(data['uuid'])){
                alert("Target just selected");
                selected_target_data = null;
                jQuery('#select_target').attr('disabled', 'disabled');
            }
            else{
                jQuery(event.target.parentNode).addClass('row_selected');
                jQuery('#select_target').removeAttr('disabled');
            }            
        }
    });
}

function searchMut(){
    // send data
    var geneid = $("#search_gene").val();
    console.log(geneid)
    var url =  urlAnnot + '/newapi/searchReferences/';
    jQuery.ajax({
        type: 'GET',
        data: {'annot_type': 'sequence_alteration', 'gene_uuid': geneid, 'ext_info': 'true'},
        url: url,
        success: function(transport) {
            console.log(transport);
            var mdt = jQuery('#table_mut').dataTable();
            mdt.fnClearTable();
            $(transport).each(function(index, value){
                //mdt.fnAddData([value['uuid'], value['chrom'], value['start'], value['end'], value['tx_ac'], value['hgvs_g'], value['hgvs_c'], value['hgvs_p'], value['x_ref'].join(", ")]);
                mdt.fnAddData(value);
            });
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


// select target and put in the final list
function selectTarget(){
    targets_selected[selected_target_data['uuid']] = selected_target_data;
    //var newArray = $.merge([null], selected_target_data);
    //jQuery('#targetAssayTab').dataTable().fnAddData(newArray);
    jQuery('#targetAssayTab').dataTable().fnAddData(selected_target_data);
    selected_target_data = null;
    jQuery('#select_target').attr('disabled', 'disabled');
    jQuery(jQuery('#table_mut').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
    });
}


function generate_table_assay_targets(){
    jQuery("#targetAssayTab").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            { "sTitle": "",
               "mDataProp": null, 
               "sWidth": "20px", 
               "sDefaultContent": '<span class="ui-icon  ui-icon-closethick"></span>', 
                "bSortable": false
            },
            { "sTitle": "mut Id", "mData": "uuid" },
            { "sTitle": "Chrom", "mData": "chrom" },
            { "sTitle": "Start", "mData": "start" }, 
            { "sTitle": "End", "mData": "end" }, 
            { "sTitle": "Transcript", "mData": "tx_ac" }, 
            { "sTitle": "HGVS.g", "mData": "hgvs_g" },
            { "sTitle": "HGVS.c", "mData": "hgvs_c" },
            { "sTitle": "HGVS.p", "mData": "hgvs_p" }, 
            { "sTitle": "Ext. ID", "mData": "x_ref" }
        ],
    "aaSorting": [[2, 'desc']],
    "bAutoWidth": false,

        "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    });

    jQuery( document ).on('click',"#targetAssayTab tbody td span.ui-icon-closethick", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#targetAssayTab").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var rmTarget = jQuery("#targetAssayTab").dataTable().fnGetData(nTr);
        jQuery("#targetAssayTab").dataTable().fnDeleteRow(pos[0]);
        delete targets_selected[rmTarget['uuid']];
    }); 
}


function saveAssay(){
    var assayName = $('#nameAssay').val();
    var nTargets = Object.keys(targets_selected).length;
    var assayType = $("input.exptype:checked").map(function(i, el) { return $(el).val();}).get()
    console.log(Object.keys(targets_selected))
    if (assayType.length == 0) {
        alert("Please choose at least one assay type");
        return;
    }
    if (assayName == '') {
        alert("Please insert a name");
        return;
    }
    if (nTargets == 0) {
        alert("Please insert at least one target");
        return;
    }

    jQuery.ajax({
        type: 'POST',
        data: {'action':'newAssay', 'name': assayName, 'assayType': JSON.stringify(assayType), 'edit': edit_assay_name == assayName ? 'true' : 'false', 'targets':JSON.stringify(Object.keys(targets_selected).map(function(el, i) { return targets_selected[el]; }))}, // insert data for the assay (name, list of mutations)
        url: './',
        success: function(transport) {
            edit_assay_name = null;
            $('#nameAssay').val('');
            $("input.exptype").prop("checked", false);
            $('#targetAssayTab').dataTable().fnClearTable();
            targets_selected = {};
            data = JSON.parse(transport);
            infoBox('Saved');
            updateAssayTable(data['assays']);
        }, 
        error: function(data) { 
            console.log(data.responseText);
            alert(data.responseText, "Error");
        }
    });
}


function infoBox(message){
    $("#infobox").text(message);
    $("#infobox").fadeIn( "slow" );
    $("#infobox").css('margin', '10px 0px');
    $("#infobox").css('padding' ,'5px');
    setTimeout(function(){
        $("#infobox").fadeTo(1000,0, function(){
            $("#infobox").html("");
            $("#infobox").removeAttr('style');
            $("#infobox").hide();
        })
    }, 2000);
}


function updateAssayTable(assays){
    jQuery("table#assayTab").dataTable().fnClearTable();
    for (var i= 0; i< assays.length; i++){
       jQuery("table#assayTab").dataTable().fnAddData([assays[i]['label'], assays[i]['name'], assays[i]['wg'], null, null]);
    }

}