//chiave l'idaldersched e valore un diz con chiave l'aliq e valore i valori di vol, conc e acqua
var dizaliquote={};
var modificato=false;
//chiave l'idaldersched e valore un diz con l'indicazione se creare l'aliquota finale o no e il barcode
var dizcreateremain={}

$(document).ready(function () {
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Dilution","aliquote_fin");
		return;
	}
	
	$("#cambia_aliquote").click(modifica_num_aliquote);
	$("#apply").click(calcola_valori);
	$("#cambia_aliq_dialog").click(modifica_num_aliq_dialog);
	$("#id_num_aliq_dialog").keypress(function(event){
		if ( event.which == 13 ) {
			modifica_num_aliq_dialog();
		}
	});
	$("#ricalcola").click(function(event){
		var num_aliquote=$("#id_num_aliq_dialog").val();
		num_aliquote=(parseInt(num_aliquote)+1);
		calcola_valori_dialog(num_aliquote);
	});
	
	$("#id_number_aliquots").keypress(function(event){
		if ( event.which == 13 ) {
			modifica_num_aliquote();
		}
	});
		
	var num=$("#id_number_aliquots").val();
	if(num>0){
		modifica_num_aliquote();
	}
	
	scrivi_misure();
	$("#aliq tr.interna").click(function(event){
		show_info_aliq(this);
	});
	$("#aliq tr.interna").find("td.td_stop input:checkbox").click(function(event){
		event.stopPropagation();
		manage_stop_procedure(this);
	});
	
	$("#submit_button").click(function(event){
		event.preventDefault();		
		salva_dati_server();
	});
	
	$("#exh_all").click(check_all_exhausted);
	
	$(".check_exh").click(function(event){
		event.stopPropagation();		
	});
	
	var righetab=$("#aliq tr.interna");
	//per nascondere il left over che ho copiato dalla schermata di derivazione automatica
	$("#tab_val tr.last_tr").hide();
	$("#tab_val tr.last_tr td input.class_task").attr("disabled",true);
	for(var i=0;i<righetab.length;i++){
		var idaldersched=$(righetab[i]).find("input.gen_aliq_der").attr("id_alsched");
		dizcreateremain[idaldersched]={"create":false};
	}	
	
	if(righetab.length==0){
		$("#aliq,#div_ext").hide();
	}
});

function create_remain(){
	var lisrighe=$("#aliq tr.interna");
	var create=true;
	if($("#id_create_remain").is(":checked")){
		$("#tab_val tr.last_tr").show();
		$("#tab_val tr.last_tr td input.class_task").attr("disabled",false);
	}
	else{
		$("#tab_val tr.last_tr").hide();
		$("#tab_val tr.last_tr td input.class_task").attr("disabled",true);
		create=false;
	}
	for(var i=0;i<lisrighe.length;i++){
		var idaldersched=$(lisrighe[i]).find("input.gen_aliq_der").attr("id_alsched");
		dizcreateremain[idaldersched]={"create":create};
	}
}

function check_all_exhausted(){
	if ($(this).is(":checked")){
		$(".check_exh").attr("checked","checked");
	}
	else{
		$(".check_exh").removeAttr("checked");
	}
} 

function manage_stop_procedure(checkbox){
	var tr=$(checkbox).parent().parent();
	if($(checkbox).is(":checked")){
		//tolgo l'onclick al tr
		$(tr).unbind( "click" );
		$(tr).css( "cursor","initial" );
		//solo se la riga ha la concentrazione presente
		if(!($(tr).hasClass("noconc"))){
			$(tr).css("background-color","#e8e8e8");
		}
	}
	else{
		//metto l'onclick al tr solo se ho la concentrazione esplicita
		if(!($(tr).hasClass("noconc"))){
			$(tr).click(function(event){
				show_info_aliq(this);
			});
			$(tr).css( "cursor","pointer" );
		}		
	}
}

