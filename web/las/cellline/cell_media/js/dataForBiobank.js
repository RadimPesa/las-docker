//manage the struct to send to biobank for the archive (like aliquots)

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function saveInLocal(typeA, oldG, pos, barcodeP, aliquots, newG, counter, tissueType, idEvent, volume, conta ){
	console.log(typeA, oldG, pos, barcodeP, aliquots, newG, counter);
    var index = 0;
    if (aliquots[typeA][oldG]){
        if (aliquots[typeA][oldG][barcodeP]){
            var found = false;
            for (var i = 0; i < aliquots[typeA][oldG][barcodeP].length; i++) {
                if (pos == aliquots[typeA][oldG][barcodeP][i]['pos']){
                    aliquots[typeA][oldG][barcodeP][i]['qty']++;
                    //aliquots[typeA][oldG][barcodeP][i]['list'].push(idOperation);
                    found = true;
                }
            }
            if (found == true){
                //storageIt('expl', JSON.stringify(aliquots));
                return aliquots;    
            }else{
                index = aliquots[typeA][oldG][barcodeP].length;
            }
        }else{
            aliquots[typeA][oldG][barcodeP] = [];
        }
    }else{
        aliquots[typeA][oldG] = {};
        aliquots[typeA][oldG][barcodeP] = [];
    }
    aliquots[typeA][oldG][barcodeP][index] = {}
    if((typeA=="FF")||(typeA=="OF")||(typeA=="CH")){
    	aliquots[typeA][oldG][barcodeP][index]['qty'] = 1;
    }
    else{
    	aliquots[typeA][oldG][barcodeP][index]['qty'] = '-';
    }
    aliquots[typeA][oldG][barcodeP][index]['genID'] = newG;
    aliquots[typeA][oldG][barcodeP][index]['pos'] = pos;
    aliquots[typeA][oldG][barcodeP][index]['tissueType'] = tissueType;
    aliquots[typeA][oldG][barcodeP][index]['counter'] = counter;
    aliquots[typeA][oldG][barcodeP][index]['idEvent'] = idEvent;
    aliquots[typeA][oldG][barcodeP][index]['volume'] = volume;
    aliquots[typeA][oldG][barcodeP][index]['conta'] = conta;
    aliquots[typeA][oldG][barcodeP][index]['furtherInfo'] = "-";
    
    //aliquots[typeA][oldG][barcodeP][index]['list'] = [];
    //aliquots[typeA][oldG][barcodeP][index]['list'].push(idOperation);
    //storageIt('expl', JSON.stringify(aliquots));
    return aliquots;    
}

/*function findSiblings(oldG, typeA){
    var list = [];
    for (genID in aliquots[typeA]) { 
        if (genID != oldG){ //non deve contare se stesso
            if (genID.substr(0, 17) == oldG.substr(0, 17) ){
                list.push(genID); 
            }
        }
    }
    return list;
}
*/

function countAliquots(aliquots, typeA, oldGenID, tissue, barcodeP, pos, idOperation){
    console.log('START');
    var counter = 0; var check = -1;
    listOldG = [oldGenID];
    if (Object.size(aliquots[typeA]) > 0){
        //var temp = findSiblings(oldGenID, typeA);
        //for (var i = 0; i < temp.length; i++) { listOldG.push(temp[i]); }
        for (var j = 0; j < listOldG.length; j++){
            var oldG = listOldG[j];
            if (Object.size(aliquots[typeA][oldG]) > 0){
                var check = checkForMissingCounter(aliquots, typeA, tissue, barcodeP, pos, listOldG, idOperation);
                for (key in aliquots[typeA][oldG]){
                    //key --> barcode piastra
                    for (var i = 0; i < aliquots[typeA][oldG][key].length; i++) {
                        if (key == barcodeP){
                            if (aliquots[typeA][oldG][key][i]['pos'] == pos){ 
                            	return aliquots[typeA][oldG][key][i]['counter']; 
                            }
                        }
                        if (tissue == aliquots[typeA][oldG][key][i]['tissueType']){ 
                        	counter++; console.log(counter);
                        }
                    }                
                }
            }   
        }
    }
    if ( check >= 0)
        return check;
    return counter;
}

