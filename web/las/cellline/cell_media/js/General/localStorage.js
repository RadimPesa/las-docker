// Funzioni per gestire il local storage

function clearData(key) {
	localStorage.removeItem(key);
}
				
function restoreData(key) {
	return localStorage.getItem(key);
}
							
/*function storageData(key,value) {
	localStorage.setItem(key,value);
}

function clearAllData_ProtocolManager() {
	clearData('name_new_protocol');
	clearData('file_name');
	clearData('description');
	clearData('group1');
	clearData('group2');
	clearData("plate_name");
	clearData("plate_number");
}

function clearAllData_GenerationAliquots() {
	// Generation
	clearData('name_new_protocol_generation');
	clearData('protocol_name_list_al');
	clearData('protocol_type_list_al');
	clearData('cell_line_gen_ID');
}

function clearAllData_GenerationCellLines() {
	// Generation
	clearData('name_new_protocol_generation_cl');
	clearData('protocol_name_list_cl');
	clearData('protocol_type_list_cl');
}

function clearAllData_Expansion() {
	clearData('dizionario_expansion');
	clearData('dizionario_protocol_expansion');
	clearData('dizionario_plate_expansion');
	clearData('dizionario_changemedia_expansion');
	clearData('dizionario_datatable_exp');
	clearData('genID_choosen');
	clearData('prot_name_id_title');
	clearData('cond_conf_choosen_id_title');
	clearData('cult_cond_exp');
	clearData('defval_exp');
	clearData('data_table_exp');
}

function clearAllData_Experiment() {
	// Experiment
}

function clearAllData_Archive() {
	// Archive
}

function clearAllData() {
	clearAllData_ProtocolManager();
	clearAllData_GenerationAliquots();	
	clearAllData_GenerationCellLines();
	clearAllData_Archive();
	clearAllData_Expansion();
	clearAllData_Experiment();
}

function clearAllData_NoExpansion() {
	clearAllData_ProtocolManager();
	clearAllData_GenerationAliquots();	
	clearAllData_GenerationCellLines();
	clearAllData_Archive();
	clearAllData_Experiment();
}*/
