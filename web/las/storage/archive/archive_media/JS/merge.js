/* globals */
var selected_phase = "-"; /* selected phase */
var selected_plate = "-"; /* selected plate */
var bi = "-";             /* initial button */
var bf = "-";             /* final button */
var flag = "-";           /* status flag */


/* tubes movements behaviour */
function move(el, plate){
	tasto_sel_sorg=el.getAttribute("barcode");
	pos_multiplo=false;
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
	                var src_list = create_src_list(el);
	                if (src_list != null){
	                    var dest_list = create_dest_list(el, src_list);
	                    if (dest_list != null){
	                        /* if this is the second click on bot */
	                        //if (flag == "bot" || flag == "bot2d"){
	                            /* I want to move 1 tube within the bot plate */
	                            //move_bottom(el, src_list, dest_list);
	                        //}
	                        /* if this is after 1/2 click on top */
	                        if (flag == "top" || flag == "top2d"){
	                            /* I want to move 1 tube from top to bot */
	                            /* save info in plates */
	                            save_bottom(el, src_list, dest_list,true);
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
		tasto_sel_sorg="";
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
        
        var irow=parseInt($("#"+bi).attr("row"));
    	var frow=parseInt($("#"+bf).attr("row"));
    	var icol=parseInt($("#"+bi).attr("col"));
    	var fcol=parseInt($("#"+bf).attr("col"));
        /* test and reverse */
        var tmp;
        if (parseInt(frow) < parseInt(irow)){
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
        	bi=$("div[col='"+icol+"'][row='"+irow+"']").attr("id");
        	bf=$("div[col='"+fcol+"'][row='"+frow+"']").attr("id");
            //bi = plate+"-"+irow+icol;
            //bf = plate+"-"+frow+fcol;
        }
    }
    //write();
    if (flag!="-"){
        highlight(create_src_list(el));
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
    tasto_sel_sorg="";
}

function highlight(src_list){
    if(src_list!=null){
	    for (i=2; i<src_list.length; i++){
	    	var src = document.getElementById(src_list[i]);
	    	
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

function controlla_coerenza_spostamenti(src_list, dest_list){
	for (var i=2; i<src_list.length; i++){
        var sorg=$("#"+src_list[i]);
        var de=$("#"+dest_list[i]);
        //per fare in modo che quando clicco nel cont a destra su un tasto gia' pieno
        //non mi si selezioni come se volessi fare lo zoom

        var inizio_dest=dest_list[i].split("-");
        //tipoaliq del div spostato
        var tipoaliqmossa=$(sorg).attr("tipo");
		var listatipialiqfiglio=tipoaliqmossa.split("&");
		//tipoaliq del cont in cui c'e' il td di destinazione
		if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
			//sto spostando all'interno della piastra sorgente
			var strdest=$(de).parent().parent().parent().parent().attr("tipo");
		}
		else if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
			//la dest e' il cont a destra
			var strdest=$(de).parent().parent().parent().attr("tipo");
		}
		var tipodest=strdest.split("&");
		//serve per vedere se l'insieme dei tipi aliq del cont spostato e' un sottoinsieme di quello del padre
		var ris = listatipialiqfiglio.every(function(val) { return tipodest.indexOf(val) >= 0; });

		if (!(ris)){
			return("Incompatible containers. Aliquot type they can contain is not the same.");
		}
		//devo controllare che il tipo del cont spostato sia coerente con il tipo del cont di destinazione
		var secondo=false;
		var contaliqmossa=$(sorg).attr("cont");
		if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
			//sto spostando all'interno della piastra sorgente
			var strdest=$(de).parent().parent().parent().parent().attr("cont");
			var itspadre=$(de).parent().parent().parent().parent().attr("itself");
		}
		else if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
			//la dest e' il cont a destra
			var strdest=$(de).parent().parent().parent().attr("cont");
			var itspadre=$(de).parent().parent().parent().attr("itself");
		}
		
		//se sia il padre che il figlio hanno l'attr itself, allora va bene, perche'
		//sono nel caso in cui ho spostato il cont singolo in visuale itself e sto cercando 
		//di rimetterlo al suo posto originale
		var itsfiglio=$(sorg).attr("itself");
		if((itspadre!=undefined)&&(itsfiglio!=undefined)){
			secondo=true;
		}
		//se sono nel caso in cui sto rimettendo un blocchetto di FF al suo posto nella visualizzazione lista
		//vedo se i barc della td e del cont coincidono e se si' lo lascio fare
		if(tipospost=="list"){
			var barccella=$(de).parent().attr("barcode");
			var barcfiglio=$(sorg).attr("barcode");			
			if((barccella!=undefined)&&(barccella==barcfiglio)){
				secondo=true;
			}
		}		
		for (var j=0;j<lisrapporti.length;j++){
			if (lisrapporti[j].figlio==contaliqmossa){
				if (lisrapporti[j].padre==strdest){
					secondo=true;
					break;
				}
			}
		}
		
		var classitasto=$(sorg).attr("class");
		//se e' un'aliquota
		if((classitasto!=undefined)&&(classitasto.indexOf("aliqclass")>-1)){
			secondo=controlla_rapporti_aliq_merge(de);
		}
		
		if (!(secondo)){
			return("Incompatible containers. Destination container type cannot contain container you want to move");
		}		
	}
	return("ok");
}

//per vedere se nel posto di dest possa starci un'aliquota
function controlla_rapporti_aliq_merge(de){
	var id=$(de).attr("id");
	if((id[0]=="r")||(id[0]=="b")){
		var aliq=$(de).parent().attr("aliq");
	}
	else if((id[0]=="m")||(id[0]=="o")){
		var aliq=$(de).attr("aliq");
	}
	if(aliq=="True"){
		return true;
	}
	return false;
}

//per contare il numero di cont gia' presenti in una posizione
function conta_figli_merge(figli,sorg){
	var numfigli=0;
	for(var i=0;i<figli.length;i++){
		var tag=$(figli[i]).prop("tagName");
		if((tag=="DIV")||(tag=="BUTTON")){
			var testo=$(figli[i]).text();
			//per capire se e' un numero o una stringa. Ad es. nel caso del #
			if (isNaN(testo)){
				numfigli+=1;
			}
			else{
				var testo=parseInt(testo);	
				var gen=$(figli[i]).attr("gen");
				if((testo==1)||(testo==0)){
					//devo vedere se il cont e' pieno e per capirlo guardo se ha l'attributo gen				
					if((gen!=undefined)&&(gen!="&")){
						numfigli+=1;
					}
				}
				else{
					if((gen!=undefined)&&(gen.indexOf("&")>-1)){
						//vuol dire che il tasto contiene piu' di un'aliquota e quindi il numero del tasto indica il numero di
						//aliq presenti
						numfigli+=testo;
					}
					else{
						numfigli+=1;
					}
				}
			}
		}
	}
	//devo aggiungere l'aliq che verra' spostata dopo
	var testo=parseInt($(sorg).text());
	if (isNaN(testo)){
		numfigli+=1;
	}
	else{
		var gen=$(sorg).attr("gen");
		if((gen!=undefined)&&(gen.indexOf("&")>-1)){
			//vuol dire che il tasto contiene piu' di un'aliquota e quindi il numero del tasto indica il numero di
			//aliq presenti
			numfigli+=testo;
		}
		else{
			numfigli+=1;
		}
	}
	return numfigli;
}

function esegui_spost(figli,testorif,posmax,sorg,quant,de){
	var tdsorg=$(sorg).parent();
	var id_dest=$(de).attr("id");
	var inizio_dest=id_dest.split("-");
	if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
    	//se sto spostando all'interno della stessa piastra, allora devo prendere il td,
    	//che e' il padre del de	
    	$(de).parent().append($(sorg)); 
    }
    else if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
    	$(de).append($(sorg));
    }
	
	//devo vedere se nel td dest c'e' solo un blocco con testorif. Se si' lo cancello
	//childNodes[0] e' il cont che gia' c'era.
	for(var i=0;i<figli.length;i++){
		var tag=$(figli[i]).prop("tagName");
		if((tag=="DIV")||(tag=="BUTTON")){
			var testo=$(figli[i]).text();
			var col=$(figli[i]).attr("col");
			var row=$(figli[i]).attr("row");
			
			if(testo==testorif){
				var htmlfiglio=$(figli[i])[0].outerHTML;
				$(figli[i]).remove();
			}
			break;
		}
	}				
	if(posmax=="1"){					
		//metto class=mark nella td di dest cosi' non posso mettere altri tasti li'
		$(de).addClass("mark");																			
	}	

	//nella cella di partenza devo fare questo solo se non c'e' niente altro, altrimenti non tocco niente
	var figlipartenza=$(tdsorg).children();
	var conta=0;
	for(var i=0;i<figlipartenza.length;i++){
		var tag=$(figlipartenza[i]).prop("tagName");
		if((tag=="DIV")||(tag=="BUTTON")){
			conta+=1;
			break
		}
	}
	if(conta==0){
		//imposto nel div spostato il giusto valore di righe e colonne
		var colvecchia=$(sorg).attr("col");
		var rigavecchia=$(sorg).attr("row");
		var idnuovo=$(tdsorg).attr("id");
		var pos=idnuovo.split("-")[1];
		$(tdsorg).html("<button align='center' id='r-"+pos+"' col='"+colvecchia+"' row='"+rigavecchia+"' type='submit' class='disp' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>"+quant+"</button>");
	}
	$(sorg).attr("col",col);
	$(sorg).attr("row",row);
	var previous = $(sorg).attr("prev");
	$(sorg).attr("c", previous);
	return sorg;
}

