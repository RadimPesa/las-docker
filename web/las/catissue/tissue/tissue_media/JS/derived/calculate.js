//richiamata dalla funzione calcola_regole_n_aliq()
/*function calcola_valori(numero,volume,conc,tot,vol_aliq,percentuale,concentr,perc){
	var vol=new Array();
	var conce=new Array();

	//serve per calcolare il volume da togliere dalla provetta madre per creare i 
	//derivati
	var calc_w_h2o=vol_aliq+(vol_aliq*perc/100.0);
	var percentualeinpiu=percentuale+(percentuale*perc/100.0);
	//}
	if (conc>=concentr){
			
		//se ho abbastanza materiale per seguire le regole di derivazione normali
		//o se devo dividere semplicemente il materiale tra le aliquote
		if (tot>=(percentualeinpiu*numero)){
    		for(i=0;i<numero-1;i++){
    			vol[i]=vol_aliq;
    			conce[i]=concentr;
    		}
    		if(numero>1){
    			vol[numero-1]=(tot-(percentualeinpiu*(numero-1)))/(conc/1000); //(ug tot - x ug presi)/conc originaria in ug/uL
    			w_sol=volume-vol[numero-1];
                w_h2o=(calc_w_h2o*(numero-1))-w_sol;
    		}
    		else{
    			vol[0]=volume-(volume*perc/100.0);
                w_h2o=0.0;
    		}
            conce[numero-1]=conc;
            
            b_h2o=0.0;
            b_sol=vol[numero-1];
        }
		else{
			//divido il volume nelle aliquote togliendo prima la percentuale per lo spipettamento
    		v=volume-(volume*perc/100.0);
			for(i=0;i<numero;i++){
    			vol[i]=v/numero;
    			conce[i]=conc;
			}
			b_sol=0.0;//vol[numero-1];
			w_sol=volume;//-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
            	
		}
	}
	else{
		//divido il volume nelle aliquote togliendo prima la percentuale per lo spipettamento
		v=volume-(volume*perc/100.0);
		for(i=0;i<numero;i++){
			vol[i]=v/numero;
			conce[i]=conc;
		}
		b_sol=0.0;//vol[numero-1];
		w_sol=volume;//-b_sol;
    	w_h2o=0.0;
    	b_h2o=0.0;
		
	}
	if(numero==1){
		w_sol=0.0;
	}
	for(i=0;i<numero;i++){
    	//creo il nome dell'input
    	volu="#volume_"+i;
    	concen="#concentration_"+i;
    	volum=parseFloat(vol[i]);
    	vol[i]=volum.toFixed(2);
    	$(volu).attr("value",vol[i]);
    	$(concen).attr("value",conce[i]);
    }
    ws=parseFloat(w_sol);
    w_sol=ws.toFixed(2);
    wh=parseFloat(w_h2o);
    w_h2o=wh.toFixed(2);
    bs=parseFloat(b_sol);
    b_sol=bs.toFixed(2);
    bh=parseFloat(b_h2o);
    b_h2o=bh.toFixed(2);
    if (w_sol==0.00)
    	w_sol="";
    if (w_h2o==0.00)
    	w_h2o="";
    if (b_h2o==0.00)
    	b_h2o="";
    if (b_sol==0.00)
    	b_sol="";
    $("#id_work_al_sol").attr("value",w_sol);
    $("#id_work_al_h2o").attr("value",w_h2o);
    $("#id_back_al_sol").attr("value",b_sol);
    $("#id_back_h2o").attr("value",b_h2o);
}

function calcola_regole_n_aliq(numero){
	
	var protocollo=$("#proto").attr("value");
	var volume=$("#id_vol_tot").attr("value");
	var conc=$("#id_conc_tot").attr("value");
	//conc e' in ng/L vol e' in uL
    tot=volume*(conc/1000);
    var vol_aliq=$("#volume_aliq").attr("value");
    var conc_aliq=$("#conc_aliq").attr("value");
    var numero_aliq=$("#numero_aliq_spip").attr("value");

    if(numero<=parseInt(numero_aliq)){
    	var perc_spip=$("#perc_spip_inf").attr("value");
    }
    else{
    	var perc_spip=$("#perc_spip_sup").attr("value");
    }
    //if (protocollo=="DNA"){
    	//calcola_valori(numero,volume,conc,tot,10.0,1000.0);
    calcola_valori(numero,volume,conc,tot,parseFloat(vol_aliq),(parseFloat(conc_aliq)/1000.0)*parseFloat(vol_aliq),parseFloat(conc_aliq),parseFloat(perc_spip));
    */	
    /*}
    if (protocollo=="RNA"){
    	calcola_valori(numero,volume,conc,tot,5.0,500.0);
    	
    }
    if (protocollo=="cRNA"){
    	calcola_valori(numero,volume,conc,tot,2.5,250.0);
    	
    }
    if (protocollo=="cDNA"){
    	calcola_valori(numero,volume,conc,tot,3.0,300.0);
    	
    }*/
    
//}
var vol=new Array();
var conce=new Array();
var moth=new Array();
var acqua=new Array();
//vettore al cui interno vengono segnate le aliquote il cui valore di volume preso dalla 
//madre e di acqua di diluizione non devono essere modificate. Perch� quei valori sono 
//gia' stati calcolati prima singolarmente. Il tutto vale quando si clicca il tasto per
//il ricalcolo dei valori
var prov_bloccate=new Array();

