probes = {}
probesName = {}
analysisMatrix = {}
aggrFunct = {}//{'use': false, 'funct': null}
refsForOutputVars = {};
fid = null;

$.arrayIntersect = function(a, b)
{
    return $.grep(a, function(i)
    {
        return $.inArray(i, b) > -1;
    });
};


// init document
jQuery(document).ready(function(){
    // CRFS TOKEN   
    jQuery('html').ajaxSend(function(event, xhr, settings) {
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

    initProbes();
    initFormulas();
    $($('input[name="formula"]')[0]).prop('checked', true);

    $('table#aggregate').on ('change', 'input.aggrFlag', function(){
        if ($(this).prop('checked')){
            var targetElem = $(this).parent().next().find('select');
            targetElem.prop('disabled', false);
            aggrFunct[targetElem.data('varname')].use = true;
        }
        else{
            var targetElem = $(this).parent().next().find('select');
            targetElem.prop('disabled', true);
            aggrFunct[targetElem.data('varname')].use = false;
        }
    });

    $('table#aggregate').on ('change', 'select.aggrMode', function() {
        var val = $(this).val();
        if (val == 'probe') {
            $(this).siblings('div.byProbe').show();
            $(this).siblings('div.acrossProbes').hide();
        } else if (val == 'all') {
            $(this).siblings('div.byProbe').hide();
            $(this).siblings('div.acrossProbes').show();
        }
    });

});


function computeAnalysis(){

    fid = $('input[name="formula"]:checked').val();
    var analysis_type = formulas[fid].analysis_type;
    $("#analysis_type option[value='" + analysis_type + "']").prop("selected", true);

    var outputs = formulas[fid].output;
    var setVar = {}
    for (var p in probes){
        setVar[probes[p]] = true;       
    }

    /* check if all variables in the formula (input and output) have been assigned at least one probe */    
    var vSet = $.arrayIntersect(Object.keys(setVar),formulas[fid]['variables'])
    if (vSet.length != formulas[fid]['variables'].length){
        alert('Assign at least one probe to each variable in the selected formula among the following ones: '  + formulas[fid]['variables'].toString() );
        return false;
    }

    $('#confAnalysis').fadeOut({
        duration: "slow", 
        start: function(){
            // retrieve aggregation directives from user form
            for (var varName in aggrFunct) {
                if (aggrFunct[varName].use == true) {
                    aggrFunct[varName].mode = $('#aggrMode-' + varName).val();
                    if (aggrFunct[varName].mode == 'all') {
                        aggrFunct[varName].functIntra = $('#aggrFunct-intra-' + varName).val();
                        aggrFunct[varName].functInter = $('#aggrFunct-inter-' + varName).val();
                    } else {
                        aggrFunct[varName].functIntra = $('#aggrFunct-' + varName).val();
                    }
                }
            }

            // build var -> probe(s) map
            varMatch = {};
            for (p in probes){
                if (!varMatch.hasOwnProperty(probes[p])){
                    varMatch[probes[p]] = []
                }
                varMatch[probes[p]].push(p);
            }

            // initialize analysis matrix
            for (s in samples) {
                analysisMatrix[s] = {};
                for (p in samples[s]) {
                    analysisMatrix[s][p] = [];
                    for (var j = 0; j < samples[s][p].length; ++j) {
                        analysisMatrix[s][p].push( $.extend(true, {}, samples[s][p][j]) );
                    }
                }
            }

            // STEP I: intra-probe aggregation (if any)
            console.log("STEP I: start");
            for (s in analysisMatrix) {
                for (var varName in aggrFunct) {
                    if (aggrFunct[varName].use == true) {
                        var func = aggrFunct[varName].functIntra;
                        for (var j = 0; j < varMatch[varName].length; ++j) {
                            var p = varMatch[varName][j];
                            var values = analysisMatrix[s][p].map(function(el) {return el.value;});
                            var itm = {};
                            if (values.indexOf(null) == -1) {
                                itm.value = math.eval(func, {x: values});
                            } else {
                                itm.value = null;
                            }
                            itm.id = analysisMatrix[s][p].map(function(el) {return el.id;});
                            analysisMatrix[s][p] = [ itm ];
                        }
                    }
                }
            }
            console.log("STEP I: done");

            // STEP II: inter-probe aggregation (if any) within each variable
            console.log("STEP II: start");
            for (var varName in aggrFunct) {
                if (aggrFunct[varName].use == true && aggrFunct[varName].mode == 'all') {
                    var func = aggrFunct[varName].functInter;
                    var aggrP = varMatch[varName].join("_");
                    for (var s in analysisMatrix) {
                        var values = [];
                        var ids = [];
                        for (var j = 0; j < varMatch[varName].length; ++j) {
                            var p = varMatch[varName][j];
                            values.push ( analysisMatrix[s][p][0].value );
                            ids.push ( analysisMatrix[s][p][0].id )
                            delete analysisMatrix[s][p];
                        }
                        var itm = {};
                        if (values.indexOf(null) == -1) {
                            itm.value = math.eval(func, {x: values});
                        } else {
                            itm.value = null;
                        }
                        itm.id = ids;
                        analysisMatrix[s][aggrP] = [ itm ];
                    }
                    varMatch[varName] = [ aggrP ];
                }
            }
            console.log("STEP II: done");

            // STEP III: cartesian product between variables and formula computation
            console.log("STEP III: start");
            var scopeFormula = {};
            for (var v in varMatch) {
                scopeFormula[v] = null;
            }

            for (var i = 0; i < outputs.length; ++i) {
                var outVar = outputs[i];
                var varSpace = [ varMatch[outVar] ];
                var cnt = 0;
                var varOrder = {};
                varOrder[outVar] = cnt++;
                for (var v in varMatch) {
                    if (v != outVar) {
                        varSpace.push ( varMatch[v] );
                        varOrder[v] = cnt++;
                    }
                }
                var cartProdProbes = cartesian( varSpace );
                for (var j = 0; j < cartProdProbes.length; ++j) {
                    var aggrP = cartProdProbes[j][0] + "|" + cartProdProbes[j].slice(1).join("_");
                    for (var s in analysisMatrix) {
                        var cartProdVals = cartesian ( cartProdProbes[j].map(function(p) { return analysisMatrix[s][p].map(function(el) { return el.value; }); }) );
                        var cartProdIds = cartesian ( cartProdProbes[j].map(function(p) { return analysisMatrix[s][p].map(function(el) { return el.id; }); }) );
                        analysisMatrix[s][aggrP] = [];
                        for (var k = 0; k < cartProdVals.length; ++k) {
                            var itm = {};
                            var isNull = false;
                            itm.vars = {};
                            for (var v in scopeFormula) {
                                if (cartProdVals[k][varOrder[v]] != null) {
                                    scopeFormula[v] = cartProdVals[k][varOrder[v]];
                                } else {
                                    isNull = true;
                                    break;
                                }
                                itm.vars[v] = cartProdIds[k][varOrder[v]];
                            }
                            if (!isNull) {
                                itm.value = math.eval(formulas[fid]['expression'], scopeFormula);
                            } else {
                                itm.value = 'N/A';
                            }
                            analysisMatrix[s][aggrP].push(itm);
                        }
                    }
                }
            }
            // delete non-output probes from analysisMatrix
            for (var s in analysisMatrix) {
                for (var p in analysisMatrix[s]) {
                    if (p.indexOf('|') == -1) {
                        delete analysisMatrix[s][p]
                    }
                }
            }
            console.log("STEP III: done");
            
            // render the table with values
            // headers
            head = '<thead> <tr> <th>Genealogy ID</th>'
            for (var p in analysisMatrix[Object.keys(analysisMatrix)[0]]) {
                head += '<th>' + probesName[p.split('|')[0]]+ '</th>'
            }

            head +=' </tr></thead>'

            $('#tabAnalysis').children().remove();
            $('#tabAnalysis').append(head)

            body = '<tbody>'

            for (s in analysisMatrix){
                body += '<tr><td>' + s + '</td>'
                for (var p in analysisMatrix[s]) {
                    body += '<td> ' + analysisMatrix[s][p].map(function(el) { return el.value; }).join(" | ") + '</td>'
                }
                body += '</tr>'
            }

            body += '</tbody>'

            $('#tabAnalysis').append(body)

            $('#tabAnalysis').dataTable();

        },
        done: function(){
            $('#analysis').fadeIn();
        }
    });
    
    return true;
}

function backToConfAnalysis() {
    $('#analysis').hide();
    $('#confAnalysis').fadeIn({
        duration: 'slow'
    });
}

function updateInput(){
    $('#aliquots_list').val(JSON.stringify(analysisMatrix));
    $('#fid').val(fid);
    $('#probe-var-map').val(JSON.stringify(probes));
    $('#aggr-crit').val(JSON.stringify(aggrFunct));
    return true;
}

function initProbes (){
    $('.vProbes').on('change', function(){
        var tid = $(this).closest('tr').attr('tid');
        probes[tid] = this.value;
    });

    var listSelect  = $('.vProbes');
    for (var i=0; i<listSelect.length; i++){
        var tid = $(listSelect[i]).closest('tr').attr('tid');
        //probes[tid] = $(listSelect[i]).val();
        probesName[tid] = $(listSelect[i]).closest('tr').attr('tname');
    }
}

function initFormulas(){
    for (var fid in formulas){
        $('#formulas').append(  '<p>' + 
                                '<input id="formula-' + fid + '" type="radio" class="formula" name="formula" value="' + fid +'"/>' + 
                                '<label for="formula-' + fid + '">' + formulas[fid].description + ':&nbsp;&nbsp;' +
                                '$' + formulas[fid]['name'] + ' = ' + math.parse(formulas[fid]['expression']) + '$' + '</label></p>');
        formulas[fid].variables.sort();
    }
    $("input.formula").change(function() {
        updateVarsForCurrentFormula($(this).val());
    });
    $("input.formula").eq(0).prop("selected", true).trigger("change");
}

function updateVarsForCurrentFormula(fid) {
    // update variable association drop-down lists and aggregation selectors
    $("select.vProbes").children().remove();
    $("table#aggregate tbody").children().remove();
    var variables = formulas[fid].variables;
    for (var j = 0; j < variables.length; ++j) {
        var varName = formulas[fid].variables[j];
        $("select.vProbes").append('<option value="' + varName + '">' + varName + '</option>');
        appendAggregationSelector(varName);
    }
    $("select.vProbes").trigger("change");
    initAggregation(fid);
}

function initAggregation(fid) {
    aggrFunct = {};
    var f = formulas[fid];
    for (var j = 0; j < f.variables.length; ++j) {
        if (!aggrFunct.hasOwnProperty(f.variables[j])) {
            aggrFunct[f.variables[j]] = {'use': false, 'mode': null, 'functIntra': null, 'functInter': null} ;
        }
    }

}

function appendAggregationSelector(varName) {
    var fatherElem = $("table#aggregate");
    var tr = $("<tr></tr>");
    tr.append(  "<td><input type='checkbox' class='aggrFlag' name='aggrFlag-" + varName + "'>" + varName + "</td>" + 
                "<td>" +
                "<label>Mode:</label>" + 
                "<select id='aggrMode-" + varName +"' class='aggrMode' data-varname='" + varName + "' disabled='true'>" + 
                    "<option value='probe'>By probe</option>" +
                    "<option value='all'>Across all probes</option>" +
                "</select><br />" +
                "<div id='byprobe-" + varName + "' class='byProbe'>" + 
                    "<label>Function:</label>" +
                    "<select id='aggrFunct-" + varName +"' class='aggrFunct' data-varname='" + varName + "' disabled='true'>" + 
                    "<option value='mean(x)'>Mean</option>" +
                    "<option value='median(x)'>Median</option>" +
                    "</select>" +
                "</div>" + 
                "<div id='acrossProbes-" + varName + "' class='acrossProbes' style='display: none'>" +
                    "<label>Intra-probe function:</label>" +
                    "<select id='aggrFunct-intra-" + varName +"' class='aggrFunct intra' data-varname='" + varName + "' disabled='true'>" + 
                        "<option value='mean(x)'>Mean</option>" +
                        "<option value='median(x)'>Median</option>" +
                    "</select><br />" +
                    "<label>Inter-probe function:</label>" +
                    "<select id='aggrFunct-inter-" + varName +"' class='aggrFunct inter' data-varname='" + varName + "' disabled='true'>" + 
                        "<option value='mean(x)'>Mean</option>" +
                        "<option value='median(x)'>Median</option>" +
                    "</select>" +
                "</div>" +
                "</td>"
            );
    fatherElem.append(tr);
}

function cartesian(arg) {
    var r = [], max = arg.length-1;
    function helper(arr, i) {
        for (var j=0, l=arg[i].length; j<l; j++) {
            var a = arr.slice(0); // clone arr
            a.push(arg[i][j]);
            if (i==max) {
                r.push(a);
            } else
                helper(a, i+1);
        }
    }
    helper([], 0);
    return r;
}

/* old computeAnalysis function */
/*
function computeAnalysis(){

    var fid = $('input[name="formula"]:checked').val();
    var analysis_type = formulas[fid].analysis_type;
    $("#analysis_type option[value='" + analysis_type + "']").prop("selected", true);

    var outputs = formulas[fid].output;
    var flagOut = false
    var setVar = {}
    for (var p in probes){
        if (outputs.indexOf( probes[p] ) != -1 ){
            flagOut = true;
        } 
        setVar[probes[p]] = true;       
    }

    // check if all the variable for th formula (input and output are assigned at least one probe    
    var vSetted = $.arrayIntersect(Object.keys(setVar),formulas[fid]['variables'])
    if (vSetted.length != formulas[fid]['variables'].length){
        alert('Assign at least one probe to each variable of selected formula among the following ones: '  + formulas[fid]['variables'].toString() );
        return false;
    }

    if (!flagOut) {
        alert('Select at least one probe as output variable among the following ones: ' + outputs.toString());
        return false;
    }

    varMatch = {};
    scopeFormula = {}
    for (p in probes){
        if (!varMatch.hasOwnProperty(probes[p])){
            varMatch[probes[p]] = []
            scopeFormula[probes[p]] = null;
        }
        varMatch[probes[p]].push(p);
    }

    // fill in aggregated variables
    var secondLevelAggrVars = []
    for (var varName in aggrFunct) {
        if (aggrFunct[varName].use == true) {
            aggrFunct[varName].mode = $('#aggrMode-' + varName).val();
            if (aggrFunct[varName].mode == 'all') {
                secondLevelAggrVars.push(varName);
                aggrFunct[varName].functIntra = $('#aggrFunct-intra-' + varName).val();
                aggrFunct[varName].functInter = $('#aggrFunct-inter-' + varName).val();
            } else {
                aggrFunct[varName].funct = $('#aggrFunct-' + varName).val();
            }

        }
    }

    // prepare analysis matrix
    for (s in samples){
        analysisMatrix[s] = {};
        for (p in samples[s]){
            analysisMatrix[s][p] = [];
        }
    }

    // generate cartesian products between tests and references
    var cartArray = cartesian( Object.keys(varMatch).map(function(key){return varMatch[key]; }) );
    console.log(cartArray);

    refsForOutputVars = {};
    // stores the different reference combinations for each output variable
    // N.B. we assume there may be more than 1 output var (not normally the case)
    // 1) for each var, we get an array holding the different probe combinations
    // 2) each probe combination is made up of n-1 elements (where n is the total no. of variables)
    // 3) in case there are multiple output variables, the output variables different than the current one are treated as references
    // 4) when a variable is being aggregated across probes, all probes for that variable count as a single element

    for (var i = 0; i < formulas[fid]['output'].length; ++i) {
        var varName = formulas[fid]['output'][i];
        // varSpace holds the distinct possible values for each variable
        // as said earlier, aggregated probes count as a single value
        var varSpace = [];
        for (var otherVar in varMatch) {
            if (otherVar == varName)
                continue;
            if (aggrFunct[otherVar].use == true && aggrFunct[otherVar].mode == 'all') {
                varSpace.push([varMatch[otherVar]]);
            } else {
                varSpace.push(varMatch[otherVar]);
            }
        }
        refsForOutputVars[varName] = cartesian(varSpace);
    }

    $('#confAnalysis').fadeOut({
        duration: "slow", 
        start: function(){

            
            // compute the matrix

            for (s in samples){ // for each sample

                // initialize dictionary that will hold second-level aggregates
                // and compute first- and second-level aggregates for second-level aggregated variables
                var secondLevelAggregates = {}
                for (var j = 0; j < secondLevelAggrVars.length; ++j) {
                    var varName = secondLevelAggrVars[j];
                    secondLevelAggregates[varName] = [];
                    var probesForVar = varMatch[varName];
                    for (var k = 0; k < probesForVar.length; ++k) {
                        var values = samples[s][probesForVar[k]];
                        if (values.indexOf(null) == -1) {
                            secondLevelAggregates[varName].push( math.eval(aggrFunct[varName].functIntra, {x: values}) );
                        } else {
                            secondLevelAggregates[varName].push( null );
                        }
                    }
                    if (secondLevelAggregates[varName].indexOf(null) == -1) {
                        secondLevelAggregates[varName] = [ math.eval(aggrFunct[varName].functInter, {x: secondLevelAggregates[varName]}) ];
                    } else {
                        secondLevelAggregates[varName] = [ null ];
                    }
                }
                
                var usedCombinations = [];
                
                for (var c = 0; c<cartArray.length; c++){ // for each combination of variables
                    var cartMeas = []
                    var mapVar = {}
                    var varOut = null
                    var currentComb = [];
                    for (var i=0; i< cartArray[c].length; i++){
                        mapVar[i] = probes [ cartArray[c][i] ];
                        cartMeas.push( samples[s][ cartArray[c][i] ]  )
                        if (probes[cartArray[c][i]] == formulas[fid]['output'])
                            varOut = cartArray[c][i];

                        // enqueue current probe to build fingerprint of current combo, except if probe belongs to a cross-probe aggregated variable and it is not an output probe (if it is, the corresponding will be repeated, which is correct), in this case enqueue the variable name
                        currentComb.push( secondLevelAggrVars.indexOf(mapVar[i]) != -1 && mapVar[i] != probes[varOut] ? mapVar[i] : cartArray[c][i]);

                    }

                    // in case of cross-probe aggregation, different combinations correspond to the same result, so this is to avoid repeating it
                    var currentCombStr = currentComb.join('_');
                    if (usedCombinations.indexOf(currentCombStr) != -1) {
                        continue;
                    } else {
                        usedCombinations.push(currentCombStr);
                    }

                    console.log(cartMeas);
                    
                    var newCartMeas = [];

                    for (var iVals=0; iVals<cartMeas.length; iVals++){
                        var varName = mapVar[iVals];
                        // check if variable must be aggregated
                        if (aggrFunct[varName].use == true) {
                            // per-probe aggregation is done here
                            if (aggrFunct[varName].mode == 'probe') {
                                if (cartMeas[iVals].indexOf(null) == -1) {
                                    newCartMeas.push([math.eval(aggrFunct[varName].funct, {x: cartMeas[iVals]})]);
                                } else {
                                    newCartMeas.push([ null ]);
                                }
                            } else {
                            // otherwise 2nd-level aggregation has already been done, so just get the value already computed
                                newCartMeas.push(secondLevelAggregates[varName]);
                            }
                        } else {
                            newCartMeas.push(cartMeas[iVals]);
                        }
                    }
                    console.log(newCartMeas);

                    cartMeas = cartesian(newCartMeas);

                    for (var pair= 0; pair<cartMeas.length; pair++){
                        var flagAn = true;
                        for (var m= 0; m< cartMeas[pair].length; m++){
                            if (cartMeas[pair][m] == null){
                                flagAn = false
                            }
                            scopeFormula [ mapVar[m] ] = cartMeas[pair][m];
                        }

                        var res = null;
                        if (flagAn){
                            res = math.eval(formulas[fid]['expression'], scopeFormula);
                            res = res.toFixed(3);
                        }
                        else{
                            res = 'N/A';
                        }

                        analysisMatrix[s][varOut].push(res);
                        console.log("value:", res, "scope:", scopeFormula, "cartesian:", cartArray[c])
                    }
                }
            }

            
            // render the table with values
            head = '<thead> <tr> <th>Genealogy ID</th>'
            for (var p in probes){
                if (outputs.indexOf( probes[p] ) != -1 ){
                    head += '<th>' + probesName[p]+ '</th>'
                }
            }

            head +=' </tr></thead>'

            $('#tabAnalysis').children().remove();
            $('#tabAnalysis').append(head)

            body = '<tbody>'


            for (s in samples){
                body += '<tr><td>' + s + '</td>'
                for (var p in probes){
                    if (outputs.indexOf( probes[p] ) != -1 ){
                        body += '<td> ' + analysisMatrix[s][p].join(" | ") + '</td>'
                    }
                }
                body += '</tr>'
            }

            body += '</tbody>'

            $('#tabAnalysis').append(body)

            $('#tabAnalysis').dataTable();

        },
        done: function(){
            $('#analysis').fadeIn();
        }
    });
    
    return true;
}
*/