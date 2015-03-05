angular.module('app.controllers').controller('newCourierbooksCtrl', function($scope, $location, $log, CourierbookSvc){
    "use.strict"

    $scope.Courierbooks = {};
    $scope.courierbooks_list = [];

    $scope.list_all = function(){
    CourierbookSvc.list_all()
        .success(function(data, status){
        $scope.courierbooks_list = data.items;
        $scope.total_items = data.items.length;
        console.log(data.items);
        })
        .error(function(data, status){
        alert('Error Accessing Dans Request Lists!');
        });
    };

    CourierbookSvc.all_list()
        .success(function(data, status){
            $scope.store_details = data.items;
            console.log($scope.store_details);
            })
        .error(function(data, status){
            alert('Error Accessing Create Request!');
            });

    CourierbookSvc.costcentres()
        .success(function(data, status){
            $scope.costcentres = data;
            // console.log($scope.costcentres);
            })
            .error(function(data, status){
            alert('Error Accessing Create Request!');
            });

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
             CourierbookSvc.get_store_details(storeNum)
                             .success(function(data, status, headers, config){
                                console.log(data);
                                 if(status == 200){
                                    if(storeDetails == 'pickup'){
                                        $scope.courierbooks['store_name_pick_up'] = data[0].name;
                                        $scope.courierbooks['address1_pick_up'] = data[0].address1;
                                        $scope.courierbooks['address2_pick_up'] = data[0].address2;
                                        $scope.courierbooks['suburb_pick_up'] = data[0].suburb;
                                        $scope.courierbooks['state_pick_up'] = data[0].state;
                                        $scope.courierbooks['post_code_pick_up'] = data[0].postcode;
                                    }
                                    else if(storeDetails == 'dest'){
                                        $scope.courierbooks['store_name_dest'] = data[0].name;
                                        $scope.courierbooks['address1_dest'] = data[0].address1;
                                        $scope.courierbooks['address2_dest'] = data[0].address2;
                                        $scope.courierbooks['suburb_dest'] = data[0].suburb;
                                        $scope.courierbooks['state_dest'] = data[0].state;
                                        $scope.courierbooks['post_code_dest'] = data[0].postcode;
                                    }

                                }
                            }).error(function(data, status, headers, config){
                                //alert("not okay");

    });

    /*create request form modal*/
    $scope.open = function (size) {
        $scope.courierbooks = {};
        $scope.courierbooks_list = [];
        $scope.costcentres = [];
        $scope.store_details = {};



    };
    }


    $scope.ok = function () {
    //do create new request service here
    console.log($scope.courierbooks);
    CourierbookSvc.create($scope.courierbooks)
            .success(function(data, status){
                console.log(data);
                $location.path("#courierbooks");

            })
            .error(function(data,status){
                console.log("Error");
            });

    //$scope.list_all();
    }

    CourierbookSvc.list_all()
        .success(function(data, status){
        $scope.courierbooks_list = data.items;
        $scope.total_items = data.items.length;
        console.log(data.items);
        })
        .error(function(data, status){
        alert('Error Accessing Dans Request Lists!');
        });

});

angular.module('app.controllers').controller('courierbookingview_ctrl', function ($scope, $routeParams, CourierbookSvc) {
    $scope.courierbook_details = {};

    CourierbookSvc.get($routeParams.key)
        .success(function(data, status){
        $scope.courierbook_details = data;
            console.log(data);
        })
        .error(function(data,status){

        });
});

angular.module('app.controllers').controller('editCtrl', function($scope, $routeParams, $location, $log, CourierbookSvc){
    "use.strict"
    $scope.courierbook_details = {};

    CourierbookSvc.costcentres()
    .success(function(data, status){
        $scope.costcentres = data;
        // console.log($scope.costcentres);
        })
        .error(function(data, status){
        alert('Error Accessing Create Request!');
        });

    CourierbookSvc.get($routeParams.key)
        .success(function(data, status){
        $scope.courierbook_details = data;
            console.log(data);
        })
        .error(function(data,status){

        });

    $scope.update = function () {
    // update data
    CourierbookSvc.update($scope.courierbook_details)
        .success(function(data, status){
        $scope.courierbook_details = data;
            console.log(data);
            $location.path("#courierbooks");
        })
        .error(function(data,status){

        });
    }
});
