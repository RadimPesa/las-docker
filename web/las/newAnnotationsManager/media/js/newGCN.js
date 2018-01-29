$(function() { 
    initCsrf();
    initControllers();
    initDialogs();
});

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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
function initCsrf() {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

var max_num_alleles = 8;
var alleles = [];
var A_code = "A".charCodeAt(0);
for (var j = A_code; j < A_code + max_num_alleles; ++j) {
    alleles.push(String.fromCharCode(j));
}

function initControllers() {
    $("#assembly, #method, #type, #class, #chrom").SumoSelect();

    $("#gene").select2({
        width: 'resolve',
        placeholder: 'Start typing a gene symbol...',
        ajax: {
            url: geneInfo_url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term // search term
                };
            },
            processResults: function (data, page) {
                // parse the results into the format expected by Select2.
            // since we are using custom formatting functions we do not need to
            // alter the remote JSON data
                return {results: data};
            },
            cache: false
        },
        minimumInputLength: 1,
        templateResult: function(item) {
            if (item.loading) return item.text;
            return item.symbol;
        },
        templateSelection: function(item) {
            if (item.id != "") {
                return item.symbol;
            }
            else
                return item.text;
        }
    });

    $("#method").on("change", function() {
        var method = $(this).val();
        if (method == undefined || method == null)
            return;
        var otherMethod = $(this).children("option").not(":selected").attr("value");
        $("#method-" + method).show();
        $("#method-" + otherMethod).hide();
    });

    $("#method").trigger("change");

    $("#frm-data").on("submit", function(e) {
        var assembly = $("#assembly").val();
        var method = $("#method").val();
        var gene = $("#gene").val()
        var cnv_class = $("#class").val();
        var xref = $("#xref").val();
        var chrom = $("#chrom").val();
        var start = $("#start").val();
        var end = $("#end").val();

        if (method == 0 && (gene == "" || gene == null || gene == undefined)) {
            alert("Please choose a gene");
            return false;
        }
        else

        if (method == 1) {
            if (start == "" || start == null || start == undefined || end == "" || end == null || end == undefined) {
                alert("Please provide start and end coordinates");
                return false;
            }
            start = parseInt(start);
            end = parseInt(end);
            if (start >= end) {
                alert("Start coordinate must be less than the end coordinate");
                return false;
            }
        }

        $("#frm-assembly").val(assembly);
        $("#frm-method").val(method);
        $("#frm-gene").val(gene);
        $("#frm-class").val(cnv_class);
        $("#frm-chrom").val(chrom);
        $("#frm-start").val(start);
        $("#frm-end").val(end);
        var xref = $("#xref").val().trim();
        $("#frm-xref").val(xref);

        $("body").addClass("loading");

        var jqXHR = $.post($(this).attr('action'), $(this).serialize(), function(res){
            // Do something with the response `res`
            $("body").removeClass("loading");
            res = $.parseJSON(res);
            console.log(res);

            if (res.exists == true) {
                alert("Variation already exists!", "Warning")
            }
            else 

            if (res.done == false) {
                alert("An error has occurred. Please try again or contact an administrator.")

            }
            else
            {
                var referer = $("#frm-referer").val();

                if (referer == 'exploreKB') {
                    alert(
                        "Variation saved (uuid = " + res.uuid + ")",
                        "Completed",
                        "Ok",
                        function() {
                            window.close();
                        }
                    );
                    
                } else {
                    alert(
                        "Variation saved (uuid = " + res.uuid + ")",
                        "Completed",
                        "Ok", 
                        function() {
                            location.replace(location.href);
                        }
                    );
                }
            }
        }).fail(function(jqXHR) {
            $("body").removeClass("loading");
            alert("The following error has occurred:<br><br>"+jqXHR.responseText, "Error")
        });

        return false;

    });

    $("#frm-data").on("reset", function(e) {
        $("#assembly").val(0)[0].sumo.reload();
        //$("#method").val(0)[0].sumo.reload();
        //$("#method").change();
        $("#gene").val(null).change();
        $("#class").val($("#class option").eq(0).val())[0].sumo.reload();
        $("#chrom").val($("#chrom option").eq(0).val())[0].sumo.enable().reload();
        $("#start").val(null);
        $("#end").val(null);
        $("#xref").val(null);
    });

}

function initDialogs() {
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}