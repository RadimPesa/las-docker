var iTableCounter = 1;
var untreated = "Untreated";
// network layout definitions
var directionInput = 'UD'; // up-down
var colors = {
    untreated: '#87cefa',
    treated: '#ff0066',
    historical: '#8b2af9',
    treatment_0: '#c5b0d5',
    treatment_1: '#9467bd',
    treatment_2: '#ff9896',
    treatment_3: '#d62728',
    treatment_4: '#98df8a',
    treatment_5: '#2ca02c',
    treatment_6: '#ffbb78',
    treatment_7: '#ff7f0e',
    treatment_8: '#aec7e8',
    treatment_9: '#1f77b4',
    treatment_10: '#9edae5',
    treatment_11: '#17becf',
    treatment_12: '#dbdb8d',
    treatment_13: '#bcbd22',
    treatment_14: '#c7c7c7',
    treatment_15: '#7f7f7f',
    treatment_16: '#f7b6d2',
    treatment_17: '#e377c2',
    treatment_18: '#c49c94',
    treatment_19: '#8c564b'
};
var highlight = { background: '#f4eb42', border: '#f4d341' };
var aliquotCounts = {
    none: { size: 20, background: '#ffffff' },
    few: { size: 30 },
    many: { size: 40}
};
var shapes = {
    vital: 'triangle',
    nonvital: 'dot'
};
var level_0 = Object.keys(colors);
var level_1 = Object.keys(shapes);
var level_2 = Object.keys(aliquotCounts);
function generateNodeGroups(g, loop_0, loop_1, loop_2) {
    for (var i = 0; i < loop_0.length; ++i) {
        for (var j = 0; j < loop_1.length; ++j) {
            for (var k = 0; k < loop_2.length; ++k) {
                var g_name = loop_0[i] + "_" + loop_1[j] + "_" + loop_2[k];
                g[g_name] = {
                    shape: shapes[loop_1[j]],
                    size: aliquotCounts[loop_2[k]].size,
                    color: {
                        border: colors[loop_0[i]],
                        background: aliquotCounts[loop_2[k]].hasOwnProperty('background') ? aliquotCounts[loop_2[k]].background : colors[loop_0[i]],
                        highlight: highlight
                    }
                };
            }
        }
    }
}

var groups = {};

var options = {
    layout: {
        hierarchical: {
            direction: directionInput,
            sortMethod : 'directed'
        }
    },
    height: '750px',
    interaction: { hover: true, selectable: true, multiselect: true },
    groups: groups,
    edges: {
        color: 'grey'
    }
};

// export options definitions
var export_opts = {
    fieldSeparator: "\t",
    listFieldSeparator: ", ",
    missingValue: "n/a",
    fields: [
        {
            name: "genID",
            displayName: "Genealogy ID",
        },
        {
            name: "explantDate",
            displayName: "Explant date",
        },
        {
            name: "implantDate",
            displayName: "Implant date",
        },
        {
            name: "vital",
            displayName: "Vital",
        },
        {
            name: "historical",
            displayName: "Historical",
        },
        {
            name: "aliquots",
            displayName: "Aliquots",
        },
        {
            name: "parentAliquot",
            displayName: "Parent aliquot",
        },
        {
            name: "parentMouse",
            displayName: "Parent mouse",
        },
        {
            name: "treatments",
            displayName: "Treatments",
        }
    ]
};
var export_file = null;

var prev_highlighted = [];

var highlight_treatments = false;


var ctrlPressed = false;

jQuery(document).ready(function(){
	initCsrf();
    initDialogs();
    initGUIElements();
    initKeyListeners();

    if (plot) {
        console.log("Start plot");
        generateNodeGroups(groups, level_0, level_1, level_2);
        markOrphanMice(mice);
        updateParents(savedParents);
        drawLegend();
        startPlot(mice);
    }

});

