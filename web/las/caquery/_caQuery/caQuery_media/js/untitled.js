x -> union
y -> intersection
z -> difference
w -> group by count
u -> templates
v -> genid


        var current_terminals = [new WireIt.Terminal(current_block, {"name": "input", direction: [-1,0], offsetPosition: [-23,12], wireConfig:{color: "#EEEEEE", bordercolor:"#282828", width: 2}, "ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1}), new WireIt.Terminal(current_block, {"name": "output", direction: [1,0], offsetPosition: [117,12], wireConfig:{color: "#EEEEEE", bordercolor:"#282828", width: 2}, "ddConfig": {"type": "output","allowedTypes": ["input"]}, "nMaxWires": 1})];
        output_terminals[QueryGen.block_id]=current_terminals[1];
        input_terminals[QueryGen.block_id]=current_terminals[0];

function handleTerminals(terminal) {
    return function() {
        currBlockId = $(terminal.parentEl).attr("data-block_id");
        currBType = QueryGen.getGraphNode(currBlockId).output_type_id;
        connTerminal = terminal.getConnectedTerminals()[0];
        var connBlock=connTerminal.parentEl;
        if (connBlock!==undefined) {
            var connBlockId=$(connBlock).attr("data-block_id");
            if (currBType !== undefined) {
                if(connBlockId!="-1") { // "-1" is the "start" block
                    connBType = QueryGen.getGraphNode(connBlockId).output_type_id;
                    if (connBType !== undefined) {
                        alert("Please define the type of the input block first", "Warning");
                        connTerminal.removeWire(terminal.wires[0]);
                        terminal.removeWire(terminal.wires[0]);
                        return;
                    }
                    if (currBType === connBType)
                        ok = true;
                    else 
                        ok = GUI.isCompatible(currBType, connBType);
                    
                    // lascio perdere le annotazioni per il momento perché tanto non sono implementate
                    // cmq ricordare che Collection Annotations => si comporta come collection
                    // idem per mouse annotations e aliquot annotations
                    if (!ok) {
                        alert("You cannot have a connection between "+QueryGen.getButtonName(currBType)+" and "+QueryGen.getButtonName(connBType), "Entity Relationship");
                        //if(iter==0){
                        connTerminal.removeWire(terminal.wires[0]);
                        terminal.removeWire(terminal.wires[0]);
                        //}
                        //else{
                        //    connectedTerminals[0].eventAddWire.subscribe(function() {
                        //        connectedTerminals[0].removeWire(current_terminals[0].wires[0]);
                        //        current_terminals[0].removeWire(current_terminals[0].wires[0]);
                        //        iter=0;
                        //    });
                    }
                }
            } else {
                if (connBlockId!="-1") {
                    connBType = QueryGen.getGraphNode(connBlockId).output_type_id;
                    if (connBType !== undefined) { // "-1" is the "start" block
                        QueryGen.setGraphNodeAttr(currBlockId, "output_type_id", connBType);
                    } else {
                        alert("Please define the type of the input block first", "Warning");
                        connTerminal.removeWire(terminal.wires[0]);
                        terminal.removeWire(terminal.wires[0]);
                        return;
                    }
                } else {
                    alert("The "+QueryGen.getButtonName(currBType) + " block may not be directly connected to the start block!");
                    connTerminal.removeWire(terminal.wires[0]);
                    terminal.removeWire(terminal.wires[0]);
                }
            }
        }       
    }
}


//OLD HANDLER

current_terminals[0].eventAddWire.subscribe(function() {
        
            var connectedTerminals = [];
            connectedTerminals=current_terminals[0].getConnectedTerminals(); //puo' essere solo uno -> temp[0]
            var connectedBlock=connectedTerminals[0].parentEl;
            if(connectedBlock!=undefined){
                var connBLabel=$(connectedBlock).attr("id");
                if(connBLabel!="start"){
                    var connBName=$(connectedBlock).children("em#name").text();
                    if(connBName=="AND" || connBName=="OR" || connBName=="NOT IN" || connBName=="GROUP BY"){
                        connBName=$(connectedBlock).children("p.param").text();
                        if(connBName==""){
                            alert("please define the type of the input block first", "Warning");
                            connectedTerminals[0].removeWire(current_terminals[0].wires[0]);
                            current_terminals[0].removeWire(current_terminals[0].wires[0]);
                        }
                    }
                    if(connBName=="TEMPLATE"){
                        connBName=$(connectedTerminals[0].el).attr("title").split(" (");
                        connBName=connBName[0];
                    }
                    var currBId=$(current_terminals[0].parentEl).attr("data-b_id");
                    var connBId=$(connectedBlock).attr("data-b_id");
                    
                    var esiste = false;
                    if (currBId === connBId) {
                        esiste = true;
                    } else {
                        for (r in GUI.data.button_compatibility) {
                            if ((GUI.data.button_compatibility[r].id1 == currBId && GUI.data.button_compatibility[r].id2 == connBId) || (GUI.data.button_compatibility[r].id1 == connBId && GUI.data.button_compatibility[r].id2 == currBId)) {
                                esiste = true;
                                break;
                            }
                        }
                    }
                    // lascio perdere le annotazioni per il momento perché tanto non sono implementate
                    // cmq ricordare che Collection Annotations => si comporta come collection
                    // idem per mouse annotations e aliquot annotations
                    if (!esiste) {
                        currBName = $(current_terminals[0].parentEl).children("em#name").text();
                        alert("You cannot have a connection between "+connBName+" and "+currBName, "Entity Relationship");
                        if(iter==0){
                            connectedTerminals[0].removeWire(current_terminals[0].wires[0]);
                            current_terminals[0].removeWire(current_terminals[0].wires[0]);
                        }
                        else{
                            connectedTerminals[0].eventAddWire.subscribe(function() {
                                connectedTerminals[0].removeWire(current_terminals[0].wires[0]);
                                current_terminals[0].removeWire(current_terminals[0].wires[0]);
                                iter=0;
                            });
                        }
                    }
                }
            }       
            else
                iter++;
        });        
