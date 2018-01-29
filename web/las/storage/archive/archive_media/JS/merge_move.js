/* used prefixes in plates */
/* s_: selected plate */
/* g_: merge plate */
/* mp_: mini plate */

/* globals */
var selected_phase = "-"; /* selected phase */
var selected_plate = "-"; /* selected plate */
var bi = "-";             /* initial button */
var bf = "-";             /* final button */
var flag = "-";           /* status flag */

/* tubes movements behaviour */
function move(el, plate){
	//se sto facendo il drag and drop non devo far scattare questa funzione legata
	//all'evento onclick
	if(drag==false){
	    /* if click is on top plate */
	    if ( plate == "top"){
	        /* have I clicked on something empty? */
	        if (el.getAttribute("assign") != "-"){
	            /* if I haven t placed that before */
	            if (el.getAttribute("c") != "tube_placed"){
	                /* if this is the first click at all */
	                if (flag == "-"){
	                    /* save initial and final coordinates */
	                    set_coord(el, el.id, el.id, "top");
	                }
	                /* if this is the second click on top */
	                else if (flag == "top"){
	                    /* ...and this click is on top again*/
	                    /* save final coordinates */
	                    set_coord(el, "null", el.id, "top2d");
	                }
	                /* if this is the third click on top... */
	                /* ...or I have clicked after a bot click */
	                else if ((flag == "top2d") || (flag == "bot")){
	                    /* ...reset coordinates */
	                    set_coord(el, "-", "-", "-");
	                }
	            }
	            else{
	                /* reset */
	                set_coord(el, "-", "-", "-");
	            }
	        }
	        else{
	            /* reset */
	            set_coord(el, "-", "-", "-");
	        }
	    }
	    /* if click is on bottom plate */
	    else{
	        /* have I clicked on something empty? */
	        if (el.getAttribute("assign") == "-"){
	            /* if this is the first click at all */
	            if (flag != "-"){
	                /* create the list of tubes to move, then test the destination area */
	                var src_list = create_src_list();
	                if (src_list != null){
	                    var dest_list = create_dest_list(el, src_list);
	                    if (dest_list != null){
	                        /* if this is the second click on bot */
	                        if (flag == "bot" || flag == "bot2d"){
	                            /* I want to move 1 tube within the bot plate */
	                            move_bottom(el, src_list, dest_list);
	                        }
	                        /* if this is after 1/2 click on top */
	                        else if (flag == "top" || flag == "top2d"){
	                            /* I want to move 1 tube from top to bot */
	                            /* save info in plates */
	                            save_bottom(el, src_list, dest_list);
	                            //save_top(el, src_list);
	                            //save_mini(el, src_list);
	                        }
	                    }
	                }
	            }
	            /* after placing -or not-, reset vars */
	            set_coord(el, "-", "-", "-");
	        }
	        /* if I have clicked on a tube */
	        else{
	            /* if this is the first click on bot */
	            if (flag == "-"){
	                /* I save the coordinates of the tube */
	                set_coord(el, el.parentNode.id, el.parentNode.id, "bot");
	            }
	            /* if this is the second click on bot */
	            else if (flag == "bot"){
	                /* I save the coordinates of the area */
	                set_coord(el, "null", el.parentNode.id, "bot2d");
	            }
	            /* if this is the third click on bot */
	            else if (flag == "bot2d"){
	                /* reset */
	                set_coord(el, "-", "-", "-");
	            }
	        }
	    }
	}
	else{
		drag=false;
	}
    //document.getElementById("plate_Description").focus();
}    
    
/* save the coordinates of pressed buttons */
function set_coord(el, set_bi, set_bf, set_flag){

    var rev = false;
    
    if (set_bi != "null"){
        bi = set_bi;
    }
    bf = set_bf;
    flag = set_flag;

    /* REVERSE SELECTION TEST */
    if (set_bi == "null"){
        var plate = bf.split("-")[0];
        pur_bi = bi.split("-")[1];
        pur_bf = bf.split("-")[1];
        irow = pur_bi.substr(0,1);
        icol = pur_bi.substr(1);
        frow = pur_bf.substr(0,1);
        fcol = pur_bf.substr(1);
        
        /* test and reverse */
        var tmp;
        if (frow < irow){
            rev = true;
            tmp = frow;
            frow = irow;
            irow = tmp;
        }
        if (parseInt(fcol) < parseInt(icol)){
            rev = true;
            tmp = fcol;
            fcol = icol;
            icol = tmp;
        }
        if (rev){
            bi = plate+"-"+irow+icol;
            bf = plate+"-"+frow+fcol;
        }
    }
    //write();

    if (flag!="-"){
        highlight(create_src_list());
    }
    else{
    	unhighlight();
    }
}

