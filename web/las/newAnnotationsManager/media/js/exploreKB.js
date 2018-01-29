$(function() { 
    initCsrf();
    initGUI();
    initTables();
    initDialogs();
    checkAnnotUpdateStatus();
    var intervalID = setInterval(checkAnnotUpdateStatus, 120000);
 });

var dt = {};

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

function initGUI() {
    $("#main_tabs").tabs();


    // === CHROM AND COORDINATES ===
    $("#chrom").select2({minimumResultsForSearch: 99, placeholder: 'Chrom'});
    // init change event handler on chrom

    $("#chrom").change(function() {
        if ($("#chrom").val() == null)
            return;
        var d = $(this).find("option:selected").data();
        $("#coord-from").attr("min", d.start);
        $("#coord-from").attr("max", d.end-1);
        $("#coord-to").attr("min", d.start+1);
        $("#coord-to").attr("max", d.end);
        $("#coord-from").val("");
        $("#coord-to").val("");
        $("#coord-from, #coord-to").blur();
        setDropDownMode("auto", dropDownArgs.gene);
        setDropDownMode("auto", dropDownArgs.transcript);
    }).change();

    // init handler to enforce min/max
    $("#coord-from, #coord-to").blur(function() {
        var $this = $(this);
        if ($this.val() == "") {
            return;
        }
        var $other = $("#coord-from, #coord-to").not($this);
        if ($other.val() == "") {
            var min = parseInt($this.attr("min"));
            var max = parseInt($this.attr("max"));
        } else {
            if ($this.attr("id") == "coord-from") {
                var min = parseInt($this.attr("min"));
                var max = parseInt($other.val()) - 1;
            } else {
                var min = parseInt($other.val()) + 1;
                var max = parseInt($this.attr("max"));
            }
        }
        if ($this.val() < min) {
            $this.val(min);
        } else
        if ($this.val() > max) {
            $this.val(max);
        }
    });

    // init handler to clear gene and transcript when coordinates change
    $("#coord-from, #coord-to").change(function() {
        setDropDownMode("auto", dropDownArgs.gene);
        setDropDownMode("auto", dropDownArgs.transcript);
    });

    // init apply region button
    $("#applyregion").click(function() {
        setDropDownMode("filtered", dropDownArgs.gene);
    });

    // init clear region button
    $("#clearregion").click(function() {
        $("#chrom").prop("selectedIndex", -1);
        $("#chrom").change();
        $("#coord-from, #coord-to").val("");
        setDropDownMode("auto", dropDownArgs.gene);
        setDropDownMode("auto", dropDownArgs.transcript);
    }).trigger("click");


    // === GENE ===
    // init gene symbol selector with auto complete (ajax-backed)
    setDropDownMode("auto", dropDownArgs.gene);

    // init handler to clear transcript when gene changes
    $("#gene2").change(function() {
        setDropDownMode("auto", dropDownArgs.transcript);
    })

    // init apply gene button
    $("#applygene").click(function() {
        setDropDownMode("filtered", dropDownArgs.transcript);
    });

    // init clear gene button
    $("#cleargene").click(function() {
        clearOptions(dropDownArgs.gene.sSelector);
        setDropDownMode("auto", dropDownArgs.transcript);
    }).trigger("click");
    

    // === TRANSCRIPT ===
    // init transcript accession selector with auto complete (ajax-backed)
    setDropDownMode("auto", dropDownArgs.transcript);


    // === PERFORM SEARCH ===
    // init go button handler
    $("#search").click(function() {
        displaySpinner("Searching...");

        var chrom = $("#chrom").val();
        var start = $("#coord-from").val();
        var end = $("#coord-to").val();
        var gene_uuid = $("#gene2").val();
        var tx_uuid = $("#transcript").val();
        var annot_type = $(".select-type").map(function() {if ($(this).prop("checked")) return $(this).attr("annot-type")}).get();

        if (annot_type.length == 0) {
            hideSpinner();
            return;
        }

        // clear data tables
        for (var t in dt) {
            dt[t].DataTable().clear().draw();      
        }
        // send a query for every annotation type
        var done = 0;
        var num_reqs = annot_type.length;
        for (var i = 0; i < num_reqs; ++i) {
            (function (j) {
                //console.log("Sending request: ", annot_type[j]);
                $.ajax({
                    url: searchReferences_url,
                    data: {chrom: chrom, start: start, end: end, gene_uuid: gene_uuid, tx_uuid: tx_uuid, annot_type: annot_type[j]},
                    success: function(data, textStatus, jqXHR) {
                        //console.log(data);
                        done++;
                        for (var z = 0; z < data.length; ++z) {
                            dt[annot_type[j]].DataTable().row.add(data[z]);
                        }
                        dt[annot_type[j]].DataTable().draw();
                        if (done == num_reqs) {
                            hideSpinner();
                            var id = dt[annot_type[0]].parent().parent().attr("id");
                            $("a[href='#" + id + "']").click();
                        }
                    }
                });
            }) (i);
        }
    });

    // === DELETE ENTRIES ===
    $("button.delete").click(function() {
        var type = $(this).parents("div").data().type;
        var uuid_list = getElementsToDelete(type);
        if (uuid_list.length == 0) return;
        confirm(
            "Do you really wish to delete the selected items?",
            "Confirm",
            "Yes",
            "No",
            function() {
                displaySpinner("Deleting reference(s) and annotations...");
                $.ajax({
                    type: "POST",
                    url: deleteReferences_url,
                    data: {uuid_list: JSON.stringify(uuid_list)},
                    success: function() {
                        hideSpinner();
                        $("#search").click();
                    },
                    error: function(jqXHR, text, errorThrown) {
                        hideSpinner();
                        $("#search").click();
                        window.confirm(
                            "One or more errors occurred while trying to delete the specified object(s)",
                            "Error",
                            "OK",
                            "Show details",
                            function() {},
                            function() {
                                var table = $("#afterdeletedialog table[data-type='" + type + "']");
                                var div = table.parents("div.table-container");
                                div.show();
                                for (var z = 0; z < jqXHR.responseJSON.length; ++z) {
                                    table.DataTable().row.add(jqXHR.responseJSON[z]);
                                }
                                table.DataTable().draw();
                                $("#afterdeletedialog").dialog("open");
                            }
                        );
                    }
                });
            }
        );
    });

    // === INSERT NEW ENTRIES
    $("button.insert").click(function() {
        var type = $(this).parents("div").data().type;
        var url = insertNew_url[type];
        console.log(url);
        var w = screen.width-100;
        var h = screen.height-400;
        var left = 10;//(screen.width/2)-(w/2);
        var top = 10;//(screen.height/2)-(h/2);
        neww = window.open(url,
                            "_blank",
                            'toolbar="no", location="no", status="no",'+
                            'menubar="no", scrollbars="no", resizable="no", '+
                            'width='+w+', height='+h+', top='+top+', left='+left
                        );

        neww.onbeforeunload = afterCloseChild;

        if (window.focus) {
            neww.focus();
        }
    });

    $("button#updateAnnotations").click(function() {
        displaySpinner("Starting annotation process...");
        $.ajax({
            type: "POST",
            url: updateAnnotations_url,
            data: {type: 'part'},
            success: function() {
                hideSpinner();
                alert("Process started succesfully.", "Update", "Ok", function() { checkAnnotUpdateStatus(); });
            },
            error: function(jqXHR, text, errorThrown) {
                hideSpinner();
                alert(text);
            }
        });
    });

    $("button#rescanAnnotations").click(function() {
        confirm(
            "This operation may require a long time to complete (up to a few hours). Please note that no other update operation may be run until completion.<br><br>Do you wish to proceed?",
            "Full annotation rescan",
            "Yes",
            "No",
            function() {
                console.log("starting rescan");
                displaySpinner("Starting annotation process...");
                $.ajax({
                    type: "POST",
                    url: updateAnnotations_url,
                    data: {type: 'full'},
                    success: function() {
                        hideSpinner();
                        alert("Process started succesfully.", "Full annotation rescan", "Ok", function() { checkAnnotUpdateStatus(); });
                    },
                    error: function(jqXHR, text, errorThrown) {
                        hideSpinner();
                        alert(text);
                    }
                });
            },
            function() {
                console.log("rescan cancelled");
            }
        );

    });
}

