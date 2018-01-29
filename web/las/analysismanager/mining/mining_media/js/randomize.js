elements = {}
elements_ids = {}
minvRange = 0
maxvRange = 0
groups_name = {}

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

	generate_result_table($('#partition_elems'));
	generate_groupstat_table($('#groups_stat'));
	jQuery("#upload").click(function(){	
		loadElements();
	});

	jQuery('#randomize').click(function(){
		runRandomize();
	});

    $('#plottype').on('change', function() {
        drawChart($( "#nbuckets" ).spinner( "value"));
    });
});





function initParams (minv, maxv, nTot){
	$( "#th" ).spinner({min:minv, max: maxv, numberFormat: "n", step: 0.01, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) {
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
        } 
    });
	$( "#th" ).spinner( "value", minv );

	$( "#minavg" ).spinner({min:minv, max: maxv, numberFormat: "n", step: 0.01, 
        change: function( event, ui ) { 
            //console.log('minavg', $(this).spinner("value"), $(this).spinner("option")); 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                //console.log($(this).spinner("option")); 
                $(this).spinner("value", $(this).spinner( "option", "min" ));
            }  
        } 
    });
	$( "#minavg" ).spinner( "value", minv );

	$( "#maxavg" ).spinner({min:minv, max: maxv, numberFormat: "n", step: 0.01, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "max" )); 
            } 
        } 
    });
	$( "#maxavg" ).spinner( "value", maxv );

	$( "#minr" ).spinner({min:minv, max: maxv, numberFormat: "n", step: 0.01, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
            $("#minavg").spinner( "option", "min", $(this).spinner("value") ); 
            $("#th").spinner( "option", "min", $(this).spinner("value") ); 
        } 
    });
	$( "#minr" ).spinner( "value", minv );
	
	$( "#maxr" ).spinner({min:minv, max: maxv, numberFormat: "n", step: 0.01, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
            $( "#maxavg" ).spinner( "option", "max", $(this).spinner("value") ); 
            $("#th").spinner( "option", "max", $(this).spinner("value") ); 
        } 
    });
	$( "#maxr" ).spinner( "value", maxv );
	
	$( "#ngroups" ).spinner({min:2, max: nTot, numberFormat: "n", step: 1, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
        } 
    });
	$( "#ngroups" ).spinner( "value", 2 );
	
	$( "#nel" ).spinner({min:1, max: nTot, numberFormat: "n", step: 1, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
        } 
    });
	$( "#nel" ).spinner( "value", 1 );
	
	$( "#optrun" ).spinner({min:1, max: 100000, numberFormat: "n", step: 1, 
        change: function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
        }
    });
	$( "#optrun" ).spinner( "value", 10000 );

    $("#slider label").empty();
	$('#slider').slider({
    	range: true,
    	values: [minv, maxv],
    	min: minv,
    	max: maxv,
    	animate: true,
    	step: 0.01,
    	slide: function( event, ui ) {
        	$( "#minr" ).val( ui.values[ 0 ]);
        	$( "#maxr" ).val( ui.values[ 1 ]);
        	$( "#th" ).spinner( "option", "min", ui.values[ 0 ] );
        	$( "#th" ).spinner( "option", "max", ui.values[ 1 ] );
        	$( "#minavg" ).spinner( "option", "min", ui.values[ 0 ] );
        	$( "#minavg" ).spinner( "option", "max", ui.values[ 1 ] );
        	$( "#maxavg" ).spinner( "option", "min", ui.values[ 0 ] );
        	$( "#maxavg" ).spinner( "option", "max", ui.values[ 1 ] );

      }
	}).each(function() {

	  // Get the options for this slider
	  var opt = $(this).data().uiSlider.options;
	  
	  // Get the number of possible values
	  var vals = opt.max - opt.min;
	  // Space out values
	  //console.log( i, vals,  opt.min , (i/2*100), (i/2*100)*vals);
	  var start = $('<label>'+( (opt.min).toFixed(2))+'</label>').css('left',1+'%');
	  var end = $('<label>'+( (vals + opt.min).toFixed(2))+'</label>').css('right',5+'%');
	  $( "#slider" ).append(start);
	  $( "#slider" ).append(end);
	
	  var hslider = Math.ceil($( "#slider" ).outerHeight()) +2 ;
	  var hlabel = Math.ceil($($( "#slider label" )[0]).outerHeight()) +2 ;
	  //console.log(hslider, hlabel);
	  $('#slider_container').css('height', hslider + hlabel);
	  
	});

	$( "#minr" ).on( "spinchange", function( event, ui ) { 
		if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
			$(this).spinner("value", $(this).spinner( "option", "min" )); 
		}  
		$( "#slider" ).slider({ values: [ $(this).spinner("value"), $('#maxr').spinner("value") ], min: $(this).spinner( "option", "min") });
        $("#minavg").spinner( "option", "min", $(this).spinner("value") ); 
        $("#th").spinner( "option", "min", $(this).spinner("value") ); 
	});

	$('#minr').on("spin", function(event, ui){
		$(this).trigger("spinchange");
	});

	$( "#maxr" ).on( "spinchange", function( event, ui ) { 
		if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
			$(this).spinner("value", $(this).spinner( "option", "max" )); 
		} 
		$("#slider" ).slider({ values: [ $('#minr').spinner("value"), $(this).spinner("value") ], max: $(this).spinner( "option", "max" ) });
        $("#maxavg").spinner( "option", "max", $(this).spinner("value") ); 
        $("#th").spinner( "option", "max", $(this).spinner("value") ); 
	});

	$('#maxr').on("spin", function(event, ui){
		$(this).trigger("spinchange");
	});

    $( "#nbuckets" ).spinner({min:2, max: nTot, numberFormat: "n", step: 1 });
    $( "#nbuckets" ).spinner( "value", 10 );

    $('#nbuckets').on("spinchange", function( event, ui ) { 
            if ($(this).spinner("value") > $(this).spinner( "option", "max" ) || $(this).spinner("value") < $(this).spinner( "option", "min" )) { 
                $(this).spinner("value", $(this).spinner( "option", "min" )); 
            } 
            //console.log('spinchange nbuckets', $(this).spinner("value"),ui);
            drawChart($(this).spinner("value"));
        } 
    );

    $('#nbuckets').on("spin", function(event, ui){
        $(this).spinner("value", ui.value);
        $(this).trigger("spinchange");
    });
	

}


