jQuery(document).ready(function () {
    
    menu = $( '#dl-menu' ).dlmenu();

    generate_result_table('table#results', 'QueryGenerator_');
    
    $('#selectAllCheck').prop('checked',false);
    $('#results').on('click','#selectAllCheck',function(){
        if(this.checked) { // check select status
            $('.selectCheck').each(function() { //loop through each checkbox
                $(this).prop('checked', true);
                var tr = $(this).closest('tr');
                var row = $('#results').dataTable().fnGetData(tr)
                selectedNode[row.ID] = true;
            });
        }else{
            $('.selectCheck').each(function() { //loop through each checkbox
                $(this).prop('checked', false);
                var tr = $(this).closest('tr');
                var row = $('#results').dataTable().fnGetData(tr)
                delete selectedNode[row.ID];
            });         
        }
    });
    
    $('#results').on('change','.selectCheck',function(){
        if (this.checked){
            $(this).prop('checked', true);
            var tr = $(this).closest('tr');
            var row = $('#results').dataTable().fnGetData(tr)
            selectedNode[row.ID] = true;
        }
        else{
            $(this).prop('checked', false);
            var tr = $(this).closest('tr');
            var row = $('#results').dataTable().fnGetData(tr)
            delete selectedNode[row.ID];
        }
    });
});


function shareData (){

        if (Object.keys(selectedNode).length == 0){
            alert('You have to select at least one entity');
            return;
        }                       
                        
        var html="<form id='shareForm' action=''><div id='shareDiv'><ul>";
        var fullWgList;
        var dialog='';
        $.ajax({
            url: "/mdam/api/getWorkingGroups/",
            type: "GET",
            dataType: 'json',
        }).done(function(res) {
            for (wgID in res['wgList']){                       
                for (wgName in res['wgList'][wgID]){
                    window.res=res['wgList'][wgID][wgName];
                    if (wgName!='admin'){
                        html+="<li><input type='checkbox' elemType='WG' class='wgCheck' id='"+wgName+"' name='"+wgName+"' value='"+wgName+"''/'>"+wgName+"<ul>";
                        for (userID in res['wgList'][wgID][wgName]){
                            html+="<li><input type='checkbox' elemType='user' WG='"+wgName+"' class='wgCheck' id='"+res['wgList'][wgID][wgName][userID]+"' name='"+res['wgList'][wgID][wgName][userID]+"' value='"+res['wgList'][wgID][wgName][userID]+"''/'>"+res['wgList'][wgID][wgName][userID]+"</li>";
                        }      
                        html+="</ul>";        
                    }
                }
            }
            html+="</ul>";
            html+="</div></form>";
            $("#shareDialog").html(html); 

            $("#shareDialog").dialog({
                autoOpen: false,
                title: 'Share data',
                buttons: {
                    "Submit Form": function() {
                        var wgList=new Array();
                        $('.wgCheck').each(function(){
                            if ($(this).prop('checked')==true){
                                dictWG={};
                                dictWG['WG']='';
                                dictWG['user']=new Array();
                                if ($(this).attr('elemType')=='WG'){
                                    dictWG['WG']=$(this).attr('name');
                                    dictWG['user'].push('owner');                
                                    wgList.push(dictWG);
                                }
                                else{
                                    var found=false;
                                    var wgName=$(this).attr('WG');
                                    for (wgID in wgList){
                                        if (wgList[wgID]['WG']==wgName){
                                            wgList[wgID]['user'].push($(this).attr('name'));
                                            found=true;
                                        }
                                    }
                                    if (!found){
                                        dictWG['WG']=wgName;
                                        dictWG['user'].push($(this).attr('name'));
                                    }                
                                }
                            }
                        });
                        if (wgList.length == 0){
                            alert('You have to select at least one Working Group');
                            return false;
                        }
                        
                        ctrl = getBusyOverlay("viewport", {color:'#B2B2B2', opacity:1, text:'Sharing data, please wait...', style: 'color: #222222;'}, {color:'#222222', weight:'3', size:100, type:'rectangle', count:12});

                        $.ajax({
                            url: "/mdam/api/shareData/",
                            type: "POST",
                            dataType: 'json',
                            data: { 
                                entities: JSON.stringify(selectedNode), 
                                wgList: JSON.stringify(wgList),
                                qid: qid,
                                rid: rid,}
                        }).done(function(res) {
                            $("#shareDialog").dialog("close");
                            ctrl.remove();
                            console.log(res);
                            if (res['message']=='ok'){
                                html="<h3>Shared entities:</h3><br>";
                                if (res['sharedEntityList'].length>0){
                                    html+="<table><tr><th>Genealogy ID</th></tr>";
                                    for (id in res['sharedEntityList'])
                                        html+="<tr><td>"+res['sharedEntityList'][id]+"</td></tr>";
                                    html+="</table><br><br><br>";
                                }
                                else{
                                    html+="<br><p>No entities shared!</p><br><br><br>";            
                                }
                                if (res['notSharedEntityList'].length>0){
                                    html+="<h3 title='These entities could not be shared because your Working Group(s) do(es) not have the ownership' >Not shared entities:</h3><br>";
                                    html+="<table><tr><th>Genealogy ID</th></tr>";
                                    for (id in res['notSharedEntityList'])
                                        html+="<tr><td>"+res['notSharedEntityList'][id]+"</td></tr>";
                                    html+="</table><br><br>";
                                }

                                var dialogReport = $('<div></div>').html(html) 
                                .dialog({
                                    autoOpen: true,
                                    title: 'Sharing Report',
                                    buttons: {
                                        "Ok": function() {
                                            $(this).dialog("close");
                                        }
                                    }
                                });
                            }

                            else{
                                alert('Error in sharing data. Please contact the system administrator');
                            }
                        });
                    },
                    "Cancel": function() {
                        $(this).dialog("close");
                    }
                }
            });
            $('#shareDialog div').tree({
            });
            $('#shareDialog div').tree('collapseAll');
            $("#shareDialog").dialog('open');
        });
}



