function pad(n) { return ("0" + n).slice(-2); }

function generate_result_table(intestazione,tabella){
    var d = new Date();
    var user = jQuery('#actual_username').val();
    //solo per le collezioni
    var infocollect="";
    var collevent=$("#collevent");
    if (collevent.length!=0){
    	infocollect+="Informed consent: "+$(collevent).val()+" ";
    }
    var codpaz=$("#codpaz");
    if (codpaz.length!=0){
    	var cod=$(codpaz).val();
    	if (cod!="/"){
    		infocollect+="Patient code: "+cod;
    	}
    }
    var filename = intestazione+"_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d);
    var titolo=intestazione+"_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "__" + d.getHours() + ":" + pad(d.getMinutes());
    var pdfmessage="Laboratory Assistant Suite - BioBanking Manager - " + user + " - " + $.datepicker.formatDate('yy-mm-dd', d) + " " + d.getHours() + ":" + pad(d.getMinutes())+"   "+infocollect;
    var tab="#"+tabella;
    jQuery(tab).dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "sDom":'TRC<\"clear\">lfrtip',
        "oTableTools": {
                "aButtons": [ "copy", 
                {
	                "sExtends": "csv",
	                "sButtonText": "Las",
	                "sTitle": filename,
	                "sFileName": filename+".las",
	                "sFieldSeperator": "\t",
	                "mColumns": "visible",
	                "sFieldBoundary": ""
                }, 
                {
                    "sExtends": "pdf",
                    "sButtonText": "Pdf",
                    "sPdfOrientation": "landscape",
                    "sPdfMessage": pdfmessage,
                    "sTitle": filename,
                    "sFileName": filename+".pdf",
                    "mColumns": "visible"
                }
                , "print"],
                "sSwfPath": "/tissue_media/JS/DataTables-1.9.1/extras/TableTools/media/swf/copy_csv_xls_pdf.swf"
        }
    });
}