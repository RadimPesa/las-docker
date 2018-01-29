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
	initForms();


});

function initForms() {
    $("#run_fingerprinting_frm").on("submit", function() {
        var description = window.prompt("Please provide a description (optional):");
        $("#run_fingerprinting_frm #descr").val(description);
    });
}

function initTable(){

	var oTable = $('#historyTable').dataTable({
		"bProcessing": true,
        "aoColumns": [
         	{ "mDataProp": null,
              "sClass": "control center",
              "sDefaultContent": '<span class="btn-details ui-icon ui-icon-carat-1-e" style="cursor: pointer"></span>',
              "bSortable": false
            },
            { "mDataProp": "timestamp",  "sTitle": "Created on" },
            { "mDataProp": "author",  "sTitle": "Author" },
            { "mDataProp": "description",  "sTitle": "Description" },
            { "mDataProp": "status",  "sTitle": "Status" },
            { "sTitle": "Download report" ,
        	  "sClass": "control center", 
              "bSortable": false},
            { "mDataProp": null,
              "sTitle": "Cancel/Delete" ,
              "sClass": "control center",
              "sDefaultContent": '<span class="btn-cancel ui-icon ui-icon-closethick" style="cursor: pointer"></span>',
              "bSortable": false
            }
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[1, 'desc']],
	});

    jQuery( document ).on('click',"#historyTable tbody td span.btn-cancel", function () {
        var id = $(this).parents('tr').data("id");
        $("#cancel_fingerprinting_frm input[name='id']").val(id);
        $("#cancel_fingerprinting_frm").submit();
    });


	jQuery( document ).on('click',"#historyTable tbody td span.btn-details", function () {
        var nTr = $(this).parents('tr')[0];
        var nTds = this;
        
        if (oTable.fnIsOpen(nTr)) {
            /* This row is already open - close it */
            console.log(this);
            //this.src = "http://i.imgur.com/SD7Dz.png";
            oTable.fnClose(nTr);
            $(this).removeClass("ui-icon-carat-1-s").addClass("ui-icon-carat-1-e")
        }
        else {
            /* Open this row */
            //var rowIndex = oTable.fnGetPosition( $(nTds).closest('tr')[0] ); 
            console.log(nTr);
            var data = $(nTr).data();
            console.log(data);

            oTable.fnOpen(nTr, fnFormatDetails(data), 'runs');
            $(this).removeClass("ui-icon-carat-1-e").addClass("ui-icon-carat-1-s")
        }
    });

	/* NOT USED

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
	*/
}

/* NOT USED

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

*/

function fnFormatDetails(data) {
    var sOut = "<ul class='inline report'>";
    sOut += "<li><span>QC cutoff:</span><span>" + data['qc_cutoff'] + "</span></li>"
    sOut += "<li><span>Mismatch cutoff:</span><span>" + data['mismatch_cutoff'] + "</span></li>"
    sOut += "<li><span>&#35; of samples:</span><span>" + data['samples'] + "</span></li>"
    sOut += "<li><span>&#35; of excluded samples:</span><span>" + data['excluded_samples'] + "</span></li>"
    sOut += "<li><span>&#35; of mismatced samples:</span><span>" + data['mismatched_samples'] + "</span></li>"
    sOut += "<li><span>&#35; of mismatched cases:</span><span>" + data['mismatched_cases'] + "</span></li>"
    sOut += "<li><span>&#35; of false mismatched samples:</span><span>" + data['false_mismatched_samples'] + "</span></li>"
    sOut += "<li><span>&#35; of unmatched samples:</span><span>" + data['unmatched_samples'] + "</span></li>"
    sOut += "<li><span>&#35; of mild unmatched cases:</span><span>" + data['mild_unmatched_cases'] + "</span></li>"
    sOut += "<li><span>&#35; of serious unmatched cases:</span><span>" + data['serious_unmatched_cases'] + "</span></li>"
    sOut += "<li><span>&#35; of validated samples:</span><span>" + data['validated_samples'] + "</span></li>"
    sOut += "</ul>"
    return sOut;
}
