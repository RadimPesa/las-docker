$(function() {
    initCsrf();
	inithandlers();
	initdialog();
});

function initCsrf() {
	$.ajaxPrefilter(function(options, originalOptions, jqXHR) {
	  var token;
	  if (!options.crossDomain) {
	    token = $.cookie("csrftoken");
	    if (token) {
	      return jqXHR.setRequestHeader('X-CSRFToken', token);
	    }
	  }
	});
}

function initdialog() {
	$("#plswait").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            closeOnEscape: false,
            open: function(event, ui) {
                $("#ui-dialog-title-plswait").siblings("a").remove();
            }
        }
    );
}

function inithandlers() {
	$("#selds").change(
		function() {
			var ds = $("#selds").val();
			if (ds == null) return;
			$.ajax({
                url: "./",
                data: "dsData="+ds,
                success: function(data) {
                	data = JSON.parse(data);
                    $("#dsname").val(data['name']);
                    $("#dsdescr").val(data['description']);
                    $("#dscolor").val(data['color']);
                    $("#dscolorh").val(data['colorHover']);
                    $("#dscolorc").val(data['colorClicked']);
                    $("#preview").attr("src", data['iconUrl']);
                    $("#dsurl").val(data['url']);
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
		}
	);

	$("#dsicon").change(
        function(evt) {
            var f = evt.target.files[0];
            //$("#previewcont span").remove();
            if (!f) {
                $("#preview").attr("src", "/caQuery_media/images/pic-icon.png");
            } else if (!f.type.match('image.*')) {
                alert("Invalid image file!");
                $("#preview").attr("src", "/caQuery_media/images/pic-icon.png");
                $("#dsicon").val("");
            } else {
                var reader = new FileReader();
                reader.onload = (function(theFile) {
                    return function(evt) {
                        $("#preview").attr("src", evt.target.result);
                    }
                }) (f);
                reader.readAsDataURL(f);
            }
        }
    );

	$("#newdsbtn").click(
		function() {
			$("#selds").prop("selectedIndex", -1);
			$(".dsdata").val("");
			$("#dscolor").val("#81bb81");
			$("#dscolorh").val("#aaffaa");
			$("#dscolorc").val("#66ff66");
			$("#dsicon").attr("disabled", false).val("");
			$("#preview").attr("src", "/caQuery_media/images/pic-icon.png");
			$(".dsdata").attr("readonly", false);
			$("#dsname").focus();
		}
	);

	$("#refreshdsbtn").click(
		function() {
			var ds = $("#selds").val();
			if (ds == null) return;
			refreshds(ds);
		}
	);

	$("#dropdsbtn").click(
		function() {
			var ds = $("#selds").val();
			if (ds == null) return;

			var name = $("#selds option:selected").text();
			
			confirm("Do you really want to delete data source " + name + "?", "Confirm", "Yes", "No", dropds(ds));

		}
	);

	$("#savedsbtn").click(
		function() {
			var ds = $("#selds").val();
			var error = false;
			if (ds) {
				$(".dsdata[type!=file]").removeClass("error").each(function() {
					if ($.trim($(this).val()).length == 0) {
						$(this).addClass('error');
						error = true;
					}
				});
			} else {
                console.log("error");
                ds = '';
				$(".dsdata").removeClass("error").each(function() {
					if ($.trim($(this).val()).length == 0) {
						$(this).addClass('error');
						error = true;
					}
				});
			}
			if (error) {
				alert("Please fill out all mandatory fields!", "Alert");
				return;
			}
			
			$("#plswait").dialog({ title: "Please wait" });
            $("#pwcontent").text("Creating data source...");
            $("#plswait").dialog("open");
			var formData = new FormData($('#dsform')[0]);
			formData.append("newDs", ds);
			$.ajax({
                url: "./",
                data: formData,
                type: "POST",
                success: function(data) {
                	$("#plswait").dialog("close");
                	if (ds) {
                		alert("Data source updated", "Done", "OK", function() {window.location.reload();});
                	} else {
                		refreshds(data);
                	}
                },
                error: function(data) {
                	$("#plswait").dialog("close");
                    alert(data.responseText);
                },
                cache: false,
                contentType: false,
                processData: false
            });
		}
	);
}

function refreshds(ds) {
	$("#plswait").dialog({ title: "Please wait" });
	$("#pwcontent").text("Importing database schema...");
    $("#plswait").dialog("open");
	$.ajax({
    	url: "./",
    	data: "refreshDs="+ds,
    	type: "POST",
    	success: function(data) {
    		$("#plswait").dialog("close");
    	   	alert("Data source saved", "Done", "OK", function() {window.location.reload();});
    	},
    	error: function(data) {
    		$("#plswait").dialog("close");
        	alert(data.responseText);
    	}
    });
}

function dropds(ds) {
	return function() {
		$.ajax({
	        url: "./",
	        data: "dropDs="+ds,
	        type: "POST",
	        success: function(data) {
	        	window.location.reload();
	        },
	        error: function(data) {
	            alert(data.responseText);
	        }
        });
	}
}
