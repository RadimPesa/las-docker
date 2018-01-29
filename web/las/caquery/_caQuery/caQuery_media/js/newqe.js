$(function() {
    initCsrf();
    inithandlers();
    initdialog();
    initdisplay();
    initdt();
    if (qeid != null){
        refreshJoinedTables();
        refreshFilters();
        refreshOutputs();
        refreshShareable();
        $('#seldst').change();
        basedst_name = $("#seldst option:selected").text();
        $("#seldst option").not("option[value='" + basedst + "']").clone().appendTo("#jndtab_tab");
    }

});

var max_predef_list = 15;

var filter_options_disabled = [ {},
                                {multi: false, batch: true , file: true }, // predefined list
                                {multi: true,  batch: true , file: true }, // date
                                {multi: true,  batch: true , file: true }, // numeric
                                {multi: true,  batch: true,  file: true}, // genid
                                {multi: false, batch: true , file: true }, // text with autocomplete
                                {multi: true,  batch: true , file: true }, // boolean
                                {multi: true,  batch: true , file: true }, // WG
                            ];

var filter_vocab_visible = [    null,
                                true,   // predefined list
                                false,  // date
                                false,  // numeric
                                false,  // genid
                                false,  // text with autocomplete
                                true,   // boolean
                                true,  //WG
                            ];

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

