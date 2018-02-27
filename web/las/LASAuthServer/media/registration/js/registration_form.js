var data="";
var userType="";
var fromTablePi='';
var toTablePi='';
var fromTableUser='';
var toTableUser='';
var affiliation=new Array();
var newaffiliation='';
var firstname = ''; 
var lastname = ''; 
var username= ''; 
var email1 = '';  
var email2 = ''; 
var userType= ''; 
var new_name='';
var new_state='';
var new_department='';
var new_name_pi_aff='';
var new_state_pi_aff='';
var new_department_pi_aff='';
var new_pi_name='';
var new_pi_lastname='';
var new_pi_mail='';
var new_pi_name_lasuserAff='';
var new_pi_lastname_lasuserAff='';
var new_pi_mail_lasuserAff='';
var new_aff_flag=false;
var roleArray= new Array();
var affiliationsFinal = new Array();
var affiliationsFinal2 = new Array();
var rolesFinal=new Array();
var popupDiv= new Array();
var registrationUrl='';
var completeUrl='';
var indexUrl='';
var project='';

function setRegistrationUrl(regUrl,compUrl,indUrl,errUrl){
    registrationUrl=regUrl;
    completeUrl=compUrl;
    indexUrl=indUrl;
    errorUrl=errUrl;
}
function fnGetSelected( oTableLocal ){
    var aReturn = new Array();
    var aTrs = oTableLocal.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( $(aTrs[i]).hasClass('row_selected') )
        {
            aReturn.push( aTrs[i] );
        }
    }
    return aReturn;
}

function resetDatatables(){
    fromTablePi.fnDestroy();
    fromTableUser.fnDestroy();
    toTablePi.fnDestroy();
    toTableUser.fnDestroy();
}
function clearDatatables(){
    fromTablePi.fnClearTable();
    fromTableUser.fnClearTable();
    toTablePi.fnClearTable();
    toTableUser.fnClearTable();
}

function setDatatables(){
    fromTableUser = $('#From_user').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }

    }).rowReordering();
    fromTablePi = $('#From_pi').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }

    }).rowReordering();
    toTablePi = $('#To_pi').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }
    }).rowReordering();
    
    toTableUser = $('#To_user').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }
    }).rowReordering();
}

function initializeSelectable(){
	var fromTableUser=$('#From_user').dataTable();
	var fromTablePi = $('#From_pi').dataTable();
	var toTableUser = $('#To_user').dataTable();
	var toTablePi = $('#To_pi').dataTable();
	
	fromTableUser.$('tr').off('click');
	fromTablePi.$('tr').off('click');
	toTableUser.$('tr').off('click');
	toTablePi.$('tr').off('click');
    
	fromTableUser.$('tr').click( function() {
        if ($(this).hasClass('row_selected') )
	        $(this).removeClass('row_selected');
        else
	        $(this).addClass('row_selected');
    });

	fromTablePi.$('tr').click( function() {

        if ($(this).hasClass('row_selected') )
            $(this).removeClass('row_selected');
        else
            $(this).addClass('row_selected');
    });

	toTableUser.$('tr').click( function() {
        if ($(this).hasClass('row_selected') )
            $(this).removeClass('row_selected');
        else
            $(this).addClass('row_selected');
    });

	toTablePi.$('tr').click( function() {
        if ($(this).hasClass('row_selected') )
            $(this).removeClass('row_selected');
        else
            $(this).addClass('row_selected');
    });

}

function resetForm(){


    data="";
    userType="";
    affiliation=new Array();
    newaffiliation='';
    firstname = ''; 
    lastname = ''; 
    username= ''; 
    email1 = '';  
    email2 = ''; 
    userType= ''; 
    new_name='';
    new_state='';
    new_department='';
    new_name_pi_aff='';
    new_state_pi_aff='';
    new_department_pi_aff='';
    new_pi_name='';
    new_pi_lastname='';
    new_pi_mail='';
    new_pi_name_lasuserAff='';
    new_pi_lastname_lasuserAff='';
    new_pi_mail_lasuserAff='';
    new_aff_flag=false;
    $('#affiliation').hide();
    $('#slave_div').hide();
    $('#aff_dialog').hide();
    $("#firstname").removeAttr('disabled');
    $("#lastname").removeAttr('disabled');
    $("#email1").removeAttr('disabled');
    $("#email2").removeAttr('disabled');
    $("#username").removeAttr('disabled');
    $("#userType").removeAttr('disabled');
    $("#userType").removeAttr('disabled');
    $('#confirm_button').removeAttr('disabled');
    $('#create_affiliation').removeAttr('disabled');
    $('#search_result_pi').hide()
    $('#search_result_user').hide()
}