function initKeyListeners() {
    $(document).keydown(function(event){
        if(event.which=="17") {
            ctrlPressed = true;
        }
    });

    $(document).keyup(function(){
        ctrlPressed = false;
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

function clearSelection() {
    if (document.selection) {
        document.selection.empty();
    } else if (window.getSelection) {
        window.getSelection().removeAllRanges();
    }
}

function initDialogs() {
    $("#editmissing-dialog").dialog({
        autoOpen: false,
        title: "Edit missing relationships",
        width: 800,
        height: 560,
        resizable: false,
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
                    var dt = $("#child-father").dataTable();
                    var newParents = {};
                    dt.$("input.genid").each(function() {
                        var child = $(this).parent().parent().find("td:eq(0)").text();
                        var parent = $(this).val();
                        newParents[child] = parent;
                    });
                    updateParents(newParents);
                    sendParentsToServer(newParents);
                    startPlot(mice);
                    $(this).dialog("close");
                }
            }
        ],
        open: function() {
            fillInOrphanMice(mice);
        }
    });

    $("#exportselected-dialog").dialog({
        autoOpen: false,
        title: "Export selected nodes",
        width: 800,
        height: 500,
        resizable: false,
        buttons: [
            {
                text: "Cancel",
                click: function() {
                    $(this).dialog("close");
                }
            },
            {
                text: "Copy to clipboard",
                click: function() {
                    // copy to clipboard
                    $("#exportselected-text").select();
                    var ret = document.execCommand("copy");
                    alert(ret ? "Copied to clipboard!" : "Could not copy to clipboard", "Export to clipboard", "Ok", function() {
                        $("#exportselected-dialog").dialog("close");
                    });
                }
            },
            {
                text: "Save to file",
                click: function() {
                    // save to file
                    var link = document.createElement('a');
                    link.setAttribute('download', 'export.txt');
                    link.href = makeTextFile($("#exportselected-text").val());
                    document.body.appendChild(link);
                    // wait for the link to be added to the document
                    window.requestAnimationFrame(function () {
                        var event = new MouseEvent('click');
                        link.dispatchEvent(event);
                        document.body.removeChild(link);
                    });
                    $(this).dialog("close");
                }
            }
        ],
        open: function() {
            var text = exportSelectedNodes();
            if (text != null) {
                $("#exportselected-text").val(text);
                $("#exportselected-dialog").next(".ui-dialog-buttonpane").children(".ui-dialog-buttonset").children("button:contains('Copy to clipboard')").attr("disabled", false).removeClass("ui-state-disabled");
                $("#exportselected-dialog").next(".ui-dialog-buttonpane").children(".ui-dialog-buttonset").children("button:contains('Save to file')").attr("disabled", false).removeClass("ui-state-disabled");
            } else {
                $("#exportselected-text").val("No nodes have been selected in the current view.");
                $("#exportselected-dialog").next(".ui-dialog-buttonpane").children(".ui-dialog-buttonset").children("button:contains('Copy to clipboard')").attr("disabled", true).addClass("ui-state-disabled");
                $("#exportselected-dialog").next(".ui-dialog-buttonpane").children(".ui-dialog-buttonset").children("button:contains('Save to file')").attr("disabled", true).addClass("ui-state-disabled");
            }
            clearSelection();
        }
    });
}

function initGUIElements() {
    $("#child-father").dataTable({
        iDisplayLength: 6,
        columns: [
            {
                title: "Child mouse GenID"
            },
            {
                title: "Parent mouse GenID",
                defaultContent: "<input type='text' class='genid' style='width: 220px; height: 25px' />",
            }
        ]
    });

    $("#editmissing").click(function() {
        $("#editmissing-dialog").dialog("open");
    });

    $("#dohighlight").click(function() {
        var genid = $("#highlight").val().trim();
        if (genid == "")
            return;
        highlightNodesByGenid(genid);
    });

    $("#removehighlight").click(removeHighlight);

    $("#exportselected").click(function() {
        $("#exportselected-dialog").dialog("open");
    });

    $("#pathtoroot").click(highlightPathToRoot);

    $(".treatcolors").change(function() {
        highlight_treatments = $(".treatcolors:checked").val() == "yes" ? true : false;
        startPlot(mice);
    });

    $("#importrel").click(importRelationships);

    $("#exportrel").click(exportRelationships);

    $("#importfile").change(function() {
        var r = new FileReader();
        r.onload = function(evt) {
            importRelationships_contd(evt.target.result);
            $("#importfile").val(null);
        }
        r.readAsText($("#importfile")[0].files[0]);
    });
}

