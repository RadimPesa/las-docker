var formInUse = false;

//usata per centrare il focus nell'input per il barcode nel miceloading
function setFocus()
{
if(!formInUse) {
	if (document.getElementById('id_barcode'))
		document.getElementById('id_barcode').focus();
	}
}
//usata per centrare il focus nell'input barcode nelle misure
function setMeasureFocus()
{
if(!formInUse) {
	if (document.getElementById('id_barcode'))
		document.getElementById('id_barcode').focus();
	}
}

//controlla i caratteri in input (non usata)
function isNormalKey(evt)
{
	 var charCode = (evt.which) ? evt.which : event.keyCode
	 if ( charCode > 122 )
		return false;
	 return true;
}
// http://www.theasciicode.com.ar/ascii-control-characters/ascii-codes-127.html


//Adds new uniqueArr values to temp array
function uniqueArr(a) {
 temp = new Array();
 for(i=0;i<a.length;i++){
  if(!contains(temp, a[i])){
   temp.length+=1;
   temp[temp.length-1]=a[i];
  }
 }
 return temp;
}

//Will check for the Uniqueness
function contains(a, e) {
 for(j=0;j<a.length;j++)if(a[j]==e)return true;
 return false;
}

//verifica se un numero e' intero
function is_int(value){ 
  if((parseFloat(value) == parseInt(value)) && !isNaN(value)){
      return true;
  } else { 
      return false;
  } 
}

function is_numeric(input){
    console.log(input);
    console.log(typeof(input)=='number');
    return typeof(input)=='number';
}

