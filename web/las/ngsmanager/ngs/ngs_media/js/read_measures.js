aliquots = []
aliquot_warnings = 0;

// init document
jQuery(document).ready(function(){
   
    generate_samples_table();
    infoFile();
    initDialog();
});

function generate_samples_table(){
    /*
     * Initialise DataTables, with image on the first column
     */
    var oTable = jQuery("table#samples").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id aliquot" },
            { "sTitle": "Id sample" },
            { "sTitle": "Select",
              "sDefaultContent": '<input type="checkbox" name="select" value="select" />'},
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Label" },
            { "sTitle": "Owner" },
            { "sTitle": "Volume (ul)" },
            { "sTitle": "Concentration (ng/ul)" },
            { "sTitle": "Cluster dens. (K/mm2)" },
            { "sTitle": "Run name" },
            { "sTitle": "Taken volume (Editable)" },
            { "sTitle": "Barcode" },
            { "sTitle": "Father container" },
            { "sTitle": "Position" },
            { "sTitle": "Exhausted",
              "sDefaultContent": '<input type="checkbox" name="exhausted" value="exhausted" />'},
            { "sTitle": "Failed",
              "sDefaultContent": '<input type="checkbox" name="failed" value="failed" />'},
            { "sTitle": "Files"},
            { "sTitle": "Files"},
        ],
        "bAutoWidth": false ,
        "aaSorting": [[0, 'desc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0, 1, 4, 8, 9, 16] },
            { "bSortable": false, "aTargets": [ 2, 14, 15, 16 ] }
        ],
        
        'fnDrawCallback': function () {
        	if(internal!="True"){
	            jQuery('#samples > tbody > tr').find('td:eq(5)').editable( 
	                function(value, settings) { 
	                    return(value);
		            }, 
		            {
			            "callback": function( sValue, y ) {
			                var aPos = oTable.fnGetPosition( this );
			                aliquot_warnings = 0;
			                oTable.fnUpdate( parseFloat(sValue), aPos[0], aPos[2] );
			            },
			            "height": "12px",
			            "width": "50px"
			        }
	            )
        	}
        },
        
    });
    if(internal=="True"){
    	oTable.fnSetColumnVis( 10, false);
    	oTable.fnSetColumnVis( 11, false);
    	oTable.fnSetColumnVis( 12, false);
    	oTable.fnSetColumnVis( 13, false);
    	oTable.fnSetColumnVis( 14, false);
    	oTable.fnSetColumnVis( 15, false);
    	oTable.fnSetColumnVis( 4, true);
    	oTable.fnSetColumnVis( 8, true);
    	oTable.fnSetColumnVis( 9, true);
    }
}

function addFile (){
    $("#form_measures").on("change", " input[type=file]:last", function(){
        var item = $(this).clone(true);
        var fileName = $(this).val();
        if(fileName){
            $(this).parent().append(item);
        }  
    });
}

// read data from the table after post of file
function readTable(){
    jQuery.each( jQuery("#samples").dataTable().fnGetNodes(), function(i, row){
        d = jQuery("#samples").dataTable().fnGetData(i);
        var exhausted = $(row).find('[name=exhausted]').prop('checked');
        var failed = $(row).find('[name=failed]').prop('checked');
        var files = [];
        var dataf = null;
        if (d[16] != ""){
            dataf = d[16];
        }
        else{
            dataf = JSON.stringify(files);
        }
        aliquots.push({'idExperiment':d[1], 'idAliquot':d[0], 'volume':d[6], 'takenvol':d[10], 'failed':failed, 'exhausted':exhausted, 'files': dataf , 'barcode': d[11],'label':d[4],'cluster':d[8],'run':d[9]});
    });
    
}

function submitResults(){
    readTable();
    $('#aliquots_list').val(JSON.stringify(aliquots));
    $('#upload_sample_file').submit();
}

function associateFiles(){
    var currfiles = $('input[type=file]:last')[0];
    var filelist = currfiles.files;
    filenames = [];
    if(filelist.length!=0){
	    for (var i=0; i<filelist.length; i++){
	        filenames.push(filelist[i].name);
	    }
	    $.each( jQuery("#samples").dataTable().fnGetNodes(), function(i, row){
	        if ($(row).find('[name=select]').prop('checked')){
	            $("#samples").dataTable().fnUpdate( JSON.stringify(filenames), i, 16,false,true );
	            $("#samples").dataTable().fnUpdate( '<span class="ui-icon ui-icon-search"></span>', i, 17,false,true );
	            $(row).find('[name=select]').prop('checked', false);
	        }         
	    });
	
	    var item = $(currfiles).clone(true);
	    $(currfiles).hide();
	    $('#filelist').append(item);
    }
    else{
    	alert("Please insert at least a file");
    }
}

function infoFile(){
    $( document ).on('click', '.ui-icon-search', function(){
        //console.log($(this).parent().parent());
        rowData = jQuery("#samples").dataTable().fnGetData($(this).parent().parent()[0]);
        var posFile = jQuery("#samples").dataTable().fnGetPosition($(this).parent().parent()[0]);
        $('#rowFile').val(posFile);
        var filelistSample = $.parseJSON(rowData[16]);
        $('.filediv_dialog').empty();
        for (var i=0; i<filelistSample.length; i++){
            $('.filediv_dialog').append('<input type="checkbox" name="filesample" value="' + filelistSample[i] + '">' + filelistSample[i]+ '<br>');
        }
        $("#viewfile_dialog").dialog("open");
        //alert('Files: ' + rowData[13]);
    })

}

function initDialog(){
	$("#viewfile_dialog").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 300,
            title: "File associated",
            buttons: [
                {
                    text: "Delete",
                    click: function() {
                        var filelistSample = $('.filediv_dialog input');
                        var finalList = [];
                        for (var i=0; i<filelistSample.length; i++){
                            if ($(filelistSample[i]).prop('checked') == false){
                                finalList.push($(filelistSample[i]).val());
                            }
                        }                        
                        var posFile = $('#rowFile').val();
                        jQuery("#samples").dataTable().fnUpdate(JSON.stringify(finalList), posFile, 16,false,true );
                        if (finalList.length==0){
                            $("#samples").dataTable().fnUpdate('', posFile, 17,false,true );
                        }                        
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
        }
    );
}