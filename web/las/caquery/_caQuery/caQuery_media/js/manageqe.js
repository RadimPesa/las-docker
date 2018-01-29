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
            $("#dsform").submit();
            return;
            $.get({
                url: "./",
                data: "ds="+ds,
                success: function(data) {
                    data = JSON.parse(data);
                    $("#qent option").remove();
                    for (i = 0; i < data.length; ++i) {
                        $("#qent").append('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
                    }
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
        }
    );


    $("#newqebtn").click(
        function() {
            var ds = $("#selds").val();
            if (ds == null)
                return;
            var w = screen.width-100;
            var h = screen.height-400;
            var left = 10;//(screen.width/2)-(w/2);
            var top = 10;//(screen.height/2)-(h/2);
            neww=window.open(   newqe_url+"?ds="+ds,
                                "_self",
                                'toolbar="no", location="no", status="no",'+
                                'menubar="no", scrollbars="no", resizable="no", '+
                                'width='+w+', height='+h+', top='+top+', left='+left
                            );

            if (window.focus) {
                neww.focus();
            }
        }
    );


    $("#editqebtn").click(
        function() {
            var ds = $("#selds").val();
            var qe = $("#qent").val();
            if (ds == null || qe == null)
                return;
            var w = screen.width-100;
            var h = screen.height-400;
            var left = 10;//(screen.width/2)-(w/2);
            var top = 10;//(screen.height/2)-(h/2);
            neww=window.open(   newqe_url+"?ds="+ds +"&qe=" + qe,
                                "_self",
                                'toolbar="no", location="no", status="no",'+
                                'menubar="no", scrollbars="no", resizable="no", '+
                                'width='+w+', height='+h+', top='+top+', left='+left
                            );

            if (window.focus) {
                neww.focus();
            }
        }
    );

    $("#dropqebtn").click(
        function() {
            var ds = $("#qent").val();
            if (ds == null) return;

            var name = $("#qent option:selected").map(function() {return $(this).text();}).get().join('<br>');
            if (ds.length > 1) {
                var suff_ent = "ies";
                var adj = "these";
            } else {
                var suff_ent = "y";
                var adj = "this";
            }
            confirm("Do you really want to delete " + adj + " entit" + suff_ent + "?<br><br><b>" + name + "</b>", "Confirm", "Yes", "No", dropqe(ds));

        }
    );
}


function dropqe(ds) {
    return function() {
        $.ajax({
            url: "./",
            data: "dropQe=".concat(ds.join('&dropQe=')),
            type: "POST",
            success: function(data) {
                $("#selds").change();
            },
            error: function(data) {
                alert(data.responseText);
            }
        });
    }
}
