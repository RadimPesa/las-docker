$(function() { 
    initCsrf();
    initGenid();
    initGUI();
    initHandlers();
 });

var plate_cnt = 0;
var plates = [];
var date_cnt = 0;
var dates = [];
var samples = []
var snp_cnt = 0;
var snps = [];
var genid = {
    'tumorType': {
        name: 'tumor type',
        start: 0,
        end: 2,
        values: ["BLC", "BRC", "CHC", "CRC", "CUP", "EPC", "GTR", "HCC", "HNC", "KDC", "LNF", "LNG", "MEL", "NCT", "NEC", "OVR", "PRC", "THC"]
    },
    'tissue': {
        name: 'tissue',
        start: 7,
        end: 8,
        values: ["AM", "BL", "BM", "CM", "LM", "LY", "MB", "MP", "NB", "NC", "ND", "NL", "NM", "NN", "NP", "PM", "PR", "SM", "TH", "TM", "TR", "UR"]
    },
    'vector': {
        name: 'vector',
        start: 9,
        end: 9,
        values: ["A", "H", "S", "X"],
    },
    'tissueType': {
        name: 'tissue type',
        start: 17,
        end: 19,
        values: ["BLD", "GUT", "LIV", "LNG", "MBR", "MLI", "MLN", "TUM"]
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

function initGenid() {
    for (var t in genid) {
        $("#selgenidtype").append('<option>'+ t +'</option>');
    }
    $("#selgenidtype").change(function() {
        var t = $(this).val();
        try {
            var fields = genid[t].fields;
        }
        catch(err) {
            return;
        }
        $("table#genid th.field,table#genid td.field").remove();
        for (var j = 0; j < fields.length; ++j) {
            $('<th class="field">' + fields[j].name + '</th>').insertBefore("table#genid th.add");
            if (fields[j].ftype == 1) {
                var x = '<td class="field"><select class="genidpar" maxlength="' + (fields[j].end - fields[j].start + 1)+'">';
                x += '<option></option>';
                for (var k = 0; k < fields[j].values.length; ++k) {
                    x += '<option>' + fields[j].values[k] + '</option>';
                }
                x += '</select></td>';
            } else
            if (fields[j].ftype == 2 || fields[j].ftype == 3 || fields[j].ftype == 4) {
                var x = '<td class="field"><input type="text" class="genidpar" maxlength="' + (fields[j].end - fields[j].start + 1)+ '" onkeypress="validate3(event)"></td>';
            }
            $(x).insertBefore("table#genid td.add");
        }
    });
    $("#selgenidtype").prop("selectedIndex", 2).change();

    $("#genidfile").change(function() {
        var r = new FileReader();
        r.onload = function(evt) {
            $("#fullgenid").val(evt.target.result);
            $("#add_gid2").click();
            $("#filefrm3")[0].reset();
        }
        r.readAsText($("#genidfile")[0].files[0]);
    });
}

function initGUI() {
    $("#main_tabs").tabs();
    $("div.modal").append("<span>Generating, please wait...</span>");
    $("div.modal span").css("position", "absolute");
    $(window).resize(function() {
        $("div.modal span").css("top", parseInt($("div.modal").css("height"))/2+60)
        $("div.modal span").css("left", (parseInt($("div.modal").css("width"))-parseInt($("div.modal span").css("width")))/2)
    });
    $(window).resize();
    $(window).focus(function() {
        $("body").removeClass("loading");
        $("div.modal").children().remove();
        $(window).off("resize");
    });

    // initialize plate tab
    $("#plateid").autocomplete({
        source: plate_autocomplete_api_url
    });

    $("#addplate").on("click", function() {
        var plateid = $("#plateid").val().trim();
        if (plateid == "")
            return;
        $.ajax({
            url: plate_autocomplete_api_url,
            data: {
                term: plateid
            },
            success: function(data, textStatus, jqXHR) {
                if (data.length > 0) {
                    var exists = plates.filter(function(el) {return el == plateid}).length !== 0;
                    if (exists)
                        return;
                    plates.push(plateid);
                    console.log("ok");
                    var text_data = {'plate_id': plateid};
                    var row = plateDt.row.add(text_data).node();
                    $(row).data("id", plate_cnt++);
                    plateDt.draw();
                    $("#plateid").val("");
                } else {
                    console.log("invalid plate");
                    alert("Invalid plate number", "Error");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert("Cannot validate data", "Error");
            }
        });
    });

    plateDt = $("#platesummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'plate_id'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        searching: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    plateDt.on( 'draw.dt', function () {
        plateDt.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();

    plateDt.on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = r.data("id");
        plateDt.row(r)
                .remove()
                .draw();
        delete plates[id];
    });
    
    // initialize date tab
    $("div#date").children('input').datepicker({
        defaultDate: "w",
        changeMonth: true,
        dateFormat: "yy-mm-dd",
        numberOfMonths: 1,
        showAnim: "",
        onSelect: function( selectedDate ) {
            var option = $(this).hasClass("rangeFrom") ? "minDate" : "maxDate";
            var instance = $( this ).data( "datepicker" );
            var date = $.datepicker.parseDate(
                instance.settings.dateFormat || $.datepicker._defaults.dateFormat,
                selectedDate,
                instance.settings
            );
            $(this).siblings("input").datepicker("option", option, date);
        }
    });
    $("div#date").children('select.rangeFrom').change(function() {
        if ($(this).val()=="<" || $(this).val()=="=") {
            $(this).siblings('input.rangeTo').val("");
            $(this).siblings('.rangeTo').attr('disabled', true);
            $(this).siblings("input.rangeFrom").datepicker("option", "maxDate", "");
        } else {
            $(this).siblings('.rangeTo').removeAttr('disabled');
        } 
    });

    dateDt = $("#datesummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'date1'},
            {data: 'date2'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        searching: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    dateDt.on( 'draw.dt', function () {
        dateDt.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();

    dateDt.on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = r.data("id");
        dateDt.row(r)
                .remove()
                .draw();
        delete dates[id];
    });

    $("#adddate").on("click", function() {
        var op1 = $("#op1 option:selected");
        var op2 = $("#op2 option:selected");
        var op2disabled = $("#op2").attr("disabled") != undefined;
        var date1 = $("#date1").val().trim();
        var date2 = op2disabled ? "" : $("#date2").val().trim();
        if (date1 == "")
            return;
        var exists = dates.filter(function(el) {return el.date1 == op1.val() + date1 && el.date2 == (op2disabled ? "" : op2.val() + date2)}).length !== 0;
        if (exists)
            return;
        dates.push({date1: op1.val() + date1, date2: date2 == "" ? "" : op2.val() + date2});
        var text_data = {date1: op1.text().trim() + " " + date1, date2: date2 == "" ? "" : op2.text().trim() + " " + date2};
        var row = dateDt.row.add(text_data).node();
        $(row).data("id", date_cnt++);
        dateDt.draw();
        $("div#date input").val("");
    });

    // initialize sample tab
    samplesDt = $("#samplesummary").DataTable({
        columns: [
            {searchable: false, orderable: false, defaultContent: ''},
            {data: 'genid', className: 'center'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    samplesDt.on("click", "span.action.delete", function () {
        console.log("delete genid");
        var r = $(this).parents("tr");
        var genid = samplesDt.row(r).data().genid;
        samplesDt.row(r).remove().draw();
        delete samples[genid];
    });

    samplesDt.on( 'draw.dt', function () {
        samplesDt.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();

    // init genid fields
    $("select.genid").each(function() {
        var id = $(this).attr("id");
        $(this).select2({
            width: 'resolve',
            placeholder: 'Select ' + genid[id].name,
            data: genid[id].values.map(function(e) {return {id: e, text: e}}),
            allowClear: true
        });
    });
  
    // init add samples button
    $("#addsamples").click(function() {
        if (!$("select.genid").get().reduce(function(prev,curr) {return prev || (curr != "" && curr != null)}, false))
            return;
        var values = $("select.genid").get().reduce(function(prev,curr) {prev[$(curr).attr("id")] = $(curr).val(); return prev;}, {});
        var g = new Array(26);
        for (var i = 0; i < g.length; ++i)
            g[i] = '-';
        for (var k in values) {
            if (values[k] != "" && values[k] != null) {
                var v = values[k];
                var j = 0;
                for (var i = genid[k].start; i <= genid[k].end; ++i) {
                    g[i] = v[j++];
                }
            }
        }
        g = g.join('');
        console.log(g);
    });

    // init add gid button
    $("#add_gid").click(function() {
        var g = genIdFromForm();
        if (validateGenid(g[0])) {
            addGenId(g);
        }
    })

    // init add gid 2 button
    $("#add_gid2").click(function() {
        var val = $("#fullgenid").val();
        if (val.trim() == "")
            return;
        var list = val.split(/\s+/g).map(normalizeGenid);
        var listOk = [];
        var listNotOk = [];
        for (var i = 0; i < list.length; ++i) {
            if (list[i] == "")
                continue;
            if (validateGenid(list[i])) {
                listOk.push(list[i]);
            } else {
                listNotOk.push(list[i]);
            }
        }
        addGenId(listOk);
        if (listNotOk.length > 0) {
            $("#fullgenid").val(listNotOk.join('\n'));
            alert("Invalid values were found and left in the text box. Please check them and retry.")
        } else {
            $("#fullgenid").val('');
        }
    });

    // init clear gid2 button
    $("#clear_gid2").click(function() {
        $("#fullgenid").val("");
    });

    // initialize snp tab
    $("#snpid").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: snp_autocomplete_api_url,
                data: {
                    q: request.term
                },
                success: function(data, textStatus, jqXHR) {
                    var data1 =[];
                    for (var j = 0; j < data.length; ++j) {
                        if (data1.indexOf(data[j].name) == -1) {
                            data1.push(data[j].name);
                        }
                    }
                    response(data1);
                }
            });
        }
    });

    $("#addsnp").on("click", function() {
        var snpid = $("#snpid").val().trim();
        if (snpid == "")
            return;
        $.ajax({
            url: snp_autocomplete_api_url,
            data: {
                q: snpid
            },
            success: function(data, textStatus, jqXHR) {
                if (data.length > 0) {
                    var exists = snps.filter(function(el) {return el == snpid}).length !== 0;
                    if (exists)
                        return;
                    snps.push(snpid);
                    console.log("ok");
                    var text_data = {'snp_id': snpid};
                    var row = snpDt.row.add(text_data).node();
                    $(row).data("id", snp_cnt++);
                    snpDt.draw();
                    $("#snpid").val("");
                } else {
                    console.log("invalid SNP");
                    alert("Invalid SNP", "Error");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert("Cannot validate data", "Error");
            }
        });
    });

    snpDt = $("#snpsummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'snp_id'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        searching: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    snpDt.on( 'draw.dt', function () {
        snpDt.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();

    snpDt.on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = r.data("id");
        snpDt.row(r)
                .remove()
                .draw();
        delete snps[id];
    });

    $(".clearall").click(function() {
        $(this).parent().parent().parent().find("table").DataTable().$("span.action.delete").click();
    });
    



}

function initHandlers() {
    $("form#report").on("submit", function(event) {
        $("body").addClass("loading");
        var list_plates = plates.filter(function(el) { return el !== undefined; });
        var list_dates = dates.filter(function(el) { return el !== undefined; });
        var list_samples = Object.keys(samples)
        var list_snps = snps.filter(function(el) { return el !== undefined; });

        $("div.modal").append("<span>Generating report, please wait...</span>");
        $("div.modal span").css("position", "absolute");
        $(window).resize(function() {
            $("div.modal span").css("top", parseInt($("div.modal").css("height"))/2+60)
            $("div.modal span").css("left", (parseInt($("div.modal").css("width"))-parseInt($("div.modal span").css("width")))/2)
        });
        $(window).resize();
        $("body").addClass("loading");
        $(window).focus(function() {
            $("body").removeClass("loading");
            $("div.modal").children().remove();
            $(window).off("resize");
        });

        $("#frm_plates").val(JSON.stringify(list_plates));
        $("#frm_dates").val(JSON.stringify(list_dates));
        $("#frm_samples").val(JSON.stringify(list_samples));
        $("#frm_snps").val(JSON.stringify(list_snps));

        return true;
    });
}

function genIdFromForm() {
    
    var genid = $(".genidpar").map(function() {
        var v=$(this).val().toUpperCase();
        if (v) {
            var l = parseInt($(this).attr("maxlength")) - v.length;
            if (l > 0) {
                v = new Array(l+1).join("0") + v;
            }
            return v;
        } else {
            //console.log (this, $(this).attr("maxlength"))
            return new Array(parseInt($(this).attr("maxlength"))+1).join("-")
        }
    }).get();

    genid = genid.join("");
    var l = 26 - genid.length;
    if (l > 0) {
        genid += new Array(l+1).join("-");
    }
    //console.log(genid)
    return [genid];
}

function normalizeGenid(v) {
    v = v.trim();
    if (v.length == 0) {
        return v;
    } else if (v.length < 26) {
        v = v + new Array(26 - v.length + 1).join("-");
    } else if (v.length > 26) {
        v = v.substr(0, 26);
    }
    return v.toUpperCase();
}

function validateGenid(val) {
    var ok;
    console.log(val);
    for (var t in genid) {
        var fields = genid[t].fields;
        ok = true;
        for (var i = 0; i < fields.length && ok; ++i) {
            var f = fields[i];
            var x = val.substring(f.start, f.end + 1);
            if (x == (new Array(f.end-f.start+2).join("-")) ||
                x == (new Array(f.end-f.start+2).join("0")) ) {
                ok = true;
                //console.log(t, f.name, "--");
                continue;
            }
            switch (f.ftype) {
                case 1: // predefined list
                    ok = f.values.indexOf(x) != -1;
                    break;
                case 2: // alphabetic
                    ok = /^[a-zA-Z]+$/.test(x);
                    break;
                case 3: // numeric
                    ok = /^[0-9]+$/.test(x);
                    break;
                case 4: // alphanumeric
                    ok = /^[a-zA-Z0-9]+$/.test(x);
                    break;
            }
            //console.log(t, f.name, ok?"OK":"error");
        }
        //if (ok && val.substr(f.end+1,26) == (new Array(26-f.end+1).join("-"))) break;
        // if genid validated AND (last field reaches end of genealogy OR remaining characters are '-' or '0')
        if (ok && (f.end == 25 || /^[\-0]+$/.test(val.substr(f.end+1,26)))) {
            console.log("Detected type:", t);
            break;
        }

    }
    console.log("[validate genid]", ok);
    return ok;
}

function validate3(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    if (key != 9) { // don't prevent tab from causing to move to next field
        key = String.fromCharCode( key );
        var regex = /[a-zA-Z0-9\b]/;
        if( !regex.test(key) ) {
            theEvent.returnValue = false;
            if(theEvent.preventDefault) theEvent.preventDefault();
        }
    }
}

function addGenId(list) {
    for (var i = 0; i < list.length; ++i) {
        if (list[i] == new Array(27).join("-"))
            continue;
        if (!(list[i] in samples)) {
            var row = $("#samplesummary").DataTable().row.add({genid: list[i]}).node();
            samples[list[i]] = true;
        }
    }
    $("#samplesummary").DataTable().draw();
}