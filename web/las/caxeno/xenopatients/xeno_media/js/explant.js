var table_name = 'table#aliquots_table'; var tessuti,  h, conta, load_rna, load_vital, load_snap, m;
h = 0; conta = 1; load_rna = false; load_snap = false; load_vital = false; notPlateBarcode = new Array();
barcodeVT = ""; barcodeSF = ""; barcodeRL = ""; barcodeBL = ""; barcodeURI = "";
var regex=/^[0-9.]+$/; var tissueDict,n,timer; var nMice = 0; var nNMice = 0; var nLMice = 0; notPlateBarcode = new Array(); explantsCounter = 0;
explants = {'VT':{}, 'RL':{}, 'SF':{}, 'FF':{}, 'CH':{}, 'OF':{}, 'PL':{}, 'PX':{}, 'FR':{}};

/**************************************************/
/**** CONFIGURAZIONE INIZIALE DELLA SCHERMATA *****/
/**************************************************/
jQuery(document).ready(function () {
    listKey = ['expl','expluser', 'expltimestamp', 'notPlateBarcode', 'tissueList', 'miceList', 'dateE', 'notesE', 'usedMice'];
    jQuery("#formPE input[type=text]").after('<br/><br/>');
    var listMice = jQuery("#formPE li")[1]
    jQuery(listMice).css('height','350px')
    jQuery(listMice).css('overflow','auto')
    url = base_url + "/api/tissue/";
    jQuery.ajax({
        url:url,
        async:false,
        method:'get',
        datatype:'json',
        success:function(d){ 
            tissueDict = JSON.parse(d); 
        }
    });
    tooltipForFirstPage();
    if (document.getElementById('barcode'))
        setPage();
    var temp = [];
    tessuti = jQuery(".s input[type='hidden']");
    for (var i = 0; i < tessuti.length; i++){ temp.push(jQuery(tessuti[i]).attr('value')); }
    localStorage.setItem('tissueList', temp.toString());
    var miceList = jQuery("#miceList input");
    var temp = [];
    for (var i = 0; i < miceList.length; i++){ temp.push(jQuery(miceList[i]).attr('id')); }
    localStorage.setItem('miceList', temp.toString());
    localStorage.setItem('dateE', jQuery("#date").text());
    localStorage.setItem('notesE', jQuery("#notes").text());
    /*ASSOCIA LE FUNZIONI AI VARI TASTI */    
    jQuery("#sf button,#rna button,#vital button").click(save);
    jQuery("#load_rna_plate,#load_sf_plate,#load_vital_plate").click(carica_piastra);
    jQuery("#o-0").click(save_oct); jQuery("#c-0").click(save_cb); jQuery("#f-0").click(save_ffpe); jQuery("#plas").click(save_plasma); 
    jQuery("#who").click(save_whole); jQuery("#pax").click(save_pax); jQuery("#pbmc").click(save_pbmc); jQuery("#uri").click(save_uri);
    jQuery("#barcplas").keypress(function(event){ if ( event.which == 13 ) { event.preventDefault(); save_plasma(); } });
    jQuery("#barcwho").keypress(function(event){ if ( event.which == 13 ) { event.preventDefault(); save_whole(); } });
    jQuery("#barcpax").keypress(function(event){ if ( event.which == 13 ) { event.preventDefault(); save_pax(); } });
    jQuery("#barcpbmc").keypress(function(event){ if ( event.which == 13 ) { event.preventDefault(); save_pbmc(); } });
    jQuery("#barcuri").keypress(function(event){ if ( event.which == 13 ) { event.preventDefault(); save_uri(); } });
    jQuery("#confirm_all").click(next_tissue);
    resetInput();
    generate_table();
    checkStorage(listKey, '');
    //per togliere l'intestazione alla tabella del secondo tab, quello per il sangue e anche alla terza
    jQuery("#tabella2 table tr:first,#tabella3 table tr:first").remove();
    //per cambiare l'id della tabella
    jQuery("#tabella2 table:first").attr("id","pias_blood");
    jQuery("#tabella3 table:first").attr("id","pias_uri");
});

//per resettare le caselle di input allo stato iniziale
function resetInput(){
    //per disabilitare tutti i pulsanti all'inizio
    jQuery("input").attr("disabled", true );
    jQuery("#startExpl input").attr("disabled", false );
    jQuery("#ffpe button").attr("disabled", true );
    jQuery("#oct button").attr("disabled", true );
    jQuery("#cb button").attr("disabled", true );
    jQuery("#sf button,#rna button,#vital button").attr("disabled", true );
    jQuery("#vital_confirm,#rna_confirm,#snap_confirm,#ffpe_confirm,#confirm_all").attr("disabled",true);
    jQuery("#load_vital_plate, #barcode_vital").attr("disabled", false);
    jQuery("#load_rna_plate, #barcode_rna").attr("disabled", false);
    jQuery("#load_sf_plate, #barcode_sf").attr("disabled", false);
    jQuery("#ok").attr("disabled", false );
    jQuery("#barcode").attr("disabled", false );
    jQuery("#initial input").attr("disabled", false );
    jQuery("input[type='radio']").attr("disabled", false );
}

function tooltipForFirstPage(){
    for (key in tissueDict){
        //jQuery(".t li input[value='" + key + "']").attr("title", capitaliseFirstLetter(tissueDict[key]));
        var id = jQuery(".t li input[value='" + key + "']").attr("id");
        jQuery("li label[for='" + id + "']").attr("title", capitaliseFirstLetter(tissueDict[key]));
    }
}

