
$(function() { 
    initCsrf();
    initTable();
    initButtons();
    initMisc();
 });

function initMisc() {
    if (redirectToBiobank == true) {
        // hard-coded and ugly!
        $("ul#atech li:contains('In-situ hybridization') input").prop("checked", true);
        $("ul#atech input").prop("disabled", true);
    }
}

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
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" }
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
        var sequence = $('#tssequence').val();
        var profile = $('#profile').val();
        if (!tsname || !sequence) {
            return;
        }
        $("body").addClass("loading");
        $.ajax({
            url: window.location,
            type: 'GET',
            success: function(msg) {
                $("body").removeClass("loading");
                var a = JSON.parse(msg);
                var tb = $("#alignments tbody");
                var data;
                var cb;
                for (var i = 0; i < a.length; ++i) {
                    if (a[i][0] == 'transcript' && a[i][6] == true) {
                        a[i][1] = '<font color="green">' + a[i][1] + '</font>';
                        cb = '<input type="checkbox" name="alignments" value="'+i+'" checked="checked">';
                    } else
                    if (a[i][0] == 'genome') {
                        cb = '<input type="checkbox" name="alignments" value="'+i+'" checked="checked">';
                    } else {
                        cb = '<input type="checkbox" name="alignments" value="'+i+'">'
                    }
                    data = [cb].concat(a[i]);
                    alignDataTable.fnAddData(data);
                }
                //$("#selall").prop("checked", true).trigger("change");
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $("body").removeClass("loading");
                alert(jqXHR.responseText, "Error");
            },
            data: 'tsname='+tsname+'&sequence='+sequence+'&profile='+profile
        });
    });

    $("#save").click(function() {
        var x = alignDataTable.$("input[name='alignments']:checked");
        var y = $("#savefrm input[name='ref'],#savefrm input[name='csrfmiddlewaretoken']");
        //$("ul#atech input").prop("disabled", false);
        var z = $("input.tech:checked");
        if (x.length == 0 || z.length == 0) {
            alert("Please choose at least one alignment and one technology", "Error");
            //$("ul#atech input").prop("disabled", true);
            return;
        }
        $.merge(x,y);
        $.merge(x,z);
        var fd = x.serialize();
        console.log(fd);
        $.ajax({
            url: window.location,
            type: 'POST',
            success: function(msg) {
                msg = JSON.parse(msg);
                if (ref == 'newsp') {
                    msg = JSON.parse(msg);
                    window.opener.$(window.opener.activeEl).val(msg[1]);
                    window.opener.$(window.opener.activeEl).data("seqid", msg[0]);
                    window.opener.$(window.opener.activeEl).change();
                    window.close();
                }
                else if (redirectToBiobank == true) {
                    if (biobankUrl) {
                        location.replace(biobankUrl + '?name=' + msg[1] + '&uuid=' + msg[2]);
                    } else {
                        alert("Warning", "Invalid URL, cannot redirect to Biobank", function() {location.reload();});
                    }
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