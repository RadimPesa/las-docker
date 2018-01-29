var iTableCounter = 1;


jQuery(document).ready(function(){
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

	initTable();


});



function initTable(){

	detailsTableHtml = $("#detailsTable").html();


	var oTable = $('#historyTable').dataTable({
		"bProcessing": true,
		"aaData": historyQuery,
         "aoColumns": [
         	{ "mDataProp": null,
              "sClass": "control center",
              "sDefaultContent": '<span class="ui-icon ui-icon-circle-plus"></span>'
            },
         	{ "mDataProp": "qid", "sTitle": "Id" },
            { "mDataProp": "title", "sTitle": "Title" },
            { "mDataProp": "description", "sTitle": "Description" },
            { "mDataProp": "creation",  "sTitle": "Created on" },
            { "mDataProp": "author",  "sTitle": "Author" },
            { "mDataProp": "nruns",  "sTitle": "Runs" },
            { "mDataProp": "lastrun", "sTitle": "Last Run" },
            { "sTitle": "View" ,
        	  "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-search"></span>'},
            { "sTitle": "Run",
        	  "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-play"></span>'},            
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[7, 'desc']],
	    "aoColumnDefs": [
        	{ "bVisible": false, "aTargets": [ 1 ] }
        ]
	});



	jQuery( document ).on('click',"#historyTable tbody td span.ui-icon-circle-plus", function () {
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
            var detailsRowData = historyQuery[rowIndex].runs;
            console.log(detailsRowData);
           
            //this.src = "http://i.imgur.com/d4ICC.png";
            oTable.fnOpen(nTr, fnFormatDetails(iTableCounter, detailsTableHtml), 'runs');
            oInnerTable = $("#historyTable_" + iTableCounter).dataTable({

                "aaData": detailsRowData,
                "bSort" : true, // disables sorting
                "aoColumns": [
                { "mDataProp": "rid" },
                { "mDataProp": "qid" },
                { "mDataProp": "timestamp" },
                { "sTitle": "Results" ,
	        	  "sClass": "control center", 
	              "sDefaultContent": '<span class="ui-icon ui-icon-arrowthickstop-1-s"></span>'},
            	],
            	"aoColumnDefs": [
        			{ "bVisible": false, "aTargets": [ 0,1 ] }
        		]
                
            });
            iTableCounter = iTableCounter + 1;
        }
    });


	jQuery( document ).on('click',"#historyTable tbody td span.ui-icon-search", function () {
        console.log('view query');
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#historyTable").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var data = jQuery("#historyTable").dataTable().fnGetData(pos[0]);
        window.location.href = view_query_url + '?qid=' + data.qid;
    });


	jQuery( document ).on('click',"#historyTable tbody td span.ui-icon-arrowthickstop-1-s", function () {
        console.log('get results');
        var nTr = jQuery(this).parents('tr')[0];
        console.log(jQuery(this).parents('table'))
        
        var posRun = jQuery(jQuery(this).parents('table')[0]).dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var dataRun = jQuery(jQuery(this).parents('table')[0]).dataTable().fnGetData(posRun[0]);

        window.location.href = display_results_url + '?qid=' + dataRun.qid +'&rid=' + dataRun.rid ;
    });

	jQuery( document ).on('click',"#historyTable tbody td span.ui-icon-play", function () {
        console.log('run query');
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#historyTable").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var data = jQuery("#historyTable").dataTable().fnGetData(pos[0]);
        runQuery(data.qid);
    });    
}


function runQuery(qid){
	$("#sqf_qid").val(qid);
    $("#submit_query_frm").submit(function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        console.log(formURL, postData);
        $.ajax({
            url : formURL,
            type: "POST",
            data : postData,
            success:function(data, textStatus, jqXHR) {
                data = JSON.parse(data);
                window.location.href = display_results_url + '?qid=' + data.qid +'&rid=' + data.rid;
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert("An error occurred.")
            }
        });
        e.preventDefault(); //STOP default action
    });
    $("#submit_query_frm").submit();


}


function fnFormatDetails(table_id, html) {
    var sOut = "<table id=\"historyTable_" + table_id + "\">";
    sOut += html;
    sOut += "</table>";
    return sOut;
}