function setPage(){
	jQuery("#tabs").tabs();
    document.getElementById('barcode').focus();
    //per fare stare su due righe i campi con i tipi di tessuti
    jQuery(".t p > label[for='id_tissue_0']").after("<br>");
    //serve per eliminare le selezioni dei tessuti da asportare
    jQuery(".t input:checked").removeAttr("checked");    
    //serve per disabilitare il checkbox dei tessuti
    jQuery(".t input").attr("disabled","disabled");
    jQuery(".t input").hide();
    jQuery(".t label").hide();
    jQuery('label[for="id_tissue_0"]').first().show();
    var selectedTissue = 1;
    var id = jQuery("#tissue").val();
    if (document.hiddenTissuesForm.tissueH.length){
        selectedTissue = document.hiddenTissuesForm.tissueH.length;
        for (i = 0; i < selectedTissue; i++){
            for (var j = 0; j < document.tissueNameList.tissue.length; j++){
                console.log( document.tissueNameList.tissue[j].value,document.hiddenTissuesForm.tissueH[i].value )
                if( document.tissueNameList.tissue[j].value == document.hiddenTissuesForm.tissueH[i].value ){
                    jQuery("#tissueNameList input[value='" + document.tissueNameList.tissue[j].value + "']").show();
                    jQuery("#tissueNameList input[value='" + document.tissueNameList.tissue[j].value + "']").parent().show();
                }
            }
        }
    }else{
        var n = id[id.length - 1];
        jQuery("#tissueNameList input[value='" + id + "']").show();
        jQuery("#tissueNameList input[value='" + id + "']").parent().show();
    }
    //prendo il valore del campo hidden che contiene l'id del checkbox da abilitare
    //abilito quel checkbox
    jQuery("#tissueNameList input[value='" + id + "']").attr("checked","checked");
    //modifico lo stile del checkbox abilitato
    jQuery("#tissueNameList input[value='" + id + "']").parent().css("border-style","solid");
    //mi occupo del genealogy ID
    var tessuto = jQuery("#tissueNameList input[value='" + id + "']").parent().text();
    tessuto = tessuto[1] + tessuto[2] + tessuto[3];
    var tumore = jQuery("#tum").val();
    var caso = jQuery("#caso").val();
    jQuery("#gen_id").val(tumore + caso + tessuto);
}

function generate_table(){
    var oTable = jQuery(table_name).dataTable( {
	"bProcessing": true,
	 "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control center", 
               // "sDefaultContent": '<img src="' + base_url + '/xeno_media/img/admin/icon_deletelink.gif">'
               "sDefaultContent": '<img src="/xeno_media/img/admin/icon_deletelink.gif">'
            },
            { "sTitle": "ID Operation" },
            { "sTitle": "Barcode" },
            { "sTitle": "Position" },
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Further Info", 
                "bVisible":false,
                "sClass": "furth_info", 
            },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'desc']],
    "aoColumnDefs": [
        { "bSortable": false, "aTargets": [ 0 ] },
    ],
    });
   jQuery(table_name+' tbody td img').live('click', function () {
        var genID = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[4]).text();
        deleteAliquot(genID);
        var nTr = jQuery(this).parents('tr')[0];
	    jQuery(table_name).dataTable().fnDeleteRow( nTr );
    } );
}



/**************************************************/
/******** FUNZIOI DI SALVATAGGIO ALIQUOTE *********/
/**************************************************/

/**** SALVATAGGIO ALIQUOTE CON CLICK SU PULSANTI ****/

function saveInLocal(typeA, oldG, tissue, pos, barcodeP, explants, newG, counter, volume, conta, furtherInfo){
    var index = 0;
    if (explants[typeA][oldG]){
        if (explants[typeA][oldG][barcodeP]){
            var found = false;
            for (var i = 0; i < explants[typeA][oldG][barcodeP].length; i++) {
                if (pos == explants[typeA][oldG][barcodeP][i]['pos']){
                    explants[typeA][oldG][barcodeP][i]['qty']++;
                    explants[typeA][oldG][barcodeP][i]['list'].push(explantsCounter);
                    found = true;
                }
            }
            if (found == true){
                storageIt('expl', JSON.stringify(explants));
                return explants;    
            }else{
                index = explants[typeA][oldG][barcodeP].length;
            }
        }else{
            explants[typeA][oldG][barcodeP] = [];
        }
    }else{
        explants[typeA][oldG] = {};
        explants[typeA][oldG][barcodeP] = [];
    }
    explants[typeA][oldG][barcodeP][index] = {}
    explants[typeA][oldG][barcodeP][index]['qty'] = 1;
    explants[typeA][oldG][barcodeP][index]['genID'] = newG;
    explants[typeA][oldG][barcodeP][index]['pos'] = pos;
    explants[typeA][oldG][barcodeP][index]['tissueType'] = tissue;
    explants[typeA][oldG][barcodeP][index]['counter'] = counter;
    explants[typeA][oldG][barcodeP][index]['volume'] = volume;
    explants[typeA][oldG][barcodeP][index]['conta'] = conta;
    explants[typeA][oldG][barcodeP][index]['furtherInfo'] = furtherInfo;
    explants[typeA][oldG][barcodeP][index]['list'] = [];
    explants[typeA][oldG][barcodeP][index]['list'].push(explantsCounter);
    storageIt('expl', JSON.stringify(explants));
    return explants;    
}

function addAliquot(typeA, oldG, tissue, barcodeT, explants, pos){
    var volume = "-"; var conta = "-"; var furtherInfo = ""; var id = "";
    if (typeA == 'FF'){
        id = '#f-output';
        jQuery("#inputf0").val("");
    }else if (typeA == 'CH'){
        id = '#c-output';
        jQuery("#inputc0").val("");
    }else if (typeA == 'OF'){
        id = '#o-output';
        jQuery("#inputo0").val("");
    }else if (typeA == 'PL'){
        id = '#plasoutput';
        volume=jQuery("#volplas").val();
        jQuery("#barcplas").val("");
    }else if (typeA == 'SF'){
        id = '#whooutput';
        volume=jQuery("#volwho").val();
        jQuery("#barcwho").val("");
    }else if (typeA == 'PX'){
        id = '#paxoutput';
        volume=jQuery("#volpax").val();
        jQuery("#barcpax").val("");
    }else if (typeA == 'VT'){
        id = '#pbmcoutput';
        volume=jQuery("#volpbmc").val();
        conta=jQuery("#contapbmc").val();
        jQuery("#barcpbmc").val("");
    }else if (typeA == 'FR'){
        id = '#urioutput';
        volume=jQuery("#voluri").val();
        jQuery("#barcuri").val("");
    }
    var counter = countExplants(explants, typeA, oldG, tissue, barcodeT, pos);
    var url = base_url + '/api.newGenIDExplant/' + oldG + '/' + tissue + '/' + typeA + '/' + counter;
    console.log(url);
    startLag();
    jQuery.ajax({
        type: 'get',
        async: false,
        url: url,
        success: function(transport) {
            notPlateBarcode.push(barcodeT);
            localStorage.setItem('notPlateBarcode', notPlateBarcode.toString());
            if ( (typeA=="PL") || (typeA=="PX") || (typeA=="VT") || (typeA=="SF") || (typeA=="FR") ){
                jQuery(table_name).dataTable().fnSetColumnVis( 5, true );
                furtherInfo = "Volume: " + volume.toString() + "ml";
                if (conta != "-")
                    furtherInfo = furtherInfo + " Count: " + conta + "cell/ml";
            }
            else
                furtherInfo = '-';
            jQuery(table_name).dataTable().fnAddData( [null, explantsCounter, barcodeT, pos, transport, furtherInfo] );
            //salvo nella struttura dati locale e lo salvo anche nel local_storage
            explants = saveInLocal(typeA, oldG, tissue, pos, barcodeT, explants, transport, counter, volume, conta, furtherInfo);
            explantsCounter++;
            //"#tissueNameList input[value='" + id + "']"
            var id_inp = jQuery(tessuti[h]).attr("value");
            console.log(jQuery("#tissueNameList input[value='" + id_inp + "']"));
            var color = jQuery("#tissueNameList input[value='" + id_inp + "']").parent().css("color");
            //USARE IL COLORE PER LA SCRITTA DEL NUOVO GENID
            jQuery(id).text(transport);
            jQuery(id).css('color', color);
            endLag();
        }
    });
}

