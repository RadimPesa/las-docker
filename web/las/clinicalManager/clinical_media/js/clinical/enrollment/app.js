(function(){ //Wrapping your Javascript in a closure is a good habit!

    angular.module('enrollment', [ 'ui.bootstrap' ])

    .factory('httpRequestInterceptor', function () {
      return {
        request: function (config) {
            config.headers['LasFunctionality'] = 'can_view_CMM_patient_enrollment';
          return config;
        }
      };
    })

    .directive('capitalize', function() {
        return {
          require: 'ngModel',
          link: function(scope, element, attrs, modelCtrl) {
            var capitalize = function(inputValue) {
              if (inputValue == undefined) inputValue = '';
              var capitalized = inputValue.toUpperCase();
              if (capitalized !== inputValue) {
                modelCtrl.$setViewValue(capitalized);
                modelCtrl.$render();
              }
              return capitalized;
            }
            modelCtrl.$parsers.push(capitalize);
            capitalize(scope[attrs.ngModel]); // capitalize initial value
          }
        };
     })


    .controller('FormController', ['$http','$scope','$filter', function($http, $scope, $filter) {

        var fc = this;
        fc.trials = [];
        fc.medicalCenters = [];
        fc.enrollmentData = {};
        fc.icAlreadyExists = false;


        $http.get('../coreProject/api/project/').success(function(data){
            fc.trials = data;
        });

        fc.getMedCent = function(val) {

            $http.get('../coreInstitution/api/institution/'+val+'/').success(function(data){
                fc.medicalCenters = data;
            });

        };

        fc.checkInformedConsent = function(ic, project) {

            // ../coreProject/api/informedConsent/
            return $http.get('../coreProject/api/informedConsent/', {
                params: {
                    ICcode: ic,
                    project: project
                }
            }).success(function(response) {
                // existing IC!!!
                fc.icAlreadyExists = true;
                $scope.enrollForm.iccode.$setValidity("foo", false);
            }).error(function(response) {
                fc.icAlreadyExists = false;
                $scope.enrollForm.iccode.$setValidity("foo", true);
            });
        }

        fc.informedConsentWarning = function(ic) {

            // ../coreProject/api/informedConsent/
            return $http.get('../coreProject/api/informedConsent/', {
                params: {
                    icGlobal: ic
                }
            }).success(function(response) {
                // existing IC!!!
                fc.icWarning = true;
                fc.globalICcodes = response.toString();
                //$scope.enrollForm.iccode.$setValidity("foo", false);
            }).error(function(response) {
                fc.icWarning = false;
                //$scope.enrollForm.iccode.$setValidity("foo", true);
            });
        }

        fc.checkIfExists = function(val) {


            if (undefined !== val && val.length === 16) {

                return $http.get('../corePatient/api/patient/', {
                    params: {
                        details: val,
                        disableGraph: 'true'
                    }
                }).then(function(response) {
                    fc.infoFiscalCode = false;
                    if (response.data.length === 0) {
                        fc.matchingLength = 0;
                    } else {
                        fc.matchingLength = 1;

                        // value pre-selected by user
                        var current_trial = fc.enrollmentData.project;
                        var current_med_cen = fc.enrollmentData.medicalCenter;
                        var current_ic = fc.enrollmentData.ICcode;

                        // get patient data
                        fc.enrollmentData = response.data[0];

                        // re-set pre-selected value
                        fc.enrollmentData.project = current_trial;
                        fc.enrollmentData.medicalCenter = current_med_cen;
                        fc.enrollmentData.ICcode = current_ic;

                    }
                });

            } else {


            }

        }


        fc.open = function($event) {
            $event.preventDefault();
            $event.stopPropagation();

            fc.opened = true;
        };

        fc.clear = function () {
            fc.enrollmentData = { };
            fc.matchingLength = null;
            fc.enrolled = null;
            fc.generalLock = null;
            $scope.enrollForm.$setPristine();
        };

        $scope.$watch(function() {
            return fc.enrollmentData.birthDate;
        },function(n,o){
            var dateView = $filter('date')(fc.enrollmentData.birthDate,'yyyy-MM-dd');
            fc.enrollmentData.birthDate = dateView;
        });


        fc.enroll = function( enrollmentDataObject ) {
            var payload = {};
            var patientsList = [];

            payload.patients = patientsList;
            enrollmentDataObject.operator = USER;//'andrea.mignone';
            //console.log(USER);
            payload.patients.push(enrollmentDataObject);
            payload = JSON.stringify(payload);
            //console.log(payload);
            //fc.matchingLength = 1;
            fc.generalLock = true;

            return $http.post('../appEnrollment/api/enrollment/', payload).success(function(response){
                console.log('enrolled!');
                fc.enrolled = true;

            }).error(function(response){
                //console.log(response);
                fc.enrolled = false;

            });
        };



    }]);





})(); //Wrapping your Javascript in a closure is a good habit!