//serve per aggiungere caselle nella tabella che riepiloga le aliquote derivate
function aggiungi_campi_tabella(){
	var protocollo=$("#scelta_prot option:selected").text();
	var volume=$("#id_vol_tot").attr("value");
	var conc=$("#id_conc_tot").attr("value");
	if (protocollo=="-----------"){
		alert("Select a derivation protocol");
	}
	else if(volume==""){
		alert("Insert volume");
	}
	else if(conc==""){
		alert("Insert concentration");
	}
	else{
		//faccio vedere la tabella con le aliq
		$("#aliq").css("display","inline");
		numero=$("#id_number_aliquots").attr("value");
		celle=$("#aliq tr>th");
		//celle e' il numero attuale di celle della tabella
		numcelle=(celle.length);
		num=numero-numcelle+1;
		
		var num_aliquote=$("#numero_aliq_tot").attr("value");
		if(num>=0){
			for(i=0;i<num;i++){
				$("#aliq tr>th:last").after("<th>Aliquot "+(i+numcelle)+"</th>");
				$("#aliq tr>td:last").after("<td align=\"center\" style=\" padding: 8px;border-width:1px;\">"+
				"<div><label for=\"volume_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;'>Volume(uL):</label>"+
				"<input id=\"volume_"+(i+numcelle-1)+"\" type=\"text\" size=\"4\" name=\"volume_"+(i+numcelle-1)+"\" maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'>"+
				"<label for=\"concentration_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;'>Concentration<br>(ng/uL):</label>"+
				"<input id=\"concentration_"+(i+numcelle-1)+"\" type='text' size='4' name=\"conc_"+(i+numcelle-1)+"\" maxlength='7' style='margin-top: 5px; margin-bottom: 5px;'>"+
				"<label for=\"moth_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;margin-top:5px;'>Mother(uL):</label>"+
				"<input id=\"moth_"+(i+numcelle-1)+"\" type=\"text\" size=\"4\" maxlength='7' readonly='readonly' style='margin-top: 5px; margin-bottom: 5px;'>"+
				"<label for=\"h2o_"+(i+numcelle-1)+"\" style='font-size: 1em; margin-bottom: 5px;'>H2O(uL):</label>"+
				"<input id=\"h2o_"+(i+numcelle-1)+"\" type='text' size='4' maxlength='7' readonly='readonly' style='margin-top: 5px;'>"+
				"</div>"+
				"</td>")
			}
			$("#aliq tr>th").css("background-color","#FFD199");
			$("#aliq tr>th:first").css("background-color","#FF9A45");
			$("#aliq tr>th:last").css("background-color","silver");

			calcola_regole_iniziali(numero);
		}
		else{
			if(numero<1){
				alert("Value has to be at least 1");
			}
			else{
				val=numcelle-numero-1;
				for(i=0;i<val;i++){
					$("#aliq tr>th:last").remove();
					$("#aliq tr>td:last").remove();
				}
				
				$("#aliq tr>th").css("background-color","#FFD199");
				$("#aliq tr>th:last").css("background-color","silver");
				
				calcola_regole_iniziali(numero);
			}
		}
	}
}



function calcola_inizio(n_aliq,volume,conc,tot,vol_aliq,concentr,val1,val2,percent,concnuova,perc_spip){
	//i commenti riguardano il caso dell'RNA

	if (conc>=concentr){
        //vol1=vol2=vol3=vol4=vol5=10.0; //uL
        //conc1=conc2=conc3=conc4=conc5=concentr; //ng/uL
		for(i=0;i<n_aliq-1;i++){
			vol[i]=vol_aliq;
			conce[i]=concentr;
		}
        if (tot>=val1){
        	$("th:contains(Working aliquots)").css("color","black");
            vol[n_aliq-1]=(tot-percent)/(conc/1000); //27.5 e' 25 maggiorato del 10% (ug tot - 27.5 ug presi)/conc originaria in ug/uL
            conce[n_aliq-1]=conc;
            w_sol=volume-vol[n_aliq-1];
            //calcolo il volume totale per creare i derivati a cui aggiungo la perc per
            //lo spipettamento
            var volparz=(vol_aliq*(n_aliq-1));
            var voltot=volparz+(volparz*(perc_spip/100.0));
            //w_h2o=44.0-w_sol;
            w_h2o=voltot-w_sol;
            b_h2o=0.0;
            b_sol=vol[n_aliq-1];
            //devo calcolare i valori da prelevare dalla madre e l'acqua con cui diluire
            //la singola provetta
            for(j=0;j<n_aliq-1;j++){
            	//ugr di una singola provetta
            	var ugrsingoli=vol[j]*(conce[j]/1000.0);
            	//aggiungo la perc per lo spipettamento
            	var ugreffettivi=ugrsingoli+(ugrsingoli*(perc_spip/100.0));
            	//vol da prelevare dalla madre
            	moth[j]=ugreffettivi/(conc/1000.0);
            	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
            	//della madre e quella della singola provetta
            	acqua[j]=(moth[j]*conc/conce[j])-moth[j];
            }
            moth[n_aliq-1]=vol[n_aliq-1];
            acqua[n_aliq-1]=0.0;
            if(n_aliq==1){
            	vol[0]=volume-(volume*perc_spip/100.0);
            	w_h2o=0.0;
            	b_sol=0.0;
            	moth[0]=volume;
            }
            
        }
        else if ((tot<=val1) && (tot>=val2)){
        	vol[n_aliq-1]=(tot-percent)/(concnuova); //(ug tot-27.5ug presi)/la concentrazione, che qui e' 0.5 ug/ul
        	conce[n_aliq-1]=concentr;
            co=conc/concentr;
            volu=volume*co;
            b_h2o=volu-volume//0.0;
            b_sol=volume//vol[n_aliq-1];
            w_sol=0.0//volume;
            w_h2o=0.0//volu-volume;
            
            for(j=0;j<n_aliq-1;j++){
            	moth[j]=vol[j]+(vol[j]*perc_spip/100.0);
            	acqua[j]=0.0;
            }
            moth[n_aliq-1]=vol[n_aliq-1];
            acqua[n_aliq-1]=0.0;
            
            //tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#FFD199");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            
            $("#aliq tr>th").css("background-color","silver");
            if(n_aliq==1){
            	vol[0]=volume-(volume*perc_spip/100.0);
            	conce[0]=conc;
            	w_sol=0.0;
            	w_h2o=0.0;
            	b_sol=0.0;
            	moth[0]=volume;
            }
        }
        else{
        	//divido il volume nelle aliquote togliendo prima la percentuale per lo
        	//spipettamento
    		//v=volume-(volume*perc_spip/100.0);
        	v=volume
        	for(i=0;i<n_aliq;i++){
    			//vol[i]=v/n_aliq;
    			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
        		vol[i]=(v/n_aliq)-(v/n_aliq*perc_spip/100.0);
        		conce[i]=conc;
    			//moth[i]=vol[i];
        		moth[i]=v/n_aliq;
            	acqua[i]=0.0;
    		}
        	b_sol=volume//moth[n_aliq-1];
        	//calcolo la somma dei volumi delle aliq in verde
        	w=0.0;
        	for(i=0;i<(n_aliq-1);i++){
        		w=w+moth[i];
        	}
			w_sol=0.0//w;
        	w_h2o=0.0;
        	b_h2o=0.0;
        	if(n_aliq==1){
        		b_sol=0.0;
        	}
        	//tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#FFD199");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            
            $("#aliq tr>th").css("background-color","silver");
        }
        
	}
	else{
		//divido il volume nelle aliquote togliendo prima la perc. per lo spipettamento
		//v=volume-(volume*perc_spip/100.0);
		v=volume
    	for(i=0;i<n_aliq;i++){
    		//vol[i]=v/n_aliq;
			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
    		vol[i]=(v/n_aliq)-(v/n_aliq*perc_spip/100.0);
    		conce[i]=conc;
			//moth[i]=vol[i];
    		moth[i]=v/n_aliq;
        	acqua[i]=0.0;
		}
    	b_sol=volume//moth[n_aliq-1];
    	//calcolo la somma dei volumi delle aliq in verde
    	w=0.0;
    	for(i=0;i<(n_aliq-1);i++){
    		w=w+moth[i];
    	}
		w_sol=0.0//w;
    	w_h2o=0.0;
    	b_h2o=0.0;
    	if(n_aliq==1){
    		b_sol=0.0;
    	}
    	//tolgo il titolo a working aliquots preparation
        $("th:contains(Working aliquots)").css("color","#FFD199");
        $("th:contains(Working aliquots)").css("border-color","black");
        $("th:contains(Back up aliquot)").text("Aliquot preparation");
        
        $("#aliq tr>th").css("background-color","silver");
	}
	
	/*v1=parseFloat(vol1);
    vol1=v1.toFixed(2);
    v2=parseFloat(vol2);
    vol2=v2.toFixed(2);
    v3=parseFloat(vol3);
    vol3=v3.toFixed(2);
    v4=parseFloat(vol4);
    vol4=v4.toFixed(2);
    v5=parseFloat(vol5);
    vol5=v5.toFixed(2);
    v6=parseFloat(vol6);
    vol6=v6.toFixed(2);
    $("#volume_0").attr("value",vol1);
    $("#volume_1").attr("value",vol2);
    $("#volume_2").attr("value",vol3);
    $("#volume_3").attr("value",vol4);
    $("#volume_4").attr("value",vol5);
    $("#volume_5").attr("value",vol6);
    $("#concentration_0").attr("value",conc1);
    $("#concentration_1").attr("value",conc2);
    $("#concentration_2").attr("value",conc3);
    $("#concentration_3").attr("value",conc4);
    $("#concentration_4").attr("value",conc5);
    $("#concentration_5").attr("value",conc6);*/
	for(i=0;i<n_aliq;i++){
	    	//creo il nome dell'input
	    	volu="#volume_"+i;
	    	concen="#concentration_"+i;
	    	var madre="#moth_"+i;
	    	var acq="#h2o_"+i;
	    	vol[i]=parseFloat(vol[i]).toFixed(2);
	    	conce[i]=parseFloat(conce[i]).toFixed(1);
			moth[i]=parseFloat(moth[i]).toFixed(2);
			acqua[i]=parseFloat(acqua[i]).toFixed(2);
	    	$(volu).attr("value",vol[i]);
	    	$(concen).attr("value",conce[i]);
	    	$(madre).attr("value",moth[i]);
	    	$(acq).attr("value",acqua[i]);
    }
    ws=parseFloat(w_sol);
    w_sol=ws.toFixed(2);
    wh=parseFloat(w_h2o);
    w_h2o=wh.toFixed(2);
    bs=parseFloat(b_sol);
    b_sol=bs.toFixed(2);
    bh=parseFloat(b_h2o);
    b_h2o=bh.toFixed(2);
    if (w_sol==0.00)
    	w_sol="";
    if (w_h2o==0.00)
    	w_h2o="";
    if (b_h2o==0.00)
    	b_h2o="";
    if (b_sol==0.00)
    	b_sol="";
    $("#id_work_al_sol").attr("value",w_sol);
    $("#id_work_al_h2o").attr("value",w_h2o);
    $("#id_back_al_sol").attr("value",b_sol);
    $("#id_back_h2o").attr("value",b_h2o);
}