function updateParents(parents) {
    for (var child in parents) {
        var parent = parents[child].trim();
        mice[child].parentMouse = parent != "" ? parent : null;
        if (parent != "" && !(parent in mice)) {
            mice[parent] = {aliquots: [], parentAliquot: null, parentMouse: null, treatments: [], vital: false, historical: true};
        }
    }
}

function sendParentsToServer(parents) {
    $.ajax({
        url: "./",
        type: "post",
        data: {
            case: case_id,
            parents: JSON.stringify(parents)
        },
        success: function(data) {
            console.log("Parent-child associations saved.");
        },
        error: function(data) {
            alert("Error: failed to save parent-child associations.");
        }
    });
}

function submitHandler() {
    var case_id = $("#case").val();
    if (case_id.length != 7) {
        alert("Please enter a valid case id", "Error");
        return false;
    }
    var missing = $("#missing").val();
    // todo: validate genids in missing
    return true;
}

function getGroup(obj) {
    if (obj.historical == true) {
        var treatment = "historical";
    } else
    if (obj.treatments.length > 0) {
        if (highlight_treatments == false) {
            var treatment = "treated";
        } else {
            var treatment = treatment_map[obj.treatments[0]];
        }
    } else {
        var treatment = "untreated";
    }

    if (obj.vital == true) {
        var vital = "vital";
    } else {
        var vital = "nonvital";
    }

    if (obj.aliquots.length == 0) {
        var aliquots = "none";
    } else if (obj.aliquots.length < 3) {
        var aliquots = "few";
    } else {
        var aliquots = "many";
    }

    return treatment + "_" + vital + "_" + aliquots;
}

function getTitle(id, obj) {
    
    return "<b>" + id + "</b>" + "<br>" + "vital: " + obj.vital + "<br>" + "historical: " + obj.historical + "<br>" + "aliquots: " + (obj.aliquots.length > 0 ? obj.aliquots.map(function(e) {return e.slice(20);}).join(", "): "n/a") + "<br>" + "treatments: " + (obj.treatments.length > 0 ? obj.treatments.join(", "): "n/a") + "<br>" + "implant date: " + (obj.implantDate != null ? obj.implantDate : "n/a") + "<br>" + "explant date: " + (obj.explantDate != null ? obj.explantDate : "n/a") + "<br>" + "death date: " + (obj.deathDate != null ? obj.deathDate : "n/a");
}

function getLevel(id) {

    return parseInt(id.slice(12, 14));
}

function splitTissueLineage(data) {
    var tissues = {};
    for (var m in data) {
        var t = m.slice(7, 9);
        var l = m.slice(10, 12);
        if (!(t in tissues)) {
            tissues[t] = {};
        }
        if (!(l in tissues[t])) {
            tissues[t][l] = {};
        }
        tissues[t][l][m] = data[m];
    }
    return tissues;
}

function remapTreatments(data) {
    var t_map = {};
    var i = 0;
    for (var m in data) {
        for (var j = 0; j < data[m].treatments.length; ++j) {
            if (!t_map.hasOwnProperty(data[m].treatments[j])) {
                t_map[data[m].treatments[j]] = "treatment_" + i;
                ++i;
            }
        }
    }
    return t_map;
}

