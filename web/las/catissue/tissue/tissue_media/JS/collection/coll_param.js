diztasti={};
dizvalpredef={};
dizsequencing={};
dizfish={};
var diztreat={};
lis_gene_wt=[]
lisfin=[];
selected_gene="";
var farmaci=false;
var lisfarmaci=[];
var lisfarmacilower=[];
var nome="";

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function chiudi_finestra(){
	window.close();
}

function salva_dati(){
	var tumore="";
	var caso="";
	var reopen=getUrlParameter("reopen");
	//se sono nella schermata di riapertura della collezione
	if (reopen=="Yes"){
		tumore=getUrlParameter("tumor");
		caso=getUrlParameter("case");
	}
	else{
		reopen="No";
		//salvo il dizionario nel local storage
		localStorage.setItem("clinicalfeat", JSON.stringify(lisfin));
	}
	var data={
			dati:JSON.stringify(lisfin),
			reopen:reopen,
			tumore:tumore,
			caso:caso,
			salva:true
	};
	var url=base_url+"/collection/param/";
	$.post(url, data, function (result) {
    	if (result == "failure") {
    		alert("Error");
    	}
    	$("#form_fin").append("<input type='hidden' name='final' />");
    	$("#form_fin").submit();
    });
}

function esegui_sequencing(){
	$("#selez").click(inseriscisottosequencing);
	var tab_gene=$("#table_genes").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Gene symbol" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
    	if(nRow.className.indexOf("gene_el")==-1){
        	nRow.className += " gene_el";
		}
        return nRow;
        }
    });
    
    var tab_mut=$("#table_mut").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Cosmic id" },
            { "sTitle": "AA mutation" },
            { "sTitle": "CDS mutation" }
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aaSorting": [[0, 'desc']],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
    	if(nRow.className.indexOf("mut_el")==-1){
        	nRow.className += " mut_el";
		}
        return nRow;
        }
    });
    
    var tab_fin=$("#table_fin").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
            },
            { "sTitle": "Cosmic id" },
            { "sTitle": "AA mutation" },
            { "sTitle": "CDS mutation" }
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aaSorting": [[1, 'desc']],
    });
    
    var tab_wt=$("#table_wt").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
            },
            { "sTitle": "Gene symbol" },
            { "sTitle": "" }
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aaSorting": [[1, 'desc']],
    });
    
    $('#search_gene').click(function(event){
        searchGene();        
    });
    
    $("#input_gene_sym").keypress(function(event){
		if ( event.which == 13 ) {
			searchGene();
		}
	});
    //per quando clicco sul check per dire che il gene e' wt
    $("#check_wt").click(function(){
    	if($(this).is(":checked")){
    		$("#div_wt").css("display","");
    		$("#div_tot").css("border","1px solid");
    		$("#div_tot").css("width","96%");
    		$("#div_tot").css("margin-left","1em");
    	}
    	else{
    		$("#div_wt").css("display","none");
    		$("#div_tot").css("border","");
    		$("#div_tot").css("width","100%");
    		$("#div_tot").css("margin-left","");
    	}
    });

    jQuery("#table_genes tbody").click(function(event) {    	
    	jQuery(jQuery('#table_genes').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
        });
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.gene_el")){
        	jQuery(event.target.parentNode).addClass('row_selected');
            var pos = jQuery("#table_genes").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
            var data = jQuery("#table_genes").dataTable().fnGetData(pos);
            selected_geneid = data[0];
            selected_gene = data[1];
            //se il check per il wt e' selezionato non chiamo la API per le mutazioni, ma metto direttamente il gene cliccato 
            //nella tabella finale
            if($("#check_wt").is(":checked")){
            	if(lis_gene_wt.indexOf(selected_gene)==-1){
            		tab_wt.fnAddData([null, selected_gene, "WT"]);
            		lis_gene_wt.push(selected_gene);
            		//devo togliere eventuali mutazioni gia' posizionate nella tabella sotto per quel gene
            		for(var chiave in dizsequencing){
            			var stringa=dizsequencing[chiave];
            			//nel posto 0 ho il nome del gene
            			var spli=stringa.split("|");
            			if(selected_gene==spli[0]){
            				delete dizsequencing[chiave];
            			}
            		}
            		//devo ridisegnare il datatable di sotto
            		tab_fin.fnClearTable();
            		for(var chiave in dizsequencing){
            			var stringa=dizsequencing[chiave];
            			//nel posto 0 ho il nome del gene
            			var spli=stringa.split("|");
            			tab_fin.fnAddData([null,chiave,spli[1],spli[2]]);
            		}
            	}
            }
            else{
            	searchMut(selected_geneid);
            }
        }        
    });
    
    /* Add event listener for deleting row  */
    $("#table_wt tbody td.control_center img").live("click", function () {
        var gene = $($($(this).parents('tr')[0]).children()[1]).text();
        for(var i=0;i<lis_gene_wt.length;i++){
        	if(lis_gene_wt[i]==gene){
        		lis_gene_wt.splice(i,1);
        		break;
        	}
        }
        var nTr = $(this).parents('tr')[0];
        $("#table_wt").dataTable().fnDeleteRow( nTr );
    } );
}