function generate_result_table(table){
	
	var actionname = 'RandomizedElements';

    var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = actionname + "_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    jQuery(table).dataTable( {
		"aoColumns": [
            { "sTitle": "#" },
            { "sTitle": "Element" },
            { "sTitle": "Value" },
            { "sTitle": "Group id"},
            { "sTitle": "Group name"}
        ],    	
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 3 ] },
        ],
        "iDisplayLength": -1,
        "sDom":'TH<\"clear\">lfrtip',
        "oTableTools": {
                "aButtons": [ 
                {
                                "sExtends": "las",
                                "sButtonText": "Las",
                                "sTitle": filename,
                                "mColumns": "visible"
                }, 
                {
                                "sExtends": "pdf",
                                "sButtonText": "Pdf",
                                "sPdfMessage": "Laboratory Assistant Suite - Analysis Manager - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()),
                                "sTitle": filename,
                                "mColumns": "visible",
                                "sPdfSize": "tabloid"
                },
                {
                                "sExtends": "data",
                                "sButtonText": "Data",
                                "sTitle": filename,
                                "mColumns": "visible"
                },
                {
                                "sExtends": "xls",
                                "sButtonText": "Xls",
                                "sTitle": filename,
                                "mColumns": "visible"
                }, 
                "print"
                ],
                "sUrl": lasauth_url + "generate_report/",        
        }
        
    });
}


function generate_groupstat_table(table){
	
	var actionname = 'RandomizedGroupStat';

    var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = actionname + "_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    var oTable = jQuery(table).dataTable( {
		"aoColumns": [
            { "sTitle": "Group id" },
            { "sTitle": "Group name (Editable)" },
            { "sTitle": "Mean" },
            { "sTitle": "Std"},
            { "sTitle": "Coeff. of variation"},
            { "sTitle": "Notes"},
        ],    	
        //"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0 ] },
        ],
        "sDom":'T<\"clear\">',//lfrtip',
        "oTableTools": {
                "aButtons": [ 
                {
                                "sExtends": "las",
                                "sButtonText": "Las",
                                "sTitle": filename,
                                "mColumns": "visible"
                }, 
                {
                                "sExtends": "pdf",
                                "sButtonText": "Pdf",
                                "sPdfMessage": "Laboratory Assistant Suite - Analysis Manager - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()),
                                "sTitle": filename,
                                "mColumns": "visible",
                                "sPdfSize": "tabloid"
                },
                {
                                "sExtends": "data",
                                "sButtonText": "Data",
                                "sTitle": filename,
                                "mColumns": "visible"
                },
                {
                                "sExtends": "xls",
                                "sButtonText": "Xls",
                                "sTitle": filename,
                                "mColumns": "visible"
                }, 
                "print"
                ],
                "sUrl": lasauth_url + "generate_report/",          
        },
        "fnDrawCallback": function () {
        jQuery('#groups_stat > tbody > tr').find('td:eq(4)').editable( 
            function(value, settings) { 
                return(value);
            }, {
                "callback": function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    oTable.fnUpdate( sValue, aPos[0], aPos[2] );
                },
                "height": "10px",
                "width": "50px"
                }
            );
        jQuery('#groups_stat > tbody > tr').find('td:eq(0)').editable( 
            function(value, settings) { 
                return(value);
            }, {
                "callback": function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    var dataGroup = oTable.fnGetData( aPos[0] );
                    if (dataGroup[1] == sValue || sValue == ''){
                        oTable.fnUpdate( dataGroup[1], aPos[0], aPos[2] );
                    }
                    else{
                        if (!groups_name.hasOwnProperty(sValue)) {
                            groups_name[sValue] = true;
                            delete groups_name[dataGroup[1]];
                            var elems = jQuery('#partition_elems').dataTable().fnGetData();
                            jQuery('#partition_elems').dataTable().fnClearTable();
                            jQuery.each(elems, function(index, values){
                                if (values[3] == dataGroup[0]){
                                    values[4] = sValue;
                                }
                                jQuery('#partition_elems').dataTable().fnAddData(values)
                            });
                            oTable.fnUpdate( sValue, aPos[0], aPos[2] );
                            jQuery('#partition_elems').dataTable().fnSort( [ [3,'asc'], [0,'asc'] ]);
                        }
                        else{
                            alert('Unique name required for groups!');
                            oTable.fnUpdate( dataGroup[1], aPos[0], aPos[2] );
                        }
                    }
                },
                "height": "10px",
                "width": "50px"
                }
            );
        }
    });
}


