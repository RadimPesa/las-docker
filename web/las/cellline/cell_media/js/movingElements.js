//Get the selected TR nodes from DataTables
function fnGetSelectedSx(){
    var aReturn = new Array();
    var aTrs = oTableSx.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( jQuery(aTrs[i]).hasClass('row_selected') )
	        aReturn.push( aTrs[i] );
    }
    return aReturn;
}

//Get the selected TR nodes from DataTables
function fnGetSelectedDx(){
    var aReturn = new Array();
    var aTrs = oTableDx.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( jQuery(aTrs[i]).hasClass('row_selected') )
	        aReturn.push( aTrs[i] );
    }
    return aReturn;
}

function moveTo(direction, tableSx, tableDx){
    //if ((groupDx != "") && (groupSx != "")){
        console.log('moving');
        console.log(direction, tableSx, tableDx);
        if (direction == 'dx'){
            var destinationTable = tableDx; var sourceTable = tableSx; var sourceRows = fnGetSelectedSx(); var oTableSource = oTableSx; var oTableDestination = oTableDx; 
            var oSettingsDestination = oSettingsDx; //var sourceGroup = groupSx; var destinationGroup = groupDx;
        }else if (direction == 'sx'){
            var destinationTable = tableSx; var sourceTable = tableDx; var sourceRows = fnGetSelectedDx(); var oTableSource = oTableDx; var oTableDestination = oTableSx;
            var oSettingsDestination = oSettingsSx; //var sourceGroup = groupDx; var destinationGroup = groupSx;
        }
        if (sourceRows.length > 0){
            var startRows = oTableDestination.fnGetNodes().length;
            for (var i = 0; i < sourceRows.length; i++){
                $(destinationTable).dataTable().fnAddData( oTableSource.fnGetData(sourceRows[i]) );

                $(oSettingsDestination.aoData[startRows+i].nTr).click( function() {
                    $(this).toggleClass('row_selected');
                });
            }
            for (var i = 0; i < sourceRows.length; i++){
                var index = oTableSource.fnGetPosition( sourceRows[i]);
                oTableSource.fnDeleteRow(index);
            }

            jQuery("#confirm").show();
        }
}