//converte la tabella del diagramma di gantt in una stringa
function gantt2str(){
	var table = document.getElementById('ganttTable');
	var rowCount = table.rows.length;
	if (rowCount > 1){
		var strGantt = "";
		var strDrugs = "";
		for(var i=2; i<rowCount+1; i++) {
			var row = table.rows[i];
			for (var j=1; j<parseInt(document.getElementById('duration').innerText)+1; j++)
			{
				strGantt += document.getElementById("cell"+i+"_"+j).getAttribute('status');
			}
			strDrugs += "_" + document.getElementById("drug_cell"+i).innerText +"_" + document.getElementById("via_cell"+i).innerText +"_" + document.getElementById("dose_cell"+i).innerText +"_" + document.getElementById("schedule_cell"+i).innerText +"#";

			strGantt += "#";
		}
		var nameA = document.getElementById('name').innerHTML = document.getElementById('id_name').value;
		var description = document.getElementById('descr').innerHTML = document.getElementById('id_description').value;
		var duration = document.getElementById('duration').innerHTML = document.getElementById('id_duration').value;
		var e = document.getElementById("id_type_of_time");
		var typeTime = e.options[e.selectedIndex].text;
		var forces_explant = false;
		var chkbox = document.getElementById("id_forces_explant");
		if(null != chkbox && true == chkbox.checked) {
			forces_explant = true;
		}

        var table = document.getElementById('stepTable');
		var url = base_url + '/api.giveMeStep/' + strGantt.replace(/#/g,'&') + '/' + strDrugs.replace(/#/g,'&');
		jQuery.ajax({
            url:url, 
			method: 'get',
			success: function(transport) {
				var steps =JSON.parse(transport['list_step']);
				var i = 0;
				var j = 0;
				for (j = table.rows.length; j >= 0; j--){
					if (document.getElementById("rowS"+j))
						document.getElementById("rowS"+j).style.display = 'none'
				}
				while(steps[i]){
					var rowCount = table.rows.length;
					var row = table.insertRow(rowCount);
					row.setAttribute("id","rowS"+rowCount);
					var cell = row.insertCell(0);
					cell.setAttribute("id","step_cell"+rowCount);
					cell.setAttribute("arm",nameA);

					cell.innerHTML = 'From '+ steps[i]['start'] +' to '+ steps[i]['end'] +': '+ steps[i]['drug'].replace('#', ' ') +', '+ steps[i]['dose'] + ' mg, ' + steps[i]['schedule'] +' times via '+ steps[i]['via'].replace('#', ' ');
					i++;
				}
			}
		});

		jQuery.ajax({
			url: base_url + '/treatments/manage/newProtocol',
			type: 'POST',
			data: {'type': '0','statusGantt':strGantt, 'drugs':strDrugs, 'nameA':nameA, 'description':description, 'duration':duration, 'typeTime':typeTime, 'forcesExplant':forces_explant},
			dataType: 'text',
		});

 
	}else{
		alert("You have to insert at least one step in the treatment.")
	}
}

//per rimpiazzare un carattere in una stringa
String.prototype.replaceAt=function(index, char) {
  return this.substr(0, index) + char + this.substr(index+char.length);
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

//restituisce il nome di un trattamento
function getName(protocol, arm){
    return jQuery.trim(String(protocol)) + ' --- ' + jQuery.trim(String(arm));
}

//per contare gli elementi di un dict
function sizeDict(dict){
    var count = 0;
    for (var i in dict) {
        if (dict.hasOwnProperty(i)) count++;
    }
    return count
}


//http://www.randomsnippets.com/2008/03/26/how-to-dynamically-remove-delete-elements-via-javascript/
function removeElement(parentDiv, childDiv){
     if (childDiv == parentDiv) {
          alert("The parent div cannot be removed.");
     }
     else if (document.getElementById(childDiv)) {     
          var child = document.getElementById(childDiv);
          var parent = document.getElementById(parentDiv);
          parent.removeChild(child);
     }
     else {
          alert("Child div has already been removed or does not exist.");
          return false;
     }
}

function hasClass(ele,cls) {
    return ele.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
}
 
function addClass(ele,cls) {
    if (!this.hasClass(ele,cls)) ele.className += " "+cls;
}
 
function removeClass(ele,cls) {
    if (hasClass(ele,cls)) {
    	var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
        ele.className=ele.className.replace(reg,' ');
    }
}

//Get the selected TR nodes from DataTables
function fnGetSelected( )
{
    var aReturn = new Array();
    var aTrs = oTable.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( jQuery(aTrs[i]).hasClass('row_selected') )
	        aReturn.push( aTrs[i] );
    }
    return aReturn;
}


////LOCAL STORAGE FUNCTIONS
function storageIt(key, value){
    localStorage.setItem(key, value);
    localStorage.setItem(key + 'timestamp', new Date().getTime());
    localStorage.setItem(key + 'user', jQuery("#user_local_storage").val());
}

function clearStorage(listKey){
    for (var i = 0; i < listKey.length; i++){
        localStorage.removeItem(listKey[i]);
    }
}

//check in the local storage fo HTML5
function checkStorage(listKey, oTable){
    //console.log(listKey);
    if (localStorage.getItem(listKey[0])){
        //console.log(listKey[0] + 'user');
        //console.log(localStorage.getItem(listKey[0] + 'user'));
        //console.log(localStorage.getItem('expluser'));
        var username = localStorage.getItem(listKey[0] + 'user');
        var timestamp = localStorage.getItem(listKey[0] + 'timestamp');
        var d = new Date(timestamp*1);
        jQuery("#dialogMessage").text("Something bad happened, but we saved the data (actions made by "+username+" the "+d+"). What do you want to do?");
        jQuery( "#dialog" ).dialog({
            resizable: false,
            height:200,
            width:340,
            modal: true,
            draggable :false,
            buttons: {
                "Restore Old Data": function() {
                    restoreData(listKey, oTable);
                    jQuery( this ).dialog( "close" );
                },
                "Delete Old Data": function() {
                    clearStorage(listKey);
                    jQuery( this ).dialog( "close" );
                }
            }
        });
    }
}

//check in the local storage fo HTML5
function checkStorageMeasure(listKey, oTable, typeM){
    if (localStorage.getItem(listKey[0])){
        var username = localStorage.getItem(listKey[0] + 'user');
        var timestamp = localStorage.getItem(listKey[0] + 'timestamp');
        var d = new Date(timestamp*1);
        jQuery("#dialogMessage").text("Something bad happened, but we saved the data (actions made by "+username+" the "+d+"). What do you want to do?");
        jQuery( "#dialog" ).dialog({
            resizable: false,
            height:200,
            width:340,
            modal: true,
            draggable :false,
            buttons: {
                "Restore Old Data": function() {
                    restoreData(listKey, oTable, typeM);
                    jQuery( this ).dialog( "close" );
                },
                "Delete Old Data": function() {
                    clearStorage(listKey);
                    jQuery( this ).dialog( "close" );
                }
            }
        });
    }
}



function post_to_url(path, params, method) {
    method = method || "post"; // Set method to post by default, if not specified.
    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
    //jQuery(form).submit();
}
function capitaliseFirstLetter(string){
    return string.charAt(0).toUpperCase() + string.slice(1);
}
