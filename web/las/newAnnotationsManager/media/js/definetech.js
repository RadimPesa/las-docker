$(function() { 
    initCsrf();
    initMisc();
    initTable();
    initHandlers();
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

function initMisc() {
    $("div.modal").append("<span>Loading, please wait...</span>");
    $("div.modal span").css("position", "absolute");
}

function initTable() {

    $("#amplicons").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 5,
        aoColumns: [
            { 
              sClass: "centered"
            },
            { 
              sClass: "centered"
            },
            { 
              sClass: "centered"
            },
            { 
              bSortable: false,
              sClass:  "centered"
            }
        ],
        oLanguage: {
            sEmptyTable: "No target sequence",
        },
        aaSorting: [[0, "asc"]],
    });

}

function selectAmplicon(auuid) {
    var a = amplicons[auuid];
    $("#aname").val(a.pcrp_name);
    $("#aref").val(a.a_ref)
    $("#astart").val(a.r_start);
    $("#aend").val(a.r_end);
    $("#alen").val(a.pcrp_length);
    $("#agene").val(a.a_gene_symbol.join(', '));
    $("body").addClass("loading");
    $("input.tech").prop("checked", false);
    $("#auuid").val(auuid);
    $.ajax({
        url: api_url,
        type: 'GET',
        data: {uuid: auuid},
        success: function(data) {
            console.log(data);
            $("body").removeClass("loading");
            for (var i = 0; i < data.length; ++i) {
                var t = data[i];
                $("#tech_" + t.id).prop("checked", true);
            }
        },
        error: function(res) {
            $("body").removeClass("loading");
            console.log(res);
            alert("An error occurred while trying to connect to server", "Error");
        }
    });
}

function initHandlers() {
    $("form#ainfo").on("submit", function() {
        if ($("#auuid").val().trim() == "")
            return false;
    });
}

