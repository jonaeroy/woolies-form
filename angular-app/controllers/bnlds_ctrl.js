angular.module('app.controllers').controller('newBnldsRequestCtrl', function($scope, $location, $modal, $log, BnldsSvc){
    "use.strict"

    $scope.bnlds={};
    $scope.items = ["dsd"];

    //list pagination variables
    $scope.max_size = 2;
    $scope.total_items = 0;
    $scope.current_page = 1;
    
    
    $scope.create = function(){
        BnldsSvc.create($scope.bnlds)
            .success(function(data, status){
                console.log(data);
            })
            .error(function(data,status){

            })

    };
    
    
    $scope.bnlds_list = [];
    
    $scope.list_all = function(){
	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
		$scope.total_items = data.items.length;
		console.log($scope.total_items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    })
    };

    /*create request form modal*/
    $scope.open = function (size) {
	var modalInstance = $modal.open({
	    templateUrl: '/ng/templates/modal/bnldform.html',
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

            })
	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
		console.log(data.items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    })
	
	$modalInstance.close($scope.bnlds_list);
    };

    $scope.cancel = function () {
	$modalInstance.dismiss('cancel');
    };
});
