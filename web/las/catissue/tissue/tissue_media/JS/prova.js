function save() {
	
        var data = {
        		barcode: "ciao",
        };

        $.post("/caxeno/", data, function (result) {

        	if (result != "failure") {
        		$("#ins").before("Tutto a posto<br><br>");
        	}
        	else {
        		alert("Error");
        	}
        });

return false;
}



$(document).ready(function () {
	$("#ins").click(save);
});