//per creare all'interno della dialog le celle della tabella con le aliq. L'html delle celle e' simile
function modifica_num_aliq_dialog(){
	var num_aliquote=$("#id_num_aliq_dialog").val();
	//aggiungo 1 a num per tenere conto del rimanente
	num_aliquote=(parseInt(num_aliquote)+1).toString();
	var idaldersched=$("#id_alsched_dialog").val();
	var strhtml="<tr>";
	for(var i=0;i<num_aliquote-1;i++){
		var intest="Aliquot "+(i+1);
		/*if(i==(num_aliquote-1)){
			intest="Left over";
		}*/
		strhtml+="<th>"+intest+"</th>";
	}
	strhtml+="</tr><tr>";
	for(var i=0;i<num_aliquote-1;i++){
		var volaliq="0.0"; var concaliq="0.0"; var madre="0.0"; var acqua="0.0";var task="";
		if(idaldersched in dizaliquote){
			var dizval=dizaliquote[idaldersched];
			var lundizval=Object.size(dizval)
			var lun2=lundizval-1;
			concaliq=dizval[lun2]['concentration'];
			if(i in dizval){
				if(i<lundizval-1){
					volaliq=dizval[i]['volume'];
					concaliq=dizval[i]['concentration'];
					madre=dizval[i]['madre'];
					acqua=dizval[i]['acqua'];
					task=dizval[i]['task'];
				}
			}
			/*if(i==(num_aliquote-1)){
				volaliq=dizval[lun2]['volume'];
				concaliq=dizval[lun2]['concentration'];
				madre=dizval[lun2]['madre'];
				acqua=dizval[lun2]['acqua'];
				task=dizval[lun2]['task'];
			}*/
		}
		strhtml+="<td align='center'><label>Volume(ul):</label><input id='vol_dia_"+(i)+"' type='text' class='cl_vol_dia' size='7' value='"+volaliq+"' "+
		"maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'><label style='margin-bottom: 5px;' class='label_conc_dia' >Concentration<br>(ng/ul):</label>"+
		"<input id='conc_dia_"+(i)+"' type='text' size='7' value='"+concaliq+"' maxlength='7' class='cl_conc_dia' style='margin-top: 5px; margin-bottom: 5px;'>"+
		"<label>Mother(ul):</label><input id='moth_dia_"+(i)+"' type='text' size='7' maxlength='7' class='mother_dia noborder' "+
		"readonly='readonly' style='background-color:#E8E8E8;text-align:center;margin-top: 5px; margin-bottom: 5px;' value='"+madre+"' "+
		"style='margin-top: 5px; margin-bottom: 5px;'><label>Diluent(ul):</label><input id='h2o_dia_"+(i)+"' "+
		"type='text' size='7' style='background-color:#E8E8E8;text-align:center;margin-top: 5px; margin-bottom: 5px;' class='inp_h2o_dia noborder' readonly='readonly' value='"+acqua+"' "+
		"style='margin-top: 5px;'><label>Slot:</label><input id='task_dia_"+i+"' style='width:3em;margin-top:5px;' class='cl_task_dia' value='"+task+"' min='1' max='3' type='number'></td>";
	}
	strhtml+="</tr>";
	$("#tab_riepilogo").children().remove();
	$("#tab_riepilogo").append(strhtml);
	
	var strhtml2="<tr><th>Left over</th></tr><tr>";
	var volaliq="0.0"; var concaliq="0.0";
	if(idaldersched in dizaliquote){
		var dizval=dizaliquote[idaldersched];
		var lundizval=Object.size(dizval)
		var lun2=lundizval-1;		
		volaliq=dizval[lun2]['volume'];
		concaliq=dizval[lun2]['concentration'];		
		var i=num_aliquote-1;
		strhtml2+="<td align='center'><label>Volume(ul):</label><input id='vol_dia_"+(i)+"' type='text' readonly='readonly' class='cl_vol_dia' size='7' value='"+volaliq+"' "+
		"maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'><label style='margin-bottom: 5px;' class='label_conc_dia' >Concentration<br>(ng/ul):</label>"+
		"<input id='conc_dia_"+(i)+"' type='text' size='7' readonly='readonly' value='"+concaliq+"' maxlength='7' class='cl_conc_dia' style='margin-top: 5px; margin-bottom: 5px;'></td>";
	}
	$("#tab_leftover").children().remove();
	$("#tab_leftover").append(strhtml2);
	
	$("#tab_riepilogo input.cl_vol_dia,#tab_riepilogo input.cl_conc_dia,#tab_riepilogo input.cl_task_dia").keydown(function() {
		modificato=true;
	});
	$("#tab_riepilogo input.cl_task_dia").change(function() {
		modificato=true;
	});
	calcola_valori_dialog(num_aliquote);
}