//per calcolare i valori iniziali delle aliq derivate con i tre tipi di regole in base alla 
//quantit� di materiale prodotto
function calcola_regole_iniziali(n_aliq){
	protocollo=$("#proto").attr("value");
	volume=$("#id_vol_tot").attr("value");
	conc=$("#id_conc_tot").attr("value");
	//conc e' in ng/L, vol e' in uL
    tot=volume*(conc/1000)
    var vol_aliq=$("#volume_aliq").attr("value");
    var conc_aliq=$("#conc_aliq").attr("value");
    var num_aliquote=$("#id_number_aliquots").attr("value");
    var estremo_inf=parseInt(num_aliquote)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0)
    var estremo_sup=(parseInt(num_aliquote)+4)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0)

    //informazioni per lo spipettamento
    var numero_ali=$("#numero_aliq_spip").attr("value");

    if(n_aliq<=parseInt(numero_ali)){
    	var perc_spip=$("#perc_spip_inf").attr("value");
    }
    else{
    	var perc_spip=$("#perc_spip_sup").attr("value");
    }
    //calcolo i ugr che rappresentano quelli utilizzati per creare le aliq con in piu'
    //i ugr per lo spipettamento. Questi ugr vengono poi tolti dalla soluzione totale
    //contenuta nella provetta madre
    //calcolo i ugr per creare le n aliq
    var ugr_parz=(parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000))*(n_aliq-1);
    //aggiungo la percentuale per lo spipettamento
    var ugrtot=ugr_parz+(ugr_parz*perc_spip/100);

    //concentrazione della singola aliq derivata/1000
    var concnuova=conc_aliq/1000.0;
    
    //if (protocollo=="DNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,1000.0,100,60,55,1);
    	//calcola_inizio(n_aliq,volume,conc,tot,100.0,10,6,5.5,0.1);
    calcola_inizio(n_aliq,volume,conc,parseFloat(tot),parseFloat(vol_aliq),parseFloat(conc_aliq),parseFloat(estremo_sup),parseFloat(estremo_inf),ugrtot,concnuova,perc_spip);
    	/*if (conc>=1000.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=1000.0; //ng/uL
            if (tot>=100){
                vol6=(tot-55)/(conc/1000); //(ug tot - 55 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_sol=vol6;
                b_h2o=0.0;
            }
            else if ((tot<=100) && (tot>=60)){
                vol6=(tot-55); //(ug tot-55ug presi)/la concentrazione, che pero' qui e' 1 ug/ul
                conc6=1000.0;
                co=conc/1000.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
                //divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
            	v=volume-(volume/10.0);
            	vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    //if (protocollo=="RNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,500.0,50,30,27.5,0.5);
    	//calcola_inizio(n_aliq,volume,conc,tot,500.0,50,30,22.0,0.5);
    	/*if (conc>=500.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=500.0; //ng/uL
            if (tot>=50){
                vol6=(tot-27.5)/(conc/1000); //27.5 e' 25 maggiorato del 10% (ug tot - 27.5 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_h2o=0.0;
                b_sol=vol6;
            }
            else if ((tot<=50) && (tot>=30)){
                vol6=(tot-27.5)/(0.5); //(ug tot-27.5ug presi)/la concentrazione, che qui e' 0.5 ug/ul
                conc6=500.0;
                co=conc/500.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
            	//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
        		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    //if (protocollo=="cRNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,250.0,25,15,13.75,0.25);
    	//calcola_inizio(n_aliq,volume,conc,tot,250.0,25,15,11.0,0.25);
    	/*if (conc>=250.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=250.0; //ng/uL
            if (tot>=25){
                vol6=(tot-13.75)/(conc/1000); //(ug tot - 13.75 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_h2o=0.0;
                b_sol=vol6;
            }
            else if ((tot<=25) && (tot>=15)){
                vol6=(tot-13.75)/(0.25); //(ug tot-13.75ug presi)/la concentrazione, che qui e' 0.25 ug/ul
                conc6=250.0;
                co=conc/250.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
            	//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
        		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    //if (protocollo=="cDNA"){
    	//calcola_inizio(n_aliq,volume,conc,tot,300.0,30,18,16.5,0.3);
    	//calcola_inizio(n_aliq,volume,conc,tot,300.0,30,18,13.2,0.3);
    	/*if (conc>=300.0){
            vol1=vol2=vol3=vol4=vol5=10.0; //uL
            conc1=conc2=conc3=conc4=conc5=300.0; //ng/uL
            if (tot>=30){
                vol6=(tot-16.5)/(conc/1000); //(ug tot - 16.5 ug presi)/conc originaria in ug/uL
                conc6=conc;
                w_sol=volume-vol6;
                w_h2o=55.0-w_sol;
                b_h2o=0.0;
                b_sol=vol6;
            }
            else if ((tot<=30) && (tot>=18)){
                vol6=(tot-16.5)/(0.3); //(ug tot-16.5ug presi)/la concentrazione, che qui e' 0.3 ug/ul
                conc6=300.0;
                co=conc/300.0;
                volu=volume*co;
                b_h2o=0.0;
                b_sol=0.0;
                w_sol=volume;
                w_h2o=volu-volume;
            }
            else{
            	//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
        		v=volume-(volume/10.0);
        		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
                //la conc e' sempre quella originale
            	conc1=conc2=conc3=conc4=conc5=conc6=conc;
            	b_sol=vol6;
    			w_sol=volume-(volume/10)-b_sol;
            	w_h2o=0.0;
            	b_h2o=0.0;
            }
            
    	}
    	else{
    		//divido il volume nelle aliquote togliendo prima il 10% per lo spipettamento
    		v=volume-(volume/10.0);
    		vol1=vol2=vol3=vol4=vol5=vol6=v/n_aliq;
    		//la conc e' sempre quella originale
        	conc1=conc2=conc3=conc4=conc5=conc6=conc;
        	b_sol=vol6;
			w_sol=volume-(volume/10)-b_sol;
        	w_h2o=0.0;
        	b_h2o=0.0;
    	}*/
    //}
    
}