function refreshCaptcha() {
    console.log("refresh captcha");
    $form = $("#captcha_form");
    $.getJSON($(this).data('url'), {'refreshCaptcha': true}, function(json) {
        $form.find("img.captcha").attr("src", json["new_cptch_image"]);
        $form.find("input[type='hidden']").val(json["new_cptch_key"]);
    });
    return false;
}

$(document).ready(function() {

    $('.js-captcha-refresh').click(refreshCaptcha);

    fromTableUser = $('#From_user').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }
    }).rowReordering();
    fromTablePi = $('#From_pi').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }

    }).rowReordering();
    toTablePi = $('#To_pi').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }
    }).rowReordering();
    
    toTableUser = $('#To_user').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        'iDisplayLength': 10,
        "sDom": 'T<"clear">lfrtip',
        "oTableTools": {
    		"sRowSelect": "multi",
    		"aButtons": [ "select_all", "select_none" ]
        }
    }).rowReordering();

    $('#add_user').click(function() { 
        rows=fnGetSelected(fromTableUser);
        for (i in rows){
            var addedRow=toTableUser.fnAddData(fromTableUser.fnGetData(rows[i]));
            var newNode = toTableUser.fnSettings().aoData[addedRow[0]].nTr;
            newNode.setAttribute('id',rows[i].id);
            fromTableUser.fnDeleteRow(rows[i]);
        }
        initializeSelectable();

        toTableUser.$('.infoButton').mouseenter(function () {
            value=$(this).attr('value');
            $('#affDialog').html(popupDiv[value]);
            $('#affDialog').dialog("open");        
        });
        toTableUser.$('.infoButton').mouseleave(function () {
            value=$(this).attr('value');
            $('#affDialog').dialog("close");        
        });
    });
    $('#remove_user').click(function() {
        rows=fnGetSelected(toTableUser);
        for (i in rows){
            if(rows[i].id !='new_aff'){                                    
                var removedRow=fromTableUser.fnAddData(toTableUser.fnGetData(rows[i]));
                var newNode = fromTableUser.fnSettings().aoData[removedRow[0]].nTr;
                newNode.setAttribute('id',rows[i].id);
            }
            toTableUser.fnDeleteRow(rows[i]);
            
        }
        if (toTableUser.fnGetData().length == 0){
            new_aff_flag=false;
            $('#create_affiliation').prop('disabled',false);
        }
        else{
            $('#create_affiliation').prop('disabled',true);
        }
        initializeSelectable();
    });

    $('#add_pi').click(function() {
        rows=fnGetSelected(fromTablePi);
        for (i in rows){
            var addedRow=toTablePi.fnAddData(fromTablePi.fnGetData(rows[i]));
            var newNode = toTablePi.fnSettings().aoData[addedRow[0]].nTr;
            newNode.setAttribute('id',rows[i].id);
            fromTablePi.fnDeleteRow(rows[i]);
        }
        initializeSelectable();
    });
    $('#remove_pi').click(function() {   
        rows=fnGetSelected(toTablePi);
        for (i in rows){
            if(rows[i].id !='new_aff'){                
                var removedRow=fromTablePi.fnAddData(toTablePi.fnGetData(rows[i]));
                var newNode = fromTablePi.fnSettings().aoData[removedRow[0]].nTr;
                newNode.setAttribute('id',rows[i].id);
            }
            toTablePi.fnDeleteRow(rows[i]);
            
        }
        if (toTablePi.fnGetData().length == 0){
            new_aff_flag=false;
            $('#create_affiliation').prop('disabled',false);
        }
        else{
            $('#create_affiliation').prop('disabled',true);
        }
        initializeSelectable();
    });

    $('#userType').on('change', function() {
        userType=$(this).val();
    });

    $(function() {
        var name = $( "#name" ),
        state = $( "#state" ),
        department = $( "#department" ),
        pi_name= $( "#pi_name" ),
        pi_lastname= $( "#pi_lastname" ),
        pi_email= $( "#pi_email" ),
        allFields = $( [] ).add( name ).add( state ).add( department ).add( pi_name ).add( pi_lastname ).add( pi_email ),
        tips = $( ".validateTips" );
        function updateTips( t ) {
            tips
            .text( t )
            .addClass( "ui-state-highlight" );
            setTimeout(function() {
            tips.removeClass( "ui-state-highlight", 1500 );
            }, 500 );
        }

        function checkLength( o, n, min, max ) {
            if ( o.val().length > max || o.val().length < min ) {
                o.addClass( "ui-state-error" );
                updateTips( "Length of " + n + " must be between " +
                min + " and " + max + "." );
                return false;
            } else {
                return true;
            }
        }

        function checkRegexp( o, regexp, n ) {
            if ( !( regexp.test( o.val() ) ) ) {
                o.addClass( "ui-state-error" );
                updateTips( n );
                return false;
            } else {
                return true;
            }
        }
        $( "#dialog-form-pi" ).dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                "Create a new PI": function() {
                    var bValid = true;
                    allFields.removeClass( "ui-state-error" );
                    bValid = bValid && checkLength( pi_name, "pi_name", 3, 16 );
                    bValid = bValid && checkLength( pi_lastname, "pi_lastname", 3, 16 );
                    bValid = bValid && checkLength( pi_email, "pi_email", 6, 80 );
                    bValid = bValid && checkRegexp( pi_email, /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i, "eg. name@domain.com" );
                    if ( bValid ) {
                
                        //METTERE IN DATATABLE!! O NO?
                        $('#create-affiliation').button('disable');
                        new_pi_name_lasuserAff= pi_name.val();
                        new_pi_lastname_lasuserAff= pi_lastname.val();
                        new_pi_mail_lasuserAff= pi_email.val();
                        $.ajax({
                            url:registrationUrl,
                            type: "POST",
                            data: {
                                    new_pi_name_lasuserAff:new_pi_name_lasuserAff,
                                    new_pi_lastname_lasuserAff:new_pi_lastname_lasuserAff,
                                    new_pi_mail_lasuserAff:new_pi_mail_lasuserAff,
                                    step:'check_lasuser_aff'},
                            }).done(function(data) {
                                if (data["critical_error"]=='true') {
                                    redirectToErrorPage();
                                } else
                                if (data["msg"]=='error'){
                                    alert('PI already exist!');
                                    return false;
                                }
                                else{
                                    var addId = $('#To_user').dataTable().fnAddData([new_pi_name_lasuserAff,new_pi_lastname_lasuserAff,'-','<img src="/lasauth_media/img/fail.gif"></img>']);
                                    var theNode = $('#To_user').dataTable().fnSettings().aoData[addId[0]].nTr;
                                    theNode.setAttribute('id','new_aff');
                                    new_aff_flag=true;
                                    initializeSelectable();
                                    $('#create_affiliation').prop('disabled',true);
                                    $('#search_result_user').show();
                                }
                          });
                        $( this ).dialog( "close" );
                    }
                },
                Cancel: function() {
                    $( this ).dialog( "close" );
                }
            },
            close: function() {
                allFields.val( "" ).removeClass( "ui-state-error" );
            }
        });

        $( "#dialog-form-aff" ).dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                "Create a new affiliation": function() {
                var bValid = true;
                allFields.removeClass( "ui-state-error" );
                bValid = bValid && checkLength( name, "name", 3, 16 );
                bValid = bValid && checkLength( state, "state", 3, 16 );
                bValid = bValid && checkLength( department, "department", 3, 16 );
                
                if ( bValid ) {
                    //METTERE IN DATATABLE!! O NO?
                    $('#create-affiliation').button('disable');
                    new_name_pi_aff=name.val();
                    new_state_pi_aff=state.val();
                    new_department_pi_aff=department.val();


                $.ajax({
                    url:registrationUrl,
                    type: "POST",
                    data: {
                            new_name_pi_aff:new_name_pi_aff,
                            new_state_pi_aff:new_state_pi_aff,
                            new_department_pi_aff:new_department_pi_aff,
                            step:'check_pi_aff'
                    },
                }).done(function(data) {
                    if (data["critical_error"]=='true') {
                        redirectToErrorPage();
                    } else
                    if (data["msg"]=='error'){
                        alert('Affiliation already exist!');
                        return false;
                    }
                    else{
                        var addId = $('#To_pi').dataTable().fnAddData([new_name_pi_aff,new_state_pi_aff,new_department_pi_aff,'<img src="/lasauth_media/img/fail.gif"></img>']);
                        var theNode = $('#To_pi').dataTable().fnSettings().aoData[addId[0]].nTr;
                        theNode.setAttribute('id','new_aff');
                        new_aff_flag=true;
                        initializeSelectable();
                        $('#create_affiliation').prop('disabled',true);
                        $('#search_result_pi').show()    
                    }        
                });
                    $( this ).dialog( "close" );
                }
            },
            Cancel: function() {
                $( this ).dialog( "close" );
            }
            },
            close: function() {
                allFields.val( "" ).removeClass( "ui-state-error" );
            }
        });
    });

    $('#affiliation').hide();
    $('#search_result_pi').hide();
    $('#search_result_user').hide();
    $( "#affDialog" ).dialog();
    $('#affDialog').dialog("close");
    $('#main_div').css('display','block');

       
});

