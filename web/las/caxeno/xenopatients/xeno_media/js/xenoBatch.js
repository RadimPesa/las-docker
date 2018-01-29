$(document).ready(function () {
	$("#tastofile").click(function(){
		$("#id_file").click();
	});
	
	$("#id_file").change(function(){
		var files = $('#id_file')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
	});

	var option = $('#action').val();
	var template = $('#action option[value=' + option +']').attr('filetemplate');
	$('#templatefile').prop("href", template);


	$('#action').on('change', function (event){
		var option = $(this).val();
		var template = $('#action option[value=' + option +']').attr('filetemplate');
		$('#templatefile').prop("href", template);
	});

});