function esegui_fish(){
	$("#selez").click(inseriscisottofish);
	var tab_gene=$("#table_genes").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Gene symbol" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
    	if(nRow.className.indexOf("gene_el")==-1){
        	nRow.className += " gene_el";
		}
        return nRow;
        }
    });
    
    var tab_fin=$("#table_fin").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
            },
            { "sTitle": "Gene" },
            { "sTitle": "Ratio to centromere" }
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aaSorting": [[1, 'desc']],
    });
    
    $('#search_gene').click(function(event){
        searchGene();        
    });
    
    $("#input_gene_sym").keypress(function(event){
		if ( event.which == 13 ) {
			searchGene();
		}
	});
    
    jQuery("#table_genes tbody").click(function(event) {
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.gene_el")){
        	jQuery(event.target.parentNode).toggleClass('row_selected');            
        }        
    });
    
    /* Add event listener for deleting row  */
    $("#table_fin tbody td.control_center img").live("click", function () {
        var gene = $($($(this).parents('tr')[0]).children()[1]).text();
        delete dizfish[gene];
        var nTr = $(this).parents('tr')[0];
        $("#table_fin").dataTable().fnDeleteRow( nTr );
    } );
}

function esegui_tnm(){
	$(".check_tnm").click(function(){
		//deseleziono gli altri eventuali check box selezionati
		$(".check_tnm").not(this).removeAttr("checked");		
	});
}

function esegui_autocomplete(){
	$("#id_treat").focus();
    var tab_fin=$("#table_fin").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
            },
            { "sTitle": "Name" }
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    "aaSorting": [[1, 'desc']],
    });
    
    $("#id_treat").autocomplete({
    	source:base_url+'/ajax/drug/autocomplete/'
    });
    
    $("#selez_treat").click(seleziona_farmaco);
    
    $("#id_treat").keypress(function(event){
		if ( event.which == 13 ) {
			seleziona_farmaco();
		}
	});
    
    /* Add event listener for deleting row  */
    $("#table_fin tbody td.control_center img").live("click", function () {
        var farmaco = $($($(this).parents('tr')[0]).children()[1]).text();
        var listemp=diztreat[nome];
        for(var i=0;i<listemp.length;i++){
        	if(listemp[i]==farmaco){
        		listemp.splice(i,1);
        		break;
        	}
        }
        if (listemp.length==0){
        	delete diztreat[nome];
        }
        else{
        	diztreat[nome]=listemp;
        }
        var nTr = $(this).parents('tr')[0];
        $("#table_fin").dataTable().fnDeleteRow( nTr );
    } );
}

function seleziona_farmaco(){
	//chiamo la API per popolarmi la lista con i nomi dei farmaci solo se non l'ho gia' fatto
	if (!(farmaci)){
		var url =  base_url + '/api/getDrugs/';
	    jQuery.ajax({
	        type: 'GET',
	        url: url,
	        success: function(transport) {
	            $(transport).each(function(index, value){
	            	//mi ritorna una lista di dizionari che scandisco e da cui prendo solo il nome del farmaco
	                lisfarmacilower.push(value["name"].toLowerCase());
	                lisfarmaci.push(value["name"]);
	            }); 
	            farmaci=true;
                inserisci_in_tabella_treat();
	        }, 
	        error: function(data) { 
	            alert("Error! Please, try again.\n" + data.status, "Warning");
	        }
	    });
	}
	else{
		inserisci_in_tabella_treat();
	}
}

function inserisci_in_tabella_treat(){
	var farmaco=$("#id_treat").val();
	$("#id_treat").val("");
	$("#id_treat").focus();
	if (farmaco==""){
		alert("Please insert drug name");
		return;
	}
	//devo vedere se il farmaco inserito si trova nella lista dei farmaci possibili
	var indice=lisfarmacilower.indexOf(farmaco.toLowerCase());
	if(indice==-1){
		alert("Drug not recognized. Please change name.");
		return;
	}
	//devo vedere se ho gia' inserito questo farmaco nella tabella
	if(nome in diztreat){
		var listemp=diztreat[nome];
		var ind2=listemp.indexOf(lisfarmaci[indice]);
		if(ind2>-1){
			//interrompo qui perche' vuol dire che quel farmaco e' gia' stato inserito prima
			//e non lo devo piu' inserire nella tabella sotto 
			
			return;
		}
	}
	var tabsotto=$("#table_fin").dataTable();	
	var rowPos=tabsotto.fnAddData([null,lisfarmaci[indice]]);
	
	if(nome in diztreat){
		var listemp=diztreat[nome];
	}
	else{
		var listemp=new Array();
	}
	listemp.push(lisfarmaci[indice]);
	diztreat[nome]=listemp;
}