function initDialogs() {
    $("#afterdeletedialog").dialog(
        {
            autoOpen: false,
            modal: true,
            width: 850,
            position: { my: "center bottom"},
            resizable: false,
            minHeight: 250,
            beforeClose: function() {
                $("#afterdeletedialog div.table-container").hide();
                $("#afterdeletedialog table").DataTable().clear().draw();
            },
            buttons:
            [
                {
                    text: "Ok",
                    click: function() {
                        $(this).dialog("close");                                                                          
                    }
                }
            ]
        }
    );
    $("#afterdeletedialog").css('max-height', '600px'); // set thru CSS because maxHeight property of dialog does not work
    $("#del-seqalts").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                data: "uuid",
                bVisible: false
            },
            {
                sTitle: "Gene symbol",
                sClass: "centered",
                data: "gene_symbol"
            },
            {
                sTitle: "Transcript ac",
                sClass: "centered",
                data: "tx_ac"
            },
            {
                sTitle: "HGVSg",
                sClass: "centered",
                data: "hgvs_g"
            },
            {
                sTitle: "HGVSc",
                sClass: "centered",
                data: "hgvs_c"
            },
            {
                sTitle: "HGVSp",
                sClass: "centered",
                data: "hgvs_p"
            },
            {
                sTitle: "External ID",
                sClass: "centered",
                data: "x_ref"
            },
            {
                sTitle: "Error",
                sClass: "centered",
                data: "error"
            }
        ],
        oLanguage: {
            sEmptyTable: "No data"
        },
        aaSorting: [[0, "asc"]]
    });

    $("#del-sgvs").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                data: "uuid",
                bVisible: false
            },
            {
                sTitle: "Name",
                sClass: "centered",
                data: "name"
            },
            {
                sTitle: "Gene symbol",
                sClass: "centered",
                data: "gene_symbol"
            },
            {
                sTitle: "Chrom",
                sClass: "centered",
                data: "chrom"
            },
            {
                sTitle: "Start",
                sClass: "centered",
                data: "start"
            },
            {
                sTitle: "End",
                sClass: "centered",
                data: "end"
            },

            {
                sTitle: "Alt",
                sClass: "G",
                data: "alt"
            },
            {
                sTitle: "Type",
                sClass: "centered",
                data: "type"
            },
            {
                sTitle: "Error",
                sClass: "centered",
                data: "error"
            }
        ],
        oLanguage: {
            sEmptyTable: "No data"
        },
        aaSorting: [[0, "asc"]]
    });

    $("#del-gcns").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                data: "uuid",
                bVisible: false
            },
            {
                sTitle: "Chrom",
                sClass: "centered",
                data: "ref"
            },
            {
                sTitle: "Gene symbol",
                sClass: "centered",
                data: "geneSymbol"
            },
            {
                sTitle: "Type",
                sClass: "centered",
                data: "type"
            },
            {
                sTitle: "Error",
                sClass: "centered",
                data: "error"
            }
        ],
         oLanguage: {
            sEmptyTable: "No data"
        },
        aaSorting: [[0, "asc"]]
    });
}