//richiamata dalla funzione copia_valori_ricalcola()
function copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,conc_aliq,val1,val2,ugr,c_ultima,perc,volback,cback,vett_vol,vett_conc,n_aliq){
	var moth=new Array();
	var acqua=new Array();
	//var concc=new Array();
	//var voll=new Array();
	var celle=$("#aliq tr>th");
	//e' il numero delle aliquote totali
	var n_aliq_effettivo=(celle.length)-1;
	//invece n_aliq � il numero di aliq compreso quella di riserva che non sono state 
	//modificate manualmente
	w_sol=0.0;
	w_h2o=0.0;
	//totg=tot_generale-(tot_generale*perc/100.0);
	volume=tot_generale/(conc/1000);
	var vol_aliq=$("#volume_aliq").attr("value");
    //calcolo i ugr che rappresentano quelli utilizzati per creare le aliq con in piu'
    //i ugr per lo spipettamento. Questi ugr vengono poi tolti dalla soluzione totale
    //contenuta nella provetta madre
    //calcolo i ugr per creare le n aliq
    var ugr_parz=(parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000))*(n_aliq-1);
    //aggiungo la percentuale per lo spipettamento
    var ugrtot=ugr_parz+(ugr_parz*perc/100);
    //il primo elemento della lista non � fra i th voluti, quindi lo salto sempre
	var lista_th=$("#aliq tr:first th");

	if (conc>=conc_aliq){
		for(i=0;i<n_aliq_effettivo-1;i++){
			vol[i]=vol_aliq;
			conce[i]=conc_aliq;
		}
		if (tot_generale>=val1){
			
			$("th:contains(Working aliquots)").css("color","black");
			vol[n_aliq_effettivo-1]=(tot_generale-ugrtot)/(conc/1000); //27.5 e' 25 maggiorato del 10% (ug tot - 27.5 ug presi)/conc originaria in ug/uL
            conce[n_aliq_effettivo-1]=conc;

            w_sol=volume-vol[n_aliq_effettivo-1];
            //calcolo il volume totale per creare i derivati a cui aggiungo la perc per
            //lo spipettamento
            //uso n_aliq che � il numero di aliquote non modificate manualmente
            var volparz=(vol_aliq*(n_aliq-1));
            var voltot=volparz+(volparz*(perc/100.0));
            //w_h2o=44.0-w_sol;
            w_h2o=voltot-w_sol;
            b_h2o=0.0;
            b_sol=vol[n_aliq_effettivo-1];
            //devo calcolare i valori da prelevare dalla madre e l'acqua con cui diluire
            //la singola provetta
            for(j=0;j<n_aliq_effettivo-1;j++){
            	//ugr di una singola provetta
            	var ugrsingoli=vol[j]*(conce[j]/1000.0);
            	//aggiungo la perc per lo spipettamento
            	var ugreffettivi=ugrsingoli+(ugrsingoli*(perc/100.0));
            	//vol da prelevare dalla madre
            	moth[j]=ugreffettivi/(conc/1000.0);
            	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
            	//della madre e quella della singola provetta
            	acqua[j]=(moth[j]*conc/conce[j])-moth[j];
            }
            if(n_aliq_effettivo==1){
            	vol[0]=volume-(volume*perc/100.0);
            	w_h2o=0.0;
            	b_sol=0.0;
            }
            moth[n_aliq_effettivo-1]=vol[n_aliq_effettivo-1];
            acqua[n_aliq_effettivo-1]=0.0;
            /*b_h2o=0.0;
            //devo calcolare i valori da prelevare dalla madre e l'acqua con cui diluire
            //la singola provetta
            for(j=0;j<n_aliq-1;j++){
            	//ugr di una singola provetta
            	var ugrsingoli=vett_vol[j]*(vett_conc[j]/1000.0);
            	//aggiungo la perc per lo spipettamento
            	var ugreffettivi=ugrsingoli+(ugrsingoli*(perc/100.0));
            	//vol da prelevare dalla madre
            	moth[j]=ugreffettivi/(conc/1000.0);
            	//per trovare l'acqua moltiplico i ul per il rapporto tra la conc
            	//della madre e quella della singola provetta
            	acqua[j]=(moth[j]*conc/vett_conc[j])-moth[j];
            	w_sol+=parseFloat(moth[j]);
        		w_h2o+=parseFloat(acqua[j]);*/
        }
		else if ((tot_generale<=val1) && (tot_generale>=val2)){
			//concentrazione della singola aliq derivata/1000
		    var concnuova=conc_aliq/1000.0;
			vol[n_aliq_effettivo-1]=(tot_generale-ugrtot)/(concnuova); //(ug tot-27.5ug presi)/la concentrazione, che qui e' 0.5 ug/ul
        	conce[n_aliq_effettivo-1]=conc_aliq;
            co=conc/conc_aliq;
            volu=volume*co;
            b_h2o=volu-volume//0.0;
            b_sol=volume//vol[n_aliq-1];
            w_sol=0.0//volume;
            w_h2o=0.0//volu-volume;
            if(n_aliq==1){
            	vol[0]=volume-(volume*perc/100.0);
            	conce[0]=conc;
            	w_sol=0.0;
            	w_h2o=0.0;
            }

            for(j=0;j<n_aliq_effettivo-1;j++){
            	moth[j]=parseFloat(vol[j])+(vol[j]*perc/100.0);
            	acqua[j]=0.0;
            }
            moth[n_aliq_effettivo-1]=vol[n_aliq_effettivo-1];
            acqua[n_aliq_effettivo-1]=0.0;
            //tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#FFD199");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            for (kk=1;kk<lista_th.length;kk++){
            	if (prov_bloccate[kk-1]!=1){
            		$(lista_th[kk]).css("background-color","silver");
            	}
            }            
			/*c="#concentration_"+(num_aliq);
			var conc6=$(c).attr("value");
			//b_h2o=(b_sol*(conc/conc6))-b_sol;
			//volback=b_h2o+b_sol;
			b_sol=0.0;
			w_sol=$("#id_work_al_sol").attr("value");
			w_h2o=$("#id_work_al_h2o").attr("value");
			//e' la concentrazione nominale della singola aliquota (ad es 100 ng/ul)
			//per il DNA
			var conc_aliq=$("#conc_aliq").val();
			//ho gi� portato tutta la conc della madre al valore voluto (ad es 100 ng/ul
			//per il DNA). Devo solo vedere se bisogna diluire di pi� una provetta
			//perch� magari � stata diminuita manualmente la concentrazione
			for(j=0;j<n_aliq-1;j++){

				acqua[j]=(vett_vol[j]*conc_aliq/vett_conc[j])-vett_vol[j];
				moth[j]=vett_vol[j];
			}*/
			
        }
		else{
    		//v=volume-(volume*perc/100.0);
    		v=volume;
			//il ciclo � lungo come tutte le aliquote effettive (5 ad es) per salvare
    		//in ogni posto del vettore vol[i] il nuovo valore del volume per le aliq
    		//non modificate manualmente. Per� la divisione del v totale avviene in base
    		//alle aliq effettivamente non modificate.
        	for(i=0;i<n_aliq_effettivo;i++){
        		//vol[i]=v/n_aliq;
    			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
        		vol[i]=(v/n_aliq)-(v/n_aliq*perc/100.0);
        		conce[i]=conc;
    			//moth[i]=vol[i];
        		moth[i]=v/n_aliq;
            	acqua[i]=0.0;
    		}
        	b_sol=volume//moth[n_aliq-1];
        	//calcolo la somma dei volumi delle aliq in verde
        	w=0.0;
        	for(i=0;i<(n_aliq-1);i++){
        		w=w+moth[i];
        	}
			w_sol=0.0//w;
        	w_h2o=0.0;
        	b_h2o=0.0;
        	//tolgo il titolo a working aliquots preparation
            $("th:contains(Working aliquots)").css("color","#FFD199");
            $("th:contains(Working aliquots)").css("border-color","black");
            $("th:contains(Back up aliquot)").text("Aliquot preparation");
            for (kk=1;kk<lista_th.length;kk++){
            	if (prov_bloccate[kk-1]!=1){
            		$(lista_th[kk]).css("background-color","silver");
            	}
            }
            
			/*b_h2o=0.0;
			b_sol=0.0;
			//tolgo la percentuale per lo spipettamento dal totale generale
			var tot=tot_generale-(tot_generale*perc/100.0) 
			//var ugrfinali=ugr+(ugr*perc/100.0);
			var volback=(tot-ugr)/(c_ultima/1000); //(ug tot - ug presi)/conc originaria in ug/uL
			
			for(j=0;j<n_aliq-1;j++){
				acqua[j]=(vett_vol[j]*conc/vett_conc[j])-vett_vol[j];
				moth[j]=vett_vol[j];
				w_sol+=parseFloat(moth[j]);
        		w_h2o+=parseFloat(acqua[j]);
			}
			
	        //w_sol=volume-volback;
	        //w_h2o=(w_sol*(conc/conc0))-w_sol;
	        b_sol=volback;
			//volback=volume0;
			//cback=conc0;*/
		}
	}
	else{
		//v=volume-(volume*perc/100.0);
		v=volume;
		//il ciclo � lungo come tutte le aliquote effettive (5 ad es) per salvare
		//in ogni posto del vettore vol[i] il nuovo valore del volume per le aliq
		//non modificate manualmente. Per� la divisione del v totale avviene in base
		//alle aliq effettivamente non modificate.
		for(i=0;i<n_aliq_effettivo;i++){
    		//vol[i]=v/n_aliq;
			//prendo v/n_aliq e tolgo la percentuale per lo spipettamento
    		vol[i]=(v/n_aliq)-(v/n_aliq*perc/100.0);
    		conce[i]=conc;
			//moth[i]=vol[i];
    		moth[i]=v/n_aliq;
        	acqua[i]=0.0;
		}
		
    	
    	b_sol=volume//moth[n_aliq-1];
    	//calcolo la somma dei volumi delle aliq in verde
    	w=0.0;
    	for(i=0;i<(n_aliq-1);i++){
    		w=w+moth[i];
    	}
		w_sol=0.0//w;
    	w_h2o=0.0;
    	b_h2o=0.0;
    	//tolgo il titolo a working aliquots preparation
        $("th:contains(Working aliquots)").css("color","#FFD199");
        $("th:contains(Working aliquots)").css("border-color","black");
        $("th:contains(Back up aliquot)").text("Aliquot preparation");
        for (kk=1;kk<lista_th.length;kk++){
        	if (prov_bloccate[kk-1]!=1){
        		$(lista_th[kk]).css("background-color","silver");
        	}
        }           
        
		/*b_h2o=0.0;
		b_sol=0.0;
		//tolgo la percentuale per lo spipettamento dal totale generale
		var tot=tot_generale-(tot_generale*perc/100.0) 
		var volback=(tot-ugr)/(c_ultima/1000); //(ug tot - ug presi)/conc originaria in ug/uL

		for(j=0;j<n_aliq-1;j++){
			acqua[j]=(vett_vol[j]*conc/vett_conc[j])-vett_vol[j];
			
			moth[j]=vett_vol[j];
			w_sol+=parseFloat(moth[j]);
    		w_h2o+=parseFloat(acqua[j]);
		}
		
		//var ugrfinali=ugr+(ugr*perc/100.0);  
		
        //w_sol=volume-volback;
        //w_h2o=(w_sol*(conc/conc0))-w_sol;
        b_sol=volback;
		//volback=volume0;
		//cback=conc0;*/
	}
	
	if(n_aliq==1){
		moth[n_aliq-1]=parseFloat(vett_vol[0])+(vett_vol[0]*perc/100.0);
		acqua[0]=(vett_vol[0]*conc/vett_conc[0])-vett_vol[0];
	}
	/*else{
		moth[n_aliq-1]=volback;
		acqua[n_aliq-1]=0.0;
	}*/

	
	vsei=parseFloat(volback);
	volback=vsei.toFixed(2);
	csei=parseFloat(cback);
	cback=csei.toFixed(1);
	ws=parseFloat(w_sol);
    w_sol=ws.toFixed(2);
    wh=parseFloat(w_h2o);
    w_h2o=wh.toFixed(2);
    bs=parseFloat(b_sol);
    b_sol=bs.toFixed(2);
    bh=parseFloat(b_h2o);
    b_h2o=bh.toFixed(2);
    if (w_sol==0.00)
    	w_sol="";
    if (w_h2o==0.00)
    	w_h2o="";
    if (b_h2o==0.00)
    	b_h2o="";
    if (b_sol==0.00)
    	b_sol="";
    var numero=$("#id_number_aliquots").attr("value");
    
    //var j=0;

    for (i=0;i<numero;i++){
    	if (prov_bloccate[i]!=1){
    		var volu="#volume_"+i;
	    	var concen="#concentration_"+i;
		    var madre="#moth_"+i;
			var acq="#h2o_"+i;
			vol[i]=parseFloat(vol[i]).toFixed(2);
	    	conce[i]=parseFloat(conce[i]).toFixed(1);
			moth[i]=parseFloat(moth[i]).toFixed(2);
			acqua[i]=parseFloat(acqua[i]).toFixed(2);
			//if(n_aliq>1){
			$(volu).attr("value",vol[i]);
		    $(concen).attr("value",conce[i]);
			//}
	    	$(madre).attr("value",moth[i]);
			$(acq).attr("value",acqua[i]);
			//j=j+1;
    	}
    }
	
    
    if(numero==1){
    	$("#id_back_al_sol").attr("value","");
    }
    //solo se il numero di aliq prodotte e' diverso da 1
    if(numero!=1){
	    $("#id_work_al_sol").attr("value",w_sol);
	    $("#id_work_al_h2o").attr("value",w_h2o);
	    $("#id_back_h2o").attr("value",b_h2o);
	    $("#id_back_al_sol").attr("value",b_sol);
		volu="#volume_"+(num_aliq);
		//$(volu).attr("value",volback);  
		cc="#concentration_"+(num_aliq);
		//$(cc).attr("value",cback);
    }
}