function searchGene(){
	jQuery('#table_mut,#table_genes').dataTable().fnClearTable();
    // send data
    geneName = jQuery('input[name=search_gene]').val();
    if (geneName == ''){
        alert("Please insert gene symbol");
        return;
    }
    selected_geneid = '';
    selected_gene = '';
    var url =  base_url + '/api/getGenes/' + geneName;
    jQuery.ajax({
        type: 'GET',
        url: url,
        success: function(transport) {
            $(transport).each(function(index, value){
                //jQuery('#table_genes').dataTable().fnClearTable();
                jQuery('#table_genes').dataTable().fnAddData([value['id_gene'], value['gene_name']]);
            });            
        }, 
        error: function(data) { 
            alert("Error! Please, try again.\n" + data.status, "Warning");
        }
    });
}

function searchMut(geneId){
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	//porto in secondo piano il dialog rispetto alla classo loading che aggiungo al body
	$(".ui-dialog").css("z-index","990");
    // send data
    var url =  base_url + '/api/getMutations/' + geneId;
    jQuery.ajax({
        type: 'GET',
        url: url,
        success: function(transport) {
            jQuery('#table_mut').dataTable().fnClearTable();
            $(transport).each(function(index, value){
                jQuery('#table_mut').dataTable().fnAddData([value['id_mutation'], value['aa_mut_syntax'], value['cds_mut_syntax']]);
            });
            var tab=$("#table_mut").dataTable();
            tab.$("tr").click(function(event) {
    			$(this).toggleClass('row_selected');    			
    	    });
            /* Add event listener for deleting row  */
    	    $("#table_fin tbody td.control_center img").live("click", function () {
    	        var id = $($($(this).parents('tr')[0]).children()[1]).text();
    	        delete dizsequencing[id];
    	        var nTr = $(this).parents('tr')[0];
    	        $("#table_fin").dataTable().fnDeleteRow( nTr );
    	    } );
            
            clearTimeout(timer);
    		$("body").removeClass("loading");
    		//rimetto in primo piano la dialog
    		$(".ui-dialog").css("z-index","1002");
        }, 
        error: function(data) { 
            alert("Error! Please, try again.\n" + data.status, "Warning");
        }
    });
}

function inseriscisottosequencing(){
	var tab=$("#table_mut").dataTable();
	var tabsotto=$("#table_fin").dataTable();
	//ho un vettore con le righe selezionate dall'utente
	var selezionati = fnGetSelected( tab );
	if (selezionati.length==0){
		alert("Please select a mutation");
	}
	else{
		for(var j=0;j<selezionati.length;j++){
			//solo se il gene non e' stato inserito nella lista di quelli che non hanno mutazioni
			if(lis_gene_wt.indexOf(selected_gene)==-1){
				var idmut=$(selezionati[j]).children(":nth-child(1)").text();
				//solo se non ho gia' messo la riga sotto
				if(!(idmut in dizsequencing)){
					var listadatitemp=new Array();
					//posto vuoto per la "X" della cancellazione
		 			listadatitemp.push(null)
					var listmp=new Array();
					//ci sono 3 colonne nella tabella sopra
					for (var k=0;k<3;k++){
						var figlio=":nth-child("+(k+1)+")";
						var dato=$(selezionati[j]).children(figlio).html();					
						listadatitemp.push(dato);
						var valore=$(selezionati[j]).children(figlio).text();
						listmp.push(valore);
					}
					var rowPos=tabsotto.fnAddData(listadatitemp);
					dizsequencing[listmp[0]]=selected_gene+"|"+listmp[1]+"|"+listmp[2];		
				}
				$(selezionati[j]).toggleClass('row_selected');
			}
		}
	}
}

function inseriscisottofish(){
	var tab=$("#table_genes").dataTable();
	var tabsotto=$("#table_fin").dataTable();
	//ho un vettore con le righe selezionate dall'utente
	var selezionati = fnGetSelected( tab );
	if (selezionati.length==0){
		alert("Please select a gene");
	}
	else{
		for(var j=0;j<selezionati.length;j++){
			var idgen=$(selezionati[j]).children(":nth-child(1)").text();
			//solo se non ho gia' messo la riga sotto
			if(!(idgen in dizfish)){
				var listadatitemp=new Array();
				//posto vuoto per la "X" della cancellazione
	 			listadatitemp.push(null)
				var listmp=new Array();
				var dato=$(selezionati[j]).children(":nth-child(1)").html();
				listadatitemp.push(dato);
				var valore=$(selezionati[j]).children(":nth-child(1)").text();
				listmp.push(valore);
				listadatitemp.push("<input type='number' class='input_fish' min=0 max=1000000000>");
					
				var rowPos=tabsotto.fnAddData(listadatitemp);
				dizfish[listmp[0]]="";		
			}
			$(selezionati[j]).toggleClass('row_selected');
		}
	}
}

