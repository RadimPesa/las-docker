var perms= new Array();
var lasauthmedia="";
function addPermission(id,permission){
	if (perms[id] == undefined)
		perms[id]=new Array();
	perms[id].push(permission);
}
function fnFormatDetails ( oTable, id )
{
   
    var sOut = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
    sOut += '<tr><td></td><td><li>Permissions<ul>';
    for(x in perms[id]){
    	sOut += "<li>"+perms[id][x]+"</li>";
    }
    sOut += '</ul></li></td></tr></table>';
     
    return sOut;
}
 
$(document).ready(function() {
    /*
     * Insert a 'details' column to the table
     */
    var nCloneTh = document.createElement( 'th' );
    var nCloneTd = document.createElement( 'td' );
    nCloneTd.innerHTML = "<img src="+lasauthmedia+"img/details_open.png>";
    nCloneTd.className = "center";
     
    $('#example thead tr').each( function () {
        this.insertBefore( nCloneTh, this.childNodes[0] );
    } );
     
    $('#example tbody tr').each( function () {
        this.insertBefore(  nCloneTd.cloneNode( true ), this.childNodes[0] );
    } );
     
    /*
     * Initialse DataTables, with no sorting on the 'details' column
     */
    var oTable = $('#example').dataTable( {
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] }
        ],
        "aaSorting": [[1, 'asc']],
        "bInfo": false,
        "bPaginate" :false,
        "bFilter": false
    });
     
    /* Add event listener for opening and closing details
     * Note that the indicator for showing which row is open is not controlled by DataTables,
     * rather it is done here
     */
    $('#example tbody td img').live('click', function () {
        var nTr = $(this).parents('tr')[0];
        if ( oTable.fnIsOpen(nTr) )
        {
            /* This row is already open - close it */
            this.src = lasauthmedia+"img/details_open.png";
            oTable.fnClose( nTr );
        }
        else
        {
            /* Open this row */
            this.src = lasauthmedia+"img/details_close.png";
            oTable.fnOpen( nTr, fnFormatDetails(oTable, nTr.id), 'details' );
        }
    } );
} );