//per ricalcolare l'acqua da diluire e la quantita' di soluzione da prendere nel caso l'utente
//cambi i valori di conc o volume nelle aliq
function copia_valori_ricalcola(){
	var blocca=false;
	var volume0=$("#volume_0").attr("value");
	var conc0=$("#concentration_0").attr("value");
	var vett_vol=new Array();
	var vett_conc=new Array();
	celle=$("#aliq tr>th");
	var vol_aliq=$("#volume_aliq").attr("value");
    var conc_aliq=$("#conc_aliq").attr("value");
	//e' il numero delle working aliquot
	num_aliq=(celle.length)-2;
	//controllo che siano stati inseriti solo numeri
	var regex=/^[0-9.]+$/;
	var err=false;

	for(j=0;j<num_aliq;j++){
		//prendo i valori di vol e conc delle aliq
		var nome_vol="#volume_"+j;
		var nome_conc="#concentration_"+j;
		vett_vol[j]=$(nome_vol).val();
		vett_conc[j]=$(nome_conc).val();
		if((!regex.test(vett_vol[j]))||(!regex.test(vett_conc[j]))){
			alert("You can only insert number. Please correct.");
			err=true;
			/*vol1=$("#volume_1").attr("value");
			conc1=$("#concentration_1").attr("value");
			$("#volume_0").attr("value",vol1);
			$("#concentration_0").attr("value",conc1);*/
		}
	}

	if(err==false){
		
		var protocollo=$("#proto").attr("value");
		var volume=$("#id_vol_tot").attr("value");
		var conc=$("#id_conc_tot").attr("value");
		//conc e' in ng/uL, vol e' in uL
		var tot_generale=volume*(conc/1000);
		var tot_presunto=0.0;
		for(j=0;j<num_aliq;j++){
			tot_aliq=vett_vol[j]*(vett_conc[j]/1000);
			//calcolo i ugr totali
			tot_presunto=tot_presunto+tot_aliq;
		}

		//se creo solo un'aliquota
		if (num_aliq==0){
			tot_presunto=volume0*(conc0/1000);
			if (tot_presunto>tot_generale){
				blocca=true;
			}
			vett_vol[0]=volume0;
			vett_conc[0]=conc0;
		}
		//informazioni per lo spipettamento
	    var numero_ali=$("#numero_aliq_spip").attr("value");

	    if((num_aliq+1)<=parseInt(numero_ali)){
	    	var perc=$("#perc_spip_inf").attr("value");
	    }
	    else{
	    	var perc=$("#perc_spip_sup").attr("value");
	    }

	    var num_aliquote=$("#id_number_aliquots").attr("value");
    	//il primo elemento della lista non � fra i th voluti, quindi lo salto sempre
    	var lista_th=$("#aliq tr:first th");

    	for(i=0;i<num_aliq;i++){
    		vol[i]=parseFloat(vol[i]).toFixed(2);
	    	conce[i]=parseFloat(conce[i]).toFixed(1);

        	if ((parseFloat(vett_vol[i])!=parseFloat(vol[i]))||(parseFloat(vett_conc[i])!=parseFloat(conce[i]))){        		
        		//calcolo i ugr di quel campione
        		var ugr_singola_prov=vett_vol[i]*(vett_conc[i]/1000);
        		//aggiungo lo spipettamento
        		var ugr_effett=ugr_singola_prov+(ugr_singola_prov*perc/100.0);
        		
        		tot_generale=tot_generale-ugr_effett;
        		//sottraggo i ugr al totale da calcolare
        		tot_presunto=tot_presunto-ugr_effett;
        		//diminuisco il numero delle aliq da creare perch� una � gia'
        		//sistemata
        		num_aliquote=parseInt(num_aliquote)-1;      		
        	}
        	
    	}
    	var estremo_inf=parseInt(num_aliquote)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0);
        var estremo_sup=(parseInt(num_aliquote)+4)*parseFloat(vol_aliq)*(parseFloat(conc_aliq)/1000.0);
        var tot_presunto_finale=tot_presunto+(tot_presunto*perc/100.0);
    	if (conc>=conc_aliq){
    		if (tot_generale>=estremo_inf){
			    if (tot_presunto_finale>tot_generale){
			    	blocca=true;
			    }
    		}
    		else{
    			if (tot_generale<0){
			    	blocca=true;
    			}
    		}
    	}
    	else{
    		if (tot_generale<0){
		    	blocca=true;
			}
    	}
    	
    	if (blocca==true){
    		alert("Unable to recalculate values. You haven't enough material to create these aliquots.");
    	}
    	else{
	    	/*var vv=parseFloat(volume0);
	    	var volum0=vv.toFixed(2);
	    	var cc=parseFloat(conc0);
	    	var con0=cc.toFixed(1);

	    	for(i=0;i<num_aliq;i++){
	    		//creo il nome dell'input
	        	var volu="#volume_"+i;
	        	var concen="#concentration_"+i;
	        	$(volu).attr("value",volum0);
	        	$(concen).attr("value",con0);
	    	}*/
    		for(i=0;i<num_aliq;i++){
        		vol[i]=parseFloat(vol[i]).toFixed(2);
    	    	conce[i]=parseFloat(conce[i]).toFixed(1);

            	if ((parseFloat(vett_vol[i])!=parseFloat(vol[i]))||(parseFloat(vett_conc[i])!=parseFloat(conce[i]))){        		
            		//calcolo i ugr di quel campione
            		var ugr_singola_prov=vett_vol[i]*(vett_conc[i]/1000);
            		//aggiungo lo spipettamento
            		var ugr_effett=ugr_singola_prov+(ugr_singola_prov*perc/100.0);
            		//cambio il colore dell'aliquota perche' e' stata modificata a mano
            		if (i==0){
            			$(lista_th[i+1]).css("background-color","red");
            		}
            		else if(i==1){
            			$(lista_th[i+1]).css("background-color","#00CCFF");
            		}
            		else if(i==2){
            			$(lista_th[i+1]).css("background-color","#936EB8");
            		}
            		else if(i==3){
            			$(lista_th[i+1]).css("background-color","yellow");
            		}
            		else{
            			$(lista_th[i+1]).css("background-color","#FF6666");
            		}
            		//devo vedere il volume che devo prendere dalla madre per avere
            		//questi ugr
            		var volu_m=ugr_effett/(conc/1000.0);
            		//calcolo la quantita' di acqua per la diluizione
            		var acqu=(conc/vett_conc[i]*volu_m)-volu_m;
	        		var madre="#moth_"+i;
	        		var acq="#h2o_"+i;
	        		volu_m=parseFloat(volu_m).toFixed(2);
	    			acqu=parseFloat(acqu).toFixed(2);
	        		$(madre).attr("value",volu_m);
	        		$(acq).attr("value",acqu);	        		
	        		
	        		//azzero il valore dei vettori per fare in modo che nei calcoli 
	        		//successivi questa aliquota non venga considerata
	        		vett_vol[i]=0.0;
	        		//vett_conc[i]=0.0;
	        		prov_bloccate[i]=1;
            	}
            	else{
            		//rimetto il colore verde all'aliquota
            		var stringa_al="Aliquot "+String(i+1);
            		$(lista_th[i+1]).css("background-color","#FFD199");
            		prov_bloccate[i]=0;
            	}
    		}
	    	//prendo la concentrazione dell'ultima aliquota che fa da riserva
	    	var conc_ultima="#concentration_"+(num_aliq);
	        var c_ultima=$(conc_ultima).attr("value");
	        //sono i ugrammi che ho nelle aliq create a cui devo sommare la percentuale
			var ugr=tot_presunto;
			var ugrfinali=ugr+(ugr*perc/100.0);  
			//tot sono i ugr totali della sol madre
			var volback=(tot-ugrfinali)/(c_ultima/1000); //(ug tot - ug presi)/conc originaria in ug/uL
			//w_sol=volume-volback;
	        //w_h2o=(w_sol*(conc/conc0))-w_sol;
	        b_sol=volback;
	        b_h2o=0.0;
	        var cback=c_ultima;

	        //var estremo_sup=$("#interv_sup").attr("value");
	        //var estremo_inf=$("#interv_inf").attr("value");
	        //if (protocollo=="DNA"){
				
				//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,1000.0,100,60,ugr,c_ultima,perc,volback,cback);
	        if (num_aliq!=0){
	        	copia_e_ricalcola(conc,volume,volume0,conc0,parseFloat(tot_generale),parseFloat(conc_aliq),parseFloat(estremo_sup),parseFloat(estremo_inf),ugr,c_ultima,perc,volback,cback,vett_vol,vett_conc,num_aliquote);
	        }
	        else{
	        	//calcolo i ugr di quel campione
        		var ugr_singola_prov=vett_vol[i]*(vett_conc[i]/1000);
        		//aggiungo lo spipettamento
        		var ugr_effett=ugr_singola_prov+(ugr_singola_prov*perc/100.0);
        		
        		//devo vedere il volume che devo prendere dalla madre per avere
        		//questi ugr
        		var volu_m=ugr_effett/(conc/1000.0);
        		//calcolo la quantita' di acqua per la diluizione
        		var acqu=(conc/vett_conc[i]*volu_m)-volu_m;
        		var madre="#moth_"+i;
        		var acq="#h2o_"+i;
        		volu_m=parseFloat(volu_m).toFixed(2);
    			acqu=parseFloat(acqu).toFixed(2);
        		$(madre).attr("value",volu_m);
        		$(acq).attr("value",acqu);	        		
	        }
	        	//calcola_inizio(num_aliquote,volume,conc,parseFloat(tot_generale),parseFloat(vol_aliq),parseFloat(conc_aliq),parseFloat(estremo_sup),parseFloat(estremo_inf),ugrtot,concnuova,perc);
	        	/*if (conc>=1000.0){
	        		if (tot_generale>=100){
	                    b_h2o=0.0;
	                }
	        		else if ((tot_generale<=100) && (tot_generale>=60)){
	        			c="#concentration_"+(num_aliq);
	        			var conc6=$(c).attr("value");
	        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
	        			//volback=b_h2o+b_sol;
	        			b_sol=0.0;
	        			w_sol=$("#id_work_al_sol").attr("value");
	        			w_h2o=$("#id_work_al_h2o").attr("value");
	                }
	        		else{
	        			b_h2o=0.0;
	        			b_sol=0.0;
	        			w_sol=volume;
	        			w_h2o=0.0;
	        			volback=volume0;
	        			cback=conc0;
	        		}
	        	}
	        	else{
	        		b_h2o=0.0;
	        		b_sol=0.0;
	        		w_sol=volume;
	        		w_h2o=0.0;
	        		volback=volume0;
	        		cback=conc0;
	        	}*/
	    	//}
			//if (protocollo=="RNA"){
				//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,500.0,50,30,ugr,c_ultima,perc,volback,cback);
				/*if (conc>=500.0){
	        		if ((tot_generale<=50) && (tot_generale>=30)){
	        			c="#concentration_"+(num_aliq);
	        			var conc6=$(c).attr("value");
	        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
	        			//volback=b_h2o+b_sol;
	        			b_sol=0.0;
	        			w_sol=$("#id_work_al_sol").attr("value");
	        			w_h2o=$("#id_work_al_h2o").attr("value");
	                }
	        		else if(tot_generale<30){
	        			b_h2o=0.0;
	        			b_sol=0.0;
	        			w_sol=volume;
	        			w_h2o=0.0;
	        			volback=volume0;
	        			cback=conc0;
	        		}
	        	}
	        	else{
	        		b_h2o=0.0;
	        		b_sol=0.0;
	        		w_sol=volume;
	        		w_h2o=0.0;
	        		volback=volume0;
	        		cback=conc0;
	        	}*/
	    	//}
			//if (protocollo=="cRNA"){
				//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,250.0,25,15,ugr,c_ultima,perc,volback,cback);
				/*if (conc>=250.0){
	        		if ((tot_generale<=25) && (tot_generale>=15)){
	        			c="#concentration_"+(num_aliq);
	        			var conc6=$(c).attr("value");
	        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
	        			//volback=b_h2o+b_sol;
	        			b_sol=0.0;
	        			w_sol=$("#id_work_al_sol").attr("value");
	        			w_h2o=$("#id_work_al_h2o").attr("value");
	                }	
	        		else if(tot_generale<15){
	        			b_h2o=0.0;
	        			b_sol=0.0;
	        			w_sol=volume;
	        			w_h2o=0.0;
	        			//volback=volume0;
	        			//cback=conc0;
	        		}
	        	}
	        	else{
	        		b_h2o=0.0;
	        		b_sol=0.0;
	        		w_sol=volume;
	        		w_h2o=0.0;
	        		//volback=volume0;
	        		//cback=conc0;
	        	}*/
	    	//}
			//if (protocollo=="cDNA"){
				//copia_e_ricalcola(conc,volume,volume0,conc0,tot_generale,300.0,30,18,ugr,c_ultima,perc,volback,cback);
				/*if (conc>=300.0){
	        		if ((tot_generale<=30) && (tot_generale>=18)){
	        			c="#concentration_"+(num_aliq);
	        			var conc6=$(c).attr("value");
	        			//b_h2o=(b_sol*(conc/conc6))-b_sol;
	        			//volback=b_h2o+b_sol;
	        			b_sol=0.0;
	        			w_sol=$("#id_work_al_sol").attr("value");
	        			w_h2o=$("#id_work_al_h2o").attr("value");
	                }	
	        		else if(tot_generale<18){
	        			b_h2o=0.0;
	        			b_sol=0.0;
	        			w_sol=volume;
	        			w_h2o=0.0;
	        			volback=volume0;
	        			cback=conc0;
	        		}
	        	}
	        	else{
	        		b_h2o=0.0;
	        		b_sol=0.0;
	        		w_sol=volume;
	        		w_h2o=0.0;
	        		volback=volume0;
	        		cback=conc0;
	        	}*/
	    	//}
	    	
	    }
	}
}

