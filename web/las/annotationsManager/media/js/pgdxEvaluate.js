$(function() { 
    initCsrf();
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

function initButtons() {
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

    $("#submit-batch").click(function() {
        if (!$("#filename").val()) {
            return;
        }
        $("#batchfrm").submit();
    });
}