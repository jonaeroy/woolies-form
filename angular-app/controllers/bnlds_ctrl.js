angular.module('app.controllers').controller('BnldsCtrl', function($scope, BnldsSvc){
    "use strict";
    //variables
    $scope.bnlds = {};
    //select option variables
    $scope.choices = ["Yes", "No", "N/A"];
    //ng-options="choice for choice in choices track by choice" ng-model="default_choice" 
    
    $scope.create = function() {
	BnldsSvc.create($scope.bnlds)
	    .success(function(data, status){
		console.log(data.items);
	    })
	    .error(function(data, status){
		
	    })
    };
    
  $scope.items = [
      {id: 1, name: 'Yes'}
      {id: 2, name: 'No'}
      {id: 3, name: 'N/A'}

  ];
 

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