//per ricalcolare nel dialog i valori delle varie aliquote create
function calcola_valori_dialog(num_aliquote){	
	var idaldersched=$("#id_alsched_dialog").val();	
	var concmadre=$("#conc_madre").val();
	var volmadre=$("#vol_madre").val();
	var quant=parseFloat(concmadre)*parseFloat(volmadre);
	var ngtot=0;var diztemp={};	
	for(var i=0;i<num_aliquote;i++){
		//sto analizzando l'ultima aliquota nuova
		if(i==num_aliquote-1){
			//trovo il volume prelevato dalla madre tramite i ng totali che so che devo prendere per fare le altre aliquote					
			var volpresomadre=ngtot/concmadre;			
			var volal=volmadre-volpresomadre;
			var concal=concmadre;
			var voldamadre=volal;
			var acqua=0.0;			
			$("#vol_dia_"+i).val(String(parseFloat(volal).toFixed(2)));
			$("#conc_dia_"+i).val(String(parseFloat(concal).toFixed(2)));
		}
		else{
			var volal=$("#vol_dia_"+i).val().trim();
			var concal=$("#conc_dia_"+i).val().trim();
			var quantita=parseFloat(volal)*parseFloat(concal);
			//vol da prelevare dalla madre
			var voldamadre=quantita/concmadre;
			//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
	    	//della madre e quella della singola provetta
			var acqua=0.0;
			if(concal!=0){
				acqua=(voldamadre*concmadre/concal)-voldamadre;
			}
			ngtot+=quantita;			
		}
		$("#moth_dia_"+i).val(String(parseFloat(voldamadre).toFixed(2)));
		$("#h2o_dia_"+i).val(String(parseFloat(acqua).toFixed(2)));
		var task=$("#task_dia_"+i).val();
		//devo salvare i nuovi valori anche nel dizionario generale
		diztemp[i]={"volume":parseFloat(volal).toFixed(2),"concentration":parseFloat(concal).toFixed(2),"madre":parseFloat(voldamadre).toFixed(2),"acqua":parseFloat(acqua).toFixed(2),"task":task};
	}
	//se qualche valore e' negativo o 0 devo metterlo in rosso togliendo prima i bordi rossi gia' presenti
	$("#tab_riepilogo input,#tab_leftover input").removeClass("bordorosso");
	var lisinp=$("#tab_riepilogo input,#tab_leftover input").not("input.inp_h2o_dia");
	for(var j=0;j<lisinp.length;j++){
		var valore=$(lisinp[j]).val();
		if(valore<=0.0){
			$(lisinp[j]).addClass("bordorosso");
		}
	}
	var lisinp=$("#tab_riepilogo input.inp_h2o_dia,#tab_leftover input.inp_h2o_dia");
	for(var j=0;j<lisinp.length;j++){
		var valore=$(lisinp[j]).val();
		if(valore<0.0){
			$(lisinp[j]).addClass("bordorosso");
		}
	}
	modificato=false;
}