function startPlot(data) {
    tissues = splitTissueLineage(data);
    treatment_map = remapTreatments(data);
    nodes = {};
    edges = {};
    global_nodes_map = {};
    global_nodes_r_map = {};
    network = {};
    ctrl = {};
    matrixTL = {};
    
    // remove previous content (if any)
    $("#tissues div.ui-tabs").tabs("destroy");
    $("#tissues.ui-tabs").tabs("destroy");
    $("#tissues").empty();
    $("#tissues").append("<ul></ul>");

    for (t in tissues) {
        console.log("Create tab for tissue: ", t);
        $("#tissues > ul").append("<li><a data-tissue='" + t + "' href='#tissue_" + t + "'><b>" + "Tissue: " + t + "</b></a></li>");
        $("#tissues").append("<div id='tissue_" + t + "' data-tissue='" + t + "'></div>");
        $("#tissue_" + t).append("<div id='tissue_" + t + "_lineages' class='lineages'><ul></ul></div>");
        network[t] = {};
        nodes[t] = {};
        edges[t] = {};
        ctrl[t] = {};
        matrixTL[t] = {};
        global_nodes_map[t] = {};
        global_nodes_r_map[t] = {};
        var lineages = Object.keys(tissues[t]);
        lineages.sort();
        for (var i = 0; i < lineages.length; ++i) {
            var l = lineages[i];
            console.log("Create tab for lineage:", l);
            $("#tissue_" + t + "_lineages > ul").append("<li><a data-tissue='" + t + "' data-lineage='" + l + "' href='#tissue_" + t + "_lineage_" + l + "'><b>" + "Lineage: " + l + "</b></a></li>");
            $("#tissue_" + t + "_lineages").append("<div id='tissue_" + t + "_lineage_" + l + "' data-tissue='" + t + "' data-lineage='" + l + "'></div>")
            $("#tissue_" + t + "_lineage_" + l).append("<div style='color: #ffffff; font-weight: bold; background-color: #444444; margin: 3px; margin-bottom: 0px; padding: 3px; padding-left: 6px'>Genealogy tree</div><div id='network_" + t + "_" + l +"' style='margin: 3px; margin-top: 0px; border: solid 1px grey; background-color: #ffffff'></div>");
            network[t][l] = null;
            global_nodes_map[t][l] = {};
            global_nodes_r_map[t][l] = [];
            matrixTL[t][l] = null;
            drawMatrixTL(t, l);
        }
    }
    $("#tissues").tabs();
    $(".lineages").tabs({
        activate: function(event, ui) {
            var t = $(ui.newTab.context).data("tissue");
            var l = $(ui.newTab.context).data("lineage");
            network[t][l].fit();
        }
    });

    for (t in tissues) {
        plotTissue(t, tissues[t]);
    }
}

function drawLegend() {
    var interaction_opts = {dragNodes: false, dragView: false, selectable: false, zoomView: false};
    new vis.Network(document.getElementById('legend-1'), {nodes: [{id: 0, shape: shapes.vital, color: { background: '#999999', border: '#777777'}}], edges: []}, {interaction: interaction_opts});
    new vis.Network(document.getElementById('legend-2'), {nodes: [{id: 0, shape: shapes.nonvital, color: { background: '#999999', border: '#777777'}}], edges: []}, {interaction: interaction_opts});
    new vis.Network(document.getElementById('legend-3'), {nodes: [{id: 0, shape: "square", color: colors.treated}], edges: []}, {interaction: interaction_opts});
    new vis.Network(document.getElementById('legend-4'), {nodes: [{id: 0, shape: "square", color: colors.untreated}], edges: []}, {interaction: interaction_opts});
    new vis.Network(document.getElementById('legend-4b'), {nodes: [{id: 0, shape: "square", color: colors.historical}], edges: []}, {interaction: interaction_opts});
    new vis.Network(document.getElementById('legend-5'), {nodes: [{id: 0, shape: "square", color: { background: '#ffffff', border: "#999999"}, size: 5*aliquotCounts.none.size}, {id: 1, shape: "square", color: "#999999", size: 5*aliquotCounts.few.size}, {id: 2, shape: "square", color: "#999999", size: 5*aliquotCounts.many.size}], edges: []}, {layout: {hierarchical: { direction: directionInput, sortMethod : 'directed'}}, interaction: interaction_opts});
}

