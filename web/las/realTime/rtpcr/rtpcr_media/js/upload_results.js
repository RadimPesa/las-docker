samples = {}


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
    
    addFile();
    filterByGene();
    initTable();
    initSamples();
    initListeners();

    $("#formMeas").on('submit',function(e) {
        e.preventDefault();
        uploadMeasFile();
    });
});


function initListeners() {
    $("#measure_table").on("click", ".addSpinner", function() {
        var sid = $(this).closest("td").attr("sid");
        addSpinner(sid);
    });

    $("#measure_table").on("click", ".removeSpinner", function() {
        var sid = $(this).closest("td").attr("sid");
        var index = $(this).attr("index");
        removeSpinner(sid, index);
    });
}

function addFile (){
    $("#form_measures").on("change", " input[type=file]:last", function(){
        var item = $(this).clone(true);
        var fileName = $(this).val();
        if(fileName){
            $(this).parent().append(item);
        }  
    });
}

function setNextFlag(flag){
	$('#flagNext').val(flag);
    $('#measures').val(JSON.stringify(samples));
	return true;
}


function filterByGene(){
    $('#geneFilter').on('change', function(){
        if ($(this).val() == 'All'){ // show all columns
            $('#measure_table th').show();
            $('#measure_table td').show();
        }
        else{//show only column with target gene
            var t = $(this).val();
            console.log(t)
            $('#measure_table th').hide();
            $('#measure_table th.genealogy').show();
            $('#measure_table td').hide();  
            $('#measure_table td.genealogy').show();
            $('#measure_table th[tid="' + t +'"]').show();  
            $('#measure_table td[tid="' + t +'"]').show();  
        }
    });
}


function handlerClose(){
    var sid = $(this).closest('td').attr('sid');
    var spinner = $(this).closest('td').find('div');
    var bs = $(this).closest('td').find('.mut');
    $(spinner).hide();
    $(bs).show();
    $(bs).text('N/A');
    samples[sid] = ['bs']
    $(this).removeClass('ui-icon-circle-close');
    $(this).addClass('ui-icon-check');
    $(this).off('click');
    $(this).on('click', handlerCheck);
}

function handlerCheck(){
    var sid = $(this).closest('td').attr('sid');
    var spinner = $(this).closest('td').find('div');
    var bs = $(this).closest('td').find('.mut');
    $(spinner).show();
    $(bs).text('');
    $(bs).hide();
    
    samples[sid] = []
    spinner.each(function() {
        samples[sid].push(parseFloat($(this).find('input').val()));
    });
        
    $(this).removeClass('ui-icon-check');
    $(this).addClass('ui-icon-circle-close');
    $(this).off('click');
    $(this).on('click', handlerClose);

}



function initTable(){
    $( ".spinner" ).spinner({step: 0.01,
      numberFormat: "n",
      min : 1,
      spin: function( event, ui ) {
        var sid = $(this).attr('sid');
        samples[sid][$(this).attr("index")] = parseFloat(ui['value']);
      }
    });

    $( ".spinner" ).on('keyup', function(evt){
        var v = $(this).val();
        var sid = $(this).attr('sid');
        if (v == '' || $.isNumeric(v)) {
            samples[sid][$(this).attr("index")] = v != '' ? parseFloat(v) : '';
        } else {
            $(this).val(samples[sid][$(this).attr("index")]);
        }
    });

    $('#measure_table').dataTable({
        "aaSorting": [[0, 'asc']],
        "bFilter": false, 
        "bInfo": false,
        "iDisplayLength": -1,
        "bPaginate": false,
        "aoColumnDefs": [
        {'bSortable': false, 'aTargets': [ 'no-sort' ] }
       ],
    });
    $('.ui-icon-circle-close').on('click', handlerClose);


}

function initSamples(){
    var list = $('#measure_table td.sample')//.map(function(){return $(this).attr("genealogy");}).get();
    for (var i=0; i<list.length; i++){
        var sid = $(list[i]).attr('sid')
        var tid = $(list[i]).attr('tid')
        samples[sid] = [''];
    }
}


function uploadMeasFile(){
    var formData = new FormData($('#formMeas')[0]);
    formData.append("actionForm", "fileMeas");
    formData.append("targets", JSON.stringify(targets));
    formData.append("idplan", idplan);
    
    $.ajax({
        url: './',  //Server script to process data
        type: 'POST',
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false,
        success: function(transport) {
            data = JSON.parse(transport);
            console.log(data);
            for (var sid in data){
                if (data[sid].length == 0)
                    continue;
                var cnt_na = 0;
                for (var i = 0; i < data[sid].length; ++i) {
                    if (data[sid][i] != NA) {
                        var j = getNextAvailableSpinner(sid);
                        setSpinnerVal(sid, j, data[sid][i]);
                    } else {
                        ++cnt_na;
                    }
                }
                if (cnt_na == data[sid].length) {
                    $("td#" + sid).find(".ui-icon-circle-close").trigger("click");
                }
            }
            $('#measFile').replaceWith($('#measFile').clone()); 
            
        },
        error: function(data) {
            alert(data.responseText, 'Error');
        }
    });
    

}

function setSpinnerVal(sid, i, val) {
    $("td#" + sid + " input:eq(" + i + ")").val(val).trigger("keyup");
}

function getNextAvailableSpinner(sid) {
    var i = samples[sid].indexOf("");
    return i == -1 ? addSpinner(sid) : i;
}

function addSpinner(sid) {
    var tid = $("td#" + sid).attr("tid");
    var index = samples[sid].length;
    samples[sid].push('');
    var elem = $(
        '<div style="display: block; width: 100%; height: 25px">' +
        '   <input class="spinner" style="background-color:lightgreen" sid="' + sid + '" tid="' + tid + '" value="" index="' + index + '" />' +
        '   <span style="float: left; width: 16px; display: inline-block">&nbsp;</span>' +
        '   <span class="ui-icon ui-icon-red ui-icon-minus removeSpinner" style="float: left" index="' + index + '"></span>' +
        '</div>');
    elem.find(".spinner").spinner({step: 0.01,
      numberFormat: "n",
      min : 1,
      spin: function( event, ui ) {
        var sid = $(this).attr('sid');
        samples[sid][$(this).attr("index")] = parseFloat(ui['value']);
      }
    });

    elem.find(".spinner").on('keyup', function(){
        var v = $(this).val();
        var sid = $(this).attr('sid');
        if (v == '' || $.isNumeric(v)) {
            samples[sid][$(this).attr("index")] = v != '' ? parseFloat(v) : '';
        } else {
            $(this).val(samples[sid][$(this).attr("index")]);
        }
    });
    $("td#" + sid).append(elem);
    return index;
}

function removeSpinner(sid, index) {
    var div = $("td#" + sid + " div:eq(" + index + ")");

    var next = div.nextAll(div).toArray();
    while (next.length > 0) {
        var elem = $(next.pop());
        var inp = elem.find("input");
        inp.attr("index", parseInt(inp.attr("index")) - 1);
        var span = elem.find("span.removeSpinner");
        span.attr("index", parseInt(span.attr("index")) - 1);
    }
    
    console.log("removeSpinner");
    console.log(sid, index);
    console.log(div);
    console.log(samples[sid]);
    samples[sid].splice(index, 1);
    console.log(samples[sid]);
    div.remove();
}