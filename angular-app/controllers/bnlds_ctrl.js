angular.module('app.controllers').controller('newBnldsRequestCtrl', function($scope, $location, $modal, $log, BnldsSvc){
    "use.strict"

    $scope.bnlds={};
    $scope.items = ["dsd"];

    //list pagination variables
    $scope.max_size = 5;
    $scope.total_items = 0;
    $scope.current_page = 1;
    $scope.items_per_page = 8;
    
    
    $scope.create = function(){
        BnldsSvc.create($scope.bnlds)
            .success(function(data, status){
                console.log(data);
            })
            .error(function(data,status){

            });

    };

    //view

    $scope.view = function(key, size){
	var modalInstance = $modal.open({
	    templateUrl: '/ng/templates/bnlds/view.html',
	    controller: 'BnldDetailsCtrl',
	    size: size,
	    resolve: {
		key: function () {
		    return key;
		}
	    }
	});

	modalInstance.result.then(function (bnlds_list) {
	}, function () {
	    $log.info('Modal dismissed at: ' + new Date());
	});
    };

    
    $scope.bnlds_list = [];
    $scope.sliced_bnlds_list
    
    $scope.list_all = function(){
	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
		$scope.total_items = data.items.length;
		$scope.pageChange();
		console.log($scope.total_items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    });
    };

    //edit
    $scope.edit = function(key){
	var modalInstance = $modal.open({
	    templateUrl: '/ng/templates/bnlds/bnldform.html',
	    controller: 'BnldEditCtrl',
	    size: 'md',
	    resolve: {
		key: function () {
		    return key;
		}
	    }
	});

	modalInstance.result.then(function (bnlds_list) {
	    $scope.bnlds_list = bnlds_list;
	    $scope.list_all();
	}, function () {
	    $log.info('Modal dismissed at: ' + new Date());
	    $scope.list_all();
	});

    };

    //request list pagination
    $scope.pageChange = function(){
	var start = ($scope.current_page-1)*$scope.items_per_page;
	var end = start + $scope.items_per_page;
	$scope.sliced_bnlds_list = $scope.bnlds_list.slice(start, end);
	$log.log(start + " : " + end);
    };

    /*create request form modal*/
    $scope.open = function (size) {
	var modalInstance = $modal.open({
	    templateUrl: '/ng/templates/bnlds/bnldform.html',
	    controller: 'BnldFormCtrl',
	    size: size,
	    resolve: {
		items: function () {
		    return $scope.items;
		}
	    }
	});

	modalInstance.result.then(function (bnlds_list) {
	    $scope.bnlds_list = bnlds_list;
	    $scope.list_all();
	}, function () {
	    $log.info('Modal dismissed at: ' + new Date());
	    $scope.list_all();
	});
    };

});


angular.module('app.controllers').controller('BnldFormCtrl', function ($scope, $modalInstance, items, BnldsSvc) {

    $scope.bnlds = {};
    $scope.choices=["Yes","No","N/A"];
    $scope.bnlds_list = [];
    $scope.ok = function () {
	//do create new request service here
	BnldsSvc.create($scope.bnlds)
            .success(function(data, status){
                console.log(data);
            })
            .error(function(data,status){

            });

	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
		console.log(data.items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    });
	
	$modalInstance.close($scope.bnlds_list);
    };

    $scope.cancel = function () {
	$modalInstance.dismiss('cancel');
    };
});


angular.module('app.controllers').controller('BnldDetailsCtrl', function ($scope, $modalInstance, key, BnldsSvc) {
    $scope.bnld_details = {};

    BnldsSvc.get(key)
        .success(function(data, status){
	    $scope.bnlds_details = data;
            console.log(data);
        })
        .error(function(data,status){

        });

    
    
    $scope.cancel = function () {
	$modalInstance.dismiss('cancel');
    };
});


angular.module('app.controllers').controller('BnldEditCtrl', function ($scope, $modalInstance, key, BnldsSvc) {
    $scope.bnlds = {};
    $scope.choices = ["Yes","No","N/A"];
    $scope.bnlds_list = [];
    BnldsSvc.get(key)
        .success(function(data, status){
	    $scope.bnlds = data;
            console.log(data);
        })
        .error(function(data,status){

        });

    
    
    $scope.ok = function () {
	BnldsSvc.update($scope.bnlds)
	    .success(function(data,status){
		
	    })
	    .error(function(data, status){

	    });

	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
		console.log(data.items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    });

	$modalInstance.close(key);
    };

    $scope.cancel = function () {
	$modalInstance.dismiss('cancel');
    };
});
