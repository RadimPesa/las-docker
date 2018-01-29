targets_selected = {};
selected_target_data = null;

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
            { "sTitle": "WG" },
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
        var pos = jQuery("#assayTab").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var assay = jQuery("#assayTab").dataTable().fnGetData(nTr);
        jQuery.ajax({
            type: 'GET',
            data: {'assayLabel': assay[0]},
            url: './',
            success: function(transport) {
                console.log(transport)
                jQuery("#targetAssayTab").dataTable().fnClearTable();
                targets_selected = {}
                data = JSON.parse(transport);
                $('#nameAssay').val( assay[1] );
                for (var i=0; i< data['targets'].length; i++){
                    console.log(data['targets'][i]);
                    targets_selected[data['targets'][i]['uuid']] = [data['targets'][i]['uuid'], data['targets'][i]['name'], data['targets'][i]['gene_symbol'], data['targets'][i]['primerfw'], data['targets'][i]['primerrv'], data['targets'][i]['type'], data['targets'][i]['ref'], data['targets'][i]['start_base'], data['targets'][i]['end_base'], data['targets'][i]['length'] ];
                    jQuery("#targetAssayTab").dataTable().fnAddData([null, data['targets'][i]['uuid'], data['targets'][i]['name'], data['targets'][i]['gene_symbol'], data['targets'][i]['primerfw'], data['targets'][i]['primerrv'], data['targets'][i]['type'], data['targets'][i]['ref'], data['targets'][i]['start_base'], data['targets'][i]['end_base'], data['targets'][i]['length'] ])

                }
            }, 
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
    
    });

    jQuery( document ).on('click',"#assayTab tbody td span.ui-icon-trash", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#assayTab").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var assay = jQuery("#assayTab").dataTable().fnGetData(nTr);
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
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Genes" }, 
            { "sTitle": "Primer A" }, 
            { "sTitle": "Primer B" },
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" }, 
            { "sTitle": "End" }, 
            { "sTitle": "Length" }, 
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
            if (targets_selected.hasOwnProperty(data[0])){
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
    var url =  urlAnnot + '/newapi/ampliconInfo/';
    jQuery.ajax({
        type: 'GET',
        data: {'gene_uuid': geneid},
        url: url,
        success: function(transport) {
            console.log(transport);
            jQuery('#table_mut').dataTable().fnClearTable();
            $(transport).each(function(index, value){
                console.log(value);
                var primerfw = null;
                var primerrv = null;

                for (var i= 0; i<value['primers'].length; i++){
                    if (primerfw == null){
                        primerfw = value['primers'][i]['name'];
                    }
                    else{
                        primerrv = value['primers'][i]['name'];
                    }
                }


                jQuery('#table_mut').dataTable().fnAddData([value['uuid'], value['name'], value['gene_symbol'], primerfw, primerrv, value['type'], value['ref'], value['start_base'], value['end_base'], value['length']]);
            });
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


// select target and put in the final list
function selectTarget(){
    targets_selected[selected_target_data[0]] = selected_target_data;
    var newArray = $.merge([null], selected_target_data);
    jQuery('#targetAssayTab').dataTable().fnAddData(newArray);
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
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Genes" }, 
            { "sTitle": "Primer A" }, 
            { "sTitle": "Primer B" }, 
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" }, 
            { "sTitle": "End" }, 
            { "sTitle": "Length" }, 
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
        delete targets_selected[rmTarget[1]];
    }); 
}


function saveAssay(){
    var assayName = $('#nameAssay').val();
    var nTargets = Object.keys(targets_selected).length;
    console.log(Object.keys(targets_selected))
    if (assayName != ''){
        if ( nTargets != 0){
            jQuery.ajax({
                type: 'POST',
                data: {'action':'newAssay', 'name': assayName, 'targets':JSON.stringify(Object.keys(targets_selected))}, // insert data for the assay (name, list of amplicons)
                url: './',
                success: function(transport) {
                    data = JSON.parse(transport);
                    $('#nameAssay').val('');
                    $('#targetAssayTab').dataTable().fnClearTable();
                    targets_selected = {};
                    infoBox('Saved');
                    updateAssayTable(data['assays']);
                }, 
                error: function(data) { 
                    console.log(data.responseText);
                    alert(data.responseText, "Error");
                }
            });
        }
        else{
            alert("Please insert at least one target")
        }
    }
    else{
        alert("Please insert a name.");
    }

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