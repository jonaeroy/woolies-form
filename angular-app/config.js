App.config(['$routeProvider','$locationProvider', '$httpProvider',
    function($routeProvider, $locationProvider, $httpProvider) {
        $routeProvider.
           // when('/requests', {
            //    templateUrl: '/ng-view/partials/bnldsform.html',
            //    controller: 'ListRequestFormCtrl'
         //   }).
          //  otherwise({
           //     redirectTo: '/requests'
          //  });

        // $route, $routeParams, $location

        .when('/ng-view', {
	    templateUrl : 'ng/templates/main.html'
	    controller : 'BnldsCtrl'
	});

	.when('/newbnldsrequest', {
	    templateUrl : 'ng/templates/bnlds/bnldsform.html',
	    controller : 'BnldsCtrl'
	});
	.when('/list', {
	    templateUrl : 'ng/templates/bnlds/list.html',
	    controller : 'BnldsCtrl'
	});

	otherwise({
	    redirect: 'ng-view'
	});

        $locationProvider.html5Mode(true);
    }]);