function show_info_aliq(riga){
	if(Object.size(dizaliquote)!=0){
		var idaldersched=$(riga).find("input.gen_aliq_der").attr("id_alsched");		
		var num_aliquote=$("#id_num_aliq_hidden").attr("value");
		if(idaldersched in dizaliquote){
			var dizval=dizaliquote[idaldersched];
			num_aliquote=Object.size(dizval);
		}
		var gen=$(riga).find("input.gen_aliq_der").val();
		var barc=$(riga).find("input.barc_aliq_der").val();
		var pos=$(riga).find("td.td_pos").text().trim();
		$("#tab_view").find("td.view_gen").html(gen+"<input id='id_alsched_dialog' value='"+idaldersched+"' type='hidden'>");
		$("#tab_view").find("td.view_barc").text(barc);
		$("#tab_view").find("td.view_pos").text(pos);		
		var strhtml="<tr>";
		for(var i=0;i<num_aliquote-1;i++){
			var intest="Aliquot "+(i+1);
			/*if(i==(num_aliquote-1)){
				intest="Left over";
			}*/
			strhtml+="<th>"+intest+"</th>";
		}
		strhtml+="</tr><tr>";
		for(var i=0;i<num_aliquote-1;i++){
			var volaliq=""; var concaliq=""; var madre=""; var acqua="";var task="";
			if(idaldersched in dizaliquote){
				var dizval=dizaliquote[idaldersched];
				volaliq=dizval[i]['volume'];
				concaliq=dizval[i]['concentration'];
				madre=dizval[i]['madre'];
				acqua=dizval[i]['acqua'];
				task=dizval[i]['task'];
			}
			strhtml+="<td align='center'><label>Volume(ul):</label><input id='vol_dia_"+(i)+"' type='text' class='cl_vol_dia' size='7' value='"+volaliq+"' "+
			"maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'><label style='margin-bottom: 5px;' class='label_conc_dia' >Concentration<br>(ng/ul):</label>"+
			"<input id='conc_dia_"+(i)+"' type='text' size='7' value='"+concaliq+"' maxlength='7' class='cl_conc_dia' style='margin-top: 5px; margin-bottom: 5px;'>"+
			"<label>Mother(ul):</label><input id='moth_dia_"+(i)+"' type='text' size='7' maxlength='7' class='mother_dia noborder' "+
			"readonly='readonly' style='background-color:#E8E8E8;text-align:center;margin-top: 5px; margin-bottom: 5px;' value='"+madre+"' "+
			"style='margin-top: 5px; margin-bottom: 5px;'><label>Diluent(ul):</label><input id='h2o_dia_"+(i)+"' "+
			"type='text' size='7' style='background-color:#E8E8E8;text-align:center;margin-top: 5px; margin-bottom: 5px;' class='inp_h2o_dia noborder' readonly='readonly' value='"+acqua+"' "+
			"style='margin-top: 5px;'><label>Slot:</label><input id='task_dia_"+i+"' style='width:3em;margin-top:5px;' class='cl_task_dia' value='"+task+"' min='1' max='3' type='number'></td>";
		}
		strhtml+="</tr>";
		$("#tab_riepilogo").children().remove();
		$("#tab_riepilogo").append(strhtml);
		
		var strhtml2="<tr><th>Left over</th></tr><tr>";
		var volaliq="0.0"; var concaliq="0.0";
		if(idaldersched in dizaliquote){
			var dizval=dizaliquote[idaldersched];
			volaliq=dizval[i]['volume'];
			concaliq=dizval[i]['concentration'];			
			var i=num_aliquote-1;
			strhtml2+="<td align='center'><label>Volume(ul):</label><input id='vol_dia_"+(i)+"' type='text' readonly='readonly' class='cl_vol_dia' size='7' value='"+volaliq+"' "+
			"maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'><label style='margin-bottom: 5px;' class='label_conc_dia' >Concentration<br>(ng/ul):</label>"+
			"<input id='conc_dia_"+(i)+"' type='text' size='7' readonly='readonly' value='"+concaliq+"' maxlength='7' class='cl_conc_dia' style='margin-top: 5px; margin-bottom: 5px;'></td>";
		}
		$("#tab_leftover").children().remove();
		$("#tab_leftover").append(strhtml2);
		
		//se qualche valore e' negativo o 0 devo metterlo in rosso
		var lisinp=$("#tab_riepilogo input,#tab_leftover input");
		for(var j=0;j<lisinp.length;j++){
			var valore=$(lisinp[j]).val();
			if(valore<0.0){
				$(lisinp[j]).addClass("bordorosso");
			}
		}
		
		$("#id_num_aliq_dialog").val((parseInt(num_aliquote)-1).toString());
		var volumemadre=$(riga).find("td.td_vol").text().trim();
		var concmadre=$(riga).find("td.td_conc").text().trim();

		$("#conc_madre").val(concmadre);
		$("#vol_madre").val(volumemadre);
		
		$("#tab_riepilogo input.cl_vol_dia,#tab_riepilogo input.cl_conc_dia,#tab_riepilogo input.cl_task_dia").keydown(function() {
			modificato=true;
		});
		$("#tab_riepilogo input.cl_task_dia").change(function() {
			modificato=true;
		});
		
		$( "#dialog" ).dialog({
	        resizable: true,
	        height:550,
	        width:1000,
	        modal: true,
	        draggable :true,
	        buttons: {
	            "Ok": function() {
	            	if(modificato){
	            		alert("Some values have been modified. Please click on \"Recalculate values\"");
	            		return;
	            	}
	            	var idaldersched=$("#id_alsched_dialog").val();
	            	var dizval=dizaliquote[idaldersched];
	            	var num_aliq=$("#id_num_aliq_dialog").val();
	            	//aggiungo 1 a num per tenere conto del rimanente
	            	num_aliq=(parseInt(num_aliq)+1).toString();
	            	var regex=/^[0-9.]+$/;
	            	var diztemp={};
	            	var q_madre=0; var diluente=0; var volmadre=0;
	            	for(var i=0;i<num_aliq;i++){
	            		var tipo="aliquot "+(i+1);
	            		if(i==(num_aliq-1)){
	            			tipo="left over";
	            		}
	            		//costruisco l'identificativo per il volume
	            		var idvol="#vol_dia_"+i;
	            		if(!($(idvol).attr("disabled"))&&($(idvol).val()== "")){
	            			alert("Insert volume for "+tipo);
	            			return;
	            		}
	            		var volume=$(idvol).val().trim();
	            		if(parseFloat(volume)<0){
	            			alert("Negative numbers not accepted. Correct volume for "+tipo);
            				return;
	            		}
	            		else{
	            			if(!($(idvol).attr("disabled"))&&(!regex.test(volume))){
	            				alert("You can only insert number. Correct volume for "+tipo);
	            				return;
	            			}
	            		}
	            		var idconc="#conc_dia_"+i;
	            		if(!($(idconc).attr("disabled"))&&($(idconc).val()=="")){
	            			alert("Insert concentration for "+tipo);
	            			return;
	            		}
	            		var conc=$(idconc).val().trim();
	            		if(parseFloat(conc)<0){
	            			alert("Negative numbers not accepted. Correct concentration for "+tipo);
            				return;
	            		}
	            		else{	            			
	            			if(!($(idconc).attr("disabled"))&&(!regex.test(conc))){
	            				alert("You can only insert number. Correct concentration for "+tipo);
	            				return;
	            			}
	            		}
	            		if(i!=(num_aliq-1)){
		            		var idtask="#task_dia_"+i;
		            		if(!($(idtask).attr("disabled"))&&($(idtask).val()=="")){
		            			alert("Insert slot for "+tipo);
		            			return;
		            		}
		            		else{
		            			var num=$(idtask).attr("value");
		            			if((isNaN(num))||(parseInt(num)<=0)||(parseInt(num)>3)){
		            				alert("You can only insert a number between 1 and 3. Correct slot for "+tipo);
		            				return;
		            			}
		            		}
	            		}	            		
	            		if(i!=(num_aliq-1)){
		            		q_madre=$("#moth_dia_"+i).val().trim();
		            		if(parseFloat(q_madre)<0){
		            			alert("Negative numbers not accepted. Correct mother quantity for "+tipo);
	            				return;
		            		}
		            		diluente=$("#h2o_dia_"+i).val().trim();
		            		if(parseFloat(diluente)<0){
		            			alert("Negative numbers not accepted. Correct diluent for "+tipo);
	            				return;
		            		}
	            		}
	            		if(i==(num_aliq-1)){		            		
		            		volmadre=volume;
	            		}
	            		diztemp[i]={"volume":parseFloat(volume).toFixed(2),"concentration":parseFloat(conc).toFixed(2),"madre":parseFloat(q_madre).toFixed(2),"acqua":parseFloat(diluente).toFixed(2),"task":num};
	            	}
	            	dizaliquote[idaldersched]=diztemp;
	            	//se sono arrivato qua vuol dire che e' tutto a posto, quindi la riga e' da colorare di verde					
					var riga=$("#aliq tr.interna td.lis_gen input[id_alsched="+idaldersched+"]").parent().parent();
					$(riga).css("background-color","#91E47D");
					$(riga).removeClass("error");
					$(riga).find("td.td_leftovervol").text(parseFloat(volmadre).toFixed(2));
					$(riga).find("td.td_leftovervol").css("color","black");
	                jQuery(this).dialog( "close" );
	            },
				"Cancel": function() {
		            jQuery(this).dialog("close");
		        }        
	        }
		});
	}
	else{
		alert("Please first click on \"Apply values\"");
	}
}

