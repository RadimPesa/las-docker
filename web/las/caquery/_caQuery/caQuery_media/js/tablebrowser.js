$(function() {
    initCsrf();
    inithandlers();
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
    detailsDt = $("#tdetails").dataTable({bFilter: false, bLengthChange: false, bPaginate: false, bInfo: false, bSort: false});
}

function inithandlers() {
    $("#selds").change(
        function() {
            detailsDt.fnClearTable();
            var ds = $("#selds").val();
            if (ds == null) return;
            $.ajax({
                url: "./",
                data: "ds="+ds,
                success: function(data) {
                    data = JSON.parse(data);
                    $("#seldst option").remove();
                    for (i = 0; i < data.length; ++i) {
                        $("#seldst").append('<option value="' + data[i][0] + '">' + data[i][1] + '</option>');
                    }
                    $("#seldst").prop('selectedIndex', -1);
                },
                error: function(data) {
                    alert("Error: failed to connect to server!");
                }
            });
        }
    );
}


