jQuery(document).ready(function() {
	jQuery('body').ajaxComplete(function(e, xhr, settings) {
		if (xhr.status == 278) {
		    window.location.href = xhr.getResponseHeader("Location").replace(/\?.*$/, "?next="+window.location.pathname);
		}
	});
	var currentDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
	var day = currentDate.getDate()
	var month = currentDate.getMonth() + 1
	var year = currentDate.getFullYear()
	var tomorrowDate = year + '-' + month + '-' + day;
	var time = "08:30";
	jQuery("#date").val(tomorrowDate);
	jQuery("#time").val(time);
	list_mice();
	$("#date").datetimepicker({
	    altField: "#time",
	    dateFormat: "yy-mm-dd"
	});
});

function alertCB(){
	//$(this).dialog("close");
	//div.remove();
	window.close();
}

//controlla i topi selezionati nella finestra che ha aperto questa e crea la tabella con i topi selezionati
function list_mice() {
	var oTable = window.opener.oTable;
    var table = window.opener.document.getElementById("measure");
    var typeMeasure = window.opener.typeMeasure;
    var rowCount = table.rows.length;
    var maxIndex = 0;var k = 0;var j = 0;
    var rows = window.opener.fnGetSelected(); //array con le righe selezionate
	var genealogy = new Array();var barcode = new Array();
	var close = false; var string = "";
    if (rows.length > 0){
        for(var i = 0; i < oTable.fnGetNodes().length; i++) {
            var row = oTable.fnGetNodes()[i];
            if (jQuery.inArray(row, rows) > -1){
            	//alert(oTable.fnGetData(i, 9));
			    if (oTable.fnGetData(i, 9) != "-" && oTable.fnGetData(i, 9) != "STOPPED" && oTable.fnGetData(i, 9) != ""){
                    var genID = oTable.fnGetData(i, 0);
				    string = (string == "") ? genID : string + ', ' + genID;
				    close = true;
			    }
			    genealogy[j] = oTable.fnGetData(i, 0);
			    barcode[j] = oTable.fnGetData(i, 1);
				j++;
            }
        }
        if (close)
        	alert("Mouse with genealogyID: "+ string + " has already a treatment. You have to stop it if you want to start a new treatment", 'Error', 'Ok', alertCB);
        console.log('glen'+genealogy.length);
	    for (k=0; k < genealogy.length; k++)
    		addRow(genealogy[k], barcode[k]);
	}

}

//aggiunge una riga alla tabella contenente i topi su cui verrà applicato il trattamento
function addRow(genealogy, barcode) {
	var table = document.getElementById('dataTable');
	var rowCount = table.rows.length;
	var newRow = rowCount + 1;
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

function loadArms(){
	var nameP = "";
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
		datatype: 'json',
		success:function(transport) {
			var arms = JSON.parse(transport.list_arm);
			document.getElementById('listArms').style.display = 'inline';
			document.getElementById('listStep').style.display = 'none';
			var i = 0;
			for (var j = table.rows.length; j >= 0; j--){
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

function loadStep(event){
	var event = event||window.event;
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
		datatype: 'json', 
		success:function(transport) {
			var steps = JSON.parse(transport.list_step);
			document.getElementById('listStep').style.display = 'inline';
			for (var j = table.rows.length; j >= 0; j--){
				if (document.getElementById("rowS"+j))
				    table.deleteRow(j);
			}
			var i = 0;
			while(steps[i]){
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

//associa il trattamento selezionato ai topi checkati nella finestra padre. Poi chiude questa finestra
function start(nameA) {
    var nameP = "";
	var oTable = window.opener.oTable;
    var rows = window.opener.fnGetSelected(); //array con le righe selezionate
	nameP = $('input[name=list_protocols]:checked').parent().text().trim();
    writeTable(oTable, rows, nameP, nameA);
}

function writeTable(oTable, rows, nameP, nameA){
	var comments = window.opener.jQuery('#checkNotes').val();
    url = base_url + "/api.durationA/" + nameA;
    jQuery.ajax({
    	url:url,
        method: 'get',
        datatype:'json',
        success:function(duration) {
            var tot = oTable.fnGetNodes().length;
            var start = $("#date").val() + ' ' + $("#time").val();
            var nameT = getName(nameP, nameA);
            for(var i = 0; i <= tot; i++) {
                var row = oTable.fnGetNodes()[i];
                if (jQuery.inArray(row, rows) > -1){
                	var barcode = oTable.fnGetData(i, 1);
					for (biomouse in window.opener.physBio[barcode]){
						var genID = window.opener.physBio[barcode][biomouse]['genID'];
						var k = window.opener.isInCurrentTable(genID);
                        if (window.opener.actions.hasOwnProperty(genID)){
                            window.opener.actions[genID]['treatment']['action'] = "start";
                            window.opener.actions[genID]['treatment']['name'] = nameT;
                            window.opener.actions[genID]['treatment']['dateP'] = document.getElementById("date").value +' '+document.getElementById("time").value;
                        }else{
                            window.opener.addKey(genID);
                            window.opener.actions[genID]['treatment']['action'] = "start";
                            window.opener.actions[genID]['treatment']['name'] = nameT;
                            window.opener.actions[genID]['treatment']['dateP'] = document.getElementById("date").value +' '+document.getElementById("time").value;
                        }
						if (k > -1){
							var index = k;
                            var tr = window.opener.oSettings.aoData[index].nTr;
                    		oTable.fnUpdate(getName(nameP, nameA), index, 9, false, false);
                    		oTable.fnUpdate(document.getElementById("date").value +' '+document.getElementById("time").value, index, 10, false, false);
                    		oTable.fnUpdate(duration, index, 11, false, false);
                            window.opener.jQuery(tr).children("td:nth-child(9)").attr('status','new');
                            window.opener.jQuery(tr).attr('status','new');
                            if (jQuery(row).hasClass('row_selected'))
            					jQuery(row).toggleClass('row_selected');
                            oTable.fnUpdate(nameT, index, 9, false, false);
                            oTable.fnUpdate(start, index, 10, false, false);
                            oTable.fnUpdate(duration, index, 11, false, false);
                            oTable.fnUpdate(comments, index, 14, false, false);

						}
					}
                }
                if (i == tot - 1)
                    window.close();
            }
        }
    });	
}