function exportData(){

    $.ajax({
        url: getResultsUrl,
        data: "qid=" + qid + "&rid="+ rid+ "&action=getHeaders",
    })
    .done(function(res) {
        res = JSON.parse(res);
        console.log(res);
        prepareExportDialog(res);
        $("#exportDialog").dialog("open");
        //alert(content);
        
    })
    .fail(function(data) {
        alert('error in retrieving headers');
    });

}

function prepareExportDialog (res){

    

    loadAccordion(res);
    $('.fileType').prop('checked', true);
    $( "#tabs" ).tabs({heightStyle: "auto"});
    
    //$('#fSel').css('overflow', 'auto');

    $("#exportDialog").dialog(
        {autoOpen: false,
        title: "Export Data",
        width: 500,
        height: 500,
        resizable: false,
        buttons:
            [
                {
                    text: "Export",
                    click: function() {
                        var fileTypes = $('.fileType:checked').map(function(_, el) {
                                            return $(el).val();
                                        }).get();
                        var selectedHeaders = $('#hSel').find('.leafNode:checked').next('a');
                        var listNode= {};
                        for (var i= 0; i< selectedHeaders.length; i++){
                            var qid = $(selectedHeaders[i]).attr('query');
                            var hid = $(selectedHeaders[i]).attr('head');
                            if (!listNode.hasOwnProperty(qid)){
                                listNode[qid] = [];
                            }
                            listNode[qid].push(hid);                            
                        }
                        
                        dowloadResults(fileTypes, listNode);
                        $(this).dialog("close");
                    }
                },
                {
                    text: "Cancel", 
                    click: function(){
                        $(this).dialog("close");
                    }
                }
            ],
        open: function( event, ui ) {
                var tabH = $('#tabs').height();
                $('#hSel').css('height', tabH *0.8);
                $('#hSel').css('overflow', 'auto');
                $('#fSel').css('height', tabH *0.8);  
                $('#fSel').css('overflow', 'auto');
            },
        });
}


