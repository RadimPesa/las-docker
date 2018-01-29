var iTableCounter = 1;


jQuery(document).ready(function(){
	initCsrf();
	initTable();


});


function initCsrf() {
    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
      var token;
      if (!options.crossDomain) {
        token = $.cookie("csrftoken");
        if (token) {
          return jqXHR.setRequestHeader('X-CSRFToken', token);
        }
      }
    });
}

function initTable(){

	detailsTableHtml = $("#detailsTable").html();


	var oTable = $('#templateTable').dataTable({
		"bProcessing": true,
		"aaData": templatesList,
         "aoColumns": [
         	{ "mDataProp": null,
              "sClass": "control center",
              "sDefaultContent": '<span class="ui-icon ui-icon-circle-plus"></span>'
            },
         	{ "mDataProp": "id", "sTitle": "Id" },
            { "mDataProp": "title", "sTitle": "Title" },
            { "mDataProp": "description", "sTitle": "Description" },
            { "mDataProp": "output",  "sTitle": "Output" },
            { "sTitle": "Edit" ,
        	  "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon  ui-icon-pencil"></span>'},
            { "sTitle": "Delete" ,
              "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon  ui-icon-trash"></span>'},
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[1, 'desc']],
	    "aoColumnDefs": [
        	{ "bVisible": false, "aTargets": [ 1 ] }
        ]
	});



	jQuery( document ).on('click',"#templateTable tbody td span.ui-icon-circle-plus", function () {
        var nTr = $(this).parents('tr')[0];
        var nTds = this;
        
        if (oTable.fnIsOpen(nTr)) {
            /* This row is already open - close it */
            console.log(this);
            //this.src = "http://i.imgur.com/SD7Dz.png";
            oTable.fnClose(nTr);
        }
        else {
            /* Open this row */
            var rowIndex = oTable.fnGetPosition( $(nTds).closest('tr')[0] ); 
            var detailsRowData = templatesList[rowIndex].translators;
            console.log(detailsRowData);
           
            //this.src = "http://i.imgur.com/d4ICC.png";
            oTable.fnOpen(nTr, fnFormatDetails(iTableCounter, detailsTableHtml), 'translators');
            oInnerTable = $("#templateTable_" + iTableCounter).dataTable({

                "aaData": detailsRowData,
                "bSort" : true, // disables sorting
                "aoColumns": [
                    { "mDataProp": "id", "sTitle": "Id" },
                    { "mDataProp": "title", "sTitle": "Title" },
                    { "mDataProp": "description", "sTitle": "Description" },
                    { "mDataProp": "output",  "sTitle": "Output" },
            	],
            	"aoColumnDefs": [
        			{ "bVisible": false, "aTargets": [ 0 ] }
        		],
                "oLanguage": {
                    "sEmptyTable":  "No translator associated"
                }
                
            });
            iTableCounter = iTableCounter + 1;
        }
    });


	jQuery( document ).on('click',"#templateTable tbody td span.ui-icon-pencil", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#templateTable").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var data = jQuery("#templateTable").dataTable().fnGetData(pos[0]);
        console.log('edit template ' + data.id);
        qt_id = data.id;
        window.location.href = view_query_url + '?tqid=' + qt_id;
    });


    jQuery( document ).on('click',"#templateTable tbody td span.ui-icon-trash", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#templateTable").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var data = jQuery("#templateTable").dataTable().fnGetData(pos[0]);
        var qt_id = data.id;
        console.log('cancel template ' + qt_id);
        $('#messDel').text('Are you sure to proceed?');
        $('#dialogDel').dialog({
            autoOpen: false,
            title: 'Delete Template',
            modal:true,
            buttons: {
                'Yes': function() {
                    $('#messDel').text('Wait...');
                    $.ajax({
                        url: "./",
                        type: "post",
                        data: {
                            action: 'delTemplate',
                            qt: qt_id,
                        },
                        success: function(data) {
                            jQuery("#templateTable").dataTable().fnDeleteRow(pos[0]);
                            $('#dialogDel').dialog("close");
                        },
                        error: function(data) {
                            $('#dialogDel').dialog("close");
                            alert("Error: failed to connect to server!");
                        }
                    });
                    
                },
                'No': function(){
                    $(this).dialog("close");
                }
            }
        });
        $('#dialogDel').dialog('open');

    });

}



function fnFormatDetails(table_id, html) {
    var sOut = "<table id=\"templateTable_" + table_id + "\">";
    sOut += html;
    sOut += "</table>";
    return sOut;
}