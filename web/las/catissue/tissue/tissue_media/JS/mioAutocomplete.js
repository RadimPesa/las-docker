$(document).ready(function () {
/*$("#id_hospital").autocomplete({
	source:'/tissue/ajax/hospital/autocomplete/'
});
$("#id_address").autocomplete({
		source:["bbbb","bgfgf","bnj"]
	});*/
$("#id_aliquot").autocomplete({
	source:base_url+'/ajax/revalue/autocomplete/'
});
});