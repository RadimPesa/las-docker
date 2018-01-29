$(function() { 
    initCsrf();
    initMisc();
    initAccordion();
    initTable();
    initInputs();
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
            { sTitle: "",
              //sWidth: "15%",
              sClass: "centered" },
            { sTitle: "Chr",
              //sWidth: "15%",
              sClass: "centered" },
            { sTitle: "Start",
              //sWidth: "30%",
              sClass: "centered" },
            { sTitle: "End",
              //sWidth: "30%",
              sClass: "centered" },
            { sTitle: "Str",
              //sWidth: "5%",
              sClass: "centered" },
            { sTitle: "Gene",
              //sWidth: "20%",
              sClass: "centered" }
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
            { sTitle: "",
              //sWidth: "15%",
              sClass: "centered" },
            { sTitle: "Chr",
              //sWidth: "15%",
              sClass: "centered" },
            { sTitle: "Start",
              //sWidth: "30%",
              sClass: "centered" },
            { sTitle: "End",
              //sWidth: "30%",
              sClass: "centered" },
            { sTitle: "Str",
              //sWidth: "5%",
              sClass: "centered" },
            { sTitle: "Gene",
              //sWidth: "20%",
              sClass: "centered" }
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

    primerDataTable = $("#primers").dataTable({
        bFilter: false,
        bLengthChange: false,
        iDisplayLength: 5,
        aoColumns: [
            { sTitle: "Name",
              sWidth: "25%",
              sClass: "centered"
            },
            { sTitle: "Sequence",
              sWidth: "65%",
              sClass: "centered"
            },
            { sTitle: "Select",
              sWidth: "10%",
              bSortable: false,
              sClass:  "centered"
            }
        ],
        oLanguage: {
            sEmptyTable: "No target sequence"
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
                sTitle: "Seq. name",
                sWidth: "8%",
                sClass: "centered"
            },
            {
                sTitle: "Chr.",
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
                sTitle: "Chr.",
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

function initInputs() {

    var max_inputs = 2;

    $(".pair").click(setActiveField);
    $("#ts1").click();

    $(".pair").change(function(evt) {
        var target = evt.target;
        var id = parseInt($(target).attr("id").substring(2,3));
        if (id < max_inputs) {
            $("#ts" + (id+1)).click();
        }
    });
}

function setActiveField(evt) {
    var target = evt.target;
    $(".pair").removeClass("pairactive");
    $(target).addClass("pairactive");
    activeEl = $(target);
}

function initButtons() {
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

                seqpairsDataTable.fnClearTable();
                var combos = JSON.parse(msg);
                for (var i = 0; i < combos.length; ++i) {
                    seqpairsDataTable.fnAddData(
                        ['<input type="checkbox" name="combos" value="'+combos[i][0]+'_'+combos[i][1]+'">']
                        .concat(combos[i].slice(2, 12))
                        .concat(['<input name="length_'+combos[i][0]+'_'+combos[i][1]+'" type="text" class="primer" value="'+combos[i][12]+'" style="width: 50%"> bp'])
                        .concat(['<input name="name_'+combos[i][0]+'_'+combos[i][1]+'" type="text" class="primer" value="'+combos[i][13]+'" style="width: 90%">'])
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
                        ['<input type="checkbox" name="combos" value="'+combo[0]+'_'+combo[1]+'">']
                        .concat(combo.slice(2, 12))
                        .concat(['<input name="length_'+combo[0]+'_'+combo[1]+'" type="text" class="primer" value="'+combo[12]+'" style="width: 50%"> bp'])
                        .concat(['<input name="name_'+combo[0]+'_'+combo[1]+'" type="text" class="primer" value="'+combo[13]+'" style="width: 90%">'])
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
        if (seqpairsDataTable.$("input[name='combos']:checked").length == 0) {
            return;
        }
        seqpairsDataTable.$("input[name='combos']").not(":checked").parent().parent().find("input[type='text']").prop("disabled", true);
        var invalid = seqpairsDataTable.$("input[name*='length']:enabled").filter(function(){s=$(this).val(); n = parseInt(s); return (isNaN(n) || s!=n);});
        var valid = seqpairsDataTable.$("input[name*='length']:enabled").not(invalid);
        valid.removeClass("error");
        if (invalid.length > 0) {
            seqpairsDataTable.$("input[name='combos']").not(":checked").parent().parent().find("input[type='text']").prop("disabled", false);
            invalid.addClass("error");
            return;
        }

        
        $("#seqpairsfrm").submit();
    });
}