$(function() {
    initCsrf();
    inithandlers();
    initmisc();
    initdt();
});

var ds2data = [];

function initdt() {
    joinsrcDt = $("#joinsrc").dataTable({
        bFilter: false,
        bLengthChange: false,
        bPaginate: false,
        bInfo: false,
        bSort: false,
        bAutoWidth: false,
        oLanguage: {
            sEmptyTable: ' '
        },
        aoColumns: [
            { sTitle: "From table",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "Attribute",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "To table",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "Attribute",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "C",
              sWidth: "6%",
              sClass: "centered"
            }
        ]
    });
    
    joinsrc2destDt = $("#joinsrc2dest").dataTable({
        bFilter: false,
        bLengthChange: false,
        bPaginate: false,
        bInfo: false,
        bSort: false,
        bAutoWidth: false,
        oLanguage: {
            sEmptyTable: ' '
        },
        aoColumns: [
            { sTitle: "From table",
              sWidth: "25%",
              sClass: "centered"
            },
            { sTitle: "Attribute",
              sWidth: "25%",
              sClass: "centered"
            },
            { sTitle: "To table",
              sWidth: "25%",
              sClass: "centered"
            },
            { sTitle: "Attribute",
              sWidth: "25%",
              sClass: "centered"
            },
            { sTitle: "C",
              sWidth: "6%",
              sClass: "centered"
            }
        ]

    });

    joindestDt = $("#joindest").dataTable({
        bFilter: false,
        bLengthChange: false,
        bPaginate: false,
        bInfo: false,
        bSort: false,
        bAutoWidth: false,
        oLanguage: {
            sEmptyTable: ' '
        },
        aoColumns: [
            { sTitle: "From table",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "Attribute",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "To table",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "Attribute",
              sWidth: "23.5%",
              sClass: "centered"
            },
            { sTitle: "C",
              sWidth: "6%",
              sClass: "centered"
            }
        ]
    });
}

function initCsrf() {
    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
      var token;
      if (!options.crossDomain) {
        token = $.cookie("csrftoken");
        if (token) {
          return jqXHR.setRequestHeader('X-CSRFToken', token);
        }
      }
    });
}

function initmisc() {
    //dataDt = $("#data").dataTable({bFilter: false, bLengthChange: false, bPaginate: false, bInfo: false, bSort: false});
    //detailsDt = $("#tdetails").dataTable({bFilter: false, bLengthChange: false, bPaginate: false, bInfo: false, bSort: false});
    $("#auto, #man").hide();
    $("input[name='method']").change();
    $("#saveauto").prop("disabled", true);
}