//dato il nome di un parametro presente nella URL, restituisce il suo valore
function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) 
        {
            return sParameterName[1];
        }
    }
    return null;
}

function loadInfo(idtasto,nometasto){
    if (diztasti.hasOwnProperty(idtasto)){
        //gia' caricato precedentemente dal server
        crea_elementi(diztasti[idtasto],nometasto);
    }else{
    	var tum=window.opener.$("#id_Tumor_Type option:selected").val();
    	//se tum non c'e' vuol dire che ho aperto la pagina dei parametri passando dalla schermata
    	//per riaprire una collezione. Quindi tum lo trovo nei parametri della URL
    	if(tum==undefined){
    		tum = getUrlParameter("tumor");
    	}
        //da caricare dal server
        jQuery.ajax({
            url: base_url + "/api/getClinicalFeature/" + idtasto + "/"+tum+ "/",
                type: 'get',
                success: function(d) {
                	if (d.data!="err"){
                		crea_elementi(d,nometasto);
                		diztasti[idtasto]=d;
                	}                    
                    else{
                    	alert("Error in server API");
                    }
                }
        });
    }
}

function crea_elementi(d,nometasto){
	var lis = JSON.parse(d.data);
	
	var lisdiv=$("div.princ");
	//se ho cliccato su un valore della lista principale a sinistra, livello varra' 2
	var livello=parseInt(d.livello);		
	//elimino le div piu' a destra di quella attuale
	for(var i=(livello-1);i<lisdiv.length;i++){
		lisdiv[i].remove();
	}
	//devo scrivere dopo l'ultima div presente
	var lisdiv=$("div.princ");
	//se ho una lista di altri parametri clinici generali che fanno da madre ad altre categorie
	if(d.listamadri){
		var codhtml="<div class='princ' style='float:left;width:20%;margin-left:1em;'><fieldset class='fieldset'><legend>"+nometasto+
		"</legend><div><table style='margin-left: auto;margin-right: auto;'><tbody>";
		for(var j=0;j<lis.length;j++){
			var diz=lis[j];
			codhtml+="<tr><td><button class='button' style='width:100%;' onclick ='loadInfo(\""+diz["id"]+"\",\""+diz["name"]+"\");'>"+diz["name"]+"</button></td></tr>";  
		}
		codhtml+="</tbody></table></div></fieldset></div>";		
	}
	else{
		var codhtml="<div class='princ' style='float:left;width:20%;margin-left:1em;'><fieldset class='fieldset'><legend>"+nometasto+
		"</legend><div><table border='1px' style='margin-left: auto;margin-right: auto;width:100%;'><tbody>";
		//se ho una lista di parametri foglie	
		for(var j=0;j<lis.length;j++){
			var diz=lis[j];
			var listemp=diz["lisval"];
			dizvalpredef[diz["id"]]=listemp;
			var checked="";
			//serve nel caso clicchi di nuovo su quel tasto, allora devo vedere i checkbox gia' selezionati
			for (var k=0;k<lisfin.length;k++){
				var diztemp=lisfin[k];
				if(diztemp["idfeat"]==diz["id"]){
					checked="checked='checked'";
					break;
				}
			}
			var classespan="span_feat";
			var disabled="";
			if((diz["type"]=="List")&&(listemp.length==0)){
				disabled="disabled='disabled'";
				classespan="";
			}
			//se il parametro e' di tipo TextTumor e la lista e' vuota non lo faccio vedere perche' vuol dire che quel parametro ha senso
			//per un altro tumore
			var blocca=false;
			if((diz["type"]=="TextTumor")&&(listemp.length==0)){
				blocca=true;
			}
			if(!(blocca)){
				codhtml+="<tr><td><input type='checkbox' class='check_feat' "+checked+" "+disabled+" idfeat='"+diz["id"]+"' tipo='"+diz["type"]+"' unit='"+diz["unit"]+"' value='"+diz["name"]+"'><span class='"+classespan+"' >"+diz["name"]+"</span></td></tr>";
			}
		}
		codhtml+="</tbody></table></div></fieldset></div>";
		if(lis.length==0){
			codhtml="";
		}
	}
	$(lisdiv[lisdiv.length-1]).after(codhtml);
	$(":checkbox.check_feat").click(function(){valori_checkbox(this);});
	//faccio in modo di far sentire il click anche se e' sul testo del checkbox
	$(".span_feat").click(function(){
		var check=$(this).parent().children(":checkbox");
		if($(check).is(":checked")){
			$(check).removeAttr("checked");
		}
		else{
			$(check).attr("checked","checked");
		}
		valori_checkbox(check);
	});
}

