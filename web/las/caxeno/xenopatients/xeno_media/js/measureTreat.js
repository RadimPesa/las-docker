jQuery(document).ready(function() {
    jQuery('#time').val('08:30');
   	jQuery("#date").datetimepicker({
        altField: "#time",
        dateFormat: "yy-mm-dd",
    });
    list_mice();
});

//aggiunge una riga alla tabella contenente i topi su cui verrà applicato il trattamento
function addRow(genealogy, barcode) {
    console.log('bbb');
	var table = document.getElementById('dataTable');
	var rowCount = table.rows.length;
	var newRow = rowCount+1;
	var row = table.insertRow(rowCount);

	var cell1 = row.insertCell(0);
	cell1.setAttribute("id","genealogy_cell"+newRow);
	cell1.innerHTML = genealogy;
	cell1.setAttribute("width","60%");

	var cell2 = row.insertCell(1);
	cell2.setAttribute("id","barcode_cell"+newRow);
	cell2.innerHTML = barcode;
	cell2.setAttribute("width","40%");
}

function alertCB(){ window.close(); }

//controlla i topi selezionati nella finestra che ha aperto questa e crea la tabella con i topi selezionati
function list_mice() {
	var oTable = window.opener.oTable;
    var typeMeasure = window.opener.typeMeasure;
    var k = 0;var j = 0;
    var rows = window.opener.fnGetSelected(); //array con le righe selezionate
	var genealogy = new Array();var barcode = new Array();
    var nodes = oTable.fnGetNodes(); var string = ""; var close = false;
    var rows = window.opener.fnGetSelected();
    if (rows.length > 0){
        for(var i = 0; i < nodes.length; i++) {
            var row = nodes[i];
            if (jQuery.inArray(row, rows) > -1){
                console.log('a');
                if (typeMeasure == "quant"){
				    if (oTable.fnGetData(i, 14) != ""){
                        var genID = oTable.fnGetData(i, 1);
                        string = (string == "") ? genID : string + ', ' + genID;
                        close = true;
					    //alert("The mouse with genealogyID: "+ genID + " has already a treatment. You have to stop it if you want start a new treatment");
					    //window.close();
				    }
    				if (oTable.fnGetData(i, 15) == "stop")
                        oTable.fnUpdate("new", i, 16, false, false);
				    genealogy[j] = oTable.fnGetData(i, 1);
				    barcode[j] = oTable.fnGetData(i, 12);
				}
                if (typeMeasure == "qual"){
				    if (oTable.fnGetData(i, 11) != ""){
                        var genID = oTable.fnGetData(i, 1);
                        string = (string == "") ? genID : string + ', ' + genID;
                        close = true;
					    //alert("The mouse with genealogyID: "+ genID + " has already a treatment. You have to stop it if you want start a new treatment");
					    //window.close();
				    }
    				if (oTable.fnGetData(i, 12) == "stop")
                        oTable.fnUpdate("new", i, 12, false, false);
				    genealogy[j] = oTable.fnGetData(i, 1);
				    barcode[j] = oTable.fnGetData(i, 9);
				}
				j++;
            }
        }
        if (close)
            alert("Mice with genealogyID: "+ string + " have already a treatment. You have to stop it if you want start a new treatment", 'Error', 'Ok', alertCB);
        console.log('glen'+genealogy.length);
	    for (k=0; k < genealogy.length; k++)
    		addRow(genealogy[k], barcode[k]);
	}
}

//associa il trattamento selezionato ai topi checkati nella finestra padre. Poi chiude questa finestra
function start(nameA) {
    var nameP = "";var k = 0;var j = 0;var genealogy = new Array();var barcode = new Array();
    var oTable = window.opener.oTable; var table = window.opener.document.getElementById("measure");
    var rowCount = table.rows.length; var rows = window.opener.fnGetSelected(); /*array con le righe selezionate*/ var n = 0;
	if (document.listProtocolsForm.list_protocols.length){
		n = document.listProtocolsForm.list_protocols.length;
		for (var j=0; j < n; j++){
			if (document.listProtocolsForm.list_protocols[j].checked == true)
				nameP = document.listProtocolsForm.list_protocols[j].nextSibling.data;
		}
	}else{
		//uso questo else nel caso in cui ci sia solo un radio button (cioe' solo un trattamento disponibile) e lo si seleziona
		//in quanto, solo in questo singolo caso, il costrutto usato sopra [document.listTreatmentsForm.list_treatments.length] restituisce NULL
		nameP  = document.getElementById('id_list_protocols_0').nextSibling.data;
	}
    var url = base_url + "/api.durationTreatment/" + nameA
    if (rows.length > 0){
        jQuery.ajax({
        	url:url,
            method: 'get',
            async:false,
            datatype: 'json',
            success: function(response) {
                var currG = window.opener.document.getElementById("tableList").getAttribute('currgroup');
                var tot = table.rows.length;
			    var nodes = oTable.fnGetNodes();
			    var rows = window.opener.fnGetSelected();
			    if (rows.length > 0){
			        for(var i = 0; i < nodes.length; i++) {
			            var row = nodes[i];
                        var genID = oTable.fnGetData(i,1);
                    	var duration = 0; var typeTime = "";
                    	var typeMeasure = window.opener.typeMeasure;
			            if (jQuery.inArray(row, rows) > -1){
                            duration = response.duration;
                            typeTime = response.typeTime;
                            duration = duration + ' [' + typeTime + ']'
                            var barcode = "";
                            if (typeMeasure == "quant"){
                                barcode = oTable.fnGetData(i,12);
    		                }else if (typeMeasure == "qual"){
                                barcode = oTable.fnGetData(i,9);
    		                }
							window.opener.addTreat(currG, barcode, nameP, nameA, $("#date").val(), duration, $("#time").val()+':00', i);
                            console.log('-----');
                            console.log(row);
            				//jQuery(row).toggleClass('row_selected');
    		            }
		            }
                    console.log('i'+i);
                    console.log('tot'+tot);
                    if (i == tot - 1)
                        window.close();
                }
            }
        });
    }else
    	window.close();
}