function loadAccordion(dataJson){
    
    var htmlCode = "<div class='accordionResults'> ";
    htmlCode += " <div class='node'> Query <p style='display:inline-block;margin:0px;float:right'><label>Select all</label><input style='float:right;' type='checkbox' class='pinToggles'></p></div> <div>";
    for (var sample in dataJson.queryHeader){
        if (dataJson.queryHeader[sample] != 'pk')
            htmlCode += "<p><input style='float:left;' type='checkbox' class='pinToggles leafNode'><a class='linkfile' query='"+  -1 + "' head='" +  sample + "'> " + dataJson.queryHeader[sample] + " </a></p>";
    }
    htmlCode += " </div> ";

    for (var tid in dataJson.meta){
        htmlCode += " <div class='node'>"+ dataJson.meta[tid].title +" <p style='display:inline-block;margin:0px;float:right'><label>Select all</label><input style='float:right;' type='checkbox' class='pinToggles'></p></div> <div>";
        for (var i in dataJson.meta[tid].headers){
            htmlCode += "<p><input style='float:left;' type='checkbox' class='pinToggles leafNode'><a class='linkfile' query='"+  tid + "' head='" +  i + "'> " + dataJson.meta[tid].headers[i] + " </a></p>";
        }
        htmlCode += " </div> ";
    }

    htmlCode += " </div> ";


    $('#hSel').empty();
    $('#hSel').append(htmlCode);
    initAccordion();
    $('.node').find('.pinToggles').click();
}


function initAccordion(){
    $(".accordionResults" ).accordion({
                collapsible: true,
                heightStyle: "content",
                active: false,
                //header: ".accheader"
            });

    $('.pinToggles').click(function(e) {
        if (!this.checked){
            if ($(this).hasClass('leafNode')){
                var node = $(this);
            }
            else{
                $(this).closest('div').next('div').find("input[type='checkbox']").prop('checked', this.checked);
                var node = $(this).closest('div');
            }
            recursiveCheck(node, this.checked);             
        }
        else{
            if ($(this).hasClass('leafNode') == false){
                $(this).closest('div').next('div').find("input[type='checkbox']").prop('checked', this.checked);
                $(this).prev('label').text('Unselect all');
                $(this).closest('div').next('div').find('label').text('Unselect all');
            }
        }
        e.stopPropagation();
    });
}


function recursiveCheck(el, checked){
    if (el.hasClass('leafNode')){
            var parent = $(el.closest(".node").children("[role='tab']")[0]);
            recursiveCheck(parent, checked);
    }
    else{
        el.find("input[type='checkbox']").prop('checked', checked);
        el.find('label').text('Select all');
        el.closest('div').next('div').find('label').text('Select all');
        var parent = el.parent().prev('.node');
        if (parent.length > 0){
            recursiveCheck( parent, checked);
        }
    }   
}


function dowloadResults(fileTypes, listNode){
    var url =  getResultsUrl;

    /* submit request do download the file */
    nIFrame = document.createElement('iframe');
    nIFrame.setAttribute( 'id', 'RemotingIFrame' );
    nIFrame.style.border='0px';
    nIFrame.style.width='0px';
    nIFrame.style.height='0px';
         
    document.body.appendChild( nIFrame );
    var nContentWindow = nIFrame.contentWindow;
    nContentWindow.document.open();
    nContentWindow.document.close();
     
    var nForm = nContentWindow.document.createElement( 'form' );
    nForm.setAttribute( 'method', 'post' );
    
    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'fileTypes' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify(fileTypes);
     
    nForm.appendChild( nInput );

    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'headers' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify(listNode);
     
    nForm.appendChild( nInput );

    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'qid' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify(qid);
     
    nForm.appendChild( nInput );


    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'rid' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify(rid);
     
    nForm.appendChild( nInput );

    nInput = nContentWindow.document.createElement( 'input' );
    nInput.setAttribute( 'name', 'action' );
    nInput.setAttribute( 'type', 'text' );
    nInput.value = JSON.stringify("download");
     
    nForm.appendChild( nInput );


    nForm.onload = function () {
        console.log('finish');
    }
    
    nForm.setAttribute( 'action', url);
     
    /* Add the form and the iframe */
    nContentWindow.document.body.appendChild( nForm );


    /* Send the request */
    nForm.submit();


}