function initTables() {
    dt['sequence_alteration'] = $("#seqalts").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                data: "uuid",
                bVisible: false
            },
            {
                sTitle: "Gene symbol",
                sClass: "centered",
                data: "gene_symbol"
            },
            {
                sTitle: "Transcript ac",
                sClass: "centered",
                data: "tx_ac"
            },
            {
                sTitle: "HGVSg",
                sClass: "centered",
                data: "hgvs_g"
            },
            {
                sTitle: "HGVSc",
                sClass: "centered",
                data: "hgvs_c"
            },
            {
                sTitle: "HGVSp",
                sClass: "centered",
                data: "hgvs_p"
            },
            {
                sTitle: "External ID",
                sClass: "centered",
                data: "x_ref"
            },
            {
                sTitle: "Delete",
                sClass: "centered",
                sDefaultContent: "<input type='checkbox' class='toDelete' />"//'<span class="btn-cancel ui-icon ui-icon-closethick" style="cursor: pointer"></span>'
            }
        ],
        oLanguage: {
            sEmptyTable: "No data"
        },
        aaSorting: [[0, "asc"]]
    });

    dt['short_genetic_variation'] = $("#sgvs").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                data: "uuid",
                bVisible: false
            },
            {
                sTitle: "Name",
                sClass: "centered",
                data: "name"
            },
            {
                sTitle: "Gene symbol",
                sClass: "centered",
                data: "gene_symbol"
            },
            {
                sTitle: "Chrom",
                sClass: "centered",
                data: "chrom"
            },
            {
                sTitle: "Start",
                sClass: "centered",
                data: "start"
            },
            {
                sTitle: "End",
                sClass: "centered",
                data: "end"
            },

            {
                sTitle: "Alt",
                sClass: "G",
                data: "alt"
            },
            {
                sTitle: "Type",
                sClass: "centered",
                data: "type"
            },
            {
                sTitle: "Delete",
                sClass: "centered",
                sDefaultContent: "<input type='checkbox' class='toDelete' />"//'<span class="btn-cancel ui-icon ui-icon-closethick" style="cursor: pointer"></span>'
            }
        ],
        oLanguage: {
            sEmptyTable: "No data"
        },
        aaSorting: [[0, "asc"]]
    });

    dt['copy_number_variation'] = $("#gcns").dataTable({
        bFilter: true,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                data: "uuid",
                bVisible: false
            },
            {
                sTitle: "Chrom",
                sClass: "centered",
                data: "ref"
            },
            {
                sTitle: "Gene symbol",
                sClass: "centered",
                data: "geneSymbol"
            },
            {
                sTitle: "Type",
                sClass: "centered",
                data: "type"
            },
            {
                sTitle: "Delete",
                sClass: "centered",
                sDefaultContent: "<input type='checkbox' class='toDelete' />"//'<span class="btn-cancel ui-icon ui-icon-closethick" style="cursor: pointer"></span>'
            }
        ],
         oLanguage: {
            sEmptyTable: "No data"
        },
        aaSorting: [[0, "asc"]]
    });

    /*$("div#main_tabs").on("click", "span.btn-cancel",
            function () {
                var tr = $(this).parents('tr');
                var table = $(this).parents('table');
                var data = table.DataTable().row(tr).data();
                console.log("Delete", data.uuid);
                var i = toDelete.indexOf(data.uuid);
                if (i == -1) {
                    toDelete.push(data.uuid);
                    $(this).addClass("red");
                } else {
                    delete toDelete[i];
                    $(this).removeClass("red");
                }
            }
    );*/

    /*$("#sgvs").on("click", "span.btn-cancel",
        function () {
            var tr = $(this).parents('tr');
            var data = $("#sgvs").DataTable().row(tr).data();
            console.log("Delete", data.uuid);
        }
    );

    $("#gcns").on("click", "span.btn-cancel",
        function () {
            var tr = $(this).parents('tr');
            var data = $("#gcns").DataTable().row(tr).data();
            console.log("Delete", data.uuid);
        }
    );*/
}

