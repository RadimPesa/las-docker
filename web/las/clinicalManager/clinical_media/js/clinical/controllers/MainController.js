/*

app.controller('TypeaheadCtrl', ['$scope', 'getPatient',function($scope, getPatient) {



  $scope.selected = "";
  $scope.getGet = function(val) {
  getPatient.makeMyCall(val).success(function(data) {
      $scope.users = data;
  });
  };




}]);
*/

app.controller('TypeaheadCtrl', ['$scope', '$http', '$window','$cookieStore', function($scope, $http, $window, $cookieStore) {

  $scope.selected = undefined;

  $scope.getPatients = function(val) {
    return $http.get('api/patient_for_client/', {
      params: {
        details: val
      }
    }).then(function(response){
      return response.data/*.map(function(item){
        return item.firstName+ ' ' + item.lastName;
      });*/
  });
  };

  $scope.go = function ( patientId ) {

    $window.location.href  = 'patientHome'
    $cookieStore.put('patient_id', patientId);
    console.log(patientId)
  };

}]);
