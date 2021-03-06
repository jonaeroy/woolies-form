angular.module('app.routes', ['ngRoute'])
    .controller('MainController', function($scope, $route, $routeParams, $location) {
	$scope.$route = $route;
	$scope.$location = $location;
	$scope.$routeParams = $routeParams;
    })
    .config(function($routeProvider, $locationProvider) {
	$routeProvider
	
	
            .when('/courierbooks', {
		templateUrl: '/ng/templates/courierbooks/list.html',
		controller: 'newCourierbooksCtrl'
            })
            .when('/open', {
		templateUrl: '/ng/templates/courierbooks/courierbookingform.html',
		controller:'newCourierbooksCtrl'

            })
            .when('/edit/:key',{
		templateUrl: '/ng/templates/courierbooks/edit.html',
		controller:'editCtrl'
            })
            .when('/view/:key',{
		templateUrl: '/ng/templates/courierbooks/view.html',
		controller:'courierbookingview_ctrl'
            })
            .otherwise({
		redirectTo: '/courierbooks'
            });


	// configure html5 to get links working on jsfiddle
	$locationProvider.html5Mode(false);
    });
