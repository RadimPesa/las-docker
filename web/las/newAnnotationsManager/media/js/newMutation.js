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

function initControllers() {
    $("#assembly, #region, #method, #level, #type, #chrom").SumoSelect();

    $("#method").on("change", function() {
        if ($(this).val() == "0") {
            $("#div-hgvs").show();
            $("#div-wizard").hide();
        } else {
            $("#div-hgvs").hide();
            $("#div-wizard").show();
        }
    });
    $("#method").trigger("change");

    // prevent deletion of leading 'c.' or 'g.' in syntax field
    $("#syntax").on('keydown', function() {
        var key = event.keyCode || event.charCode;
        var caretPos = doGetCaretPosition(this);
        // if (backspace or left arrow and cursor right of or within "c.") or (delete and cursor within "c.") or (any key and cursor within "c.")
        if ( ((key == 8 || key == 37) && caretPos <= 2) || (key == 46 && caretPos <=1) || caretPos <= 1)
            return false;
    });

    $("#type").on("change", function() {
        var selType = $(this).val();
        var elems = sa_types_params[selType];
        elems = elems.map(function(e) {return '#par-' + e;}).join(',');
        $(elems).show();
        $("div.par").not(elems).hide();
    });
    $("#type").trigger("change");

    $("#gene").select2({
        width: 'resolve',
        placeholder: 'Start typing a gene symbol...',
        ajax: {
            url: annotations_url + '/newapi/geneInfo/',
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
            return '<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>';
        },
        templateSelection: function(item) {
            if (item.id != "") {
                $("#chrom").val(item.chrom)[0].sumo.reload();
                $("#chrom")[0].sumo.disable();
                return '<b>'+item.symbol + '</b>&nbsp;<span class="small">(' + item.ac + ')</span>';
            }
            else
                return item.text;
        }
    });

    $("#gene").on("change", function() {
        var v = $("#gene").val();
        if (v == null || v == "")
            return;
        $.ajax({
            url: annotations_url + '/newapi/getGeneDefaultTx/',
            dataType: "json",
            type: 'GET',
            data: {uuid: $(this).val()},
            success: function(res) {
                $("#transcript").val(res['ac']);
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            }
        });
    })

    $("#frm-data").on("submit", function(e) {
        var assembly = $("#assembly").val();
        var method = $("#method").val();
        var gene = $("#gene").val() || $("body").data("selectedGene");

        if (method == "0") {
            if (gene == "") {
                alert("Please choose a gene symbol");
                return false;
            }
            var syntax = $("#syntax").val().trim();
            if (syntax == "c.") {
                alert("Please provide the HGVS mutation syntax");
                return false;
            }
            $("#frm-syntax").val(syntax);

        } else

        if (method == "1") {
            var chrom = $("#chrom").val();
            var start = $("#start").val().trim();
            if (start == "") {
                alert("Please provide the mutation start coordinate");
                return false;
            }
            if (!isNumber(start)) {
                alert("The mutation start coordinate must be an integer number");
                return false;
            }
            var type = $("#type").val();
            var elems = sa_types_params[type];
            var params = {};
            var v;
            for (var i = 0; i < elems.length; ++i) {
                v = $("#" + elems[i]).val().trim();
                if (v == "") {
                    alert("Please provide a value for the following parameter: " + sa_params[elems[i]]);
                    return false;
                }
                params[elems[i]] = v;
            }
            $("#frm-type").val(type);
            $("#frm-chrom").val(chrom);
            $("#frm-start").val(start);
            $("#frm-params").val(JSON.stringify(params));
        }

        $("#frm-assembly").val(assembly);
        $("#frm-method").val(method);
        $("#frm-gene").val(gene);
        var xref = $("#xref").val().trim();
        $("#frm-xref").val(xref);

        $("body").addClass("loading");
        var jqXHR = $.post($(this).attr('action'), $(this).serialize(), function(res){
            // Do something with the response `res`
            $("body").removeClass("loading");
            res = $.parseJSON(res);
            console.log(res);

            if (res.exists == true) {
                alert("Mutation already exists!", "Warning")
            }
            else 

            if (res.done == false) {

                if (res.genes.length == 0) {
                    confirm("No genes have been found in the specified genomic region. Do you wish to proceed anyway?", "No genes found", "Yes", "No", saveSequenceAlteration)
                }
                else 

                if (res.genes.length > 1) {
                    for (var i = 0; i < res.genes.length; ++i) {
                        var currGene = res.genes[i];
                        geneDt.row.add(['<input type="radio" name="dgene" value="' + currGene.uuid + '">', currGene.symbol, currGene.hgvsc + " (" + currGene.hgvsp + ")"]);
                    }
                    geneDt.draw();
                    $("#disambiguateGene").dialog("open");
                }

            }
            else
            {
                // check here whether noSave is set
                var noSave = $("#frm-noSave").val();
                var referer = $("#frm-referer").val();
                // if not, proceed normally
                if (noSave != "true") {
                    
                    if (referer == 'exploreKB') {
                        alert(
                            "Mutation saved (uuid = " + res.uuid + ")",
                            "Completed",
                            "Ok",
                            function() {
                                window.close();
                            }
                        );
                        
                    } else {
                        alert("Mutation saved (uuid = " + res.uuid + ")", "Completed", "Ok", function() {location.replace(location.href);});
                    }
                } else {
                // if so, return info to initiator
                    // res.info is returned to initiator in some way
                    alert("Window will now be closed", "Completed", function() {
                        opener.addNewMutation(res.info[0]);
                        window.close();
                    });
                }
            }


            
        }).fail(function(jqXHR) {
            $("body").removeClass("loading");
            alert("The following error has occurred:<br><br>"+jqXHR.responseText, "Error")
        });

        return false;

    });

    $("#frm-data").on("reset", function(e) {
        //$("#method").val(0)[0].sumo.reload();
        //$("#method").change();
        $("#gene").val(null).change();
        $("#transcript").val(null);
        $("#type").val($("#type option").eq(0).val())[0].sumo.reload();
        $("#chrom").val($("#chrom option").eq(0).val())[0].sumo.enable().reload();
        $("#start").val(null);
        $("div.par input").val(null);
        $("#syntax").val($("#syntax").data("initvalue"));
        $("body").removeData("selectedGene");
        $("#frm-ignoreNoGene").val("");
        $("#frm-noSave").val("");
    });

    $("#cleargene").on("click", function() {
        $("#gene").val(null).change();
        $("#transcript").val(null);
        $("#chrom").val($("#chrom option").eq(0).val())[0].sumo.enable().reload();
    });

}