//carica i singoli step del braccio selezionato
function loadStep(event){
	var event=event||window.event;
	idEl = event.target.id;
	arm = document.getElementById(idEl).getAttribute("armName");
    var table = document.getElementById('stepTable');

    var tableA = document.getElementById('armTable');
    var j = 0;
	for (j = tableA.rows.length; j >= 0; j--){
		if (document.getElementById("arm_cell"+j))
			document.getElementById("arm_cell"+j).style.color = 'black';
	}


    document.getElementById(idEl).style.color = "red";
	var url = base_url + "/api.list_step/" + arm;
	jQuery.ajax({
		url:url,
		method: 'get',
		success:function(transport) {
			//var response = transport.responseJSON;
			//var steps = eval('(' + response.list_step + ')');
			var steps = JSON.parse(transport['list_step']);
			var i = 0;
			var j = 0;
			document.getElementById('listStep').style.display = 'inline';
			for (j = table.rows.length; j >= 0; j--){
				if (document.getElementById("rowS"+j))
				    table.deleteRow(j);
			}
			while(steps[i])
				{
					var rowCount = table.rows.length;
					var row = table.insertRow(rowCount);
					row.setAttribute("id","rowS"+i);
					var cell = row.insertCell(0);
					cell.setAttribute("id","step_cell"+i);
					cell.innerHTML = 'From '+ steps[i]['start_step'] +' to '+ steps[i]['end_step'] +': '+ steps[i]['drugs_id'] +', '+ steps[i]['dose'] + ' mg, ' + steps[i]['schedule'] +' times via '+ steps[i]['id_via'];
					i++;
				}
		}
	});
}

//carica i bracci del protocollo selezionato
function loadArms(){
	var nameP = ""
    if (document.listProtocolsForm.list_protocols.length > 1) {
	    for (i=0; i<document.listProtocolsForm.list_protocols.length; i++){
		    if (document.listProtocolsForm.list_protocols[i].checked==true){
			    nameP = document.listProtocolsForm.list_protocols[i].nextSibling.data;
		    }
	    }
    }else{
        nameP = document.getElementById('id_list_protocols_0').nextSibling.data;
    }

    var table = document.getElementById('armTable');
	var protocol = nameP;
	var url = base_url + "/api.list_arm/" + protocol.substr(1);
	jQuery.ajax({
		url:url,
		method: 'get',
		dataType:'json',
		success:function(transport) {
			console.log(transport);
			//var response = transport.responseJSON;
			//var arms = eval('(' + response.list_arm + ')');
			var arms = JSON.parse(transport['list_arm']);
			var i = 0; var j = 0;
			document.getElementById('listArms').style.display = 'inline';
			document.getElementById('listStep').style.display = 'none';

			for (j = table.rows.length; j >= 0; j--){
				if (document.getElementById("row"+j))
				    table.deleteRow(j);
			}

			while(arms[i]){
				var rowCount = table.rows.length;
				var row = table.insertRow(rowCount);
				row.setAttribute("id","row"+i);
				var cell1 = row.insertCell(0);
				cell1.setAttribute("id","arm_cell"+i);

				cell1.setAttribute("class","defCursor");
				cell1.setAttribute("style", "border:4px outset lightgrey;background-color:silver;color:black;");
				var armName = arms[i].split(' --- ')
				cell1.setAttribute("onclick","start('"+armName[0]+"')"); //
				cell1.setAttribute("armName", armName[0]);
				cell1.innerHTML = arms[i];

				var cell2 = row.insertCell(1);
				cell2.setAttribute("id","info_cell"+i);
				cell2.setAttribute("onclick","loadStep(event)");
				cell2.setAttribute("class","defCursor");
				cell2.setAttribute("armname",armName[0]);
				cell2.setAttribute("style", "border:4px outset lightgrey;background-color:silver;color:black;");
				//cell2.innerHTML = "<img src='" + base_url + "/xeno_media/img/admin/selector-search.gif' id='view"+ i +"' armname='"+armName[0]+"'></img>";
                                cell2.innerHTML = "<img src='/xeno_media/img/admin/selector-search.gif' id='view"+ i +"' armname='"+armName[0]+"'></img>";
				i++;
			}
		}
	});
}
