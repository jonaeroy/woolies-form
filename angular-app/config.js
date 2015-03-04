angular.module('app.routes', ['ngRoute'])
    .controller('MainController', function($scope, $route, $routeParams, $location) {
	$scope.$route = $route;
	$scope.$location = $location;
	$scope.$routeParams = $routeParams;
    })

    .config(function($routeProvider, $locationProvider) {
	$routeProvider
	    .when('/list', {
		templateUrl: '/ng/templates/bnlds/list.html',
		controller: 'newBnldsRequestCtrl'
	    })
        .when('/add', {
        templateUrl: '/ng/templates/bnlds/bnldform.html',
        controller:'newBnldsRequestCtrl'

        })
        .when('/edit/:key',{
        templateUrl: '/ng/templates/bnlds/bnldform.html',
        controller:'editBnldsCtrl'
        })
	    .otherwise({
		redirectTo: '/list'
	    });

	// configure html5 to get links working on jsfiddle
	$locationProvider.html5Mode(false);
    });
