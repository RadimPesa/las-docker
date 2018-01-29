$(function() { 
    $(".dialog."+t).dialog({
        autoOpen: false,
        modal: true,
        width: 300,
        beforeclose: function(event, ui) {
            $(':input')
                .removeAttr('checked')
                .removeAttr('selected');
            $("select#confronto").remove();
            $("span#trattino").remove();
            $("label").remove();
            $("input#from").remove();
            $("input#to").remove();
            $("b").remove();
            $(".valuesovf br").remove();
            $("input#value").remove();
            $(".valuesovf").css('display', 'none');
            $("input#addvalue").remove();
            $("input#addnumber").remove();
            $("#add_btn").remove();
            $("p#addvalues").remove();
        }, 
        buttons: [
            {
                text: "Ok",
                click: function() {
                    {% for x in allparameters %}
                        var selected=$("#bankform input[type='radio']:checked").val();
                        if("{{x.id}}"==selected){
                            var dialog_id=$(".dialog."+t).attr("id");
                            boxdone[dialog_id]=true;
                            $("p#box"+dialog_id).append('<p class="param">{{x.name}}</p>');
                            if("{{x.userprovided}}"=="False"){
                                {% for y in allvalues %}
                                    if($('input:checkbox[value={{y.id}}]').is(':checked')){
                                        var newem = '<em id="value">{{y.value}}</em>';
                                        $(newem).appendTo("p#box"+dialog_id);
                                        $("p#box"+dialog_id).append('<p>');
                                    }
                                {% endfor %}
                            } else if("{{x.userprovided}}"=="True") {
                                if("{{x.type_id.idtype}}"==4){
                                    $("p#addvalues b").each(function(index) {
                                        var newaddval=$(this).text()
                                        $("p#box"+dialog_id).append('<em id="value">'+newaddval+'</em>');
                                        $("p#box"+dialog_id).append('<p>');
                                    });
                                }
                                if("{{x.type_id.idtype}}"==3){
                                    var confronto=$("select#confronto").val();
                                    var addnum=$("input#addnumber").val();
                                    if(confronto!="" && addnum!="")
                                        $("p#box"+dialog_id).append('<em id="value">'+confronto+addnum+'</em>');
                                    var confronto=$("select#confronto").last().val();
                                    var addnum=$("input#addnumber").last().val();
                                    if(confronto!="" && addnum!="")
                                        $("p#box"+dialog_id).append('<em id="value"> - '+confronto+addnum+'</em>');
                                }
                                if("{{x.type_id.idtype}}"==5){ //probabilita annotazione
                                    $("p#addvalues b").each(function(index) {
                                        var newaddval=$(this).text()
                                        $("p#box"+dialog_id).append('<em id="value">'+newaddval+'</em>');
                                        $("p#box"+dialog_id).append('<p>');
                                    });
                                }
                                                                            
                                if("{{x.type_id.idtype}}"==2){
                                    var confrontodata=$("select#confrontodata").val();
                                    var confrontodata2=$("select#confrontodata").last().val();
                                    var from=$("input#from").val();
                                    var to=$("input#to").val();
                                    if(from!="")
                                        $("p#box"+dialog_id).append('<em id="value">'+confrontodata+from+'</em>');
                                    if(to!="")
                                        $("p#box"+dialog_id).append('<em id="value"> - '+confrontodata2+to+'</em>');
                                }                                                                                                               
                            }
                        }
                    {% endfor %}
                    $(':input','#bankform')
                        .not(':button, :submit, :reset, :hidden')
                        .removeAttr('checked')
                        .removeAttr('selected');
                    $("select#confronto").remove();
                    $("span#trattino").remove();
                    $("label").remove();
                    $("input#from").remove();
                    $("input#to").remove();
                    $("b").remove();
                    $(".valuesovf br").remove();
                    $("p#addvalues").remove();
                    $("#add_btn").remove();
                    $("input#addvalue").remove();
                    $("input#addnumber").remove();
                    $("input#value").remove();
                    $(".valuesovf").css('display','none');                                                                          
                    $(this).dialog("close");                                                                                         
                }
            }
        ] 
    });
});
                