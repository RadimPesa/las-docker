(function(){ //Wrapping your Javascript in a closure is a good habit!

    angular.module('list', [ 'smart-table', 'xeditable', 'ui.bootstrap' ])
    .config(['$httpProvider', function($httpProvider) {
        //$httpProvider.defaults.xsrfCookieName = 'csrftoken';
        //$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        $httpProvider.interceptors.push('httpRequestInterceptor');

    }])

    .directive('pageSelect', function() {
          return {
            restrict: 'E',
            template: '<input type="text" class="select-page" ng-model="inputPage" ng-change="selectPage(inputPage)" no-dirty-check>',
            link: function(scope, element, attrs) {
              scope.$watch('currentPage', function(c) {
                scope.inputPage = c;
              });
            }
          }
    })

    .directive('noDirtyCheck', function() {
      // Interacting with input elements having this directive won't cause the
      // form to be marked dirty.
      return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
          ctrl.$pristine = false;
        }
      }
    })


    .factory('httpRequestInterceptor', function () {
      return {
        request: function (config) {
            config.headers['LasFunctionality'] = 'can_view_CMM_Enrollment_list';
          return config;
        }
      };
    })

    .run(function(editableOptions) {
      editableOptions.theme = 'bs3'; // bootstrap3 theme. Can be also 'bs2', 'default'
    })

    // filter method, creating `myCustomFilter` a globally
    // available filter in our module
    .filter('myCustomFilter', ['$filter', function($filter){

        // Removes an element from an array.
        // String value: the value to search and remove.
        // return: an array with the removed element; false otherwise.
        Array.prototype.remove = function(value) {
            var idx = this.indexOf(value);
            if (idx != -1) {
                return this.splice(idx, 1); // The second parameter is the number of elements to remove.
            }
            return false;
        }

        // search for a substring in deep
        function deepSearchInObject(obj, value, excludedTop) {

            var excludedTop = excludedTop || []; // init optional arg
            //console.log(excludedTop);
            var analyzable_keys = Object.keys(obj);
            for (var i=0; i < excludedTop.length; i++){
                analyzable_keys.remove(excludedTop[i]);
            }

            //console.log('Object.keys ' + Object.keys(o));
            return analyzable_keys.some( function(x) {
                //console.log('analyzing ' + x);
                // Recursion for complex type (i.e. Arrays and Objects)
                if (Array.isArray(obj[x]) || typeof obj[x] === 'object' && obj[x] !== null) {
                  return deepSearchInObject(obj[x], value);
                }
                if (obj[x] == null) {
                  //do nothing
                } else {
                  return obj[x].toLowerCase().indexOf(value.toLowerCase()) > -1;
                }
            });
        }

        // function that's invoked each time Angular runs $digest()
        return function(input, predicate){
            searchValue = predicate['$'];
            // predicate function
            var customPredicate = function(value, index, array) {

                // no value from filter, return true for each element of the array
                if (typeof searchValue === 'undefined') {
                    return true;
                }
                excludedValues = ['patientId', 'gender', 'vitalStatus'];
                return deepSearchInObject(value, searchValue, excludedValues);
            };
            //console.log(customPredicate);
            return $filter('filter')(input, customPredicate, false);
        };
    }])

    .controller('SmartTableController', ['$http', '$window', function ($http, $window) {

        var stc = this;
        stc.rowList = [ ];
        stc.fetching = false;
        stc.trials = [ ];
        stc.itemsByPage = 20;

        $http.get('../coreProject/api/project/').success(function(data){
            stc.trials = data;
        });


        stc.fetchData = function(val) {
        /* IMPORTANT: dafault server page_size = 10. I set page_size = 10000 to fetch al the dataset in the firs call */
            stc.fetching = true;
            $http.get('/clinical/coreProject/api/patientListedByProject/',{
                params: {
                        project: val,
                        page_size : 10000
                        }
            }).success(function(data){
                stc.fetching = false;
                stc.rowList = data.results;
                stc.displayedCollection = [].concat(stc.rowList);

                //console.log(stc.rowList);
            });


        };

        stc.updateData = function(patientId, alias, project) {
            return $http.put('/clinical/coreProject/api/localId/', {
                    patientId   : patientId,
                    alias       : alias,
                    project     : project
            }).then(function(res) {
              //return res.data;
                return true;
            }).catch(function(error) {
                return error.data;
            });
        };

        stc.goToCrf = function(id) {
            return $http.get('/clinical/corePatient/api/patient_for_client/'+id+'/'
            ).then(function(response){
                console.log(response);
                sessionData = {};
                sessionData['id'] = response.data['id'];
                sessionData['identifier'] = response.data['identifier'];
                sessionData['firstName'] = response.data['firstName'];
                sessionData['lastName'] = response.data['lastName'];
                sessionData['fiscalCode'] = response.data['fiscalCode'];
                sessionData['birthDate'] = response.data['birthDate'];
                sessionData['birthPlace'] = response.data['birthPlace'];
                sessionData['birthNation'] = response.data['birthNation'];
                sessionData['sex'] = response.data['sex'];
                sessionData['race'] = response.data['race'];
                sessionData['residencePlace'] = response.data['residencePlace'];
                sessionData['residenceNation'] = response.data['residenceNation'];
                sessionData['vitalStatus'] = response.data['vitalStatus'];
                sessionData['mergedList'] = response.data['mergedList'];
                $window.sessionStorage.setItem("patient", JSON.stringify(sessionData));
                //window.location.replace("/clinical/corePatient/crf");
                window.open('/clinical/corePatient/crf','_blank');
            });
        };


    }]);



})(); //Wrapping your Javascript in a closure is a good habit!
