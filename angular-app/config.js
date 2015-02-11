App.config(
    function($routeProvider, $locationProvider) {
        $routeProvider.
            when('/requests', {
                templateUrl: '/ng-view/partials/list-request-form.html',
                controller: 'ListRequestFormCtrl'
            }).
            otherwise({
                redirectTo: '/requests'
            });

        // $route, $routeParams, $location

        $locationProvider.html5Mode(false);
    }
);