function cambia_prot(){
	var idprot=$(this).children(":selected").attr("value");
	var urlprot=base_url+"/api/derived/calculate/"+idprot;
	$.getJSON(urlprot,function(d){
		if(d.data!="errore"){
			var stringa=d.riga.split(";");
			$("#proto").attr("value",stringa[0]);
			$("#id_number_aliquots").attr("value",stringa[1]);
			$("#numero_aliq_tot").attr("value",stringa[1]);
			$("#volume_aliq").attr("value",stringa[2]);
			$("#conc_aliq").attr("value",stringa[3]);
			//$("#interv_sup").attr("value",stringa[4]);
			//$("#interv_inf").attr("value",stringa[5]);
			$("#numero_aliq_spip").attr("value",stringa[4]);
			$("#perc_spip_sup").attr("value",stringa[5]);
			$("#perc_spip_inf").attr("value",stringa[6]);
		}
		else{
			alert("Select protocol");
		}
	});
}

$(document).ready(function () {
	
	$("#calcola").click(function(event){
		event.preventDefault();
		aggiungi_campi_tabella();
	});
	
	$("#ricalcola").click(function(event){
		event.preventDefault();
		copia_valori_ricalcola();
	});
	
	$("#id_number_aliquots").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_campi_tabella();
		}
	});
	
	$("#scelta_prot").change(cambia_prot);
	
});