//funzione associata ai tasti/celle delle piastre vital, rna e snap
function save() {
    var tipo, code, posizione;
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        if ( (barcodeRL == "") && ((jQuery(this).attr("id")).charAt(0))=="r" )
            alert("Insert the plate barcode in rna later");
        else if((barcodeSF == "") && ((jQuery(this).attr("id")).charAt(0))=="s" )
            alert("Insert the plate barcode in snap frozen");
        else if( (barcodeVT == "") && ((jQuery(this).attr("id")).charAt(0))=="v" )
            alert("Insert the plate barcode in vital");
        else{
            var barcodeP = "";
            var oldG = jQuery("#genID").text();
            if (jQuery(this).attr("id").charAt(0)=="r" ){
                typeA = 'RL';
                barcodeP = barcodeRL;
            }else if (jQuery(this).attr("id").charAt(0)=="s"){
                typeA = 'SF';
                barcodeP = barcodeSF;
            }else if (jQuery(this).attr("id").charAt(0)=="v"){
                typeA = 'VT';
                barcodeP = barcodeVT;
            }
            var id = jQuery(tessuti[h]).attr("value");
            var tissue = jQuery.trim( jQuery("#tissueNameList input[value='" + id + "']").parent().text() );
            var pos = jQuery(this).attr("id").split("-")[1];
            var counter = countExplants(explants, typeA, oldG, tissue, barcodeP, pos);
            var url = base_url + '/api.newGenIDExplant/' + oldG + '/' + tissue + '/' + typeA + '/' + counter;
            var button = this;
            startLag();
            jQuery.ajax({
                type: 'get',
                async: false,
                url: url,
                success: function(transport) {
                    //per identificare i tasti selezionati
                    jQuery(button).attr("sel","s_new");
                    jQuery(button).attr("title", transport);
                    //salvo il valore attuale del pulsante, lo incremento e lo aggiorno
                    var num = parseInt(jQuery(button).text());
                    jQuery(button).text(num + 1);
                    //prendo l'id del tissue selezionato, per colorare correttamnente la nuova aliquota
                    var id_inp = jQuery(tessuti[h]).attr("value");
                    var colore = jQuery("#tissueNameList input[value='" + id_inp + "']").parent().css("color");
                    jQuery(button).css("background-color",colore);
                    //posizione, barcode e idGen per la tabella riassuntiva
                    jQuery(table_name).dataTable().fnAddData( [null, explantsCounter, barcodeP, pos, transport, '-' ] );
                    //salvo nella struttura dati locale e lo salvo anche nel local_storage
                    explants = saveInLocal(typeA, oldG, tissue, pos, barcodeP, explants, transport, counter, '-', '-', '-');
                    explantsCounter++;
                    endLag();
                }
            });
        }
    }else
        alert("First, you must select a mouse.");
}

function saveT(tipo, inputid){
    if ( (jQuery(inputid).val() == "")  || (jQuery(inputid).val().indexOf(' ') > -1) ){
        alert("Insert/check the barcode");
    }else{
        var barcodeT = jQuery(inputid).val();
        var url = base_url + "/explants/checkBarcodeT";
        var obj = jQuery(this);
        var radio = jQuery('input:radio[name="cho_'+tipo+'"]:checked').val();
        if ( (radio == "tube") || (radio == undefined) ){
            if (checkNotPlateBarcode(barcodeT) == false){
                jQuery.ajax({
                    type: 'POST',
                    url: url,
                    data: {'barcodeT':barcodeT},
                    dataType: "json",
                    success: function(response) {
                        console.log(response);
                        if(response.data == "err_esistente"){
                            alert("Error. Barcode you entered already exists");
                        }else if((response.data == "err_tipo")||(response.data == "errore_aliq")){
                           alert("Error. Block isn't for "+tipo);
                        }else{
                            if (response.message == '403'){
                                window.location.href = "/forbidden";
                                return;
                            }else{
                                var oldG = jQuery("#genID").text();
                                var id_inp = jQuery(tessuti[h]).attr("value");
                                var tissue = jQuery.trim( jQuery("#tissueNameList input[value='" + id_inp + "']").parent().text() );
                                addAliquot(tipo, oldG, tissue, barcodeT, explants, '-');
                            }                    
                        }
                    },
                });
            }else{
                alert("You have already used this barcode.");
            }
        }else if (radio == "plate"){
            carica_piastra_sangue(barcodeT,tipo);
        }
    }
}

//funzione associata ai singoli tasti di salvataggio ffpe
function save_ffpe() {
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        var inputid = "#inputf0";
        saveT('FF', inputid);
    }else
        alert("First, you must select a mouse.");
}

//funzione associata ai singoli tasti di salvataggio oct
function save_oct() {
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        var inputid = "#inputo0";
        saveT('OF', inputid);
    }else
        alert("First, you must select a mouse.");
}

//funzione associata ai singoli tasti di salvataggio cb
function save_cb() {
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        var inputid = "#inputc"+(jQuery(this).attr("id")).charAt(2);
        saveT('CH', inputid);
    }else
        alert("First, you must select a mouse.");
}

