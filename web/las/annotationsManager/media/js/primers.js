
$(function() { 
    initCsrf();
    initTable();
    initButtons();
 });

function initCsrf() {
    $('html').ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }); 
}

function initTable() {
    alignDataTable = $("#alignments").dataTable({
        bFilter: false,
        bLengthChange: false,
        //"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": 5,
        aoColumns: [
            { sTitle: '<input type="checkbox" id="selall" value="">',
              //sWidth: "10%",
              bSortable: false,
              sClass: "centered" },
            { sTitle: "Chr",
              //sWidth: "15%",
              sClass: "centered" },
            { sTitle: "Start",
              //sWidth: "30%",
              sClass: "centered" },
            { sTitle: "End",
              //sWidth: "30%",
              sClass: "centered" },
            { sTitle: "Str",
              //sWidth: "5%",
              sClass: "centered" },
            { sTitle: "Gene",
              //sWidth: "20%",
              sClass: "centered" }
        ],
        oLanguage: {
            sEmptyTable: "No alignments available"
        },
        aaSorting: [[1, "asc"]]
    });
    
    $("#selall").change(toggleSelAlign);

}

function toggleSelAlign() {
    var val = $("#selall").is(":checked");
    alignDataTable.$('input').prop('checked', val);
}

function initButtons() {
    $("#align").click(function() {
        alignDataTable.fnClearTable();
        var tsname = $('#tsname').val();
        var sequence = $('#sequence').val();
        if (!tsname || !sequence) {
            return;
        }
        $.ajax({
            url: window.location,
            type: 'GET',
            success: function(msg) {
                var a = JSON.parse(msg);
                var tb = $("#alignments tbody");
                for (var i = 0; i < a.length; ++i) {
                    alignDataTable.fnAddData(['<input type="checkbox" name="alignments" value="'+i+'">'].concat(a[i]));
                }
                $("#selall").prop("checked", true).trigger("change");
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            },
            data: 'tsname='+tsname+'&sequence='+sequence
        });
    });

    $("#save").click(function() {
        var x = alignDataTable.$("input[name='alignments']:checked");
        var y = $("#savefrm input[name='ref'],#savefrm input[name='csrfmiddlewaretoken']");
        $.merge(x,y);
        var fd = x.serialize();
        $.ajax({
            url: window.location,
            type: 'POST',
            success: function(msg) {
                if (ref == 'newsp') {
                    msg = JSON.parse(msg);
                    window.opener.$(window.opener.activeEl).val(msg[1]);
                    window.opener.$(window.opener.activeEl).data("seqid", msg[0]);
                    window.opener.$(window.opener.activeEl).change();
                    window.close();
                } else {
                    location.reload();
                }
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            },
            data: fd,
            cache: false,
            contentType: false,
            processData: false
        });
    });

    $("#browse, #filename1").click(function() {
        $('#filename').click();
    });

    $("#filename").change(function() {
        $("#filename1").val($(this).val().split('\\').pop());
    });

    var fileinfo_ot = new Opentip(
                        "#fileinfo",
                        "Sequences should be listed in a single-tab-separated file, according to the following format:<br><br>"+
                        "<pre style='color: #452063'>identifier_1     sequence_1\nidentifier_2     sequence_2\n...              ...</pre>"+
                        "<br>Please note that identifiers should be unique within the file.",
                        {
                            fixed: true,
                            target: true,
                            tipJoint: "bottom left",
                            background: "#ECE9EF",
                            borderColor: "#C7BCD0"
                        });

    $("#batchalign").click(function() {
        if (!$("#filename").val()) {
            return;
        }
        var ctrl = getBusyOverlay("viewport", {color:'#B2B2B2', opacity:0.3, text:'Computing alignments, please wait...', style: 'color: #222222;'}, {color:'#222222', weight:'3', size:100, type:'rectangle', count:12});
        $("#batchfrm").submit();
    });
                        
}