function checkForMissingCounter(aliquots, typeA,  tissue, barcodeP, pos, listOldG, idOperation){
    var found = false;
    for (var i = 0; i < idOperation; i++) {
        found = false;
        for (var k = 0; k < listOldG.length; k++){
            var oldG = listOldG[k];
            for (key in aliquots[typeA][oldG]){
                for (var j = 0; j < aliquots[typeA][oldG][key].length; j++) {
                    if (parseInt(aliquots[typeA][oldG][key][j]['counter']) == i && aliquots[typeA][oldG][key][j]['tissueType'] == tissue){ found = true; }
                }
            }
        }
        if (found == false)
            return i;
    }
    return -1;
}


function deleteAliquot(genID, aliquots){
    var pos = "";  var liquid = false;
    for (typeA in aliquots){
        for (oldG in aliquots[typeA]){
            for (barcode in aliquots[typeA][oldG]){
                for (var i = 0; i < aliquots[typeA][oldG][barcode].length; i++){
                    if (aliquots[typeA][oldG][barcode][i]['genID'] == genID){
                        pos = aliquots[typeA][oldG][barcode][i]['pos'];
                        //if (aliquots[typeA][oldG][barcode][i]['qty'] == 1){
                            if((aliquots[typeA][oldG][barcode][i]['furtherInfo']) != "-"){ liquid = true; }
                            if (aliquots[typeA][oldG][barcode].length == 1){
                                if (Object.size(aliquots[typeA][oldG]) == 1){
                                    delete aliquots[typeA][oldG];
                                }else{
                                    delete aliquots[typeA][oldG][barcode];
                                }
                            }else{
                                aliquots[typeA][oldG][barcode].splice(i,1); 
                            }
                        //}else{
                        //    aliquots[typeA][oldG][barcode][i]['qty']--;
                        //}
                        //deleteInPlate(typeA, barcode, pos, genID, liquid);
                        //storageIt('expl', JSON.stringify(aliquots));
                        return [barcode, pos];
                    }
                }
            }
        }
    }
}

/*function deleteInPlate(typeA, barcode, pos, genID, liquid){
    //PL, PX, FR
    if (typeA == 'VT'){
        if (liquid == true){
            removeNotPlateBarcode(barcode);
            if (genID == jQuery("#pbmcoutput").text()){ jQuery("#pbmcoutput").text("Deleted"); }
            if (jQuery("#barcode_blood_plate").val() == barcode){ canc("tabella2 table:first button[id='v-" + pos+"']"); }
        }else{
            if (barcodeVT == barcode){ canc("tabs-1 table[id='vital'] button[id='v-"+pos+"']"); }
        }
    }else if (typeA == 'RL'){
        if (barcodeRL == barcode){ canc('r-' + pos); }    
    }else if (typeA == 'SF'){
        if (liquid == true){
            removeNotPlateBarcode(barcode);
            if (genID == jQuery("#whooutput").text()){ jQuery("#whooutput").text("Deleted"); }
            if (jQuery("#barcode_blood_plate").val() == barcode){ canc("tabella2 table:first button[id='s-" + pos+"']"); }
        }else{
            if (barcodeSF == barcode){ canc("tabs-1 table[id='sf'] button[id='s-"+pos+"']"); }
        }
    }else if (typeA == 'FF'){
        removeNotPlateBarcode(barcode);
        if (genID == jQuery("#f-output").text()) { jQuery("#f-output").text("Deleted"); }
    }else if (typeA == 'OF'){
        removeNotPlateBarcode(barcode);
        if (genID == jQuery("#o-output").text()) { jQuery("#o-output").text("Deleted"); }
    }else if (typeA == 'CH'){
        removeNotPlateBarcode(barcode);
        if (genID == jQuery("#c-output").text()) { jQuery("#c-output").text("Deleted"); }
    }else if (typeA == 'PL'){
        removeNotPlateBarcode(barcode);
        if (genID == jQuery("#plasoutput").text()) { jQuery("#plasoutput").text("Deleted"); }
        if (jQuery("#barcode_blood_plate").val() == barcode){ canc('l-' + pos); }
    }else if (typeA == 'PX'){
        removeNotPlateBarcode(barcode);
        if (genID == jQuery("#paxoutput").text()) { jQuery("#paxoutput").text("Deleted"); }
        if (jQuery("#barcode_blood_plate").val() == barcode){ canc('x-' + pos); }
    }else if (typeA == 'FR'){
        removeNotPlateBarcode(barcode);
        if (genID == jQuery("#urioutput").text()) { jQuery("#urioutput").text("Deleted"); }
        if (jQuery("#barcode_uri_plate").val() == barcode){ canc('f-' + pos); }
    }
}*/