function salva_sangue() {
    var tipo,code; var volume = ""; var conta = "";
    if((jQuery(this).attr("id").charAt(0)) == "v"){
        tipo = "VT";
        code = barcodeBL;
        volume = jQuery("#volpbmc").val();
        conta = jQuery("#contapbmc").val();
    }else if((jQuery(this).attr("id").charAt(0)) == "s"){
        tipo="SF";
        code = barcodeBL;
        volume = jQuery("#volwho").val();
    }else if((jQuery(this).attr("id").charAt(0)) == "l"){
        tipo = "PL";
        code = barcodeBL;
        volume = jQuery("#volplas").val();
    }else if((jQuery(this).attr("id").charAt(0)) == "x"){
        tipo = "PX";
        code = barcodeBL;
        volume = jQuery("#volpax").val();
    }else if((jQuery(this).attr("id").charAt(0)) == "f"){
        tipo = "FR";
        code = barcodeURI;
        volume = jQuery("#voluri").val();
    }
    if((!regex.test(volume))||((!regex.test(conta))&&(conta!=""))){
        alert("You can only insert number. Please correct.");
    }else{
        //per identificare i tasti selezionati
        jQuery(this).attr("sel","s");
        //scrivo il nuovo numero nel pulsante
        jQuery(this).text("1");
        //prendo l'id del tessuto selezionato
        var id_inp = jQuery(tessuti[h]).attr("value");
        //prendo il colore della label(che e' il padre del check selezionato)
        var colore = jQuery("#tissueNameList input[value='" + id_inp + "']").parent().css("color");
        //cambio il colore del tasto
        jQuery(this).css("background-color",colore);
        var posto = jQuery(this).attr("id");
        //lo disabilito perche' non si possa mettere piu' niente li' dentro
        jQuery(this).attr("disabled",true);
        var pos = jQuery(this).attr("id").split("-")[1];
        var tissue = jQuery.trim( jQuery("#tissueNameList input[value='" + id_inp + "']").parent().text() );
        console.log(tissue);
        var oldG = jQuery("#genID").text();
        var counter = countExplants(explants, tipo, oldG, tissue, code, pos);
        if (parseInt(counter) < 10)
            var countgen = "0" + String(counter);
        else
            countgen = counter;
        addAliquot(tipo, oldG, tissue, code, explants, pos)
        var oTable = jQuery(table_name).dataTable();
        oTable.fnSetColumnVis( 5, true );
    }
}

function saveLiquidNoCount(inputid, volid, type){
    if(jQuery(inputid).val() == "")
        alert("Insert barcode");
    else{
        if(jQuery(volid).val() == ""){
            alert("Insert volume");
        }else{
            if (type != 'VT'){
                var numero = jQuery(volid).val();
                if( (!regex.test(numero)) ){
                    alert("You can only insert number. Please correct volume");
                }else{
                    //devo vedere se e' stato scelto di caricare una piastra o una provetta
                    var radio = jQuery('input:radio[name="cho_' + type + '"]:checked');
                    if (radio.length == 0)
                        alert("Choose if you want to load a tube or a plate");
                    else
                        saveT(type, inputid);
                }
            }else{
                if(jQuery("#contapbmc").val() == ""){
                    alert("Insert count");
                }else{
                    var vol = jQuery("#volpbmc").val();
                    var conta = jQuery("#contapbmc").val();
                    if( (!regex.test(vol)) || (!regex.test(conta)) ){
                        alert("You can only insert number. Please correct.");
                    }else{
                        //devo vedere se e' stato scelto di caricare una piastra o una provetta
                        var radio = jQuery('input:radio[name="cho_VT"]:checked');
                        if (radio.length == 0){
                            alert("Choose if you want to load a tube or a plate");
                        }else{
                            saveT('VT', inputid);
                        }
                    }
                }
            }
        }
    }
}
function save_plasma() { saveLiquidNoCount("#barcplas", "#volplas", 'PL'); }
function save_whole() { saveLiquidNoCount("#barcwho", "#volwho", 'SF'); }
function save_pax() { saveLiquidNoCount("#barcpax", "#volpax", 'PX'); }
function save_uri() { saveLiquidNoCount("#barcuri", "#voluri", 'FR'); }
function save_pbmc() { saveLiquidNoCount("#barcpbmc", "#volpbmc", 'VT'); }

/**** SALVATAGGIO ALIQUOTE CON IL TASTO INVIO ****/
/**** solo per ffpe, oct, cb ****/
//funzione associata alla pressione del tasto invio all'interno dei campi del barcode per salvare ffpe
function save_ffpe_from_key(id) {
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        var inputid = "#inputf0";
        saveT('FF', inputid);
    }else
        alert("First, you must select a mouse.");
}

//funzione associata alla pressione del tasto invio all'interno dei campi del barcode per salvare oct
function save_oct_from_key(id) {
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        var inputid = "#inputo0";
        saveT('OF', inputid);
    }else
        alert("First, you must select a mouse.");
}

//funzione associata alla pressione del tasto invio all'interno dei campi del barcode per salvare cb
function save_cb_from_key(id) {
    //consente questa operazione solo se c'e' un topo precedentemente selezionato tramite il campo di inserimento del barcode
    if (document.getElementById('genID').innerHTML){
        var inputid = "#inputc0";
        saveT('CH', inputid);
    }else
        alert("First, you must select a mouse.");
}

/**************************************************/
/****** GESTIONE LOGICA BARCODE E CONTATORI *******/
/**************************************************/
function checkNotPlateBarcode(barcode){
    for (var i=0; i < notPlateBarcode.length; i++){ if (notPlateBarcode[i] == barcode){ return true; } }
    return false;
}

function removeNotPlateBarcode(barcode){
    for (var i=0; i < notPlateBarcode.length; i++){ if (notPlateBarcode[i] == barcode){ notPlateBarcode.splice(i,1) } }
    localStorage.setItem('notPlateBarcode', notPlateBarcode.toString());
}

function checkForMissingCounter(explants, typeA,  tissue, barcodeP, pos, listOldG){
    var found = false;
    for (var i = 0; i < explantsCounter; i++) {
        found = false;
        for (var k = 0; k < listOldG.length; k++){
            var oldG = listOldG[k];
            for (key in explants[typeA][oldG]){
                for (var j = 0; j < explants[typeA][oldG][key].length; j++) {
                    if (parseInt(explants[typeA][oldG][key][j]['counter']) == i && explants[typeA][oldG][key][j]['tissueType'] == tissue){ found = true; }
                }
            }
        }
        if (found == false)
            return i;
    }
    return -1;
}

function findSiblings(oldG, typeA){
    var list = [];
    for (genID in explants[typeA]) { 
        if (genID != oldG){ //non deve contare se stesso
            if (genID.substr(0, 17) == oldG.substr(0, 17) ){
                list.push(genID); 
            }
        }
    }
    return list;
}

