function derivedyn(){
	var altype=$("select#aliquottype").val();
	
	if(altype==""){
		$("input#aliquotnumber").attr("disabled", "disabled");
		$("input#aliquotnumber").val("");
	}
	else{
		$("input#aliquotnumber").removeAttr("disabled");
		if(altype!="R" && altype!="D" && altype!="P"){
			$("select#derived2type").attr("disabled", "disabled");
			$("input#derivednumber").attr("disabled", "disabled");
			$("select#derived2type").val("");
			$("input#derivednumber").val("");
		}
		else{
			$("select#derived2type").removeAttr("disabled");
			$("input#derivednumber").removeAttr("disabled");
		}
	}
}

function vectorcheck(){
	if($("select#vector").val()=="H"){
		$("input#lineage").attr("disabled", "disabled");
		$("input#lineage").val("");
		$("input#passage").attr("disabled", "disabled");
		$("input#passage").val("");
		$("input#mousenumber").attr("disabled", "disabled");
		$("input#mousenumber").val("");
		$("select#tissuetype").attr("disabled", "disabled");
		$("select#tissuetype").val("");
	}
	else{
		$("input#lineage").removeAttr("disabled");
		$("input#passage").removeAttr("disabled");
		$("input#mousenumber").removeAttr("disabled");
		$("select#tissuetype").removeAttr("disabled");
	}	
}

function genIdFromForm() {
	
	var genid = $(".genidpar").map(function() {
		var v=$(this).val().toUpperCase();
		if (v) {
			var l = parseInt($(this).attr("maxlength")) - v.length;
			if (l > 0) {
				v = new Array(l+1).join("0") + v;
			}
			return v;
		} else {
			console.log (this, $(this).attr("maxlength"))
			return new Array(parseInt($(this).attr("maxlength"))+1).join("-")
		}
	}).get();

	genid = genid.join("");
	var l = 26 - genid.length;
	if (l > 0) {
		genid += new Array(l+1).join("-");
	}
	console.log(genid)
	return [genid];
}



function genIdFromForm2() {
	
	var genid = $(".genidpar2").map(function() {
		var v=$(this).val().toUpperCase();
		if (v) {
			var l = parseInt($(this).attr("maxlength")) - v.length;
			if (l > 0) {
				v = new Array(l+1).join("0") + v;
			}
			return v;
		} else {
			console.log (this, $(this).attr("maxlength"))
			return new Array(parseInt($(this).attr("maxlength"))+1).join("-")
		}
	}).get();

	genid = genid.join("");
	var l = 26 - genid.length;
	if (l > 0) {
		genid += new Array(l+1).join("-");
	}
	console.log(genid)
	return [genid];
	

}

function genIdFromText(){

	var elenco = $("textarea#fullgenid").val();
    var invalid = []
	elenco = elenco.split(/\s+/g);
	for(e in elenco){
		if (elenco[e].length == 0)
            continue;
        if(elenco[e].length != 26){
			invalid.push(elenco[e]);
		} else {
            appendGenid(elenco[e]);
        }
		//if($("div#genidlist").find(":contains('"+elenco[e]+"')").length==0)
		//	$("div#genidlist").append('<p id="genidel">'+elenco[e]+'</p>');
	}
	if (invalid.length != 0) {
        var s_alert = "";
        var s_text = "";
        for (var i=0; i<(invalid.length > 3 ? 3 : invalid.length);++i) {
            s_alert += invalid[i] + '<br>';
        }
        s_alert = s_alert.substr(0,s_alert.length-4); //strip final <br>
        for (var i=0; i<invalid.length; ++i) {
            s_text += invalid[i] + '\n';
        }
        s_text = s_text.substr(0,s_text.length-1); //strip final newline
        $("textarea#fullgenid").val(s_text);
        s_alert += invalid.length > 3 ? "<br>and " + (invalid.length-3) + " more" : "";
        alert("Invalid Genealogy ID(s):<br><br>"+s_alert,"Warning", "Ok", function(){$("textarea#fullgenid").focus();});
    } else {
        $("textarea#fullgenid").val("");
        $("textarea#fullgenid").focus();
    }
    
	
}

//funzione per aggiungere lista con i box azzurri
function appendGenid(value){
    if(value!="" && $("#genidlist .dialogitem:contains('"+value+"')").length == 0) { // value is not empty and element isn't already in the list
        $("#genidlist").append(    '<span class="dialogitem">'+value+
                                            '<span class="ditemclose ui-icon ui-icon-closethick"></span>'+
                                            '</span>');
        $("#genidlist span.dialogitem").last().children("span.ditemclose").click(function() {
            $(this).parent().remove();
        });
    }
    //$("#addvalue"+param_id).val("");
    //$("#addvalue"+param_id).focus();
};