function plotTissue(tissue, tissueData) {
    var lineages = Object.keys(tissueData);
    lineages.sort();
    for (var i = 0; i < lineages.length; ++i) {
        var lineage = lineages[i];
        var nodes_map = global_nodes_map[tissue][lineage];
        var nodes_r_map = global_nodes_r_map[tissue][lineage];
        console.log("Plot lineage:", lineage);
        console.log("   with data:", tissueData[lineage]);
        var nodes_list = [];
        var edges_list = [];
        var j = 0;
        for (var m in tissueData[lineage]) {
            var short_id = m.slice(10, 17);
            nodes_list.push( {   id: j,
                            group: getGroup(tissueData[lineage][m]),
                            title: getTitle(m, tissueData[lineage][m]),
                            level: getLevel(m)
                        });
            nodes_map[m] = j;
            nodes_r_map[j++] = m;
        }
        for (var m in tissueData[lineage]) {
            if (tissueData[lineage][m]['parentMouse'] != null) {
                var p = tissueData[lineage][m]['parentMouse'];
                edges_list.push({from: nodes_map[p], to: nodes_map[m]})
            }
        }

        // create a network
        var container = document.getElementById("network_" + tissue + "_" + lineage);
        nodes[tissue][lineage] = new vis.DataSet({});
        edges[tissue][lineage] = new vis.DataSet({});
        nodes[tissue][lineage].add(nodes_list);
        edges[tissue][lineage].add(edges_list);
        var data = {
            nodes: nodes[tissue][lineage],
            edges: edges[tissue][lineage]
        };

        if (network[tissue][lineage] !== null) {
            network[tissue][lineage].destroy();
            network[tissue][lineage] = null;
        }
        
        network[tissue][lineage] = new vis.Network(container, data, options);

        // display "loading" overlay (avoids a blank div being displayed for several seconds when drawing large networks)
        ctrl[tissue][lineage] = getBusyOverlay(container, {color:'#B2B2B2', opacity:1, text:'Loading...', style: 'color: #222222;'}, {color:'#222222', weight:'3', size:50, type:'rectangle', count:12});
        
        network[tissue][lineage].on("hold", function (data) {
            console.log(nodes_r_map[data.nodes[0]]);
        });
        
        // set "afterDrawing" event handler to remove overlay once drawing is complete and clear event handler
        network[tissue][lineage].on("afterDrawing", function(tissue, lineage) {
            return function (data) {
                console.log("Finish drawing: ", tissue, lineage);
                ctrl[tissue][lineage].remove();
                network[tissue][lineage].off("afterDrawing");
                network[tissue][lineage].fit();
            }
        } (tissue, lineage));

    }
    return;
}

