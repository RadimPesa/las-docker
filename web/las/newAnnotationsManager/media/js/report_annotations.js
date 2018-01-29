$(function() { 
    initCsrf();
    initGenid();
    initControllers();
    initTables();
 });

var seqalt_list = {};
var sample_list = {};

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
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }); 
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
    $("#alter_tabs, #sample_tabs").tabs();

    // init gene symbol selector with auto complete (ajax-backed)
    $("#gene").select2({
        width: 'resolve',
        placeholder: 'Start typing a gene symbol...',
        ajax: {
            url: "./",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    searchGene: params.term // search term
                };
            },
            processResults: function (data, page) {
                // parse the results into the format expected by Select2.
            // since we are using custom formatting functions we do not need to
            // alter the remote JSON data
                return {results: data};
            },
        },
        minimumInputLength: 1,
        templateResult: function(item) {
            if (item.loading) return item.text;
            return '<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>';
        },
        templateSelection: function(item) {
            if (item.id != "")
                return '<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>';
            else
                return item.text;
        }
    });
    
    // change event when gene is selected
    $("#gene").change(function() {
        var gene_uuid = $(this).val();
        if (gene_uuid == null) return;
        clearOptions("#tx, #exon, #seqalt");
        console.log("New gene selected: ", gene_uuid);
        $.ajax({
            url: "./",
            dataType: "json",
            type: 'GET',
            data: {getTranscripts: JSON.stringify([gene_uuid])},
            success: function(res) {
                // find default tx
                var defaultTx = res[gene_uuid].default;
                var tx = res[gene_uuid].all;

                tx.unshift({'empty': true, 'id': -1, 'text': 'Any'});
                $("#tx").select2({
                    width: 'resolve',
                    placeholder: 'Transcript accession',
                    data: tx,
                    templateResult: function(item) {
                        if (item.loading || item.id == -1) return item.text;
                        return '<b>'+item.tx_ac+'</b>&nbsp;<span class="small">('+item.num_exons+' exons'+(item.is_refseq?', RefSeq':'')+')</span>';
                    },
                    templateSelection: function(item) {
                        if (item.id != "" && item.id != -1) {
                            return '<b>'+item.tx_ac+'</b>&nbsp;<span class="small">('+item.num_exons+' exons'+(item.is_refseq?', RefSeq':'')+')</span>';
                        }
                        else {
                            return item.text;
                        }
                    }
                })
                    .val(defaultTx)
                    .change();
                    
                $("#tx option:selected").attr("data-default", "true");
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            }
        });
    });

    // init transcript selector
    $("#tx").select2({width: 'resolve', placeholder: 'Transcript accession'});

    // init set default tx
    $("#setdefaulttx").click(function() {
        $("#tx option[data-default=true]").prop("selected", true);
        $("#tx").change();
    })

    // change event when tx is selected
    $("#tx").change(function() {
        var tx_uuid = $(this).val();
        clearOptions("#exon, #seqalt");
        if (tx_uuid == null) return;
        console.log("New transcript selected: ", tx_uuid);
        $.ajax({
            url: "./",
            dataType: "json",
            type: 'GET',
            data: {getExons: tx_uuid},
            success: function(exons) {
                exons.unshift({'empty': true, 'id': -1, 'text': 'Any'});
                $("#exon").select2({
                    width: 'resolve',
                    placeholder: 'Exon',
                    data: exons,
                    templateResult: function(item) {
                        if (item.loading || item.id == -1) return item.text;
                        return '<b>Exon '+item.cnt+'</b>&nbsp;<span class="small">('+item.length+' bp)</span>';
                    },
                    templateSelection: function(item) {
                        if (item.id != "" && item.id != -1) {
                            return '<b>Exon '+item.cnt+'</b>&nbsp;<span class="small">('+item.length+' bp)</span>';
                        } else {
                            return item.text;
                        }
                    }
                })
                    .val(-1)
                    .change();
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            }
        });
    });

    // init exon selector
    $("#exon").select2({width: 'resolve', placeholder: 'Exon'});

    $("#exon").change(function() {
        updateSeqAltList();
    });

    // init seqalt selector
    mydata = [{id: 1, text: 'opt1'}];
    $("#seqalt").select2({width: 'resolve', placeholder: 'Sequence alteration',
    });

    // init cds selector
    /*
    $("#cds").change(function () {
        if ($(this).val() == 0) {
            $("#tx,#exon").prop("disabled", true).val(null).change();
        } else {
            $("#tx,#exon").prop("disabled", false);
        }
    });
    */

    
    // init clear parameters for filtering seq.alt.
    $("#clearallalt").click(function() {
        clearOptions("#gene, #tx, #exon");
    });

    // init add seq alt button
    $("#addseqalt").click(function() {
        addSeqaltGeneItem("#seqalt option:selected", "region");
    });

    // init add seq alt-all button
    $("#addseqalt-all").click(function() {
        addSeqaltGeneItem("#seqalt option", "region");
    });

    // init seq alt target list
    $( "#targetalt" ).sortable();
    $( "#targetalt" ).disableSelection();
    // init gene target list
    $( "#targetgenes" ).sortable();
    $( "#targetgenes" ).disableSelection();

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
        var el = $("#gene2 option:selected");
        var gene_uuid = el.val();
        $.ajax({
            url: "./",
            dataType: "json",
            type: 'GET',
            data: {getTranscripts: JSON.stringify([gene_uuid])},
            success: function(res) {
                // find default tx
                var d = res[gene_uuid].default;
                var tx = res[gene_uuid].all;
                var tx_ac = tx.filter(function(el) {return el.id == d})[0].tx_ac;
                el.data().data.tx_ac = tx_ac;
                addSeqaltGeneItem("#gene2 option:selected", "gene");
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            }
        });
    });

    // init add seq alt-all button
    $("#addgene-all").click(function() {
        var el = $("#gene2 option");
        var uuids = el.map(function(i,x) {return $(x).val();}).get();
        $.ajax({
            url: "./",
            dataType: "json",
            type: 'GET',
            data: {getTranscripts: JSON.stringify(uuids)},
            success: function(res) {
                // find default tx
                for (var j = 0; j < uuids.length; ++j) {
                    var d = res[uuids[j]].default;
                    var tx = res[uuids[j]].all;
                    if (tx.length > 0) {
                        var tx_ac = tx.filter(function(el) {return el.id == d})[0].tx_ac;
                        $(el[j]).data().data.tx_ac = tx_ac;
                    }
                }
                addSeqaltGeneItem("#gene2 option", "gene");
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            }
        });
    });

    // init add gid button
    $("#add_gid").click(function() {
        var g = genIdFromForm();
        addGenId(g);
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
        var list1 = Object.keys(seqalt_list);
        var list2 = Object.keys(sample_list);
        var missing = [];
        if (list1.length == 0 && list2.length == 0) {
            alert("Please choose at least one target alteration/gene or one target sample");
            event.preventDefault();
            return;
        }
        $("#frm_seqalt").val(JSON.stringify(seqalt_list));
        $("#frm_samples").val(JSON.stringify(list2));
    });

}

