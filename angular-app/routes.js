AppCore.config(['$routeProvider', '$locationProvider', '$httpProvider',
  function($routeProvider, $locationProvider, $httpProvider) {
    //$httpProvider.defaults.withCredentials = true;
    $routeProvider
      .when('/ng-view', {
        templateUrl : 'ng/templates/home/myhome.html'
        ,controller  : 'personController'
      })
      .when('/account', {
        templateUrl : 'ng/templates/account/account_management.html'
        ,controller  : 'personController'
      })
      .otherwise({
        templateUrl : 'ng/templates/home/wala.html'
        ,controller  : 'personController'
      });
      $locationProvider.html5Mode(true);
}]);
