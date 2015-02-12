angular.module('app.controllers').controller('BnldsCtrl', function($scope, BnldsSvc){
    "use strict";

    $scope.bnlds = {};
    $scope.create = function() {
	BnldsSvc.create($scope.bnlds)
	    .success(function(data, status){
		console.log(data.items);
	    })
	    .error(function(data, status){
		
	    })
    };


});


angular.module('app.controllers').controller('BnldsListCtrl', function($scope, BnldsSvc){
    $scope.bnlds_items = [];
    BnldsSvc.list()
	.success(function(data, status){
	    $scope.bnlds_items = data.items;
	})
	.error(function(data, status)){
	    alert("Error Occured!");
	}
    
});