function controlla_pos_multiple(src_list,dest_list,posmax){
	//prendo solo il primo elemento, tanto poi l'inizio dell'id e' uguale per tutti gli id dest
	var inizio_dest=dest_list[2].split("-");
	for (var i=2; i<src_list.length; i++){
        var sorg=$("#"+src_list[i]);
        var de=$("#"+dest_list[i]);
        var figli=$(de).children();
		var classitasto=$(sorg).attr("class");
		var itself=$(sorg).attr("itself");
		//devo vedere se la cella dest e' disponibile, nel senso se non e' not available
		if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
			var aliqdisp=$(de).parent().attr("notavailable");
		}
		else if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
			var aliqdisp=$(de).attr("notavailable");
		}
		if(aliqdisp!="True"){
			//se e' un'aliquota
			if((classitasto!=undefined)&&(classitasto.indexOf("aliqclass")>-1)){
				//e' il posmax del singolo cont, non della piastra in toto
				var posmaxcont=$(de).attr("posmax");
				if((posmaxcont=="1")&&(itself=="undefined")){
					//devo vedere se bloccare il tutto perche' il numero di aliq accettabili e' stato raggiunto
					var numfigli=conta_figli_merge(figli,sorg);
					if(numfigli>1){
						return("Error: maximum number of containers for this position has been exceeded");
					}																					
				}
				else{						
					if((posmaxcont!="None")&&(itself=="undefined")){
						var posint=parseInt(posmaxcont);
						var numfigli=conta_figli_merge(figli,sorg);
						if(numfigli>posint){
							return("Error: maximum number of containers for this position has been exceeded");
						}
					}
					//devo vedere se il figlio presente nella cella contiene piu' di un container. Allora do' errore
					//e dico di usare lo spostamento manuale
					for(var j=0;j<figli.length;j++){
						var tag=$(figli[j]).prop("tagName");
						if((tag=="DIV")||(tag=="BUTTON")){
							var classedest=$(figli[j]).attr("class");
							//se non e' un'aliquota
							if((classedest!=undefined)&&(classedest.indexOf("aliqclass")==-1)){
								var testodest=parseInt($(figli[j]).text());
								if(!(isNaN(testodest))&&(testodest>1)){
									return("Destination is not unique. Please use manually move");
								}
							}
						}
					}
				}
			}
			//se non e' un'aliquota
			else{
				if((posmax!="None")){
					var posint=parseInt(posmax);
					var conta=0;
					for(var j=0;j<figli.length;j++){
						var tag=$(figli[j]).prop("tagName");
						if((tag=="DIV")||(tag=="BUTTON")){
							var pezzi=parseInt($(figli[j]).text());
							if (!(isNaN(pezzi))){
								if(pezzi==0){
									pezzi=1;
								}
								conta+=pezzi;
							}
						}
					}
					//devo aggiungere il cont che verra' spostato dopo
					var testo=parseInt($(sorg).text());
					if(itself!="undefined"){
						testo=0;
					}
					if(testo==0){
						conta+=1;
					}
					conta+=testo;
					if(conta>posint){
						return("Error: maximum number of containers for this position has been exceeded");						
					}
				}
			}
		}
		else{
			return("Unable to move: destination container is not available.");
		}
    }
	return ("ok");
}