function getElementsToDelete(type) {
    var toDelete = []
    var table = dt[type];
    table.DataTable()
        .$("input.toDelete:checked")
        .map(function() {
            var tr = table.DataTable().$(this).parents('tr');
            var data = table.DataTable().row(tr).data();
            //console.log(data);
            return data.uuid;
        })
        .each(function(i, e) {
            toDelete.push(e);
        });
    return toDelete;
}

function clearOptions(selector) {
    var sel = selector.split(',').map(function(x) {return x.trim();});
    for (var i = 0; i < sel.length; ++i) {
        $(sel[i] + " option").remove();
        $(sel[i]).val(null).change();
    }
}

function setDropDownMode(sMode, oArgs) {
    clearOptions(oArgs.sSelector);
    if (sMode == "auto") {
        $(oArgs.sSelector).select2({
            width: '250',
            placeholder: oArgs.sPlaceHolder,
            ajax: {
                url: oArgs.sApiUrl,
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
            templateResult: oArgs.fTemplateResult,
            templateSelection: oArgs.fTemplateSelection
        });
    } else
    if (sMode == "filtered") {
        var params = oArgs.fFilterParams();
        clearOptions(oArgs.sSelector);

        $.ajax({
            url: oArgs.sFilterApiUrl,
            dataType: "json",
            type: 'GET',
            data: params,
            success: function(res) {
                $(oArgs.sSelector).select2({
                    width: '250',
                    placeholder: oArgs.sPlaceHolder,
                    data: oArgs.fPostProcessFilteredData(res),
                    allowClear: true,
                    templateResult: oArgs.fTemplateResult,
                    templateSelection: oArgs.fTemplateSelection
                })
                    .val(null)
                    .change()
                    .select2("open");
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            }
        });
    }
}

// sSelector, sPlaceHolder, sApiUrl, fTemplateResult, fTemplateSelection, fFilterParams, sFilterApiUrl, fPostProcessFilteredData
var dropDownArgs = {
    gene: {
        sSelector: "#gene2",
        sPlaceHolder: "Gene symbol",
        sApiUrl: geneInfo_url,
        fTemplateResult: function(item) {
            if (item.loading) return item.text;
            return '<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>';
        },
        fTemplateSelection: function(item) {
            if (item.id != "")
                return '<b>'+item.symbol + '</b>&nbsp;<span class="small">(' + item.ac + ')</span>';
            else
                return item.text;
        },
        fFilterParams: function() {
            var chrom = $("#chrom").val();
            var coord_from = $("#coord-from").val();
            var coord_to = $("#coord-to").val();
            if (chrom == null) {
                return;
            }
            if (coord_from == "") {
                coord_from = $("#coord-from").attr("min")
                $("#coord-from").val(coord_from);
            }
            if (coord_to == "") {
                coord_to = $("#coord-to").attr("max")
                $("#coord-to").val(coord_to);
            }
            return {chrom: $("#chrom").val(), start: $("#coord-from").val(), end: $("#coord-to").val()};
        },
        sFilterApiUrl: genesInRegion_url,
        fPostProcessFilteredData: function(res) {
            for (var j = 0; j < res.length; ++j) {
                res[j].text = res[j].symbol + ' ' + res[j].ac;
            }
            return res;
        }
    },
    transcript: {
        sSelector: "#transcript",
        sPlaceHolder: "Transcript accession",
        sApiUrl: transcriptInfo_url,
        fTemplateResult: function(item) {
            if (item.loading) return item.text;
            return '<b>'+item.ac+'</b>';  
        },
        fTemplateSelection: function(item) {
            if (item.id != "")
                return '<b>' + item.ac + '</b>';
            else
                return item.text;
        },
        fFilterParams: function() {
            var gene_uuid = $("#gene2").val();
            if (gene_uuid == null)
                return;
            return {gene_uuid: gene_uuid};
        },
        sFilterApiUrl: transcriptsForGene_url,
        fPostProcessFilteredData: function(res) {
            for (var j = 0; j < res.length; ++j) {
                res[j].text = res[j].symbol + ' ' + res[j].ac;
            }
            return res;
        }
    }
};

function displaySpinner(text) {
    $("body").addClass("loading");
    $("div.modal").append("<span style='font-size: 18px'>" + text + "</span>");
    $("div.modal span").css("position", "absolute");
    $(window).resize(function() {
        $("div.modal span").css("top", parseInt($("div.modal").css("height"))/2+80)
        $("div.modal span").css("left", (parseInt($("div.modal").css("width"))-parseInt($("div.modal span").css("width")))/2)
    });
    $(window).resize();
    $("body").addClass("loading");
}

function hideSpinner() {
    $("body").removeClass("loading");
    $("div.modal").children().remove();
    $(window).off("resize");
}

var pendingRefs_info = {
    checking: {btn_disabled: true, btn1_disabled: true, class: 'wait', msg: 'Checking for new references...'},
    ok: {btn_disabled: true, btn1_disabled: false, class: 'ok', msg: 'Annotations and knowledge base are synchronized.'},
    running: {btn_disabled: true, btn1_disabled: true, class: 'ok', msg: 'An update is currently running.'},
    pending: {btn_disabled: false, btn1_disabled: false, class: 'warn', msg: 'There are new knowledge base entries. Annotations need to be updated.'},
    error: {btn_disabled: true, btn1_disabled: true, class: 'error', msg: 'An error has occurred while checking for new references.'},
    runningFull: {btn_disabled: true, btn1_disabled: true, class: 'ok', msg: 'A full rescan is currently running.'},
};

function checkAnnotUpdateStatus() {
    console.log("Checking pending references");
    $("#pending").removeClass().addClass(pendingRefs_info.checking.class);
    $("#pending button").prop("disabled", pendingRefs_info.checking.btn_disabled);
    $.ajax({
        url: checkAnnotUpdateStatus_url,
        success: function(data, textStatus, jqXHR) {
            var status = data.runningFull ? 'runningFull' : (data.runningPartial ? 'running': (data.pendingRefs ? 'pending' : 'ok'));
            $("#pending").removeClass().addClass(pendingRefs_info[status].class);
            $("#pending span.msg").text(pendingRefs_info[status].msg);
            $("#pending button").prop("disabled", pendingRefs_info[status].btn_disabled);
            $("button#rescanAnnotations").prop("disabled", pendingRefs_info[status].btn1_disabled);
        },
        error: function(jqXHR, text, errorThrown) {
            $("#pending").removeClass().addClass(pendingRefs_info.error.class);
            $("#pending button").prop("disabled", pendingRefs_info.error.btn_disabled);
            $("button#rescanAnnotations").prop("disabled", pendingRefs_info.error.btn1_disabled);
        }
    });
}

function afterCloseChild() {
    console.log("running afterCloseChild...");
    $("#search").click();
    checkAnnotUpdateStatus();
}