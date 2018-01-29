(function ( $ ) {

    $.fn.boxlist = function(options) {

        function insertValues(value_array) {
            var invalid = [];
            for (var i=0; i < value_array.length; ++i) {
                if (value_array[i] != "" && itemcontainer.find(".boxlistitem").map(function() {if ($(this).text() == value_array[i]) return this}).length == 0) { // text box is not empty and element isn't already in the list
                    if (conf.fnValidateInput(value_array[i]) == true) {
                        itemcontainer.append('<span class="boxlistitem">'+value_array[i]+'<span class="boxlistdel ui-icon ui-icon-closethick"></span></span>');
                        //itemcontainer.find('span.boxlistdel').last().click(function() {
                        //    $(this).parent().remove();
                        //});
                    } else {
                        invalid.push(value_array[i]);
                    }
                }
            }
            return invalid;
        };

        if (options === 'getValues') {
            if (this.data("boxlist")) {
                return this.data("boxlist-conf").oContainerEl.find("div.boxlist div.itemcontainer").children(".boxlistitem").map(function() {return $(this).text()}).get();
            }
        }

        else
        if (options === 'clearValues') {
            if (this.data("boxlist")) {
                this.data("boxlist-conf").oContainerEl.find("div.boxlist div.itemcontainer").children(".boxlistitem").remove();
            }
            return this;
        }

        else {

            var conf = {
                bMultiValuedInput: false,
                oBtnEl: this.siblings('.add_btn').first(),
                oContainerEl: this.parent(),
                fnParseInput: null,
                fnEachParseInput: null,
                aoAltInput: [],
                fnValidateInput: function(v) {return true},
            };
            conf = $.extend(conf, options);

            conf.fnParseInput = conf.fnParseInput ?
                                    conf.fnParseInput : 
                                    (conf.bMultiValuedInput ?
                                        (conf.fnEachParseInput ?
                                            function(val) {return val.split(/\s+/g).map(conf.fnEachParseInput);} :
                                            function(val) {return val.split(/\s+/g);}) :
                                        function(val) {return [val];});

            var p = $('<div class="boxlist" id="' + this.attr('id') + '_list"><p class="boxlisttitle">Values<span class="listdel">CLEAR</span></p></div>');
            conf.oContainerEl.append(p);
            var itemcontainer = $('<div class="itemcontainer"></div>');
            p.append(itemcontainer);
            itemcontainer.on("click", "span.boxlistdel", function() {$(this).parent().remove();});
            var inputEl = this;

            conf.oContainerEl.find("span.listdel").click(function() {
                conf.oContainerEl.find("div.boxlist div.itemcontainer").children(".boxlistitem").remove();
            });
            
            inputEl.keypress(function(event){
        		if ( event.which == 13 ) {
        			var value_array = conf.fnParseInput(inputEl.val());
                    var invalid = insertValues(value_array);
                    if (invalid.length > 0) {
                        alert("Invalid values were found!","Warning", "Ok");
                    }
                    inputEl.val(invalid.join(" ")).focus();        			
        		}
        	});

            conf.oBtnEl.click(function() {
                var value_array = conf.fnParseInput(inputEl.val());
                var invalid = insertValues(value_array);
                if (invalid.length > 0) {
                    alert("Invalid values were found!","Warning", "Ok");
                }
                inputEl.val(invalid.join(" ")).focus();
            });

            for (var i = 0; i < conf.aoAltInput.length; ++i) {
                conf.aoAltInput[i].oBtnEl.click((function(index) {
                    return function() {
                        var value_array = conf.aoAltInput[index].fnParseInput();
                        insertValues(value_array);
                    }
                }) (i));
            }
            
            // save status
            this.data("boxlist", true);
            this.data("boxlist-conf", conf);

            return this;
        }
   
    }
} ( jQuery ));
