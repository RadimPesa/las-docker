$(function() { 
    initCsrf();
    initGenid();
    initControllers();
    initTables();
    loadGenePredefLists();
});

var gene_list = {};
var sample_list = {};
var criteria = [];
var criteria_cnt = 0;

var criteriaDt;
var genesDt;
var samplesDt;

var next_index = 1;
var count = 0;

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
//function initCsrf() {
//    $('html').ajaxSend(function(event, xhr, settings) {
//        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
//            //Only send the token to relative URLs i.e. locally.
//            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')//);
//}
//    }); 
//}
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

function loadGenePredefLists(index) {
    var url = annotations_url + '/newapi/predefinedGenomicLists/';
    $.ajax({
        url: url,
        success: function(res) {
            var select = $("#predef_genes");
            select.children().remove();
            for (var i = 0; i < res.length; ++i) {
                var option = $("<option></option>");
                option.text(res[i].name);
                option.val(res[i].id);
                option.data("data", res[i].data);
                select.append(option);
            }
            if (index !== undefined) {
                var opt = select.find("option[value=" + index + "]");
                if (opt.length) {
                    opt.prop("selected", true);
                } else {
                    select.prop("selectedIndex", -1);
                }
            } else {
                select.prop("selectedIndex", -1);
            }
        },
        error: function(jqXHR, text, errorThrown) {
            alert("An error occurred while loading predefined gene lists.")
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

function initControllers() {
    // init alter-tabs
    $("#annot-src, #tech").SumoSelect(); //select2({minimumResultsForSearch: Infinity});
    $("#domain").SumoSelect({selectAll: true});

    // update domain dropdown lists
    $("select#tech").on("change", function() {
        var techVal = $(this).val();
        var domain_elem = $("select#domain");
        //var an_elem = $(this).closest("span.criterion").find("select.an");
        domain_elem.children().remove();
        //an_elem.children().remove();
        //an_elem[0].sumo.reload();
        var this_labels = technologies[techVal]['labels'];
        for (var j = 0; j < this_labels.length; ++j) {
            domain_elem.append('<option value="' + this_labels[j] + '">' + labels[this_labels[j]] + '</option>');
        };
        domain_elem[0].sumo.reload();
    }).change();


    $("#main_tabs").tabs();

    $("#newcriterion").click(newCriterion);

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

    // init chrom selector
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
        $("#coord-from, #coord-to").blur();
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

    // init clear region button
    $("#clearregion").click(function() {
        $("#chrom").prop("selectedIndex", -1);
        $("#chrom").change();
        $("#coord-from, #coord-to").val("");
        setGene2mode("auto");
    }).trigger("click");

    // init gene2 as drop-down list
    // init gene symbol selector with auto complete (ajax-backed)
    setGene2mode("auto");

    // init apply region button
    $("#applyregion").click(function() {
        setGene2mode("filtered");
    });

    // init add gene button
    $("#addgene").click(function() {
        addGeneItem("#gene2 option:selected", "gene");
    });

    // init add seq alt-all button
    $("#addgene-all").click(function() {
        addGeneItem("#gene2 option", "gene");
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

    $("#savegenelist").click(function() {
        var url = annotations_url + '/newapi/newPredefinedGenomicList/';
        var list1 = Object.keys(gene_list);
        if (list1.length == 0)
            return;
        var name = prompt("Name:", "Please type the name of the new list");
        $.ajax({
            method: "POST",
            url: url,
            data: { name: name, uuid_list: JSON.stringify(list1) },
            success: function(res) {
                loadGenePredefLists(res);
            },
            error: function(jqXHR, text, errorThrown) {
                if (jqXHR.responseJSON.status == -1) {
                    window.alert("This name is already in use. Please provide a different one.", "Error", "OK", function() {$("#savegenelist").click();});
                } else {
                    window.alert("An error has occurred while saving the list.", "Error", "OK");
                }
            }
        });
    });
    
    $("#delgenelist").click(function() {
        var url = annotations_url + '/newapi/deletePredefinedGenomicList/';
        var selected = $("#predef_genes").val();
        if (selected === null)
            return;
        var name = $("#predef_genes option:selected").text();
        confirm("Do you really want to delete predefined list <b>" + name + "</b>?", "Delete gene list", "Yes", "No", function() {
            $.ajax({
                method: "POST",
                url: url,
                data: { id: selected },
                success: function(res) {
                    loadGenePredefLists();
                },
                error: function(jqXHR, text, errorThrown) {
                    window.alert("An error has occurred while deleting the list.", "Error", "OK");
                }
            });
        });
    });

    // handler to load predefined gene list
    $("#predef_genes").change(function() {
        var selectedOption = $("#predef_genes option:selected");
        if (selectedOption.length == 0)
            return;
        // check if the panel already contains values
        if (Object.keys(gene_list).length != 0) {
            // if so, ask the user whether she wants to empty the current list and replace it with the selected one
            // or merge it with the contents of the selected one
            tripleChoiceDialog("The gene panel already contains some genes. Do you want to replace this content or merge it with the selected list?", "Replace or merge", "Cancel", "Replace", "Merge",
                null,
                function() {
                    $("#genes span.clearall").click();
                    selectedOption.prop("selected", true);
                    addGeneItem("#predef_genes option:selected", "gene");
                }, 
                function() {
                    addGeneItem("#predef_genes option:selected", "gene");
                }
            );
        } else {
            // if not, go ahead and add in the new list
            addGeneItem("#predef_genes option:selected", "gene");
        } 
    });


    $("#exportsites").click(function() {
        var toSend = $("#altgenesummary").DataTable().data().toArray();
        if (toSend.length == 0)
            return;
        toSend = JSON.stringify(toSend);

        /* submit request do download the file */
        var nIFrame = document.createElement('iframe');
        nIFrame.setAttribute('id', 'RemotingIFrame' );
        nIFrame.style.border = '0px';
        nIFrame.style.width = '0px';
        nIFrame.style.height = '0px';
             
        document.body.appendChild( nIFrame );
        var nContentWindow = nIFrame.contentWindow;
        nContentWindow.document.open();
        nContentWindow.document.close();
         
        var nForm = nContentWindow.document.createElement('form');
        nForm.setAttribute('method', 'post');
        
        var nInput = nContentWindow.document.createElement( 'input' );
        nInput.setAttribute( 'name', 'sitesList' );
        nInput.setAttribute( 'type', 'text' );
        nInput.value = toSend;
         
        nForm.appendChild(nInput);

        var nInput = nContentWindow.document.createElement('input');
        nInput.setAttribute('name', 'action');
        nInput.setAttribute('type', 'text');
        nInput.value = 'getSitesFile';
         
        nForm.appendChild(nInput);

        var nInput = nContentWindow.document.createElement('input');
        nInput.setAttribute('name', 'csrfmiddlewaretoken');
        nInput.setAttribute('type', 'hidden');
        nInput.value = getCookie('csrftoken');
         
        nForm.appendChild(nInput);

        nForm.onload = function () {
            console.log('finish');
        }
        
        nForm.setAttribute('action', window.location);
         
        /* Add the form and the iframe */
        nContentWindow.document.body.appendChild(nForm);

        /* Send the request */
        nForm.submit();
    });

    $("#frm_report").submit(function(event) {
        var list0 = criteria.filter(function(el) { return el !== undefined; });
        var list1 = Object.keys(gene_list);
        var list2 = Object.keys(sample_list);
        if (list0.length == 0 & list1.length == 0 && list2.length == 0) {
            alert(  "Please select at least one querying criterion, gene or sample.", "Parameters missing");
            event.preventDefault();
            return;
        }

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

        $("#frm_source").val($("#annot-src").val());
        $("#frm_criteria").val(JSON.stringify(list0));
        $("#frm_genes").val(JSON.stringify(list1));
        $("#frm_samples").val(JSON.stringify(list2));
    });
}

function initTables() {
    genesDt = $("#altgenesummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'chrom', className: 'center'},
            {data: 'gene', className: 'center'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });


    genesDt.on( 'draw.dt order.dt search.dt', function () {
        genesDt.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();

    criteriaDt = $("#criteriasummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'technology'},
            {data: 'domain'}, // render: function ( data, type, row ) { return data.join("<br>"); }
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        searching: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    criteriaDt.on( 'draw.dt', function () {
        criteriaDt.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();

    criteriaDt.on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = r.data("id");
        criteriaDt.row(r)
                .remove()
                .draw();
        delete criteria[id];
    });

    genesDt.on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = genesDt.row(r).data().id;
        genesDt.row(r).remove().draw();
        delete gene_list[id];
    });

    samplesDt = $("#samplesummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'genid', className: 'center'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
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

    $(".clearall").click(function() {
        $(this).parent().parent().parent().find("table").DataTable().$("span.action.delete").click();
    });

    // add another handler to clearall button within gene panel so that selected predefined list is also cleared
    $("#genes span.clearall").click(function() {
        $("#predef_genes").prop("selectedIndex", -1);
    });
}

function newCriterion() {
    var tech_val = $("#tech").val();
    var domain_val = $("#domain").val();
    if (!domain_val || domain_val.length == 0)
        return;

    for (var j = 0; j < domain_val.length; ++j) {
        var data = {'technology': tech_val, 'domain': domain_val[j]};
        var exists = criteria.filter(function(el) {return el.technology == data.technology && el.domain == data.domain;}).length !== 0;
        if (exists)
            continue;
        criteria.push(data);
        var text_data = {'technology': technologies[tech_val].name, 'domain': labels[domain_val[j]]};
        var row = $("#criteriasummary").DataTable().row.add(text_data).node();
        $(row).data("id", criteria_cnt++);
    }
    $("#criteriasummary").DataTable().draw();
}

function clearOptions(selector) {
    var sel = selector.split(',').map(function(x) {return x.trim();});
    for (var i = 0; i < sel.length; ++i) {
        $(sel[i] + " option").remove();
        $(sel[i]).val(null).change();
    }
}

function getGeneInfo(data) {
    return {
        chrom: data.chrom,
        gene: data.symbol,
        id: data.id
    };
}

function addGeneItem(srcSelector) {
    var list = $(srcSelector).get().map(function(el) {
        return $(el).data().data;
    });
    // ugly fix to make predefined gene lists load without changing much code
    if (list[0].length)
        list = list[0];
    for (var i = 0; i < list.length; ++i) {
        if (!(list[i].id in gene_list)) {
            var info = getGeneInfo(list[i]);
            var row = $("#altgenesummary").DataTable().row.add(info).node();
            gene_list[list[i].id] = true;
        }
    }
    $("#altgenesummary").DataTable().draw();
}

function addGenId(list) {
    for (var i = 0; i < list.length; ++i) {
        if (list[i] == new Array(27).join("-"))
            continue;
        if (!(list[i] in sample_list)) {
            var row = $("#samplesummary").DataTable().row.add({genid: list[i]}).node();
            sample_list[list[i]] = true;
        }
    }
    $("#samplesummary").DataTable().draw();
}

function setGene2mode(mode) {
    clearOptions("#gene2");
    if (mode == "auto") {
        $("#gene2").select2({
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
                if (item.id != "")
                    return '<b>'+item.symbol + '</b>&nbsp;<span class="small">(' + item.ac + ')</span>';
                else
                    return item.text;
            }
        });
    } else
    if (mode == "filtered") {
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

        clearOptions("#gene2");
        $.ajax({
            url: annotations_url + '/newapi/genesInRegion/',
            dataType: "json",
            type: 'GET',
            data: {chrom: $("#chrom").val(), start: $("#coord-from").val(), end: $("#coord-to").val()},
            success: function(res) {
                $("#gene2").select2({
                    width: 'resolve',
                    placeholder: 'Gene symbol',
                    data: function() {
                        for (var j = 0; j < res.length; ++j) {
                            res[j].text = res[j].symbol + ' ' + res[j].ac;
                        }
                        return res;
                        }(),
                    allowClear: true,
                    templateResult: function(item) {
                        if (item.loading) return item.text;
                        return '<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>';
                        return markup;
                    },
                    templateSelection: function(item) {
                        if (item.id != "")
                            return '<b>'+item.symbol + '</b>&nbsp;<span class="small">(' + item.ac + ')</span>';
                        else
                            return item.text;
                    }
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
