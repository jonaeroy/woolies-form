angular.module('app.controllers').controller('BnldsCtrl', function($scope, BnldsSvc){
    "use strict";
    //variables

    $scope.bnlds = {};
    //select options variables
    $scope.choices = ["Yes", "No","N/A"];
    //ng-options = "choice for choice in choices track by choice" ng-model="default_choice"
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
