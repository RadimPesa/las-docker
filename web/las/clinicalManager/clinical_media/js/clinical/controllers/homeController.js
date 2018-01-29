app.controller('homeCtrl', ['$scope', '$cookieStore', '$http', function($scope, $cookieStore, $http) {

  var patient_id = $cookieStore.get('patient_id');
  console.log(patient_id)


  $http.get("/clinical/corePatient/api/patient_for_client/"+patient_id+"/")
    .success(function(response) {
      $scope.patient = response;
      //console.log($scope.patient.firstName);
    }

      );


  //console.log($scope.patient.lastName)




}]);
