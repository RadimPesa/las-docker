/**
 * ... provides classes to ...
 * @module ...
 */
/**
 * @class ...
 * @static
 * @namespace ...
 */
$(function() {
    initGenidDialog();
    initGenidHandler();
}); 
    
function initGenidDialog() {

    $("#geniddialog").dialog({
        autoOpen: false,
        modal: true,
        width: 1050,
        beforeclose: function(event, ui) {
            $("#fullgenid").boxlist("clearValues");
            $("table#genid").children("tbody").children("tr").children("td").children("input").val("");
            $("table#genid").children("tbody").children("tr").children("td").children("select").val("");
            $("#fullgenid").val("");
        }, 
        buttons: 
        [
            {
                text: "Clear all values",
                click: function() {
                    $("#genidlist").children().remove();
                }
            },
            {
                text: "Ok",
                click: function() {
                    $(this).dialog("close");
                }
            }
        ] 
    });
    
    $("#fullgenid").boxlist({
        bMultiValuedInput: true,
        oBtnEl: $("#add_gid2"),
        oContainerEl: $("#genidlist"),
        fnEachParseInput: function(v) {
            v = v.trim();
            if (v.length == 0) {
                return v;
            } else if (v.length < 26) {
                v = v + new Array(26 - v.length + 1).join("-");
            } else if (v.length > 26) {
                v = v.substr(0, 26);
            }
            return v.toUpperCase();
        },
        fnValidateInput: function(val) {
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
                }
                
                if (ok && (f.end == 25 || /^[\-0]+$/.test(val.substr(f.end+1,26)))) {
                    console.log("Detected type:", t);
                    break;
                }

            }
            console.log("[validate genid]", ok);
            return ok;
        },

        aoAltInput: [
            {
                oBtnEl: $("#add_gid"),
                fnParseInput: genIdFromForm
            }
        ]
    });


    $("#genidfile").change(function() {
        var r = new FileReader();
        r.onload = function(evt) {
            $("#fullgenid").val(evt.target.result);
            $("#add_gid2").click();
            $("#genidfrm")[0].reset();
        }
        r.readAsText($("#genidfile")[0].files[0]);
    });
};

function initGenidHandler() {
    $("#selgenidtype").change(function() {
        var t = $("#selgenidtype").val();
        try {
            var fields = genid[t].fields;
        }
        catch(err) {
            return;
        }
        $("table#genid th.field,table#genid td.field").remove();
        for (var i = 0; i < fields.length; ++i) {
            $('<th class="field">' + fields[i].name + '</th>').insertBefore("table#genid th.add");
            if (fields[i].ftype == 1) {
                var x = '<td class="field"><select class="genidpar2" maxlength="' + (fields[i].end - fields[i].start + 1)+'">';
                x += '<option></option>';
                for (var j = 0; j < fields[i].values.length; ++j) {
                    x += '<option>' + fields[i].values[j] + '</option>';
                }
                x += '</select></td>';
            } else

            if (fields[i].ftype == 2 || fields[i].ftype == 3 || fields[i].ftype == 4) {
                var x = '<td class="field"><input type="text" class="genidpar2" maxlength="' + (fields[i].end - fields[i].start + 1)+ '" onkeypress="validate3(event)"></td>';
            }
            $(x).insertBefore("table#genid td.add");
        }
    });

    $("#selgenidtype").prop("selectedIndex", 0).change();
};


