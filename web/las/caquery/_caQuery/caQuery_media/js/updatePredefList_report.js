$(function() {
    initCsrf();
    initmisc();
});

function initCsrf() {
    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
      var token;
      if (!options.crossDomain) {
        token = $.cookie("csrftoken");
        if (token) {
          return jqXHR.setRequestHeader('X-CSRFToken', token);
        }
      }
    });
}

function initmisc() {
    //dataDt = $("#data").dataTable({bFilter: false, bLengthChange: false, bPaginate: false, bInfo: false, bSort: false});
    detailsDt = $("#details").dataTable({bFilter: false, bLengthChange: false, bPaginate: false, bInfo: false, bSort: false});

    $("span.edit").addClass("ui-icon ui-icon-pencil");
    $("span.exclude").addClass("no ui-icon ui-icon-check");

    $("span.edit").click(function() {
        var vid = $(this).data("vid");
        var inputEl = $("#val" + vid);

        if (inputEl.hasClass("edit")) {
            inputEl.select().focus();
            return;
        }

        var oldVal = inputEl.val();
        inputEl.addClass("edit").attr("readonly", false).select().focus();
        var spanOk = $("<span class='edit ui-icon ui-icon-circle-check'></span>");
        var spanCancel = $("<span class='edit ui-icon ui-icon-circle-close'></span>");
        spanOk.click(function() {
            // save new value
            $.ajax({
                url: "./",
                type: "post",
                data: {
                    action: "updateval",
                    vid: vid,
                    valueForDisplay: inputEl.val()
                },
                success: function(data) {
                    console.log("Saved");
                    inputEl.siblings().remove();
                    inputEl.removeClass("edit").attr("readonly", true);
                    inputEl.parent().animate({"background-color": "#B8DCB8"},"slow").animate({"background-color": "#FFFFFF"},1000)
                },
                error: function(data) {
                    console.log("Error");
                    inputEl.siblings().remove();
                    inputEl.removeClass("edit").attr("readonly", true).val(oldVal);
                    inputEl.parent().animate({"background-color": "#FF7171"},100)
                                    .animate({"background-color": "#FFFFFF"},100)
                                    .animate({"background-color": "#FF7171"},100)
                                    .animate({"background-color": "#FFFFFF"},100)
                                    .animate({"background-color": "#FF7171"},100)
                                    .animate({"background-color": "#FFFFFF"},100);
                }
            });
        });
        spanCancel.click(function() {
            inputEl.siblings().remove();
            inputEl.removeClass("edit").attr("readonly", true).val(oldVal);

        });
        inputEl.after(spanOk).after(spanCancel);
    });

    $("span.exclude").click(function() {
        if ($(this).hasClass("yes")) {
            $(this).removeClass("yes ui-icon ui-icon-close").addClass("no ui-icon ui-icon-check");
            $(this).parent().parent().removeClass("excluded");
            $(this).parent().siblings("td.third").children().show();
        } else {
            $(this).removeClass("no ui-icon ui-icon-check").addClass("yes ui-icon ui-icon-close");
            $(this).parent().parent().addClass("excluded");
            $(this).parent().siblings("td.third").children().hide();
        }
    })

    $("button#finish").click(function() {
        var exclude = $("span.exclude.yes").map(function() {return $(this).data("vid")}).get();
        $("#finishform input[name=exclude]").val(JSON.stringify(exclude));
        finishform.submit();
    })
}
