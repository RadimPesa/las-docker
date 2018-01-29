var label="";
var genid="";
var trtabsample="";
var failed=false;
var indicetab=1;
//chiave il genid e valore un dizionario con dentro tutti i dati inseriti nella schermata
var diztot={};
//lista per mantenere i genid nell'ordine in cui sono stati inseriti i valori collegati
var lisgen=[];

jQuery(document).ready(function(){
    var tab=$("#tab_aliq").dataTable({
		"aLengthMenu": [[1, 25, 50, 100, -1], [1, 25, 50, 100, "All"]],
		"bAutoWidth": false,
		"aoColumnDefs": [
		    { "bSortable": false, "aTargets": [ 4,5 ] },
		    { "bVisible": false, "aTargets": [ 6] },
		]
	});
    
    $("#tab_fin").dataTable({
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false
	});
    
    tab.$("tr").click(select_sample);
    
    $("#confirm_only,#confirm_finish").click(confirm_values);
    
    //$("#associate").click(associateFiles);
    
    $("#date").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
    
    $("#instrument").change(instrument_changed);
    
    $(".radiobutton").change(radio_changed);    	
    
    $( document ).on('click', '.ui-icon-search', function(){
        rowData = jQuery("#tab_aliq").dataTable().fnGetData($(this).parent().parent()[0]);
        var posFile = jQuery("#tab_aliq").dataTable().fnGetPosition($(this).parent().parent()[0]);
        $('#rowFile').val(posFile);
        var filelistSample = $.parseJSON(rowData[6]);
        $('.filediv_dialog').empty();
        for (var i=0; i<filelistSample.length; i++){
            $('.filediv_dialog').append('<input type="checkbox" name="filesample" value="' + filelistSample[i] + '">' + filelistSample[i]+ '<br>');
        }
        $("#viewfile_dialog").dialog("open");
    });
    
    $("#viewfile_dialog").dialog({
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
                    var tabella=jQuery("#tab_aliq").dataTable();
                    var posFile = $('#rowFile').val();
                    tabella.fnUpdate(JSON.stringify(finalList), parseInt(posFile), 6 );
                    if (finalList.length==0){
                    	tabella.fnUpdate('', parseInt(posFile), 4 );
                    }
                    //devo cancellare gli eventuali file anche nel dizionario generale riepilogativo                        
                    var datirigatr=tabella.fnGetNodes(parseInt(posFile));
                    //in datiriga ho l'oggetto tr
                    var gen=$(datirigatr).find("td input.inputgen").val();
                    var datiriga=tabella.fnGetData(parseInt(posFile));
                    //in datiriga[6] ho il json della lista con i nomi dei file caricati
                    var listfiles=datiriga[6];
                    if (gen in diztot){
                    	var diztemp=diztot[gen];
                    	diztemp["files"]=listfiles;
                    	diztot[gen]=diztemp;
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
    });
    
    //Quando si clicca per confermare tutto parte la POST al server
	$("#save").click(function(event){
		event.preventDefault();
		//vuol dire che la lista delle aliquote sotto e' vuota
		if(Object.size(diztot)==0){
			alert("Please insert data for a sample at least");
		}
		else{			
			var titolo=$("#titoloreq").val();
			var descr=$("#descrreq").val();
			$("#titolodialog").val(titolo);
			$("#id_notes").val(descr);
			$("#id_notes").focus();
			jQuery( "#dialogTitle" ).dialog({
	            resizable: false,
	            height:340,
	            width:380,
	            modal: true,
	            draggable :false,
	            buttons: {
	                "OK": function() {
	                	var description=$("#id_notes").val().trim();	                	
	                    jQuery( this ).dialog( "close" );
	        			var timer = setTimeout(function(){$("body").addClass("loading");},500);
	        			//comunico la struttura dati al server
	        	    	var data = {
	    	    			salva:true,	        	    			
	    	    			//prendo direttamente dal dialog il valore del titolo
	    	    			titleexp:$("#titolodialog").val(),
	    	    			//e' la descrizione generica della richiesta
	    	    			description:description,
	    	    			dizdata:JSON.stringify(diztot),
	    					lisgen:JSON.stringify(lisgen)
	        		    };
	        	    	
	        	    	var url=base_url+"/execute_experiment/save/";
	        			$.post(url, data, function (result) {
        		    		clearTimeout(timer);
        			    	$("body").removeClass("loading");
        		    		$("#upload_sample_file").append("<input type='hidden' name='conferma' />");	    	
        		    		$("#upload_sample_file").submit();	        		    	
	        			});
	                },
	                "Cancel": function() {
	                    jQuery( this ).dialog( "close" );
	                }
	            }
	        });						
		}
	});	
});

function radio_changed(){
	var lisradio=$(".radiobutton:checked");
	for (var i=0;i<lisradio.length;i++){
		var valore=$(lisradio[i]).val();
		//anche se c'e' un solo Failed blocco subito gli altri campi
		if(valore=="Failed"){
    		$("#tableform").find("input:text, select").attr("disabled",true);
    		failed=true;
    		break;
    	}
	}    	
	if(valore=="Ok"){
		$("#tableform").find("input:text, select").attr("disabled",false);
		failed=false;
	}
}

function instrument_changed(){
	var strumento=$("#instrument option:selected").val();
	if(strumento=="NS500_140"){
		$("#sampleidbso").attr("disabled",false);		
	}
	else {
		$("#sampleidbso").attr("disabled",true);
	}
}

function select_sample(event){
	var tab=$("#tab_aliq").dataTable();
	$(tab.fnSettings().aoData).each(function (){
		$(this.nTr).removeClass('row_selected');
	});
	$(event.target.parentNode).addClass('row_selected');
	var labelscelta=$(event.target.parentNode).children("td.label").text().trim();
	genid=$(event.target.parentNode).children("td.label").children("input.inputgen").val();
	trtabsample=event.target.parentNode;
	var volume=$(event.target.parentNode).children("td.operator").children("input.takenvol").val();
	$("#tdvolumefornito").text(volume);
	if(labelscelta!=label){
		label=labelscelta;
		//cancello i dati inseriti per il campione precedente
		$("#tableform .da_canc").val("");
		$("#tableform").find("select option[value='']").attr("selected","selected");
		$("#exhausted").attr("checked",false);
		//assegno agli altri campi della tabella il valore gia' caricato in precedenza, se c'e'
		if(label in dizvalexp){
			//mi occupo degli input text
			var listainput=$("#tableform input:text");
			for (var j=0;j<listainput.length;j++){
				var tag=$(listainput[j]).attr("tag");
				if(tag in dizvalexp[label]){
					$(listainput[j]).val(dizvalexp[label][tag]);
				}
			}
			var dizradio={};
			if("Purity" in dizvalexp[label]){
				dizradio["purity"]=dizvalexp[label]["Purity"];
			}
			if("Quantity" in dizvalexp[label]){
				dizradio["quantity"]=dizvalexp[label]["Quantity"];
			}
			if("Fragment distribution" in dizvalexp[label]){
				dizradio["distribution"]=dizvalexp[label]["Fragment distribution"];
			}
			for(var name in dizradio){
				$("input[name="+name+"][value="+dizradio[name]+"]").attr("checked","checked");
			}
			//chiamo la funzione per bloccare o meno gli input se i controlli di qualita' sono falliti 
			radio_changed();
			
			instrument_changed();
			
			var dizselect={};
			if("Assay" in dizvalexp[label]){
				dizselect["assay"]=dizvalexp[label]["Assay"];
			}
			if("Sample treatment" in dizvalexp[label]){
				dizselect["treatment"]=dizvalexp[label]["Sample treatment"];
			}
			if("Instrument" in dizvalexp[label]){
				dizselect["instrument"]=dizvalexp[label]["Instrument"];
			}
			if("Run chemistry" in dizvalexp[label]){
				dizselect["chemistry"]=dizvalexp[label]["Run chemistry"];
			}
			for(var name in dizselect){
				$("#"+name+" option[value="+dizselect[name]+"]").attr("selected","selected");
			}
			//per l'esaurito
			if("Exhausted" in dizvalexp[label]){
				if (dizvalexp[label]["Exhausted"]=="True"){
					$("#exhausted").attr("checked",true);
				}
			}
		}
	}
}

function confirm_values(){
	var idtasto=$(this).attr("id");
	var concludi=false;
	if (idtasto=="confirm_finish"){
		concludi=true;
	}
	var regex=/^[0-9]+$/;
	var diztemp={};
	
	if(label==""){
		alert("Please select a sample in the table");
		return;
	}
	var labelfinale=label;
	
	if (!($("input[name=purity]").is(":checked"))){
		alert("Please check purity");
		return;
	}
	var pur=$("input[name=purity]:checked").val();
	diztemp["Purity"]=pur;
	if (!($("input[name=quantity]").is(":checked"))){
		alert("Please check quantity");
		return;
	}
	var quant=$("input[name=quantity]:checked").val();
	diztemp["Quantity"]=quant;
	if (!($("input[name=distribution]").is(":checked"))){
		alert("Please check fragment distribution");
		return;
	}
	var distr=$("input[name=distribution]:checked").val();
	diztemp["Fragment distribution"]=distr;
	
	if(!($("#volumeusato").is(":disabled"))){
		//non lo faccio ricadere nella casistica degli input numerici, perche' il volume va sempre messo, non solo alla fine
		var volusato=$("#volumeusato").val().trim();
		if(volusato==""){
			alert("Please insert value for used volume");
			return;
		}
		else{
			if(!regex.test(volusato)){
				alert("You can only insert integer number. Please correct value for used volume");
				return;
			}
		}
		diztemp["Used volume"]=volusato;
	}
	
	var esaurita="False";
	if($("#exhausted").is(":checked")){
		esaurita="True";
	}
	diztemp["Exhausted"]=esaurita;
	
	//solo se l'esperimento e' riuscito ha senso controllare questi campi
	if(!failed){
		//e' una serie di input con valori numerici come il volume e la cluster density
		var lisvalnum=$(".numvalue");
		for (var i=0;i<lisvalnum.length;i++){
			if(!($(lisvalnum[i]).is(":disabled"))){
				var numero=$(lisvalnum[i]).val().trim();
				var id=$(lisvalnum[i]).attr("id");
				var nomelabel=$("label[for="+id+"]").text();
				var labfin=nomelabel.substr(0,nomelabel.length-2).toLowerCase();
				if((numero=="")&&(concludi)){
					alert("Please insert value for "+labfin);
					return;
				}
				else if((numero!="")){
					if(!regex.test(numero)){
						alert("You can only insert integer number. Please correct value for "+labfin);
						return;
					}
				}
				var nome=$(lisvalnum[i]).attr("name");
				diztemp[nome]=numero;
			}
		}
		
		var assay=$("#assay option:selected").val();
		if((assay=="")&&(concludi)){
			alert("Please select an assay");
			return;
		}
		if(assay!=""){
			labelfinale+="_"+assay;
		}
		diztemp["Assay"]=assay;
		
		var treatment=$("#treatment option:selected").val();
		if((treatment=="")&&(concludi)){
			alert("Please select a sample treatment");
			return;
		}
		if(treatment!=""){
			labelfinale+="_"+treatment;
		}
		diztemp["Sample treatment"]=treatment;
		
		var pack=$("#pack").val().trim();
		if((pack=="")&&(concludi)){
			alert("Please insert pack slip library prep");
			return;
		}
		diztemp["Pack slip"]=pack;
		
		var library=$("#library").val().trim();
		if((library=="")&&(concludi)){
			alert("Please insert library name");
			return;
		}
		diztemp["Library name"]=library;
		
		var dd=$("#date").val().trim();
		if((dd=="")&&(concludi)){
			alert("Please insert value for date");
			return;
		}
		else if((dd!="")){
			var bits =dd.split('-');
			var d = new Date(bits[0], bits[1] - 1, bits[2]);
			var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
			if (!booleano){
				alert("Incorrect format for date: it should be YYYY-MM-DD");
				return;
			}
		}
		diztemp["Date"]=dd;
		
		var instrument=$("#instrument option:selected").val();
		if((instrument=="")&&(concludi)){
			alert("Please select an instrument");
			return;
		}
		diztemp["Instrument"]=instrument;
		
		if(!($("#sampleidbso").is(":disabled"))){
			var sampleidbso=$("#sampleidbso").val().trim();
			if((sampleidbso=="")&&(concludi)){
				alert("Please insert value for sample ID BSO");
				return;
			}
			else{
				diztemp["Sample ID BSO"]=sampleidbso;
			}
		}
		
		var chemistry=$("#chemistry option:selected").val();
		if((chemistry=="")&&(concludi)){
			alert("Please select run chemistry");
			return;
		}
		diztemp["Run chemistry"]=chemistry;
		
		var flowcell=$("#flowcell").val().trim();
		if(flowcell!=""){
			diztemp["Lot n. flowcell"]=flowcell;
		}
		
		var cartridge=$("#cartridge").val().trim();
		if(cartridge!=""){
			diztemp["Lot n. reagent cartridge"]=cartridge;
		}
		
		var buffer=$("#buffer").val().trim();
		if(buffer!=""){
			diztemp["Lot n. buffer"]=buffer;
		}
		
		var box=$("#box").val().trim();
		if(box!=""){
			diztemp["Lot n. accessory box"]=box;
		}
		//la cluster density rientra tra i numeri e quindi l'ho gia' controllata prima
		
		var pm=$("#pm").val().trim();
		if((pm=="")&&(concludi)){
			alert("Please insert pM loaded");
			return;
		}
		diztemp["pM loaded"]=pm;
		
		var run=$("#run").val().trim();
		if((run=="")&&(concludi)){
			alert("Please insert run name");
			return;
		}
		diztemp["Run name"]=run;
		
		diztemp["labelfinale"]=labelfinale;
		
		if(concludi){
			//devo fare la differenza tra il volume fornito e quello usato per avere il vol rimanente da passare alla biobanca
			var volforn=parseFloat($("#tdvolumefornito").text());
			var volusato=parseFloat(diztemp["Used volume"]);
			var volrimanente=volforn-volusato;
			if(volrimanente<0){
				volrimanente=0;
			}
			diztemp["volrimanente"]=String(volrimanente);
		}
		
		diztemp["Failed"]="False";
		var fallito="No";
	}
	else{
		diztemp["Failed"]="True";
		labelfinale="";
		var fallito="Yes";
	}
	diztemp["label"]=label;	
	diztemp["description"]=$(trtabsample).children("td.description").text();
	diztemp["Finished experiment"]="False";
	if(concludi){
		diztemp["Finished experiment"]="True";
	}
	
	diztemp=associa_file(diztemp);
	
	var oTable=$("#tab_fin").dataTable();
	if(genid in diztot){
		//di questo campione avevo gia' inserito i suoi dati
		var dizappoggio=diztot[genid];
		//prendo l'indice della riga della tabella da aggiornare
		var indice=dizappoggio["indice"];
		diztemp["indice"]=indice;
		//per aggiornare il contenuto di una cella (nuovo valore, riga, colonna)
		oTable.fnUpdate(labelfinale,(indice-1),2);
		oTable.fnUpdate(fallito,(indice-1),3);
	}
	else{
		oTable.fnAddData( [indicetab, label, labelfinale,fallito]);
		diztemp["indice"]=indicetab;
		indicetab+=1;
	}
	
	diztot[genid]=diztemp;
	
	dizvalexp[label]=diztemp;
	//se il gen non e' gia' in lista, lo metto
	if($.inArray(genid, lisgen)==-1){
		lisgen.push(genid);
	}
	//faccio comparire il simbolo di eseguito nella tabella
	if(concludi){
		$(trtabsample).children("td.foto").children("img.confirm_end").css("display","");
		$(trtabsample).children("td.foto").children("img.confirm_partial").css("display","none");
	}
	else{
		$(trtabsample).children("td.foto").children("img.confirm_partial").css("display","");
		$(trtabsample).children("td.foto").children("img.confirm_end").css("display","none");
	}
}

function associa_file(diztemp){
    var currfiles = $('input[type=file]:last')[0];
    var filelist = currfiles.files;
    var tab=$("#tab_aliq").dataTable();
    var indice=tab.fnGetPosition(trtabsample);
    tab.fnUpdate( "", indice, 4 );
    filenames = [];
    if(filelist.length!=0){
	    for (var i=0; i<filelist.length; i++){
	        filenames.push(filelist[i].name);
	    }	    
	    tab.fnUpdate( JSON.stringify(filenames), indice, 6 );
	    tab.fnUpdate( '<span class="ui-icon ui-icon-search"></span>', indice, 4 );
	
	    //var item = $(currfiles).clone(true);
	    $(currfiles).hide();
	    //$('#filelist').append(item);
	    $("#filelist").append("<input id='currentfile' type='file' name='file' class='file' multiple />");
	    diztemp["files"]=JSON.stringify(filenames);
    }
    return diztemp;
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
