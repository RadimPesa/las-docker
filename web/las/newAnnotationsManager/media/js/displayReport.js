$(function() { 
    initCsrf();
    initControllers();
    initTables();
    initDisplay();
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

function initControllers() {
    $("#sel_hgvs").prop("selectedIndex", 0);

    $("#sel_hgvs").change(function() {
        var v = $("#sel_hgvs").val();
        displayContent(v);
    });

}

function initDisplay() {
    displayContent(0);
}

function initTables() {
    $("#results").DataTable({
        //sort: false,
        scrollX: true,
    });

}

function displayContent(index) {
    // headers (skip first column)
    $($("table#results").DataTable().columns(".site").header()).each(function(i, el) {
        var val = $(el).data("content_" + index);
        $(el).text(val);
    });
    // contents
    $("table#results").DataTable().$("td.data").each(function(i, el) {
        var val = $(el).data("content_" + index);
        $(el).text(val);
    });
    $("table#results").DataTable().draw();
}