//Per aggiungere righe nella tabella delle aliquote da creare
function modifica_num_aliquote(){
	var num=$("#id_number_aliquots").val();
	if(num==""){
		alert("Please insert number of aliquots to create");
		return;
	}
	else if((isNaN(num))||(parseInt(num)<=0)){
		alert("Not a valid number");
		return;
	}
	//aggiungo 1 a num per tenere conto del rimanente
	num=(parseInt(num)+1).toString();
	$("#tab_apply").css("border-bottom-style","none");
	$("#id_num_aliq_hidden").val(num);
	var vol="";//$("#volume_aliq").val();
	var conc="";//$("#conc_aliq").val();
	$("#tab_val").children().remove();
	var strhtml="";
	for(var i=0;i<parseInt(num);i++){
		var intest="Aliquot "+(i+1);
		var classeultima="";
		if(i==(num-1)){
			classeultima="last_tr";
			intest="Left over";
		}
		strhtml+="<tr class='"+classeultima+"' align='center'><td rowspan='2'><b>"+intest+"</b></td><td style='border-bottom-style:none;'><label>Volume (ul):</label>"+
				"<input id='volume_"+String(i)+"' maxlength='7' type='text' value='"+vol+"' class='class_input_volume' name='volume_"+String(i)+"' size='2' /></td>" +
				"<td rowspan='2'><b>Slot:</b></td><td rowspan='2'><input id='task_"+String(i)+"' class='class_task' style='width:3em;' "+
				"type='number' name='task_"+String(i)+"' min='1' max='3'/></td></tr><tr class='"+classeultima+"' align='center'><td style='border-top-style:none;'>"+
				"<label >Concentration<br>(ng/ul):</label><input id='concentration_"+String(i)+"' value='"+conc+"'  maxlength='7' type='text' class='class_input_conc' "+
				"name='conc_"+String(i)+"' size='2'/></td></tr>";
	}
	$("#tab_val").append(strhtml);
	//disabilito vol e conc dell'ultima aliquota perche' e' quella che fa da riserva e quindi l'utente non deve compilarla. La lascio vuota.
	//Per vedere effettivamente i valori, bisogna entrare nel dettaglio di ogni derivazione.
	$("#tab_val tr:last").find(".class_input_conc").attr("disabled",true);
	$("#tab_val tr:last").find(".class_input_conc").val("");
	$("#tab_val tr:last").prev("tr").find(".class_input_volume").attr("disabled",true);
	$("#tab_val tr:last").prev("tr").find(".class_input_volume").val("");
	create_remain();
}

