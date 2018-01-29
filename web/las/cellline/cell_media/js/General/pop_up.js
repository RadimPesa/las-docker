// Funzione per visualizzare una finestra modale
// Caso Generico
function pop_up(str) {
	document.getElementById("dialog_p").innerHTML = str;
	jQuery("#dialog").dialog( {
		resizable: false,
		height:200,
		width:340,
		modal: true,
		draggable: false,
		buttons: {
			"Ok": function() {
				jQuery(this).dialog("close");
			}
		}
	});
}

// Funzione per visualizzare una finestra modale
// Caso della BioBanca (Aliquot Generation)
function pop_up_biobank_aliq(str,end_way) {
	document.getElementById("dialog_p").innerHTML = str;
	jQuery("#dialog").dialog( {
		resizable: false,
		height:200,
		width:340,
		modal: true,
		draggable :false,
		buttons: {
			"Ok": function() {
				jQuery(this).dialog("close");
				if (end_way=="ok") {
					salva_dati_generation_aliquots_2();
				}
			}
		}
	});
}

// Funzione per visualizzare una finestra modale
// Caso della BioBanca (Cell Line Generation)
function pop_up_biobank_cell(str,end_way) {
	document.getElementById("dialog_p").innerHTML = str;
	jQuery("#dialog").dialog( {
		resizable: false,
		height:200,
		width:340,
		modal: true,
		draggable :false,
		buttons: {
			"Ok": function() {
				jQuery(this).dialog("close");
				if (end_way=="ok") {
					salva_dati_generation_cell_line_2();
				}
			}
		}
	});
}

// Funzione per visualizzare una finestra modale
// Caso della BioBanca (Cell Line Archive)
function pop_up_biobank_archive(str,end_way) {
	document.getElementById("dialog_p").innerHTML = str;
	jQuery("#dialog").dialog( {
		resizable: false,
		height:200,
		width:340,
		modal: true,
		draggable :false,
		buttons: {
			"Ok": function() {
				jQuery(this).dialog("close");
				if (end_way=="ok") {
					salva_dati_archive_2();
				}
			}
		}
	});
}