function loadElements(){
	var formData = new FormData($('#upload_elem_file')[0]);
	//console.log(formData);
    $.ajax({
        url: base_url + "/api.readRandomize",
        type: 'POST',
        //Ajax events
        success: function(transport) {
            if (transport.hasOwnProperty('response')){
                alert(transport['response']);
                var control = $("#id_file");
                control.replaceWith( control = control.clone( true ) );
                return;
            }
        	var nTot = transport['elements'].length;
        	var minv = 0;
			var maxv = 0;
			elements = {};
			jQuery('#partition_elems').dataTable().fnClearTable();
            jQuery.each(transport['elements'], function(index, value){
                jQuery('#partition_elems').dataTable().fnAddData([index+1, value['obj'], value['val'], -1, '']);
                if ( elements.hasOwnProperty(value['obj']) ){
                	alert ('Not unique identifiers for elements');
                	return
                }
                elements[value['obj']] = parseFloat(value['val']);
                elements_ids[value['obj']] = index;
                if (index==0){ minv=parseFloat(value['val']); maxv= parseFloat(value['val']);}
                else{
	                if (parseFloat(value['val']) < minv ){ minv= parseFloat(value['val']);}
	                if (parseFloat(value['val']) > maxv ){ maxv= parseFloat(value['val']);}
	            }
            });
            var control = $("#id_file");
            control.replaceWith( control = control.clone( true ) );
            
            initParams(minv, maxv, nTot);
            $('#parameters').show();
            $('#groups_random').show();
			$('#elem_list').show();
            minvRange = minv;
            maxvRange = maxv;
            drawChart($("#nbuckets").spinner( "value"));
        },

        error: function(msg) {
            alert(msg['response']);
        },

        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
    });

	

}


function runRandomize(){
	dataSubmit = {}

	dataSubmit['th'] = $( "#th" ).spinner( "value");
	dataSubmit['minr'] = $( "#minr" ).spinner( "value");
	dataSubmit['maxr'] = $( "#maxr" ).spinner( "value");
	dataSubmit['minavg'] = $( "#minavg" ).spinner( "value");
	dataSubmit['maxavg'] = $( "#maxavg" ).spinner( "value");
	dataSubmit['ngroups'] = $( "#ngroups" ).spinner( "value");
	dataSubmit['nel'] = $( "#nel" ).spinner( "value");
	dataSubmit['optrun'] = $( "#optrun" ).spinner( "value");
	dataSubmit['data'] = elements;

    var jsonData = JSON.stringify(dataSubmit);
    startLag();
    jQuery.ajax({
        type: 'POST',
        url: base_url + "/api.runRandomize",
        data: jsonData, 
        dataType: "json", 
        success: function(transport) { 
        	if (transport.hasOwnProperty('response')){
                endLag();
        		alert(transport['response']);
        		return;
        	}
        	var insertedElem = {};
            groups_name = {};
        	$('#glob_mean').text(transport['mean'].toFixed(3));
        	$('#glob_std').text(transport['std'].toFixed(3));
        	$('#glob_coeffvar').text(transport['coeffVar'].toFixed(4));
        	jQuery('#partition_elems').dataTable().fnClearTable();
        	$('#groups_stat').dataTable().fnClearTable();
        	jQuery.each(transport['buckets'], function(index, value){
        		$('#groups_stat').dataTable().fnAddData([parseInt(index)+1, (parseInt(index)+1).toString(), value['mean'].toFixed(3), value['std'].toFixed(3), value['coeffVar'].toFixed(4), '']);
        		jQuery.each(value['elements'], function(i, elem){
					jQuery('#partition_elems').dataTable().fnAddData([elements_ids[elem[0]], elem[0], elem[1], parseInt(index)+1, (parseInt(index)+1).toString()]);
                    groups_name[(parseInt(index)+1).toString()] = true;
					insertedElem[elem[0]] = true;
        		});
            });

        	jQuery.each(elements, function(key, val){
        		if (!insertedElem.hasOwnProperty(key)){
        			jQuery('#partition_elems').dataTable().fnAddData([elements_ids[key], key, val, dataSubmit['ngroups']+1 , 'discarded']);
        		}
        	});
        	jQuery('#partition_elems').dataTable().fnSort( [ [3,'asc'], [0,'asc'] ]);
			

        	$('#final_info').show();
        	endLag();
        },

        error: function(data) { 
        	endLag();
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");

        }
    });

}

