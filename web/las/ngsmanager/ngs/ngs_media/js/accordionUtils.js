function selectAll(checkBox){
	var accordionId = $(checkBox).attr("value");
	
	var checkBoxes = checkBoxToArray(accordionId);
	//console.log(checkBoxes);
	var changedVal = 0;
	if (checkBoxStatus(checkBoxes)){
		//select all
		var t = $("#" + accordionId + "Table").dataTable();
		var input = t.$("tr").find("input");
		$.each(input, function(index, el){
			if ($(el).prop('checked') == false){
				changedVal++;
				$(el).prop('checked', true);
			}
		});
		return changedVal;
	}else{
		//deselect all
		var t = $("#" + accordionId + "Table").dataTable();
		var input = t.$("tr").find("input");

		$.each(input, function(index, el){
			if ($(el).prop('checked') == true){
				changedVal++;
				$(el).prop('checked', false);
			}
		});
		return -changedVal;
	}
}

//return true if all boxes have to be checked
//return false if all boxes have to be unchecked
function checkBoxStatus(checkBoxes){
	for (var i=0; i < checkBoxes.length; i++){
		if (checkBoxes[i] == false)
			return true;
	}
	return false;
}

function checkBoxToArray(accordionId){
	//var trs = $("#"+accordionId + " table tbody tr");
	var t = $("#" + accordionId + "Table").dataTable();
	var input = t.$("tr").find("input");
	var checkBoxes = [];
	for (var i=0; i < input.length; i++){
		//var checkB = $($(trs[i]).children("td")[5]).children("input")[0];
		checkBoxes.push($(input[i]).is(':checked'))
	}
	return checkBoxes;
}

function testBoxAll(selectOneBox){
	var accordionId = $(selectOneBox).attr('name');
	var checkBoxes = checkBoxToArray(accordionId);
	switchSelectAll(accordionId, checkBoxes);
	return ($(selectOneBox).prop('checked') ? 1 : -1 );
}

//seleziona/deseleziona il select all se all'interno si modifica le selezioni
function switchSelectAll(accordionId, checkBoxes){
	//console.log(checkBoxes.length);
	for (var i=0; i < checkBoxes.length; i++){
		//console.log(checkBoxes[i]);
		if (checkBoxes[i] == false){
			$("input.selectAll[name='"+accordionId+"']").prop('checked', false);
			return;
		}
	}
	$("input.selectAll[name='"+accordionId+"']").prop('checked', true);
}


function getSelectedValue(){
	elements = [];
	$.each ( $("tr").find("input.selectOne:checked"), function(index, value){
		elements.push($(value).attr('value'));
	});
	return elements;
}