function newAff(){
    if (userType=='pi')
        $( "#dialog-form-aff" ).dialog( "open" );
    else
        $( "#dialog-form-pi" ).dialog( "open" );
}

function showSlaveDiv(){
    var new_name='';
    var new_state='';
    var new_department='';
    var new_pi_name='';
    var new_pi_lastname='';
    var new_pi_mail='';

    $('#affDialog').dialog("close");
    firstname = $('#firstname').val(); 
    lastname = $('#lastname').val(); 
    username= $('#username').val(); 
    email1 = $('#email1').val();  
    email2 = $('#email2').val(); 
    userType= $('#userType').val(); 
    captcha_0 = $('#id_captcha_0').val();
    captcha_1 = $('#id_captcha_1').val();

    var usernameRegex = /^[a-zA-Z0-9.]+$/;
    var nameRegex= /^[a-zA-ZàáâäãåąćęèéêëìíîïłńòóôöõøùúûüÿýżźñçčšžÀÁÂÄÃÅĄĆĘÈÉÊËÌÍÎÏŁŃÒÓÔÖÕØÙÚÛÜŸÝŻŹÑßÇŒÆČŠŽ∂ð ,.'-]+$/;
    var emailRe = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/igm;

    if (firstname == '' || !nameRegex.test(firstname))
    {
        alert('Please enter a valid firstname.');
        return false;
    }
    if (lastname == '' || !nameRegex.test(lastname))
    {
        alert('Please enter a valid lastname.');
        return false;
    }
    if (username == '' || !usernameRegex.test(username))
    {
        alert('Please enter a valid username.');
        return false;
    }
    if (email1 == '' || !emailRe.test(email1))
    {
        alert('Please enter a valid email address.');
        return false;
    }
    if (email2 != email1)
    {
        alert("E-mail addresses don't match");
        return false;
    }
    if(userType=='nothing'){
        alert("Please select the User Type");
        return false;
    }
    // validate user data and captcha form
    $.ajax({
        url:registrationUrl,
        type: "POST",
        data: { firstname: firstname,
                lastname: lastname,
                username: username,
                email1: email1,
                email2: email2,
                userType: userType,
                step:"data_check",
                project:project,
                captcha_0: captcha_0,
                captcha_1: captcha_1
        }
    }).done(function(data) {
        if (data["critical_error"]=='true'){
            alert(data["error_string"]);
            refreshCaptcha();
            return false;
        }
        else{        
            $("#firstname").prop('disabled', true);
            $("#lastname").prop('disabled', true);
            $("#email1").prop('disabled', true);
            $("#email2").prop('disabled', true);
            $("#username").prop('disabled', true);
            $("#userType").prop('disabled', true);
            $("#userType").prop('disabled', true);
            $("#confirm_button").prop('disabled', true);
            $("#id_captcha_1").prop('disabled', true);
            $("#refresh_captcha").prop('disabled', true);

            console.log("captcha successfully verified", data["regsession"]);
            $.cookie("reg_session", data["regsession"], { path: '/' });

            if($('#userType').val()=='pi'){
                $("#pi_name_row").css("display","none");
                $("#pi_lastname_row").css("display","none");
                $("#pi_mail_row").css("display","none");
                $("#affiliation").show();           
            }
            else if($('#userType').val()=='user'){
                $("#pi_name_row").css("display","table-row");
                $("#pi_lastname_row").css("display","table-row");
                $("#pi_mail_row").css("display","table-row");
                $("#affiliation").show();        
            }
        }
    });

}

function searchAffiliation(){
    var aff_name=$('#aff_name').val(); 
    var aff_state=$('#aff_state').val(); 
    var aff_department=$('#aff_dep').val(); 
    var aff_pi_name=$('#aff_pi_name').val(); 
    var aff_pi_lastname=$('#aff_pi_lastname').val(); 
    var aff_pi_mail=$('#aff_pi_mail').val(); 
    var affiliations= new Array();

    clearDatatables();
    resetDatatables(); 
    if (userType=='pi'){
        $.ajax({
        url:registrationUrl,
        type: "POST",
        data: { aff_name:aff_name,
                aff_state:aff_state,
                aff_department:aff_department,
                userType: userType,
                project:project,
                step: 'search_affiliation',},
        }).done(function(data) {
            if (data["critical_error"]=='true') {
                redirectToErrorPage();
            } else

            if (data["affiliations"]=='none'){
                initializeSelectable();
                setDatatables(); 
            }
            else{
               for (aff in data["affiliations"])
                    affiliations.push(data["affiliations"][aff]);
                rows=''
                for (aff in affiliations){
                    
                    //costruire datatable con affiliazioni, che si trovano in affiliations 
                    rows += '<tr id='+affiliations[aff]['id']+'>';
                    rows += '<td>'+affiliations[aff]['name']+'</td><td>'+affiliations[aff]['state']+'</td><td>'+affiliations[aff]['department']+'</td>';
                    if(affiliations[aff]['validated']==false)
                        rows+= '<td><img src="/lasauth_media/img/fail.gif"></img></td>';
                    else
                        rows+= '<td><img src="/lasauth_media/img/ok.gif"></img></td>';
                    rows += '</tr>';    
               }                
                $('#From_pi tbody').html(rows);

                setDatatables();   
                if(new_aff_flag == true){
                    var addId = $('#To_pi').dataTable().fnAddData([new_name_pi_aff,new_state_pi_aff,new_department_pi_aff,'<img src="/lasauth_media/img/fail.gif"></img>']);
                    var theNode = $('#To_pi').dataTable().fnSettings().aoData[addId[0]].nTr;
                    theNode.setAttribute('id','new_aff');
                    
                }
                initializeSelectable();
            }
            $('#search_result_pi').show()
        });
    }
    else{
        $.ajax({
        url:registrationUrl,
        type: "POST",
        data: { aff_name:aff_name,
                aff_state:aff_state,
                aff_department:aff_department,
                aff_pi_name:aff_pi_name,
                aff_pi_lastname:aff_pi_lastname,
                aff_pi_mail:aff_pi_mail,
                userType: userType,
		project:project,
                step: 'search_affiliation',},
        }).done(function(data) {        
            if (data["critical_error"]=='true') {
                redirectToErrorPage();
            } else

            if (data["affiliations"]=='none'){
                initializeSelectable();
                setDatatables();                 
            }
            else{
                for (aff in data["affiliations"])
                    affiliations.push(data["affiliations"][aff]);
                rows=''
                for (aff in affiliations){
                        id="button"+affiliations[aff]['id'];
                        rows += '<tr id='+affiliations[aff]['id']+'>';
                        rows += '<td>'+affiliations[aff]['firstname']+'</td><td>'+affiliations[aff]['lastname']+'</td>';
                        rows +='<td><button class="button infoButton" value='+affiliations[aff]['id']+' id="button'+affiliations[aff]['id']+'">INFO</button></td>';                           
                        rows+= '<td><img src="/lasauth_media/img/ok.gif"></img></td>';
                        rows += '</tr>'; 
                        popup="";
                        var i=1;
                        for(item in affiliations[aff]['affiliations']){
                            popup+=i+")&nbsp;";
                            popup+=affiliations[aff]['affiliations'][item]['name'];
                            popup+=",&nbsp;"+affiliations[aff]['affiliations'][item]['state'];
                            popup+=",&nbsp;"+affiliations[aff]['affiliations'][item]['department'];
                            popup+='<br>';
                            i=i+1;
                        }
                        popupDiv[affiliations[aff]['id']]=popup;  
                        $( '#button'+affiliations[aff]['id']).click(function() {
                            $('#affDialog').html(affiliations[aff]['id']);
                            $('#affDialog').dialog("open");
                        });                          
                              
               }       
               $('#From_user tbody').html(rows);
               setDatatables();   
               if(new_aff_flag == true){
                   var addId = $('#To_user').dataTable().fnAddData([new_pi_name_lasuserAff,new_pi_lastname_lasuserAff,'-','<img src="/lasauth_media/img/fail.gif"></img>']);
                   var theNode = $('#To_user').dataTable().fnSettings().aoData[addId[0]].nTr;
                   theNode.setAttribute('id','new_aff');
               }
               initializeSelectable();
            }
            fromTableUser.$('.infoButton').mouseenter(function () {
                value=$(this).attr('value');
                $('#affDialog').html(popupDiv[value]);
                $('#affDialog').dialog("open");        
            });
            fromTableUser.$('.infoButton').mouseleave(function () {
                value=$(this).attr('value');
                $('#affDialog').dialog("close");        
            });
            $('#search_result_user').show()           
        });
    }
}

function showPopup(id){
    $('#affDialog').html(popupDiv[id]);
    $('#affDialog').dialog("open");

}

function secondStepDiv(){
    if (userType=='pi'){
        var rows = toTablePi.fnGetNodes();
        new_name=new_name_pi_aff;
        new_state=new_state_pi_aff;
        new_department=new_department_pi_aff;
        }
    else{
        var rows = toTableUser.fnGetNodes();
        new_pi_name=new_pi_name_lasuserAff;    
        new_pi_lastname=new_pi_lastname_lasuserAff;
        new_pi_mail=new_pi_mail_lasuserAff;
    }
    if (rows==''){
        alert("Please select at least one affiliation!");
        return false;
    }
    else{
        affiliation=new Array();
        for(var i=0;i<rows.length;i++)        
            affiliation.push($(rows[i]).attr('id'));
    }
    $.ajax({
        url:registrationUrl,
        type: "POST",
        data: { firstname: firstname,
                project: project,
                lastname: lastname,
                username: username,
                email1: email1,
                email2: email2,
                userType: userType,
                affiliation:affiliation,
                new_name:new_name,
                new_state:new_state,
                new_department:new_department,
                new_pi_name:new_pi_name,
                new_pi_lastname:new_pi_lastname,
                new_pi_mail:new_pi_mail,
                new_aff_flag:new_aff_flag,
                step:'phase_two'
    },
    }).done(function(data) {
        if (data["critical_error"]=='true') {
            redirectToErrorPage();
        } else {
            $("#slave_div").html(data)
        }
    });

    //MEMORIZZO IN SESSIONE INFO UTILI, SCRIVERE SUPERVISORI, PASSARE ALLA FASE 2
    if($('#userType').val()=='pi'){
        $("#main_div").slideToggle("slow");
        $("#affiliation").slideToggle("slow");
        $('#usernameLabelPI').html("username: "+ username);
        $("#slave_div").show();
    }
    else if($('#userType').val()=='user'){
        $("#main_div").slideToggle("slow");
        $("#affiliation").slideToggle("slow");
        $('#usernameLabelLAS').html("username: "+ username);
        $("#slave_div").show();
    }
    $('#wg_name').val(username+"_WG");

}

function register(){

    if (userType=='pi'){
        var activities =new Array();
        $("input[type='checkbox']:checked").each(
            function() {
                var className = $(this).attr('class');
                if (className != 'checkCategory')
                    activities.push($(this).attr('id'));
            }
        );
        if($('#wg_name').val() ==''){
            alert ('Please insert a valid Working Group Name');
            return false;
        }
        if (activities.length == 0){
            alert ('Please insert at least one activity');
            return false;
        }        
        if (activities.length == 0){
            alert("You have to choose at least one activity!");
            return false;
        }
        var c=true;
        if ((new_aff_flag)||(invalid_flag)){
            c=confirm("YOU HAVE SELECTED AT LEAST ONE NON-VALIDATED AFFILIATION.\n THIS AFFILIATION WILL BE CHECKED FROM LAS MANAGER\n Do you want to continue?")
        }
        if (c==true){
            startLag();
            alert(project);
            $.ajax({
                url:registrationUrl,
                type: "POST",
                data: { firstname: firstname,
                        lastname: lastname,
                        username: username,
                        email1: email1,
                        email2: email2,
                        userType: userType,
                        affiliation:affiliation,
                        activities:activities,
                        new_aff_name:new_name_pi_aff,
                        new_aff_state:new_state_pi_aff,
                        new_aff_department:new_department_pi_aff,
                        step:'register',
			project:project,
                        wgName:$('#wg_name').val(),
                        },
            }).done(function(data) {
                endLag();
                if (data["critical_error"]=='true') {
                    redirectToErrorPage();
                } else

                if (data['result']=='ok')
                    window.location.href = completeUrl;
                else if (data['result']=='duplicate'){
                    endLag();
                    alert('Working Group already exist! Please change the name.');
                    return false;
                }
                else{
                    alert ('General error!Please retry later.');
                    return false;
                }
            });
        }
        else 
            return false;
    }
    else{
        var c=true;            
        if (new_aff_flag==true){
            c=confirm("YOUR SUPERVISOR IS NOT YET VALIDATED!\nYOUR REQUEST WILL BE EVALUATED ONLY IF THE SUPERVISOR WILL JOIN LAS WITHIN 7 DAYS\n Do you want to continue?")
        }
        for (id in roles){
            if (roles[id].length==0){
                alert("You have to choose at least one role for each PI!");
                    return false;
            }   
            if ((affiliationArray[id].length==0) && (id!=0)){
                alert("You have to choose at least one affiliation for each validated PI!");
                    return false;
            }   
        }
        if (c==true){
            startLag();
            $.ajax({
                url:registrationUrl,
                type: "POST",
                data: { firstname: firstname,
                        lastname: lastname,
                        username: username,
                        email1: email1,
                        email2: email2,
                        userType: userType,
                        roles:roles,
                        new_pi_name:new_pi_name,
                        new_pi_lastname:new_pi_lastname,
                        new_pi_mail:new_pi_mail,
                        supervisors:supervisorsArray,
                        affiliations:affiliationArray,
                        step:'register',
                        project:project,
                        },
            }).done(function(data) {
                endLag();
                if (data["critical_error"]=='true') {
                    redirectToErrorPage();
                } else

                if (data['result']=='ok'){
                    window.location.href = completeUrl;
                }
                else{
                    alert ('Error in registration!Please retry later or contact administrator.');
                    window.location.href = indexUrl;
                }
            });
        }
    }
}




function demoRegister(){
    var new_name='';
    var new_state='';
    var new_department='';
    var new_pi_name='';
    var new_pi_lastname='';
    var new_pi_mail='';

    $('#affDialog').dialog("close");
    firstname = $('#firstname').val();
    lastname = $('#lastname').val();
    username= $('#username').val();
    email1 = $('#email1').val();
    email2 = $('#email2').val();
    userType='pi';
    var usernameRegex = /^[a-zA-Z0-9.]+$/;
    var nameRegex= /^[a-zA-ZàáâäãåąćęèéêëìíîïłńòóôöõøùúûüÿýżźñçčšžÀÁÂÄÃÅĄĆĘÈÉÊËÌÍÎÏŁŃÒÓÔÖÕØÙÚÛÜŸÝŻŹÑßÇŒÆČŠŽ∂ð ,.'-]+$/;
    var emailRe = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/igm;

    if (firstname == '' || !nameRegex.test(firstname))
    {
        alert('Please enter a valid firstname.');
        return false;
    }
    if (lastname == '' || !nameRegex.test(lastname))
    {
        alert('Please enter a valid lastname.');
        return false;
    }
    if (username == '' || !usernameRegex.test(username))
    {
        alert('Please enter a valid username.');
        return false;
    }
    if (email1 == '' || !emailRe.test(email1))
    {
        alert('Please enter a valid email address.');
        return false;
    }
    if (email2 != email1)
    {
        alert("E-mail addresses don't match");
        return false;
    }
    if(userType=='nothing'){
        alert("Please select the User Type");
        return false;
    }
    $.ajax({
        url:registrationUrl,
        type: "POST",
        data: { firstname: firstname,
                lastname: lastname,
                username: username,
                email1: email1,
                email2: email2,
                userType: userType,
                step:"data_check",
                project:project,
    },
    }).done(function(data) {
        if (data["error"]=='true'){
            alert(data["error_string"]);
            return false;
        }
        else{
            startLag();
            $.ajax({
                url:registrationUrl,
                type: "POST",
                data: { firstname: firstname,
                        lastname: lastname,
                        username: username,
                        email1: email1,
                        email2: email2,
                        userType: userType,
                        step:'demo_register',
                        },
            }).done(function(data) {
                endLag();
                if (data['result']=='end'){
                    window.location.href = completeUrl;
                }
                else{
                    alert ('Error in registration!Please retry later or contact administrator.');
                    window.location.href = indexUrl;
                }
            });
        }
    });
}

function redirectToErrorPage() {
    window.location.replace(errorUrl);
}