/* unselect all buttons */
function unhighlight(){    
    /* retrieve button list */
    //var s_buttons = document.getElementById("selPlate").getElementsByTagName("button");
    //var m_buttons = document.getElementById("mergedPlate").getElementsByTagName("button");
	var s_buttons=$("#operativa table div");
	var m_buttons=$("#freezer table div");
    /* return back plates to unselection */
    var i;
    for (i=0; i<s_buttons.length; i++){
        var previous = s_buttons[i].getAttribute("prev");
        s_buttons[i].setAttribute("c", previous);
    }
    for (i=0; i<m_buttons.length; i++){
        var previous = m_buttons[i].getAttribute("prev");
        m_buttons[i].setAttribute("c", previous);
    }
}

function highlight(src_list){
	//per lo spostamento in una sola piastra
	var una=$("#modo").attr("value");

	if(tipo=='SF'){
    	var plate = "s-";
    }
    else if(tipo=='VT'){
    	var plate = "v-";
    }
    else{
    	var plate = "r-";
    }
    if (flag=='bot' || flag=='bot2d'){
    	if (una=="True"){
        	plate="a-";
        }
        else{
        	plate = "m-";
        }
    }
    var src="";
    if(src_list!=null){
	    for (i=2; i<src_list.length; i++){
	    	if(plate=="m-"){ 
	    		src = document.getElementById(plate+src_list[i]).childNodes[0];
	    	}
	    	else if(plate=="a-"){ 
	    		var lun=document.getElementById(plate+src_list[i]).childNodes.length;
	    		if(lun==1){
	    			src = document.getElementById(plate+src_list[i]).childNodes[0];
	    		}
	    		else{
	    			src = document.getElementById(plate+src_list[i]).childNodes[1];
	    		}
	    	}
	    	else{
	    		src = document.getElementById(plate+src_list[i]);
	    	}
	        var cl = src.getAttribute("c");
	        if (cl != "pb_highlight" && cl !="tube_placed"){
	            src.setAttribute("prev", cl);
	            src.setAttribute("c", "pb_highlight");
	        }
	    }
    }
    else{
    	unhighlight();
    }
}

/* save info and color the plate, searching in the list */
function save_bottom(el, src_list, dest_list){
	
    /* retrieve positioning area in bottom plate */
    var orizz = src_list[0];
    var vert = src_list[1];
    
    if(tipo=='SF'){
    	var plate = "s-";
    }
    else if(tipo=='VT'){
    	var plate = "v-";
    }
    else{
    	var plate = "r-";
    }

    /* remember: the first two elements in this list are the area dimension */
    var list_len = src_list.length;
    var i;
    var stringa_sorg="";
    var stringa_dest="";
    var barcodedest=$("#barcode_freezer").val();
	var barcodesorg=$("#barcode_operative").val();
    for (i=2; i<list_len; i++){
        var src = document.getElementById(plate+src_list[i]);
        var dest = document.getElementById("m-"+dest_list[i]);
        
        sorg=$("#"+plate+src_list[i]);
        de=$("#m-"+dest_list[i]);
        var num=$(sorg).attr("num");
		var bar=$(sorg).attr("barcode");
		var geneal=$(sorg).attr("gen");
		var id=$(sorg).attr("id");
		var pezzi=$(sorg).text();
		
        $(de).children().remove();
        $(de).append($(sorg));
        $(de).attr("class","mark");
        $(de).children().attr("c","plateButtonOFF");
        $(de).children().attr("onclick","move(this,\"bot\")");
        
        if (src.getAttribute("c") == "plateButtonON"){
            dest.childNodes[0].setAttribute("assign", src.getAttribute("assign"));
            dest.childNodes[0].setAttribute("c", "plateButtonON");
            dest.childNodes[0].setAttribute("prev", "plateButtonON");

        }
		
		
		//salvo nella mappa gli spostamenti effettuati su quelle piastre
        var vett_stored=mappa[barcodedest];
		vett_stored[bar]=dest_list[i]+"|"+barcodedest+"|"+bar+"|"+geneal+"|"+pezzi+"|"+id;
		mappa[barcodedest]=vett_stored;
		
		var vett_op=mappa[barcodesorg];
		vett_op[num]=num+"|"+barcodesorg;
		mappa[barcodesorg]=vett_op;
		
		//preparo le stringhe da inviare alla vista
		stringa_sorg+=src_list[i]+"_";
		stringa_dest+=dest_list[i]+"_";
    }

    var data = {
    		multiplo:true,
    		strsorg:stringa_sorg,
    		strdest:stringa_dest,
    		barcodesorg:$("#barcode_operative").val(),
    		barcodedest:$("#barcode_freezer").val(),
    		ti:tipo,
    };
	var url=base_url+"/move/save/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    });
	//abilito il tasto per confermare
	$("#p_confirm").attr("disabled",false);
}