function initdt() {
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

function initdisplay() {
    //$("#entthird").hide();
    if ($("#seldst").val() == null)
        $("#seldst").prop("selectedIndex", -1);
    $("#vocab").hide();
    $("#subflt2").hide();
}

function initdialog() {
    $("#newjndtab_dialog").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 500,
            title: "New joined table",
            buttons: [
                {
                    text: "Cancel",
                    click: function() {$(this).dialog("close");}
                },
                {
                    text: "OK",
                    click: function() {
                        var tgttab = $("#jndtab_tab").val();
                        var pathok = $("#jndtab_pathauto").data("pathok");
                        if (tgttab == null) {return;}
                        else if (pathok == false) {
                            alert("Please choose a different target table", "Error");
                            return;
                        }
                        // everything is ok, save joined table
                        $.ajax({
                            url: "./",
                            type: "post",
                            data: {
                                action: 'createJndTab',
                                fromDst: basedst,
                                toDst: tgttab,
                                path: JSON.stringify($("#jndtab_pathauto").data("dsr"))
                            },
                            success: function(data) {
                                console.log("Joined table created (id=" + data + ")");
                                refreshJoinedTables();
                                $("#newjndtab_dialog").dialog("close");
                            },
                            error: function(data) {
                                alert("Error: failed to connect to server!");
                            }
                        });


                    }
                }
            ]
        }
    );

    $("#newattr_dialog").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 500,
            title: "New attribute",
            buttons: [
                {
                    text: "Cancel",
                    click: function() {$(this).dialog("close");}
                },
                {
                    text: "OK",
                    click: function() {
                        var name = $("#attrname").val().trim();
                        var descr = $("#attrdescr").val();
                        var jndTab = $("#jndtab").val();
                        var dstattr = $("#attrdstattr").val();
                        var attrtype = $("#attrtype").val();
                        if (name == "" || attrdstattr == null || attrtype == null) {
                            alert("Please fill all required fields", "Error");
                            return;
                        }
                        // if predefined list or boolean, retrieve values from db
                        if (attrtype == 1 || attrtype == 6 || attrtype == 7) {
                            $("#pwcontent").text("Importing values from database, please wait...");
                            $("#plswait").dialog("open");
                            $.ajax({
                                url: "./",
                                type: "get",
                                data: {
                                    action: "getPredefValues",
                                    jndTab: jndTab,
                                    attr: dstattr,
                                    vocab: $("input[name=vocab]:checked").val()
                                },
                                success: function(data) {
                                    data = JSON.parse(data);
                                    $("#plswait").dialog("close");
                                    if (data.data.length > max_predef_list) {
                                        confirm("The selected table holds more than " + max_predef_list + " distinct values. The recommended type for this filter is 'text with autocompletion'.<br><br>Are you sure you want to create a predefined list?", "Warning", "Yes", "No", handle_list(data));
                                    } else {
                                        handle_list(data)();
                                    }
                                },
                                error: function(data) {
                                    $("#plswait").dialog("close");
                                    alert("Error: failed to connect to server!");
                                }
                            });
                        } else {
                            // else, go ahead and save filter
                            $.ajax({
                                url: "./",
                                type: "post",
                                data: {
                                    action: "createAttr",
                                    name: name,
                                    descr: descr,
                                    jndTab: jndTab,
                                    attr: dstattr,
                                    type: attrtype,
                                },
                                success: function(data) {
                                    console.log("JTAttribute created (id=" + data + ")");
                                    refreshJTAttributes();
                                    $("#newattr_dialog").dialog("close");
                                },
                                error: function(data) {
                                    alert("Error: failed to connect to server!");
                                }
                            });
                        }
                    
                    }
                }
            ]
        }
    );

    $("#viewjndtab_dialog").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 500,
            title: "View path to joined table",
            buttons: [
                {
                    text: "OK",
                    click: function() {$(this).dialog("close");}
                }
            ]
        }
    );

    $("#listdiag").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 800,
            title: "Edit predefined list",
            buttons: [
                {
                    text: "OK",
                    click: function() {

                        var name = $("#attrname").val().trim();
                        var descr = $("#attrdescr").val();
                        var jndTab = $("#jndtab").val();
                        var dstattr = $("#attrdstattr").val();
                        var attrtype = $("#attrtype").val();
                        var vocab = $("input[name=vocab]:checked").val();
                        var predefList_dst = $("#selectcolumn").data("dst");
                        var predefList_attr = $("#selectcolumn option:selected").text();

                        $("#pwcontent").text("Saving, please wait...");
                        $("#plswait").dialog("open");

                        var jtattr;

                        $.ajax({
                            url: "./",
                            type: "post",
                            data: {
                                action: "createAttr",
                                name: name,
                                descr: descr,
                                jndTab: jndTab,
                                attr: dstattr,
                                type: attrtype,
                                predefList_dst: predefList_dst,
                                predefList_attr: predefList_attr
                            },
                            success: function(data) {
                                console.log("JTAttribute created (id=" + data + ")");
                                jtattr = data;
                                var list = [];
                                var listExclude = [];
                                listDt.$("tr").each(
                                    function() {
                                        var td = $(this).find("td");
                                        if ($(td[0]).find("input").is(":checked") == true) {
                                            // take value either from textbox (user-entered) or from td
                                            var ii = $(td[1]).find("input");
                                            if (ii.length == 0)
                                                var k = $(td[1]).text();
                                            else
                                                var k = ii.val();
                                            var v = $(td[2]).find("input").val();
                                            list.push([k,v])
                                        } else {
                                            // values to exclude (will be recorded in DB so that they are not imported again)
                                            // take value either from textbox (user-entered) or from td
                                            var ii = $(td[1]).find("input");
                                            if (ii.length == 0)
                                                var k = $(td[1]).text();
                                            else
                                                var k = ii.val();
                                            listExclude.push(k);
                                        }
                                    }
                                );
                                
                                $.ajax({
                                    url: "./",
                                    type: "post",
                                    data: {
                                        action: "createValues",
                                        list: JSON.stringify(list),
                                        excludeList: JSON.stringify(listExclude),
                                        jtattr: jtattr
                                    },
                                    success: function(data) {
                                        $("#plswait").dialog("close");
                                        console.log("List saved");
                                        $("#listdiag").dialog("close");
                                        refreshJTAttributes();
                                    },
                                    error: function(data) {
                                        $("#plswait").dialog("close");
                                        alert("An error occurred");
                                    }
                                });
                            },
                            error: function(data) {
                                $("#plswait").dialog("close");
                                alert("Error: failed to connect to server!");
                            }
                        });
                    }
                }
            ],
            close: function() {
                listDt.fnClearTable();
                listDt.fnDestroy();
                $("#tlist").remove();
                $("#selectcolumn").off("change");
            }
        }
    );

    $("#plswait").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            closeOnEscape: false,
            open: function(event, ui) {
                $("#ui-dialog-title-plswait").siblings("a").remove();
            }
        }
    );

    $("#editpath").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 800,
            closeOnEscape: false,
            title: "Manual path definition",
            buttons: [
                {
                    text: "Cancel",
                    click: function() {
                        $("#editpath").dialog("close");
                    }
                },
                {
                    text: "OK",
                    click: endmanpathdef
                }
            ]
        }
    );

    $("#newflt_dialog").dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        width: 500,
        title: "New filter",
        open: function() {
            $("input[type=checkbox][name=opts]").prop("checked", false);
            $("input[type=checkbox][name=genidopts]").prop("checked", true);
            if ( $($("#attrs :selected")[0]).attr('dtype') != "4" ){
                $('#genidtypes').hide();
            }
        },
        buttons: [
            {
                text: "Cancel",
                click: function() {
                    $("#newflt_dialog").dialog("close");
                }
            },
            {
                text: "OK",
                // button to save filter and close filter definition window 
                click: function() {
                    var jta = $("#attrs").val();
                    var opts = $("input[type=checkbox][name=opts]:checked:enabled")
                                .map(function() {
                                    return $(this).val();
                                })
                                .get();
                    var genidtypes = $("input[type=checkbox][name=genidopts]:checked:enabled").map(function() {
                                    return $(this).val();
                                    })
                                    .get();
                    console.log(genidtypes);
                    if (genidtypes.length == 0){
                        alert("Please select at least one entity type", "Error");
                        return;
                    }
                    $.ajax({
                        url: "./",
                        type: "post",
                        data: {
                            action: "createFlt",
                            jta: jta[0],
                            qe: qeid,
                            opts: JSON.stringify(opts),
                            genidtypes: JSON.stringify(genidtypes)
                        },
                        traditional: true,
                        success: function(data) {
                            console.log("Filter created (id=" + data + ")");
                            refreshFilters();
                            $("#newflt_dialog").dialog("close");
                        },
                        error: function(data) {
                            alert("Error: failed to connect to server!");
                        }
                    });
                }
            }
        ]
    });

    $("#newout_dialog").dialog(
        {
            autoOpen: false,
            modal: true,
            resizable: false,
            width: 500,
            title: "Edit output",
            open: function(event, ui) {
                $("#outfnname").val("");
                if ($("#attrs").val().length > 1) {
                    $("#outname").val("");
                } else {
                    $("#outname").val($("#attrs option:selected").text());
                }
                $("#outattrs option").remove();
                $("#attrs option:selected").clone().appendTo("#outattrs");
            },
            buttons: [
                {
                    text: "Cancel",
                    click: function() {
                        $(this).dialog("close");
                    }
                },
                {
                    text: "OK",
                    click: function() {
                        var outname = $("#outname").val().trim();
                        var fnname = $("#outfnname").val().trim();
                        var jta_list = $("#outattrs option")
                                        .map(function() {
                                            return $(this).val();
                                        })
                                        .get();
                        $.ajax({
                            url: "./",
                            type: "post",
                            data: {
                                action: "createOut",
                                qe: qeid,
                                outname: outname,
                                fnname: fnname,
                                jta: JSON.stringify(jta_list)
                            },
                            success: function(data) {
                                console.log("Output created (id=" + data + ")");
                                $("#newout_dialog").dialog("close");
                                refreshOutputs();
                            },
                            error: function(data) {
                                alert("Error: failed to connect to server!");
                            }
                        });


                    }
                }
            ]
        }
    );

    $("#subflt_dialog").dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        width: 800,
        title: "Edit subfilters",
        buttons: [
            {
                text: "Cancel",
                click: function() {
                    $(this).dialog("close");
                }
            },
            {
                text: "OK",
                click: function() {
                    var list = subfltDt.$("input[type=checkbox]:checked")
                                            .parent()
                                            .parent()
                                            .map(function() {
                                                return [
                                                    $(this).children("td:eq(1)").find("span").data("id"),
                                                    $(this).children("td:eq(2)").find("select").val()
                                                    ]
                                            });
                    if (list.length == 0) {
                        $(this).dialog("close");
                        return;
                    }
                    var list1 = [];
                    for (j=0; j<list.length; j+=2) {
                        list1.push([list[j], list[j+1]]);
                    }
                    var jta = $("#attrs").val()[0];
                    var parflt = $("#filters").val()[0];
                    var opts = [];
                    $.ajax({
                        url: "./",
                        type: "post",
                        data: {
                            action: "createFlt",
                            jta: jta,
                            qe: qeid,
                            opts: JSON.stringify(opts),
                            parflt: parflt,
                            list: JSON.stringify(list1)
                        },
                        traditional: true,
                        success: function(data) {
                            console.log("Filter created (id=" + data + ")");
                            refreshFilters();
                            refreshJTAttributes();
                            $("#subflt_dialog").dialog("close");
                        },
                        error: function(data) {
                            alert("Error: failed to connect to server!");
                        }
                    });
                }

            }
        ],
        close: function() {
            subfltDt.fnClearTable();
            subfltDt.fnDestroy();
            $("#subflttab").remove();
        }
    });

}

