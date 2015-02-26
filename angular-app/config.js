angular.module('app.routes', ['ngRoute'])
    .controller('MainController', function($scope, $route, $routeParams, $location) {
	$scope.$route = $route;
	$scope.$location = $location;
	$scope.$routeParams = $routeParams;
    })

    .config(function($routeProvider, $locationProvider) {
	$routeProvider
	    .when('/', {
		templateUrl: '/ng/templates/layouts/dashboard.html',
		controller: 'MainController'
	    })
	    .otherwise({
		redirectTo: '/'
	    });

	// configure html5 to get links working on jsfiddle
	$locationProvider.html5Mode(false);
    });