function drawChart(nbuckets){
    var plottype = $('#plottype  option:selected').val();
    if (plottype == 'dist'){
        $( "#select_bins" ).hide();
        drawDistChart();
    }
    else if (plottype == 'hist'){
        $( "#select_bins" ).show();
        drawHistChart(nbuckets);
    }

}



function drawDistChart(){
    //console.log('dist');
    $('#chart1').empty();
    var datasorted = [];
    $.each(elements, function(key, value){
        datasorted.push([parseFloat(value), key]);
    });
    datasorted.sort(function(a,b){return a[0]-b[0]});
    var graphPoints = [];
    var xticks = [0];
    $.each(datasorted, function(index, value){
        graphPoints.push([index+1, value[0], value[1]]);
        xticks.push(index+1);
    });
    xticks.push(graphPoints.length+1);
    var minx = 0;
    if (graphPoints[0][1] < 0){
        minx = graphPoints[0][1];
    }
    //console.log(graphPoints);
    $.jqplot ('chart1', [graphPoints], {
        axesDefaults: {
            labelRenderer: $.jqplot.CanvasAxisLabelRenderer
        },
        series:[ 
            {
                color: '#006262',
            }
        ],
        axes: {
            xaxis: {
                //min:0,
                padMin: 0,
                padMax: 1,
                label: "Sample rank",
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                ticks:xticks,
                tickOptions: {
                    formatString: '%d', 
                    fontSize: '8pt'
                },
            },
            yaxis: {
                min: minx,
                padMin: 0,
                padMax: 1,
                label: "Values",
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
                tickOptions: {
                    formatString: '%.2f', 
                    fontSize: '8pt'
                },
            }
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5,
            yvalues: 3,
            tooltipLocation: 'n',
            formatString:'<table class="jqplot-highlighter"> \
                          <tr><td>Rank position:</td><td>%s</td></tr> \
                          <tr><td>Value:</td><td>%s</td></tr> \
                          <tr><td>Object id:</td><td>%s</td></tr></table>'
        },
        cursor: {
            show: false,
        }
    });

}


function drawHistChart(nbuckets){
    //console.log('hist');
    $('#chart1').empty();
    var rangeBucket = (maxvRange-minvRange)/nbuckets;
    var dataBuckets = [];
    var ticks = [];
    for (var i=0; i<nbuckets; i++){
        dataBuckets.push(0);
        ticks.push('[' + Math.round(minvRange+ (maxvRange-minvRange)/nbuckets*i).toFixed(2) + ',' + Math.round(minvRange+(maxvRange-minvRange)/nbuckets*(i+1)).toFixed(2) + ')');
    }

    var maxnBuck = 0
    $.each(elements, function(key, value){
        var index = Math.floor((value-minvRange)/rangeBucket);
        if (index == nbuckets){
            index--;
        }
        dataBuckets[index] += 1; 
        if (dataBuckets[index] > maxnBuck){
            maxnBuck = dataBuckets[index];
        }
    });
   
   var yticks = [];
   for (var i=0; i<=maxnBuck+1; i++){
        yticks.push(i);
   }
     
    $.jqplot('chart1', [dataBuckets], {
        seriesDefaults:{
            renderer:$.jqplot.BarRenderer,
            rendererOptions: {fillToZero: true, barMargin: 3}
        },

        legend: {
            show: false,
        },
        series:[ 
            {
                color: '#006262',
            }
        ],
        axes: {
            xaxis: {
                renderer: $.jqplot.CategoryAxisRenderer,
                tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                ticks: ticks,
                tickOptions: {
                    angle: -30,
                    fontSize: '8pt',
                    labelPosition: 'middle'
                },
                label: "Bins",
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
            },
            yaxis: {
                padMin: 0,
                padMax: 1.2,
                min: 0,
                tickOptions: {
                    formatString: '%d', 
                    fontSize: '8pt'
                },
                ticks: yticks,
                label: "#Objects",
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
            }
        }
    });

}