function move_bottom(el, src_list, dest_list){
	var tipo=$("#tipo").val();
	var i;
    var stringa_sorg="";
    var stringa_sorg_pias_dest="";
    var stringa_dest="";
    var barcodedest=$("#barcode_freezer").val();
    var barcode_sorg=$("#barcode_operative").val();
    //per lo spostamento in una sola piastra
	var una=$("#modo").attr("value");
	
	var piastra="";
	if(una=="True"){
		piastra="a-";
	}
	else{
		piastra="m-";
	}
    for (i=2; i<src_list.length; i++){
        var src = document.getElementById(piastra+src_list[i]);
        var dest = document.getElementById(piastra+dest_list[i]);

        sorg=$("#"+piastra+src_list[i]).children();
        de=$("#"+piastra+dest_list[i]);
        var num=$(sorg).attr("num");
		var bar=$(sorg).attr("barcode");
		var geneal=$(sorg).attr("gen");
		var pezzi=$(sorg).text();
		
		//preparo le stringhe da inviare alla vista
		//visto che sono nella piastra di destinazione, devo prendere l'id del tasto
		//per avere la posizione originaria e non posso basarmi sulla src_list
		var al=$(sorg).attr("id");
		s=al.split("-");
		stringa_sorg+=s[1]+"_";
		
		stringa_sorg_pias_dest+=src_list[i]+"_";
		stringa_dest+=dest_list[i]+"_";

        $(de).children().remove();
        $(de).append($(sorg));
        $(de).attr("class","mark");
        $(de).children().attr("c","plateButtonOFF");
        $(de).children().attr("onclick","move(this,\"bot\")");
        
        $("#"+piastra+src_list[i]).removeAttr("class");

        if (tipo=="VT"){
			src.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>0</button>";
		}
		else{
			src.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>X</button>";
		}
        
        if(una!="True"){
        	//salvo nella mappa gli spostamenti effettuati su quella piastra
        	var vett_stored=mappa[barcodedest];
			vett_stored[bar]=dest_list[i]+"|"+barcodedest+"|"+bar+"|"+geneal+"|"+pezzi+"|"+al;
			mappa[barcodedest]=vett_stored;
        }
        else{
        	var vett_op=mappa[barcode_sorg];
			vett_op[num]=num+"|"+barcode_sorg+"|"+bar+"|"+geneal+"|"+pezzi+"|"+dest_list[i]+"|"+al;
			mappa[barcode_sorg]=vett_op;
			barcodedest=barcode_sorg;
        }
    }
    var data = {
    		multiplo:true,
    		stored:true,
    		strsorg:stringa_sorg,
    		strsorg2:stringa_sorg_pias_dest,
    		strdest:stringa_dest,
    		barcodesorg:barcode_sorg,
    		barcodedest:barcodedest,
    		ti:tipo
    };
	var url=base_url+"/move/save/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    });
	//abilito il tasto per confermare
	$("#p_confirm").attr("disabled",false);
}