/* save info and color the plate, searching in the list */
function save_bottom(el, src_list, dest_list,exec_alert){
	var msg=controlla_coerenza_spostamenti(src_list, dest_list);
	if (msg=="ok"){
	    /* retrieve positioning area in bottom plate */
	    var orizz = src_list[0];
	    var vert = src_list[1];
	    // remember: the first two elements in this list are the area dimension
	    var stringa_sorg="";
	    var stringa_dest="";
	    var barcodedest=cont_dest;
		var barcodesorg=cont_sorg;
		//prendo solo il primo elemento, tanto a me serve una proprieta'
		//del cont padre
		var inizio_dest=dest_list[2].split("-");
		if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
			//sto spostando all'interno della piastra sorgente
			var posmax=$("#"+dest_list[2]).parent().parent().parent().parent().attr("posmax");
		}
		else if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
			//la dest e' il cont a destra
			var posmax=$("#"+dest_list[2]).parent().parent().parent().attr("posmax");
		}

		var ris=controlla_pos_multiple(src_list,dest_list,posmax);
		if(ris!="ok"){
			if(exec_alert){
				alert(ris);
			}
			return ris;
		}
		
		//extend e' per copiare il contenuto di un diz in un altro, true permette di eseguire una copia approfondita di tutto
		//quello che c'e' nel diz originale, quindi anche degli altri diz eventualmente contenuti
		var mapp_agg_tmp=$.extend(true,{},mappa_aggiunti);
		var mapp_tolti_tmp=$.extend(true,{},mappa_tolti);	
		var dizrigh_tmp=$.extend(true,{},diz_righe_tolte);	
		var dizgentemp=$.extend(true,{},dati_server);		
		var piassorgtmp=$("#operativa table").html();
		var piasdesttmp=$("#freezer table").html();
		//barc del cont che sto effettivamente vedendo, non quello caricato
		var barcodedestattuale=$("#freezer table").attr("barcode");
		var barcodesorgattuale=$("#operativa table").attr("barcode");
		
		var canctab=false;
		var tipaltemp="";
		var bar;
		for (var i=2; i<src_list.length; i++){
			var sorg=$("#"+src_list[i]);
	        var de=$("#"+dest_list[i]);
	        
	        var piastra_sorg=$(sorg).parent().parent().parent().parent();
			bar=$(sorg).attr("barcode");
			var idcellasorg=$(sorg).parent().attr("id");
			var mult=$(sorg).parent().parent().parent().parent().attr("mult");
			var padre=$(sorg).parent().parent().parent().parent().attr("father");
			var classitasto=$(sorg).attr("class");
			var aliq=false;
			//se e' un'aliquota
			if((classitasto!=undefined)&&(classitasto.indexOf("aliqclass")>-1)){
				aliq=true;
			}
			
			//tolgo il class=mark nella td di partenza
			$(sorg).parent().removeClass("mark");
			var tipoaliqmossa=$(sorg).attr("tipo");	
			if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
				var piastra_dest=$(de).parent().parent().parent().parent();
				var padredest=$(de).parent().parent().parent().parent().attr("father");
				var costardest=$(de).parent().parent().parent().parent().attr("costar");
				var multdest=$(de).parent().parent().parent().parent().attr("mult");
				var idcella=$(de).parent().attr("id");
				var barcelladest=$(de).parent().attr("barcode");
				var figli=$(de).parent().children();				
				var tipaliq=tipoaliqmossa.split("-");
				aggiungi_in_tabella([bar],tipaliq[0]);
				
			}
			else if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
				var piastra_dest=$(de).parent().parent().parent();
				var padredest=$(de).parent().parent().parent().attr("father");
				var costardest=$(de).parent().parent().parent().attr("costar");
				var multdest=$(de).parent().parent().parent().attr("mult");
				var idcella=$(de).attr("id");
				var barcelladest=$(de).attr("barcode");
				var figli=$(de).children();
				canc_da_tabella([bar]);			
				canctab=true;
				var tipaliq=tipoaliqmossa.split("&");
				tipaltemp=tipaliq[0];
			}
								
			var contpadre=$(piastra_dest).parent().parent().parent().parent().attr("id");
			if(contpadre=="operativa"){
				if(mult=="True"){
					var barcodedest=cont_sorg;
				}
				else{
					var barcodedest=barcodesorgattuale;
				}
			}
			else if(contpadre=="freezer"){
				if(multdest=="True"){
					var barcodedest=cont_dest;
				}
				else{
					var barcodedest=barcodedestattuale;
				}
			}
			else{
				var barcodedest=null;
			}
			
			var contpadresorg=$(piastra_sorg).parent().parent().parent().parent().attr("id");
			if(contpadresorg=="operativa"){
				if(mult=="True"){
					var barcodesorg=cont_sorg;
				}
				else{
					var barcodesorg=barcodesorgattuale;
				}
			}
			else if(contpadresorg=="freezer"){
				if(multdest=="True"){
					var barcodesorg=cont_dest;
				}
				else{
					var barcodesorg=barcodedestattuale;
				}
			}
			else{
				var barcodesorg=null;
			}
			
			var classitasto=$(sorg).attr("class");
			//se e' un'aliquota
			if((classitasto!=undefined)&&(classitasto.indexOf("aliqclass")>-1)){
				//e' il posmax del singolo cont, non della piastra in toto
				var posmaxcont=$(de).attr("posmax");
				var sorgnuova=esegui_spost(figli,"0",posmaxcont,sorg,"0",de);												
			}
			//se non e' un'aliquota
			else{
				var sorgnuova=esegui_spost(figli,"X",posmax,sorg,"X",de);
			}
			
			var id_dest=$(de).attr("id");
			var idtmp=id_dest.split("-");
			if((inizio_dest[0]=="m")||(inizio_dest[0]=="o")){
				//cambio l'id al tasto spostato cosi' da non averne due uguali
				$(sorgnuova).attr("id","b-"+idtmp[1]);
			}
			else if((inizio_dest[0]=="r")||(inizio_dest[0]=="b")){
				$(sorgnuova).attr("id","r-"+idtmp[1]);
			}
			
			flag = "-";
			var htmlsorg=$(sorgnuova)[0].outerHTML;
			var idobj=$(sorgnuova).attr("id");
						
			aggiorna_mappe_cont(barcodesorg,bar,mult,padre,barcodedest,idcella,idcellasorg,htmlsorg,padredest);
			//se ho la dest sotto forma di lista di cont (ad es. stessa posizione in un cassetto) 
			if(multdest=="True"){			
				//sono nel caso in cui sto vedendo una lista di aliquote
				if(barcelladest==undefined){
					barcodedest=padredest;
				}
				else{
					barcodedest=barcelladest.split("|")[0];
				}
				idcella="-";
			}
			var testo=$(sorgnuova).text();
			aggiorna_diz_generale(bar,barcodesorg,barcodedest,aliq,idcella,costardest,testo);
	    }
		
		prepara_per_undo(mapp_agg_tmp,mapp_tolti_tmp,dizrigh_tmp,dizgentemp,piassorgtmp,piasdesttmp,canctab,bar,tipaltemp,cont_sorg,cont_dest);
		
	    tasto_sel_sorg="";
	    pos_multiplo=true;	    

		return "ok";
	}
	else{
		if(exec_alert){
			alert(msg);
		}
		return msg;
	}
}