function drawMatrixTL(tissue, lineage) {
    var ext_container = $("#tissue_" + tissue + "_lineage_" + lineage);
    var div = $("<div style='color: #ffffff; font-weight: bold; background-color: #444444; margin: 3px; margin-bottom: 0px; padding: 3px; padding-left: 6px'>Mice count for treatment arms vs. aliquot types</div>");
    ext_container.append(div);
    var container = $("<div id='matrix_" + tissue + "_" + lineage +"' style='margin: 3px; margin-top: 0px; border: solid 1px grey; background-color: #ffffff; padding: 5px'></div>");
    container.text("Click on a count cell to highlight the corresponding nodes on the tree (CTRL + click adds to current selection)");
    ext_container.append(container);
    var res = computeMatrixTL(tissues[tissue][lineage]);
    matrixTL[tissue][lineage] = res;
    var t_list = res[0]; var a_list = res[1]; var m = res[2];
    if (t_list.length == 0) {
        container.append("<p style='margin: 10px'>No treated mice.</p>");
        return;
    }
    if (a_list.length == 0) {
        container.append("<p style='margin: 10px'>No aliquots available.</p>");
        return;
    }
    var table = $("<table class='count'></table>");
    var tbody = $("<tbody></tbody>");
    
    // add column headers
    var tr = $("<tr></tr>");
    tr.append("<td></td>");
    for (var column = 0; column < a_list.length; ++column) {
        tr.append("<td class='aliquot_type'>" + a_list[column] + "</td>");
    }
    // append column for row total
    tr.append("<td>Count<br>distinct</td>");
    tbody.append(tr);
    for (var row = 0; row < t_list.length; ++row) {
        var tr = $("<tr></tr>");
        if (highlight_treatments == false) {
            tr.append("<td class='treatment_type'>" + t_list[row] + "</td>");
        } else {
            if (row == 0) {
                tr.append("<td class='treatment_type' style='background-color: " + colors.untreated + "'>" + t_list[row] + "</td>");
            } else {
                tr.append("<td class='treatment_type' style='background-color: " + colors[treatment_map[t_list[row]]] + "'>" + t_list[row] + "</td>");
            }
        }
        var row_elems = [];
        for (var column = 0; column < a_list.length; ++column) {
            tr.append("<td class='data' data-treatment='" + t_list[row] + "' data-aliqtype='" + a_list[column] + "'>" + m[t_list[row]][a_list[column]].length + "</td>");
            row_elems = row_elems.concat(m[t_list[row]][a_list[column]]);
        }
        // append row total
        tr.append("<td class='data' data-treatment='" + t_list[row] + "'>" + unique(row_elems).length + "</td>");
        tbody.append(tr);
    }
    // append row for column total
    var tr = $("<tr></tr>");
    tr.append("<td>Count distinct</td>");
    var all_elems = [];
    for (var column = 0; column < a_list.length; ++column) {
        var col_elems = [];
        for (var row = 0; row < t_list.length; ++row) {
            col_elems = col_elems.concat(m[t_list[row]][a_list[column]]);
            all_elems = all_elems.concat(m[t_list[row]][a_list[column]]);
        }
        tr.append("<td class='data' data-aliqtype='" + a_list[column] + "'>" + unique(col_elems).length + "</td>");
    }
    // append empty cell to complete row
    tr.append("<td>" + unique(all_elems).length + "</td>");
    tbody.append(tr);
    table.append(tbody);
    container.append(table);
    table.on("click", "td.data", function() {
        var active = getActiveTissueLineage();
        var tissue = active[0];
        var lineage = active[1];
        var treatment = $(this).data("treatment");
        var aliquot_type = $(this).data("aliqtype");
        if (treatment != undefined && aliquot_type != undefined) {
            var genids = matrixTL[tissue][lineage][2][treatment][aliquot_type];
        } else if (treatment == undefined) {
            var column_elems = [];
            for (var t in matrixTL[tissue][lineage][2]) {
                column_elems = column_elems.concat(matrixTL[tissue][lineage][2][t][aliquot_type]);
            }
            var genids = unique(column_elems);
        } else if (aliquot_type == undefined) {
            var row_elems = [];
            for (var a in matrixTL[tissue][lineage][2][treatment]) {
                row_elems = row_elems.concat(matrixTL[tissue][lineage][2][treatment][a]);
            }
            var genids = unique(row_elems);
        }
        var nodeId_list = genids.map(function(el, i) {
            return global_nodes_map[tissue][lineage][el];
        });
        var selected_nodes = network[tissue][lineage].getSelectedNodes();
        if (ctrlPressed) {
            network[tissue][lineage].selectNodes(selected_nodes.concat(nodeId_list));
        } else {
            network[tissue][lineage].selectNodes(nodeId_list);
        }
    });
}

function markOrphanMice(data) {
    for (var m in data) {
        data[m].orphan = data[m].parentMouse ? false : true;
    }
}
    
function fillInOrphanMice(data, newParents={}) {
    var dt = $("#child-father").dataTable();
    dt.fnClearTable();
    for (var m in data) {
        if (data[m].orphan) {
            var i = dt.fnAddData([m])[0];
            var parentMouse = newParents[m] ? newParents[m] : data[m].parentMouse ? data[m].parentMouse : null;
            if (parentMouse) {
                var row = dt.fnGetNodes(i);
                dt.$("input", row).val(parentMouse);
            }
        }
    }
    $("#child-father").dataTable()
                .$("input.genid")
                .autocomplete({
                    source: function(request, response) {
                        var results = $.ui.autocomplete.filter(Object.keys(mice), request.term);
                        response(results.slice(0, 10));
                    }
                });
}

function toggleHighlightNodes(node_ids, flag) {
    var highlightColor = "#7fff00";
    var highlightBorderColor = "#59b300";
    var color = flag ? {background: highlightColor, border: highlightBorderColor} : {};
    for (var i = 0; i < node_ids.length; ++i) {
        var coords = node_ids[i];
        var n = nodes[coords[0]][coords[1]].get(coords[2]);
        n.color = color;
        nodes[coords[0]][coords[1]].update(n);
    }
}

function getTissue(genid) {

    return genid.slice(7, 9);
}

function getLineage(genid) {

    return genid.slice(10, 12);
}