function inithandlers() {
    // button to create new entity
    $("input[name='genid']").change(function() {
        if ($(this).val() == "yes") {
            var dst = $("#seldst").val();
            if (dst != null) {
                $.ajax({
                    url: "./",
                    data: {
                        action: 'getGenidField',
                        dst: dst
                    },
                    success: function(data) {
                        data = JSON.parse(data);
                        var sel = $("#selgenid");
                        sel.children().remove();
                        var col = data.columns;
                        for (var j = 0; j < col.length; ++j) {
                            sel.append("<option value='"+col[j]+"'>"+col[j]+"</option>");
                        }
                        if (data.default) {
                            sel.children("[value='"+data.default+"']").prop("selected", true);
                        } else {
                            sel.prop("selectedIndex", -1);
                        }
                    },
                    error: function(data) {
                        alert("Error: failed to connect to server!");
                    }
                });
            }
            $("#genidfield").show();
        } else {
            $("#genidfield").hide();
        }
    });

    $("#create").click(
        function() {
            var ds = $("#ds").val();
            var name = $("#qename").val().trim();
            var descr = $("#qedescr").val();
            var dst = $("#seldst").val();
            var genid = $("input[name=genid]:checked").val();
            var genidfield = $("#selgenid").val();
            if (name == '' || dst == null || (genid == 'yes' && genidfield == null)) {
                alert("Please fill all required fields", "Error")
                return;
            }
            $.ajax({
                url: "./",
                type: "post",
                data: "action=createqe&dst="+dst+"&name="+name+"&descr="+descr+"&genid="+genid+"&genidfield="+genidfield,
                success: function(data) {
                    console.log("Entity created (id=" + data + ")");
                    qeid = data;
                    basedst = dst;
                    basedst_name = $("#seldst option:selected").text()
                    $("#qename").prop("disabled", true);
                    $("#qedescr").prop("disabled", true);
                    $("#seldst").prop("disabled", true);
                    $("#create").prop("disabled", true);
                    $("input[type=radio][name=genid]").prop("disabled", true);
                    $("#finish").prop("disabled", false);
                    $("#entsecond").fadeIn("slow");
                    refreshJoinedTables();
                    $("#seldst option").not("option[value='" + dst + "']").clone().appendTo("#jndtab_tab");
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
        }
    );

    $("#finish").click(
        function() {
            if ($("#outputs option").length == 0) {
                alert("Please define at least one output for the current entity", "Error")
            } else {
                $("#qe").val(qeid);
                $("#qe_name").val($('#qename').val());
                $("#qe_description").val($('#qedescr').val());
                $("#qeform").submit();
            }
        }
    );
  

    $("#seldst").change(
        function(){
            $("#viewdst").prop("href", tablebrowser_url + "?dst=" + $("#seldst").val());
            $("input[name='genid']:checked").change();
        }
    );

 

    $("#attrtype").change(
        function() {
            var atype = $("#attrtype").val();
            if (atype == null) {
                $("#vocab").hide();
                return;
            }
            var ops = filter_options_disabled[atype];
            for (var i in ops) {
                $("#" + i).prop("disabled", ops[i]);
                $("label[for=" + i +"]").toggleClass("disabled", ops[i]);
            }
            $("#vocab").toggle(filter_vocab_visible[atype]);
            
            if ($("#attrtype").val() == 6) {
                $("input[name=vocab]").eq(1).prop("checked", true);
            } else {
                $("input[name=vocab]").eq(0).prop("checked", true);
            }
        }
    );

    $("#fltbatch").change(
        function() {
            if ($("#fltbatch").is(":checked")) {
                $("#fltmulti").prop("checked", true);
            }
        }
    );

    $("#fltmulti").change(
        function() {
            if (!$("#fltmulti").is(":checked")) {
                $("#fltbatch").prop("checked", false);
            }
        }
    );

    

    $("#resetdest").click(function() {
        joindestDt.fnClearTable();
        insertjoin(joindestDt, $("#srcdst").data("dst"));
    });

    $("#fltmanpath").click(function() {
        var toDst = $("#flttgttab").val();
        if (toDst == null) {
            return;
        }
        startmanpathdef($("#seldst").val(), $("#seldst option:selected").text(), toDst, $("#flttgttab option:selected").text(), $("#pathdiv"));
    });

    $("#jndtab_pathman").click(function() {
        var toDst = $("#jndtab_tab").val();
        if (toDst == null) {
            return;
        }
        startmanpathdef(basedst, basedst_name, toDst, $("#jndtab_tab option:selected").text(), $("#jndtab_pathauto"));
    });

    $("#newjndtab").click(function() {
        $("#jndtab_tab").prop("selectedIndex", -1);
        $("#jndtab_pathauto").children().remove();
        $("#newjndtab_dialog").dialog("open");
    });

    $("#jndtab_tab").change(function() {
        var dst = $("#jndtab_tab").val();
        if (dst == null) return;
        $.ajax({
            url: "./",
            data: "action=getPath&fromdst="+basedst+"&todst="+dst,
            success: function(data) {
                data = JSON.parse(data);
                $("#jndtab_pathauto").children().remove();

                if (data.path == null) {
                    $("#jndtab_pathauto").data("pathok", false);
                    $("#jndtab_pathauto").append('<p class="path" style="color: red">There is no path available</p>');
                } else {
                    $("#jndtab_pathauto").data("pathok", true);
                    $("#jndtab_pathauto").data("dsr", data.dsr);
                    $("#jndtab_pathauto").append("<ol></ol>")
                    for (i = 0; i < data.path.length; ++i) {
                        $("#jndtab_pathauto ol").append('<li><a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + data.path[i][0] + '">' + data.path[i][1] + '</a>.' + data.path[i][2] +' &rarr; <a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + data.path[i][3] + '">' + data.path[i][4] + '</a>.' + data.path[i][5] + '<span class="'+ (data.path[i][6] == true ? 'one' : 'many') + '"></span></li>');
                    }
                }
            },
            error: function(data) {
                alert("Error: failed to connect to server!");
            }
        });

    });

    $("#deljndtab").click(function() {
        var id = $("#jndtab").val();
        if (id == null) return;

        confirm("Do you really want to delete this joined table?", "Confirm", "Yes", "No", function() {
            $.ajax({
                url: "./",
                data: {
                    action: 'delJndTab',
                    jndtab: id,
                    qe: qeid
                },
                type: "POST",
                success: function(data) {
                    refreshJoinedTables();
                    refreshJTAttributes();
                    refreshFilters();
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    });


    $("#viewjndtab").click(function() {
        var opt = $("#jndtab option:selected");
        if (opt == null) return;

        var el = $("#viewjndtab_dialog div ol");
        el.children().remove()
        var path = opt.data("path");
        for (i = 0; i < path.length; ++i) {
            el.append('<li><a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + path[i][0] + '">' + path[i][1] + '</a>.' + path[i][2] +' &rarr; <a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + path[i][3] + '">' + path[i][4] + '</a>.' + path[i][5] + '<span class="'+ (path[i][6] == true ? 'one' : 'many') + '"></span></li>');
        }

        if (path.length == 0) {
            el.append("<span>(not applicable)</span>")
        }
        $("#viewjndtab_dialog").dialog("open");
    });

    $("#newattr").click(function() {
        if ($("#jndtab").val() == null) return;
        $("#attrname").val("");
        $("#attrdescr").val("");
        $("#attrtype").prop("selectedIndex", -1).change();
        $("#newattr_dialog").dialog("open");

    });

    $("#jndtab").change(function() {
        refreshJTAttributes();

        var v = $("#jndtab").val();
        if (v == null) return;
        $.ajax({
            url: "./",
            data: {
                action: 'getAttrs',
                jndTab: v
            },
            success: function(data) {
                data = JSON.parse(data);
                var sel = $("#attrdstattr");
                sel.children().remove();
                for (var j = 0; j < data.length; ++j) {
                    sel.append("<option value='"+data[j]+"'>"+data[j]+"</option>");
                }
            },
            error: function(data) {
                alert("Error: failed to connect to server!");
            }
        });

    });

    $("#delattr").click(function() {
        var a = $("#attrs").val();
        if (a == null) return;
        confirm("Do you really want to delete this attribute?", "Confirm", "Yes", "No", function() {
            $.ajax({
                url: "./",
                data: {
                    action: 'delJTAttr',
                    jtattr: a[0],
                    qe: qeid
                },
                type: "POST",
                success: function(data) {
                    refreshJTAttributes();
                    refreshFilters();
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    });

    $("#addflt").click(function() {
        if ($("#attrs").val() != null) {
            $("#newflt_dialog").dialog("open");
        }
    });

    $("#addout").click(function() {
        if ($("#attrs").val() != null) {
            $("#newout_dialog").dialog("open");
        }
    });

    $("#delflt").click(function() {
        var f = $("#filters").val();
        console.log(f);
        if (f == null) return;
        confirm("Do you really want to delete this filter?", "Confirm", "Yes", "No", function() {
            $.ajax({
                url: "./",
                data: {
                    action: 'delFilter',
                    f: JSON.stringify(f)
                },
                type: "POST",
                success: function(data) {
                    refreshFilters();
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    });

    $("#delout").click(function() {
        var o = $("#outputs").val();
        console.log(o)
        if (o == null) return;
        confirm("Do you really want to delete this output?", "Confirm", "Yes", "No", function() {
            $.ajax({
                url: "./",
                data: {
                    action: 'delOutput',
                    o: JSON.stringify(o)
                },
                type: "POST",
                success: function(data) {
                    refreshOutputs();
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    });

    $("#shareout").click(function() {
        if ($("#outputs").val().length > 1){
            alert('Only one output can be used to share');
            return;
        }
        var o = $("#outputs").val()[0];
        var oname = $("#outputs :selected").text();
        console.log(o)
        if (o == null) return;
        confirm("Do you really want to make the entity shareable based on this output ("+ oname + ")? Previous share definition will be overwritten.", "Confirm", "Yes", "No", function() {
            $.ajax({
                url: "./",
                data: {
                    action: 'shareOutput',
                    o: JSON.stringify(o)
                },
                type: "POST",
                success: function(data) {
                    refreshShareable();
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    });


    $("#unshare").click(function() {
        
        confirm("Do you really want to make the entity unshareable ?", "Confirm", "Yes", "No", function() {
            $.ajax({
                url: "./",
                data: {
                    action: 'unshare',
                    qe: qeid
                },
                type: "POST",
                success: function(data) {
                    refreshShareable();
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    });

    $("#attrup").click(function() {
        var a = $("#outattrs option:selected");
        if (a == null) return;
        a.prev().before(a);
    });

    $("#attrdown").click(function() {
        var a = $("#outattrs option:selected");
        if (a == null) return;
        a.next().after(a);
    });

    $("#addsubflt").click(function() {
        var attrs = $("#attrs").val();
        var l = $("#filters option").length;
        if (attrs == null || l == 0) return;
        $("#subflt2").show('slide', {direction: 'right'}, 400);
        $("#jndtab,#attrs,#outputs").prop("disabled", true);
        $("button.btn1").prop("disabled", true);
        $("#filters option").click(function() {
            var f = $("#filters").val();
            $("#subflt2").hide();
            $("#jndtab,#attrs,#outputs").prop("disabled", false);
            $("button.btn1").prop("disabled", false);
            $("#filters option").off("click");

            $.ajax({
                url: "./",
                data: {
                    action: "getFilterValues",
                    flt: f[0]
                },
                async: false,
                success: function(data) {
                    data = JSON.parse(data);
                    if (data.length == 0) {
                        alert("No predefined values are available for this filter.", "Cannot continue");
                        return;
                    }
                    handleSubFlt(data);
                },
                error: function(data) {
                    alert(data.responseText, "Unable to complete operation");
                }
            });
        });
    })

}

function handleSubFlt(data) {
    $("#subflt_dialog").append("<table id='subflttab' style='width: 95%'></table>");
    var aoColumns = [
        {
            sWidth: "1%",
            sClass: "centered"
        },
        {
            sWidth: "25%",
            sTitle: "Value",
            sClass: "centered"
        },
        {
            sWidth: "73%",
            sTitle: "Subfilter type",
            sClass: "centered"
        }
    ];

    var sel = $("<select class='edit'></select>");
    $("#attrtype option[data-subflt=True]").clone().appendTo(sel);
    subfltDt = $("#subflttab").dataTable({
        bFilter: false,
        bLengthChange: false,
        bSort: false,
        bAutoWidth: true,
        aoColumns: aoColumns
    }); 
    for (var j=0; j < data.length; ++j) {
        subfltDt.fnAddData(['<input type="checkbox" checked="checked">',
                            '<span data-id="'+data[j][0]+'">'+data[j][1]+'</span>']
                            .concat(sel.clone()[0].outerHTML)
                        );
    }

    $("#subflt_dialog").dialog("open");

}

function refreshJTAttributes() {
    var v = $("#jndtab").val();
    $("#attrs").children().remove();
    if (v == null) return;
    $.ajax({
        url: "./",
        data: "action=getJtAttrs&jndTab="+v,
        async: false,
        success: function(data) {
            data = JSON.parse(data);
            var sel = $("#attrs");
            for (var j = 0; j < data.length; ++j) {
                sel.append("<option value='"+data[j][0]+"' dtype='"+ data[j][2] +"'>"+data[j][1]+"</option>");
            }
        },
        error: function(data) {
            alert("Error: failed to connect to server!");
        }
    });
}

function refreshJoinedTables() {
    $.ajax({
        url: "./",
        data: "action=getJndTab&dst="+basedst,
        success: function(data) {
            data = JSON.parse(data);
            $("#jndtab option").remove();
            for (i = 0; i < data.length; ++i) {
                $("#jndtab").append('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
                $("#jndtab option:last").data("path", data[i][2]);
                $("#jndtab option:last").data("baseTable", data[i][3]);
            }
        },
        error: function(data) {
            alert("Error: failed to connect to server!");
        }
    });
}

function handle_list(list) {
    return function() {

        $("#newattr_dialog").dialog("close");

        $("#listdiag").append("<table id='tlist' style='width: 95%''></table>");

        var aoColumns = [
            {
                sWidth: "1%",
                sClass: "centered"
            },
            {
                sWidth: "28%",
                sTitle: "Database value",
                sClass: "centered"
            },
            {
                sWidth: "69%",
                sTitle: "Displayed value",
                sClass: "centered"
            }
        ];
        
        $("#selectcolumn").children().remove();

        for (var j = 1; j < list.headers.length; ++j) {
            $("#selectcolumn").append("<option value='"+j+"'>"+list.headers[j]+"</option>");
        }
        $("#selectcolumn").data("dst", list.dst);

        listDt = $("#tlist").dataTable({
            bFilter: false,
            bLengthChange: false,
            bSort: false,
            bAutoWidth: true,
            aoColumns: aoColumns
        });


        //load data into table
        listDt.fnClearTable();
        for (var i = 0; i < list.data.length; ++i) {
            listDt.fnAddData(['<input type="checkbox" checked="checked">']
                                .concat(list.data[i][0])
                                .concat(list.data[i].slice(1,2).map(function(x) {return '<input style="width: 90%; margin: 0px" type="text" class="dispval" value="'+x+'"><span class="fa fa-unlock-alt iconlock"></span>';}))
                            );

        }
        // if boolean, make sure there are two possible values
        if ($("#attrtype").val() == 6) {
            if (list.data.length < 2) {
                var n = 2 - list.length;
                for (var i = 0; i < n; ++i) {
                    listDt.fnAddData(['<input style="width: 98%; margin: 0px" type="text" placeholder="(fill missing)">', '<input style="width: 98%; margin: 0px" type="text" class="dispval" placeholder="(fill missing)"><span class="fa fa-unlock-alt iconlock"></span>']);
                }
            }
        }
        
        listDt.$("input.dispval").each(function() {
            $(this).data("locked", false);
        });

        $("#selectcolumn").change(function() {
            var selCol = $("#selectcolumn").val();
            if (selCol == null) return;
            var inputs = listDt.$("input.dispval");
            for (var j = 0; j < inputs.length; ++j) {
                if ($(inputs[j]).data("locked") == false) {
                    $(inputs[j]).val(list.data[j][selCol]);
                }
            }
        });

        listDt.$("span.iconlock").click(function() {
            if ($(this).hasClass("fa-unlock-alt")) {
                $(this).removeClass("fa-unlock-alt").addClass("fa-lock");
                $(this).siblings("input").data("locked", true);
            } else {
                $(this).removeClass("fa-lock").addClass("fa-unlock-alt");
                $(this).siblings("input").data("locked", false);
            }
        });

        $("#listdiag").dialog("open");
    }
}

// refresh filters displayed in main window
function refreshFilters() {
    $.ajax({
        url: "./",
        data: {
            action: "getFilters",
            qe: qeid,
        },
        success: function(data) {
            data = JSON.parse(data);
            $("#filters option").remove();
            for (i = 0; i < data.length; ++i) {
                $("#filters").append('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
                if (data[i][2] != null) {
                    $("#filters").append('<option value="' + data[i][3].join() + '">&nbsp;&#8627;&nbsp;' + data[i][2] + '</option>');
                    $("#filters option:last").data("isList", true);
                }
            }
        },
        error: function(data) {
            alert("Error: failed to connect to server!");
        }
    });
}

// refresh outputs displayed in main window
function refreshOutputs() {
    $.ajax({
        url: "./",
        data: {
            action: "getOutputs",
            qe: qeid
        },
        success: function(data) {
            data = JSON.parse(data);
            $("#outputs option").remove();
            for (i = 0; i < data.length; ++i) {
                $("#outputs").append('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
            }
        },
        error: function(data) {
            alert("Error: failed to connect to server!");
        }
    });
}


function refreshShareable(){
    $.ajax({
        url: "./",
        data: {
            action: "getShare",
            qe: qeid
        },
        success: function(data) {
            data = JSON.parse(data);
            if (data['shareable'] == true){
                $('#shareable').show();
                $('#shareable input').val(data['output']);
                $('#unshare').show();
            }
            else{
                $('#shareable').hide();
                $('#unshare').hide();
            }   
        },
        error: function(data) {
            alert("Error: failed to connect to server!");
        }
    });
}



function startmanpathdef(fromDst, fromDstName, toDst, toDstName, tgtEl) {
    $("#srcdst").val(fromDstName).data("dst", fromDst);
    $("#destdst").val(toDstName).data("dst", toDst);
    joindestDt.fnClearTable();
    insertjoin(joindestDt, fromDst);
    $("#manpathdiv").text("");
    $("#editpath").data("tgtEl", tgtEl);
    $("#editpath").dialog("open");
}

function endmanpathdef() {
    var n = joindestDt.fnSettings().fnRecordsTotal();
    var dst = joindestDt.$(joindestDt.fnGetNodes(n-2)).find("select").val();
    if (dst != $("#destdst").data("dst")) {
        alert("Path does not reach table " + $("#destdst").val(), "Error");
        return;
    }
    joindestDt.fnDeleteRow(--n);

    var tgtEl = $("#editpath").data("tgtEl");
    tgtEl.children().remove();

    tgtEl.data("pathok", true);
    tgtEl.data("dsr", joindestDt.$("option:selected").map(function() {return $(this).data("dsr")[0]}).get())
    tgtEl.append("<ol></ol>")
    joindestDt.$("tr:eq(0)").children("td:eq(0)").data("dst", $("#srcdst").data("dst"))
    joindestDt.$("select.dt").each(function() {
        var fromDstName = $(this).parent().parent().children("td:eq(0)").text();
        var fromAttr = $(this).parent().parent().children("td:eq(1)").text();
        var fromDst = $(this).parent().parent().children("td:eq(0)").data("dst");
        var toDstName = $(this).children("option:selected").text();
        var toAttr = $(this).parent().parent().children("td:eq(3)").text();
        var toDst = $(this).children("option:selected").val();
        var span = $(this).parent().parent().children("td:eq(4)").html();
        tgtEl.find("ol").append('<li><a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + fromDst + '">' + fromDstName + '</a>.' + fromAttr +' &rarr; <a class="path" target="_blank" href="'+tablebrowser_url + '?dst=' + toDst + '">' + toDstName + '</a>.' + toAttr + span +'</li>');
        $(this).parent().parent().next().children("td:eq(0)").data("dst", toDst);
    });

    $("#editpath").dialog("close");

}

function insertjoin(target, last) {
    $.ajax({
        url: "./",
        data: {action: 'reachFromDst', dst: last},
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
}