/*function move_bottom(el, src_list, dest_list){
	//devo controllare che il tipo della piastra caricata sia coerente con quello dell'altra
	var trov=0;
	for (var i=0;i<tipoarchive.length;i++){
		for (var k=0;k<tipooperativa.length;k++){
			if (tipoarchive[i]==tipooperativa[k]){
				trov=1;
				break;
			}
		}
	}
	if (trov==1){
		var tipo=$("#tipo").val();
		var i;
	    var stringa_sorg="";
	    var stringa_sorg_pias_dest="";
	    var stringa_dest="";
	    var barcodedest=$("#barcode_freezer").val();
	    for (i=2; i<src_list.length; i++){
	        var src = document.getElementById("m-"+src_list[i]);
	        var dest = document.getElementById("m-"+dest_list[i]);
	        
	        sorg=$("#m-"+src_list[i]).children();
	        de=$("#m-"+dest_list[i]);
	        var num=$(sorg).attr("num");
			var bar=$(sorg).attr("barcode");
			var geneal=$(sorg).attr("gen");
			var id=$(sorg).attr("id");
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
	        
	        $("#m-"+src_list[i]).removeAttr("class");
	
	        if (tipo=="VT"){
				src.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>0</button>";
			}
			else{
				src.innerHTML="<button align='center' type='submit' assign='-' prev='plateButtonOFF' onclick='move(this,\"bot\")' c='plateButtonOFF'>X</button>";
			}
						
	    }
	    var data = {
	    		multiplo:true,
	    		stored:true,
	    		strsorg:stringa_sorg,
	    		strsorg2:stringa_sorg_pias_dest,
	    		strdest:stringa_dest,
	    		barcodesorg:$("#barcode_operative").val(),
	    		barcodedest:$("#barcode_freezer").val(),
	    		ti:tipo,
	    };
		var url=base_url+"/store/save/";
		$.post(url, data, function (result) {
	
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    });
		//abilito il tasto per confermare
		$("#p_confirm").attr("disabled",false);
	}
	else{
		alert("Incompatible containers. Aliquot type they can contain is not the same.");
	}
}*/


