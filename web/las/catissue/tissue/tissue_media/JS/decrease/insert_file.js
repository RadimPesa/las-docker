var aliquots = []
var aliquot_warnings = 0;
var listaappoggio=[];
var contatore=1;
//chiave l'id dell'esperimento e valore il tag scelto dall'utente
var experimenttag={};

// init document
jQuery(document).ready(function(){
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Experiment","aliquote_fin");
	}
	else{
		aggiorna_dati();		
	}		
	
	$(".classetastofile").click(function(){
		$("#currentfile").click();
	});
	
	$("#currentfile").change(function(){
		//var files = $('#currentfile')[0].files;
		var files = $('input[type=file]:first')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","	        
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
	});
	
    infoFile();
    initDialog();
});

function aggiorna_dati(){
	//solo se nella tabella ho delle aliquote
	var listarighe=$("#samples tr");
	if (listarighe.length>1){
		var lbarc="";
		var lgen="";
		var lis_pezzi_url=[];
		var utente=$("#actual_username").val();
		var url=base_url+"/api/storage/tube/";
		//per dare il valore all'nth-child devo tenere conto che a questo punto sono presenti tutte le colonne della tabella. Quelle nascoste non sono ancora
		//state tolte
		var listagen=$("#samples tr").children(":nth-child(4)").not("th");
		//prendo i barcode
		var listabarc=$("#samples tr").children(":nth-child(10)").not("th");
		//prendo i campi relativi alla piastra
		var listapias=$("#samples tr").children(":nth-child(8)").not("th");
		//prendo i campi relativi alla posizione della provetta
		var listapos=$("#samples tr").children(":nth-child(9)").not("th");
		//prendo i campi relativi alla posizione della piastra
		var listapospiastra=$("#samples tr").children(":nth-child(7)").not("th");
		//prendo i campi relativi al rack
		var listarack=$("#samples tr").children(":nth-child(6)").not("th");
		//prendo i campi relativi al freezer
		var listafreezer=$("#samples tr").children(":nth-child(5)").not("th");
		//prendo i campi relativi alla disponibilita' della prima tabella
		//listadisp=$("#samples tr").children(":nth-child(9)").not("th");
		for (var i=0;i<listagen.length;i++){
			//mi da' il gen attuale
			var gen=$(listagen[i]).text();
			lgen=lgen+gen+"&";
			lgen = lgen.replace(/#/g, "%23");
			if (lgen.length>2000){
	            lis_pezzi_url.push(lgen);
	            lgen="";
			}
		}
		if (lgen==""){
			lgen="-";
			lis_pezzi_url.push("-");
		}
		else{
			lis_pezzi_url.push(lgen);
		}
		var timer = setTimeout(function(){$("body").addClass("loading");},1000);
		for (var j=0;j<lis_pezzi_url.length;j++){
			urlst=url+lis_pezzi_url[j]+"/"+utente;
			$.getJSON(urlst,function(d){
				if (d.data!="errore"){
					diz=JSON.parse(d.data);
					if(Object.size(diz)!=0){
						//scrivo nel campo apposito l'indicazione della posizione della provetta
						for(var i=0;i<listagen.length;i++){
							var gen=String($(listagen[i]).text().trim());
							var listaval=diz[gen];
							if(listaval!=undefined){
								var val=listaval.split("|");
																
								//solo se non e' gia' in lista lo inserisce
								if(($.inArray(val[0].toUpperCase(),listaappoggio)==-1)&&(val[0]!="None")){
									listaappoggio.push(val[0].toUpperCase());	
								}
								if(($.inArray(val[2].toUpperCase(),listaappoggio)==-1)&&(val[2]!="None")){
									listaappoggio.push(val[2].toUpperCase());
								}
								if(($.inArray(val[4].toUpperCase(),listaappoggio)==-1)&&(val[4]!="None")){
									listaappoggio.push(val[4].toUpperCase());
								}
								if(($.inArray(val[5].toUpperCase(),listaappoggio)==-1)&&(val[5]!="None")){
									listaappoggio.push(val[5].toUpperCase());
								}
								
								$(listabarc[i]).text(val[0]);
								$(listapos[i]).text(val[1]);
								$(listapias[i]).text(val[2]);
								$(listapospiastra[i]).text(val[3]);
								$(listarack[i]).text(val[4]);
								$(listafreezer[i]).text(val[5]);
							}
						}
					}
					//lo faccio solo una volta alla fine del ciclo generale
					if (contatore==lis_pezzi_url.length){
						var oTable= $("#samples").dataTable( {
					        "bProcessing": true,         
					        "bAutoWidth": false ,
					        "aaSorting": [[1, 'asc']],
					        "aoColumnDefs": [
					            { "bVisible": false, "aTargets": [ 0, 11] },
					            { "bSortable": false, "aTargets": [ 2, 12 ] }
					        ],       
					    });
						oTable.$(".nofiles").click(function(){
							if($(this).is(":checked")){
								//se selziono il no files blocco la possibilita' di caricare file per quel campione
								$(this).parent().parent().find(".sel_aliq").attr("disabled",true);
								$(this).parent().parent().find(".sel_aliq").attr("checked",false);
							}
							else{
								$(this).parent().parent().find(".sel_aliq").attr("disabled",false);
							}
						});
						
						clearTimeout(timer);
						$("body").removeClass("loading");
					}
				}
				else{
					alert("Problems while interacting with storage");
				}
				contatore++;
			});
		}
	}
	else{
		$("#samples").dataTable( {
	        "bProcessing": true,         
	        "bAutoWidth": false ,
	        "aaSorting": [[1, 'asc']],
	        "aoColumnDefs": [
	            { "bVisible": false, "aTargets": [ 0,11] },
	            { "bSortable": false, "aTargets": [ 2, 12 ] }
	        ],       
	    });
	}	
}

function addFile (){	
    $("#form_measures input[type=file]:last").live("change", function(){
    //$("#form_measures").on("change", " input[type=file]:last", function(){
        var item = $(this).clone(true);
        var fileName = $(this).val();
        if(fileName){
            $(this).parent().append(item);
        }  
    });
}

// read data from the table after post of file
function readTable(){
	piena=false;
    jQuery.each( jQuery("#samples").dataTable().fnGetNodes(), function(i, row){
        var d = jQuery("#samples").dataTable().fnGetData(i);
        var nofile= $(row).find('input.nofiles').prop('checked');
        if(nofile==true){
        	piena=true;
        }
        var files = [];
        var dataf = null;
        if (d[11] != ""){
            dataf = d[11];
            piena=true;
        }
        else{
            dataf = JSON.stringify(files);
        }
        var filetype="";
        if (d[0] in experimenttag){
        	filetype=experimenttag[d[0]];
        }
        if(filetype==undefined){
        	filetype="";
        }
        aliquots.push({'idAliquotExperiment':d[0], 'nofile':nofile, 'files': dataf,'filetype':filetype});
    });
    return piena;
}

function submitResults(){
    var piena=readTable();
    if(!piena){
    	alert("Please execute at least an action");
    	return;
    }
    $('#aliquots_list').val(JSON.stringify(aliquots));
    $('#upload_sample_file').submit();
}

function associateFiles(){
    var currfiles = $('input[type=file]:first')[0];
    var filelist = currfiles.files;
    filenames = [];
    if(filelist.length!=0){
	    for (var i=0; i<filelist.length; i++){
	        filenames.push(filelist[i].name);
	    }
	    $.each( jQuery("#samples").dataTable().fnGetNodes(), function(i, row){
	        if ($(row).find('[name=select]').prop('checked')){
	            $("#samples").dataTable().fnUpdate( JSON.stringify(filenames), i, 11,false,true );
	            $("#samples").dataTable().fnUpdate( '<span class="ui-icon ui-icon-search"></span>', i, 12,false,true );
	            $(row).find('[name=select]').prop('checked', false);
	            $(row).find(".nofiles").attr("disabled",true);
	            //prendo l'id dell'esperimento
	            var d = jQuery("#samples").dataTable().fnGetData(i);
	            //prendo il tag scelto
	            var tag=$("#id_tag option:selected").val();
	            experimenttag[d[0]]=tag;
	        }
	    });
	
	    var item = $(currfiles).clone(true);
	    $('#filelist').append(item);
    }
    else{
    	alert("Please insert at least a file");
    }
}

function infoFile(){
    //$( document ).on('click', '.ui-icon-search', function(){
	$(".ui-icon-search").live("click", function(){
        //console.log($(this).parent().parent());
        var rowData = jQuery("#samples").dataTable().fnGetData($(this).parent().parent()[0]);
        var posFile = jQuery("#samples").dataTable().fnGetPosition($(this).parent().parent()[0]);
        $('#rowFile').val(posFile);
        var filelistSample = $.parseJSON(rowData[11]);
        $('.filediv_dialog').empty();
        for (var i=0; i<filelistSample.length; i++){
            $('.filediv_dialog').append('<span><input style="display:inline;" type="checkbox" name="filesample" value="' + filelistSample[i] + '"><span class="nomfile" style="cursor:pointer;">' + filelistSample[i]+ '</span></span><br>');
        }
        
        //faccio in modo di far sentire il click anche se e' sul testo del checkbox
		$(".nomfile").click(function(){
			var check=$(this).parent().children(":checkbox");
			if($(check).is(":checked")){
				$(check).removeAttr("checked");
			}
			else{
				$(check).attr("checked","checked");
			}
		});
        
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
                        var posFile = parseInt($('#rowFile').val());                        
                        jQuery("#samples").dataTable().fnUpdate(JSON.stringify(finalList), posFile, 11,false,true );
                        if (finalList.length==0){
                            $("#samples").dataTable().fnUpdate('', posFile, 12,false,true );
                            var rows=$("#samples").dataTable().fnGetNodes();
                            $(rows[posFile]).find(".nofiles").attr("disabled",false);
                            //$(row).find(".nofiles").attr("disabled",false);
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

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
