$(function() { 
    initCsrf();
    initMisc();
    initAccordion();
    initTable();
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

function initMisc() {
    //$("#content").css("padding-bottom", "100px");
    //$("#content").css("height", "auto");
    $("#main_tabs").tabs();
}

function initAccordion() {

    accTs1 = null;
    accTs2 = null;

    align1DataTable = $("#align1").dataTable({
        bFilter: false,
        bLengthChange: false,
        //"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": 5,
        aoColumns: [
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" }
        ],
        oLanguage: {
            sEmptyTable: "No alignments available"
        },
        aaSorting: [[1, "asc"]]
    });

    align2DataTable = $("#align2").dataTable({
        bFilter: false,
        bLengthChange: false,
        //"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": 5,
        aoColumns: [
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" },
            { sClass: "centered" }
        ],
        oLanguage: {
            sEmptyTable: "No alignments available"
        },
        aaSorting: [[1, "asc"]]
    });

    $("#otherCombo").accordion({
        active: false,
        collapsible: true,
        animate: 200,
        heightStyle: "content",
        beforeActivate: function(evt, ui) {
            if ($(ui.newPanel).length == 0) {
                // accordion is being collapsed
                // unregister event handlers
                $("#ts1").off('change.accordion');
                $("#ts2").off('change.accordion');
                return;
            }
            
            $("#ts1").on('change.accordion', function() {
                updateAligns("1");
            });

            $("#ts2").on('change.accordion', function() {
                updateAligns("2");
            });


            if (accTs1 != $("#ts1-seqid").val()) {
                updateAligns("1");
            }

            if (accTs2 != $("#ts2-seqid").val()) {
                updateAligns("2");
            }
        }
    });
}

function updateAligns(id) {
    // animation
    $("#align"+id+"-div").hide();
    $("#loada"+id).show();
    
    if ($("#ts"+id+"-seqid").val()) {

        $.ajax({
            url: window.location,
            type: 'GET',
            success: function(msg) {
                eval('align'+id+'DataTable.fnClearTable()');
                var p = JSON.parse(msg);
                for (var i = 0; i < p.length; ++i) {
                    eval('align'+id+'DataTable.fnAddData('+
                        '[\'<input type="radio" name="al'+id+'" value="'+p[i][0] +'">\']'+
                        '.concat(p[i].slice(1)))');
                }
                eval('align'+id+'DataTable.$("input[type=\'radio\']").first().prop("checked", true)');
                // animation
                $("#loada"+id).hide();
                $("#align"+id+"-div").slideDown('fast');

            },
            error: function() {
                alert("Cannot connect to server", "Error");
            },
            data: 'act=getalign&ts_id='+$('#ts'+id+"-seqid").val()
        });
    } else {
        eval('align'+id+'DataTable.fnClearTable()');
        // animation
        $("#loada"+id).hide();
        $("#align"+id+"-div").slideDown('fast');
    }

    eval('accTs' + id +' = $("#ts'+id+'-seqid").val()');
}

function initTable() {

    $("#primers").dataTable({
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

    seqpairsDataTable = $("#seqpairs").dataTable({
        bFilter: false,
        bLengthChange: false,
        iDisplayLength: 8,
        aoColumns: [
            {
                sTitle: '<input type="checkbox" id="selall" value="">',
                sWidth: "3%",
                sClass: "centered",
                bSortable: false
            },
            {
                sTitle: "Type",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Seq. name",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Ref.",
                sWidth: "6%",
                sClass: "centered"
            },
            {
                sTitle: "Start",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "End",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Gene name",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Seq. name",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Ref.",
                sWidth: "6%",
                sClass: "centered"
            },
            {
                sTitle: "Start",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "End",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Gene name",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Length",
                sWidth: "6%",
                sClass: "centered"
            },
            {
                sTitle: "Name",
                sClass: "centered"
            }
        ],
         oLanguage: {
            sEmptyTable: "No sequence combo"
        },
        aaSorting: [[0, "asc"]]
    });

    $("#selall").change(toggleSelCombo);
}

function toggleSelCombo() {
    var val = $("#selall").is(":checked");
    seqpairsDataTable.$('input').prop('checked', val);
}

function selectPrimer(target, primerID, primerName) {
    $("#ts" + target).val(primerName);
    $("#ts" + target + "-seqid").val(primerID);
}


function initButtons() {
    // specifications tab

    $("#gene2").select2({
        width: 'resolve',
        placeholder: 'Gene symbol',
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
                $("#tschrom").val(item.chrom).change();
                $("#tsgene").val(item.id);
                return '<b>'+item.symbol + '</b>&nbsp;<span class="small">(' + item.ac + ')</span>';
            } else
                return item.text;
        }
    });

    $("#selenst").select2({
        width: 'resolve',
        placeholder: 'Ensemble transcript accession',
        ajax: {
            url: annotations_url + '/newapi/transcriptInfo/',
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
            return '<b>'+item.ac+'</b>';
        },
        templateSelection: function(item) {
            if (item.id != "") {
                return '<b>'+item.ac + '</b>';
            } else
                return item.text;
        }
    });

    $("#selrefseq").select2({
        width: 'resolve',
        placeholder: 'RefSeq transcript accession',
        ajax: {
            url: annotations_url + '/newapi/refSeqInfo/',
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
            return '<b>'+item.ac+'</b>';
        },
        templateSelection: function(item) {
            if (item.id != "") {
                return '<b>'+item.ac + '</b>';
            } else
                return item.text;
        }
    });

    $("#selintrons li input[name='tsexclintr']").on("change", function() {
        if ($(this).prop("checked") == true) {
            $(this).siblings("div").children("select").prop("disabled", false);
            $("#selintrons li input[name='tsexclintr']").not($(this)).siblings("div").children("select").prop("disabled", true);
        }
    });
    $("#selintrons li input[name='tsexclintr'][value='include']").prop("checked", true).change();

    $("#save1").click(function() {
        // name
        var nam = $("#tsname1");
        if (nam.val().trim() == "") {
            alert("Please provide a name for the target sequence");
            return;
        }

        var gene = $("#tsgene");
        if (gene.val() === undefined || gene.val().trim() == "") {
            alert("Please type a gene symbol for the target sequence");
            return;
        }

        // coordinates
        var start = $("#tsstart");
        var end = $("#tsend");
        var chrom = $("#tschrom");
        var length = $("#tslength");
        if (start.val().trim() == "" || end.val().trim() == "" || parseInt(start.val().trim()) >= parseInt(end.val().trim()) || length.val().trim() == "") {
            alert("Please provide start and end coordinates (start < end) and the probe length", "Error");
            return;
        }

        // introns
        var tsexclintr = $("input[name=tsexclintr]:checked").val()
        if (tsexclintr == 'excludeenst') {
            var enst = $("#selenst").val();
            if (enst == "") {
                alert("Please select an Ensembl transcript", "Error");
                return;
            }
            $("#txid").val(enst);
        }
        else
        if (tsexclintr == 'excluderefseq') {
            var refseq = $("#selrefseq").val();
            if (refseq == "") {
                alert("Please select a RefSeq transcript", "Error");
                return;
            }
            $("#txid").val(refseq);
        }
        else {
            return;
        }
        
        $.ajax({
            type: 'POST',
            url: window.location,
            data: $("#savefrm1").serialize(),
            success: function() {window.location.replace(window.location);},
            error: function(jqXHR, textStatus, errorThrown) {alert(jqXHR.responseText, "Error")}
        });
    });

    $("#tschrom").change(function() {
        var opt = $("#tschrom option:selected");
        var min = opt.data("start");
        var max = opt.data("end");
        $("#tsstart").attr("min", min);
        $("#tsstart").attr("max", max);
        $("#tsend").attr("min", min);
        $("#tsend").attr("max", max);
    });

    // primers tab

    $("#search").click(function() {
        
        // animation
        $("#primers-div").hide();
        $("#loadts").show();
        
        $.ajax({
            url: window.location,
            type: 'GET',
            success: function(msg) {
                primerDataTable.fnClearTable();
                var p = JSON.parse(msg);
                for (var i = 0; i < p.length; ++i) {
                    primerDataTable.fnAddData(['<span id="name-'+p[i][0]+'">'+p[i][1]+'</span>',
                                                p[i][2],
                                                '<span style="display: inline-block; cursor: pointer" class="ui-icon ui-icon-circle-triangle-e selseq" data-seqid="'+p[i][0]+'"></span>']);
                }
                primerDataTable.$('.selseq').click(function() {
                    var id = $(this).data("seqid");
                    var v = $("#name-"+id).text();
                    $(activeEl).next("input[type='hidden']").val(id);
                    $(activeEl).val(v).change(); // manually trigger change event
                });
                // animation
                $("#loadts").hide();
                $("#primers-div").slideDown('fast');

            },
            error: function() {
                alert("Cannot connect to server", "Error");
            },
            data: 'act=searchts&tsname='+$('#tsname').val()+'&gsymbol='+$('#gsymbol').val()
        });
    });

    $(".clr").click(function(evt) {
        var target = evt.target;
        var id = parseInt($(target).attr("id").substring(3,4));
        $("#ts"+id).removeData();
        $("#ts"+id).val("").click();
        $("#ts"+id).val("").change();
    });

    $(".new").click(function(evt) {
        var w = screen.width-100;
        var h = screen.height-400;
        var target = evt.target;
        var id = parseInt($(target).attr("id").substring(3,4));
        $("#ts"+id).val("").click();
        var left = 10;//(screen.width/2)-(w/2);
        var top = 10;//(screen.height/2)-(h/2);
        neww=window.open(   ts_url,
                            "_blank",
                            'toolbar="no", location="no", status="no",'+
                            'menubar="no", scrollbars="no", resizable="no", '+
                            'width='+w+', height='+h+', top='+top+', left='+left
                        );

        if (window.focus) {
            neww.focus();
        }
        // register unload handler only after window has fully loaded,
        // otherwise unload event is triggered when window is loading
        // (because URL has changed)
        //$(neww).load(function() {
        //    $(neww).unload(function() {
        //        alert("window closed");
        //    });
        //});
    });

    $("#findpairs").click(function() {
        var ts1_id = $("#ts1-seqid").val();
        var ts2_id = $("#ts2-seqid").val();
        
        if (!ts1_id || !ts2_id || ts1_id == ts2_id) {
            return;
        }
        
        // animation
        $("#pairs").hide();
        $("#loadsc").show();
        
        $.ajax({
            url: window.location,
            type: 'GET',
            success: function(msg) {

                //seqpairsDataTable.fnClearTable();
                var combos = JSON.parse(msg);
                for (var i = 0; i < combos.length; ++i) {
                    seqpairsDataTable.fnAddData(
                        ['<input type="checkbox" class="combo" data-pr1="'+combos[i][0]+'" data-pr2="'+combos[i][2]+'" data-al1="'+combos[i][1]+'" data-al2="'+combos[i][3]+'">']
                        .concat(combos[i].slice(4, 15))
                        .concat(['<input type="text" class="primer length" value="'+combos[i][15]+'" style="width: 50%"> bp'])
                        .concat(['<input type="text" class="primer name" value="'+combos[i][16]+'" style="width: 90%">'])
                    );
                }
                // animation
                $("#loadsc").hide();
                $("#pairs").slideDown('fast');
            },
            error: function() {
                alert("Cannot connect to server", "Error");
            },
            data: 'act=seqcombo&ts1_id='+ts1_id+'&ts2_id='+ts2_id
        });
    });

    $("#insert").click(function() {
        var al1_id = align1DataTable.$("input:checked").val();
        var al2_id = align2DataTable.$("input:checked").val();

        if (!al1_id || !al2_id || al1_id == al2_id) {
            return;
        }

        // animation
        $("#pairs").hide();
        $("#loadsc").show();
        
        $.ajax({
            url: window.location,
            type: 'GET',
            success: function(msg) {
                var combo = JSON.parse(msg);
                if (combo) {
                    seqpairsDataTable.fnAddData(
                        ['<input type="checkbox" class="combo" data-pr1="'+combo[0]+'" data-pr2="'+combo[2]+'" data-al1="'+combo[1]+'" data-al2="'+combo[3]+'">']
                        .concat(combo.slice(4, 15))
                        .concat(['<input type="text" class="primer length" value="'+combo[15]+'" style="width: 50%"> bp'])
                        .concat(['<input type="text" class="primer name" value="'+combo[16]+'" style="width: 90%">'])
                    );
                }
                // animation
                $("#loadsc").hide();
                $("#pairs").slideDown('fast');
                $("#accord").click();

            },
            error: function() {
                alert("Cannot connect to server", "Error");
            },
            data: 'act=newcombo&al1_id='+al1_id+'&al2_id='+al2_id
        });

    });

    $("#save").click(function() {
        var query_string = "";
        if (seqpairsDataTable.$("input.combo:checked").length == 0) {
            return;
        }
        var selectedCombosTR = seqpairsDataTable.$("input.combo:checked").parent().parent();
        var invalid = selectedCombosTR.find("input.length").filter(function(){s=$(this).val(); n = parseInt(s); return (isNaN(n) || s!=n);});
        var valid = selectedCombosTR.find("input.length").not(invalid);
        valid.removeClass("error");
        if (invalid.length > 0) {
            alert("Please correct invalid length values", "Error")
            invalid.addClass("error");
            return;
        }

        var combos = selectedCombosTR.map(function(i, el) {
            var inp = $(el).find("input.combo");
            var pr1 = inp.data("pr1");
            var pr2 = inp.data("pr2");
            var al1 = inp.data("al1");
            var al2 = inp.data("al2");
            var length = $(el).find("input.length").val();
            var name = $(el).find("input.name").val();
            return {pr1: pr1, al1: al1, pr2: pr2, al2: al2, length: length, name: name};
        }).get();

        $("#combos-list").val(JSON.stringify(combos));
        
        $("#seqpairsfrm").submit();
    });
}