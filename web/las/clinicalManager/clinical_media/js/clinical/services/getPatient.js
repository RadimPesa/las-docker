/*app.factory('getPatient', ['$http', function($http) { 


    function myInternal(arg1) {
        return $http.get('api/patient/?firstName=' + arg1) 
            .success(function(data) { 
              return data; 
            }) 
            .error(function(err) { 
              console.log("failed to fetch typeahead data");
              return err; 
            });
    }
    return {
        makeMyCall: function(arg1) {
            return myInternal(arg1);
        }
    };

}]);

*/