function inithandlers() {
    $("select").change(function() {
        $("#saveauto").prop("disabled", true);
    });

    $("input[name='method']").change(function() {
        $("#auto, #man").hide();
        var mtd = $("input[name='method']:checked:enabled").val();
        $("#"+mtd).show();

    });

    $("#selds1").change(
        function() {
            var ds = $("#selds1").val();
            if (ds == null) return;
            var dsOther = $("#selds2").val();
            if (dsOther != null) {
                if (dsOther != ds) {
                    $("#method-auto").prop("disabled", true);
                    $("label[for='method-auto']").addClass("disabled");
                } else {
                    $("#method-auto").prop("disabled", false);
                    $("label[for='method-auto']").removeClass("disabled");
                }
            }
            $.ajax({
                url: "./",
                data: "ds="+ds,
                success: function(data) {
                    data = JSON.parse(data);
                    $("#selqe1 option").remove();
                    for (i = 0; i < data.length; ++i) {
                        var opt = $('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
                        opt.data("dst", [data[i][2], data[i][3]]);
                        $("#selqe1").append(opt);
                    }
                    $("#selqe1").prop('selectedIndex', -1);
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
        }
    );

    $("#selds2").change(
        function() {
            var ds = $("#selds2").val();
            if (ds == null) return;
            var dsOther = $("#selds1").val();
            if (dsOther != null) {
                if (dsOther != ds) {
                    $("#method-auto").prop("disabled", true);
                    $("label[for='method-auto']").addClass("disabled");
                } else {
                    $("#method-auto").prop("disabled", false);
                    $("label[for='method-auto']").removeClass("disabled");
                }
            }
            $.ajax({
                url: "./",
                data: "ds="+ds,
                success: function(data) {
                    data = JSON.parse(data);
                    $("#selqe2 option").remove();
                    for (i = 0; i < data.length; ++i) {
                        var opt = $('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
                        opt.data("dst", [data[i][2], data[i][3]]);
                        $("#selqe2").append(opt);
                    }
                    $("#selqe2").prop('selectedIndex', -1);
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
        }
    );

    $("#selqe1,#selqe2").change(function() {
        var qe1 = $("#selqe1 option:checked").text();
        var qe2 = $("#selqe2 option:checked").text();
        $("#qpname").val("From " + qe1 + " to " + qe2);
        $("#revqpname").val("From " + qe2 + " to " + qe1);
        $("#revqpnameman").val("From " + qe2 + " to " + qe1);
    });

    $("#go").click(
        function() {
            var qe1 = $("#selqe1").val();
            var qe2 = $("#selqe2").val();
            if (qe1 == null || qe2 == null) {
                alert("Please select source and destination entities from the drop-down lists", "Error");
                return;
            }
            if (qe1 == qe2) {
                //alert("A query path cannot be defined from an entity to itself!<br><br>Please select two different entities as source and destination.", "Error");
                //return;
                ;
            }
            var mtd = $("input[name='method']:checked:enabled").val();
            if (mtd == null) {
                alert("Please select a path definition method (automatic or manual)", "Error");
                return;
            }
            if (mtd == 'auto') {
                $("button").prop("disabled", true);
                $("#autopathdiv").children().remove();
                $("#autopathdiv").removeData("dsr");
                $.ajax({
                    url: "./",
                    data: {fromqe: qe1, toqe: qe2},
                    success: function(data) {
                        $("button").prop("disabled", false);
                        data = JSON.parse(data);
                        //console.log(data);
                        if (data.path == null) {
                            $("#autopathdiv").append('<p class="path" style="color: red">There is no path available</p>');
                            $("#autopathdiv").data("pathok", false);
                        } else {
                            $("#autopathdiv").data("dsr", data.dsr);
                            $("#autopathdiv").data("pathok", true);
                            $("#autopathdiv").append("<ol></ol>");
                            for (i = 0; i < data.path.length; ++i) {
                                $("#autopathdiv ol").append('<li><span class="pathel"><a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + data.path[i][0] + '">' + data.path[i][1] + '</a>.' + data.path[i][2] +'</span> &rarr; <span class="'+ (data.path[i][6] == true ? 'one' : 'many') + '"></span><span class="pathel"><a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + data.path[i][3] + '">' + data.path[i][4] + '</a>.' + data.path[i][5] + '</span></li>');
                            }
                        }
                    },
                    error: function(data) {
                        $("#go").prop("disabled", false);
                        alert("Error: failed to connect to server!");
                    }
                });


            } else {

                joinsrcDt.fnClearTable();
                joinsrc2destDt.fnClearTable();
                joindestDt.fnClearTable();
                $("#manpathdiv").text("");

                var dst1 = $("#selqe1 option:selected").data("dst");
                var dst2 = $("#selqe2 option:selected").data("dst");
                
                $("#srcdst").data("dst", dst1[0]);
                $("#srcdst").val("[" + $("#selds1 option:selected").text() + "]." + dst1[1]);
                $("#lblsrc").text("[" + $("#selds1 option:selected").text() + "]");

                $("#destdst").data("dst", dst2[0]);
                $("#destdst").val("[" + $("#selds2 option:selected").text() + "]." + dst2[1]);
                $("#lbldest").text("[" + $("#selds2 option:selected").text() + "]");

                if ($("#selds1").val() == $("#selds2").val()) {

                    $("tr.fullform").hide();
                    insertjoin(joindestDt, $("#srcdst").data("dst"));    
                
                } else {

                    $("tr.fullform").show();
                    insertjoin(joinsrcDt, $("#srcdst").data("dst"));
                
                    $.ajax({
                        url: "./",
                        data: {ds_dst_attr: $("#selds2").val()},
                        success: function(data) {
                            ds2data = JSON.parse(data);
                        },
                        error: function(data) {
                            alert("Error: failed to connect to server!");
                        }
                    });
                }

                /*$("#srcdst,#destdst").addClass("loading");
                var expectedCallbacks = 2;
                $.ajax({
                    url: "./",
                    data: {qe: qe1},
                    success: function(data) {
                        data = JSON.parse(data);
                        $("#srcdst").removeClass("loading");
                        $("#srcdst").data("dst", data[0]);
                        $("#srcdst").val(data[1]);
                        --expectedCallbacks || handleman();

                    },
                    error: function(data) {
                        $("#srcdst").removeClass("loading");
                        alert("Error: failed to connect to server!");
                    }
                });
                $.ajax({
                    url: "./",
                    data: {qe: qe2},
                    success: function(data) {
                        data = JSON.parse(data);
                        $("#destdst").removeClass("loading");
                        $("#destdst").data("dst", data[0]);
                        $("#destdst").val(data[1]);
                        --expectedCallbacks || handleman();
                    },
                    error: function(data) {
                        $("#destdst").removeClass("loading");
                        alert("Error: failed to connect to server!");
                    },
                });
                // execution continues with function handleman
                */
            }
        }
    );

    $("#saveauto").click(function() {
        var pathok = $("#autopathdiv").data("pathok");
        if (!pathok) {
            alert("No path available!", "Error");
            return;
        }
        
        var postdata = {
            auto: 'auto',
            name: $("#qpname").val(),
            descr: $("#qpdescr").val(),
            fromqe: $("#selqe1").val(),
            toqe: $("#selqe2").val(),
            isdefault: $("#qpdefault").is(":checked"),
            path: JSON.stringify($("#autopathdiv").data("dsr"))
        };
        if ($("#savereverseauto").prop("checked") == true) {
            postdata.saverev = true;
            postdata.revname = $("#revqpname").val();
            postdata.revdescr = $("#revqpdescr").val();
            postdata.revIsdefault = $("#revqpdefault").is(":checked");
        }

        $.ajax({
            url: "./",
            type: "post",
            data: postdata,
            success: function(data) {
                alert("Query path saved.", "Done", "OK", function() {window.location.reload()});
              
            },
            error: function(data) {
                alert("Error: failed to connect to server!");
            }
        });
    });

    $("#resetsrc").click(function() {
        joinsrcDt.fnClearTable();
        insertjoin(joinsrcDt, $("#srcdst").data("dst"));
    });

    $("#oksrc").click(function() {
        var n = joinsrcDt.fnSettings().fnRecordsTotal();
        joinsrcDt.fnDeleteRow(--n);
        if (n > 0) {
            var opt = joinsrcDt.$(joinsrcDt.fnGetNodes(n-1)).find("select option:selected");
            var dst = opt.val();
            var dst_name = "[" + $("#selds1 option:selected").text() + "]." + opt.text();
        } else {
            var dst = $("#srcdst").data("dst");
            var dst_name = $("#srcdst").val();
        }

        joinsrc2destDt.fnClearTable();

        var sel = '<select class="dt"></select>';
        var selc = '<select class="dt"><option value="1">1</option><option value="0">N</option></select>'
        var r = joinsrc2destDt.fnAddData([dst_name, sel, sel, sel, selc]);
        r = joinsrc2destDt.fnGetNodes(r);

        joinsrc2destDt.$(r).find("td").eq(0).data("dst", dst);
        var sel1 = joinsrc2destDt.$(r).find("select").eq(0);
        var sel2 = joinsrc2destDt.$(r).find("select").eq(1);
        var sel3 = joinsrc2destDt.$(r).find("select").eq(2);
        
        $.ajax({
            url: "./",
            data: {dst_attr: dst},
            success: function(data) {
                data = JSON.parse(data);
                for (var i = 0; i < data.length; ++i) {
                    sel1.append('<option value="' + data[i] + '">' + data[i] + '</option>');
                }
            },
            error: function(data) {
                alert("Error: failed to connect to server!");
            }
        });

        var ds2name = "[" + $("#selds2 option:selected").text() + "].";
        for (var i = 0; i < ds2data.length; ++i) {
            var opt = $('<option value="' + ds2data[i][0] + '">' + ds2name + ds2data[i][1] + '</option>');
            opt.data("attrs", ds2data[i][2]);
            sel2.append(opt);
        }
        sel2.prop("selectedIndex", -1);
        sel2.change(function() {
            if ($(this).val() == null) {
                $("option", sel3).remove();
                return;
            }
            sel3.find("option").remove();
            var attrs = $(this).find("option:selected").data("attrs");
            for (var i = 0; i < attrs.length; ++i) {
                sel3.append('<option value="'+attrs[i]+'">' + attrs[i] + '</option>');
            }
            sel3.prop("selectedIndex", -1);
        });



    });

    $("#resetsrc2dest").click(function() {
        var sel1 = joinsrc2destDt.$("select").eq(0);
        var sel2 = joinsrc2destDt.$("select").eq(1);
        var sel3 = joinsrc2destDt.$("select").eq(2);
        sel1.prop("selectedIndex", -1);
        sel2.prop("selectedIndex", -1).change();
    });

    $("#oksrc2dest").click(function() {
        var sel1 = joinsrc2destDt.$("select").eq(0);
        var sel2 = joinsrc2destDt.$("select").eq(1);
        var sel3 = joinsrc2destDt.$("select").eq(2);
        if (sel1 == null || sel2 == null || sel3 == null) {
            alert("All fields are required!", "Error");
            return;
        }
        joindestDt.fnClearTable();
        var sel2 = joinsrc2destDt.$("select").eq(1);
        insertjoin(joindestDt, sel2.val());
    });

    $("#resetdest").click(function() {
        joindestDt.fnClearTable();
        var sel2 = joinsrc2destDt.$("select").eq(1);
        insertjoin(joindestDt, sel2.val());
    });

    $("#okdest").click(function() {
        var n = joindestDt.fnSettings().fnRecordsTotal();
        
        if (n > 1) {
            var dst = joindestDt.$(joindestDt.fnGetNodes(n-2)).find("select").val();
        } else {
            var dst = joinsrc2destDt.$("select").eq(1).val();
        }

        if (dst != $("#destdst").data("dst")) {
            $("#manpathdiv").text("Path does not reach table " + $("#destdst").val())
                            .removeClass("ok")
                            .addClass("nok")
                            .data("pathok", false);
            return;
        } else {
            $("#manpathdiv").text("Path ok.")
                            .removeClass("nok")
                            .addClass("ok")
                            .data("pathok", true);
        }

        joindestDt.fnDeleteRow(--n);
    });

    $("#saveman").click(function() {
        var pathok = $("#manpathdiv").data("pathok");
        if (!pathok) {
            alert("Path is malformed. Please check and try again.", "Error");
            return;
        }
        
        if ($("#selds1").val() == $("#selds2").val()) {
            var left = JSON.stringify(joindestDt.$("option:selected").map(function() {return $(this).data("dsr")[0]}).get());
            var right = "[]";
            var bridge = "[]";
        } else {
            var left = JSON.stringify(joinsrcDt.$("option:selected").map(function() {return $(this).data("dsr")[0]}).get());
            var right = JSON.stringify(joindestDt.$("option:selected").map(function() {return $(this).data("dsr")[0]}).get());
            var bridge = JSON.stringify([
                joinsrc2destDt.$("td").eq(0).data("dst"),
                joinsrc2destDt.$("select").eq(1).val(),
                joinsrc2destDt.$("select").eq(0).val(),
                joinsrc2destDt.$("select").eq(2).val(),
                joinsrc2destDt.$("select").eq(3).val()
            ]);
        }

        var postdata = {
            man: 'man',
            name: $("#qpname").val(),
            descr: $("#qpdescr").val(),
            fromqe: $("#selqe1").val(),
            toqe: $("#selqe2").val(),
            isdefault: $("#qpdefault").is(":checked"),
            left: left,
            right: right,
            bridge: bridge
        };

        if ($("#savereverseman").prop("checked") == true) {
            postdata.saverev = true;
            postdata.revname = $("#revqpnameman").val();
            postdata.revdescr = $("#revqpdescrman").val();
            postdata.revIsdefault = $("#revqpdefaultman").is(":checked");
        }

        $.ajax({
            url: "./",
            type: "post",
            data: postdata,
            success: function(data) {
                alert("Query path saved.", "Done", "OK", function() {window.location.reload()});
            },
            error: function(data) {
                alert("Error: failed to connect to server!");
            }
        });
    });

    $("#savereverseauto").change(function() {
        var checked = $(this).prop("checked");
        $("#reversedetailauto").toggle(checked);
    });

    $("#savereverseman").change(function() {
        var checked = $(this).prop("checked");
        $("#reversedetailman").toggle(checked);
    });





}

function insertjoin(target, last) {
    $.ajax({
        url: "./",
        data: {fromdst: last},
        success: function(data) {
            data = JSON.parse(data);
            console.log(data);
            var sel = '<select class="dt"></select>';
            var r = target.fnAddData([data[0][1], "", sel, "", ""]);
            r = target.fnGetNodes(r);
            sel = target.$(r).find("select")
            for (var i = 0; i < data.length; ++i) {
                var opt = $('<option value="' + data[i][2] + '">' + data[i][3] + '</option>');
                opt.data("dsr", data[i][4]);
                sel.append(opt);
            }
            sel.prop("selectedIndex", -1);
            sel.change(function() {
                if (target.$(this).val() == null)
                    return;
                var dsr = target.$(this).children("option:selected").data("dsr");
                var tr = target.$(this).parent().parent()
                tr.children("td:nth-child(2)").text(dsr[1]);
                tr.children("td:nth-child(4)").text(dsr[2]);
                tr.children("td:nth-child(5)").html('<span class="'+ (dsr[3] == true ? 'one' : 'many') + '"></span>');
                if (tr.next().length > 0) {
                    tr.nextAll().each(function() {target.fnDeleteRow($(this).index())});
                }
                insertjoin(target, target.$(this).val());
            });
        },
        error: function(data) {
            
            alert("Error: failed to connect to server!");
        },
    });
    //target.fnAddData()
}