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

    initGUI();
    generate_tables();
});


// init data tables
function generate_tables(){
    jQuery("table#probes_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Probe name", "width": "50%" },
            { "sTitle": "Gene symbol", "width": "45%" },
            { "sTitle": "Variable", "width": "5%" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[2, 'asc'], [0, 'asc']],
    "bFilter": false
    });

    jQuery("table#aggreg_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Variable", "width": "4%" },
            { "sTitle": "Mode", "width": "32%" },
            { "sTitle": "Intra-probe function", "width": "32%" },
            { "sTitle": "Inter-probe function", "width": "32%" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    "bFilter": false
    });

    jQuery("table#aggreg_table tbody tr").each(function() {
        var var_name = $(this).attr("variable_name");
        $(this).children().eq(0).addClass(varmap[var_name]);
    });

    jQuery("table#inputs_table").dataTable( {
        "bProcessing": true,
        "bAutoWidth": false ,
        "aaSorting": [[0, 'asc']],
        "bFilter": true
    });

    jQuery("table#inputs_table thead span").each(function() {
        var var_name = $(this).attr("variable_name");
        $(this).addClass(varmap[var_name]);
    });

    jQuery("table#outputs_table").dataTable( {
        "bProcessing": true,
        "bAutoWidth": false ,
        "aaSorting": [[0, 'asc']],
        "bFilter": true
    });

    jQuery("table#outputs_table tbody").click(function(event) {
        var hasClass = jQuery(event.target.parentNode).hasClass('row_selected');
        var dt = jQuery('table#outputs_table').dataTable();
        var dti = jQuery('table#inputs_table').dataTable();
        // remove highlighting from all rows in outputs_table
        dt.$("tr.row_selected").removeClass("row_selected").each(function() {
            highlightInputs(false, this);
        });
        // remove filtering function from inputs_table
        $.fn.dataTableExt.afnFiltering.pop();
        
        if (!hasClass) {
            jQuery(event.target.parentNode).addClass('row_selected');
            highlightInputs(true, event.target.parentNode);
            $.fn.dataTableExt.afnFiltering.push(function( oSettings, aData, iDataIndex ) {
                if (oSettings.sInstance == 'inputs_table') {
                    return highlighted_rows.indexOf(aData[0]) != -1;
                } else {
                    return true;
                }
            });
        }

        dti.fnDraw();

    });
    
}

// init the data table
function initGUI() {
    $("#main_tabs").tabs();
}

var highlighted_rows = [];

function highlightInputs(op, element) {
    var variables = JSON.parse(jQuery(element).attr("variables"));
    var dt = jQuery('table#inputs_table').dataTable();
    for (var v in variables) {
        var ids = flatten([variables[v]]);
        var className = varmap[v];
        for (var i = 0; i < ids.length; ++i) {
            dt.$("#sample_" + ids[i]).toggleClass(className, op);
            if (op) {
                highlighted_rows.push(dt.$("#sample_" + ids[i]).closest("tr").attr("input_id"));
            } else {
                highlighted_rows.pop(); // we remove one element regardless of which particular element is being unhighlighted
            }
        }
    }
}

// This is done in a linear time O(n) without recursion
// memory complexity is O(1) or O(n) if mutable param is set to false
function flatten(array, mutable) {
    var toString = Object.prototype.toString;
    var arrayTypeStr = '[object Array]';

    var result = [];
    var nodes = (mutable && array) || array.slice();
    var node;

    if (!array.length) {
        return result;
    }

    node = nodes.pop();

    do {
        if (toString.call(node) === arrayTypeStr) {
            nodes.push.apply(nodes, node);
        } else {
            result.push(node);
        }
    } while (nodes.length && (node = nodes.pop()) !== undefined);

    result.reverse(); // we reverse result to restore the original order
    return result;
}