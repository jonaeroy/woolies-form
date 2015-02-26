AppUIControllers.controller('newRequestCtrl', function ($scope, $rootScope, $routeParams, $cookies, $cookieStore, $http, $location, NewRequestRest, $modal){
    "use strict";
$scope.message = "hello";
$rootScope.storelist = {};
$rootScope.costcentres = {};
$rootScope.user_fullname = '';

$scope.showRequestForm = function(){
    $scope.getUserFullName();
    $scope.loadCostCentre();
    $scope.loadStore();
    $location.path("newcourierbookrequest");

};
$scope.pickupstore_key = "";
$scope.destinationstore_key = "";

$scope.$watch('pickupstore_key', function(newValue, oldValue) {
    console.log('Selected Store =====> ', newValue);
    $scope.pass_storeKey(newValue, 'pickup');
});

$scope.$watch('destinationstore_key', function(newValue, oldValue) {
    console.log('Selected Store =====> ', newValue);
    $scope.pass_storeKey(newValue, 'dest');
});

$scope.pass_storeKey = function(storeNum, storeDetails){
         NewRequestRest.getStoreDetails(storeNum)
                         .success(function(data, status, headers, config){
                            console.log(data);
                             if(status == 200){
                                if(storeDetails == 'pickup'){
                                    $scope.store_name_pick_up = data[0].name;
                                    $scope.address1_pick_up = data[0].address1;
                                    $scope.address2_pick_up = data[0].address2;
                                    $scope.suburb_pick_up = data[0].suburb;
                                    $scope.state_pick_up = data[0].state;
                                    $scope.post_code_pick_up = data[0].postcode;
                                }
                                else if(storeDetails == 'dest'){
                                    $scope.store_name_dest = data[0].name;
                                    $scope.address1_dest = data[0].address1;
                                    $scope.address2_dest = data[0].address2;
                                    $scope.suburb_dest = data[0].suburb;
                                    $scope.state_dest = data[0].state;
                                    $scope.post_code_dest = data[0].postcode;
                                }

                            }
                        }).error(function(data, status, headers, config){
                            //alert("not okay");

                        });


};
$scope.getUserFullName = function(){
                NewRequestRest.getUserFullName()
                                .success(function(full_name, status, headers, config){
                                    if(status == 200){
                                                $rootScope.user_fullname = full_name;
                                    }
                                }).error(function(data, status, headers, config){
                                   alert("not okay");

                                });
};
$scope.loadCostCentre = function(){
            NewRequestRest.costcentres()
                                .success(function(ccdata, status, headers, config){
                                    if(status == 200){
                                        $rootScope.costcentres = ccdata;
                                    }
                                }).error(function(data, status, headers, config){
                                   alert("not okay");
                                   $rootScope.costcentres = {};

                                });

};
$scope.loadStore = function(){
            NewRequestRest.storelist()
                                .success(function(storedata, status, headers, config){
                                    if(status == 200){
                                        $rootScope.storelist = storedata;
                                    }
                                }).error(function(data, status, headers, config){
                                   alert("not okay");
                                   $rootScope.storelist = {};
                                });

};

});