function initTables() {
    $("#altgenesummary").DataTable({
        columns: [
            {searchable: false, defaultContent: ''},
            {data: 'chrom', className: 'center'},
            {data: 'gene', className: 'center'},
            {data: 'tx', className: 'center'},
            {data: 'locg', className: 'center'},
            {data: 'locc', className: 'center'},
            {data: 'locp', className: 'center'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        sort: false,
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    $("#altgenesummary").DataTable().on( 'order.dt search.dt', function () {
        $("#altgenesummary").DataTable().column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();

    $("#altgenesummary tbody").on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = r.data("id");
        $("#altgenesummary").DataTable().row(r)
                                        .remove()
                                        .draw();
        delete seqalt_list[id];
    });

    $("#samplesummary").DataTable({
        columns: [
            {data: 'genid', className: 'center'},
            {defaultContent: '<span class="action delete ui-icon ui-icon-close"></span>', orderable: false, searchable: false, className: 'center'}
        ],
        lengthMenu: [ 8, 25, 50, 100 ]
    });

    $("#samplesummary tbody").on("click", "span.action.delete", function () {
        var r = $(this).parents("tr");
        var id = r.data("id");
        $("#samplesummary").DataTable().row(r)
                                        .remove()
                                        .draw();
        delete sample_list[id];
    });

    $("#clearall1").click(function() {
        $("#altgenesummary").DataTable().rows().remove().draw();
        seqalt_list = {};
    });

    $("#clearall2").click(function() {
        $("#samplesummary").DataTable().rows().remove().draw();
        sample_list = {};
    });

}

function getDefaultTranscript(tx) {
    // select transcript with max num exons, with preference for refseq transcripts
    // returns index of selected tx within the array
    var toSelect = tx.reduce(
        function (prev,curr,init) {
            if ((curr.is_refseq == true && prev.refseq == false) || (curr.num_exons > prev.num)) {
                return {refseq: curr.is_refseq, num: curr.num_exons, val: curr.id};
            } else {
                return prev;
            }
        },
        
        {refseq:false, val:null, num:0}
    );
    return toSelect.val;
}

function updateSeqAltList() {
    var theGene = $("#gene").val();
    var theTx = $("#tx").val();
    var theExon = $("#exon").val();
    if (theGene == null || theTx == null || theExon == null)
        return;
    console.log("Updating SeqAlt list");
    console.log({getAltLocInGene: theGene, tx: theTx, exon: theExon});
    clearOptions("#seqalt");
    $.ajax({
        url: "./",
        dataType: "json",
        type: 'GET',
        data: {getAltLocInGene: theGene, tx: theTx, exon: theExon},
        success: function(res) {
            $("#seqalt").select2({
                width: 'resolve',
                placeholder: 'Sequence alteration',
                data: res,
                allowClear: true,
                templateResult: function(item) {
                    if (item.loading) return item.text;
                    if (item.locp) {
                        var markup = '<b>'+item.locp+'</b>&nbsp;<span class="small">('+item.locc+', '+item.locg+')</span>';
                    } else {
                        var markup = '<b>'+item.locg+'</b>';
                    }
                    return markup;
                },
                templateSelection: function(item) {
                    if (item.id != "") {
                        if (item.locp) {
                            var markup = '<b>'+item.locp+'</b>&nbsp;<span class="small">('+item.locc+', '+item.locg+')</span>';
                        } else {
                            var markup = '<b>'+item.locg+'</b>';
                        }
                        return markup;
                    }
                    else
                        return item.text;
                }

            })
                .val(null)
                .change()
                //.select2("open");
        },
        error: function() {
            alert("Cannot connect to server", "Error");
        }
    });
}

function clearOptions(selector) {
    var sel = selector.split(',').map(function(x) {return x.trim();});
    for (var i = 0; i < sel.length; ++i) {
        $(sel[i] + " option").remove();
        $(sel[i]).val(null).change();
    }
}

function getSeqaltGeneInfo(data) {
    return {
        chrom: data.chrom,
        gene: data.symbol,
        tx: data.tx_ac || "n/a",
        locg: data.locg || "n/a",
        locc: data.locc || "n/a",
        locp: data.locp || "n/a",
        id: data.id
    };
}

function addSeqaltGeneItem(srcSelector, type) {
    var list = $(srcSelector).get().map(function(el) {
        return $(el).data().data;
    });
    for (var i = 0; i < list.length; ++i) {
        if (!(list[i].id in seqalt_list)) {
            var info = getSeqaltGeneInfo(list[i]);
            var row = $("#altgenesummary").DataTable().row.add(info).node();
            seqalt_list[list[i].id] = {type: type, tx: list[i].tx_ac};
            $(row).data("id", list[i].id);
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
            $(row).data("id", list[i]);
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
                url: "./",
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        searchGene: params.term // search term
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
            url: "./",
            dataType: "json",
            type: 'GET',
            data: {getGenesInRegion: $("#chrom").val(), regionStart: $("#coord-from").val(), regionEnd: $("#coord-to").val()},
            success: function(res) {
                $("#gene2").select2({
                    width: 'resolve',
                    placeholder: 'Gene symbol',
                    data: res,
                    allowClear: true,
                    templateResult: function(item) {
                        if (item.loading) return item.text;
                        return '<b>'+item.symbol+'</b>&nbsp;<span class="small">'+item.ac+'</span>';
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