function isInteger(x) {
    return x % 1 === 0;
}

function valori_checkbox(check){
	var tipo=$(check).attr("tipo");
	nome=$(check).attr("value");
	var unit=$(check).attr("unit");
	var idfeat=$(check).attr("idfeat");
	if($(check).is(":checked")){
		$("#fList,#pdialog").empty();
		//devo far comparire l'input box per inserire i valori
		//in base al tipo della feature, l'input box sara' diverso
		var larg=300;
		var altezza=250;
		var resiz=false;
		var width="";
		var html="";
		if (tipo=="Date"){
			$("#pdialog").append("Select date:");
			html+="<tr><td>";
			html+="<input type='text' id='iddata' size='12' />";
			html+="</td></tr>";			
		}
		else if(tipo=="Year"){
			var d = new Date();
			var n = d.getFullYear();
			$("#pdialog").append("Insert year (yyyy):");
			html+="<tr><td>";
			html+="<input type='number' value='1900' id='id_anno' min='1900' max='"+String(n)+"' />";
			html+="</td></tr>";
		}
		else if((tipo=="Text")||(tipo=="TextTumor")){
			$("#pdialog").append("Insert value:");
			html+="<tr><td>";
			html+="<input type='text' id='id_text' maxlength='140' />&nbsp&nbsp"+unit;
			html+="</td></tr>";	
		}
		//se e' un numero allora metto un minimo e un massimo
		else if(tipo=="Number"){
			$("#pdialog").append("Insert value:");
			html+="<tr><td>";
			html+="<input type='number' id='id_num' min='1' max='1000000000' />&nbsp&nbsp"+unit;
			html+="</td></tr>";
		}
		else if(tipo=="List"){
			$("#pdialog").append("Select value:");
			html+="<tr><td>";
			var lisval=dizvalpredef[idfeat];
			html+="<select id='id_lista' >";
			for(var kk=0;kk<lisval.length;kk++){
				var dizte=lisval[kk];
				if(dizte["value"].length>30){
					//aumento la larghezza della dialog perche' le liste hanno valori lunghi
					larg=500;
				}
				html+="<option value="+dizte["id"]+">"+dizte["value"]+"</option>";
			}
			html+="</td></tr>";	
		}
		else if(tipo=="RadioList"){		
			$("#pdialog").append("Choose value:");
			html+="<tr><td align='center'>";
			var lisval=dizvalpredef[idfeat]; 
			for(var kk=0;kk<lisval.length;kk++){
				var dizte=lisval[kk];
				if(dizte["value"].length>30){
					//aumento la larghezza della dialog perche' le liste hanno valori lunghi
					larg=500;
				}
				html+="<input type='radio' style='display:inline;' value='"+dizte["value"]+"' name='choose'>"+dizte["value"]+"&nbsp&nbsp";
			}			
			html+="</td></tr>";			
		}
		else if(tipo=="Sequencing"){
			larg=900;
			altezza=800;
			resiz=true;
			html+="<table style='margin-left:4%;'><tbody><tr><td><b>Gene:</b></td><td><input id='input_gene_sym' type='text' name='search_gene' maxlength='45'>"+
				"<input style='margin-left:1em;' id='search_gene' class='button' type='submit' value='Search gene symbol'></td></tr></tbody></table>";
			html+="<div style='float:left;width:90%;padding-left:4%;padding-top:1%;padding-bottom:1em;'><table id='table_genes' style='float:left'><tbody></tbody>"+
				"</table></div>" +
				"<div id='div_tot' style='float:left;width:100%;' ><div style='float:left;padding-left:4%;'><input type='checkbox' id='check_wt' style='margin-left:0px;' >No mutations detected (WT)</div>" +
				"<div id='div_wt' style='width:90%;float:left;padding-left:4%;margin-top:1%;display:none;'><table id='table_wt' style='float:left'><tbody></tbody></table></div></div>"+
				"<div style='float:left;width:100%;'><br><div style='float:left;width:90%;padding-left:4%;'>"+
				"<table id='table_mut' style='float:left'><tbody></tbody></table></div>" +				
				"<br><div style='float:left;width:90%;text-align:center;'><input id='selez' class='button' type='button' style='display: inline;'  value='↓'>" +
				"</div><br><div style='float:left;width:90%;padding-left:4%;padding-top:2%;' align='center'>Selected mutations:</div><div style='float:left;width:90%;padding-left:4%;'>"+
				"<table id='table_fin' style='float:left'><tbody></tbody></table></div>";
			width="100%";
		}
		else if(tipo=="FISH"){
			resiz=true;
			larg=900;
			altezza=500;
			html+="<table style='margin-left:4%;'><tbody><tr><td><b>Gene:</b></td><td><input id='input_gene_sym' type='text' name='search_gene' maxlength='45'>"+
			"<input style='margin-left:1em;' id='search_gene' class='button' type='submit' value='Search gene symbol'></td></tr></tbody></table>";
			html+="<div style='float:left;width:90%;padding-left:4%;padding-top:1%'><table id='table_genes' style='float:left'><tbody></tbody>"+
			"</table></div><div style='float:left;width:100%;'><div style='float:left;width:90%;padding-left:4%;'>"+
			"<div style='float:left;width:100%;text-align:center;margin-bottom:2%;'><input id='selez' class='button' type='button' style='display: inline;'  value='↓'>" +
			"</div><table id='table_fin' style='float:left'><tbody></tbody></table></div>";
			width="100%";
		}
		else if(tipo=="TNM"){
			resiz=true;
			larg=1000;
			html+="<table border='1px' style=''><th>Prefix modifiers</th><th>Mandatory parameters</th><th>Other parameters</th>"+
			"<tr><td><input type='checkbox' value='c' class='check_tnm'><span style='margin-right:1em;'>c</span><input type='checkbox' value='p' class='check_tnm'><span style='margin-right:1em;'>p</span>" +
			"<input type='checkbox' value='y' class='check_tnm'><span style='margin-right:1em;'>y</span><input type='checkbox' value='r' class='check_tnm'><span style='margin-right:1em;'>r</span>" +
			"<input type='checkbox' value='a' class='check_tnm'><span style='margin-right:1em;'>a</span><input type='checkbox' value='u' class='check_tnm'><span style='margin-right:1em;'>u</span></td>" +
			"<td><select id='t_tnm' style='margin-right:1em;'><option>Tx</option><option>Tis</option><option>T0</option><option>T1</option><option>T2</option>" +
			"<option>T3</option><option>T4</option></select>" +
			"<select id='n_tnm' style='margin-right:1em;'><option>Nx</option><option>N0</option><option>N1</option><option>N2</option><option>N3</option></select>" +
			"<select id='m_tnm'><option>M0</option><option>M1</option></select>" +
			"<td>G&nbsp<select id='g_tnm' style='margin-right:1em;'><option value='No'>---</option><option>G1</option><option>G2</option><option>G3</option><option>G4</option></select>" +
			"S&nbsp<select id='s_tnm' style='margin-right:1em;'><option value='No'>---</option><option>S0</option><option>S1</option><option>S2</option><option>S3</option></select>" +
			"R&nbsp<select id='r_tnm' style='margin-right:1em;'><option value='No'>---</option><option>R0</option><option>R1</option><option>R2</option></select>" +
			"L&nbsp<select id='l_tnm' style='margin-right:1em;'><option value='No'>---</option><option>L0</option><option>L1</option></select>" +
			"V&nbsp<select id='v_tnm' style='margin-right:1em;'><option value='No'>---</option><option>V0</option><option>V1</option><option>V2</option></select>" +
			"C&nbsp<select id='c_tnm' style='margin-right:1em;'><option value='No'>---</option><option>C1</option><option>C2</option><option>C3</option><option>C4</option><option>C5</option></select>" +
			"</td></tr></table>";
			html+="<br><div><span style='margin-right:0.5em;' class='fa fa-info-circle'></span>For further information about TNM click <a href='http://en.wikipedia.org/wiki/TNM_staging_system' target='_blank' >here</a></div>";
		}
		else if(tipo=="Autocomplete"){
			resiz=true;
			width="100%";
			larg=900;
			altezza=350;
			html+="<table style='margin-left:4%;'><tbody><tr><td><b>Drug name:</b></td><td><input id='id_treat' type='text' maxlength='45'>"+
			"<input style='margin-left:1em;' id='selez_treat' class='button' type='submit' value='Select drug'></td></tr></tbody></table>";
			html+="<div style='float:left;width:90%;margin-left:4%;'>"+			
			"<table id='table_fin' style='float:left'><tbody></tbody></table></div>";
		}
		
		if(nome=="Disease status at follow up"){
			larg=500;
			html+="<tr><td>Warning: you also have to insert a value for \"Date last follow up\"</tr></td>";
		}
		
		$("#fList").css("width",width);
		$("#fList").append(html);
		jQuery( "#dialog" ).dialog({
            resizable: resiz,
            height:altezza,
            width:larg,
            modal: true,
            draggable :true,
            dialogClass: "no-close",
            closeOnEscape: false,
            title: nome,
            //position: { my: "top", at: "top", of: window },
            open: function() {
                $("#iddata").datepicker({ dateFormat: 'yy-mm-dd', maxDate: 0});
                //per togliere il focus al campo input, altrimenti non mi si carica il datepicker
                $("#iddata").blur();
                if(tipo=="Sequencing"){
                	esegui_sequencing();
                }
                else if(tipo=="FISH"){
                	esegui_fish();
                }
                else if(tipo=="TNM"){
                	esegui_tnm();
                }
                else if(tipo=="Autocomplete"){
                	esegui_autocomplete();
                }                
            },
            buttons: {
	            "Cancel": function() {
            	    jQuery(check).attr('checked', false);
                    jQuery(this).dialog( "close" );
                    //se ho deselezionato Date last follow up devo togliere anche Disease status at follow up
            		if(nome=="Date last follow up"){
            			var check2=$(":checkbox[value='Disease status at follow up']");
            			var idfe=$(check2).attr("idfeat");
            			$(check2).removeAttr("checked");
            			for(var i=0;i<lisfin.length;i++){
            				var diztemp=lisfin[i];
            				if(diztemp["idfeat"]==idfe){
            					lisfin.splice(i,1);
            					break;
            				}
            			}
            		}
            		scrivi_valori();
            		if(lisfin.length==0){
            			$("#selectedList").css("display","none");
            		}
	            },
	            "Ok": function() {
					var lisval=[];
	            	if (tipo=="Date"){
	            		var dd=$("#iddata").val().trim();
	        			var bits =dd.split('-');
	        			var d = new Date(bits[0], bits[1] - 1, bits[2]);
	        			var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
	        			if (!booleano){
	        				alert("Incorrect data format: it should be YYYY-MM-DD");
	        				return;
	        			}
	        			else{
	        				//salvo nel dizionario il valore
	        				lisval.push(dd);
	        			}
	            	}
	            	else if(tipo=="Year"){
	            		var val=$("#id_anno").val().trim();
	            		//visto che uso il type number, se non e' un numero mi rida' ""
	            		if(val==""){
	            			alert("Please insert a valid number");
	            			return;
	            		}
	            		else{
	            			var d = new Date();
	            			var n = d.getFullYear();
	            			var vv=parseInt(val);
	            			if((!(isInteger(val)))||(vv<1900)||(vv>n)){
	            				alert("Please insert a year between 1900 and "+String(n));
		            			return;
	            			}
	            			lisval.push(val);
	            		}
	            	}
	            	else if((tipo=="Text")||(tipo=="TextTumor")){
	            		var val=$("#id_text").val().trim();
	            		if(val==""){
	            			alert("Please insert value");
	            			return;
	            		}
	            		lisval.push(val)
	            	}
	            	else if(tipo=="Number"){
	            		var val=$("#id_num").val().trim();
	            		//visto che uso il type number, se non e' un numero mi rida' ""
	            		if(val==""){
	            			alert("Please insert a valid number");
	            			return;
	            		}
	            		else{
	            			var vv=parseFloat(val);
	            			if(vv<0){
	            				alert("Please insert a positive number");
		            			return;
	            			}
	            			lisval.push(val);
	            		}
	            	}
	            	else if(tipo=="List"){
	            		var val=$("#id_lista option:selected").text();
	            		lisval.push(val)
	            	}
	            	else if(tipo=="RadioList"){
	            		var val=$('input:radio[name="choose"]:checked').val();
	            		if(val==undefined){
	            			alert("Please choose a value");
	            			return;
	            		}
	            		else{
	            			lisval.push(val);
	            		}
	            	}
	            	else if(tipo=="Sequencing"){
	            		if((Object.size(dizsequencing)==0)&&(lis_gene_wt.length==0)){
	            			alert("Please select a mutation or set \"WT\"");
	            			return;
	            		}
	            		for(var k in dizsequencing){
	            			var vv=dizsequencing[k];
	            			var val=vv.split("|");
	            			var strfin=val[0]+": "+val[1]+" "+val[2];
	            			lisval.push(strfin);
	            		}
	            		for (var ii=0;ii<lis_gene_wt.length;ii++){
	            			var strfin=lis_gene_wt[ii]+": WT";
	            			lisval.push(strfin);
	            		}
	            	}
	            	else if(tipo=="FISH"){
	            		var lisinp=$(".input_fish");
	            		for(var jj=0;jj<lisinp.length;jj++){
	            			var valore=$(lisinp[jj]).val().trim();
	            			var gene=$(lisinp[jj]).parent().parent().children(":nth-child(2)");
            				var valgene=$(gene).text();
	            			if(valore==""){	            				
	            				alert("Please insert a valid number for "+valgene);
	            				return;
	            			}
	            			else{
	            				var vv=parseFloat(valore);
		            			if(vv<0){
		            				alert("Please insert a positive number for "+valgene);
			            			return;
		            			}	            			
		            			var strfin=valgene+": "+valore;
		            			lisval.push(strfin);
	            			}
	            		}
	            	}
	            	else if(tipo=="TNM"){
	            		var strfin="";
	            		var prefisso=$(".check_tnm:checked").val();
	            		if(prefisso!=undefined){
	            			strfin+=prefisso;
	            		}
	            		var t=$("#t_tnm option:selected").val();
	            		var n=$("#n_tnm option:selected").val();
	            		var m=$("#m_tnm option:selected").val();
	            		strfin+=t+n+m;
	            		var lis=["g","s","r","l","v","c"];
	            		for (var ii=0;ii<lis.length;ii++){
	            			var xx=$("#"+lis[ii]+"_tnm option:selected").val();
	            			if(xx!="No"){
	            				strfin+=xx;
	            			}
	            		}
	            		lisval.push(strfin);
	            	}
	            	else if(tipo=="Autocomplete"){
	            		if(!(nome in diztreat )){
	            			alert("Please select a drug");
	            			return;
	            		}
	            		var listemp=diztreat[nome];	            	
	            		for(var k=0;k<listemp.length;k++){	            			
	            			lisval.push(listemp[k]);
	            		}
	            	}
	            	var diztemp={};
	            	diztemp["value"]=lisval;
	            	diztemp["unit"]=unit;
	            	diztemp["nome"]=nome;
	            	diztemp["idfeat"]=idfeat;
	            	lisfin.push(diztemp);
	            	scrivi_valori();
	            	jQuery(this).dialog( "close" );
	            	//eccezione per questo parametro. Se c'e', devo anche inserire 'date last follow up'
	            	if(nome=="Disease status at follow up"){
	            		var check=$(":checkbox[value='Date last follow up']");
	            		if(!($(check).is(":checked"))){
	            			$(check).attr("checked","checked");
	            			valori_checkbox(check);
	            		}
	            	}
	            }
            }
        });
	}
	else{
		//se ho deselezionato Date last follow up devo togliere anche Disease status at follow up
		if(nome=="Date last follow up"){
			var check2=$(":checkbox[value='Disease status at follow up']");
			var idfe=$(check2).attr("idfeat");
			$(check2).removeAttr("checked");
			for(var i=0;i<lisfin.length;i++){
				var diztemp=lisfin[i];
				if(diztemp["idfeat"]==idfe){
					lisfin.splice(i,1);
					break;
				}
			}
		}
		//devo togliere l'elemento dalla lista finale e ridisegnare la tabella sulla destra con il riepilogo dei parametri
		for(var i=0;i<lisfin.length;i++){
			var diztemp=lisfin[i];
			if(diztemp["idfeat"]==idfeat){
				lisfin.splice(i,1);
				break;
			}
		}
		if(tipo=="Sequencing"){
			for(var k in dizsequencing){
				delete dizsequencing[k];
			}
			//cancello anche la lista dei geni wt
			lis_gene_wt.splice(0,lis_gene_wt.length);
		}
		else if(tipo=="FISH"){
			for(var k in dizfish){
				delete dizfish[k];
			}
		}
		else if(tipo=="Autocomplete"){
			delete diztreat[nome];
		}
		scrivi_valori();
		if(lisfin.length==0){
			$("#selectedList").css("display","none");
		}
	}
}