//per calcolare vol e conc di ogni singola aliquota e colorare le righe 
function calcola_valori(){
	var num_aliq=$("#id_num_aliq_hidden").val();
	var regex=/^[0-9.]+$/;
	var ngtot=0;
	var dizvalori={};
	for(var i=0;i<num_aliq;i++){
		var tipo="aliquot "+(i+1);
		if(i==(num_aliq-1)){
			tipo="left over";
		}
		//costruisco l'identificativo per il volume
		var idvol="#volume_"+i;
		if(!($(idvol).attr("disabled"))&&($(idvol).val()== "")){
			alert("Insert volume for "+tipo);
			return;
		}
		else{
			var volume=$(idvol).attr("value").trim();
			if(!($(idvol).attr("disabled"))&&(!regex.test(volume))){
				alert("You can only insert number. Correct volume for "+tipo);
				return;
			}
		}
		var idconc="#concentration_"+i;
		if(!($(idconc).attr("disabled"))&&($(idconc).val()=="")){
			alert("Insert concentration for "+tipo);
			return;
		}
		else{
			var conc=$(idconc).attr("value").trim();
			if(!($(idconc).attr("disabled"))&&(!regex.test(conc))){			
				alert("You can only insert number. Correct concentration for "+tipo);
				return;
			}
		}
		var idtask="#task_"+i;
		if(!($(idtask).attr("disabled"))&&($(idtask).val()=="")){
			alert("Insert slot for "+tipo);
			return;
		}
		else{
			var num=$(idtask).attr("value");
			if((isNaN(num))||(parseInt(num)<=0)||(parseInt(num)>3)){
				alert("You can only insert a number between 1 and 3. Correct slot for "+tipo);
				return;
			}
		}
		//calcolo i ng che mi servono per questa aliquota solo fino a i-1 perche' l'ultima aliquota fa da riserva
		if(i<num_aliq-1){
			dizvalori[i]={"volume":volume,"concentration":conc,"task":num};
			var quantita=parseFloat(volume)*parseFloat(conc);
			ngtot+=quantita;
		}
		else{
			dizvalori[i]={"task":num};
		}
	}
	//non prendo le fallite
	var lisrighe=$("#aliq tr.interna").not("tr.failed");
	for(var i=0;i<lisrighe.length;i++){
		var volume=$(lisrighe[i]).find("td.td_vol").text().trim();
		var conc=$(lisrighe[i]).find("td.td_conc").text().trim();
		var quant=parseFloat(volume)*parseFloat(conc);
		$(lisrighe[i]).unbind( "click" );
		$(lisrighe[i]).css( "cursor","initial" );
		$(lisrighe[i]).removeAttr("onClick");
		if(!isNaN(conc)){
			var checkstop=$(lisrighe[i]).find("td.td_stop input:checkbox");
            var quant=parseFloat(volume)*parseFloat(conc);
            //solo se non termino qui la procedura
            if(!($(checkstop).is(":checked"))){
                if(quant>=ngtot){
                    //tutto a posto: coloro di verde
                    $(lisrighe[i]).css("background-color","#91E47D");
                    $(lisrighe[i]).removeClass("error");
                }
                else{
                    //manca materiale: coloro di rosso
                    $(lisrighe[i]).css("background-color","#DF9982");
                    $(lisrighe[i]).addClass("error");
                }
            }
            //scrivo nel diz i valori delle aliquote
            var idaldersched=$(lisrighe[i]).find("input.gen_aliq_der").attr("id_alsched");
            var diztemp={};var volaliq=0.0;var concaliq=0.0;var volmadre=0.0;var acqua=0.0;
            for(var j=0;j<num_aliq;j++){
                //sto analizzando l'ultima aliquota nuova
                if(j==num_aliq-1){
                    //trovo il volume prelevato dalla madre tramite i ng totali che so che devo prendere per fare le altre aliquote                                 
                    var volpresomadre=ngtot/conc;   
                    volaliq=volume-volpresomadre;
                    concaliq=conc;
                    volmadre=volaliq;
                    acqua=0.0;
                    //solo se non termino qui la procedura
                    if(!($(checkstop).is(":checked"))){
	                    $(lisrighe[i]).find("td.td_leftovervol").text(parseFloat(volaliq).toFixed(2));
	                    if (volaliq<0){
	                        $(lisrighe[i]).find("td.td_leftovervol").css("color","red");
	                        $(lisrighe[i]).find("td.td_leftovervol").css("border-color","black");
	                    }
	                    else{
	                        $(lisrighe[i]).find("td.td_leftovervol").css("color","black");
	                    }
                    }
                }
                else{
                    volaliq=dizvalori[j]["volume"];
                    concaliq=dizvalori[j]["concentration"];
                    var quantita=parseFloat(volaliq)*parseFloat(concaliq);
                    //vol da prelevare dalla madre
                    volmadre=quantita/conc;
                    //per trovare l'acqua moltiplico i ul per il rapporto tra la conc
                    //della madre e quella della singola provetta
                    acqua=(volmadre*conc/concaliq)-volmadre;
                }
                if((parseFloat(volaliq)<0)||(parseFloat(concaliq)<0)||(parseFloat(volmadre)<0)||(parseFloat(acqua)<0)){
                    //qualche valore e' negativo quindi coloro la riga di rosso solo se non termino qui la procedura
					if(!($(checkstop).is(":checked"))){
						$(lisrighe[i]).css("background-color","#DF9982");
					}
                    $(lisrighe[i]).addClass("error");
                }
                diztemp[j]={"volume":parseFloat(volaliq).toFixed(2),"concentration":parseFloat(concaliq).toFixed(2),"madre":parseFloat(volmadre).toFixed(2),"acqua":parseFloat(acqua).toFixed(2),"task":dizvalori[j]["task"]};
            }
            dizaliquote[idaldersched]=diztemp;									
			
			if(!($(checkstop).is(":checked"))){
				$(lisrighe[i]).click(function(event){
					show_info_aliq(this);
				});
				$(lisrighe[i]).css( "cursor","pointer" );
			}
		}
		//se non c'e' la concentrazione imposto lo stop procedure
		else{
			//$(lisrighe[i]).css("background-color","#DF9982");
			//metto una classe per dire che questa riga non ha concentrazione
			$(lisrighe[i]).addClass("noconc");
			var check=$(lisrighe[i]).find("td.td_stop input:checkbox");
			$(check).attr("checked","checked");
		}
	}
}

