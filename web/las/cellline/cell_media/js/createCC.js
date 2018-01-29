var previous=""; var actual="";
elementsDict = {};
elementsDict['loaded'] = {};
elementsDict['selected'] = {};

function loadInfo(nameE){
    if (elementsDict['loaded'].hasOwnProperty(nameE)){
        //gia' caricato precedentemente dal server
        writeElements(elementsDict['loaded'][nameE], nameE);
    }else{
        //da caricare dal server
        console.log( base_url + '/api/getElements/' + nameE + '/');
        jQuery.ajax({
            async:false,

            url: base_url + '/api/getElements/' + nameE + '/',
                type: 'get',
                success: function(transport) {
                    var elements = JSON.parse(transport);
                    document.getElementById("central_div").style.visibility = 'visible';
                    elementsDict['loaded'][nameE] = elements;
                    //console.log(elementsDict);
                    writeElements(elements, nameE);
                }
        });
    }
}

//scrive gli elementi figli dell'elemento selezionato nella tabella centrale
//deve ricaricare mantenendo checckati gli elementi precedentemente selezionati
function writeElements(elements, nameE){
    previous = actual;
    actual = nameE;
    //jQuery("#up").attr('onclick', "loadInfo('"+previous+"')");//dovrebbe andare su di un livello, ma per ora si limita  a tornare indietro
    var rowCount = document.getElementById('center_table').rows.length;
    if (rowCount > 1) {
        $('#center_table tbody').empty();
    }
    for (var i=0; i < elements.length; i++){
        //console.log(elements[i]);
        //console.log(nameE);
        if (elements[i].hasChildren){
            //il nodo ha figli
            //console.log('children');
            var onclick = "onclick=loadInfo('" + elements[i].element['name'] + "');";
            var row = jQuery('<tr><td><div class="drag_no_smaller" '+onclick+'>'+ elements[i].element['name'] +'</div></td></tr>');
            row.appendTo('#center_table tbody');
        }else{
            //il nodo non ha figli
            for (key in elements[i]){
                if (elementsDict['selected'].hasOwnProperty(elements[i][key].element['name'])){
                    var row = jQuery('<tr><td><input type="checkbox" name="final_element" checked value='+ elements[i][key].element['name'] +'>'+ elements[i][key].element['name'] +'</td></tr>');
                }else{
                   var row = jQuery('<tr><td><input type="checkbox" name="final_element" value='+ elements[i][key].element['name'] +'>'+ elements[i][key].element['name'] +'</td></tr>');
               }
                row.appendTo('#center_table tbody');
                jQuery('#center_table tbody input[type="checkbox"]:last').click(function callSF(){showFeature(this);});
            }
        }
    }
}

function getFather(nameE){
    //console.log(nameE);
    for (element in elementsDict['loaded']){
        for (e in elementsDict['loaded'][element]){
            if (!elementsDict['loaded'][element][e].hasOwnProperty('element')){
                if (elementsDict['loaded'][element][e].hasOwnProperty(nameE)){
                    return [elementsDict['loaded'][element][e][nameE]['element']['condition_protocol_element_id'],e];
                }
            }
        }
    }
}

