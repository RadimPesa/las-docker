var idcheck=1;
var lisparam=['Extraction date','Source','Fluorescence (ng/ul)','Nanodrop (ng/ul)','Purity280 (260/280)','Purity230 (260/230)','Provided volume (ul)','Elution buffer','Capture type'];

jQuery(document).ready(function(){	

    inizializza();
    
    jQuery('#select').click(function(event){
    	var url =  base_url + '/execute_experiment/';
    	//prendo il checkbox selezionato
    	var checksel=$(".check_select:checked");
    	var inputid=$(checksel).siblings(".request_id").val();
        var response = {'idplan': inputid}
        var json_response = JSON.stringify(response);
        jQuery.ajax({
            type: 'POST',
            url: url,
            data: json_response, 
            dataType: "json",  
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
    });
    
    $("#sample").autocomplete({
		source:base_url+'/api.loadsample/autocomplete/'
	});
    
    $("#loadlabel").click(load_sample);
    
    $("#sample").keypress(function(event){
		if ( event.which == 13 ) {
			load_sample();
		}
	});
    
    $(".info_request").click(show_info);
});

function show_info(){
	var label=$(this).attr("label").trim();
    $("#request_infos").empty();
    $("#request_infos").append("<tr><td >Label:</td><td>"+label+"</td></tr>");
	if (label in dizdatialiq){
		var dizdati=dizdatialiq[label];
		for (var i=0;i<lisparam.length;i++){
			var val=dizdati[lisparam[i]];
			var row = "<tr><td >"+lisparam[i]+":</td><td>"+val+"</td></tr>";
			$("#request_infos").append(row);
		}
	}
	$( "#dialog" ).dialog({
        resizable: true,
        height:450,
        width:600,
        modal: true,
        draggable :true,
        buttons: {
            "Ok": function() {
                jQuery(this).dialog( "close" );
            }
        }
    });
}

function inizializza(){
	$( "#accordion" ).accordion({
		header: ".divinterna",
		heightStyle: "content",
		collapsible: true,
		active:false
	});
	
	var tab2=$(".tabaliq").dataTable({
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
		"aoColumnDefs": [
 	        { "bSortable": false, "aTargets": [ 3 ] },
 	    ]
	});
	
		
	$(".check_select").click(function (event) {
		event.stopPropagation();
		if($(this).is(":checked")){
			$(".check_select,#loadlabel").attr("disabled",true);
			$(this).attr("disabled",false);
			$("#select").attr("disabled",false);
		}
		else{
			$(".check_select,#loadlabel").attr("disabled",false);
			$("#select").attr("disabled",true);
		}
	});		
}

function load_sample(){
	var label=$("#sample").val().trim();
	if(label==""){
		alert("Please insert a valid sample label");
		return;		
	}
	if($.inArray(label,listalabel)>-1){
    	alert("Label already present in request list");
    	return;
    }
	else{
		var url =  base_url + "/api.sample/reanalyze/" + label+"/";
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
	    jQuery.ajax({
	        type: 'GET',
	        url: url, 
	        success: function(transport) {
	            var res=transport["data"];
	            if(res!="errore"){
	            	var r=JSON.parse(res);
	            	var dizdati=JSON.parse(transport["dizdatialiq"]);
	            	//serve ad unire il dizionario nuovo che ho con quello generale che contiene tutte le label
	            	$.extend(dizdatialiq,dizdati);
		            var diz=r[label];
		            if(diz["exists"]=="no"){
		            	alert(label+ " does not exist in LAS");
		            	clearTimeout(timer);
		    	    	$("body").removeClass("loading");
		            	return;
		            }		            
		            //se il campione esiste allora faccio comparire la richiesta collegata
		            var html="<div class='divinterna' style='border-width:0.1em;border-color: black;'><span style='display:inline;font-size:1em;margin-left:2em;'>"+
		            	"<b>Title:</b> "+diz["titlereq"]+"&nbsp;&nbsp;&nbsp; <b>Description:</b> "+diz["descriptionreq"]+" &nbsp;&nbsp;&nbsp; "+
		            	"<b>Operator:</b> "+diz["ownerreq"]+"</span><p style='display:inline-block;margin:0px;float:right'><label style='font-size:1em;'>" +
		            	"Select</label><input id='check_"+String(idcheck)+"' class='check_select' type='checkbox' style='float:right;'><input type='hidden' class='request_id' " +
		            	"value='"+diz["idreq"]+"' /></p></div>";
		            html+="<div class='divtabelle'><table class='tabaliq' id='"+diz["labelaliq"]+"' border='1px'><thead><th>Label</th><th>Description</th><th>Operator</th>" +
		            	"<th>Info</th></thead><tbody align='center'><tr><td>"+diz["labelaliq"]+"</td><td>"+diz["descriptionaliq"]+"</td>" +
		            	"<td>"+diz["owneraliq"]+"</td><td><img src='"+base_url+"/ngs_media/img/info_icon.png' id='show_"+String(idcheck)+"' title='Show info' class='info_request' style='cursor:pointer;vertical-align:middle;' label='"+diz["labelaliq"]+"'</td></tr></tbody></table></div>";
		            $("#accordion").append(html);
		            $('#accordion').accordion('destroy');
		            $( "#accordion" ).accordion({
		        		header: ".divinterna",
		        		heightStyle: "content",
		        		collapsible: true,
		        		active:false
		        	});	            
		            var tab2=$("#"+diz["labelaliq"]).dataTable({
		        		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		        		"bAutoWidth": false
		        	});
		            //non uso il .on perche' non riuscirei a bloccare l'evento di apertura dell'accordion, quindi riassegno il .click
		            //solo a questo oggetto
		            $("#check_"+String(idcheck)).click(function (event) {
		            	event.stopPropagation();
		        		if($(this).is(":checked")){
		        			$(".check_select,#loadlabel").attr("disabled",true);
		        			$(this).attr("disabled",false);
		        			$("#select").attr("disabled",false);
		        		}
		        		else{
		        			$(".check_select,#loadlabel").attr("disabled",false);
		        			$("#select").attr("disabled",true);
		        		}
		        	});
		            $("#show_"+String(idcheck)).click(show_info);
		            idcheck++;
		            listalabel.push(diz["labelaliq"]);
	            }
	            else{
	            	alert("Error in loading data");
	            }
	            clearTimeout(timer);
		    	$("body").removeClass("loading");
	        },  
	        error: function(data) { 
	            alert("Error! Please, try again.\n" + data.status, "Warning");
	            clearTimeout(timer);
		    	$("body").removeClass("loading");
	        }
	    });
	}
}