/* create the list of buttons to move */
function create_src_list(){

	var list = [];
    var x=new Array();
    var y=new Array();
    for(i=0;i<26;i++){
    	x[i]=i+1;
    	y[i]=ascii_value("A")+i;
    }
    
    //var x = [1,2,3,4,5,6,7,8,9,10,11,12,13];
    //var y = ["A","B","C","D","E","F","G","H"];
    var i = 0;
    var j = 0;
    var k = 2;
    
    //per lo spostamento in una sola piastra
	var una=$("#modo").attr("value");
    var plate="";
    if(tipo=='SF'){
    	plate = "s-";
    }
    else if(tipo=='VT'){
    	plate = "v-";
    }
    else{
    	plate = "r-";
    }
    
    var pur_bi = bi.split("-")[1];
    var pur_bf = bf.split("-")[1];
    
    var irow_ascii = pur_bi.substr(0,1);
    var icol = pur_bi.substr(1);
    var frow_ascii = pur_bf.substr(0,1);
    var fcol = pur_bf.substr(1);
    
    var frow = ascii_value(frow_ascii);
    var irow = ascii_value(irow_ascii);
    var a_char = ascii_value("A");
    var orizz = fcol - icol + 1;
    var vert = frow - irow + 1;
    /* the first two vars are the area dimension */
    list[0] = orizz;
    list[1] = vert;
    var off_i = irow - a_char;
    var off_j = icol - 1;
    /* fill the list */
    for (i=0; i<vert; i++){
        for (j=0; j<orizz; j++){
        	//fromCharCode trasforma da ascii a carattere
            list[k] = String.fromCharCode(y[i+off_i]) + x[j+off_j];

            /* AREA TESTS */
            /* if there's a tube already moved in merge plate, stop everything */
            if (flag=='bot' || flag=='bot2d'){
                if (una=="True"){
                	plate="a-";
                }
                else{
                	plate = "m-";
                }
                var gen=$("#"+plate+list[k]).children().attr("gen");
            }
            else{
            	var gen=$("#"+plate+list[k]).attr("gen");
            }

            if (gen==undefined){
            	return null;
            }
            /*if (document.getElementById(plate+list[k]).getAttribute("class") == "tube_placed"){
                return null;
            }*/  
            
            k=k+1;
        }
    }
    
    return list;
}

/* create the list of buttons chosen as destination */
function create_dest_list(el, src_list){
    var list = [];
    var x=new Array();
    var y=new Array();
    for(i=0;i<26;i++){
    	x[i]=i+1;
    	y[i]=ascii_value("A")+i;
    }
    //var x = [1,2,3,4,5,6,7,8,9,10,11,12,13];
    //var y = ["A","B","C","D","E","F","G","H"];
    var k = 2;
    
    var orizz = src_list[0];
    var vert = src_list[1];
    
    //per lo spostamento in una sola piastra
	var una=$("#modo").attr("value");
	if (una=="True"){
    	var plate="a-";
    }
    else{
    	var plate = "m-";
    }
	
    var pur_bi = el.parentNode.id.split("-")[1];
    var irow_ascii = pur_bi.substr(0,1);
    var icol = pur_bi.substr(1);
    var irow = ascii_value(irow_ascii);
    var a_char = ascii_value("A");
    var off_i = irow - a_char;
    var off_j = icol - 1;
    /* fill the list */
    for (i=0; i<vert; i++){
        for (j=0; j<orizz; j++){
        	//fromCharCode trasforma da ascii a carattere
            list[k] = String.fromCharCode(y[i+off_i]) + x[j+off_j];
            /* AREA TESTS */
            var orizzoff = src_list[0]+off_j;
            var vertoff = src_list[1]+off_i;
            /* if out of bounds, don't add */
            if (orizzoff>12 || vertoff>8){
                return null;
            }
            /* if there are already filled places, stop everything */
            if ($("#"+plate+list[k]).children().attr("assign") != "-"){
                return null;
            }           
            
            k=k+1;
        }
    }
    
    unhighlight();
    return list;
}

/* converto from ascii to number */
function ascii_value(c){
        /* restrict input to a single character */
        c = c.charAt (0);
        /* loop through all possible ASCII values */
        var i;
        for (i = 0; i < 256; ++ i){
                /* convert i into a 2-digit hex string */
                var h = i.toString (16);
                if (h.length == 1)
                        h = "0"+h;

                /* insert a % character into the string */
                h = "%"+h;
                /* determine the character represented by the escape code */
                h = unescape(h);
                /* if the characters match, we've found the ASCII value */
                if (h == c)
                        break;
        }
        return i;
}