function showFeature(check){
    //if is checked
        //if it has feature 
            //open dialog
        //else
            //none
    //else
        //delete from the list of the selected elements
    //console.log(jQuery(check).val());
    var nameE = jQuery(check).val();
    var resultTemp = getFather(nameE); //recuperare il father dal dict per leggere le feature dell'elemento selezionato
    var father = resultTemp[0];
    var indexE = resultTemp[1];
    //console.log(father);
    //console.log(e);
    if (jQuery(check).is(':checked')){
        //l'utente ha appena checkato l'opzione
        //ogni elemente ha sempre almeno una feature, anche se non ha feature effettive. In tal caso, ha la feature virtuale 'No feature'
        //l'elemento cliccato ha delle feature da definire
        jQuery("#fList").empty();
        console.log(father);
        console.log(indexE);
        console.log(nameE);
        var featureList = elementsDict['loaded'][father][indexE][nameE]['feature'];
        console.log(featureList);
        var noFeature = false;
        for (var i=0; i < featureList.length; i++){
            var defValue = featureList[i]['featureInfo']['default_value'];
            var unityM = featureList[i]['featureInfo']['unity_measure'];
            var nameF = featureList[i]['featureInfo']['name'];
            var input = "";
            if (nameF == 'No feature'){
                noFeature = true;
                break;
            }
            //console.log(featureList[i]['defValue'].length);
            if (featureList[i]['defValue'].length == 0){
                //nessun valore particolare ammesso
                input = '<input type="number" name="'+nameF+'" value="'+defValue+'">';
            }else if (featureList[i]['defValue'].length >= 1){
                //uno  o piu' allowed_values
                var input = "<select id='"+nameF+"' name='"+nameF+"'>";
                for (var j=0; j < featureList[i]['defValue'].length; j++){
                    var aValue = featureList[i]['defValue'][j]['allowed_value'];
                    //console.log(aValue);
                    var temp = "<option value='"+ aValue +"' >"+ aValue +"</option>";
                    input += temp;
                }
                input += '</select>';
                
            }
            //console.log(input);
            var row = jQuery("<tr><td>" + nameF + "</td><td>" + input + "</td><td>[" + unityM + "]</td></tr>");
            row.appendTo("#fList");
        }
        jQuery("#fList").append(featureList);
        //var checkbox = this;
        //console.log(check);
        if (!noFeature){
            jQuery( "#dialog" ).dialog({
                resizable: false,
                height:300,
                width:340,
                modal: true,
                draggable :false,
                buttons: {
                    "Cancel": function() {
                            jQuery(check).attr('checked', false);
                            jQuery(this).dialog( "close" );
                    },
                    "Ok": function() {
                            var valueRows = jQuery("#fList tbody tr");
                            var tempValueList = [];
                            for (var i = 0; i < valueRows.length; i++){
                                var tds = jQuery(valueRows[i]).children();
                                tempValueList.push( jQuery(jQuery(tds[1]).children()[0]).val() );
                            }
                            for (var i = 0; i < tempValueList.length; i++){
                                if (tempValueList[i] == ""){
                                    alert("Insert all value!");
                                    return;
                                }
                            }
                            for (var i = 0; i < valueRows.length; i++){
                                var tds = jQuery(valueRows[i]).children();
                                var nameF = jQuery(tds[0]).text();
                                var value = jQuery(jQuery(tds[1]).children()[0]).val();
                                var unity = jQuery(tds[2]).text().substring(1, jQuery(tds[2]).text().length-1)
                                selectElement(nameE, nameF, value, unity);
                                //writeSelected(nameE, nameF, value, unity);
                            }
                            writeSelected(nameE);
                            jQuery(this).dialog( "close" );
                        }
                    }
            });
        }else{
            //alert('no feature for this element');
            //{u'nameF': u'No feature', u'unity': None, u'value': u'-'}
            selectElement(nameE, 'No feature', '-', '');
            writeSelected(nameE);
        }
    }else{
        //l'utente ha appena deselezionato l'opzione, bisogna eliminare l'elemento dalla lista degli elementi selezionati
        delete elementsDict['selected'][nameE];
        jQuery("#"+nameE+"_row").remove();
        if (jQuery("#selectedTable tbody").children().length == 0)
            jQuery("#selectedList").css('display','none');
    }
}

function writeSelected(nameE){
    //nuovo elemento da scrivere nel 'riassunto' a destra
    jQuery("#selectedList").css('display','block');
    var string = "<tr id='" + nameE+ "_row'><td><strong>"+nameE+"</strong></td><td><ul>";
    for (var i = 0; i < elementsDict['selected'][nameE].length; i++){
        var nameF = elementsDict['selected'][nameE][i]['nameF'];
        console.log(nameF);
        if (nameF != 'No feature'){
            var value = elementsDict['selected'][nameE][i]['value'];
            var unity = elementsDict['selected'][nameE][i]['unity'];
            string += "<li>" + nameF + ": " + value + " [" + unity + "]" + "</li>";
        }
    }
    string += "</ul></td></tr>";
    jQuery(string).appendTo("#selectedTable");
}

function selectElement(nameE, nameF, value, unity){
    if (!elementsDict['selected'].hasOwnProperty(nameE))
        elementsDict['selected'][nameE] = [];
    if (nameF != ""){
        var temp = {};
        temp['nameF'] = nameF;
        temp['value'] = value;
        temp['unity'] = unity;
        //temp['nameE'] = nameE;
        elementsDict['selected'][nameE].push(temp);
    }
}

function saveProtocol(){
    jQuery.ajax({
        url: base_url + '/protocol/culturing_conditions/',
        type: 'POST',
        data: {'elementsDict':JSON.stringify(elementsDict['selected'])},
        dataType: 'text',
    });
}