function filterNodesByGenid(genid) {
    var genid_tissue = getTissue(genid);
    var genid_lineage = getLineage(genid);

    var node_ids = [];
    for (var tissue in global_nodes_r_map) {
        if (tissue == genid_tissue || genid_tissue == "") {
            for (var lineage in global_nodes_r_map[tissue]) {
                if (lineage == genid_lineage || genid_lineage == "") {
                    for (var i = 0; i < global_nodes_r_map[tissue][lineage].length; ++i) {
                        if (global_nodes_r_map[tissue][lineage][i].startsWith(genid)) {
                            node_ids.push([tissue, lineage, i]);
                        }
                    }
                }
            }
        }
    }
    return node_ids;
}

function highlightNodesByGenid(genid) {
    toggleHighlightNodes(prev_highlighted, false);
    prev_highlighted = filterNodesByGenid(genid);
    toggleHighlightNodes(prev_highlighted, true);
}

function removeHighlight() {

    toggleHighlightNodes(prev_highlighted, false);
}

function getAliquotType(genid) {
    if (isNaN(genid.slice(21, 22))) {
        // normal aliquot
        return genid.slice(20, 22);
    } else {
        if (isNaN(genid.slice(23, 24))) {
            // 2nd derivation
            return genid.slice(20, 21) + genid.slice(23, 24);
        } else {
            // R or D
            return genid.slice(20, 21);
        }
    }
}

function getUniqueTreatmentsTL(data) {
    var treatments = [];
    for (m in data) {
        var info = data[m];
        for (var j = 0; j < info.treatments.length; ++j) {
            var t = info.treatments[j];
            if (treatments.indexOf(t) == -1) {
                treatments.push(t);
            }
        }
    }
    return [untreated].concat(treatments.sort());
}

function getUniqueTreatmentsM(data) {
    var treatments = [];
    for (var j = 0; j < data.treatments.length; ++j) {
        var t = data.treatments[j];
        if (treatments.indexOf(t) == -1) {
            treatments.push(t);
        }
    }
    if (treatments.length) {
        return treatments.sort();
    } else {
        return [untreated];
    }
}

function getUniqueAliquotTypesTL(data) {
    var aliquotTypes = [];
    for (m in data) {
        var info = data[m];
        for (var j = 0; j < info.aliquots.length; ++j) {
            var a = getAliquotType(info.aliquots[j]);
            if (aliquotTypes.indexOf(a) == -1) {
                aliquotTypes.push(a);
            }
        }
    }
    return aliquotTypes.sort();
}

function getUniqueAliquotTypesM(data) {
    var aliquotTypes = [];
    for (var j = 0; j < data.aliquots.length; ++j) {
        var a = getAliquotType(data.aliquots[j]);
        if (aliquotTypes.indexOf(a) == -1) {
            aliquotTypes.push(a);
        }
    }
    return aliquotTypes.sort();
}

function computeMatrixTL(data) {
    var column_headers = getUniqueAliquotTypesTL(data);
    var row_headers = getUniqueTreatmentsTL(data);
    var count_matrix = {};
    for (var i = 0; i < row_headers.length; ++i) {
        count_matrix[row_headers[i]] = {};
        for (var j = 0; j < column_headers.length; ++j) {
            count_matrix[row_headers[i]][column_headers[j]] = []; // = 0;
        }
    }
    for (var m in data) {
        var info = data[m];
        var a_list = getUniqueAliquotTypesM(info);
        var t_list = getUniqueTreatmentsM(info);
        for (var i = 0; i < t_list.length; ++i) {
            for (var j = 0; j < a_list.length; ++j) {
                count_matrix[t_list[i]][a_list[j]].push(m); // += 1;
            }
        }
    }
    return [row_headers, column_headers, count_matrix];
}

function getActiveTissueLineage() {
    // get active tissue tab
    var active_tissue_index = $("#tissues").tabs("option", "active");
    var active_tissue_div = $($("#tissues").tabs("widget").children("div.ui-tabs-panel").get(active_tissue_index));
    // get lineages tabs object
    var lineages = active_tissue_div.find(".lineages");
    // get active lineage tab
    var active_lineage_index = lineages.tabs("option", "active");
    var active_lineage_div = $(lineages.tabs("widget").children("div.ui-tabs-panel").get(active_lineage_index));
    // get active tissue and lineage names
    var tissue = active_lineage_div.data("tissue");
    var lineage = active_lineage_div.data("lineage");
    return [tissue, lineage];
}