//per scrivere i valori nella tabella a destra con il riepilogo dei parametri da salvare
function scrivi_valori(){
	$("#selectedList").css("display","");
	$("#selectedTable").empty();
	var html="";
	for(var i=0;i<lisfin.length;i++){
		var dizt=lisfin[i];
		var nomefeat=dizt["nome"];
		var unit=dizt["unit"];
		var lisval=dizt["value"];
		var stringa="";
		for(var j=0;j<lisval.length;j++){
			if(unit==""){
				stringa+=lisval[j]+"<br>";
			}
			else{
				stringa+=lisval[j]+" "+unit+"<br>";
			}
		}
		var strfin=stringa.substring(0,stringa.length-4);
		html+="<tr><td><strong>"+nomefeat+":</strong></td><td>";		
		html+=strfin+"</td></tr>";
	}
	$(html).appendTo("#selectedTable");
}

/* Get the rows which are currently selected */
function fnGetSelected( oTableLocal )
{
	var aReturn = new Array();
	var aTrs = oTableLocal.fnGetNodes();
	
	for ( var i=0 ; i<aTrs.length ; i++ )
	{
		if ( $(aTrs[i]).hasClass('row_selected') )
		{
			aReturn.push( aTrs[i] );
		}
	}
	return aReturn;
}

$(document).ready(function () {
	
	$("#close").click(chiudi_finestra);
	
	$("#conferma1").click(function(event){
		event.preventDefault();
		salva_dati();
	})
	
	$("a:contains('LAS Home')").remove();
	$("#home").removeAttr("href");	
});
