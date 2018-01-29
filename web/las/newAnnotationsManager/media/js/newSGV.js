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
    $("#addhr").click(function() {
        var hr = $("span.hr.hidden").clone();
        $(hr).children(".chrom, .strand").SumoSelect();
        $("#hr-container").append(hr);
        $(hr).removeClass("hidden");
    });

    $("#assembly, #method, #type, #chrom, #strand").SumoSelect();
    
    $("#allele").SumoSelect({selectAll: true});

    $("#sgv_name-0 select#name").select2({
        width: 'resolve',
        placeholder: 'Start typing an SNP name...',
        ajax: {
            url: snpFromDbSnp_url,
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
            return item.name;
        },
        templateSelection: function(item) {
            if (item.id != "") {
                console.log(item);
                $("#sgv_name-0 input").val(sgv_types[item.type].name);
                refreshAlleles(item.alleles, item.type);
                return item.name;
            }
            else
                return item.text;
        }
    });

    $("#method").on("change", function() {
        if ($(this).val() == "1") {
            $("#div-manual").show();
            $("#sgv_name-0").hide();
            $("#sgv_name-1").show();
            //refreshAlleles();
            $("#type").trigger("change");
        } else {
            $("#div-manual").hide();
            $("#sgv_name-0").show();
            $("#sgv_name-1").hide();
            //refreshAlleles(0);
        }
    });

    $("#method").trigger("change");

    $("#type").on("change", function() {
        var selType = $(this).val();
        var elems = sgv_types_params[selType];
        elems = elems.map(function(e) {return '#par-' + e;}).join(',');
        $(elems).show();
        $("div.par").not(elems).hide();
        if ($("#method").val() != "1") {
            return;
        }
        var h = sgv_types[selType].help;
        hideAllCallouts();
        clearAllCalloutHandlers();
        ensureCallouts(h.length);
        for (var j = 0; j < h.length; ++j) {
            setCalloutText(j, h[j].text);
            setCallout(j, h[j].param);
        }

    });
    $("#type").trigger("change");

    $("#frm-data").on("submit", function(e) {
        var assembly = $("#assembly").val();
        var method = $("#method").val();
        var dbsnp_pk = $("#sgv_name-0 select").val()
        var name = $("#sgv_name-1 input").val();
        var allele = $("#allele").val();

        if (method == "0" && (allele == "" || allele === null)) {
            alert("Please choose an allele");
            return false;
        }

        if (method == "0") {
            if (dbsnp_pk == "") {
                alert("Please type the name of an existing SGV");
                return false;
            }
            $("#frm-dbsnp_pk").val(dbsnp_pk);
        } else

        if (method == "1") {
            if (name == "") {
                alert("Please specify a name");
                return false;
            }
            $("#frm-sgv_name").val(name);
            var chrom = $("#chrom").val();
            var start = $("#start").val().trim();
            if (start == "") {
                alert("Please provide the start coordinate");
                return false;
            }
            if (!isNumber(start)) {
                alert("The start coordinate must be an integer number");
                return false;
            }
            var strand = $("#strand").val();
            var type = $("#type").val();
            var elems = sgv_types_params[type];
            var params = {};
            var v;
            for (var i = 0; i < elems.length; ++i) {
                v = $("#" + elems[i]).val().trim();
                if (v == "") {
                    alert("Please provide a value for the following parameter: " + sgv_params[elems[i]]);
                    return false;
                }
                params[elems[i]] = v;
            }
            $("#frm-strand").val(strand);
            $("#frm-type").val(type);
            $("#frm-chrom").val(chrom);
            $("#frm-start").val(start);
            $("#frm-params").val(JSON.stringify(params));
        }

        var hr = getHomologousRegions();
        $("#frm-hr").val(JSON.stringify(hr));
        $("#frm-assembly").val(assembly);
        $("#frm-method").val(method);
        $("#frm-allele").val(allele);
        var xref = $("#xref").val().trim();
        $("#frm-xref").val(xref);

        $("body").addClass("loading");
        var jqXHR = $.post($(this).attr('action'), $(this).serialize(), function(res){
            // Do something with the response `res`
            $("body").removeClass("loading");
            res = $.parseJSON(res);
            console.log(res);

            if (res.done == false) {
                alert("An error has occurred. Please try again or contact an administrator.")

            }
            else
            {
                var referer = $("#frm-referer").val();

                if (referer == 'exploreKB') {
                    alert(
                        "Variation(s) saved",
                        "Completed",
                        "Ok",
                        function() {
                            window.close();
                        }
                    );
                    
                } else {
                    alert(
                        "Variation(s) saved",
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
        $("#sgv_name-0 select").val(null).change();
        $("#sgv_name-1 input").val(null);
        $("#type").val($("#type option").eq(0).val())[0].sumo.reload();
        $("#chrom").val($("#chrom option").eq(0).val())[0].sumo.enable().reload();
        $("#start").val(null);
        $("#end").val(null);
        $("#strand").val($("#strand option").eq(0).val())[0].sumo.reload();
        $("div.par input").val("");
        $("#xref").val(null);
    });

}

function refreshAlleles(alleles, type) {
    $("#allele option").remove();
    for (var j = 0; j < alleles.length; ++j) {
        var o = $("<option>");
        var a = alleles[j];
        o.val(j);
        o.text(a + " (observed)");
        $("#allele").append(o);
    }
    if (type == 'single') {
        var bases = ['A', 'T', 'C', 'G'];
        for (var i = 0; i < bases.length; ++i) {
            if (alleles.indexOf(bases[i]) == -1) {
                var o = $("<option>");
                o.val('_' + j++ + '_' + bases[i]);
                o.text(bases[i]);
                $("#allele").append(o);
            }
        }
    }
    $("#allele")[0].sumo.reload();
}

function initDialogs() {
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function setCallout(calloutId, fieldElemId) {
    if (calloutId >= numCallouts)
        return;

    var calloutSelector = "#callout-" + calloutId;

    var elem = $("label[for='" + fieldElemId + "']").next();
    var pos = elem.position();
    var width = parseInt(elem.css("width"), 10);
    var calloutHeight = parseInt($(calloutSelector).css("height"), 10);
    var calloutPos = {left: parseInt(pos.left, 10) + width + 10, top: parseInt(pos.top, 10) - 30 - calloutHeight*0.2, position: "absolute"}
    $(calloutSelector).css(calloutPos);
    elem.on("focusin", function() {
        displayCallout(calloutId);
    });
    elem.on("focusout", function() {
        hideCallout(calloutId);
    });
}

function setCalloutText(calloutId, text) {
    if (calloutId >= numCallouts)
        return;

    var calloutSelector = "#callout-" + calloutId;

    $(calloutSelector).text(text);
}

var numCallouts = 1;

function addCallout() {
    var c = $("span#callout-0").clone()
    c.attr("id", "callout-" + numCallouts);
    ++numCallouts;
    $("article#riquadro").append(c);
}

function ensureCallouts(i) {
    if (i > numCallouts) {
        for (; numCallouts < i;) {
            addCallout();
        }
    }
}

function displayCallout(calloutId) {
    if (calloutId >= numCallouts)
        return;

    var calloutSelector = "#callout-" + calloutId;

    $(calloutSelector).show();
}

function hideCallout(calloutId) {
    if (calloutId >= numCallouts)
        return;

    var calloutSelector = "#callout-" + calloutId;

    $(calloutSelector).hide();
}

function hideAllCallouts() {
    $("span.callout").hide();
}

function clearAllCalloutHandlers() {
    $("div.par input").off("focusin");
    $("div.par input").off("focusout");
}

function getHomologousRegions() {
    return $("#hr-container .hr").map(function() {
        var chrom = $(this).find(".chrom").val().trim();
        var start = $(this).find(".start").val().trim();
        var strand = $(this).find(".strand").val().trim();
        if (chrom != "" && start != "" && strand != "") {
            return {chrom: chrom, start: start, strand: strand};
        }
    }).get();
}