function countExplants(explants, typeA, oldGenID, tissue, barcodeP, pos){
    console.log('START');
    var counter = 0; var check = -1;
    listOldG = [oldGenID];
    if (Object.size(explants[typeA]) > 0){
        var temp = findSiblings(oldGenID, typeA);
        for (var i = 0; i < temp.length; i++) { listOldG.push(temp[i]); }
        for (var j = 0; j < listOldG.length; j++){
            var oldG = listOldG[j];
            if (Object.size(explants[typeA][oldG]) > 0){
                var check = checkForMissingCounter(explants, typeA, tissue, barcodeP, pos, listOldG);
                for (key in explants[typeA][oldG]){
                    //key --> barcode piastra
                    for (var i = 0; i < explants[typeA][oldG][key].length; i++) {
                        if (key == barcodeP){
                            if (explants[typeA][oldG][key][i]['pos'] == pos){ return explants[typeA][oldG][key][i]['counter']; }
                        }
                        if (tissue == explants[typeA][oldG][key][i]['tissueType']){ counter++; console.log(counter);}
                    }                
                }
            }   
        }
    }
    if ( check >= 0)
        return check;
    return counter;
}

function startLag(){
    jQuery("#sf button,#rna button,#vital button,#ffpe button,#oct button,#cb button").attr("disabled", true );
    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s']").attr("disabled", true );
    jQuery("#confirm_all").attr("disabled", true );
    jQuery("#nextMouse").attr("disabled", true );
    timer = setTimeout(function(){jQuery("body").addClass("loading");}, 2000);    
}

function endLag(){
    clearTimeout(timer);
    jQuery("#sf button,#rna button,#vital button,#ffpe button,#oct button,#cb button").attr("disabled", false );
    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s'],#ffpe button[sel='s'],#oct button[sel='s'],#cb button[sel='s']").attr("disabled", true );
    jQuery("#rna button:contains('X'),#sf button:contains('X')").attr("disabled", true );
    jQuery("#confirm_all").attr("disabled", false );
    jQuery("#nextMouse").attr("disabled", false );
    jQuery("body").removeClass("loading");
}

function checkKey(evt){ //per selezionare un topo con il tasto invio
    var charCode = (evt.which) ? evt.which : event.keyCode;
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        insertMouse();
}

function checkKeyForLoadP(evt){ //per caricare una piastra con il tasto invio
    var charCode = (evt.which) ? evt.which : event.keyCode;
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        carica_piastra_from_key((evt.target.getAttribute('id')));
}

function checkKeyForNoP(evt){ //per mettere un'aliquota dove non si hanno piastre con invio
    var charCode = (evt.which) ? evt.which : event.keyCode;
    if ( charCode == 13 ){ //codice ASCII del carattere carriage return (invio)
        if (evt.target.getAttribute('id').charAt(5) == 'f')
            save_ffpe_from_key(evt.target.getAttribute('id'));
        if (evt.target.getAttribute('id').charAt(5) == 'o')
            save_oct_from_key(evt.target.getAttribute('id'));
        if (evt.target.getAttribute('id').charAt(5) == 'c')
            save_cb_from_key(evt.target.getAttribute('id'));
        }
}


