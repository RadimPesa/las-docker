$(document).ready(function() {
    var oTable;
    started = false;
});

function openTable(labelT){
    console.log(labelT);
    
    //send name table db for the complete list
    var url = base_url + '/xenoAdmin/start';
    var first = true;
    var th = [];
    $("#allRecords tbody").empty();
    $("#allRecords thead").empty();
    $("#form").empty();
    //create  the form
    var string = "<table>";
    for (attr in tables[labelT]['attrs']){
        console.log(attr);
        console.log(tables[labelT]['attrs'][attr]);
        var type = tables[labelT]['attrs'][attr];
        var mandatory = "";
        if (type.split('|')[1] == 'y')
            mandatory = ' (*)';
        if (type.split('|')[0] == 'string'){
            string += '<tr><td><label for "'+ attr +'">'+attr+mandatory+' </td><td><input id = "' + attr +'" type="text" mandatory="'+type.split('|')[1]+'" maxlength="' + type.split('|')[2] + '"></label></td></tr>';
        }else{
            string += '<tr><td><label for "'+ attr +'">'+attr+mandatory+'</td><td><textarea id="'+attr+'" rows="4" mandatory="'+type.split('|')[1]+'" cols="50"></textarea></label></td></tr>';
        }
    }
    string += "</table><br/><input type='button' value='Add record' onclick='addRecord(" + '"' + labelT + '"' + ");'/>";
    $("#form").append(string);
    $.ajax({
        url: url,
        type: 'get',
        data: {'nameT': tables[labelT]['nameT']},
        success: function(response) {
            console.log(response);
            $("#list").hide();
            $("#records").show();
            if (started){
                /*var len = oTable.fnGetNodes().length;
                for(var i = 0; i < len; i++) {
                    oTable.fnDeleteRow(0);
                }*/
                $('*[class^="dataTable"]').remove();
                $('hr').after("<table id='allRecords'><thead></thead><tbody></tobdy></table>");
            }
            for (r in response){
                string = '<tr>';
                for (f in response[r]){
                    if (f.substring(0, 2) != "id"){
                        if (first)
                            th.push(f);
                        string += '<td>'+ response[r][f]+"</td>";
                    }
                }
                string += '</tr>';
                first = false;
                $("#allRecords tbody").append(string);
            }
            string = '<tr>';
            for (var i = 0; i < th.length; i++){
                string += '<th>' + th[i] + '</th>';
            }
            string += '</tr>';
            $("#allRecords thead").append(string);
            oTable = $("#allRecords").dataTable({ "sDom": 'TRCH<\"clear\">lfrtip'} );
            started = true;
        }
    });
}

function addRecord(labelT){
    console.log(labelT);
    var mandatoryElems = $("[mandatory='y']");
    for (var i = 0; i < mandatoryElems.length; i++){
        if ( $(mandatoryElems[i]).val() == "" ){
            alert("Please, fill all the mandatory inputs.", "Warning");
            return;
        }
    }
    console.log('passati controlli');
    var dataR = {};
    for (attr in tables[labelT]['attrs']){
        var value = $("#"+attr).val();
        dataR[attr] = value;
    }
    console.log(dataR);
    var url = base_url + '/xenoAdmin/start';
    var d = JSON.stringify({'dataR': dataR, 'model': tables[labelT]['nameT']});
    console.log(d);
    $.ajax({
        url: url,
        type: 'post',
        data: {'d':d},
        success: function(response) {
            console.log(response);
            if (response.substring(0, 3) == 'Add'){
                openTable(labelT)
            }else{
                alert(response);
            }
        }
    });
}
