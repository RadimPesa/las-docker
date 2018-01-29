$("span.home").click(function(){
    window.location="{% url _caQuery.views.home %}";	
});


//$(function() {
//    $('html').ajaxSend(function(event, xhr, settings) {
//	    function getCookie(name) {
//	        var cookieValue = null;
//	        if (document.cookie && document.cookie != '') {
//	           var cookies = document.cookie.split(';');
//	            for (var i = 0; i < cookies.length; i++) {
//	               var cookie = jQuery.trim(cookies[i]);
//	               // Does this cookie string begin with the name we want?
//	               if (cookie.substring(0, name.length + 1) == (name + '=')) {
//	                   cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//	                   break;
//	               }
//	           }
//	       }
//	       return cookieValue;
//	   }
//	   if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
//	       // Only send the token to relative URLs i.e. locally.
//	       xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
//	   }
//	});	
//});

$(function() { 
    
    $( "#tabs" ).tabs();
    
    $("#newdsdialog").dialog(
    	{
	        autoOpen: false,
	        modal: true,
            width: 350,
            resizable: false,
	        buttons:
	        [
	        	{
	                text: "Cancel",
	                click: function() {
	                	$(this).dialog("close");
	                }
	            },
                {
                    text: "Import",
                    click: function() {
                        $(this).dialog("close");
                        $("#plswait").dialog({ title: "Importing data source" });
                        $("#plswait").dialog("open");
                        var formData = new FormData($('#newdsform')[0]);
                        
                        $.ajax({
                            url: base_url + "/api/createds/",
                            type: 'POST',
                            /*xhr: function() {  // Custom XMLHttpRequest
                                var myXhr = $.ajaxSettings.xhr();
                                if(myXhr.upload){ // Check if upload property exists
                                    myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
                                }
                                return myXhr;
                            },*/
                            //Ajax events
                            success: function(msg) {
                                $("#plswait").dialog("close");
                                alert(msg[1], msg[0], "OK", function() { location.reload(); });
                            },

                            error: function() {
                                $("#plswait").dialog("close");
                                alert("Cannot connect to server", "Error");
                            },

                            // Form data
                            data: formData,
                            //Options to tell jQuery not to process data or worry about content-type.
                            cache: false,
                            contentType: false,
                            processData: false
                        });
                        
                        /*var name = $("#newds_name").val();
                        var url = $("#newds_url").val();
                        console.log($('#newdsform').serialize());
                        $.ajax({
                            type: "POST",
                            url: base_url + "/api/createds/",
                            data: "name=" + name + "&url=" + url,
                            dataType: "json",
                            success: function(msg) {
                                $("#plswait").dialog("close");
                                alert(msg[1], msg[0], "OK", function() { location.reload(); });
                            },
                            error: function() {
                                $("#plswait").dialog("close");
                                alert("Cannot connect to server", "Error");
                            }
                        });*/
                    }
                }
        	]
		}
	);
    
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
    
    $("#newqpdialog").dialog(
    	{
	        autoOpen: false,
	        modal: true,
            resizable: false,
            width: 460,
	        buttons:
	        [
	        	{
	                text: "Cancel",
	                click: function() {
	                	$(this).dialog("close");
	                }
	            },
                {
                    text: "OK",
                    click: function() {
                        if ($('#qpavl').data('pathok') == false) {
                            alert("No path has been selected matching the current entities.", "Warning");
                            return;
                        }
                        var path = []
                        $('#pathdisplay li').each(function() {
                            path.push($(this).data('r_id'));
                        });
                        var from = $('#newqp_entA').val();
                        var to = $('#newqp_entB').val();
                        $.ajax({
                            type: "POST",
                            url: base_url + "/api/createqp/",
                            data: "fromEnt=" + from + "&toEnt=" + to + "&path=" + JSON.stringify(path),
                            dataType: "json",
                            success: function(msg) {
                                if (msg[0] == 'Error') {
                                    alert(msg[1], msg[0], "OK");
                                } else {
                                    $(this).dialog("close");
                                    location.reload();
                                }
                                    
                            },
                            error: function() {
                                alert("Cannot connect to server", "Error");
                            }
                        });

                    }
                }
            ]
        }
    );

    $("#selds").change(
        function() {
            var ds = $("#selds").val();
            
            // populate lists in "Queryable entities" tab
            $('#qrbEnt option').remove();
            $('#avlEnt option').remove();
            $.ajax({
                url: base_url + "/api/dsEntList/",
                data: "ds="+ds,
                success: function(data) {
                    for (var i=0;i<data.length;++i) {
                        if (data[i].queryable == true) {
                            var el = $('<option value="'+data[i].id+'">'+data[i].name+'</option>').data("changed", false);
                            $("#qrbEnt").append(el);
                        } else {
                            var el = $('<option value="'+data[i].id+'">'+data[i].name+'</option>').data("changed", false);
                            $("#avlEnt").append(el);
                        }
                    }    
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
            
            // populate list in "Query paths" tab
            $('#qpaths option').remove();
            $.ajax({
                url: base_url + "/api/qpathList/",
                data: "ds="+ds,
                success: function(data) {
                    for (var i=0;i<data.length;++i) {
                        var el = $('<option value="'+data[i][0]+'">'+data[i][1] + ' &#8596; ' + data[i][2] +'</option>');
                        $("#qpaths").append(el);
                    }
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });

            
        }
    );

    $("#newdsbtn").click(
        function() {
            $("#newdsdialog").dialog("open");
        }
    );

    $("#dropdsbtn").click(
        function() {
            var ds = $("#selds").val();
            if (ds == null) return;
            $.ajax({
                type: "POST",
                url: base_url + "/api/deleteds/",
                data: "dsid=" + ds,
                dataType: "json",
                success: function(msg) {
                    alert(msg[1], msg[0], "OK", function() { location.reload(); });
                },
                error: function() {
                    alert("Cannot connect to server", "Error");
                }
            });
        }
    );

    $("#btnToRight").click(
        function() {
            $("#avlEnt option").filter(":selected").each(function() {
                    var c = !($(this).data("changed"));
                    var el = $('<option value="'+$(this).prop("value")+'">'+$(this).text()+'</option>').data("changed", c);
                    $("#qrbEnt").append(el);
                    $(this).remove();
                }
            );
        }
    );

    $("#btnToLeft").click(
        function() {
            $("#qrbEnt option").filter(":selected").each(function() {
                    var c = !($(this).data("changed"));
                    var el = $('<option value="'+$(this).prop("value")+'">'+$(this).text()+'</option>').data("changed", c);
                    $("#avlEnt").append(el);
                    $(this).remove();
                }
            );
        }
    );

    $("#btnReset").click(
        function() {
            $("#avlEnt").children().remove();
            $("#qrbEnt").children().remove();
            $("#selds").trigger('change');
        }
    );

    $("#btnSave").click(
        function() {
            var changedEnt = []
            $("#qrbEnt option").filter(function() {return $(this).data("changed")==true;}).each(function() {changedEnt.push($(this).val());});
            $("#avlEnt option").filter(function() {return $(this).data("changed")==true;}).each(function() {changedEnt.push($(this).val());});
            if (changedEnt.length > 0) {
                $.ajax({
                    type: "POST",
                    url: base_url + "/api/updatedsent/",
                    data: "entList=" + JSON.stringify(changedEnt),
                    dataType: "json",
                    success: function(msg) {
                        alert(msg[1], msg[0], "OK");
                        $("#qrbEnt option").filter(function() {return $(this).data("changed")==true;}).each(function() {($(this).data("changed", false));});
                        $("#avlEnt option").filter(function() {return $(this).data("changed")==true;}).each(function() {($(this).data("changed", false));});
                    },
                    error: function() {
                        alert('err');
                    }
                });
            }
        }
    );

    $("#newqpbtn").click(
        function() {
            $('#newqp_entA option').remove();
            $('#newqp_entB option').remove();
            $('#pathdisplay').children().remove();
            $('#pathimg').removeClass().addClass('statuscheck');
            $('#pathavl').data('pathok', false);
            var ds = $("#selds").val();
            if (ds == null) {
                return;
            }
            $.ajax({
                url: base_url + "/api/dsEntList/",
                data: "ds="+ds+"&queryable=yes",
                success: function(data) {
                    for (var i=0;i<data.length;++i) {
                        $("#newqp_entA").append('<option value="'+data[i].id+'">'+data[i].name+'</option>');
                        $("#newqp_entB").append('<option value="'+data[i].id+'">'+data[i].name+'</option>');
                        $("#newqp_entA").prop("selectedIndex", -1);
                        $("#newqp_entB").prop("selectedIndex", -1);
                    }
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
            $("#newqpdialog").dialog("open");
            $("#newqp_entA").change(function() { $('#pathimg').removeClass().addClass('statuscheck'); $('#qpavl').data('pathok', false); });
            $("#newqp_entB").change(function() { $('#pathimg').removeClass().addClass('statuscheck'); $('#qpavl').data('pathok', false); });

        }
    );

    $("#findpathbtn").click(
        function() {
            entA = $("#newqp_entA").val();
            entB = $("#newqp_entB").val();
            if (entA == null || entB == null || entA == entB) {
                return;
            }
            $('#pathdisplay').children().remove();
            $('#pathimg').removeClass().addClass('statusload');
            $.ajax({
                url: base_url + "/api/getsqp/",
                data: "fromEntId="+entA+"&toEntId="+entB,
                success: function(data) {
                    if (data.length > 0) {
                        $('#qpavl').data('pathok', true);
                        $('#pathimg').removeClass().addClass('statusok');
                        for (var i = 0; i < data.length; ++i) {
                            var cl = (i % 2 == 0) ? "even" : "odd";
                            var el = $('<li class="'+ cl +'"><span class="small">From</span>&nbsp;<span class="highlight">'+ data[i][0] +'</span><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp<span class="small">to</span>&nbsp;<span class="highlight">'+ data[i][1] +'</span><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="small">via</span>&nbsp;<span class="highlight">'+ data[i][2] +'</span></li>').data('r_id', data[i][3]);
                            $("#pathdisplay").append(el);
                        }
                    } else {
                        $('#pathimg').removeClass().addClass('statusnok');
                        $("#pathdisplay").append('<span class="highlight">No path available.</span>');
                    }
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
        }
    );

    $("#editpathbtn").click(
        function() {
            alert("Sorry, not implemented yet!");
        }
    );

    $("#iconfile").change(
        function(evt) {
            var f = evt.target.files[0];
            $("#previewcont span").remove();
            if (!f) {
                $("#previewcont").append('<span><img class="thumb" src="/caQuery_media/images/noimage.gif" />');
            } else if (!f.type.match('image.*')) {
                $("#previewcont").append('<span><img class="thumb" src="/caQuery_media/images/invalidimage.gif" />');
            } else {
                var reader = new FileReader();
                reader.onload = (function(theFile) {
                    return function(evt) {
                        $("#previewcont").append('<span><img class="thumb" src="' + evt.target.result + '" title="' + escape(theFile.name) + '" />');
                    }
                }) (f);
                reader.readAsDataURL(f);
            }
        }
    );
    
    $('#normcolor').colpick({
        colorScheme:'dark',
        layout:'hex',
        onSubmit:function(hsb,hex,rgb,el) {
            $(el).css('background-color', '#'+hex);
            $(el).colpickHide();
            $('#normcolhex').val('#'+hex);
        }
    });

    $('#hovercolor').colpick({
        colorScheme:'dark',
        layout:'hex',
        onSubmit:function(hsb,hex,rgb,el) {
            $(el).css('background-color', '#'+hex);
            $(el).colpickHide();
            $('#hcolhex').val('#'+hex);
        }
    });
    
    $('.colpick').css('z-index', 9999);
    
    $("#defqedialog1").dialog(
    	{
	        autoOpen: false,
	        modal: true,
            resizable: false,
            width: 700,
            height: 500,
	        buttons:
	        [
	        	{
	                text: "Cancel",
	                click: function() {
                        $(this).dialog("close");
	                }
	            },
                {
                    text: "< Previous",
                    click: function() {
                    },
                    disabled: true
                },
                {
                    text: "Next >",
                    click: function() {
                        var srcent = $("#srcent1").val();
                        if (srcent == null) {
                            return;
                        }
                        $("#srcent2").val(srcent);
                        $("#srcent2").trigger("change");
                        $(this).dialog("close");
                        $("#defqedialog2").dialog("open");
                    }
                }

            ]
        }
    );
    
    $("#defqedialog2").dialog(
    	{
	        autoOpen: false,
	        modal: true,
            resizable: false,
            width: 700,
            height: 500,
	        buttons:
	        [
	        	{
	                text: "Cancel",
	                click: function() {
                        $(this).dialog("close");
	                }
	            },
                {
                    text: "< Previous",
                    click: function() {
                        $(this).dialog("close");
                        $("#defqedialog1").dialog("open");
                    }
                },
                {
                    text: "Next >",
                    click: function() {
                        $(this).dialog("close");
                        $("#defqedialog3").dialog("open");
                    }
                }

            ]
        }
    );

    $("#newqentbtn").click(
        function() {
            var ds = $("#selds").val();
            if (ds == null) {
                return;
            }
            $.ajax({
                url: base_url + "/api/dsEntList/",
                data: "ds="+ds,
                success: function(data) {
                    for (var i=0;i<data.length;++i) {
                        $("#srcent1").append('<option value="'+data[i].id+'">'+data[i].name+'</option>');
                    }
                    $("#srcent1").prop("selectedIndex", -1);
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
            
            $("#defqedialog1").dialog("open");
            
        }
    );
    
    $("#usrno").change(
        function() {
            $("#yes").css("display", "none");
            $("#no").css("display", "");
        }
    );

    $("#usryes").change(
        function() {
            $("#yes").css("display", "");
            $("#no").css("display", "none");
        }
    );
    
    $("#srcent2").change(
        function() {
            var srcent2 = $("#srcent2").val();
            $("#relent option").remove();
            $("#srcent1 option").each(
                function() {
                    if ($(this).val() != srcent2) {
                        $("#relent").append($(this).clone());
                    }
                }
            );
        }
    );

    
    
    
});