/**************************************************/
/********** GESTIONE CARICAMENTO PIASTRE **********/
/**************************************************/
function carica_piastra_sangue(codice,tipo){
    var timer = setTimeout(function(){jQuery("body").addClass("loading");},2000);
    //sto caricando una piastra per le urine
    if (tipo == "FR"){ var nameP = "tabella3 table:first"; }else{ var nameP = "tabella2 table:first"; }
    jQuery("#" + nameP + " button,#confirm_all").attr("disabled", false );
    var nom = "cho_" + tipo;
    var radio = jQuery('input:radio[name="'+nom+'"]:checked').val();
    var barr = codice.replace(/#/g,"%23");
    var url = base_url + "/api.explTable/" + barr + "/" + tipo + "/" + radio;
    jQuery.getJSON(url,function(d){
        if (d.data == "errore"){
            alert("Plate doesn't exist");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if (d.data == "errore_piastra"){
            alert("Plate aim is not working");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if (d.data == "errore_aliq"){
            var val = jQuery("#" + nameP + " th").text().toLowerCase();
            alert("Plate selected is not " + val + " ");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if (d.data == "errore_store"){
            alert("Error while connecting with storage");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if (d.data == "err_tipo"){
            alert("Error. Block isn't for "+typeP);
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if (d.data == "err_esistente"){
            alert("Error. Barcode you entered already exists");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else{
            jQuery("#" + nameP ).replaceWith(d.data);
            if(tipo == "FR"){
                //faccio apparire il barcode nel campo sotto la piastra per le urine
                jQuery("#barcode_uri_plate").val(codice);
                barcodeURI = codice;
            }else{
               //faccio apparire il barcode nel campo sotto la piastra per il sangue
                jQuery("#barcode_blood_plate").val(codice);
                barcodeBL = codice;
            }
            jQuery("#" + nameP + " button").css("background-color","rgb(249,248,242)");
            jQuery("#" + nameP + " button").click(salva_sangue);
            //mi occupo dei posti gia' selezionati in precedenza, nel caso questo sia un 
            //ricaricamento della stessa piastra
            var nome = tipo[0].toLowerCase();
            if (tipo == "PL"){ nome = 'l'; }else if(tipo == "PX"){ nome = "x"; }else if(tipo == "FR"){ nome = "f"; }
            //piastra_ricaricata(tipo,nome,codice,sangue);
            loadPreviousChange(tipo, nome, codice, true); //params typeP, nameP, barcodeP, sangue
            /*VT vital 01 */
            }
        clearTimeout(timer);
        jQuery("body").removeClass("loading");
    });
    jQuery("body").removeClass("loading");
}

/**** CARICAMENTO PIASTRA DA BIOBANCA PER SNAP, VITAL, RNA ****/
function loadPlate(clickedID){
    if ( (clickedID == "load_rna_plate") || (clickedID == "barcode_rna") ){
        if ( (jQuery("#barcode_rna").val() == "")  || (jQuery("#barcode_rna").val().indexOf(' ') > -1) )
            alert("Insert/check the plate barcode in rna later");
        else{
            var radio = jQuery('input:radio[name="choose_rna"]:checked');
            if (radio.length==0){
                alert("Choose if you want to load a tube or a plate");
                return;
            }else{
                insertTubes('RL', 'rna', jQuery("input[name='choose_rna']:checked").val());
                barcodeRL = jQuery("#barcode_rna").val();
            }
        }
    }else if ( (clickedID == "load_sf_plate") || (clickedID == "barcode_sf") ){
        
        if ( (jQuery("#barcode_sf").val() == "")  || (jQuery("#barcode_sf").val().indexOf(' ') > -1) )
            alert("Insert/check the plate barcode in snap frozen");
        else{
            var radio = jQuery('input:radio[name="choose_sf"]:checked');
            if (radio.length==0){
                alert("Choose if you want to load a tube or a plate");
                return;
            }else{
                insertTubes('SF', 'sf', jQuery("input[name='choose_sf']:checked").val());
                barcodeSF = jQuery("#barcode_sf").val();
            }
        }
    }else if ( (clickedID == "load_vital_plate") || (clickedID == "barcode_vital") ){
        if ( (jQuery("#barcode_vital").val() == "")  || (jQuery("#barcode_vital").val().indexOf(' ') > -1) )
            alert("Insert/check the plate barcode in vital");
        else{
            var radio = jQuery('input:radio[name="choose_vital"]:checked');
            if (radio.length==0){
                alert("Choose if you want to load a tube or a plate");
                return;
            }else{
                insertTubes('VT', 'vital', jQuery("input[name='choose_vital']:checked").val());
                barcodeVT = jQuery("#barcode_vital").val();
            }
        }
    }
}

//per caricare una piastra, dopo averne immesso il barcode
function carica_piastra(){ loadPlate(jQuery(this).attr("id")); }
//per caricare una piastra premendo invio, non con il bottone
function carica_piastra_from_key(id){ loadPlate(id); }

//funzione utilizzata per parametrizzare l'inserimento delle varie provette nella rispettiva piastra
function insertTubes(typeP, nameP, typeC){
    jQuery("#" + nameP + "button,#confirm_all").attr("disabled", false );
    jQuery("#" + nameP + '_confirm').attr("loaded", '1' );
    barcode = jQuery("#barcode_" + nameP).val();
    var url = base_url + "/api.explTable/" + barcode + "/" + typeP + "/" + typeC;
    startLag();
    jQuery.getJSON(url, function(transport){
        if(transport.data=="errore") {
            alert("The plate doesn't exist");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if(transport.data=="errore_piastra") {
            alert("Plate aim is not working");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if(transport.data == "errore_aliq") {
            var val = jQuery("#" + nameP + " th").text().toLowerCase();
            alert("Plate selected is not "+val+" ");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if(transport.data=="errore_store") {
            alert("Error while connecting with storage");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if(transport.data=="err_tipo"){
            alert("Error. Block isn't for "+typeP);
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else if(transport.data=="err_esistente"){
            alert("Error. Barcode you entered already exists");
            jQuery("#" + nameP + " button,#confirm_all").attr("disabled", true );
        }else{
            jQuery("#" + nameP ).replaceWith(transport.data);
            jQuery("#" + nameP + " button").css("background-color","rgb(249,248,242)");
            jQuery("#" + nameP + " button").click(save);
            jQuery("#load_" + nameP + "_plate").attr("load", "1");
            if (nameP == "sf")
                jQuery("#snap_confirm").attr("disabled",false);
            else
                jQuery("#" + nameP + "_confirm").attr("disabled",false);
        }
        loadPreviousChange(typeP, nameP, barcode, false);
        endLag();
    });
}

//carica le eventuali modifiche fatte in questa sessione alla piastra che si sta caricando
function loadPreviousChange(typeP, nameP, barcodeP, sangue){
    for (mouse in explants[typeP]){
        for (barcode in explants[typeP][mouse]){
            if (barcode == barcodeP){
                for (var i = 0; i < explants[typeP][mouse][barcode].length; i++){
                    var pos = explants[typeP][mouse][barcode][i]['pos'];
                    var qty = explants[typeP][mouse][barcode][i]['qty'];
                    var tissue = explants[typeP][mouse][barcode][i]['tissueType'];
                    var genID = explants[typeP][mouse][barcode][i]['genID'];
                    //devo vedere se e' un'aliquota del sangue o no
                    if(sangue){
                        if (typeP=="FR"){
                            var id_tube = "#tabella3 table:first button[id='"+nameP[0]+"-"+pos+"']";
                        }else{
                            var id_tube = "#tabella2 table:first button[id='"+nameP[0]+"-"+pos+"']";
                        }   
                    }else{
                        var id_tube = "#" + nameP[0] + "-" + pos;
                    }
                    jQuery(id_tube).text(qty);
                    jQuery(id_tube).attr('sel', 's');
                    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s'],#plasma button[sel='s'],#pias_uri button[sel='s']").attr("disabled", true );
                    jQuery(id_tube).attr('title', genID);
                    for (var j = 0; j < jQuery("#tissueNameList ul label").length; j++){
                        var label = jQuery("#tissueNameList ul label")[j];
                        if ( jQuery.trim( jQuery(label).text() ) == tissue ){
                            var color = jQuery(label).css("color");
                            jQuery(id_tube).css("background-color",color);
                        }
                    }
                }
            }
        }
    }    
}

/**************************************************/
/******** CANCELLZIONE ESPIANTI / ALIQUOTE ********/
/**************************************************/
//per cancellare gli espianti programmati selezionati
function deleteExplants(){
    var selected = jQuery("#formPE input[type='checkbox']:checked"); var miceList = "";
    for (var i=0; i < selected.length; i++){
        if (miceList == "")
            miceList = selected[i].value;
        else
            miceList += ',' + selected[i].value
    }
    jQuery.ajax({
        url: base_url + '/explants/start',
        type: 'POST',
        data: { 'miceList':miceList, 'delete':'delete' },
        dataType: 'text',
    });
}

/**** CANCELLAZIONE ALIQUOTE INSERITE ****/
function deleteAliquot(genID){
    var pos = "";  var liquid = false;
    for (typeA in explants){
        for (mouse in explants[typeA]){
            for (barcode in explants[typeA][mouse]){
                for (var i = 0; i < explants[typeA][mouse][barcode].length; i++){
                    if (explants[typeA][mouse][barcode][i]['genID'] == genID){
                        pos = explants[typeA][mouse][barcode][i]['pos'];
                        if (explants[typeA][mouse][barcode][i]['qty'] == 1){
                            if((explants[typeA][mouse][barcode][i]['furtherInfo']) != "-"){ liquid = true; }
                            if (explants[typeA][mouse][barcode].length == 1){
                                if (Object.size(explants[typeA][mouse]) == 1){
                                    delete explants[typeA][mouse];
                                }else{
                                    delete explants[typeA][mouse][barcode];
                                }
                            }else{
                                explants[typeA][mouse][barcode].splice(i,1); 
                            }
                        }else{
                            explants[typeA][mouse][barcode][i]['qty']--;
                        }
                        deleteInPlate(typeA, barcode, pos, genID, liquid);
                        storageIt('expl', JSON.stringify(explants));
                        return;
                    }
                }
            }
        }
    }
}

function deleteInPlate(typeA, barcode, pos, genID, liquid){
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
}

//per cancellare l'inserimento in una piastra (RNA, SNAP, VITAL)
function canc(id_tube){
    id_tube = "#" + id_tube; var num = parseInt(jQuery(id_tube).text());
    if(num > 1){
        num = num - 1;
        jQuery(id_tube).text(num);
    }
    else{
        jQuery(id_tube).css("background-color","rgb(249,248,242)");
        jQuery(id_tube).text(0);
        jQuery(id_tube).removeAttr('sel');
        jQuery(id_tube).attr("disabled", false );
    }
}


/**************************************************/
/************ GESTIONE TOPI E ALIQUOTE *************/
/**************************************************/
function acceptMouse(){    
    jQuery("#barcode, #confirm, #ok").attr("disabled", true );
    jQuery("#nextMouse, #inputf0, #inputo0, #inputc0, #f-0, #o-0, #c-0, #tabs-2 input, #tabs-3 input, input[type='radio']").attr("disabled",false);
    if (nMice > 1){
        jQuery("#ffpe input, #ffpe button, #oct input, #oct button, #cb input, #cb button").attr("disabled",false);
        jQuery("#ffpe input[name='dis'], #ffpe button[sel='s'], #oct input[name='dis'], #oct button[sel='s'], #cb input[name='dis'], #cb button[sel='s']").attr("disabled",true);
        if ( jQuery("#load_vital_plate").attr("load") ){
            jQuery("#vital button").attr("disabled",false);
            jQuery("#vital button[sel='s']").attr("disabled",true);
        }
        if ( jQuery("#load_rna_plate").attr("load") ){
            jQuery("#rna button").attr("disabled",false);
            jQuery("#rna button[sel='s']").attr("disabled",true);
        }
        if ( jQuery("#load_sf_plate").attr("load") ){
            jQuery("#sf button").attr("disabled",false);
            jQuery("#sf button[sel='s']").attr("disabled",true);
        }
    }
    jQuery("#barcode_vital,#barcode_rna,#barcode_sf,#ffpe_plate,#confirm_all,#load_vital_plate,#load_rna_plate,#load_sf_plate,#ffpe_plate,#oct_plate,#cb_plate,#confirm_all,input[loaded='1']").attr("disabled",false);
}

//riceve un barcode del topo dall'apposito input e lo rende disponbile ad essere espiantato, se passa i controlli
function insertMouse(){
    if (document.getElementById('barcode').value){
        barcode = document.getElementById('barcode').value.toUpperCase();
        var site = jQuery("#id_site option:selected").attr('value');
        e = document.getElementById('miceList');
        found = false;
        for (var i = 0; i< e.childNodes.length;i++){
            //controlla tra quelli selezionati tra i 'ready for explant'
            var b = e.childNodes[i].value; var shortbs = b; var typeE = ""
            if (b){
                typeE = b.substr(0,1);
                shortbs = b.substring(1, b.length);

            }
            //console.log(typeE, shortb);
            //if(shortb == barcode){
            //console.log(shortbs, barcode+site);
            if(shortbs == barcode+site){
                //console.log('HHHHHHHH');
                if ( document.getElementById(b).getAttribute('used') == '0'){
                    var url = base_url + "/api.genealogy/" + barcode + '/' + site + '/';
                    console.log(url);
                    jQuery.ajax({
                        async:false,
                        url: url,
                        type: 'get',
                        datatype: 'json',
                        success: function(transport) {
                            var response = transport;
                            document.getElementById('genID').innerHTML  = response.mouse_genealogy;
                            jQuery("#statusM").text(response.mouseStatus);
                            jQuery("#measureDate").text(response.measureDate);
                            jQuery("#explantDate").text('-');
                            jQuery("#supervisorDate").text(response.supervisorDate);
                            jQuery("#measureNotes").text(response.measureNotes);
                            jQuery("#explantNotes").text(response.explNotes);
                            jQuery("#supervisorNotes").text(response.supervisorNotes);
                      }
                    });
                    nMice++;
                    acceptMouse();
                    if (typeE == 'N') { nNMice++; }else { nLMice++; }
                }else
                    alert('This mouse has already been explanted.');
                found = true;
            }
        }
        if(!found){
            alert("Sorry, but this mouse isn't in the list of the mice ready for this explants.");
            document.getElementById('barcode').focus()
            document.getElementById('barcode').value = "";
        }
    }else{
        alert("You've inserted a blank barcode.");
        document.getElementById('barcode').focus()
    }
}

//per passare al topo successivo prima di aver preso tutti i tessuti di quello attuale
function nextMouse(){
    jQuery("#sf button[sel='s_new'],#rna button[sel='s_new'],#vital button[sel='s_new']").attr("sel", "s" );
    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s']").attr("disabled", true );
    var barcode = document.getElementById('barcode').value.toUpperCase();
    var site = jQuery("#id_site option:selected").attr('value');
    if (document.getElementById('N' + barcode + site)){ document.getElementById('N' + barcode + site).setAttribute('used','1'); }
    if (document.getElementById('L' + barcode + site)){ document.getElementById('L' + barcode + site).setAttribute('used','1'); }
    saveUsedMice();
    document.getElementById('barcode').value = "";
    document.getElementById('genID').innerHTML = "";
    document.getElementById('barcode').focus();
    //per disabilitare tutti i pulsanti all'inizio
    jQuery("input, #ffpe button, #sf button,#rna button,#vital button, #vital_confirm,#rna_confirm,#snap_confirm,#ffpe_confirm,#confirm_all").attr("disabled", true );
    //abilito solo l'input per il barcode del topo
    jQuery("#ok, #barcode, #confirm").attr("disabled", false );
}

function nextM(){
    //salvo
    var id = jQuery(tessuti[h]).attr("value");
    var tessuto = jQuery("#tissueNameList input[value='" + id + "']").parent().text();
    tessuto = tessuto[1] + tessuto[2] + tessuto[3];
    var tumore = jQuery("#tum").val();
    var caso = jQuery("#caso").val();
    jQuery("#gen_id").val(tumore + caso + tessuto);
    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s']").attr("disabled", true );
    //disabilito il vecchio checkbox
    jQuery(id).removeAttr("checked");
    //modifico lo stile del vecchio checkbox
    jQuery(id).parent().css("border-style","none");
    //prendo il valore del campo hidden che contiene l'id del checkbox da abilitare
    var id = jQuery("#tissueNameList input[value='" + tessuti[0] + "']").attr("value"); 
    h = 0; id = '#' + id;
    //abilito quel checkbox
    jQuery(id).attr("checked","checked");
    //modifico lo stile del checkbox abilitato
    jQuery(id).parent().css("border-style","solid");
    var tessuto = jQuery(id).parent().text();
    tessuto = tessuto[1] + tessuto[2] + tessuto[3];
    nextMouse(); 
}

/**** CONFERME ALIQUOTE INSERITE ****/
//associata al tasto "next tissue"
function next_tissue(){
    jQuery("#sf button[sel='s_new'],#rna button[sel='s_new'],#vital button[sel='s_new']").attr("sel", "s" ); //aggiorno da s_new a s (s_new:tessuti appena depositati, che diventando 's' non saranno piu' cliccabili)
    var id = jQuery(tessuti[h]).attr("value");
    //disabilito il vecchio checkbox
    jQuery("#tissueNameList input[value='" + id + "']").removeAttr("checked");
    //modifico lo stile del vecchio checkbox
    jQuery("#tissueNameList input[value='" + id + "']").parent().css("border-style","none");
    h = h + 1;
    if(h == tessuti.length){ //quando ho finito i tessuti di un topo
        resetInput();
        alert("You've explanted all the selected tissues for mouse.");
        h = 0;
        //serve per eliminare le selezioni dei tessuti da asportare
        jQuery(".t input:checked").removeAttr("checked");    
        //serve per disabilitare il checkbox dei tessuti
        jQuery("#confirm").attr("disabled",false);
        jQuery(".t input").attr("disabled","disabled");
        //prendo il valore del campo hidden che contiene l'id del checkbox da abilitare
        var id = jQuery("#tissue").val();
        //abilito quel checkbox
        jQuery("#tissueNameList input[value='" + id + "']").attr("checked","checked");
        //modifico lo stile del checkbox abilitato
        jQuery("#tissueNameList input[value='" + id + "']").parent().css("border-style","solid");
        var tessuto = jQuery("#tissueNameList input[value='" + id + "']").parent().text();
        tessuto = tessuto[1] + tessuto[2] + tessuto[3];
        var tumore = jQuery("#tum").val();
        var caso = jQuery("#caso").val();
        jQuery("#gen_id").val(tumore + caso + tessuto);
        jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s']").attr("disabled", true );
        nextMouse();
    }
    else{
        //disabilito i tasti con delle aliquote gia' dentro
        jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s']").attr("disabled", true );
        var id = jQuery(tessuti[h]).attr("value");
        //abilito quel checkbox
        jQuery("#tissueNameList input[value='" + id + "']").attr("checked","checked");
        //modifico lo stile del checkbox abilitato
        jQuery("#tissueNameList input[value='" + id + "']").parent().css("border-style","solid");
        //modifico la scritta per il tipo di tessuto collezionato
        var testo = jQuery("#tissueNameList input[value='" + id + "']").parent().text();
        var n;
        //mi occupo del genealogy ID
        var tessuto = jQuery("#tissueNameList input[value='" + id + "']").parent().text();
        //tolgo lo spazio iniziale che mi mette l'html
        tessuto = tessuto[1] + tessuto[2] + tessuto[3];
        var tumore = jQuery("#tum").val();
        var caso = jQuery("#caso").val();
        jQuery("#gen_id").val(tumore + caso + tessuto);
    }
}

/**************************************************/
/********* GESTIONE STORAGE E SALVATAGGIO *********/
/**************************************************/
function clearStorage(listKey){ clearStorageExpl(listKey, true); }

function clearStorageExpl(listKey, flag){
    var temp = localStorage.getItem('expl');
    for (var i = 0; i < listKey.length; i++){ localStorage.removeItem(listKey[i]); }
    if (flag == true){
        var bb = new BlobBuilder();
        bb.append(temp);
        var blob = bb.getBlob("application/xhtml+xml;charset=" + document.characterSet);
        saveAs(blob, "explantsDump.txt");
        window.location.href = base_url + "/explants/start";
    }
}

function restoreData(listKey, a){
    explants = JSON.parse(localStorage.getItem(listKey[0]));
    //rimettere le righe nella tabella riassuntiva
    for (typeA in explants){
        for (mouse in explants[typeA]){
            for (barcode in explants[typeA][mouse]){
                for (var i = 0; i < explants[typeA][mouse][barcode].length; i++){
                    var pos = explants[typeA][mouse][barcode][i]['pos']
                    var genID = explants[typeA][mouse][barcode][i]['genID']
                    var furtherInfo = explants[typeA][mouse][barcode][i]['furtherInfo'];
                    for (var j = 0; j < explants[typeA][mouse][barcode][i]['list'].length; j++){
                        var tempCounter = explants[typeA][mouse][barcode][i]['list'][j]
                        if (tempCounter >= explantsCounter) { explantsCounter = tempCounter + 1; }
                        jQuery(table_name).dataTable().fnAddData( [null, tempCounter, barcode, pos, genID, furtherInfo ] );
                    }
                }
            }
        }
    }
    var stringArray = localStorage.getItem('notPlateBarcode');
    if (stringArray){ //entra qui solo se esiste almeno un elemento da inserire nella lista --> altrimenti, crasherebbe qui
        var splitted = stringArray.split(',');
        for (var i=0; i < stringArray.split(',').length; i++){ notPlateBarcode.push(splitted[i]); }
    }
    jQuery("#confirm").removeAttr('disabled');
}

//per salvare i dati degli espianti
function submitExplant(){
    jQuery("#confirm").attr("disabled",true);
    startLag();
    var mice = localStorage.getItem('usedMice');
    jQuery.ajax({
        url: base_url+'/explants/submit',
        type: 'POST',
        data: {'explants':JSON.stringify(explants), 'date': jQuery("#date").text(), 'operator': jQuery("#username").text(), 'notes': jQuery("#notes").text(), 'miceList' : mice},
        dataType: 'text',
    });
}

function saveUsedMice(){
    var mice = localStorage.getItem('usedMice');
    var miceList = jQuery("#miceList").children().filter('[used="1"]');
    for (var i = 0; i < miceList.length; i++){ 
        if ( mice == "" ) { 
            mice += jQuery(miceList[i]).attr("value") + '_' + jQuery(miceList[i]).attr('used'); 
        }else{ 
            mice += "|" + jQuery(miceList[i]).attr("value") + '_' + jQuery(miceList[i]).attr('used'); 
        } 
    }
    localStorage.setItem('usedMice', mice);
}