function scrivi_misure(){
	var lisrighe=$("#aliq tr.interna");
	for(var i=0;i<lisrighe.length;i++){
		$(lisrighe[i]).css("background-color","#e8e8e8");
		$(lisrighe[i]).removeClass("noconc");
		var idaldersched=$(lisrighe[i]).find("input.gen_aliq_der").attr("id_alsched");
		if(idaldersched in dizmisure){
			var dizvalori=dizmisure[idaldersched];
			var volume=dizvalori["vol"];
			if(volume==""){
				volume="-";
			}
			conc=dizvalori["conc"];
			if(conc==""){
				conc="-";
			}
			$(lisrighe[i]).find("td.td_vol").text(volume);
			$(lisrighe[i]).find("td.td_conc").text(conc);
		}
	}
	//svuoto il dizionario delle aliquote cosi' non rischio di avere i dati con la conc di prima
	for(var k in dizaliquote){
		delete dizaliquote[k];
	}
}

function salva_dati_server(){
	if(Object.size(dizaliquote)==0){
		alert("Please first click on \"Apply values\"");
		return;
	}
	//verifico che non ci siano righe rosse cioe' che abbiano la classe error
	var liserror=$("#aliq tr.interna.error").not("tr.failed");
	if(liserror.length!=0){
		//devo controllare che non abbiano lo stop
		for(var i=0;i<liserror.length;i++){
			var checkb=$(liserror[i]).find("td.td_stop input:checkbox");
			if(!($(checkb).is(":checked"))){
				var gen=$(liserror[i]).find("input.gen_aliq_der").val();
				alert("Please correct values for "+gen);
				return;
			}
		}
	}
	//verifico che non ci siano righe senza concentrazione e senza lo stop impostato
	var lisnoconc=$("#aliq tr.interna.noconc").not("tr.failed");
	for(var i=0;i<lisnoconc.length;i++){
		var checkstop=$(lisnoconc[i]).find("td.td_stop input:checkbox");
		if(!($(checkstop).is(":checked"))){
			var indice=$(lisnoconc[i]).find("td.lis_indici").text();
			alert("Line "+indice+" has not a concentration. Please check \"Stop procedure\".");
			return;
		}		
	}
	//per il tipo di container		
	var tipo=$("#id_container option:selected").val();
	if(tipo==""){
		alert("Please select source container type");
		return;
	}
	var exp_name=$("#id_exp_name").val();
	if(exp_name==""){
		alert("Please insert experiment name");
		return;
	}
	var lisrighe=$("#aliq tr.interna");
	for(var i=0;i<lisrighe.length;i++){
		var idaldersched=$(lisrighe[i]).find("input.gen_aliq_der").attr("id_alsched");
		var barc=$(lisrighe[i]).find("input.barc_aliq_der").val();
		var pos=$(lisrighe[i]).find("td.td_pos").text().trim();
		var checkstop=$(lisrighe[i]).find("td.td_stop input:checkbox");
		var ch_stop="false";
		if($(checkstop).is(":checked")){
			ch_stop="true";
		}
		var exhausted=$(lisrighe[i]).find("td.td_exh input:checkbox");
		var exh="false";
		if($(exhausted).is(":checked")){
			exh="true";
		}
		var diztemp=dizcreateremain[idaldersched];
		diztemp["barcode"]=barc;
		diztemp["position"]=pos;
		diztemp["checkstop"]=ch_stop;
		diztemp["exhausted"]=exh;
		dizcreateremain[idaldersched]=diztemp;
	}
	var timer = setTimeout(function(){$("body").addClass("loading");},500);
	//riempio le variabili da trasmettere con la post
	var data = {
			salva:true,
    		dizaliq:JSON.stringify(dizaliquote),    		
    		dizremain:JSON.stringify(dizcreateremain)
    };
	var url=base_url+"/split/robot/plandilution/";
	$.post(url, data, function (result) {
    	if (result == "failure") {
    		alert("Error");
    	}
    	
    	$("#form_conf").append("<input type='hidden' name='finish' />");
		$("#form_conf").submit();
    });
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