var QueryGen = {

    clickedButton   : null,
    template_id     : null,
    block_id        : 1,
    boxdone         : [],
    jsonStrGraph    : {},
    startName       : '',
    endName         : '',
    correlationElements: [
        null,
        null,
        "<span style='display: inline-block'><input class='correlated rangeFrom' type='text' readonly /><span class='correlated'>+</span><input type='number' value='0' step='1' class='correlated rangeTo' /><span class='correlated'>days</span></span>",
        "<span style='display: inline-block'><input class='correlated rangeFrom' type='text' readonly /><span class='correlated'>+</span><input type='number' value='0' step='1' class='correlated rangeFrom' /></span>",
        "<span style='display: inline-block'><input class='correlated' type='text' readonly /></span>",
        "<span style='display: inline-block'><input class='correlated' type='text' readonly /></span>"
    ],

    //gbItem : '<p class="gbitem"><select class="op"><option value="COUNT">COUNT</option><option value="SUM">SUM</option><option value="MIN">MIN</option><option value="MAX">MAX</option><option value="AVG">AVG</option></select><select></select><select class="rangeFrom"><option value=">"> &#x2265; </option><option value="="> = </option><option value="<"> &#x2264; </option></select><input type="number" step="0.1" class="rangeFrom" /><span id="trattino"> - </span><select class="rangeTo"><option value="<"> &#x2264; </option></select><input type="number" step="0.1" class="rangeTo" /><span class="ui-icon ui-icon-closethick gbitemdel"></span></p>',

    gbItem : '<p class="gbitem"><select class="op"><option value="COUNT">COUNT</option><option value="SUM">SUM</option><option value="MIN">MIN</option><option value="MAX">MAX</option><option value="AVG">AVG</option></select><select></select><select class="rangeFrom"><option value=">"> &#x2265; </option><option value="="> = </option><option value="<"> &#x2264; </option></select><input class="rangeFrom" /><span id="trattino"> - </span><select class="rangeTo"><option value="<"> &#x2264; </option></select><input class="rangeTo" /><span class="ui-icon ui-icon-closethick gbitemdel"></span></p>',

    gbOut : '<p class="gbitem"><select class="op"><option value="COUNT">COUNT</option><option value="SUM">SUM</option><option value="MIN">MIN</option><option value="MAX">MAX</option><option value="AVG">AVG</option></select><select></select></span><label style="margin-left: 30px">Name:</label><input type="text" /><span class="ui-icon ui-icon-closethick gbitemdel"></p>',

    template: {
        blocks: [],
        curr_block_id: 0,
        base_query: null,
        conf: {},
        in_template: false,
    },
    
    getGraphSize: function() {
        var c = 0, i;
        for (i in QueryGen.jsonStrGraph) {
            if (QueryGen.jsonStrGraph.hasOwnProperty(i)) ++c;
        }
        return c;
    },

    saveAsTranslator: function() {
        QueryGen.template.base_query = QueryGen.generateQueryDict();
        if (QueryGen.template.base_query == null)
            return;
    
        QueryGen.template.blocks = [];
        for (var x in QueryGen.jsonStrGraph) {
            if (x == 'start' || x == 'end')
                continue;
            var b = QueryGen.jsonStrGraph[x];
            // if it is an entity or a configurable operator (i.e. group by or genealogy id) except the extend operator or a configurable template
            if (b.button_cat == 'qent' || b.button_cat == 'op' && b.button_id != 7 && ((b.button_id != 6 && ops[b.button_id].configurable == true) || (b.button_id == 6 && templates[b.template_id].parameters.length > 0))) {
                QueryGen.template.blocks.push(b);
                QueryGen.generateTemplate(b);
                
            }
        }

        QueryGen.template.curr_block_id = 0;
        $("#stf_isTranslator").val("true");

        QueryGen.submitTemplate();

    },

    submitTemplate: function() {
        // regenerate query from scratch
        QueryGen.template.base_query = QueryGen.generateQueryDict();

        // save current configuration
        for (var x in QueryGen.template.conf) {
            QueryGen.saveToTemplate(x);
        }
        // check if an option has been specified for each parameter in each block
        var res = QueryGen.checkTemplate();
        if (res == -1) {
            alert("Please specify an option for all template parameters.", "Cannot continue");
            return;
        } else
        if (res == -2) {
            alert("Please provide a name, and optionally a description, for all template parameters left blank.", "Cannot continue");
            return;
        } else
        if (res == -3) {
            alert("Please provide a value for all template parameters that must be locked to the current value.", "Cannot continue");
            return;
        }

        // check if a title has been provided
        var title = $("#query_title").val().trim();
        var description = $("#query_description").val().trim();
        if (title == "") {
            alert("Please provide a title for the template. A concise description, although not mandatory, is recommended.");
            return;
        }

        var ctrl = getBusyOverlay("viewport", {color:'#B2B2B2', opacity:0.3, text:'Saving template, please wait...', style: 'color: #222222;'}, {color:'#222222', weight:'3', size:100, type:'rectangle', count:12});

        // check if template name is already in use
        $.ajax({
            url: $("#submit_template_frm").attr("action"),
            data: "check_template_name="+title + "&tqid=" + tqid + "&transid=" + transid,
            success: function(data) {
                data = JSON.parse(data);
                if (data == true) {
                    ctrl.remove();
                    alert("The template name you chose is already in use. Please choose a different name.");
                } else {
                    QueryGen.postProcessTemplate();
                    QueryGen.template.base_query.graph_nodes = JSON.stringify(QueryGen.template.base_query.graph_nodes);
                    $("#stf_title").val(title);
                    $("#stf_description").val(description);
                    $("#stf_base_query").val(QueryGen.template.base_query.graph_nodes);
                    $("#stf_conf").val(JSON.stringify(QueryGen.template.conf));
                    if (tqid){
                        $("#stf_idtemplate").val(tqid);
                    }
                    if (transid){
                        $("#stf_idtemplate").val(transid);
                    }
                    console.log(QueryGen.template.base_query.graph_nodes);
                    console.log(JSON.stringify(QueryGen.template.conf));
                    $("#submit_template_frm").submit();
                }
            },
            error: function(data) {
                alert("Error: failed to connect to server!");
            }
        });

    },

    postProcessTemplate: function() {
        var templ_param_id = 0;
        for (var block_id in QueryGen.template.conf) {
            var block = QueryGen.template.base_query.graph_nodes[block_id];
            var blockParams = QueryGen.template.conf[block_id].parameters;
            for (var param_id in blockParams) {
                if (blockParams[param_id].opt == 2) {
                    if (block.button_cat == 'qent') {
                        // each free qent parameter must be added to the corresponding block's param. list, if not already in the list, and it must have no value
                        var thisParam = block.parameters.filter(function(e) {return e.f_id == param_id});
                        if (thisParam.length > 0) {
                            thisParam[0].values = []
                        } else {
                            block.parameters.push({
                                f_id: param_id,
                                values: []
                            });
                        }
                    } else

                    if (block.button_cat == 'op') {
                        if (block.button_id == '4') { // group by
                            // each free gb parameter has been defined by the user with an associated value, which must be cleared
                            var thisParam = block.parameters.filter(function(e) {return e.uid == param_id})[0];
                            thisParam.values = [];
                        } else

                        if (block.button_id == '5') { // genealogy id
                            // values must be cleared for a free genealogy id parameter
                            block.parameters[0].values = [];
                        } else

                        if (block.button_id == '6') { // template
                            // each free template parameter must be added to the corresponding block's param. list, if not already in the list, and it must have no value
                            var thisParam = block.parameters.filter(function(e) {return e.f_id == param_id});
                            if (thisParam.length > 0) {
                                thisParam[0].values = []
                            } else {
                                block.parameters.push({
                                    f_id: param_id,
                                    values: []
                                });
                            }
                        }
                    }
                } else

                if (blockParams[param_id].opt == 3) {
                    // subfilter values (if any) must be removed from the query
                    var thisParam = block.parameters.filter(function(e) {return e.f_id == param_id});
                    delete thisParam[0].subvalues;
                }

            }
            var newBlockParams = {};
            for (var param_id in blockParams) {
                if (blockParams[param_id].opt == 0)
                    continue;

                var index;
                if (block.button_cat == 'qent') {
                    // find index of object that has f_id == param_id
                    for (index = 0; index < block.parameters.length && block.parameters[index].f_id != param_id; ++index);
                } else

                if (block.button_cat == 'op') {
                    if (block.button_id == '4') { // group by
                        // find index of object that has uid == param_id
                        index = blockParams[param_id].index;
                        // delete "index" property which is no longer needed
                        delete blockParams[param_id].index;
                    } else

                    if (block.button_id == '5') { // genealogy id
                        // index is 0
                        index = 0;
                    } else

                    if (block.button_id == '6') { //template
                        // find index of object that has f_id == param_id
                        for (index = 0; index < block.parameters.length && block.parameters[index].f_id != param_id; ++index);
                    }
                }
                newBlockParams[index] = $.extend(blockParams[param_id], blockParams[param_id].opt != 1 ? {templ_param_id: templ_param_id++}:{}); // if opt == 1, param is locked to current value, hence it is not an actual template parameter
            }
            QueryGen.template.conf[block_id].parameters = newBlockParams;
        }
    },

    checkTemplate: function() {
        // check if an option has been specified for each parameter
        for (var b_id in QueryGen.template.conf) {
            var f_list = QueryGen.template.conf[b_id].parameters;
            for (var f_id in f_list) {
                if (f_list[f_id].opt == -1) {
                    return -1;
                } else

                if (f_list[f_id].opt == 2 && f_list[f_id].name == "") {
                    return -2;
                } else

                if (f_list[f_id].opt == 1 || f_list[f_id].opt == 3) {
                    // check if "lock" or lock main" has been selected but no values have been provided for the filter
                    var thisParam = QueryGen.template.base_query.graph_nodes[b_id].parameters.filter(function(e) {return (e.f_id != undefined? e.f_id : (e.uid != undefined ? e.uid : e.param_name)) == f_id});
                    if (thisParam.length == 0 || thisParam[0].values == undefined || thisParam[0].values.length == 0) {
                        return -3;
                    }
                }
            }
        }
        return 0;
    },

    backToDesign: function() {
        // save current configuration
        for (var x in QueryGen.template.conf) {
            QueryGen.saveToTemplate(x);
        }
        QueryGen.template.in_template = false;
        
        $('#templateReset').dialog({
            autoOpen: false,
            modal: true,
            width: 320,
            resizable: false,
            buttons:
            [
                {
                    text: "Yes",
                    click: function() {
                        tqid = null;
                        tparams = null;
                        $("#definetempl").hide("fast");
                        QueryGen.unhideDesignTools();
                        $("#clear_btn,#save_transl,#save_templ").show();
                        $("#back_to_design").hide();
                        //$('#redolast').show();
                        $("#query_submit").off("click").on("click", QueryGen.submitGraph);
                        $(this).dialog("close");
                    }
                },
                {
                    text: "No",
                    click: function() {
                        $(this).dialog("close");
                    }
                }
            ]
        }).dialog("open");
    },

    startTemplateDefinition: function() {
        QueryGen.template.base_query = QueryGen.generateQueryDict();

        $('.templateform').remove();
        if (QueryGen.template.base_query == null)
            return;
        QueryGen.template.in_template = true;
        // hide button panels
        QueryGen.hideDesignTools();
        // show template definition panel
        $("#definetempl").show("fast");
        // hide non-template buttons
        $("#clear_btn,#save_transl,#save_templ").hide();
        // show back to design button
        $("#back_to_design").show();
        // set submission handler
        $("#query_submit").off("click").on("click", QueryGen.submitTemplate);

        $("article#blockparams table.paramlist").remove();
        QueryGen.template.blocks = [];
        for (var x in QueryGen.jsonStrGraph) {
            if (x == 'start' || x == 'end')
                continue;
            var b = QueryGen.jsonStrGraph[x];
            console.log(b);
            // if it is an entity or a configurable operator (i.e. group by or genealogy id) except the extend operator or a configurable template
            if (b.button_cat == 'qent' || b.button_cat == 'op' && b.button_id != 7 && ((b.button_id != 6 && ops[b.button_id].configurable == true) || (b.button_id == 6 && templates[b.template_id].parameters.length > 0))) {
                QueryGen.template.blocks.push(b);
                QueryGen.generateTemplate(b);
                QueryGen.updateTemplateConf(b);
                QueryGen.prepareTemplateForm(b);
            }
        }

        QueryGen.template.curr_block_id = 0;
        QueryGen.changeTemplateForm({data: {dir: 0}});
    },


    updateTemplateConf: function(bid){
        if (tparams){
            console.log(bid.id);
            var block = bid.id;
            
            if (!$.isEmptyObject(tparams[block].inputs)){
                QueryGen.template.conf[bid.id]['inputs'] =  tparams[block]['inputs'];
            }
            
            console.log(QueryGen.template.conf[bid.id], tparams);
            for (var p in tparams[block]['parameters']){
                console.log(p, QueryGen.template.conf[bid.id]);
                console.log(QueryGen.template.conf[bid.id].parameters[p],  tparams[block]['parameters'][p]);
                QueryGen.template.conf[bid.id].parameters[p]['name'] = tparams[block]['parameters'][p]['name'];
                QueryGen.template.conf[bid.id].parameters[p]['description'] = tparams[block]['parameters'][p]['description'];
                QueryGen.template.conf[bid.id].parameters[p]['opt'] = parseInt(tparams[block]['parameters'][p]['opt']);
                console.log(QueryGen.template.conf[bid.id].parameters)
            }            
        }
    },

    updateTemplateAndForm: function(bid) {
        QueryGen.saveToTemplate(bid);
        QueryGen.template.base_query = QueryGen.generateQueryDict();
        var b = QueryGen.jsonStrGraph[bid];
        QueryGen.generateTemplate(b);
        QueryGen.prepareTemplateForm(b);
        if (QueryGen.template.blocks[QueryGen.template.curr_block_id].id == bid) {
            QueryGen.changeTemplateForm({data: {dir: 0}});
        }
    },

    saveToTemplate: function(bid) {
        $("#div" + bid + " table#paramdef tr.param").each(function() {
            var s = $(this).find("select");
            var d = s.data();
            var v = s.val();
            QueryGen.template.conf[d.b_id].parameters[d.f_id].opt = v;
            if (v == 2 || v == 3) {
                //var r = $(this).next();
                var t = $(this).find("input:eq(0)");
                QueryGen.template.conf[bid].parameters[d.f_id].name = t.val();
                //r = r.next();
                t = $(this).find("input:eq(1)");
                QueryGen.template.conf[bid].parameters[d.f_id].description = t.val();
            } else {
                QueryGen.template.conf[bid].parameters[d.f_id].name = "";
                QueryGen.template.conf[bid].parameters[d.f_id].description = "";
            }
        });

        $("#div" + bid + " table#inpdef tbody tr").each(function() {
            var iid = $(this).data("input_id");
            QueryGen.template.conf[bid].inputs[iid] = {name: $(this).find("input:eq(0)").val(), description: $(this).find("input:eq(1)").val()};
        });

    },

    generateTemplate: function(b) {
        if (b.button_cat == 'qent') {
            // if refreshing, the current block might already be in the template, so we don't wanna overwrite the previous contents
            if (QueryGen.template.conf[b.id] == undefined) {

                QueryGen.template.conf[b.id] = {inputs: {}, parameters: {}};
                // we allow to define what to do with all filters of a given block (including those that have not been selected by the template designer in the block configuration window)
                // n.b. filters that are enabled in the block configuration will be set to option "1", otherwise they will be set to option "0"
                var e = qent[b.button_id];
                var enabled_filters = [];
                var pars = b.parameters;
                for (var i = 0, ll = pars.length; i <ll; ++i) {
                    enabled_filters.push(pars[i].f_id);
                }
                for (var f_id in e.filters) {
                    if (e.filters[f_id].type == 7)
                        QueryGen.template.conf[b.id].parameters[f_id] = {name: 'WG', description: '', opt: 2};
                    
                    else
                        QueryGen.template.conf[b.id].parameters[f_id] = {name: '', description: '', opt: enabled_filters.indexOf(f_id) == -1 ? 0 : 1};
                }
            }
        } else
                
        if (b.button_cat == 'op') {
            if (b.button_id == 4) { //group by
                // if refreshing, the current block might already be in the template, so we don't wanna overwrite the previous contents
                var old_conf = QueryGen.template.conf[b.id] || {inputs: {}, parameters: {}}
                QueryGen.template.conf[b.id] = {inputs: {}, parameters: {}}
                // we only allow to define what to do with filters that have already been defined
                // i.e., we don't allow the end user to define its own filters but only to provide values for filters defined by the template designer
                for (var j = 0, ll = b.parameters.length; j < ll; ++j) {
                    // if refreshing, the current filter might already be in the block, so we don't wanna overwrite its previous settings
                    if (old_conf.parameters[b.parameters[j].uid] != undefined) {
                        // if it's there, only update the filter index
                        QueryGen.template.conf[b.id].parameters[b.parameters[j].uid] = $.extend(old_conf.parameters[b.parameters[j].uid], {index: j});
                    } else {
                        QueryGen.template.conf[b.id].parameters[b.parameters[j].uid] = {name: '', description: '', opt: 1, index: j};
                    }
                }
            } else
            if (b.button_id == 5) { //genealogy id
                // we store whether the genealogy id value(s) shall be entered by the user or are locked to the ones defined by the template designer
                QueryGen.template.conf[b.id] = QueryGen.template.conf[b.id] || {inputs: {}, parameters: {'genid':{name: '', description: '', opt: -1}}};
            }
            if (b.button_id == 6) { // template
                if (QueryGen.template.conf[b.id] == undefined) {

                    QueryGen.template.conf[b.id] = {inputs: {}, parameters: {}};
                    // we allow to define what do with all filters of a given template block (including those that have not been selected by the template designer in the template configuration window)
                    // n.b. filters that are enabled in the template configuration will be set to option "1", otherwise they will be set to option "0"
                    var t = templates[b.template_id];
                    var enabled_filters = [];
                    var pars = b.parameters;
                    for (var i = 0, ll = pars.length; i < ll; ++i) {
                        enabled_filters.push(parseInt(pars[i].f_id));
                    }
                    for (var i = 0, ll = t.parameters.length; i < ll; ++i) {
                        var f_id = i;
                        if (t.parameters[i].type == 7)
                            QueryGen.template.conf[b.id].parameters[f_id] = {name: 'WG', description: '', opt: 2};
                        else    
                            QueryGen.template.conf[b.id].parameters[f_id] = {name: '', description: '', opt: enabled_filters.indexOf(f_id) == -1 ? 0 : 1};
                    }
                }
            }
        }

        var old_inputs = QueryGen.template.conf[b.id].inputs;
        QueryGen.template.conf[b.id].inputs = {};
        for (var i = 0; i < b.w_in.length; ++i) {
            if (b.w_in[i] == 'start') {
                QueryGen.template.conf[b.id].inputs[i] = old_inputs[i] || {name: '', description: ''};
            }
        }
    },

    showTemplateForm: function(next_id) {
        // fill block id label
        var b = QueryGen.template.blocks[next_id];

        var currb_id = QueryGen.template.blocks[QueryGen.template.curr_block_id].id;

        var div1 = $("#div" + currb_id);
        var div2 = $("#div" + b.id);

        var dir1, dir2;
        if (currb_id < b.id) {
            dir1 = 'left';
            dir2 = 'right';
        } else {
            dir1 = 'right';
            dir2 = 'left';
        }
        div1.hide({effect: "slide", direction: dir1}); //, complete: function() {$(this).css("position", "");}});
        div2.show({effect: "slide", direction: dir2}); //, complete: function() {$(this).css("position", "");}});
    },

    prepareTemplateForm: function(b) {
        var div = '<div style="position: absolute; display: none" class="templateform"><p id="blockinfo" style="font-size: 14px; margin-left: 20px">Block<span style="margin-left: 5px" class="blockid2"></span>&nbsp;:<span style="margin-left: 10px; font-weight: bold"></span></p><article id="blockparams"><table id="inpdef" class="paramlist" style="margin-bottom: 20px"><thead><th style="padding: 5px; width: 30%; background-color: #cccccc">Input</th><th style="padding: 5px; width: 70%; background-color: #cccccc">Description</th></thead><tbody></tbody></table><table id="paramdef" class="paramlist"><thead><th style="padding: 5px; width: 30%; background-color: #cccccc">Filter name</th><th style="padding: 5px; width: 70%; background-color: #cccccc">Option</th></thead><tbody></tbody></table></article></div>';

        $("#div"+b.id).remove();

        var thediv = $(div);
        thediv.attr("id", "div" + b.id);
        console.log(b)
        console.log(b.id);
        
        if ($.isEmptyObject(QueryGen.template.conf[b.id].inputs)) {
            thediv.find("#inpdef").hide();
        } else {
            var inptbody = thediv.find("#inpdef tbody");
            var inputs = QueryGen.template.conf[b.id].inputs;

            for (var i in inputs) {
                var itr = $("<tr></tr>").data("input_id", i);
                var itd1 = $("<td style='text-align: center; font-weight: bold'>" + (parseInt(i)+1) + "</td>");
                var itd2 = $('<td><label style="width: 80px; display: inline-block" for="tinput-name"><i>Name:</i></label><input type="text" id="tinput-name" /><br><label style="width: 80px; display: inline-block" for="tinput-descr"><i>Description:</i></label><input type="text" id="tinput-descr" /></td>');
                itd1.appendTo(itr);
                itd2.appendTo(itr);
                itd2.find("input:eq(0)").val(inputs[i].name);
                itd2.find("input:eq(1)").val(inputs[i].description);
                itr.appendTo(inptbody);
            }
        }

        var p = thediv.find("#blockinfo");
        p.children("span:eq(0)").text(b.id);
        if (b.button_cat == 'qent') {
            p.children("span:eq(1)").text(qent[b.button_id].name);
        } else
        if (b.button_cat == 'op') {
            if (b.button_id == 6) { // we wanna show the template name rather than just "Template"
                p.children("span:eq(1)").text(templates[b.template_id].name);
            } else {
                p.children("span:eq(1)").text(ops[b.button_id].name);
            }
        }

        $("#templbtn").before(thediv);
        
        var tdselect = "<td><select class='selparam template'><option value='0'>Do not use</option><option value='1'>Lock to current value</option><option value='2'>Leave blank</option></select></td>";
        var tdselect_predefList = "<td><select class='selparam template'><option value='0'>Do not use</option><option value='1'>Lock to current values (main+sub)</option><option value='2'>Leave blank</option><option value='3'>Lock to current values (main only)</option></select></td>";

        var tbody = thediv.find("#paramdef tbody");

        if (b.button_cat == 'qent') {
            var e = qent[b.button_id];
            for (var x in QueryGen.template.conf[b.id].parameters) {
                var tr = $("<tr class='param' id='f" + b.id + "-" + x + "'></tr>");
                var td1 = $("<td>"+e.filters[x].name+"</td>"); 
                var td2 = $(e.filters[x].type == 1 ? tdselect_predefList : tdselect);
                td2.find("select").data("f_id", x).data("b_id", b.id);
                td1.appendTo(tr);
                td2.appendTo(tr);
                tr.appendTo(tbody);
                td2.find("select").prop("selectedIndex", QueryGen.template.conf[b.id].parameters[x].opt);
                if (e.filters[x].type == 7){
                    td2.find("select").prop('disabled', true);
                }
            }
        } else

        if (b.button_cat == 'op') {
            var o = ops[b.button_id];

            if (b.button_id == 5) { // genealogy id
                var tr = $("<tr class='param'></tr>");
                var td1 = $("<td>Genealogy ID list</td>");
                var td2 = $(tdselect);
                td2.find("select").data("b_id", b.id).data("f_id", 'genid');
                td2.find("option:eq(0)").attr("disabled", true);
                td1.appendTo(tr);
                td2.appendTo(tr);
                tr.appendTo(tbody);
                td2.find("select").prop("selectedIndex", QueryGen.template.conf[b.id].parameters['genid'].opt);
            } else

            if (b.button_id == 4) { // group by
                var connBlock = QueryGen.getGraphNode(b.id).w_in[0];
                var connBType = QueryGen.getGraphNode(connBlock).output_type_id;
                var attr_list = qent[connBType].outputs;
                for (var x in QueryGen.template.conf[b.id].parameters) {
                    var j = QueryGen.template.conf[b.id].parameters[x].index;
                    var f = b.parameters[j];
                    var name = f.op + "(" + (f.attr == -1 ? "*" : attr_list[f.attr].name) + ")";
                    var tr = $("<tr class='param' id='f" + b.id + "-" + f.uid + "'></tr>");
                    var td1 = $("<td>"+name+"</td>");
                    var td2 = $(tdselect);
                    td2.find("select").data("b_id", b.id).data("f_id", x);
                    td2.find("option:eq(0)").attr("disabled", true);
                    td1.appendTo(tr);
                    td2.appendTo(tr);
                    tr.appendTo(tbody);
                    td2.find("select").prop("selectedIndex", QueryGen.template.conf[b.id].parameters[x].opt);
                }
            }

            if (b.button_id == 6) { // template
                var t = templates[b.template_id];
                for (var i = 0, ll = t.parameters.length; i < ll; ++i) {
                    var f_id = i;
                    var tr = $("<tr class='param' id='f" + b.id + "-" + x + "'></tr>");
                    var td1 = $("<td>"+t.parameters[i].name+"</td>");
                    var td2 = $(t.parameters[i].type == 1 ? tdselect_predefList : tdselect);
                    td2.find("select").data("f_id", f_id).data("b_id", b.id);
                    td1.appendTo(tr);
                    td2.appendTo(tr);
                    tr.appendTo(tbody);
                    td2.find("select").prop("selectedIndex", QueryGen.template.conf[b.id].parameters[f_id].opt);
                    if (t.parameters[i].type == 7){
                        td2.find("select").prop('disabled', true);
                    }

                }
            }

        }
        tbody.find("tr.param td:nth-child(2)").each(function() {
            var f_id = $(this).find("select").data("f_id");

            var x = $('<span style="display: none"><br><label style="width: 80px; display: inline-block"><i>Name:</i></label><input type="text" /><br><label style="width: 80px; display: inline-block"><i>Description:</i></label><input type="text" /></span>')
            $(this).append(x);
            x.find("input:eq(0)").val(QueryGen.template.conf[b.id].parameters[f_id].name);
            x.find("input:eq(1)").val(QueryGen.template.conf[b.id].parameters[f_id].description);
        });
        tbody.find("select.selparam").change(function() {
            var v = $(this).val();

            if (v == 2 || v == 3) { // show "name" and "description" fields if "leave blank" or "lock to current value (main only)" is selected
                $(this).next().show();
            } else {
                $(this).next().hide();
            }
        }).change();
    },

    changeTemplateForm: function(evt) {
        var next_id = QueryGen.template.curr_block_id;
        if (evt.data.dir == 1 && QueryGen.template.curr_block_id < QueryGen.template.blocks.length - 1)
            ++next_id;
        else if (evt.data.dir == -1 && QueryGen.template.curr_block_id > 0)
            --next_id;
        QueryGen.showTemplateForm(next_id);
        QueryGen.template.curr_block_id = next_id;
        if (QueryGen.template.curr_block_id == 0) {
            $("#prev-param").attr("disabled", true);
            $("#prev-param").addClass("disabled");
        } else {
            $("#prev-param").attr("disabled", false);
            $("#prev-param").removeClass("disabled");
        }
        if (QueryGen.template.curr_block_id == QueryGen.template.blocks.length - 1) {
            $("#next-param").attr("disabled", true);            
            $("#next-param").addClass("disabled");
        } else {
            $("#next-param").attr("disabled", false);
            $("#next-param").removeClass("disabled");
        }
    },

    // checks if graph is acyclic
    checkAcyclic: function() {
        var res;
        for (var x in QueryGen.jsonStrGraph) {
            console.log(x);
            if (!QueryGen.jsonStrGraph[x].visited) {
                res = QueryGen.visitAcyclic(x);
                if (!res) {
                    break;
                }
            }
        }
        //clean up
        for (var x in QueryGen.jsonStrGraph) {
            QueryGen.setGraphNodeAttr(x, 'visited', false);
            QueryGen.setGraphNodeAttr(x, 'onstack', false);
        }
        return res;
        
    },
    
    // visits graph starting from a given node to check for acyclicity
    visitAcyclic : function(curr_id) {
        var curr = QueryGen.getGraphNode(curr_id);
        if (curr.visited) {
            if (!(curr.onstack)) {
                return true;
            } else {
                return false;
            }
        } else {
            QueryGen.setGraphNodeAttr(curr_id, 'visited', true);
            QueryGen.setGraphNodeAttr(curr_id, 'onstack', true);
            if (curr.w_out) {
                for (var i=0; i < curr.w_out.length; ++i){
                    var next_node = curr.w_out[i].split('.')[0];
                    var res = QueryGen.visitAcyclic(next_node);
                    if (!res) {
                        return false;
                    }
                }
            }
            QueryGen.setGraphNodeAttr(curr_id, 'onstack', false);
            return true;
        }
    },
    
    checkConnected: function() {
        for (var x in QueryGen.jsonStrGraph) {

            if (    (x == QueryGen.startName && QueryGen.jsonStrGraph[x].w_out.length < 1)  ||
                    (x == QueryGen.endName && QueryGen.jsonStrGraph[x].w_in.length != 1)) {
                console.log("start or end block disconnected");
                return false;
            } else

            if (x != QueryGen.startName && x != QueryGen.endName) {
                var len_in;
                if (QueryGen.jsonStrGraph[x].button_cat == 'qent') {
                    len_in = 1;
                } else

                if (QueryGen.jsonStrGraph[x].button_cat == 'op' && QueryGen.jsonStrGraph[x].button_id != 6) { // not templates
                    len_in = ops[QueryGen.jsonStrGraph[x].button_id].numInputs;
                } else

                if (QueryGen.jsonStrGraph[x].button_cat == 'op' && QueryGen.jsonStrGraph[x].button_id == 6) { // templates
                    len_in = templates[QueryGen.jsonStrGraph[x].template_id].inputs.length;
                }
                var len_out = 1;

                if (QueryGen.jsonStrGraph[x].w_in.length != len_in || 
                    QueryGen.jsonStrGraph[x].w_out.length != len_out) {
                    return false;
                } else {
                    for (var j=0; j<QueryGen.jsonStrGraph[x].w_in.length; ++j) {
                        if (!QueryGen.jsonStrGraph[x].w_in[j]) {
                            return false;
                        }
                    }
                }
            }
        }
        return true;
    },
    
    checkParameters: function() {
        // andrebbe schematizzato a database quali blocchi/operatori abbiano dei parametri obbligatori
        // n.b. il group by non richiede per forza parametri
        var requiresConfig = {
            // inserire qui le tuple [categoria_bottone, id_bottone] per i bottoni che richiedono configurazione
            data: [["op", 5], ["op", 4], ["op", 7]],
            
            check: function(obj) {
                for (var i = 0, len = this.data.length; i < len; ++i) {
                    if (this.data[i][0] == obj.button_cat && this.data[i][1] == obj.button_id)
                        return true;
                }
                return false;
            }
        };

        for (var x in QueryGen.jsonStrGraph) {
            if (requiresConfig.check(QueryGen.jsonStrGraph[x]) && QueryGen.jsonStrGraph[x].parameters.length < 1) {
                return false;
            }
        }
        return true;
    },

   
    submitGraphAsTranslator : function() {
        
        if (QueryGen.jsonStrGraph['start'].w_out.length > 1) {
            alert(  "This feature requires that a single block be connected to the start block",
                    "Cannot save as translator",
                    "Ok"
            );
            return;
        }
        
        if ($("textarea#query_title").val().trim() == '' || $("textarea#query_description").val().trim() == '') {
            alert(  "Please fill in the title and description fields",
                    "Cannot save as translator",
                    "Ok"
            );
            return;
        }
        
        if (Object.keys(QueryGen.jsonStrGraph).length < 3) {
            alert(  "To translate an entity into another you need at least one block",
                    "Cannot save as translator",
                    "Ok"
            );
            return;
        }

        QueryGen.saveAsTranslator();
    }, 
    
    submitGraph : function() {
        
        var q = QueryGen.generateQueryDict();
        if (q == null)
            return;
        q.graph_nodes = JSON.stringify(q.graph_nodes);
        
        ctrl = getBusyOverlay("viewport", {color:'#B2B2B2', opacity:0.3, text:'Running query, please wait...', style: 'color: #222222;'}, {color:'#222222', weight:'3', size:100, type:'rectangle', count:12});
        
        $("#sqf_title").val(q['title']);
        $("#sqf_description").val(q['description']);
        $("#sqf_graph_nodes").val(q['graph_nodes']);
        $("#sqf_qid").val(qid);
        
        console.log(qid);
        console.log(q['graph_nodes']);
        
        $("#submit_query_frm").submit(function(e) {
            var postData = $(this).serializeArray();
            var formURL = $(this).attr("action");
            $.ajax({
                url : formURL,
                type: "POST",
                data : postData,
                success:function(data, textStatus, jqXHR) {
                    data = JSON.parse(data);
                    window.location.href = display_results_url + '?qid=' + data.qid + '&rid=' + data.rid;
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    alert("An error occurred.")
                }
            });
            e.preventDefault(); //STOP default action
        });
        $("#submit_query_frm").submit();

    },
    
    removeNullOutputs : function() {
        // remove undefined elements from GB "outputs" array and
        // from EXTEND "parameters" and "outputs" array
        // and fix references to these arrays in subsequent query blocks
        for (var i in QueryGen.jsonStrGraph) {
            var x = QueryGen.jsonStrGraph[i];
            if (x.button_cat == 'op') {
                // create remapping
                var remap = {};
                var toRemove = 0;
                for (var j = 0; j < x.outputs.length; ++j) {
                    if (x.outputs[j] == undefined) {
                        ++toRemove;
                    } else {
                        remap[j] = j - toRemove;
                    }
                }
                if (toRemove == 0) continue;

                if (x.button_id == 4) { // group by
                    // remove undefined elements
                    x.outputs = x.outputs.filter(function(el) {return el != undefined;});
                } else

                if (x.button_id == 7) { // extend
                    // remove undefined elements
                    x.outputs = x.outputs.filter(function(el) {return el != undefined;});
                    x.parameters = x.parameters.filter(function(el) {return el != undefined;});

                }

                // fix references in next block
                var connBlockId = x.w_out[0].split('.')[0];
                if (connBlockId == 'end') continue;
                
                var next = QueryGen.jsonStrGraph[connBlockId];
                var f = QueryGen.findCorrelatedFilters(connBlockId);
                
                if (next.button_cat == 'qent') {
                    for (var j = 0; j < f.length; ++j) {
                        var param = next.parameters[f[j]];
                        for (var k = 0; k < (param.values.length < 2 ? param.values.length : 2); ++k) {
                            var v = param.values[k].split('_');
                            var vv = v[1].split('+');
                            var oid = remap[vv[0]];
                            param.values[k] = v[0] + '_' + oid + (vv[1] ? '+' + vv[1] : '');
                        }
                    }
                } else

                if (next.button_cat == 'op' && next.button_id == 4) { // group by
                    // fix correlated parameters
                    for (var j = 0; j < f.length; ++j) {
                        var param = next.parameters[f[j]];
                        var v = param.attr.split('_');
                        param.attr = v[0] + '_' + remap[v[1]];
                    }
                    // find and fix correlated outputs
                    for (var j = 0; j < next.outputs.length; ++j) {
                        var out = next.outputs[j];
                        if (out.attr[0] == 'c') {
                            var v = out.attr.split('_');
                            out.attr = v[0] + '_' + remap[v[1]];
                        }
                    }
                } else

                if (next.button_cat == 'op' && next.button_id == 7) { // extend
                    for (var j = 0; j < f.length; ++j) {
                        var param = next.parameters[f[j]];
                        param.out_id = remap[param.out_id];
                    }
                }
            }
        }   
    },

    generateQueryDict : function() {
        // perform some preliminary checks:
        // -graph has at least one block
        // -graph is connected
        // -graph is acyclic
        // -all blocks requiring configuration have been configured
        
        // la nuova interfaccia permette di configurare più parametri
        // simultaneamente nello stesso box, cosa non consentita prima.
        // per permettere di utilizzare temporaneamente il vecchio codice
        // server-side, nel generare il grafo di query, tutti i blocchi
        // che hanno più di un parametro configurato vengono splittati,
        // generando tanti blocchi dello stesso tipo, ciascuno con un solo
        // parametro settato. i nuovi blocchi sono numerati in questo modo:
        // -il primo mantiene l'id del blocco originale
        // -agli altri viene assegnato un nuovo id incrementale
        // -nel nodo originale viene aggiunto un attributo "last_id", contenente
        // il massimo degli id assegnati ai nuovi blocchi. questo valore deve essere 
        // utilizzato nell'assegnare il w_in dei blocchi successivi,
        // al posto dell'id originale
        
        var atleast1 = Object.keys(QueryGen.jsonStrGraph).length > 2 ? true : false;
        var acycl = QueryGen.checkAcyclic();
        var conn = QueryGen.checkConnected();
        var paramsOk = QueryGen.checkParameters();
        var errMsg = '';

        
        if (!atleast1) {
            errMsg += '-query graph should include at least one block<br>';
        }
        if (!acycl) {
            errMsg += '-query graph has a cycle<br>';
        }
        if (!conn) {
            errMsg += '-one or more terminals are disconnected<br>';
        }
        if (!paramsOk) {
            errMsg += '-one or more blocks must be configured<br>'
        }
        if (errMsg != '') {
            alert(  "The following problems were identified:<br>" + errMsg,
                    "Cannot submit query!",
                    "Ok"
            );
            return null;
        }

        // remove undefined outputs from group by and extend blocks,
        // and fix references to outputs in downstream blocks
        QueryGen.removeNullOutputs();

        var title=$("textarea#query_title").val();
        var description=$("textarea#query_description").val();

        var query = {
            'title' : title,
            'description' : description,
            'graph_nodes' : QueryGen.getQueryDict()
        };
        
        return query;
        
    },
    
    getQueryDict : function() {

        var d = {}
        var z = $("#canvas").offset();
        for (var x in QueryGen.jsonStrGraph) {
            var j = QueryGen.jsonStrGraph[x];
            
            var o = (x != "start" && x != "end") ? $("#box"+x).offset() : {left: 0, top: 0};
            d[x] = {
                button_id: j.button_id,
                parameters: j.parameters ? (j.button_cat == "op" && j.button_id == 6 ? QueryGen.processTemplateParameters(j.parameters, j.template_id) : QueryGen.processParameters(j.parameters, j.button_id)) : null,
                outputs: j.outputs,
                query_path_id: j.query_path_id instanceof Array ? j.query_path_id : [j.query_path_id],
                gb_entity: j.gb_entity,
                w_in: j.w_in,
                w_out: j.w_out,
                button_cat: j.button_cat,
                output_type_id: j.output_type_id,
                offsetX: o.left - z.left,
                offsetY: o.top - z.top,
                template_id: j.template_id
            };
        }
        d['end']['translators'] = QueryGen.jsonStrGraph['end']['translators'];

        return d;
    },

    processParameters: function(pList, button_id) {
        var params = [];
        var subflt = [];
        var l = pList.length;
        
        var WgFilters = {}
        if (qent.hasOwnProperty(button_id)){
            if (workingGroupsList.indexOf('admin') >= 0 ) {
                console.log(button_id, qent[button_id])
                if (qent[button_id].hasWG){    
                    for (var f in qent[button_id].filters){
                        if (qent[button_id].filters[f].type == 7){
                            var W = qent[button_id]['filters'][f].values
                            for (var wj in W){
                                if (workingGroupsList.indexOf( W[wj][1]) != -1 && W[wj][1] == 'admin'){
                                    WgFilters[f] = W[wj][0];
                                }
                            }
                        }
                    }
                }
            }
        }
        
        for (var i = 0; i < l; ++i) {
            if (pList[i]['par_flt_id'] == undefined) {
                if (WgFilters.hasOwnProperty(pList[i]['f_id'])){
                    if (pList[i].values.indexOf(WgFilters[pList[i]['f_id']]) != -1 )
                        continue;
                    }
                params.push($.extend({}, pList[i]));
            } else {
                subflt.push(i);
            }
        }
        for (var i = 0; i < subflt.length; ++i) {
            var s = pList[subflt[i]];
            var parflt;
            for (var j = 0; j < params.length; ++j) {
                if (params[j]['f_id'] == s['par_flt_id']) {
                    parflt = params[j];
                    break;
                }
            }
            if (parflt['subflt'] == undefined) parflt['subflt'] = [];
            for (var j = 0; j < parflt.values.length; ++j) {
                if (parflt.values[j] == s['par_flt_value']) {
                    parflt.subflt[j] = {'f_id': s['f_id'], 'values': s['values']};
                    break;
                }
            }
        }
        return params;
    },

    processTemplateParameters: function(pList, template_id) {
        var params = [];
        var subflt = [];
        var l = pList.length;

        var WgFilters = {}
        if (workingGroupsList.indexOf('admin') >= 0 ) {
            for (var t in templates[template_id].parameters){
                if (templates[template_id].parameters[t].type == 7){
                    var button_id = templates[template_id].parameters[t].src_button_id
                    var filter_id = templates[template_id].parameters[t].src_f_id
                    var W = qent[button_id]['filters'][filter_id].values
                   for (var wj in W){
                        if (workingGroupsList.indexOf( W[wj][1]) != -1 && W[wj][1] == 'admin'){
                            WgFilters[t] = W[wj][0];
                        }
                    }
                    
                }
            }
        }
        
        for (var i = 0; i < l; ++i) {
            if (pList[i]['par_flt_id'] == undefined) {
                if (WgFilters.hasOwnProperty(pList[i]['f_id'])){
                    if (pList[i].values.indexOf(WgFilters[pList[i]['f_id']]) != -1 )
                        continue;
                    }
                params.push($.extend({}, pList[i]));
            } else {
                subflt.push(i);
            }
        }
        for (var i = 0; i < subflt.length; ++i) {
            var s = pList[subflt[i]];
            var parflt;
            for (var j = 0; j < params.length; ++j) {
                if (params[j]['f_id'] == s['par_flt_id']) {
                    parflt = params[j];
                    break;
                }
            }
            if (parflt['subvalues'] == undefined) parflt['subvalues'] = [];
            for (var j = 0; j < parflt.values.length; ++j) {
                if (parflt.values[j] == s['par_flt_value']) {
                    parflt.subvalues[j] = s['values'];
                    console.log(parflt.subvalues);
                    break;
                }
            }
        }
        return params;
    },

    // GUI function
    // handle click on button3 and button2 buttons
    // toggle clicked button on/off and set cursor in design area accordingly
    buttonClickHandler : function() {
        if ($(this).hasClass("clicked")) {
            $(this).removeClass("clicked");
            QueryGen.clickedButton = null;
        } else {
            $(this).addClass("clicked");
            if (QueryGen.clickedButton)
                QueryGen.clickedButton.removeClass("clicked");
            QueryGen.clickedButton = $(this);
        }
        
        if (QueryGen.clickedButton)
            $("section#central").css("cursor", "crosshair");
        else
            $("section#central").css("cursor", "auto");

    },

    drawQueryElement : function(block_id, button_id, button_title, button_category, button_ds_label, n_inputs, configurable, out_from_in, e, button_subtitle, template_id) {
        
        if (button_subtitle != undefined) {
            var subtitle = "<span style='font-size: 8pt; font-weight: bold'>" + button_subtitle + "</span>";
        } else {
            var subtitle = "";
        }

        $("section#central").append('<p class="box ' + button_ds_label + '" id="box'+block_id+'"><span class="blockid">'+block_id+'</span><span class="x" title="Remove block"></span><br><em id="name">'+button_title+'</em><br>'+subtitle+'</p>');
    
        var block = $("p#box"+block_id);
        
        if (configurable == true) {
        	block.children("span.x").after('<span class="arrow" title="Configure block"></span>');
        } else {
            block.children("span.x").after('<span class="dummyarrow"></span>');
        }
        
        block.append('<p class="hr"></p>');
        block.attr("data-btn_id",button_id);
        block.attr("data-block_id",block_id);
        
        // nel punto in cui ho cliccato con il mouse
        block.css("left", e.pageX);
        block.css("top", e.pageY-11);


        if (configurable == true) {
            
            if (button_category == "op") {
                if (button_id == 4) { // group by button
                    block.append('<span id="led" class="filteroff2"></span>');
                    block.children("span.arrow").click(function() {
                        if (QueryGen.getGraphNode(block_id).w_in.length > 0) {
                            QueryGen.prepareGBDialog(block_id, outTerminal);
                            $("#gbdialog").dialog("open");
                        } else {
                            alert("You need to connect the grouping operator to an input block before you can configure it.",
                                "Oops!",
                                "Ok"
                            );
                        }
                    }); 
                } else

                if (button_id == 6) { // templates button
                    // insert wg parameters
                    if (templates[template_id].parameters.length > 0) {
                        block.append('<span id="led" class="filteroff"></span>');
                    }
                    // insert selected wg for template
                    var paramsWg=new Array();
                    var wgSetted = false;
                    for (var p= 0; p<templates[template_id].parameters.length; p++ ){
                        console.log(templates[template_id].parameters[p])
                        if (templates[template_id].parameters[p]['type'] == 7){
                            console.log("WG_filter: ", p);
                            
                            wgObj= new Object();
                            wgObj['values']=new Array();
                            wgObj['f_id'] = p.toString();       
                            var src_button_id = templates[template_id].parameters[p]['src_button_id'];
                            var src_f_id = templates[template_id].parameters[p]['src_f_id'];
                            
                            var W = qent[src_button_id]['filters'][src_f_id].values;

                            for (var wj in W){
                                if (workingGroupsList.indexOf( W[wj][1]) != -1 )
                                    wgObj['values'].push(W[wj][0]);
                            }
                            
                            paramsWg.push(wgObj);

                            if (!wgSetted) {
                                for (var wj in QueryGen.getGraphNode(block_id).parameters){
                                    if (wgObj['f_id'].indexOf( QueryGen.getGraphNode(block_id).parameters[wj]['f_id']) != -1 )
                                        wgSetted = true;
                                }
                            }
                            
                        }
                    }

                    if (!wgSetted){
                        QueryGen.setGraphNodeAttr(block_id, 'parameters', paramsWg);
                    }

                    if (QueryGen.getGraphNode(block_id).parameters.length > 0) {
                        $("p#box"+block_id).children("span#led").removeClass("filteroff").addClass("filteron");
                    } else {
                        $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff");
                    }


                    block.children("span.arrow").click(function() {
                        QueryGen.prepareTemplateConfigDialog(block_id);
                        $("#templconfigdialog").dialog("open");
                    });
                    
                } else

                if (button_id == 5) { // genid button
                    block.append('<span id="led" class="filteroff2"></span>');
                    block.children("span.arrow").click(
                        function() {
                            QueryGen.prepareGenidDialog(block_id);
                            $("#geniddialog").dialog("open");
                        }
                    );
                } else

                if (button_id == 7) { // extend (join) button
                    block.append('<span id="led" class="filteroff2"></span>');
                    block.children("span.arrow").click(function() {
                        if (QueryGen.getGraphNode(block_id).w_in.length > 0) {
                            QueryGen.prepareExtendDialog(block_id, outTerminal);
                            $("#extenddialog").dialog("open");
                        } else {
                            alert("You need to connect the extend operator to an input block before you can configure it.",
                                "Oops!",
                                "Ok"
                            );
                        }
                    });
                    // set handler that must be run when upstream block's dialog is closed
                    QueryGen.handle_dialog_close.map(block_id, QueryGen.update_extend_ent_outputs);
                }

            } else { // all other (configurable) buttons
                block.append('<span id="led" class="filteroff"></span>');
                block.children("span.arrow").click(
                    function() {
                        //console.log("prepare config dialog for block ", block_id);
                        QueryGen.prepareConfigDialog(block_id);
                        $("#configdialog").dialog("open");
                    }
                );

                
                if (qent[button_id].hasWG==true){
                    // insert selected wg
                    for (var p in qent[button_id].filters ){
                        console.log(p)
                        if (qent[button_id].filters[p]['type'] == 7){
                            var paramsWg=new Array();
                            wgObj= new Object();
                            wgObj['values']=new Array();
                            wgObj['f_id'] = p.toString();       
                            
                            var W = qent[button_id].filters[p].values;

                            for (var wj in W){
                                if (workingGroupsList.indexOf( W[wj][1]) != -1 )
                                    wgObj['values'].push(W[wj][0]);
                            }
                            
                            paramsWg.push(wgObj);
                            var wgSetted = false
                            for (var wj in QueryGen.getGraphNode(block_id).parameters){
                                if (wgObj['f_id'].indexOf( QueryGen.getGraphNode(block_id).parameters[wj]['f_id']) != -1 )
                                    wgSetted = true;
                            }
                            
                            if (!wgSetted){
                                QueryGen.addGraphNodeAttr(block_id, 'parameters', paramsWg);
                            }

                            if (QueryGen.getGraphNode(block_id).parameters.length > 0) {
                                $("p#box"+block_id).children("span#led").removeClass("filteroff").addClass("filteron");
                            } else {
                                $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff");
                            }
                        }
                    }
                }
            }
        }
        
        var current_block = $("#box"+block_id); 

        // h = current block height (due to block title + subtitle + ...)
        // hm = minimum block height
        //    = 2.m + n.ht + (n-1).dm
        // m = margin (upper and lower)
        // ht = terminal element height = 30px
        // n = number of inputs
        // d = current distance between contiguous terminals
        // dm = minimum distance between contiguous terminals = 20px
        // 1st terminal offset = 0px, last terminal offset = h - ht + pad (this already includes an appropriate margin; pad is the sum of top and bottom padding (equalling 8px). This allows some extra space)
        // this leaves a total height, for the other (n-2) terminals + (n-1) spaces between terminals, of h - 52px (where 52px = 2.ht - 8px)
        // hence:
        // hm = n.ht + (n-1).dm - 8px
        // if h <= hm:
        //    h = hm
        //    d = dm
        // else: (height is already more than needed, need to adjust spaces between terminals)
        //    d = (h - n.ht + 8px) / (n-1)
        // to be more general, padding is read from the element rather than hard-coded
        var h = parseInt(current_block.css("height"));
        var pad = parseInt(current_block.css("padding-top")) + parseInt(current_block.css("padding-bottom"));
        var ht = 30;
        var dm = 0;
        var hm = n_inputs*ht + (n_inputs-1)*dm - pad;
        var d;

        var vertical_offset = new Array(n_inputs);
        if (n_inputs > 1) {
            if (h <= hm) {
                h = hm;
                current_block.css("height", h);
                d = dm;
            } else {
                d = (h - n_inputs*ht + pad) / (n_inputs-1);
            }
            vertical_offset[0] = 0;
            for (var i = 1; i < n_inputs-1; ++i) {
                vertical_offset[i] = vertical_offset[i-1] + ht + d;
            }
            vertical_offset[n_inputs-1] = h + pad - ht;
        } else {
            vertical_offset[0] = (h + pad - ht) / 2;
        }
        out_term_vert_offset = (h + pad - ht) / 2;
        
        var current_terminals = new Array(n_inputs+1);
        
        for (var i = 0; i < n_inputs; ++i) {
            var label_input = button_category == "op" && button_id == 6 ? templates[template_id].inputs[i].name + "\n" + templates[template_id].inputs[i].description :
                "Input " + (i+1);
            var label_output = button_category == "op" && button_id == 6 ? GUI.getButtonName(templates[template_id].output) : "Output";
                
            current_terminals[i] = new WireIt.Terminal(current_block[0], {"name": label_input, direction: [-1,0], offsetPosition: [-23, vertical_offset[i]], wireConfig:{color: "#EEEEEE", bordercolor:"#282828", width: 2}, "ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 });
        }
        current_terminals[n_inputs] = new WireIt.Terminal(current_block[0], {"name": label_output, direction: [1,0], offsetPosition: [117, out_term_vert_offset], wireConfig:{color: "#EEEEEE", bordercolor:"#282828", width: 2}, "ddConfig": {"type": "output","allowedTypes": ["input"]}, "nMaxWires": 1 });

        var outTerminal = current_terminals[n_inputs];
        block.data("in-terminal", current_terminals.slice(0,n_inputs));
        block.data("out-terminal", current_terminals.slice(n_inputs,n_inputs+1));

        //output_terminals[QueryGen.block_id]=current_terminals[1];
        //input_terminals[QueryGen.block_id]=current_terminals[0];
        //new WireIt.util.DD(current_terminals,current_block);  //draggable
        block.draggable({ containment: $('#canvas'), drag: function( event, ui ) {
            for (var i=0; i<=n_inputs;++i)
                current_terminals[i].redrawAllWires();
            }
        });
        
        //controllo relazioni tra entita'.    
        if (button_category == "qent") {
            // event add wire
            current_terminals[0].eventAddWire.subscribe(QueryGen.new_Handle_Ent_AddEvent(current_terminals[0]));
            // evento remove wire
            current_terminals[0].eventRemoveWire.subscribe(QueryGen.new_Handle_EntTempl_RemoveEvent(block_id, 0));

        } else if (button_category == "op") {
            
            if (button_id == 7) { // extend (join) button
                // evento add wire
                current_terminals[0].eventAddWire.subscribe(QueryGen.new_Handle_Join_AddEvent(current_terminals[0]));
                // evento remove wire
                current_terminals[0].eventRemoveWire.subscribe(QueryGen.new_Handle_Join_RemoveEvent(block_id));
            } else 
            if (button_id == 6) { // templates
                for (var z = 0; z < n_inputs; ++z) {
                    // event add wire
                    current_terminals[z].eventAddWire.subscribe(QueryGen.new_Handle_Templ_AddEvent(current_terminals[z], z));
                    // evento remove wire
                    current_terminals[z].eventRemoveWire.subscribe(QueryGen.new_Handle_EntTempl_RemoveEvent(block_id, z));
                }
            } else

            if (button_id == 5) { // genealogy id
                current_terminals[0].eventAddWire.subscribe(QueryGen.new_Handle_Genid_AddEvent(current_terminals[0]));
                current_terminals[0].eventRemoveWire.subscribe(QueryGen.new_Handle_Genid_RemoveEvent(block_id));
            } else

            if (button_id == 4) { // group by
                current_terminals[0].eventAddWire.subscribe(QueryGen.new_Handle_GB_AddEvent(current_terminals[0]));
                current_terminals[0].eventRemoveWire.subscribe(QueryGen.new_Handle_GB_RemoveEvent(block_id));
            } else

            if (button_id <= 3 && button_id >= 1) { // logical operators
                // eventi add wire
                current_terminals[0].eventAddWire.subscribe(QueryGen.new_Handle_Op_AddEvent(current_terminals[0], 0));
                current_terminals[1].eventAddWire.subscribe(QueryGen.new_Handle_Op_AddEvent(current_terminals[1], 1));
                // eventi remove wire
                current_terminals[0].eventRemoveWire.subscribe(QueryGen.new_Handle_Op_RemoveEvent(block_id, 0));
                current_terminals[1].eventRemoveWire.subscribe(QueryGen.new_Handle_Op_RemoveEvent(block_id, 1));
            }

        }

		block.children("span.x").click(function() {   //to delete a block
			// prevent deletion if template mode is enabled
            if (QueryGen.template.in_template == true) return;

            in_terminals = $(this).parent().data("in-terminal");
            out_terminals = $(this).parent().data("out-terminal");
            var connTerminal = out_terminals[0].getConnectedTerminals()[0];
            var goOn = false;
            if (connTerminal !== undefined && $(connTerminal.parentEl).attr("id") != "end") {
                var connBlock = connTerminal.parentEl;
                var connBlockId = $(connBlock).attr("data-block_id");
                var f = QueryGen.findCorrelatedFilters(connBlockId);
                if (f.length) {
                    confirm("Some filters in the next block are correlated to this block, and will be removed.<br>Are you sure you want to continue?",
                            "Warning", "Yes", "No",
                            function() {
                                QueryGen.removeCorrelatedFilters(connBlockId, f);
                                for (var i=0; i<=n_inputs;++i)
                                    current_terminals[i].removeAllWires();
                                block.remove();
                                QueryGen.deleteGraphNode(block_id);
                            }
                    );
                } else {
                    goOn = true;
                }
            } else {
                goOn = true;
            }

            if (goOn) {
                for (var i=0; i<=n_inputs;++i)
                    current_terminals[i].removeAllWires();
                block.remove();
                QueryGen.deleteGraphNode(block_id);
            }
		});

        return block;
                
    },
    
    prepareTemplateConfigDialog: function(block_id) {
        var n = QueryGen.getGraphNode(block_id);
        var t = templates[n.template_id];
        var out_btn = t.output;

        $("#templconfigdialog #templconfigtabs").tabs("option", "active", 0)
        $("#templconfigdialog #templname").html("Name: <b>" + t.name + "</b>");
        $("#templconfigdialog #templdescr").html("Description: " + (t.description != ""? t.description : "n/a") );

        // hide or show filters tab depending on whether template has parameters or not
        if (t.parameters.length == 0) {
            $("#templconfigdialog #a_templ_flt").hide();
            $("#templconfigdialog #templconfigtabs").tabs("option", "active", 1)
        } else {

            $("#templconfigdialog #a_templ_flt").show();
            $("#templconfigdialog #templconfig-flt").children().remove();
            var filters = t.parameters;
            for (var i = 0; i < filters.length; ++i) {
                var flt = filters[i];
                var flt_type = flt.type;
                $("#templconfigdialog #templconfig-flt").append('<p id="pf'+i+'">'+
                '<input type="checkbox" class="cfgchk" id="if'+i+'" value="'+i+'" data-f_id="'+i+'">'+
                '&nbsp;<label for="if'+i+'">'+flt.name+'</label></p>'+
                '<p class="cfgval" id="cfgval'+i+'"></p>');
                $("#templconfigdialog #if"+i).data("id", i);
            
                // add filter elements
                $("#templconfigdialog #cfgval"+i).data("f_type", flt_type);

                if (flt_type == 6) { // Boolean
                    $("#templconfigdialog #templ_val_"+i).addClass("valuesovf");
                    var values = qent[flt.src_button_id].filters[flt.src_f_fid].values;
                    for (var j = 0; j < values.length; ++j) {
                        var v = values[j];
                        $("#templconfigdialog #templ_val_"+i).append('<input name="par'+i+'" class="par'+i+'" id="val'+j+'" type="radio" value="'+v[0]+'"/><b>'+v[1]+'</b><br>');
                    }
                } else 

                if (flt_type == 1) { // Predefined list
                    var f_multival = qent[flt.src_button_id].filters[flt.src_f_id].multiValued;
                    var input_type = f_multival == true ? "checkbox" : "radio";
                    $("#templconfigdialog #cfgval"+i).addClass("valuesovf");
                    $("#templconfigdialog #cfgval"+i).append("<table id='tval"+i+"' style='width: 99%'><tbody></tbody></table>");
                    if (flt.src_main_flt_values == undefined) {
                        var values = qent[flt.src_button_id].filters[flt.src_f_id].values;
                    } else {
                        var values = qent[flt.src_button_id].filters[flt.src_f_id].values.filter(function(e) {
                            return flt.src_main_flt_values.indexOf(e[0]) != -1;
                        });
                    }
                    for (var j in values) {
                        var v = values[j];
                        var r = $("<tr><td></td><td></td></tr>");
                        r.find("td:eq(0)").append('<input name="par'+i+'" class="par'+i+'" id="val'+v[0]+'" type="'+input_type+'" value="'+v[0]+'"/><b>'+v[1]+'</b>');
                        
                        if (v[2] != null) { // value has an associated subfilter

                            if (v[4] == 3) { // numeric
                                var el = $('<select class="rangeFrom">'+
                                                '<option value=">"> &#x2265; </option>'+
                                                '<option value="="> = </option>'+
                                                '<option value="<"> &#x2264; </option>'+
                                            '</select>'+
                                            '<input type="text" class="rangeFrom" value=""/>'+
                                            '<span id="trattino"> - </span>'+
                                            '<select class="rangeTo">'+
                                                '<option value="<"> &#x2264; </option>'+
                                            '</select>'+
                                            '<input type="text" class="rangeTo" value=""/>');

                            } else

                            if (v[4] == 2) { // date
                                var el = $('<select class="rangeFrom">'+
                                                '<option value=">"> &#x2265; </option>'+
                                                '<option value="="> = </option>'+
                                                '<option value="<"> &#x2264; </option>'+
                                            '</select>'+
                                            '<input type="text" class="rangeFrom" value=""/>'+
                                            '<span id="trattino"> - </span>'+
                                            '<select class="rangeTo">'+
                                                '<option value="<"> &#x2264; </option>'+
                                            '</select>'+
                                            '<input type="text" class="rangeTo" value=""/>');
                                $([el[1], el[4]]).datepicker({
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
                            } else

                            if (v[4] == 4) { // text
                                var el = $('<input id="addvalue'+v[2]+'" type="text" value="" onkeypress="validate2(event)"/>'); 
                            }

                            var td = r.find("td:eq(1)");
                            td.append(v[3]+"&nbsp;");
                            td.append(el);
                            td.attr("id", "cfgval"+v[2]);
                            td.addClass("cfgval1");
                            td.data("f_type", v[4]);
                            td.attr("data-f_id", v[2]);
                            td.data("disabled", true);
                            td.data("par_flt_id", i);
                            td.data("par_flt_value", v[0]);

                            el.prop("disabled", true);
                            if (input_type == "checkbox") {
                                r.find("td:eq(0)").children("input").click(function() {
                                    $(this).parent().siblings("td").find("input,select").prop("disabled",!$(this).is(":checked"));
                                    $(this).parent().siblings("td").data("enabled", $(this).is(":checked"));
                                });
                            } else if (input_type == "radio") {
                                var prev_el;
                                r.find("td:eq(0)").children("input").click(function() {
                                    if (prev_el) {
                                        prev_el.find("input,select").prop("disabled",true);
                                        prev_el.data("enabled",false);
                                    }
                                    prev_el = $(this).parent().siblings("td");
                                    prev_el.find("input,select").prop("disabled",false);
                                    prev_el.data("enabled",true);
                                });

                            }
                        }

                        //$("#cfgval"+i).append('<input name="par'+i+'" class="par'+i+'" id="val'+v[0]+'" type="'+input_type+'" value="'+v[0]+'"/><b>'+v[1]+'</b><br>');

                        $("#templconfigdialog #tval"+i).append(r);
                    }
                    
                    if (f_multival == true) {
                        $("#templconfigdialog #pf"+i).append('<em class="counter" id="cnt'+i+'" data-count_val="0"></em>');
                        $("#templconfigdialog .par"+i).change(function (index) {
                                return function() {
                                    var cnt = $("#templconfigdialog #cnt"+index).attr("data-count_val");
                                    if ($(this).prop('checked') == true)
                                        ++cnt;
                                    else
                                        --cnt;
                                    $("#templconfigdialog #cnt"+index).attr("data-count_val", cnt);
                                }
                            } (i)
                        );
                    }
                } else

                if (flt_type == 2) { // Date
                    $("#templconfigdialog #cfgval"+i).append(  '<select class="rangeFrom">'+
                                            '<option value=">"> &#x2265; </option>'+
                                            '<option value="="> = </option>'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<input type="text" class="rangeFrom" value=""/>'+
                                        '<span id="trattino"> - </span>'+
                                        '<select class="rangeTo">'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<input type="text" class="rangeTo" value=""/>');
                    $('#templconfigdialog #cfgval'+i).children('.rangeFrom').change(QueryGen.toggleStatus);
                        
                    $("#templconfigdialog #cfgval"+i).children(':input').datepicker({
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

                } else

                if (flt_type == 3) { // Numeric
                    $("#templconfigdialog #cfgval"+i).append(  '<select class="rangeFrom">'+
                                                '<option value=">"> &#x2265; </option>'+
                                                '<option value="="> = </option>'+
                                                '<option value="<"> &#x2264; </option>'+
                                            '</select>'+
                                            '<input type="number" step="0.1" maxlength="200" class="rangeFrom" value="" onkeypress="validate(event)"/>'+
                                            '<span id="trattino"> - </span>'+
                                            '<select class="rangeTo">'+
                                                '<option value="<"> &#x2264; </option>'+
                                            '</select>'+
                                            '<input type="number" step="0.1" maxlength="200" class="rangeTo" value="" onkeypress="validate(event)"/>');
                    $('#templconfigdialog #cfgval'+i).children('.rangeFrom').change(QueryGen.toggleStatus);
                } else

                if (flt_type == 4) { // Genid
                    // decide whether to instantiate textarea for batch input or not
                    var f_idButton = i;
                    if (qent.hasOwnProperty(flt.src_button_id)){
                        console.log(f_idButton, qent[flt.src_button_id].filters[flt.src_f_id].genid)
                        // decide whether to instantiate textarea for batch input or not
                        var htmlCode = '<p>Genealogy ID type: <select id="selgenidtype' + f_idButton +'">'
                        for (var g in qent[flt.src_button_id].filters[flt.src_f_id].genid) {
                            htmlCode += '<option>'+ qent[flt.src_button_id].filters[flt.src_f_id].genid[g] +'</option>'
                        }
                    }
                    else{
                        var htmlCode = '<p>Genealogy ID type: <select id="selgenidtype' + f_idButton +'">'
                        var arrayGenid = ['Aliquot', 'Mouse', 'Derived aliquot'];
                        for (var g in arrayGenid) {
                            htmlCode += '<option>'+ arrayGenid[g] +'</option>'
                        }

                    }
                    htmlCode += '</select></p>'

                    htmlCode += '<table id="genid'+ f_idButton + '">'+ 
                                '<thead style="font-size: 10px"> <th style="width: 40px" class="add"></th> </thead> <tbody>  <tr> <td style="width: 40px" class="add"> '+ 
                                '<span id="add_gid'+ f_idButton +'" class="add_btn" style="margin-right:5px;">add</span> </td> </tr> </tbody> </table> <br>'+
                                '<div> <table> <tr> <td> <span style="font-size:10px;margin-right:10px;">Load Genealogy IDs from file:</span> </td> <td> <form id="genidfrm' + f_idButton + '"><input type="file" id="genidfile' + f_idButton +'" /></form> </td> </tr>' +
                                '<tr> <td> <span style="font-size:10px;margin-right:10px;">Insert full Genealogy IDs:<br>(newline or blank separated)</span> </td> <td> ' +
                                '<textarea id="fullgenid'+ f_idButton + '" type="text" style="width:500px;height:80px; resize:none" maxlength="20000"></textarea></td> <td> <span id="add_gid2_' + f_idButton +'" class="add_btn" style="margin-right:5px;">add</span> </td> </tr> </table> </div> <br> <div id="genidlist'+ f_idButton + '" style="max-height: 200px;overflow: auto;"></div>'

                    $("#templconfigdialog #cfgval"+f_idButton).append(htmlCode);
                    

                    $("#fullgenid" + f_idButton).boxlist({
                            bMultiValuedInput: true,
                            oBtnEl: $("#add_gid2_" + f_idButton),
                            oContainerEl: $("#genidlist" + f_idButton),
                            fnEachParseInput: function(v) {
                                v = v.trim();
                                if (v.length == 0) {
                                    return v;
                                } else if (v.length < 26) {
                                    v = v + new Array(26 - v.length + 1).join("-");
                                } else if (v.length > 26) {
                                    v = v.substr(0, 26);
                                }
                                return v.toUpperCase();
                            },
                            fnValidateInput: function(val) {
                                var ok;
                                console.log(val);
                                for (var t in genid) {
                                    var fields = genid[t].fields;
                                    ok = true;
                                    for (var j = 0; j < fields.length && ok; ++j) {
                                        var f = fields[j];
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
                            },

                            aoAltInput: [
                                {
                                    oBtnEl: $("#add_gid" + f_idButton),
                                    fnParseInput: genIdFromForm
                                }
                            ]
                        });

                    $("#genidfile" + f_idButton).change(function() {
                            var r = new FileReader();
                            r.onload = function(evt) {
                                $("#fullgenid" +f_idButton ).val(evt.target.result);
                                $("#add_gid2_" +f_idButton ).click();
                                $("#genidfrm" +f_idButton )[0].reset();
                            }
                            r.readAsText($("#genidfile" + f_idButton )[0].files[0]);
                        });

                    $("#selgenidtype" + f_idButton ).change(function() {
                            
                            var t = $(this).val();
                            
                            try {
                                var fields = genid[t].fields;
                            }
                            catch(err) {
                                return;
                            }
                            $("table#genid"+ f_idButton + " th.field,table#genid" + f_idButton + " td.field").remove();
                            for (var j = 0; j < fields.length; ++j) {
                                $('<th class="field">' + fields[j].name + '</th>').insertBefore("table#genid" + f_idButton +" th.add");
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
                                $(x).insertBefore("table#genid" + f_idButton +" td.add");
                            }
                        });

                        $("#selgenidtype" + f_idButton ).prop("selectedIndex", 0).change();

                } else

                if (flt_type == 5) { // Text with autocomplete
                    var flt_batchInput = true;
                    var flt_fileInput = true;
                    var flt_multiValued = true;
                    var flt_api_id = null;

                    if (qent.hasOwnProperty(flt.src_button_id)){
                        flt_batchInput = qent[flt.src_button_id].filters[flt.src_f_id].batchInput;
                        flt_fileInput = qent[flt.src_button_id].filters[flt.src_f_id].fileInput;
                        flt_multiValued = qent[flt.src_button_id].filters[flt.src_f_id].multiValued;
                        flt_api_id = qent[flt.src_button_id].filters[flt.src_f_id].api_id;
                    }

                    $("#templconfigdialog #cfgval"+i).append('<input id="addvalue'+i+'" type="text" value="" onkeypress="validateText(event,'+  i +')"/>'); //validate2
                    if (flt_api_id){
                        var url = autocomplete_api_url + "?id=" + flt_api_id;
                        $('#templconfigdialog #addvalue'+i).autocomplete({
                            source: (function(u) {
                                        return function(request, response) {
                                            $.ajax({
                                                url: u,
                                                dataType: "jsonp",
                                                data: {
                                                    term: request.term
                                                },
                                                success: function(data) {
                                                    response(data)
                                                }
                                            });
                                        }
                                    }) (url)
                        });
                    }
                    // decide whether to instantiate boxlist for multivalue or not
                    if (flt_multiValued == true) {
                        $("#templconfigdialog #cfgval"+i).data("multiValued", true);
                        $("#templconfigdialog #cfgval"+i).append('<span class="add_btn" id="add_btn'+i+'">add</span>');
                        $("#templconfigdialog #addvalue"+i).boxlist();
                    } else {
                        $("#templconfigdialog #cfgval"+i).data("multiValued", false);
                    }
                }
                else

                if (flt_type == 7) { // WG

                    var myGroups = [];
                    for (var j in qent[flt.src_button_id].filters[flt.src_f_id].values) {
                        var v = qent[flt.src_button_id].filters[flt.src_f_id].values[j];
                        if (workingGroupsList.indexOf(v[1]) >= 0 ) { //&& v[1]!='admin'
                            myGroups.push(v);
                        }
                    }

                    var input_type = qent[flt.src_button_id].filters[flt.src_f_id].multiValued == true ? "checkbox" : "radio";
                    $("#templconfigdialog #cfgval"+i).addClass("valuesovf");
                    $("#templconfigdialog #cfgval"+i).append("<table id='tval"+i+"' style='width: 99%'><tbody></tbody></table>");

                    for (var j = 0; j < myGroups.length; ++j) {
                        var v = myGroups[j];
                        var r = $("<tr><td></td><td></td></tr>");
                        r.find("td:eq(0)").append('<input name="par'+i+'" class="par'+i+'" id="val'+v[0]+'" type="'+input_type+'" value="'+v[0]+'" /><b>'+v[1]+'</b>');
                        $("#templconfigdialog #tval"+i).append(r);
                    }
                        
                    $("#templconfigdialog #pf"+i).append('<em class="counter" id="cnt'+i+'" data-count_val="0"></em>');
                    
                    $("#templconfigdialog .par"+i).change(function (index) {
                            return function() {
                                var cnt = $("#templconfigdialog #cnt"+index).attr("data-count_val");
                                if ($(this).prop('checked') == true)
                                    ++cnt;
                                else
                                    if (cnt != 1){
                                        --cnt;
                                    }
                                    else{
                                        alert('You should select at least one WG');
                                        $(this).prop('checked', true);
                                    }
                                $("#templconfigdialog #cnt"+index).attr("data-count_val", cnt);
                            }
                        } (i)
                    );
                }

                $("#templconfigdialog .cfgval").hide();
                $("#templconfigdialog .counter").hide();

                $("#templconfigdialog .cfgchk").change(
                    function () {
                        var f_id = $(this).data("f_id");
                        $("#templconfigdialog #cfgval" + f_id).toggle($(this).prop('checked'));
                        $("#templconfigdialog #cnt" + f_id).toggle($(this).prop('checked'));
                    }
                );
               
            }
        }

        // populate inputs tab
        var inTerminal = $("p#box" + block_id).data("inTerminal");
        for (var i = 0; i < t.inputs.length; ++i) {
            $("#templconfigdialog #templinputs ul").append('<li><a href="#templ-inp-' +i + '">Input ' + (i+1) + '</a></li>');
            $("#templconfigdialog #templinputs").append('<div id="templ-inp-' +i + '"></div>');
            
            var current_has_input = false;
            var msg = "Input currently disconnected.";

            connTerminal = inTerminal[i].getConnectedTerminals()[0];
            
            if (connTerminal !== undefined) {
                var connBlock = connTerminal.parentEl;
                var connBlockId = $(connBlock).attr("data-block_id");

                msg = "Input connected to start block.";
                if (connBlockId != QueryGen.startName) {
                    current_has_input = true;
                    var connNode = QueryGen.getGraphNode(connBlockId);
                    var out_type = connNode.output_type_id;

                    if (out_type != undefined) {
                        if (out_type == t.inputs[i].qent_id) {
                            current_has_input = false;
                            msg = "Input connected to entity of the same type."
                        } else {
                            $("#templconfigdialog #templ-inp-" + i).append('<p class="valuesovf" id="templ-in-list-'+i+'"></p>')
                            var all_paths = qent[out_type].fw_query_paths;
                            for (var j in all_paths) {
                                var p = all_paths[j];
                                if (p.toEntity == t.inputs[i].qent_id) {
                                    $("#templconfigdialog #templ-in-list-"+i).append('<input id="in'+j+'" name="inputpaths'+i+'" type="radio" value="'+j+'"/><label for="in'+j+'"><b>'+p.name+'</b>&nbsp;&nbsp;'+(p.description || "")+'</label><br>');
                                    if (p.isDefault == true) {
                                        $("#templconfigdialog #templ-in-list-"+i+" #in"+j).prop("checked", true);
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (!current_has_input) {
                $("#templconfigdialog #templ-inp-" + i).append("<p>" + msg + "</p>");
            }
        }

        $("#templconfigdialog #templinputs").tabs();

        // populate output tab
        if (t.outputsList.length == 0) {
            var o = qent[out_btn].outputs;
            for (var i in o) {
                $("#templconfigdialog #templ-config-out-list").append('<input id="out'+i+'" type="checkbox" value="'+i+'"/><label for="out'+i+'"><b>'+o[i].name+'</b></label><br>');
            }
        } else {
            var o = t.outputsList;
            for (var i = 0; i < t.outputsList.length; ++i) {
                $("#templconfigdialog #templ-config-out-list").append('<input id="out'+i+'" type="checkbox" value="'+i+'"/><label for="out'+i+'"><b>'+o[i]+'</b></label><br>');
            }
        }

        // restore previous values (if any)

        // filters
        var params = QueryGen.getGraphNode(block_id).parameters;
        if (params.length > 0) {
            for (var j = 0; j < params.length; ++j) { 
                var f_id = params[j]['f_id'];
                console.log(f_id);
                //if ($('#templconfigdialog #if' + f_id).prop('checked') == false)
                    $('#templconfigdialog #if' + f_id).trigger('click');
                var f_type = $("#templconfigdialog #cfgval"+f_id).data("f_type");

                if (f_type == 7){
                    $('#if'+f_id).prop('disabled','true');
                }
                
                if (f_type == 1 || f_type == 6 || f_type == 7 ) { // predefined list or boolean
                    console.log(params[j])
                    for (var i = 0; i < params[j]['values'].length; ++i) {
                        $("#templconfigdialog .par"+f_id+"#val"+params[j]['values'][i]).trigger('click');
                    }
                } else

                if (f_type == 4 ) { // genid
                    for (var i = 0; i < params[j]['values'].length; ++i) {
                            $("#templconfigdialog #fullgenid"+f_id).val(params[j]['values'][i]);
                            $("#templconfigdialog span#add_gid2_" + f_id).trigger('click');
                    }
                } else

                if (f_type == 5) { // text with or without autocomplete
                    for (var i = 0; i < params[j]['values'].length; ++i) {
                        $("#templconfigdialog #addvalue"+f_id).val(params[j]['values'][i].slice(1));
                        $("#templconfigdialog #add_btn"+f_id).trigger('click');
                    }
                } else

                if (f_type == 3) { // numeric
                    var from = params[j]['values'][0];
                    from = from.slice(1); // skip past 'c' or 'u'
                    $("#templconfigdialog #cfgval"+f_id).children("select.rangeFrom").val(from[0]);
                    from = from.slice(1); // skip past '>', '=' or '<'
                    $("#templconfigdialog #cfgval"+f_id).children("select.rangeFrom").trigger('change');

                    $("#templconfigdialog #cfgval"+f_id).children("input.rangeFrom").val(from);

                    if (params[j]['values'].length > 1) {
                        var to = params[j]['values'][1];
                        to = to.slice(1);
                        $("#templconfigdialog #cfgval"+f_id).children("select.rangeTo").val(to[0]);
                        to = to.slice(1);
                        $("#templconfigdialog #cfgval"+f_id).children("input.rangeTo").val(to);
                    }
                } else

                if (f_type == 2) { // date
                    var from = params[j]['values'][0];
                    from = from.slice(1);
                    $("#templconfigdialog #cfgval"+f_id).children("select.rangeFrom").val(from[0]);
                    from = from.slice(1);
                    $("#templconfigdialog #cfgval"+f_id).children("select.rangeFrom").trigger('change');
                    
                    $("#templconfigdialog #cfgval"+f_id).children("input.rangeFrom").val(from);

                    if (params[j]['values'].length > 1) {
                        var to = params[j]['values'][1];
                        to = to.slice(1);
                        $("#templconfigdialog #cfgval"+f_id).children("select.rangeTo").val(to[0]);
                        to = to.slice(1);
                        $("#templconfigdialog #cfgval"+f_id).children("input.rangeTo").val(to);
                        $("#templconfigdialog #cfgval"+f_id).children("input.rangeFrom").datepicker("option", "maxDate", to);
                        $("#templconfigdialog #cfgval"+f_id).children("input.rangeTo").datepicker("option", "minDate", from);
                    }
                }
            }
        }

        // outputs
        // make list of outputs from current block that are referenced through correlation by next block
        var block = $("#box"+block_id);
        var outTerminal = block.data("out-terminal")[0];
        var outConnTerminal = outTerminal.getConnectedTerminals()[0];
        if (outConnTerminal !== undefined && $(outConnTerminal.parentEl).attr("id") != "end") {
            var outConnBlock = outConnTerminal.parentEl;
            var outConnBlockId = $(outConnBlock).attr("data-block_id");
            var corr_outs = QueryGen.findCorrelatedOutputs(outConnBlockId);
        } else {
            var corr_outs = [];
        }

        var outputs = QueryGen.getGraphNode(block_id).outputs;

        for (var j = 0; j < outputs.length; ++j) {
            if (outputs[j] != undefined) {
                $("#templconfigdialog #out"+outputs[j]).prop("checked", true);
                if (corr_outs.indexOf(j) != -1) {
                    $("#templconfigdialog #out"+outputs[j]).click(function() {alert("Output is in use by next block.", "Cannot uncheck"); $(this).prop("checked", true);});
                }
            }
        }

        // inputs
        var inputs = QueryGen.getGraphNode(block_id).query_path_id;
        for (var z = 0; z < t.inputs.length; ++z) {
            var paths = $("#templconfigdialog #templ-in-list-" + z + " input");
            // if previous entity is the same as the current one, then there is no path in the input tab -- this case is handled separately even in the query engine
            if (paths.length > 0) {
                paths.filter("[value=" + inputs[z] + "]").prop("checked", true);
            }
        }                        

        // configure behavior when dialog buttons are clicked
        $("#templconfigdialog").dialog("option", {
            buttons:
            [
                {
                    text: "Remove all filters",
                    click: function() {
                        $("#templconfigdialog .cfgchk").prop('checked', false).change();
                    }
                },
                {
                    text: "Ok",
                    click: function() {
                        // save parameters
                        var params = [];
                        var checkboxes = $("#templconfigdialog .cfgchk:checked");
                        var subfilters = $("#templconfigdialog td.cfgval1").filter(function() {return $(this).data("enabled")});
                        checkboxes.add(subfilters).each(function() {

                            //alert('block='+block_id+' par_id='+$(this).attr('data-par_id'));
                            var f_id = $(this).attr('data-f_id');
                            var cfgval = $("#templconfigdialog #cfgval"+f_id);
                            var f_type = cfgval.data("f_type");

                            var v_list = [];

                            if (cfgval.data("par_flt_id") != undefined) {
                                var par_flt_id = cfgval.data("par_flt_id");
                                var par_flt_value = cfgval.data("par_flt_value");
                            } else {
                                var par_flt_id = null;
                                var par_flt_value = null;
                            }
                            
                            if (f_type == 1 || f_type == 6 || f_type == 7) { // predefined list or boolean
                                
                                cfgval.find("input.par"+f_id+":checked").each(function() {
                                    v_list.push($(this).val());
                                });

                                
                            } else if (f_type == 2 || f_type == 3) { // date or numeric
                                
                                var val;
                                val = 'u' + cfgval.children("select.rangeFrom").val() + cfgval.children("input.rangeFrom").val().trim();
                                notEmpty = val.length > 2;
                                if (notEmpty) v_list.push(val);

                                if (!cfgval.children('select.rangeTo').prop('disabled')) {
                                    val = 'u' + cfgval.children("select.rangeTo").val() + cfgval.children("input.rangeTo").val().trim();
                                    notEmpty = val.length > 2;
                                    if (notEmpty) v_list.push(val);
                                }
                                
                            } else if ( f_type == 5) { // text with or without autocomplete
                                var v_list = [];
                                if (cfgval.data("multiValued") == true) {
                                    v_list = $("#templconfigdialog #addvalue"+f_id).boxlist("getValues").map(function(x) {return 'u'+x});
                                } else {
                                    var x = 'u' + $("#templconfigdialog #addvalue"+f_id).val();
                                    if (x.length > 1) {
                                        v_list.push(x);
                                    }
                                }
                            } else if ( f_type == 4) { // genid
                                console.log( $("#templconfigdialog #fullgenid" +f_id ).boxlist("getValues") );
                                var v_list = $("#templconfigdialog #fullgenid" +f_id ).boxlist("getValues");                               
                            }

                            if (v_list.length > 0) {
                                var dic = {'f_id':f_id, 'values': v_list};
                                if (par_flt_id != null) {
                                    $.extend(dic, {'par_flt_id': par_flt_id, 'par_flt_value': par_flt_value});
                                }
                                params.push(dic);
                            }
                                
                        });
                        QueryGen.setGraphNodeAttr(block_id, 'parameters', params);
                        if (QueryGen.getGraphNode(block_id).parameters.length > 0) {
                            $("p#box"+block_id).children("span#led").removeClass("filteroff").addClass("filteron");
                        } else {
                            $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff");
                        }

                        // save inputs
                        var query_path_id = n.query_path_id;
                        for (var z = 0; z < t.inputs.length; ++z) {
                            var paths = $("#templconfigdialog #templ-in-list-" + z + " input");
                            // if previous entity is the same as the current one, then there is no path in the input tab -- this case is handled separately even in the query engine
                            if (paths.length > 0) {
                                query_path_id[z] = paths.filter(":checked").val();
                            } else {
                                query_path_id[z] = null;
                            }
                        }

                        //save outputs
                        var outs = [];
                        $("#templconfigdialog #templ-config-out-list input:checked").each(function() {outs.push($(this).val());});
                        var old_outs = QueryGen.getGraphNode(block_id).outputs;
                        // delete outputs that have been de-selected
                        for (var i = 0; i < old_outs.length; ++i) {
                            if (outs.indexOf(old_outs[i]) == -1) {
                                old_outs[i] = undefined;
                            }
                        }
                        // append new outputs
                        for (var i = 0; i < outs.length; ++i) {
                            if (old_outs.indexOf(outs[i]) == -1) {
                                old_outs.push(outs[i]);
                            }
                        }

                        $(this).dialog("close");                                                                                         
                    }
                }
            ],
            beforeClose: function(event, ui) {
                // clear inputs
                $("#templconfigdialog #templinputs").tabs("destroy");
                $("#templconfigdialog #templinputs ul li").remove();
                $("#templconfigdialog #templinputs div").remove();
                // clear outputs
                $("#templ-config-out-list").children().remove();
                // clear filters
                $("#templconfig-flt ul li").remove();
                // run dialog close handler
                QueryGen.handle_dialog_close.runHandler(block_id);                
            }
        });
    },

    prepareExtendDialog: function(block_id, outTerm) {
        
        var connBlock = QueryGen.getGraphNode(block_id).w_in[0];
        var connBType = QueryGen.getGraphNode(connBlock).output_type_id;
        
        var r = GUI.getManyToOneRelationships2(connBType);
        var fw_query_paths = qent[connBType].fw_query_paths;
                
        $("#extenddialog #ent-list").children().remove();
        
        // populate list of entities
        for (var i = 0; i < r.length; ++i) {
            $("#extenddialog #ent-list").append('<input class="qp" id="qp'+r[i]+'" type="checkbox" value="'+r[i]+'" data-toEntity="'+fw_query_paths[r[i]].toEntity+'"/><label for="qp'+r[i]+'" title="'+(fw_query_paths[r[i]].description || "")+'"><b>'+qent[fw_query_paths[r[i]].toEntity].name+'</b>&nbsp;(Path: <i>'+fw_query_paths[r[i]].name+'</i>)</label><br>');
            var ul = $("<ul></ul>");
            ul.hide();
            ul.css("list-style-type", "none")
              .css("margin-top", "3px")
              .css("margin-bottom", "0px")
              .css("padding-left", "25px");
            var qent_id = fw_query_paths[r[i]].toEntity;
            for (var x in qent[qent_id].outputs) {
                ul.append('<li><input class="out" id="out'+x+'" type="checkbox" value="' + x + '"/><label for="out' + x + '">' + qent[qent_id].outputs[x].name + '</label>');
            }
            $("#extenddialog #ent-list").append(ul);
        }

        // display entity attributes when entity is checked
        $("#extenddialog #ent-list input.qp").change(function() {
            if ($(this).prop("checked") == true) {
                $(this).next().next().next().show();
            } else {
                if ($(this).hasClass("noRemove")) {
                    alert("One or more outputs from this entity are in use by next block", "Cannot uncheck");
                    $(this).prop("checked", true);
                } else {
                    $(this).next().next().next().hide();
                }
            }
        });

        // restore previously checked attributes

        // first make a list of outputs from current block that are referenced through correlation by next block
        var block = $("#box"+block_id);
        var outTerminal = block.data("out-terminal")[0];
        var outConnTerminal = outTerminal.getConnectedTerminals()[0];
        if (outConnTerminal !== undefined && $(outConnTerminal.parentEl).attr("id") != "end") {
            var outConnBlock = outConnTerminal.parentEl;
            var outConnBlockId = $(outConnBlock).attr("data-block_id");
            var corr_outs = QueryGen.findCorrelatedOutputs(outConnBlockId);
        } else {
            var corr_outs = [];
        }

        var params = QueryGen.getGraphNode(block_id).parameters || [];
        for (var i = 0; i < params.length; ++i) {
            if (params[i] != undefined) {
                $("#extenddialog #ent-list #qp" + params[i].query_path_id).prop("checked", true).change();
                $("#extenddialog #ent-list #out" + params[i].out_id).prop("checked", true);

                // check if output is in use in next block (correlation) and, if so, disable it so it can't be unchecked
                if (corr_outs.indexOf(i) != -1) {
                    $("#extenddialog #ent-list #out" + params[i].out_id).click(function() {alert("Output is in use by next block", "Cannot uncheck"); $(this).prop("checked", true);});;
                    $("#extenddialog #ent-list #qp" + params[i].query_path_id).addClass("noRemove");
                }
            }
        }

        // configure behavior when dialog buttons are clicked
        $("#extenddialog").dialog({
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
                        // save selected outputs
                        var out = [];
                        $("#extenddialog #ent-list input.out:checked").each(function() {
                            var out_id = $(this).val();
                            var par_input_el = $(this).parent().parent().prev().prev().prev();
                            if (par_input_el.prop("checked") == true) {
                                var ent_id = par_input_el.data("toentity");
                                var qp_id = par_input_el.val();
                                out.push([ent_id, out_id, qp_id]);
                            }
                        });
                        
                        var old_outs = QueryGen.getGraphNode(block_id).outputs;
                        var old_params = QueryGen.getGraphNode(block_id).parameters;

                        // delete stale outputs
                        for (var i = 0; i < old_params.length; ++i) {
                            var p = old_params[i];
                            if (p != undefined && p.query_path_id != "self") {
                                // look for p in out
                                var found = false;
                                for (var j = 0; found == false && j < out.length; ++j) {
                                    if (out[j][2] == p.query_path_id && out[j][1] == p.out_id) {
                                        found = true;
                                    }
                                }
                                if (found == false) {
                                    old_outs[i] = undefined;
                                    old_params[i] = undefined;
                                }
                            }
                        }

                        // delete trailing undefined entries
                        for (var l = old_outs.length-1; l >= 0; --l) {
                            if (old_outs[l] == undefined) {
                                --old_outs.length;
                                --old_params.length;
                            } else {
                                break;
                            }
                        }

                        // add new outputs
                        for (var i = 0; i < out.length; ++i) {
                            var o = out[i];
                            // look for o in old_params
                            var found = false;
                            for (var j = 0; found == false && j < old_params.length; ++j) {
                                if (old_params[j] != undefined) {
                                    if (old_params[j].query_path_id == o[2] && old_params[j].out_id == o[1]) {
                                        found = true;
                                    }
                                }
                            }
                            if (found == false) {
                                old_outs.push("e" + qent[o[0]].name + "_" + qent[o[0]].outputs[o[1]].name); // "e" stands for "extended entity"
                                old_params.push({query_path_id: o[2], out_id: o[1]});
                            }
                        }

                        if (out.length > 0) {
                            $("p#box"+block_id).children("span#led")
                                               .removeClass("filteroff2")
                                               .addClass("filteron");
                            // update output type
                            QueryGen.setGraphNodeAttr(block_id, "output_type_id", connBType);
                        } else {
                            $("p#box"+block_id).children("span#led")
                                               .removeClass("filteron")
                                               .addClass("filteroff2");
                           // disconnect out wire
                           outTerminal.removeAllWires();
                           // update output type
                            QueryGen.setGraphNodeAttr(block_id, "output_type_id", undefined);
                            // if template mode is on, close it, since extend block needs configuration
                            if (QueryGen.template.in_template) {
                                QueryGen.backToDesign();
                            }
                        }
                        
                        $(this).dialog("close");
                    }
                 }
            ]
        });
    },

    prepareGBDialog: function(block_id, outTerm) {
        
        var connBlockId = QueryGen.getGraphNode(block_id).w_in[0];
        var connBType = QueryGen.getGraphNode(connBlockId).output_type_id;
        
        var r = GUI.getManyToOneRelationships(connBType);
                
        $("#gbdialog select#selattr").children().remove();
        for (var i=0; i<r.length; ++i) {
            $("#gbdialog select#selattr").append('<option value="'+r[i]+'">'+GUI.getButtonName(r[i])+'</value>');
        }
        // assign handler to re-populate input tab whenever grouping entity changes
        $("#gbdialog select#selattr").change(function() {
            // populate input tab
            $("#gbdialog #gbconfig-in-list").children().remove();

            var out_type = $(this).val();
            var all_paths = qent[connBType].fw_query_paths;
            for (var i in all_paths) {
                var p = all_paths[i];
                if (p.toEntity == out_type && p.oneToMany == true){
                    $("#gbdialog #gbconfig-in-list").append('<input id="in'+i+'" name="inputpaths" type="radio" value="'+i+'"/><label for="in'+i+'"><b>'+p.name+'</b>&nbsp;&nbsp;'+(p.description || "")+'</label><br>');
                    if (p.isDefault == true) {
                        $("#gbdialog #gbconfig-in-list #in"+i).prop("checked", true);
                    }
                }
            }
            // if there is no default path, select the first one
            if ($("#gbdialog #gbconfig-in-list input:checked").length == 0) {
                $("#gbdialog #gbconfig-in-list input:eq(0)").prop("checked", true);
            }
        }).change(); // trigger event to populate

        $("#gbdialog #gbconfig-flt-list,#gbconfig-out-list").children().remove();
        $("#gbdialog #gbconfigtabs").tabs("option", "active", 0)
                                        
        //$('input,select').keypress(function(event) { return event.keyCode != 13; }); //disable enter key
        
        // populate drop-down attribute list
        // differentiate whether previous block is entity, extend op or group by
        var connButtonCat = QueryGen.getGraphNode(connBlockId).button_cat;
        var connButtonId = QueryGen.getGraphNode(connBlockId).button_id;
        if (connButtonCat == "qent") {
             var o = qent[connBType].outputs;
        } else
        if (connButtonCat == "op" && connButtonId == 7) {
            var o = QueryGen.getGraphNode(connBlockId).outputs
                    .map(function (el) {
                        return {name: el};
                    })
                    .reduce(function (prev,curr,ind) {
                        prev['c' + connBlockId + '_' + ind] = curr; // mark this as "correlated"
                        return prev;
                    }, {} );
        } else
        if (connButtonCat == "op" && connButtonId == 4) {
             // add both entity attributes and aggregate attributes from the group by outputs
            var o = QueryGen.getGraphNode(connBlockId).outputs
                    .map(function (el) {
                        return {name: el.name};
                    })
                    .reduce(function (prev,curr,ind) {
                        prev['c' + connBlockId + '_' + ind] = curr; // mark this as "correlated"
                        return prev;
                    }, {} );
            $.extend(true, o, qent[connBType].outputs);
        }
        $("#gbdialog").data("outs", $.extend(true, {}, o));

        // restore previous group-by entity
        var old_gb_attr = QueryGen.getGraphNode(block_id).gb_entity;
        if (old_gb_attr) {
            $("#gbdialog select#selattr").val(old_gb_attr);
        }
        
        // restore previous filters (if any)
        var next_uid = 0;
        var params = QueryGen.getGraphNode(block_id).parameters;
        var old_gb_attr;
        for (var i = 0; i < params.length; ++i) {
            $("#gbdialog #gbitemadd-flt").click();
            var p = $("#gbdialog #gbconfig-flt-list p.gbitem").last();
            var f = params[i];
            p.children(":eq(0)").val(f.op);
            p.children(":eq(1)").val(f.attr);
            if (f.values.length == 0){
                QueryGen.jsonStrGraph[block_id].parameters[i].values = ['u>1'];
                var v = 'u>1';
            }
            else{
                var v = f.values[0];
            }
                // first character is 'u' (always uncorrelated), skip it
            
            p.children(":eq(2)").val(v[1]).change();
            p.children(":eq(3)").val(v.substr(2));
            if (f.values.length > 1) {
                v = f.values[1];
                p.children(":eq(5)").val(v[1]);
                p.children(":eq(6)").val(v.substr(2));
            }
            
            // retrieve and set filter's unique identifier
            p.data("uid", f.uid);
            if (f.uid >= next_uid)
                next_uid = f.uid + 1;

        }
        $("#gbdialog").data("next_uid", next_uid);

        // restore previous outputs (if any)
        
        // make list of outputs from current block that are referenced through correlation by next block
        var block = $("#box"+block_id);
        var outTerminal = block.data("out-terminal")[0];
        var outConnTerminal = outTerminal.getConnectedTerminals()[0];
        if (outConnTerminal !== undefined && $(outConnTerminal.parentEl).attr("id") != "end") {
            var outConnBlock = outConnTerminal.parentEl;
            var outConnBlockId = $(outConnBlock).attr("data-block_id");
            var corr_outs = QueryGen.findCorrelatedOutputs(outConnBlockId);
        } else {
            var corr_outs = [];
        }

        var outs = QueryGen.getGraphNode(block_id).outputs;
        for (var i = 0; i < outs.length; ++i) {
            if (outs[i] != undefined) {
                $("#gbdialog #gbitemadd-out").click();
                var p = $("#gbdialog #gbconfig-out-list p.gbitem").last();
                var o = outs[i];
                p.children(":eq(0)").val(o.op);
                p.children(":eq(1)").val(o.attr);
                p.children(":eq(3)").val(o.name);

                // check if output is in use in next block (correlation) and, if so, disable it so it can't be deleted
                if (corr_outs.indexOf(i) != -1) {
                    $("#gbconfig-out-list p.gbitem:last span.gbitemdel").addClass("noRemove");
                }

            }
        }

        // configure behavior when dialog buttons are clicked
        $("#gbdialog").dialog({
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
                        var gb_attr = $('#gbdialog select#selattr').val();
                        var gb_cnt = $("#gbdialog input#addnum").val();
                        if (gb_cnt == '') {
                            alert("Please specify a counting condition.", "Oops!");
                        } else {
                            
                            // save filters
                            var flt = [];

                            $("#gbdialog #gbconfig-flt-list p.gbitem").filter(function() {return $(this).children("select:eq(1)").val()!=null})
                                                            .each(function() {
                                                                var values = [];
                                                                var v = $(this).children(":eq(3)").val();
                                                                if (v != "") values.push('u' + $(this).children(":eq(2)").val() + v);
                                                                v = $(this).children(":eq(6):enabled").val();
                                                                if (v && v != "") values.push('u' + $(this).children(":eq(5)").val() + v);
                                                                if (values.length == 0) return;
                                                                var f = {};
                                                                f.op = $(this).children(":eq(0)").val();
                                                                f.attr = $(this).children(":eq(1)").val();
                                                                f.values = values;
                                                                f.uid = $(this).data("uid");
                                                                flt.push(f);
                                                            });
                            QueryGen.setGraphNodeAttr(block_id, "parameters", flt);
                            if (flt.length > 0) {
                                $("p#box"+block_id).children("span#led").removeClass("filteroff2").addClass("filteron");
                                // save group-by entity
                                QueryGen.setGraphNodeAttr(block_id, 'gb_entity', gb_attr);
                                // non serve più: QueryGen.setGraphNodeAttr(block_id, 'connBlock', GUI.getButtonName(connBType));
                                QueryGen.setGraphNodeAttr(block_id, "output_type_id", parseInt(gb_attr));
                            } else {
                                $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff2");
                                // if template mode is on, close it, since group by block needs configuration
                                if (QueryGen.template.in_template) {
                                    QueryGen.backToDesign();
                                }
                            }

                            // save outputs
                            var out = [];
                            $("#gbdialog #gbconfig-out-list p.gbitem").filter(function() {return $(this).children("select:eq(1)").val()!=null})
                                                            .each(function() {
                                                                var attr = $(this).children(":eq(1)").val();
                                                                if (attr == null) return;
                                                                var o = {};
                                                                o.op = $(this).children(":eq(0)").val();
                                                                o.attr = attr;
                                                                var name = $(this).children(":eq(3)").val();
                                                                if (name == "") {
                                                                    name = o.op + "(" + $(this).children(":eq(1)").children("option:selected").text() + ")";
                                                                }
                                                                o.name = name;
                                                                out.push(o);
                                                            });
                            var old_outs = QueryGen.getGraphNode(block_id).outputs;
                            // delete outputs that have been deleted
                            for (var i = 0; i < old_outs.length; ++i) {
                                if (old_outs[i] != undefined) {
                                    if (out.filter(function(e) {
                                            return e.op == old_outs[i].op && e.attr == old_outs[i].attr;
                                        }).length == 0) {
                                        old_outs[i] = undefined;
                                    }
                                }
                            }
                            // append new outputs
                            for (var i = 0; i < out.length; ++i) {
                                var thisOut = old_outs.filter(function(e) {
                                        return e != undefined && e.op == out[i].op && e.attr == out[i].attr;
                                    });
                                if (thisOut.length == 0) {
                                    old_outs.push(out[i]);
                                } else {
                                    if (thisOut[0].name != out[i].name) {
                                        thisOut[0].name = out[i].name;
                                    }
                                }
                            }

                            if (old_gb_attr != gb_attr) {
                                outTerm.removeAllWires();
                            }
                            
                            // save input
                            var query_path_id = $("#gbdialog #gbconfig-in-list input:checked").val();
                            QueryGen.setGraphNodeAttr(block_id, 'query_path_id', query_path_id);

                            // if template mode is on, update template
                            if (QueryGen.template.in_template == true) {
                                QueryGen.updateTemplateAndForm(block_id);
                            }

                            $(this).dialog("close");
                        }
                        
                    }
                }
            ],
            beforeClose: function() {
                // disable change event handler
                $("#gbdialog select#selattr").off("change");
                // run dialog close handler
                QueryGen.handle_dialog_close.runHandler(block_id);
            }
        });
    },
    
    prepareGenidDialog: function(block_id) {
        // restore previous values, if any
        var params = QueryGen.getGraphNode(block_id).parameters;
        $("#geniddialog #selgenidtype").prop("selectedIndex", 0).change();
        $("#geniddialog #fullgenid").boxlist("clearValues");
        if (params.length > 0) {
            //var list = [];
            //for (var i = 0; i < params[0]['values'].length; ++i) {
            //    list.push(params[0]['values'][i]);
            //}
            $("#geniddialog #fullgenid").val(params[0]['values'].join(" "));
            $("#geniddialog span#add_gid2").trigger('click');
        }
        // configure behavior when dialog buttons are clicked
        $("#geniddialog").dialog({
            buttons: 
            [
                {
                    text: "Clear all values",
                    click: function() {
                        $("#geniddialog #fullgenid").boxlist("clearValues");
                    }
                },
                {
                    text: "Ok",
                    click: function() {
                        var v_list = $("#geniddialog #fullgenid").boxlist("getValues");
                         
                        if (v_list.length > 0) {
                            QueryGen.setGraphNodeAttr(block_id, 'parameters', [{'param_name':'genid', values:v_list}]);
                            $("p#box"+block_id).children("span#led").removeClass("filteroff2").addClass("filteron");
                        } else {
                            QueryGen.setGraphNodeAttr(block_id, 'parameters', []);
                            $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff2");
                        }
                        $(this).dialog("close");
                    }
                }
            ]
        });
    },

    contextMenuHandler: function(e) {
        var el = $(e.target);
        el.addClass("clicked");
        var o = el.offset();
        var menu = $("#ctxmenu");
        menu.css("left", o.left + parseInt(el.css("width")) + 10);
        menu.css("top", o.top - 10);
        if (menu.data("target") && !menu.data("target").is(el)) menu.data("target").removeClass("clicked");
        menu.data("target", el);
        menu.find("#menu-item-" + el.data("menu-item")).prop("checked", true);
        menu.hide().fadeIn(100);

        e.stopPropagation();

        $("body").on("click.ctxmenu", function (e) {
            var el = $(e.target); // element (i.e., menu item, menu or anything else) clicked by user
            var mitem;
            var menu = $("#ctxmenu");
            var target = menu.data("target"); // element that initiated the menu (i.e., "correlate" button)
            
            // click on menu item
            if ((mitem = el.closest("p.menu-item")).length > 0) {
                var input_el = mitem.children("input.menu-item");
                var v = input_el.val();

                QueryGen.toggleCorrelation(target, v, input_el.data("label"));
                
                target.removeClass("clicked");
                menu.fadeOut(100);
                $("body").off("click.ctxmenu");
            } else

            // click anywhere else in the document
            if (el.closest("#ctxmenu").length === 0) {
                target.removeClass("clicked");
                menu.fadeOut(100);
                $("body").off("click.ctxmenu");
            }
        });
    },

    toggleCorrelation: function(target, v, label) {
        var prev = target.data("menu-item");
        target.data("menu-item", v);

        if (target.hasClass("corr-par")) {
            var chk = target.data("checkbox");
            var par = target.data("paragraph");
            chk.prop("checked", true);
            if (v != 0) {
                if (prev == 0) {
                    target.after($(QueryGen.correlationElements[target.data("type")]));
                }
                target.next().children("input:eq(0)").val(label);
                par.hide();
            } else {
                target.next().remove();
                par.show();
            }
        } else

        if (target.hasClass("corr-input")) {
            if (v != 0) {
                if (prev == 0) {
                    target.next().hide();
                    target.after($(QueryGen.correlationElements[target.data("type")]))
                }
                target.next().children("input:eq(0)").val(label);
            } else {
                if (prev != 0) {
                    target.next().remove();
                    target.next().show();
                }
            }
        }
    },
    
    prepareConfigDialog: function(block_id) {
        var n = QueryGen.getGraphNode(block_id);
        var btn_id = n.button_id;
        var btn = qent[btn_id];
        
        // set filter tab as the active one
        $("#configtabs").tabs("option", "active", 0)

        // populate context menu with outputs from previous block
        var menu = $("#ctxmenu");
        var block = $("#box"+block_id);
        var terminal = block.data("in-terminal")[0];
        var connTerminal = terminal.getConnectedTerminals()[0];
        if (connTerminal !== undefined) {
            var connBlock = connTerminal.parentEl;
            var connBlockId = $(connBlock).attr("data-block_id");
            if (connBlockId != QueryGen.startName) {
                var connNode = QueryGen.getGraphNode(connBlockId);
                var outs = connNode.outputs;
                var connBtn_id = connNode.button_id;
                menu.find("p.menu-item:eq(0)").siblings("p.menu-item").remove();
                // allow correlation with previous block only if block-1 is entity and block-1 and block have a many-to-one relationship
                // otherwise a group by should be used to correlate them
                if (connNode.button_cat == 'qent' && GUI.isManyToOneRelationship(connBtn_id, btn_id)) {
                    for (var j = 0; j < outs.length; ++j) {
                        if (outs[j] != undefined) {
                            var name = qent[connBtn_id].outputs[outs[j]].name;
                            var val = connBlockId+'_'+(j);
                            var el = $('<p class="menu-item"><input id="menu-item-'+(val)+'" class="menu-item" name="dd" type="radio" value="'
                                        +val+'" /><label for="menu-item-'+(val)+'">'+connBlockId +':' +name+'</label></p>');
                            el.find("input").data("label", connBlockId +':' + name);
                            menu.append(el);
                        }
                    }
                } else

                if (connNode.button_cat == 'op' && connBtn_id == 6 && GUI.isManyToOneRelationship(connNode.output_type_id, btn_id)) {
                    for (var j = 0; j < outs.length; ++j) {
                        if (outs[j] != undefined) {
                            var name = qent[connNode.output_type_id].outputs[outs[j]].name;
                            var val = connBlockId+'_'+(j);
                            var el = $('<p class="menu-item"><input id="menu-item-'+(val)+'" class="menu-item" name="dd" type="radio" value="'
                                        +val+'" /><label for="menu-item-'+(val)+'">'+connBlockId +':' +name+'</label></p>');
                            el.find("input").data("label", connBlockId +':' + name);
                            menu.append(el);
                        }
                    }
                } else

                if (connNode.button_cat == 'op' && connBtn_id == 4) {// group by
                    for (var j = 0; j < outs.length; ++j) {
                        if (outs[j] != undefined) {
                            var name = outs[j].name;
                            var val = connBlockId+'_'+(j);
                            var el = $('<p class="menu-item"><input id="menu-item-'+(val)+'" class="menu-item" name="dd" type="radio" value="'
                                        +val+'" /><label for="menu-item-'+(j+1)+'">'+connBlockId+':'+name+'</label></p>');
                            el.find("input").data("label", connBlockId +':' + name);
                            menu.append(el);
                        }
                    }
                } else

                if (connNode.button_cat == 'op' && connBtn_id == 7) {// extend
                    for (var j = 0; j < outs.length; ++j) {
                        if (outs[j] != undefined) {
                            var name = outs[j];
                            var val = connBlockId+'_'+(j);
                            var el = $('<p class="menu-item"><input id="menu-item-'+(val)+'" class="menu-item" name="dd" type="radio" value="'
                                        +val+'" /><label for="menu-item-'+(j+1)+'">'+connBlockId+':'+name.substr(1)+'</label></p>'); // "substr" removes the first character which is either 'e' meaning 'extended' (for attributes in the extended entity) or 's' meaning 'self' (for attributes in the original entity)
                            el.find("input").data("label", connBlockId +':' + name);
                            menu.append(el);
                        }
                    }
                }

                // populate input tab
                $("#configdialog #config-in-list").children().remove();

                var out_type = connNode.output_type_id;
                if (out_type != undefined) {
               
                    var all_paths = qent[out_type].fw_query_paths;
                    for (var i in all_paths) {
                        var p = all_paths[i];
                        if (p.toEntity == btn_id) {
                            $("#config-in-list").append('<input id="in'+i+'" name="inputpaths" type="radio" value="'+i+'"/><label for="in'+i+'"><b>'+p.name+'</b>&nbsp;&nbsp;'+(p.description || "")+'</label><br>');
                        }
                    }
                }

            }
        } else {
            menu.find("p.menu-item:eq(0)").siblings("p.menu-item").remove();

            // remove elements from input tab
            $("#configdialog #config-in-list").children().remove();
        }

        // populate outputs tab
        for (var i in btn.outputs) {
            $("#configdialog #config-out-list").append('<input id="out'+i+'" type="checkbox" value="'+i+'"/><label for="out'+i+'"><b>'+btn.outputs[i].name+'</b></label><br>');
        }

        // populate filters tab
        $("#configdialog").dialog({title: btn.name + ' configuration'});
        for (var i in btn.filters) {
            var f = btn.filters[i];
            $("#configdialog #config-flt").append('<p id="pf'+i+'">'+
                '<input type="checkbox" class="cfgchk" id="if'+i+'" value="'+i+'" data-f_id="'+i+'">'+
                '&nbsp;<label for="if'+i+'">'+f.name+'</label></p>'+
                '<p class="cfgval" id="cfgval'+i+'"></p>');
            
            // add filter elements
            $("#configdialog #cfgval"+i).data("f_type", f.type)

            if (f.type == 6) { // Boolean
                $("#configdialog #cfgval"+i).addClass("valuesovf");
                for (var j in f.values) {
                    var v = f.values[j];
                    $("#configdialog #cfgval"+i).append('<input name="par'+i+'" class="par'+i+'" id="val'+j+'" type="radio" value="'+v[0]+'"/><b>'+v[1]+'</b><br>');
                }
            } else
	    	
            if (f.type == 1) { // Predefined list
                var input_type = f.multiValued == true ? "checkbox" : "radio";
                $("#configdialog #cfgval"+i).addClass("valuesovf");
                $("#configdialog #cfgval"+i).append("<table id='tval"+i+"' style='width: 99%'><tbody></tbody></table>");
                for (var j in f.values) {
                    var v = f.values[j];
                    var r = $("<tr><td></td><td></td></tr>");
                    r.find("td:eq(0)").append('<input name="par'+i+'" class="par'+i+'" id="val'+v[0]+'" type="'+input_type+'" value="'+v[0]+'"/><b>'+v[1]+'</b>');
                    
                    if (v[2] != null) { // value has an associated subfilter

                        if (v[4] == 3) { // numeric
                            var el = $('<select class="rangeFrom">'+
                                            '<option value=">"> &#x2265; </option>'+
                                            '<option value="="> = </option>'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="text" class="rangeFrom" value=""/>'+
                                        '<span id="trattino"> - </span>'+
                                        '<select class="rangeTo">'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="text" class="rangeTo" value=""/>');
                            $(el[1]).data("type", 3);
                            $(el[1]).addClass("corr" + v[2]);
                            $(el[5]).data("type", 3);
                            $(el[5]).addClass("corr" + v[2]);
                            $(el[0]).change(QueryGen.toggleStatus);
                        } else

                        if (v[4] == 2) { // date
                            var el = $('<select class="rangeFrom">'+
                                            '<option value=">"> &#x2265; </option>'+
                                            '<option value="="> = </option>'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="text" class="rangeFrom" value=""/>'+
                                        '<span id="trattino"> - </span>'+
                                        '<select class="rangeTo">'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="text" class="rangeTo" value=""/>');
                            $(el[1]).data("type", 2);
                            $(el[1]).addClass("corr" + v[2]);
                            $(el[5]).data("type", 2);
                            $(el[5]).addClass("corr" + v[2]);
                            $([el[2],el[6]]).datepicker({
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

                            $(el[0]).change(QueryGen.toggleStatus);
                        } else

                        if (v[4] == 4) { // text
                            var el = $('<span class="corr-input"></span><input id="addvalue'+v[2]+'" type="text" value="" onkeypress="validate2(event)"/>');
                            $(el[0]).data("type", 4);
                            $(el[0]).addClass("corr" + v[2]);
                        }

                        var td = r.find("td:eq(1)");
                        td.append(v[3]+"&nbsp;");
                        td.append(el);
                        td.attr("id", "cfgval"+v[2]);
                        td.addClass("cfgval1");
                        td.data("f_type", v[4]);
                        td.attr("data-f_id", v[2]);
                        td.data("disabled", true);
                        td.data("par_flt_id", i);
                        td.data("par_flt_value", v[0]);

                        el.prop("disabled", true);
                        if (input_type == "checkbox") {
                            r.find("td:eq(0)").children("input").click(function() {
                                $(this).parent().siblings("td").find("input,select").prop("disabled",!$(this).is(":checked"));
                                $(this).parent().siblings("td").data("enabled", $(this).is(":checked"));
                            });
                        } else if (input_type == "radio") {
                            var prev_el;
                            r.find("td:eq(0)").children("input").click(function() {
                                if (prev_el) {
                                    prev_el.find("input,select").prop("disabled",true);
                                    prev_el.data("enabled",false);
                                }
                                prev_el = $(this).parent().siblings("td");
                                prev_el.find("input,select").prop("disabled",false);
                                prev_el.data("enabled",true);
                            });

                        }
                    }

                    $("#configdialog #tval"+i).append(r);
                }
                
                if (f.multiValued == true) {
                    $("#configdialog #pf"+i).append('<em class="counter" id="cnt'+i+'" data-count_val="0"></em>');
                    $("#configdialog .par"+i).change(function (index) {
                            return function() {
                                var cnt = $("#configdialog #cnt"+index).attr("data-count_val");
                                if ($(this).prop('checked') == true)
                                    ++cnt;
                                else
                                    --cnt;
                                $("#configdialog #cnt"+index).attr("data-count_val", cnt);
                            }
                        } (i)
                    );
                }
            } else

            if (f.type == 2) { // Date
                $("#configdialog #cfgval"+i).append(  '<select class="rangeFrom">'+
                                            '<option value=">"> &#x2265; </option>'+
                                            '<option value="="> = </option>'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="text" class="rangeFrom" value=""/>'+
                                        '<span id="trattino"> - </span>'+
                                        '<select class="rangeTo">'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="text" class="rangeTo" value=""/>');
                $("#configdialog #cfgval"+i).find("span.corr-input").data("type", 2).addClass("corr" + i);;

                $('#configdialog #cfgval'+i).children('.rangeFrom').change(QueryGen.toggleStatus);
                        
                $("#configdialog #cfgval"+i).children(':input').datepicker({
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

            } else

            if (f.type == 3) { // Numeric
                $("#configdialog #cfgval"+i).append(  '<select class="rangeFrom">'+
                                            '<option value=">"> &#x2265; </option>'+
                                            '<option value="="> = </option>'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="number" step="0.1" maxlength="200" class="rangeFrom" value="" onkeypress="validate(event)"/>'+
                                        '<span id="trattino"> - </span>'+
                                        '<select class="rangeTo">'+
                                            '<option value="<"> &#x2264; </option>'+
                                        '</select>'+
                                        '<span class="corr-input"></span>'+
                                        '<input type="number" step="0.1" maxlength="200" class="rangeTo" value="" onkeypress="validate(event)"/>');
                $("#configdialog #cfgval"+i).find("span.corr-input").data("type", 3).addClass("corr" + i);
                $('#configdialog #cfgval'+i).children('.rangeFrom').change(QueryGen.toggleStatus);
            } else

            if (f.type == 4) { // Genid
                var f_idButton = i;
                // decide whether to instantiate textarea for batch input or not
                var htmlCode = '<p>Genealogy ID type: <select id="selgenidtype' + f_idButton +'">'
                for (var t in f.genid) {
                    htmlCode += '<option>'+ f.genid[t] +'</option>'
                }
                htmlCode += '</select></p>'

                htmlCode += '<table id="genid'+ f_idButton + '">'+ 
                            '<thead style="font-size: 10px"> <th style="width: 40px" class="add"></th> </thead> <tbody>  <tr> <td style="width: 40px" class="add"> '+ 
                            '<span id="add_gid'+ f_idButton +'" class="add_btn" style="margin-right:5px;">add</span> </td> </tr> </tbody> </table> <br>'+
                            '<div> <table> <tr> <td> <span style="font-size:10px;margin-right:10px;">Load Genealogy IDs from file:</span> </td> <td> <form id="genidfrm' + f_idButton + '"><input type="file" id="genidfile' + f_idButton +'" /></form> </td> </tr>' +
                            '<tr> <td> <span style="font-size:10px;margin-right:10px;">Insert full Genealogy IDs:<br>(newline or blank separated)</span> </td> <td> ' +
                            '<textarea id="fullgenid'+ f_idButton + '" type="text" style="width:500px;height:80px; resize:none" maxlength="20000"></textarea></td> <td> <span id="add_gid2_' + f_idButton +'" class="add_btn" style="margin-right:5px;">add</span> </td> </tr> </table> </div> <br> <div id="genidlist'+ f_idButton + '" style="max-height: 200px;overflow: auto;"></div>'

                $("#configdialog #cfgval"+f_idButton).append(htmlCode);
                

                $("#fullgenid" + f_idButton).boxlist({
                        bMultiValuedInput: true,
                        oBtnEl: $("#add_gid2_" + f_idButton),
                        oContainerEl: $("#genidlist" + f_idButton),
                        fnEachParseInput: function(v) {
                            v = v.trim();
                            if (v.length == 0) {
                                return v;
                            } else if (v.length < 26) {
                                v = v + new Array(26 - v.length + 1).join("-");
                            } else if (v.length > 26) {
                                v = v.substr(0, 26);
                            }
                            return v.toUpperCase();
                        },
                        fnValidateInput: function(val) {
                            var ok;
                            console.log(val);
                            for (var t in genid) {
                                var fields = genid[t].fields;
                                ok = true;
                                for (var j = 0; j < fields.length && ok; ++j) {
                                    var f = fields[j];
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
                                            //e' per gestire le linee che hanno un contatore al posto del TUM e se non metto questo if
	                                    //mi danno errore in caso scriva il loro gen per intero
	                                    if(!(ok)&&(f.name=="Tissue type")){
	                            	        // numeric
	                            	        ok = /^[0-9]+$/.test(x);
	                                    }
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
                        },

                        aoAltInput: [
                            {
                                oBtnEl: $("#add_gid" + f_idButton),
                                fnParseInput: genIdFromForm
                            }
                        ]
                    });

                $("#genidfile" + f_idButton).change(function() {
                        var r = new FileReader();
                        r.onload = function(evt) {
                            $("#fullgenid" +f_idButton ).val(evt.target.result);
                            $("#add_gid2_" +f_idButton ).click();
                            $("#genidfrm" +f_idButton )[0].reset();
                        }
                        r.readAsText($("#genidfile" + f_idButton )[0].files[0]);
                    });

                $("#selgenidtype" + f_idButton ).change(function() {
                        
                        var t = $(this).val();
                        
                        try {
                            var fields = genid[t].fields;
                        }
                        catch(err) {
                            return;
                        }
                        $("table#genid"+ f_idButton + " th.field,table#genid" + f_idButton + " td.field").remove();
                        for (var j = 0; j < fields.length; ++j) {
                            $('<th class="field">' + fields[j].name + '</th>').insertBefore("table#genid" + f_idButton +" th.add");
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
                            $(x).insertBefore("table#genid" + f_idButton +" td.add");
                        }
                    });

                    $("#selgenidtype" + f_idButton ).prop("selectedIndex", 0).change();
            } else

            if (f.type == 5) { // Text with autocomplete
                var f_idButton = i;
                var htmlCode = '<input style="width:30%;float:left" id="addvalue'+f_idButton+'" type="text" value="" onkeypress="validateText(event, ' + f_idButton + ')"/>';// validate2
                if (f.multiValued == true) {
                    htmlCode += ' <span class="add_btn" id="add_btn'+i+'">add</span> ';
                }
                if (f.fileInput == true){
                    htmlCode += ' <form style="width:30%;float:left"  id="textfrm' + f_idButton + '"><input type="file" id="textfile' + f_idButton +'" /></form>'
                }

               
                $("#configdialog #cfgval"+f_idButton).append(htmlCode);

                var url = autocomplete_api_url + "?id=" + f.api_id;
                $('#configdialog #addvalue'+f_idButton).autocomplete({
                    source: (function(u) {
                                return function(request, response) {
                                    $.ajax({
                                        url: u,
                                        dataType: "jsonp",
                                        data: {
                                            term: request.term
                                        },
                                        success: function(data) {
                                            response(data)
                                        }
                                    });
                                }
                            }) (url)
                });

                

                // also decide whether to insert input-style or paragraph-style correlation button
                if (f.multiValued == true) {
                    $("#configdialog #cfgval"+i).data("multiValued", true);
                    //$("#configdialog #cfgval"+i).append('<span class="add_btn" id="add_btn'+i+'">add</span>');
                    $("#configdialog #addvalue"+i).boxlist({bMultiValuedInput: true, fnParseInput:function(val) {return [val];}});
                    // insert paragraph-style correlation button
                    var el = $("<span class='corr-par'></span>");
                    el.data("type", 5);
                    el.addClass("corr" + f_idButton);
                    el.data("checkbox", $("#configdialog #if"+f_idButton));
                    el.data("paragraph", $("#configdialog #cfgval"+f_idButton));
                    $("#configdialog #pf"+i).append(el);
                    if (f.fileInput == true){
                        $("#configdialog #textfile" + f_idButton ).change(function(i) {
                            return function() {
                                var r = new FileReader();
                                r.onload = function(evt) {
                                    var text= evt.target.result;
                                    var lines = text.split("\n");
                                    for (var k=0; k<lines.length; ++k){
                                        $("#addvalue" + i ).val(lines[k].trim());
                                        $("#add_btn" + i ).click();
                                    }
                                    $("#textfrm" + i )[0].reset();
                                };
                                console.log( f_idButton);

                                r.readAsText($("#configdialog #textfile" + i)[0].files[0]);
                            }
                        } (f_idButton) );

                    }


                } else {
                    $("#configdialog #cfgval"+f_idButton).data("multiValued", false);
                    // insert input-style correlation button
                    var el = $("<span class='corr-input'></span>");
                    el.data("type", 5).addClass("corr" + f_idButton);
                    $("#configdialog #cfgval"+f_idButton).children(":eq(0)").before(el);
                }

            } else
		
    	    if (f.type == 7) { // WG
                var myGroups = [];
                for (var j in f.values) {
                    var v = f.values[j];
                    if (workingGroupsList.indexOf(v[1]) >= 0) { //  && v[1]!='admin'
                        myGroups.push(v);
                    }
                }

                var input_type = f.multiValued == true ? "checkbox" : "radio";
                $("#configdialog #cfgval"+i).addClass("valuesovf");
                $("#configdialog #cfgval"+i).append("<table id='tval"+i+"' style='width: 99%'><tbody></tbody></table>");

                for (var j = 0; j < myGroups.length; ++j) {
                    var v = myGroups[j];
                    var r = $("<tr><td></td><td></td></tr>");
                    r.find("td:eq(0)").append('<input name="par'+i+'" class="par'+i+'" id="val'+v[0]+'" type="'+input_type+'" value="'+v[0]+'"  /><b>'+v[1]+'</b>');
                    $("#configdialog #tval"+i).append(r);
                }
                    
                if (f.multiValued == true) {
                    $("#configdialog #pf"+i).append('<em class="counter" id="cnt'+i+'" data-count_val="0"></em>');
                    $("#configdialog .par"+i).change(function (index) {
                            return function() {
                                var cnt = $("#configdialog #cnt"+index).attr("data-count_val");
                                if ($(this).prop('checked') == true)
                                    ++cnt;
                                else
                                    if (cnt != 1){
                                        --cnt;
                                    }
                                    else{
                                        alert('You should select at least one WG');
                                        $(this).prop('checked', true);
                                    }
                                $("#configdialog #cnt"+index).attr("data-count_val", cnt);
                            }
                        } (i)
                    );
                }
                $('#if'+i).prop('checked','true');
                $('#if'+i).prop('disabled','true');

            }
        }

        
        $("#configdialog .cfgval").hide();
        $("#configdialog .counter").hide();
        $("#configdialog .cfgchk").change(
            function () {
                var f_id = $(this).data("f_id");
                var f = btn.filters[f_id];
                $("#configdialog #cfgval" + f_id).not(".noshow").toggle($(this).prop('checked'));
                $("#configdialog #cnt" + f_id).toggle($(this).prop('checked'));
            }
        );

        // set current menu item in each correlation button
        $("#configdialog #config-flt").find(".corr-par,.corr-input").data("menu-item", 0);

        // assign click handlers to correlation buttons (to open up menu)
        $("#configdialog").find("#config-flt").find(".corr-par,.corr-input").on("click.context", QueryGen.contextMenuHandler);
        
        $("#configdialog .cfgchk:checked").change();
        // restore previous values (if any)

        // filters
        var params = QueryGen.getGraphNode(block_id).parameters;
        console.log('params reload',  params);
        if (params.length > 0) {
            for (var j = 0; j < params.length; ++j) { 
                var f_id = params[j]['f_id'];
                $('#configdialog #if' + f_id).trigger('click');
                var f_type = $("#configdialog #cfgval"+f_id).data("f_type");
                
                if (f_type == 1 || f_type == 6 || f_type == 7) { // predefined list or boolean
                    for (var i = 0; i < params[j]['values'].length; ++i) {
                        //console.log(".par"+f_id+"#val"+params[j]['values'][i]);
                        $("#configdialog .par"+f_id+"#val"+params[j]['values'][i]).trigger('click');
                    }

                } else


                if (f_type == 5) { // text with or without autocomplete
                    var isCorrelated = params[j]['values'][0][0] == 'c';

                    if (!isCorrelated) {
                        for (var i = 0; i < params[j]['values'].length; ++i) {
                            $("#configdialog #addvalue"+f_id).val(params[j]['values'][i].slice(1));
                            $("#configdialog #add_btn"+f_id).trigger('click');
                        }
                    } else {
                        // menu-item (i.e., index of output + 1)
                        var mi = params[j]['values'][0].substr(1);
                        var corr_el = $(".corr"+f_id);
                        if ($("#menu-item-"+mi).length == 0) {
                            mi = "0";
                        }
                        var label = $("#menu-item-"+mi).data("label");
                        QueryGen.toggleCorrelation(corr_el, mi, label);
                    }
                 
                } else

                if (f_type == 4){
                    console.log('params genid ', params);
                    for (var i = 0; i < params[j]['values'].length; ++i) {
                            $("#configdialog #fullgenid"+f_id).val(params[j]['values'][i]);
                            $("span#add_gid2_" + f_id).trigger('click');
                    }
                    
                } else

                if (f_type == 3) { // numeric
                    var from = params[j]['values'][0];
                    var isCorrelated = from[0] == 'c';
                    from = from.slice(1); // skip past 'c' or 'u'
                    $("#configdialog #cfgval"+f_id).children("select.rangeFrom").val(from[0]);
                    from = from.slice(1); // skip past '>', '=' or '<'
                    $("#configdialog #cfgval"+f_id).children("select.rangeFrom").trigger('change');

                    if (!isCorrelated) {
                        $("#configdialog #cfgval"+f_id).children("input.rangeFrom").val(from);
                    } else {
                        var val = from.split("+");
                        var mi = val[0];
                        var corr_el = $(".corr"+f_id+":eq(0)");
                        if ($("#menu-item-"+mi).length == 0) {
                            mi = "0";
                        }
                        var label = $("#menu-item-"+mi).data("label");
                        QueryGen.toggleCorrelation(corr_el, mi, label);
                        $(".corr"+f_id+":eq(0)").next().children("input[type=number]").val(val[1]);
                    }

                    if (params[j]['values'].length > 1) {
                        var to = params[j]['values'][1];
                        var isCorrelated = to[0] == 'c';
                        to = to.slice(1);
                        $("#configdialog #cfgval"+f_id).children("select.rangeTo").val(to[0]);
                        to = to.slice(1);
                        
                        if (!isCorrelated) {
                            $("#configdialog #cfgval"+f_id).children("input.rangeTo").val(to);
                        } else {
                            var val = to.split("+");
                            var mi = val[0];
                            var corr_el = $(".corr"+f_id+":eq(1)");
                            if ($("#menu-item-"+mi).length == 0) {
                                mi = "0";
                            }
                            var label = $("#menu-item-"+mi).data("label");
                            QueryGen.toggleCorrelation(corr_el, mi, label);
                            $(".corr"+f_id+":eq(1)").next().children("input[type=number]").val(val[1]);
                        }
                    }
                    
                } else

                if (f_type == 2) { // date
                    var from = params[j]['values'][0];
                    var isCorrelated = from[0] == 'c';
                    from = from.slice(1);
                    $("#configdialog #cfgval"+f_id).children("select.rangeFrom").val(from[0]);
                    from = from.slice(1);
                    $("#configdialog #cfgval"+f_id).children("select.rangeFrom").trigger('change');
                    
                    if (!isCorrelated) {
                        $("#configdialog #cfgval"+f_id).children("input.rangeFrom").val(from);
                    } else {
                        var val = from.split("+");
                        var mi = val[0];
                        var corr_el = $(".corr"+f_id+":eq(0)");
                        if ($("#menu-item-"+mi).length == 0) {
                            mi = "0";
                        }
                        var label = $("#menu-item-"+mi).data("label");
                        QueryGen.toggleCorrelation(corr_el, mi, label);
                        $(".corr"+f_id+":eq(0)").next().children("input[type=number]").val(val[1]);
                    }

                    if (params[j]['values'].length > 1) {
                        var to = params[j]['values'][1];
                        var isCorrelated = to[0] == 'c';
                        to = to.slice(1);
                        $("#configdialog #cfgval"+f_id).children("select.rangeTo").val(to[0]);
                        to = to.slice(1);
                        
                        if (!isCorrelated) {
                            $("#configdialog #cfgval"+f_id).children("input.rangeTo").val(to);
                        
                            $("#configdialog #cfgval"+f_id).children("input.rangeFrom").datepicker("option", "maxDate", to);
                            $("#configdialog #cfgval"+f_id).children("input.rangeTo").datepicker("option", "minDate", from);
                        } else {
                            var val = to.split("+");
                            var mi = val[0];
                            var corr_el = $(".corr"+f_id+":eq(1)");
                            if ($("#menu-item-"+mi).length == 0) {
                                mi = "0";
                            }
                            var label = $("#menu-item-"+mi).data("label");
                            QueryGen.toggleCorrelation(corr_el, mi, label);
                            $(".corr"+f_id+":eq(1)").next().children("input[type=number]").val(val[1]);
                        }
                    }
                }
            }
        }
        // outputs
        
        // make list of outputs from current block that are referenced through correlation by next block
        var outTerminal = block.data("out-terminal")[0];
        var outConnTerminal = outTerminal.getConnectedTerminals()[0];
        if (outConnTerminal !== undefined && $(outConnTerminal.parentEl).attr("id") != "end") {
            var outConnBlock = outConnTerminal.parentEl;
            var outConnBlockId = $(outConnBlock).attr("data-block_id");
            var corr_outs = QueryGen.findCorrelatedOutputs(outConnBlockId);
        } else {
            var corr_outs = [];
        }

        var outputs = QueryGen.getGraphNode(block_id).outputs;
        for (var j = 0; j < outputs.length; ++j) {
            if (outputs[j] != undefined) {
                $("#configdialog #out"+outputs[j]).prop("checked", true);
                // check if output is in use in next (correlation) and, if so, disable it so it can't be unchecked
                if (corr_outs.indexOf(j) != -1) {
                    $("#configdialog #out"+outputs[j]).click(function() {alert("Output is in use by next block", "Cannot uncheck"); $(this).prop("checked", true);});;
                }
            }
        }

        // inputs
        var query_path_id = QueryGen.getGraphNode(block_id).query_path_id;
        var paths = $("#configdialog #config-in-list input");
        // if previous entity is the same as the current one, then there is no path in the input tab -- this case is handled separately even in the query engine
        if (paths.length > 0) {
            paths.filter("[value=" + query_path_id + "]").prop("checked", true);
        }

        // configure behavior when dialog buttons are clicked
        $("#configdialog").dialog("option", {
            buttons:
            [
                {
                    text: "Remove all filters",
                    click: function() {
                        $("#configdialog .cfgchk").prop('checked', false).change();
                    }
                },
                {
                    text: "Ok",
                    click: function() {
                        // save parameters
                        var params = [];
                        var checkboxes = $("#configdialog .cfgchk:checked");
                        var subfilters = $("#configdialog td.cfgval1").filter(function() {return $(this).data("enabled")});
                        checkboxes.add(subfilters).each(function() {

                            //alert('block='+block_id+' par_id='+$(this).attr('data-par_id'));
                            var f_id = $(this).attr('data-f_id');
                            var cfgval = $("#configdialog #cfgval"+f_id);
                            var f_type = cfgval.data("f_type");

                            var v_list = [];

                            if (cfgval.data("par_flt_id")) {
                                var par_flt_id = cfgval.data("par_flt_id");
                                var par_flt_value = cfgval.data("par_flt_value");
                            } else {
                                var par_flt_id = null;
                                var par_flt_value = null;
                            }
                            
                            if (f_type == 1 || f_type == 6 || f_type == 7) { // predefined list or boolean
                                
                                cfgval.find("input.par"+f_id+":checked").each(function() {
                                    v_list.push($(this).val());
                                });

                                
                            } else if (f_type == 2 || f_type == 3) { // date or numeric
                                
                                var val;
                                // "mi" stands for "menu item"
                                var mi0 = $(".corr"+f_id+":eq(0)").data("menu-item");
                                var mi1 = $(".corr"+f_id+":eq(1)").data("menu-item");
                                var notEmpty;

                                if (mi0 != 0) {
                                    val = 'c' + cfgval.children("select.rangeFrom").val() + mi0 + '+' + cfgval.find("input[type=number]:eq(0)").val();
                                    notEmpty = true;
                                } else {
                                    val = 'u' + cfgval.children("select.rangeFrom").val() + cfgval.children("input.rangeFrom").val().trim();
                                    notEmpty = val.length > 2;
                                }
                                if (notEmpty) v_list.push(val);

                                if (!cfgval.children('select.rangeTo').prop('disabled')) {
                                    if (mi1 != 0) {
                                        val = 'c' + cfgval.children("select.rangeTo").val() + mi1 + '+' + cfgval.find("input[type=number]:eq(1)").val();
                                        notEmpty = true;
                                    } else {
                                        val = 'u' + cfgval.children("select.rangeTo").val() + cfgval.children("input.rangeTo").val().trim();
                                        notEmpty = val.length > 2;
                                    }
                                    if (notEmpty) v_list.push(val);
                                }
                                
                            } else if (f_type == 5) { // text with or without autocomplete
                                
                                var mi = $(".corr"+f_id).data("menu-item");

                                var v_list = [];
                                if (mi == 0) {
                                    if (cfgval.data("multiValued") == true) {
                                        v_list = $("#configdialog #addvalue"+f_id).boxlist("getValues").map(function(x) {return 'u'+x});
                                    } else {
                                        var x = 'u' + $("#configdialog #addvalue"+f_id).val();
                                        if (x.length > 1) {
                                            v_list.push(x);
                                        }
                                    }
                                } else {
                                    v_list.push('c' + mi);
                                }
                            }
                            else if (f_type == 4){ // genid
                                v_list = $("#configdialog #fullgenid" +f_id ).boxlist("getValues");
                            }
                            if (v_list.length > 0) {
                                var dic = {'f_id':f_id, 'values': v_list};
                                if (par_flt_id != null) {
                                    $.extend(dic, {'par_flt_id': par_flt_id, 'par_flt_value': par_flt_value});
                                }
                                params.push(dic);
                                console.log(params);
                            }
                                
                        });
                        QueryGen.setGraphNodeAttr(block_id, 'parameters', params);
                        if (QueryGen.getGraphNode(block_id).parameters.length > 0) {
                            $("p#box"+block_id).children("span#led").removeClass("filteroff").addClass("filteron");
                        } else {
                            $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff");
                        }

                        // save input
                        var paths = $("#configdialog #config-in-list input");
                        // if previous entity is the same as the current one, then there is no path in the input tab -- this case is handled separately even in the query engine
                        if (paths.length > 0) {
                            var query_path_id = paths.filter(":checked").val();
                            QueryGen.setGraphNodeAttr(block_id, 'query_path_id', query_path_id);
                        }

                        //save outputs
                        var outs = [];
                        $("#configdialog #config-out-list input:checked").each(function() {outs.push($(this).val());});
                        var old_outs = QueryGen.getGraphNode(block_id).outputs;
                        // delete outputs that have been de-selected
                        for (var i = 0; i < old_outs.length; ++i) {
                            if (outs.indexOf(old_outs[i]) == -1) {
                                old_outs[i] = undefined;
                            }
                        }
                        // append new outputs
                        for (var i = 0; i < outs.length; ++i) {
                            if (old_outs.indexOf(outs[i]) == -1) {
                                old_outs.push(outs[i]);
                            }
                        }

                        $(this).dialog("close");                                                                                         
                    }
                }
            ],
            beforeClose: function()
            {
                $("#config-flt p").remove();
                $("#config-out-list").children().remove();
                // run dialog close handler
                QueryGen.handle_dialog_close.runHandler(block_id);                
            },
        });
    },
    
    findCorrelatedFilters: function(block_id) {
        // return index of curr. block's filters that have correlated values from prev. block
        var n = QueryGen.getGraphNode(block_id);
        var f = n.parameters;
        var rem = [];
        if (n.button_cat == "qent") {
            for (var i = 0; i < f.length; ++i) {
                for (var j = 0; j < (f[i].values.length < 2 ? f[i].values.length : 2); ++j) {
                    if (f[i].values[j][0] == 'c') {
                        rem.push(i);
                        break;
                    }
                }
            }
        } else

        if (n.button_cat == "op" && n.button_id == 4) { // group by operator
            for (var i = 0; i < f.length; ++i) {
                if (f[i].attr[0] == 'c') {
                    rem.push(i);
                }
            }
        } else


        if (n.button_cat == "op" && n.button_id == 7) { // extend operator
            for (var i = 0; i < f.length; ++i) {
                if (f[i].query_path_id == 'self') {
                    rem.push(i);
                }
            }
        }
        return rem;
    },

    findCorrelatedOutputs: function(block_id) {
        // return index of prev. block's outputs that are referenced by curr. block's filters through correlation
        var n = QueryGen.getGraphNode(block_id);
        var f = n.parameters;
        var o = [];
        if (n.button_cat == "qent") {
            for (var i = 0; i < f.length; ++i) {
                for (var j = 0; j < (f[i].values.length < 2 ? f[i].values.length : 2); ++j) {
                    if (f[i].values[j][0] == 'c') {
                        o.push(parseInt(f[i].values[j].split("_")[1].split("+")[0]));
                    }
                }
            }
        } else

        if (n.button_cat == "op" && n.button_id == 7) { // extend operator
            for (var i = 0; i < f.length; ++i) {
                if (f[i] != undefined) {
                    o.push(f[i].out_id);
                }
            }
        }

        return o;
    },


    removeCorrelatedFilters: function(block_id, rem) {
        var f = QueryGen.getGraphNode(block_id).parameters;
        var i = rem.length-1;
        while (i >= 0) {
            f.splice(rem[i], 1);
            --i;
        }
        if (f.length == 0) {
            $("p#box"+block_id).children("span#led").removeClass("filteron").addClass("filteroff");
        }
    },

    // GUI function
    
    toggleStatus: function () {
        if ($(this).val()=="<" ||  $(this).val()=="=") {
            $(this).siblings('.rangeTo').attr('disabled', true);
        } else {
            $(this).siblings('.rangeTo').removeAttr('disabled');
        } 
    },

    // BL function
    initBaseTerminals : function(start_id, end_id, end_terminal) {
        QueryGen.startName = start_id;
        QueryGen.endName = end_id;
         
        QueryGen.jsonStrGraph[start_id] =
            {
                "id" : start_id,
                "w_out": [],

            };
        QueryGen.jsonStrGraph[end_id] =
        {
            "id" : end_id,
            "w_in": [],
            "translators": []
        };
        // handle wire add events on end terminal
        end_terminal.eventAddWire.subscribe(function() {
            var connTerminal = end_terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            if (connBlock !== undefined) {
                var connBlockId = $(connBlock).attr("data-block_id");
                if (connBlockId == "start") {
                    alert(  "The start and the end terminals cannot be directly connected.",
                                "Cannot continue",
                                "Ok",
                                function() {
                                    connTerminal.removeWire(end_terminal.wires[0]);
                                    end_terminal.removeWire(end_terminal.wires[0]);
                                }
                        );
                        return;
                }
                var connBType = QueryGen.getGraphNode(connBlockId).button_id;
                var connBCat = QueryGen.getGraphNode(connBlockId).button_cat;
                if (connBCat == "op") {
                    if (ops[connBType].canBeLast == false) {

                        alert(  "The "+ops[connBType].name + " block may not be connected to the end block.",
                                "Oops!",
                                "Ok",
                                function() {
                                    connTerminal.removeWire(end_terminal.wires[0]);
                                    end_terminal.removeWire(end_terminal.wires[0]);
                                }
                        );
                        return;
                    } else

                    if (ops[connBType].outFromConf == true && QueryGen.getGraphNode(connBlockId).parameters.length == 0) {
                        alert(  "Please configure the "+ops[connBType].name + " block first.",
                                "Oops!",
                                "Ok",
                                function() {
                                    connTerminal.removeWire(end_terminal.wires[0]);
                                    end_terminal.removeWire(end_terminal.wires[0]);
                                }
                        );
                        return;
                    }
                }
                
                // update outputs on connected block
                var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
                conn_out.push(end_id);
                // update inputs on current block
                var curr_in = QueryGen.getGraphNode(end_id).w_in;
                curr_in[0] = connBlockId+'';
            }
        });
        // handle wire remove events on end terminal
        end_terminal.eventRemoveWire.subscribe(function() {
            var curr_in = QueryGen.getGraphNode(end_id).w_in;
            var connBlockId = curr_in[0];
            
            // remove this block from connected block's output wires
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            // n.b. we use splice because conn_out may have multiple outputs (e.g. start terminal)
            conn_out.splice(conn_out.indexOf(end_id), 1);
            
            // set current block's input wires to null
            curr_in[0] = undefined;

            // clear translators in end block
            QueryGen.setGraphNodeAttr("end", "translators", []);
        });

        $("#configend").click(QueryGen.configEndDialog);
        
    },

    configEndDialog : function() {
        var term = end_terminal.getConnectedTerminals()[0];
        if (term == undefined) {
            alert ("Please connect some block to the end terminal first", "Terminal disconnected");
            return;
        }
        var blockId = $(term.parentEl).data("block_id");
        var outType = QueryGen.getGraphNode(blockId).output_type_id;
        
        var trans = $("#translatorslist");
        // clear previous translators
        trans.children().remove();

        // populate translators list
        for (var x in templates) {
            var t = templates[x];
            if (t.isTranslator == true && outType == t.translatorInputType) {
                if ($(t.WG).filter(workingGroupsList).length != 0 || $(templates[x].WG).filter(["admin"]).length != 0){ 
                    trans.append('<input id="trans'+x+'" type="checkbox" value="'+x+'"><label for="trans'+x+'"><b>'+t.name+'</b>: '+t.description+'</label><br>');
                }
            }
        }
        if (trans.children().length == 0) {
            trans.append("<i>No translators available for the current output entity</i>");
        }

        // restore previous values (if any)
        var currentTrans = QueryGen.getGraphNode("end").translators;
        for (var i = 0; i < currentTrans.length; ++i) {
            $("#trans" + currentTrans[i]).prop("checked", true);
        }
        
        // configure behavior when buttons are clicked
        $("#translatordialog").dialog({
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
                        var trans = [];
                        $("#translatorslist input:checked").each(function() {trans.push($(this).val());});
                        QueryGen.setGraphNodeAttr("end", "translators", trans);
                        $(this).dialog("close");
                    }
                }
            ]
        });
        $("#translatordialog").dialog("open");
        
    },
    
    // BL function
    addGraphNode : function(block_id, button_id, button_cat, template_id) {

        QueryGen.jsonStrGraph[block_id] =
            {
                "id" : block_id,
                "button_id" : button_id,
                "button_cat" : button_cat,
                "parameters": [],
                "w_out": [],
                "w_in": [],
                "outputs": [],
                "query_path_id": null
            };
        

        // define output ent
        if (button_cat == "qent") {// for qents, output ent is the qent
            QueryGen.jsonStrGraph[block_id].output_type_id = button_id;
        } else if (button_cat == "op") { // for ops
            if (button_id == 6) { // templates
                var n_inputs = templates[template_id].inputs.length;
                QueryGen.jsonStrGraph[block_id].w_in = new Array(n_inputs);
                QueryGen.jsonStrGraph[block_id].query_path_id = new Array(n_inputs);
                QueryGen.jsonStrGraph[block_id].output_type_id = templates[template_id].output;
                QueryGen.jsonStrGraph[block_id].template_id = template_id;
            } else {
                if (ops[button_id].outFromIn == true) { // if it depends on input, initialize inputs
                    var n_inputs = ops[button_id].numInputs;
                    var a = new Array(n_inputs);
                    for (var i = 0; i < n_inputs; ++i) {
                        a[i] = false;
                    }
                    QueryGen.jsonStrGraph[block_id].conn_inputs = a;
                } else if (ops[button_id].outFromConf == true || ops[button_id].canBeLast == false) { // if it depends on config, do nothing
                    ;
                } else { // else the op is an entity in its own right
                    QueryGen.jsonStrGraph[block_id].output_type_id = button_id;
                }
            }
        }
        //console.log(QueryGen.jsonStrGraph[block_id]);
    },
    
    // BL function
    getGraphNode : function(block_id) {
        return QueryGen.jsonStrGraph[block_id];

    },
    
    //BL function
    deleteGraphNode: function(block_id) {
        delete QueryGen.jsonStrGraph[block_id];
    },
    
    // BL function
    setGraphNodeAttr : function(block_id, attr_name, val) {
        QueryGen.jsonStrGraph[block_id][attr_name] = val;   
    },

    addGraphNodeAttr : function(block_id, attr_name, val) {
        QueryGen.jsonStrGraph[block_id][attr_name].push.apply(QueryGen.jsonStrGraph[block_id][attr_name], val);
    },
    
    handle_dialog_close: {
        handlers : {},
        map: function(block_id, h) {
            this.handlers[block_id] = h;
        },
        unmap: function(block_id) {
            delete handlers[block_id];
        },
        runHandler: function(from_block_id) {
            var w = QueryGen.getGraphNode(from_block_id).w_out;
            if (w != undefined && w.length > 0) {
                var to_block_id = w[0].split(".")[0];
                if (this.handlers[to_block_id] != undefined) {
                    this.handlers[to_block_id](from_block_id, to_block_id);
                }
            }
        }
    },

    update_extend_ent_outputs : function(from, to) {
        var out = [];
        var n = QueryGen.getGraphNode(from);
        var ent_outputs = n.outputs;
        
        if (n.button_cat == "qent" || n.button_cat == "op" && (n.button_id == 6 || n.button_id == 4)) {
            for (var i = 0; i < ent_outputs.length; ++i) {
                if (ent_outputs[i] != undefined) {
                    var name = n.button_cat == "op" && n.button_id == 4 ? ent_outputs[i].name : "s" + qent[n.output_type_id].name + "." + qent[n.output_type_id].outputs[ent_outputs[i]].name; // "s" stands for "self" (the entity that's being extended itself)
                    out.push([i, name]);
                }
            }
        } else {
            return;
        }
        
        var old_outs = QueryGen.getGraphNode(to).outputs;
        var old_params = QueryGen.getGraphNode(to).parameters;

        // delete stale entity outputs
        for (var i = 0; i < old_params.length; ++i) {
            var p = old_params[i];
            if (p != undefined && p.query_path_id == "self") {
                // look for p in out
                var found = false;
                for (var j = 0; found == false && j < out.length; ++j) {
                    if (out[j][0] == p.out_id) {
                        found = true;
                    }
                }
                if (found == false) {
                    old_outs[i] = undefined;
                    old_params[i] = undefined;
                }
            }
        }

        // delete trailing undefined entries
        for (var l = old_outs.length-1; l >= 0; --l) {
            if (old_outs[l] == undefined) {
                --old_outs.length;
                --old_params.length;
            } else {
                break;
            }
        }

        // add new outputs
        for (var i = 0; i < out.length; ++i) {
            var o = out[i];
            // look for o in old_outs
            var found = false;
            for (var j = 0; found == false && j < old_params.length; ++j) {
                if (old_params[j] != undefined && old_params[j].query_path_id == "self" && old_params[j].out_id == o[0]) {
                    found = true;
                    // update name                        
                    old_outs[j] = o[1];
                }
            }
            if (found == false) {
                old_outs.push(o[1]);
                old_params.push({query_path_id: "self", out_id: o[0]});
            }
        }
    },

    new_Handle_GB_RemoveEvent : function(currBlockId) {
        return function() {
            
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            var connBlockId = curr_in[0];
            
            
            QueryGen.setGraphNodeAttr(currBlockId, "parameters", []);
            QueryGen.setGraphNodeAttr(currBlockId, "w_in", []);
            QueryGen.setGraphNodeAttr(currBlockId, "outputs", []);
            
            // remove this block from connected block's output wires
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.splice(conn_out.indexOf(currBlockId+".0"), 1);
            
            QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", undefined);
            
            var currBlock = $("p#box"+currBlockId);
            currBlock.children("span#led").removeClass("filteron").addClass("filteroff2");
            currBlock.data("outTerminal")[0].removeAllWires();
            
        }
    },

                   
    new_Handle_GB_AddEvent : function(terminal) {
        return function() {
            var currBlock = $(terminal.parentEl);
            var currBlockId = currBlock.attr("data-block_id");
            var connTerminal = terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            if (connBlock === undefined) return;
            
            var connBlockId = $(connBlock).attr("data-block_id");

            if (connBlockId == QueryGen.startName) {
                var ok = false;
                var msg = "The group by operator may not be connected to the start block.";
            } else {
                connBType = QueryGen.getGraphNode(connBlockId).button_id;
                connBCat = QueryGen.getGraphNode(connBlockId).button_cat;
                connBOutType = QueryGen.getGraphNode(connBlockId).output_type_id;

                if (connBCat == "qent") { // entity
                    var ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                    var msg = GUI.getButtonName(connBOutType) + " does not allow grouping operations.";
                } else

                if (connBCat == "op") {

                    if (connBType == 7) { // extend
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the extend block first.";
                        if (ok) {
                            ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                            msg = "The extend operator's output entity " + GUI.getButtonName(connBOutType) + " does not allow grouping operations.";
                        }

                    } else

                    if (connBType == 6) { // template
                        var ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                        var msg = GUI.getButtonName(connBOutType) + " does not allow grouping operations.";
                    } else

                    if (connBType == 5) { // genid
                        var ok = false;
                        var msg = "The Genealogy ID operator may not be connected to the group by operator."
                    } else

                    if (connBType == 4) { // group by
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the group by block first.";
                        if (ok) {
                            ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                            msg = "Group by's output entity " + GUI.getButtonName(connBOutType) + " does not allow grouping operations.";
                        }

                    } else

                    if (connBType <= 3 && connBType >= 1) { // logical operator
                        var ok = connBOutType != undefined;
                        var msg = "Please connect some entity to the " + ops[connBType].name + " operator first.";
                        if (ok) {
                            ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                            msg = GUI.getButtonName(connBOutType) + " does not allow grouping operations.";
                        }
                    }
                }
            }

            if (ok == false) {
                alert(  msg,
                        "Cannot continue",
                        "Ok",
                        function() {
                            connTerminal.removeWire(terminal.wires[0]);
                            terminal.removeWire(terminal.wires[0]);
                        }
                    );
                return;
            }

            // update of current node's output type will be done later when grouping attribute is selected
            // update outputs on connected block
            conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.push(currBlockId + ".0");
            // update inputs on current block
            curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            curr_in.push(connBlockId);

        }
    },
    
    new_Handle_Join_AddEvent : function(terminal) {
        return function() {
            var currBlock = $(terminal.parentEl);
            var currBlockId = currBlock.attr("data-block_id");
            var connTerminal = terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            if (connBlock === undefined) return;
            
            var connBlockId = $(connBlock).attr("data-block_id");

            if (connBlockId == QueryGen.startName) {
                var ok = false;
                var msg = "The extend operator may not be connected to the start block.";
            } else {
                var connBType = QueryGen.getGraphNode(connBlockId).button_id;
                var connBCat = QueryGen.getGraphNode(connBlockId).button_cat;
                var connBOutType = QueryGen.getGraphNode(connBlockId).output_type_id;

                if (connBCat == "qent") { // entity
                    var ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                    var msg = GUI.getButtonName(connBOutType) + " cannot be extended with attributes from other entities.";
                } else

                if (connBCat == "op") {

                    if (connBType == 7) { // extend
                        var ok = false;
                        var msg = "Extend operators cannot be chained."
                    } else

                    if (connBType == 6) { // template
                        var ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                        var msg = GUI.getButtonName(connBOutType) + " cannot be extended with attributes from other entities.";
                    } else

                    if (connBType == 5) { // genid
                        var ok = false;
                        var msg = "The Genealogy ID operator may not be connected to the Extend operator."
                    } else

                    if (connBType == 4) { // group by
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the group by block first.";
                        if (ok) {
                            ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                            msg = "Group by's output entity " + GUI.getButtonName(connBOutType) + " cannot be extended with attributes from other entities.";
                        }

                    } else

                    if (connBType <= 3 && connBType >= 1) { // logical operator
                        var ok = connBOutType != undefined;
                        var msg = "Please connect some entity to the " + ops[connBType].name + " operator first.";
                        if (ok) {
                            ok = GUI.getManyToOneRelationships(connBOutType).length > 0;
                            msg = GUI.getButtonName(connBOutType) + " cannot be extended with attributes from other entities.";
                        }
                    }
                }
            }

            if (ok == false) {
                alert(  msg,
                        "Cannot continue",
                        "Ok",
                        function() {
                            connTerminal.removeWire(terminal.wires[0]);
                            terminal.removeWire(terminal.wires[0]);
                        }
                    );
                return;
            }

            // update of current node's output type will be done when configuration is saved
            // update outputs
            QueryGen.update_extend_ent_outputs(connBlockId, currBlockId);
            // update outputs on connected block
            conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.push(currBlockId + ".0");
            // update inputs on current block
            curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            curr_in.push(connBlockId);
        }
    },

    new_Handle_Join_RemoveEvent : function(currBlockId) {
        return function() {
            
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            var connBlockId = curr_in[0];
                    
            QueryGen.setGraphNodeAttr(currBlockId, "parameters", []);
            QueryGen.setGraphNodeAttr(currBlockId, "outputs", []);
            QueryGen.setGraphNodeAttr(currBlockId, "w_in", []);
            
            // remove this block from connected block's output wires
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.splice(conn_out.indexOf(currBlockId+".0"), 1);
           
            QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", undefined);
            
            var currBlock = $("p#box"+currBlockId);
            currBlock.children("span#led").removeClass("filteron").addClass("filteroff2");
            currBlock.data("outTerminal")[0].removeAllWires();
            
        }
    },

    new_Handle_EntTempl_RemoveEvent : function(currBlockId, tid) {
        return function() {
            
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            var connBlockId = curr_in[tid];
            
            // remove this block from connected block's output wires
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            // n.b. we use splice because conn_out may have multiple outputs (e.g. start terminal)
            conn_out.splice(conn_out.indexOf(currBlockId+"."+tid), 1);
            
            // set current block's input wires to null
            curr_in[tid] = undefined;

        }
    },

    new_Handle_Op_RemoveEvent : function(currBlockId, tid) {
        return function() {
            var c = QueryGen.getGraphNode(currBlockId).conn_inputs;
            c[tid] = false;
            
            // delete currently connected block from w_in
            var curr_w_in = QueryGen.getGraphNode(currBlockId).w_in;
            var connBlockId = curr_w_in[tid];
            curr_w_in[tid] = undefined;
            
            // delete curr block from connected block's wires out
            var conn_w_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_w_out.splice(conn_w_out.indexOf(currBlockId+"."+tid), 1);
            
            if (!c[0] && !c[1]) {
                var currBlock = $("#box" + currBlockId);
                currBlock.children("p.param").remove();
                QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", undefined);
                var outTerminal = currBlock.data("outTerminal")[0];
                outTerminal.removeAllWires();
            }
        }
    },
           
    new_Handle_Genid_RemoveEvent: function(currBlockId) {
        return function() {
            // delete currently connected block from w_in
            var curr_w_in = QueryGen.getGraphNode(currBlockId).w_in;
            var connBlockId = curr_w_in[tid];
            curr_w_in[0] = undefined;
            
            // delete curr block from connected block's wires out
            var conn_w_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_w_out.splice(conn_w_out.indexOf(currBlockId+".0"), 1);
            
            QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", undefined);
        }
    },

    new_Handle_Ent_AddEvent: function(terminal) {
        return function() {
            //console.log("Handle_Ent_AddEvent");
            var currBlock = $(terminal.parentEl);
            var currBlockId = currBlock.attr("data-block_id");
            var currBType = QueryGen.getGraphNode(currBlockId).button_id;

            var connTerminal = terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            if (connBlock === undefined) return;
            var connBlockId = $(connBlock).attr("data-block_id");
            
            if (connBlockId != QueryGen.startName) {
                var connBNode = QueryGen.getGraphNode(connBlockId);
                var connBType = connBNode.button_id;
                var connBOutType = connBNode.output_type_id;
                var connBCat = connBNode.button_cat;

                if (connBCat == "qent") { // entity
                    var ok = GUI.isCompatible(currBType, connBOutType);
                    var msg = GUI.getButtonName(currBType) + " and " + GUI.getButtonName(connBOutType) + " may not be connected.";
                } else

                if (connBCat == "op") {

                    if (connBType == 7) { // extend
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the extend block first.";
                        if (ok) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            msg = "The extend operator's output entity " + GUI.getButtonName(connBOutType) + " may not be connected to " + GUI.getButtonName(currBType);
                        }
                    } else

                    if (connBType == 6) { // template
                        var ok = GUI.isCompatible(currBType, connBOutType);
                        var msg = GUI.getButtonName(currBType) + " and " + GUI.getButtonName(connBOutType) + " may not be connected";
                    } else

                    if (connBType == 5) { // genid
                        var ok = qent[currBType].genid_prefilter == true;
                        var msg = GUI.getButtonName(currBType) + " does not support genealogy ID pre-filtering.";
                        if (ok && connBOutType != undefined) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            msg = "Genealogy ID's predecessor " + GUI.getButtonName(connBOutType) + " may not be connected to " + GUI.getButtonName(currBType);
                        }
                    } else

                    if (connBType == 4) { // group by
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the group by block first.";
                        if (ok) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            msg = "Group by's output entity " + GUI.getButtonName(connBOutType) + " may not be connected to " + GUI.getButtonName(currBType);
                        }

                    } else

                    if (connBType <= 3 && connBType >= 1) { // logical operator
                        var ok = connBOutType != undefined;
                        var msg = "Please connect some entity to the " + ops[connBType].name + " operator first.";
                        if (ok) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            var msg = GUI.getButtonName(currBType) + " and " + GUI.getButtonName(connBOutType) + " may not be connected";
                        }
                    }
                }

                if (ok == false) {
                    alert(  msg,
                            "Cannot continue",
                            "Ok",
                            function() {
                                connTerminal.removeWire(terminal.wires[0]);
                                terminal.removeWire(terminal.wires[0]);
                            }
                        );
                    return;
                }
            }
            // update output wires on connected block
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.push(currBlockId + ".0");

            // update input wires on current block
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            curr_in[0] = connBlockId;

            // update input paths on current block
            var out_type = connBNode.output_type_id;
            if (out_type != undefined && out_type != currBType) {
                var all_paths = qent[out_type].fw_query_paths;
                for (var i in all_paths) {
                    var p = all_paths[i];
                    if (p.toEntity == currBType && p.isDefault == true) {
                        QueryGen.setGraphNodeAttr(currBlockId, "query_path_id", i);
                    }
                }
            } else {
                QueryGen.setGraphNodeAttr(currBlockId, "query_path_id", null);
            }
        }
    },
    
    new_Handle_Templ_AddEvent: function(terminal, tid) {
        return function() {
            var currBlock = $(terminal.parentEl);
            var currBlockId = currBlock.attr("data-block_id");
            var currBNode = QueryGen.getGraphNode(currBlockId);
            var currTemplateId = currBNode.template_id;
            var currBType = templates[currTemplateId].inputs[tid].qent_id;

            var connTerminal = terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            if (connBlock === undefined) return;
            var connBlockId = $(connBlock).attr("data-block_id");
            
            if (connBlockId != QueryGen.startName) {
                var connBNode = QueryGen.getGraphNode(connBlockId);
                var connBType = connBNode.button_id;
                var connBOutType = connBNode.output_type_id;
                var connBCat = connBNode.button_cat;

                if (connBCat == "qent") { // entity
                    var ok = GUI.isCompatible(currBType, connBOutType);
                    var msg = GUI.getButtonName(currBType) + " and " + GUI.getButtonName(connBOutType) + " may not be connected.";
                } else

                if (connBCat == "op") {
                    if (connBType == 7) { // extend
                        var ok = false;
                        var msg = "The extend operator may not be connected to a template block";
                    } else

                    if (connBType == 6) { // template
                        var ok = GUI.isCompatible(currBType, connBOutType);
                        var msg = GUI.getButtonName(currBType) + " and " + GUI.getButtonName(connBOutType) + " may not be connected";
                    } else

                    if (connBType == 5) { // genid
                        var ok = qent[currBType].genid_prefilter == true;
                        var msg = GUI.getButtonName(currBType) + " does not support genealogy ID pre-filtering.";
                        if (ok && connBOutType != undefined) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            msg = "Genealogy ID's predecessor " + GUI.getButtonName(connBOutType) + " may not be connected to " + GUI.getButtonName(currBType);
                        }
                    } else

                    if (connBType == 4) { // group by
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the group by block first.";
                        if (ok) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            msg = "Group by's output entity " + GUI.getButtonName(connBOutType) + " may not be connected to " + GUI.getButtonName(currBType);
                        }

                    } else

                    if (connBType <= 3 && connBType >= 1) { // logical operator
                        var ok = connBOutType != undefined;
                        var msg = "Please connect some entity to the " + ops[connBType].name + " operator first.";
                        if (ok) {
                            ok = GUI.isCompatible(currBType, connBOutType);
                            var msg = GUI.getButtonName(currBType) + " and " + GUI.getButtonName(connBOutType) + " may not be connected";
                        }
                    }
                }

                if (ok == false) {
                    alert(  msg,
                            "Cannot continue",
                            "Ok",
                            function() {
                                connTerminal.removeWire(terminal.wires[0]);
                                terminal.removeWire(terminal.wires[0]);
                            }
                        );
                    return;
                }
            }
            // update outputs on connected block
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.push(currBlockId + "." + tid);

            // update inputs on current block
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            curr_in[tid] = connBlockId;

            // update input paths for current terminal on current block
            var out_type = connBNode.output_type_id;
            if (out_type != undefined && out_type != currBType) {
                var all_paths = qent[out_type].fw_query_paths;
                for (var i in all_paths) {
                    var p = all_paths[i];
                    if (p.toEntity == currBType && p.isDefault == true) {
                        currBNode.query_path_id[tid] =  i;
                    }
                }
            } else {
                currBNode.query_path_id[tid] =  null;
            }

        }
    },

    new_Handle_Op_AddEvent: function(terminal, tid) {
        return function() {
            var currBlock = $(terminal.parentEl);
            var currBlockId = currBlock.attr("data-block_id");
            var currBNode = QueryGen.getGraphNode(currBlockId);
            var currBType = currBNode.button_id;
            var currBOutType = currBNode.output_type_id;
            
            var connTerminal = terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            
            if (connBlock === undefined) return;
            var connBlockId = $(connBlock).attr("data-block_id");
            
            if (connBlockId == QueryGen.startName) {
                var ok = false;
                var msg = "The " + GUI.getButtonName(currBType, "op") + " operator may not be connected to the start block.";
            
            } else {
                var connBNode = QueryGen.getGraphNode(connBlockId);
                var connBCat = connBNode.button_cat;
                var connBType = connBNode.button_id;
                var connBOutType = connBNode.output_type_id;

                if (connBCat == "qent") { // entity
                    var ok = currBOutType == undefined || connBOutType == currBOutType;
                    var msg = "Input entities to the " + GUI.getButtonName(currBType, "op") + " operator must have the same type.";
                } else

                if (connBCat == "op") {

                    if (connBType == 7) { // extend
                        var ok = false;
                        var msg = "The extend operator may not be connected to the " + GUI.getButtonName(currBType, "op") + " operator.";
                    } else

                    if (connBType == 6) { // template
                        var ok = currBOutType == undefined || connBOutType == currBOutType;
                        var msg = "Input entities to the " + GUI.getButtonName(currBType, "op") + " operator must have the same type.";
                    } else

                    if (connBType == 5) { // genid
                        var ok = false;
                        var msg = "The " + GUI.getButtonName(currBType, "op") + " operator does not support genealogy ID pre-filtering.";
                    } else

                    if (connBType == 4) { // group by
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the group by block first.";
                        if (ok) {
                            ok = currBOutType == undefined || connBOutType == currBOutType;
                            msg = "Input entities to the " + GUI.getButtonName(currBType, "op") + " operator must have the same type.";
                        }

                    } else

                    if (connBType <= 3 && connBType >= 1) { // logical operator
                        var ok = connBOutType != undefined;
                        var msg = "Please connect some entity to the " + ops[connBType].name + " operator first.";
                        if (ok) {
                            ok = currBOutType == undefined || connBOutType == currBOutType;
                            var msg = "Input entities to the " + GUI.getButtonName(currBType, "op") + " operator must have the same type.";
                        }
                    }
                }
            }

            if (ok == false) {
                alert(  msg,
                        "Cannot continue",
                        "Ok",
                        function() {
                            connTerminal.removeWire(terminal.wires[0]);
                            terminal.removeWire(terminal.wires[0]);
                        }
                    );
                return;
            }

            var c = QueryGen.getGraphNode(currBlockId).conn_inputs;
            c[tid] = true;

            // display type that will be assigned to logical operator
            if (currBOutType == undefined) {
                currBlock.append('<p class="param">'+GUI.getButtonName(connBOutType)+'</p>');
            }
            
            QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", connBOutType);

            // update outputs on connected block
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.push(currBlockId + "." + tid);
            // update inputs on current block
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            curr_in[tid] = connBlockId;

        }
    },

    new_Handle_Genid_AddEvent: function(terminal) {
        return function() {
            var currBlock = $(terminal.parentEl);
            var currBlockId = currBlock.attr("data-block_id");
            var currBNode = QueryGen.getGraphNode(currBlockId);

            var nextBlockId = currBNode.w_out[0];
            if (nextBlockId == undefined) {
                var nextBType = undefined;
            } else {
                var iid = nextBlockId.split(".")[1];
                nextBlockId = nextBlockId.split(".")[0];
                var nextBNode = QueryGen.getGraphNode(nextBlockId);
                if (nextBNode.button_cat == "qent") {
                    var nextBType = nextBNode.output_type_id;
                } else {
                    var templId = nextBNode.template_id;
                    var nextBType = templates[templId].inputs[iid].qent_id;
                }
            }

            var connTerminal = terminal.getConnectedTerminals()[0];
            var connBlock = connTerminal.parentEl;
            
            if (connBlock === undefined) return;
            var connBlockId = $(connBlock).attr("data-block_id");
            
            if (connBlockId == QueryGen.startName) {
                var ok = true;
            
            } else {
                var connBNode = QueryGen.getGraphNode(connBlockId);
                var connBCat = connBNode.button_cat;
                var connBType = connBNode.button_id;
                var connBOutType = connBNode.output_type_id;

                if (connBCat == "qent") { // entity
                    var ok = nextBType == undefined || GUI.isCompatible(connBOutType, nextBType);
                    var msg = "The Genealogy ID operator cannot be used to connect incompatible entities.";
                } else

                if (connBCat == "op") {

                    if (connBType == 6) { // template
                        var ok = nextBType == undefined || GUI.isCompatible(connBOutType, nextBType);
                        var msg = "The Genealogy ID operator cannot be used to connect incompatible entities.";
                    } else

                    if (connBType == 5) { // genid
                        var ok = false;
                        var msg = "Genealogy ID operators cannot be cascaded.";
                    } else

                    if (connBType == 4) { // group by
                        var ok = connBOutType != undefined;
                        var msg = "Please configure the group by block first.";
                        if (ok) {
                            ok = nextBType == undefined || GUI.isCompatible(connBOutType, nextBType);
                            msg = "The Genealogy ID operator cannot be used to connect incompatible entities.";
                        }

                    } else

                    if (connBType <= 3 && connBType >= 1) { // logical operator
                        var ok = connBOutType != undefined;
                        var msg = "Please connect some entity to the " + ops[connBType].name + " operator first.";
                        if (ok) {
                            ok = nextBType == undefined || GUI.isCompatible(connBOutType, nextBType);
                            msg = "The Genealogy ID operator cannot be used to connect incompatible entities.";
                        }
                    }
                }
            }

            if (ok == false) {
                alert(  msg,
                        "Cannot continue",
                        "Ok",
                        function() {
                            connTerminal.removeWire(terminal.wires[0]);
                            terminal.removeWire(terminal.wires[0]);
                        }
                    );
                return;
            }

            QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", connBOutType);

            // update outputs on connected block
            var conn_out = QueryGen.getGraphNode(connBlockId).w_out;
            conn_out.push(currBlockId + ".0");
            // update inputs on current block
            var curr_in = QueryGen.getGraphNode(currBlockId).w_in;
            curr_in[0] = connBlockId;

        }
    },

  
    // GUI function
    canvasClickHandler : function(evt) {
        if (QueryGen.clickedButton) {
            var button_id = QueryGen.clickedButton.data("dbid");
            var button_category = QueryGen.clickedButton.data("bcat");
            
            if (button_category == "op" && button_id == 6) {
                // template button
                // open template selection dialog
                $("#templdialog").data("evt", evt).dialog("open");
                QueryGen.clickedButton.removeClass("clicked");
                QueryGen.clickedButton = null;
                $("section#central").css("cursor", "auto");
                return;
            }

            if (button_category == "qent") {
                var button_title =  qent[button_id].name;
                var n_inputs = 1;
                var config = true;
                var button_ds_label = qent[button_id].dslabel;
                var out_from_in = false;
            } else if (button_category == "op") {
                var button_title =  ops[button_id].name;
                if (button_id != 6) {
                    var n_inputs = ops[button_id].numInputs;
                }
                var config = ops[button_id].configurable;
                var button_ds_label = "set";
                var out_from_in = ops[button_id].outFromIn;
            }
            
            QueryGen.addGraphNode(QueryGen.block_id, button_id, button_category); // call BL function to add new node to query graph
            QueryGen.drawQueryElement(QueryGen.block_id, button_id, button_title, button_category, button_ds_label, n_inputs, config, out_from_in, evt); // call GUI function to draw box

            QueryGen.block_id++;            
            
            QueryGen.clickedButton.removeClass("clicked");
            QueryGen.clickedButton = null;
            $("section#central").css("cursor", "auto");
        }

    },

    confirmTemplateSelection: function() {
        var tid = $("#seltempl").val();
        if (tid == null) return;

        var t = templates[tid];
        var button_title =  "Template";
        var button_subtitle = t.name;
        var n_inputs = t.inputs.length;
        var config = true;
        var button_ds_label = "set";
        var out_from_in = false;
        var button_id = 6;
        var button_category = "op";
        var evt = $("#templdialog").data("evt");
            
        QueryGen.addGraphNode(QueryGen.block_id, button_id, button_category, tid); // call BL function to add new node to query graph
        QueryGen.drawQueryElement(QueryGen.block_id, button_id, button_title, button_category, button_ds_label, n_inputs, config, out_from_in, evt, button_subtitle, tid); // call GUI function to draw box

        QueryGen.block_id++;


    },

    loadQueryGraph: function(queryGraph) {
     
        var o = $("#canvas").offset();
        var queue = [];

        for (var i=0; i < queryGraph['end'].w_in.length; ++i) {
            queue.push(['end', i, queryGraph['end'].w_in[i]]);
        }
        QueryGen.setGraphNodeAttr('end', 'translators', queryGraph['end'].translators)
        
        while (queue.length > 0) {
            var edge = queue.shift();
            var h = edge[0];
            var index  = edge[1];
            var j = edge[2];
            var x = queryGraph[j];
            console.log(x)
            var button_subtitle = undefined;
            var template_id = undefined;
            
            if (x.button_cat == "qent") {
                var button_title =  qent[x.button_id].name;
                var n_inputs = 1;
                var config = true;
                var button_ds_label = qent[x.button_id].dslabel;
                var out_from_in = false;
            } else
            if (x.button_cat == "op") {
                var button_title =  ops[x.button_id].name;
                var config = ops[x.button_id].configurable;
                var button_ds_label = "set";
                var out_from_in = ops[x.button_id].outFromIn;
                if (x.button_id != 6) {
                    var n_inputs = ops[x.button_id].numInputs;
                } else {
                    var template_id = x.template_id;
                    var n_inputs = templates[template_id].inputs.length;
                    var button_subtitle = templates[template_id].name;
                }
            }

            // click coordinates in the event format
            var pos = {pageX: x.offsetX + o.left, pageY: x.offsetY + 11 + o.top};
            
            QueryGen.addGraphNode(j, x.button_id, x.button_cat, template_id);
            
            if (x.button_cat == "qent"){
                for (var ip=0; ip<x.parameters.length; ++ip){
                    if (x.parameters[ip]['values'].length == 0 ){
                        x.parameters.splice(ip, 1);
                        ip--;
                    }
                }
            }

            QueryGen.setGraphNodeAttr(j, "parameters", x.parameters);

            QueryGen.setGraphNodeAttr(j, "output_type_id", x.output_type_id);
            QueryGen.setGraphNodeAttr(j, "outputs", x.outputs);
            QueryGen.setGraphNodeAttr(j, "gb_entity", x.gb_entity);
            if (x.button_cat == 'op' && x.button_id == 6) {
                QueryGen.setGraphNodeAttr(j, "template_id", x.template_id);
            }

            if ("conn_inputs" in QueryGen.getGraphNode(j)) {
                QueryGen.setGraphNodeAttr(j, "conn_inputs", [true, true]);
            }

            QueryGen.drawQueryElement(  j,
                                        x.button_id,
                                        button_title,
                                        x.button_cat,
                                        button_ds_label,
                                        n_inputs,
                                        config,
                                        out_from_in,
                                        pos,
                                        button_subtitle,
                                        template_id);


            if (x.parameters.length > 0) {
                $("p#box"+j).children("span#led").removeClass("filteroff filteroff2").addClass("filteron");
            }
            
            var t1 = $("#box"+j).data("out-terminal")[0];
            var t2 = $( (h == 'start' || h == 'end') ? "#"+h : "#box"+h).data("in-terminal")[index];
            //console.log("new wire: " + j +" -> " + h + "[" + index + "]");
            //console.log("queryGraph:", queryGraph);
            var w = new WireIt.Wire(t1, t2, $("#canvas").get(0), {color: "#EEEEEE", bordercolor:"#282828", width: 2});
            //console.log("queryGraph:", queryGraph);
            w.redraw();

            if (QueryGen.block_id <= j) {
                QueryGen.block_id = parseInt(j)+1;
            }

            for (var i=0; i < queryGraph[j].w_in.length; ++i) {
                console.log("iteration " + i);
                console.log("w_in: ", queryGraph[j].w_in);
                console.log("queue: ", queue);
                if (queryGraph[j].w_in[i] != 'start') {
                    queue.push([j, i, queryGraph[j].w_in[i]]);
                }
                else {
                    // if connected terminal is start, don't add edge to the queue, but just draw the wire
                    var t1 = $("#start").data("out-terminal")[0];
                    var t2 = $( (j == 'start' || j == 'end') ? "#"+j : "#box"+j).data("in-terminal")[i];
                    //console.log("new wire: start -> " + j + "[" + i + "]");
                    //console.log("w_in: ", queryGraph[j].w_in);
                    var w = new WireIt.Wire(t1, t2, $("#canvas").get(0), {color: "#EEEEEE", bordercolor:"#282828", width: 2});
                    //console.log("queryGraph:", queryGraph);
                    w.redraw();
                    //console.log("w_in: ", queryGraph[j].w_in);
                }
                
            }

        }
        
        // inputs must be restored at the end
        // they cannot be restored while the graph is being built because when a new block is connected
        // the "inputs" field in the block downstream is reset to the default input path
        // (thus overwriting any previous value)
        for (var j in queryGraph) {
            console.log( QueryGen.getGraphNode(j));
            QueryGen.setGraphNodeAttr(j, "query_path_id", queryGraph[j].query_path_id);
        }

        // load query template definition if tqid is in the request
        console.log(QueryGen.jsonStrGraph);
        
        if (tqid){
            QueryGen.startTemplateDefinition();
                
        }
        

    },

    hideDesignTools: function() {
        var leftcol = $("#leftcol");
        var width = parseFloat(leftcol.css("width")) + 
                    parseFloat(leftcol.css("margin-left")) + 
                    parseFloat(leftcol.css("margin-right"));
        $("#leftcol,#rightcol").hide(
            {
                progress: function() {

                    if (leftcol.css("display") == "none") return;
                    var new_width = parseFloat(leftcol.css("width")) + parseFloat(leftcol.css("margin-left")) +  parseFloat(leftcol.css("margin-right"));
                    var delta = width - new_width;
                    width = new_width;
                    $("p.box").each(function() {
                        var coords = $(this).offset();
                        $(this).offset(
                            {
                                top: coords.top,
                                left: coords.left - delta
                            }
                        );
                        var in_t = $(this).data("in-terminal")[0];
                        var out_t = $(this).data("out-terminal");
                        in_t.redrawAllWires();
                        for (var i = 0, l = out_t.length; i < l; ++i) {
                            out_t[i].redrawAllWires();
                        }
                    });
                }
            }
        );
    },

    unhideDesignTools: function() {
        var leftcol = $("#leftcol");
        var width = 0;
        $("#leftcol,#rightcol").show(
            {
                progress: function() {

                    if (leftcol.css("display") == "none") return;
                    var new_width = parseFloat(leftcol.css("width")) + parseFloat(leftcol.css("margin-left")) +  parseFloat(leftcol.css("margin-right"));
                    var delta = width - new_width;
                    width = new_width;
                    $("p.box").each(function() {
                        var coords = $(this).offset();
                        $(this).offset(
                            {
                                top: coords.top,
                                left: coords.left - delta
                            }
                        );
                        var in_t = $(this).data("in-terminal")[0];
                        var out_t = $(this).data("out-terminal");
                        in_t.redrawAllWires();
                        for (var i = 0, l = out_t.length; i < l; ++i) {
                            out_t[i].redrawAllWires();
                        }
                    });
                }
            }
        );
    },

    setDesignOverlay: function() {
        var s = $("#overlay");
        var c = $("#canvas");
        var w = c.css("width");
        var h = c.css("height");
        s.css("width", w);
        s.css("height", h);
        s.show();
    },

    unsetDesignOverlay: function() {
        $("#overlay").hide();
    }
}


var GUI = {
    
    isCompatible : function (a, b) {

        if (a == b) return true;

        for (var i in qent[a].fw_query_paths) {
            if (qent[a].fw_query_paths[i].toEntity == b)
                return true;
        }
        return false;
    },
    
    isManyToOneRelationship: function(a, b) {
        
        if (a == b) return true;

        for (var i in qent[a].fw_query_paths) {
            if (qent[a].fw_query_paths[i].toEntity == b)
                return !qent[a].fw_query_paths[i].oneToMany;
        }

        return null;
    },

    getManyToOneRelationships : function(a) {
    // returns a list of buttons reachable from current button through a many-to-one relationship
        var list = [];
        for (var i in qent[a].fw_query_paths) {
            if (qent[a].fw_query_paths[i].oneToMany == true) {
                list.push(qent[a].fw_query_paths[i].toEntity);
            }
        }
        return list;
    },

    getManyToOneRelationships2 : function(a) {
    // returns a list of QueryPath ids leading from current button to another button through a many-to-one relationship
        var list = [];
        for (var i in qent[a].fw_query_paths) {
            if (qent[a].fw_query_paths[i].oneToMany == true) {
                list.push(i);
            }
        }
        return list;
    },

    
    getButtonName : function (id, cat) {
        
        if (cat === undefined || cat === "qent")
            return qent[id].name;

        else

        if (cat === "op")
            return ops[id].name;
        
    },
    
    getParameterName : function (id) {

        return GUI.data.Parameter[id].name;
    },
    
    getValue : function (id) {

        return GUI.data.Value[id].value;
    }
}