function initDialogs() {
    $("#disambiguateGene").dialog({
        autoOpen: false,
        modal: true,
        width: 550,
        height: 400,
        buttons:
            [
                {
                    text: "Cancel",
                    click: function() {
                        $(this).dialog("close");
                    }
                },
                {
                    text: "Ok",
                    click: function() {
                        var selectedGene = geneDt.$("input:checked");
                        if (selectedGene.length == 0) {
                            alert("Please select a gene from the list", "Error");
                            return;
                        }
                        saveSequenceAlteration(selectedGene.val());
                        $(this).dialog("close");
                    }
                }
            ],
        beforeClose: function() {
            geneDt.rows().remove().draw();
        }
    });
    geneDt = $("table#genes").DataTable({
        ordering: false,
        searching: false,
        info: false,
        paging: false
    });
}

/*
** Returns the caret (cursor) position of the specified text field.
** Return value range is 0-oField.value.length.
*/
function doGetCaretPosition (oField) {

  // Initialize
  var iCaretPos = 0;

  // IE Support
  if (document.selection) {

    // Set focus on the element
    oField.focus ();

    // To get cursor position, get empty selection range
    var oSel = document.selection.createRange ();

    // Move selection start to 0 position
    oSel.moveStart ('character', -oField.value.length);

    // The caret position is selection length
    iCaretPos = oSel.text.length;
  }

  // Firefox support
  else if (oField.selectionStart || oField.selectionStart == '0')
    iCaretPos = oField.selectionStart;

  // Return results
  return (iCaretPos);
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function saveSequenceAlteration(gene_uuid) {
    // if there's a gene_uuid, set that value as the form's gene_uuid
    if (gene_uuid) {
        console.log("Gene set: ", gene_uuid);
        $("body").data("selectedGene", gene_uuid);
    } else {
        $("#frm-ignoreNoGene").val("true");
    }
    
    $("#frm-data").submit();
}
