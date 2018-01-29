(function(){ //Wrapping your Javascript in a closure is a good habit!

    angular.module('crf', [ 'ui.bootstrap', 'xeditable' ])

    .factory('httpRequestInterceptor', function () {
      return {
        request: function (config) {
            config.headers['LasFunctionality'] = 'can_view_CMM_Case_Report_Form';
          return config;
        }
      };
    })

    .run(function(editableOptions) {
        editableOptions.theme = 'bs3';
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

    .directive('crfPanels', function(){
        return {
            restrict: 'E',
            templateUrl: static_media('js/clinical/crf/tab-template.html'),

            controller: ['$rootScope', '$scope', '$window', '$filter',  function($rootScope, $scope, $window, $filter) {
                pn = this;
                //pn.tab = 1;
                // dnamic init
                if ($window.sessionStorage.getItem('patient') == null) {
                    pn.tab = 1; // init
                } else {
                    pn.tab = 2; // init
                }

                pn.selectTab = function(setTab) {
                    pn.tab = setTab;
                };

                pn.isSelected = function(checkTab) {
                    return pn.tab === checkTab;
                };

                pn.ignorePatientChanges = function( ) {
                    pn.patient = JSON.parse($window.sessionStorage.getItem('patient'));
                };

                $scope.$watch(function() {
                    return pn && pn.patient && pn.patient.birthDate;
                },function(n,o){
                    if (n != null) {
                        var dateView = $filter('date')(n, 'yyyy-MM-dd');
                        pn.patient.birthDate = dateView;
                    } else {
                        //do nothing
                    }
                });


                $scope.$watch(function () {
                    return $window.sessionStorage.getItem('patient');
                }, function (value) {
                    pn.patient = JSON.parse(value);
                    //pn.patient.birthDate = new Date(pn.patient.birthDate);
                    $rootScope.$broadcast('patientChanged', pn.patient);
                });
            }],
            controllerAs: 'panels'
        };
    })

    // filter method, creating `getNameOrAnonymous` a globally
    // available filter in our `app` module
    .filter('getNameOrAnonymous', function () {
        // function that's invoked each time Angular runs $digest()
        // pass in `item` which is the single Object we'll manipulate
        return function (item) {
            // return the current `item`, but call `toUpperCase()` on it
            if (item.some(function(s) {return !s} ) ) {
                return 'Anonymous Patient';
            }
            else {
                return item.join(' ');
            }
        };
    })

    .filter('diseaseStatus', function () {
        return function (item) {
            // return the current `item`, but call `toUpperCase()` on it
            if (item) {
                return 'Active';
            } else {
                return 'Ended'
            }
        };
    })

    .controller('PatientSelectionController', ['$http', '$window',  function($http, $window) {

        var psc = this;
        psc.selected = undefined;

        psc.getPatients = function(val) {
            return $http.get('api/patient_for_client/', {
                params: {
                    details: val
                }
            }).then(function(response){
                return response.data;
            });
        };

        psc.selectByPersonalData = function ( patientObject ) {
            console.log(patientObject)
            $window.sessionStorage.setItem("patient", JSON.stringify(patientObject));
        };
    }])

    .controller('PatientDetailsController', ['$scope', '$http', function($scope, $http) {

        var pdc = this;
        pdc.popOverTemplate = static_media('js/clinical/crf/trial-popover-template.html');
        pdc.projects = [];

        pdc.getDetails = function(val) {
            return $http.get('../coreProject/api/enrollmentsList/'+val+"/").then(function(response){
                pdc.projects = response.data;
            });
        };

        $scope.$on('patientChanged', function(event, data) {
            if(data == null){
                // do nothing
            } else {
                pdc.getDetails(data.identifier);
            }

        });

    }])

    .controller('PersonalDetailFormController', ['$scope', '$http', '$window', '$timeout',  function($scope, $http, $window, $timeout) {

        var pdfc = this;
        pdfc.update = false; //init
        pdfc.fiscalCodeAlreadyExists = false;
        //pdfc.modified = undefined;
        pdfc.userInput = undefined;
        pdfc.mergingPatient = undefined;
        pdfc.mergingError = undefined;
        pdfc.time = 0;
        pdfc.maxTime = 10;  // waiting seconds


        pdfc.stop = function(){
            console.log('stop the Timer')
            $timeout.cancel(pdfc.mytimeout);
        }

        pdfc.checkPatientUUID = function(uuid) {

            pdfc.mergingPatient = undefined;
            pdfc.mergingError = undefined;
            pdfc.time = 0;
            pdfc.timer = false;
            pdfc.stop();


            // check if is not the uuid of this Patient
            if (uuid == JSON.parse($window.sessionStorage.getItem('patient')).identifier)  {
                console.log('Same UUID of current Patient');
                $scope.mergingForm.identifier.$setValidity("foo", false);
                return;
            }

            if (uuid == undefined){
                console.log('uuid undefined');
                return;
            }


            return $http.get('../corePatient/api/patient/'+uuid+'/').success(function(response) {
                // existing Patient!!!
                $scope.mergingForm.identifier.$setValidity("foo", true);
                //console.log(response);
                pdfc.mergingPatient = response;

                pdfc.timer = true;


                function countDown(maxSeconds) {

                    if (pdfc.time < maxSeconds) {
                        pdfc.time ++;
                        console.log(pdfc.time);
                        pdfc.mytimeout = $timeout(function(){countDown(maxSeconds);},1000);

                    } else {
                        return;
                    }
                }

                countDown(pdfc.maxTime);




            }).error(function(response) {

                $scope.mergingForm.identifier.$setValidity("foo", false);
                //$scope.enrollForm.iccode.$setValidity("foo", true);
            });
        }

        pdfc.merge = function(uuid) {
            old = JSON.parse($window.sessionStorage.getItem('patient')).identifier;
            payload = JSON.stringify({'new':uuid, 'old': old});
            console.log(payload)

            return $http.put('../corePatient/api/patient_for_client/', payload).success(function(response) {

                $window.sessionStorage.setItem("patient", JSON.stringify(response));
                $('#MergingModal').modal('toggle');



            }).error(function(response) {
                console.log('Error, '+response)
                pdfc.mergingError = response.exception

                //$scope.enrollForm.iccode.$setValidity("foo", true);
            });

        }

        pdfc.checkFiscalCode = function(val) {

            var current_code = JSON.parse($window.sessionStorage.getItem('patient')).fiscalCode;
            pdfc.fiscalCodeAlreadyExists = false;

            if (undefined !== val && val.length === 16 && val != current_code) {

                return $http.get('../corePatient/api/patient/', {
                    params: {
                        details: val,
                        disableGraph: 'true'
                    }
                }).then(function(response) {
                    if (response.data.length === 0) {
                        console.log('fiscal code is brand new');
                        //pdfc.fiscalCodeAlreadyExists = false;
                        $scope.ModForm.fiscalCode.$setValidity("foo", true);
                    } else {
                        pdfc.fiscalCodeAlreadyExists = true;
                        $scope.ModForm.fiscalCode.$setValidity("foo", false);
                    }

                });

            } else {
                //do nothing
                console.log('do nothing');
                //please, note that if the input is not valid, ng-change is not fired
            }
        };

        pdfc.open = function($event) {
            $event.preventDefault();
            $event.stopPropagation();

            pdfc.opened = true;
        };

        pdfc.putDetails = function( patientObject ) {
            pk = patientObject.identifier;
            var vs = patientObject.vitalStatus;
            payload = JSON.stringify(patientObject);
            //console.log(payload);
            //console.log(vs);
            return $http.put('api/patient_classic_rest/'+pk+'/', payload).success(function(response){
                patientObject.vitalStatus = vs;
                $window.sessionStorage.setItem("patient", JSON.stringify(patientObject));
                pdfc.modified = true;
            }).error(function(response){
                pdfc.modified = false;
            });
        };

    }])

    .controller('PathologiesController', ['$http','$scope','$filter', function($http, $scope, $filter) {

    var pc = this;
    pc.oncoPaths = [];
    pc.oncoPathValues = [];
    pc.freeze = false;

    /*$http.get('../coreOncoPath/api/oncoPathDicts/opt/').success(function(data){
        pc.oncoPathValues = data.OncoPathType;
    });*/


    pc.getOncoPath = function(val) {
        return $http.get('../coreOncoPath/api/oncoPath/', {
            params: {
                patient: val
            }
        }).then(function(response){
            pc.oncoPaths = response.data.results;
        });
    };

    pc.addOncoPath = function() {
        pc.inserted = {
            id:'',
            identifier: '',
            name: '',
            status: true
        };
        pc.oncoPaths.push(pc.inserted);
        pc.freeze = true;
    };

    pc.save = function(oldObject, newValue, patientId) {
        if (!newValue) {
            return "Please, select a Pathology";
        }

        if (oldObject.name == newValue) { // no changes
            // do nothing
            console.log('no changes: do nothing')
            return true;
        }

        if (oldObject.name) { // existing OncoPath
            console.log('change '+oldObject.name+' into '+newValue);
            return $http.put('/clinical/appPathologyManagement/api/oncoPathManagement/'+oldObject.identifier+'/', {
                    operator    : USER,
                    name        : newValue,
                    status      : true//,
                    //patient     : patientId
            }).then(function(res) {
              //return res.data;
                return true;
            }).catch(function(error) {
                return error.data;
            });

        } else { // new OncoPath
            return $http.post('/clinical/appPathologyManagement/api/oncoPathManagement/', {
                    operator    : USER,
                    name        : newValue,
                    status      : true,
                    patient     : patientId
            }).then(function(res) {
              //return res.data;
                console.log(res);
                // bind model with new OncoPath data returned by API (e.g. UUID)
                brand_new_data = pc.oncoPaths[pc.oncoPaths.length - 1];

                brand_new_data.name = res.data.name;
                brand_new_data.status = res.data.status;
                brand_new_data.id = res.data.id;
                brand_new_data.identifier = res.data.identifier;
                return true;
            }).catch(function(error) {
                return error.data;
            });
        }
    };

    pc.canc = function(data) {
        if (!data.name) {
            pc.oncoPaths.splice(pc.oncoPaths.length - 1,1);
        }
    };



    $scope.$on('patientChanged', function(event, data) {
        if(data == null){
            // do nothing
        } else {
            pc.getOncoPath(data.identifier);
        }

    });


    }]);





})(); //Wrapping your Javascript in a closure is a good habit!