function getSelectedNodes(tissue, lineage) {

    return network[tissue][lineage].getSelectedNodes();
}

function exportSelectedNodes() {
    var active = getActiveTissueLineage();
    var tissue = active[0];
    var lineage = active[1];
    var nodes = getSelectedNodes(tissue, lineage);
    var nodes_info = nodes.map(function(el, i) {
        var genid = global_nodes_r_map[tissue][lineage][el];
        var obj = mice[genid];
        obj.genID = genid;
        return obj;
    });
    
    if (nodes_info.length == 0) return null;
    
    // generate output
    var output = [];
    var line = [];
    // export headers
    for (var i = 0; i < export_opts.fields.length; ++i) {
        line.push(export_opts.fields[i].displayName);
    }
    output.push(line.join(export_opts.fieldSeparator));
    // export data
    for (var i = 0; i < nodes_info.length; ++i) {
        line = [];
        for (var j = 0; j < export_opts.fields.length; ++j) {
            var f = nodes_info[i][export_opts.fields[j].name];
            if (Array.isArray(f)) {
                if (f.length > 0) {
                    line.push(f.join(export_opts.listFieldSeparator));
                } else {
                    line.push(export_opts.missingValue);
                }
            } else {
                if (f === undefined || f === null) {
                    line.push(export_opts.missingValue);
                } else {
                    line.push(String(f));
                }
            }
        }
        output.push(line.join(export_opts.fieldSeparator));
    }
    return output.join("\n");
}

function makeTextFile(text) {
    var data = new Blob([text], {type: 'text/plain'});

    // If we are replacing a previously generated file we need to
    // manually revoke the object URL to avoid memory leaks.
    if (export_file !== null) {
      window.URL.revokeObjectURL(export_file);
    }

    export_file = window.URL.createObjectURL(data);

    // returns a URL you can use as a href
    return export_file;
  };

function unique(a) {
    var seen = {};
    return a.filter(function(item) {
        return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
}

function highlightPathToRoot() {
    var res = getActiveTissueLineage();
    var tissue = res[0];
    var lineage = res[1];
    var selected = network[tissue][lineage].getSelectedNodes();
    var queue = [];
    for (var i = 0; i < selected.length; ++i) {
        var x = selected[i];
        while (x) {
            queue.push(x);
            var connectedEdges = network[tissue][lineage].getConnectedEdges(x);
            var incoming = null;
            for (var j = 0; j < connectedEdges.length; ++j) {
                var e = edges[tissue][lineage].get(connectedEdges[j]);
                if (e.to == x) {
                    incoming = e.from;
                    break;
                }
            }
            x = incoming;
        }
    }
    network[tissue][lineage].selectNodes(queue);
}

function importRelationships() {
    // save manually inserted entries (if any)
    var dt = $("#child-father").dataTable();
    var newParents = {};
    dt.$("input.genid").each(function() {
        var child = $(this).parent().parent().find("td:eq(0)").text();
        var parent = $(this).val();
        newParents[child] = parent;
    });
    updateParents(newParents);
    // read file and load entries
    $("#importfile").click();
}

function importRelationships_contd(text) {
    var lines = text.split("\n");
    var dict = {};
    for (var i = 0; i < lines.length; ++i) {
        var line = lines[i];
        var fields = line.split('\t');
        if (fields[1].trim() != "") {
            dict[fields[0]] = fields[1];
        }
    }
    // update "mice" with the new entries
    //updateParents(dict);
    // redraw the table
    fillInOrphanMice(mice, dict);
}

function exportRelationships() {
    var dt = $("#child-father").dataTable();
    var rels = [];
    dt.$("input.genid").each(function() {
        var child = $(this).parent().parent().find("td:eq(0)").text();
        var parent = $(this).val();
        rels.push([child, parent].join("\t"));
    });
    var text = rels.join("\n");
    var link = document.createElement('a');
    link.setAttribute('download', case_id + '_relationships.txt');
    link.href = makeTextFile(text);
    document.body.appendChild(link);
    // wait for the link to be added to the document
    window.requestAnimationFrame(function () {
        var event = new MouseEvent('click');
        link.dispatchEvent(event);
        document.body.removeChild(link);
    });
}