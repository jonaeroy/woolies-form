angular.module('app.controllers').controller('DashboardCtrl', function($scope, $location, DashboardSvc){
    "use strict";
    //variables
    $scope.dashboard_data = {};
    $scope.title = '';
    
    $scope.load_settings = function(){
	DashboardSvc.load_settings()
	    .success(function(data){
		$scope.dashboard_data = data;
		$scope.title = data.title;
		console.log(data);
	    })
	    .error(function(){
		alert('Errors!');
	    })
	    
    }

    $scope.init = function(){
	$scope.load_settings();
    }
});