/* create the list of buttons to move */
function create_src_list(el){
	var list = [];
	var k = 2;
	var irow=parseInt($("#"+bi).attr("row"));
	var frow=parseInt($("#"+bf).attr("row"));
	var icol=parseInt($("#"+bi).attr("col"));
	var fcol=parseInt($("#"+bf).attr("col"));
	var inizioid=bf.split("-")[0];
	var orizz = fcol - icol+1;
    var vert = frow - irow+1;
    /* the first two vars are the area dimension */
    list[0] = orizz;
    list[1] = vert;
    for (var i=0; i<vert; i++){
        for (var j=0; j<orizz; j++){
        	var idogg=$("div[col='"+String(j+icol)+"'][row='"+String(i+irow)+"']");
        	var idtasto=$(idogg).attr("id");
        	if (idogg.length>1){
        		var idtmp=idtasto.split("-");
        		idtasto=inizioid+"-"+idtmp[1];
        	}
        	list[k]=idtasto;
            /* AREA TESTS */
            /* if there's a tube already moved in merge plate, stop everything */
            var gen=$("#"+list[k]).attr("gen");
            
            if (gen==undefined){
            	return null;
            }            
            k=k+1;
        }
    }
    return list;
}

/* create the list of buttons chosen as destination */
function create_dest_list(el, src_list){
	var list = [];
	var k = 2;
	var irow=parseInt($(el).attr("row"));
	var icol=parseInt($(el).attr("col"));
    /* the first two vars are the area dimension */
    var orizz = src_list[0];
    var vert = src_list[1];
    
    var orizzoff = src_list[0]+icol;
    var vertoff = src_list[1]+irow;
    //prendo le colonne della piastra in cui ho cliccato per posizionare i cont
    var colpiastra=$(el).parent().parent().parent().parent().attr("col");
    var rigpiastra=$(el).parent().parent().parent().parent().attr("row");
    var idpias=$(el).parent().parent().parent().parent().parent().attr("id");

    // if out of bounds, don't add
    if (orizzoff>colpiastra || vertoff>rigpiastra){
        return null;
    }

    for (var i=0; i<vert; i++){
        for (var j=0; j<orizz; j++){
        	if(idpias=="plate_operative"){
        		var idogg=$("#"+idpias+" button[col='"+String(j+icol)+"'][row='"+String(i+irow)+"']").attr("id");
        	}
        	else{
        		var idogg=$("#"+idpias+" button[col='"+String(j+icol)+"'][row='"+String(i+irow)+"']").parent().attr("id");
        	}
            list[k] = idogg;
            // if there are already filled places, stop everything
            if(idpias=="plate_operative"){            
	            if ($("#"+list[k]).attr("assign") != "-"){
	                return null;
	            }       
            }
            else{
            	if ($("#"+list[k]).children().attr("assign") != "-"){
	                return null;
	            }  
            }
            k=k+1;
        }
    }
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

