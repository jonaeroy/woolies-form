angular.module('app.services').
factory('Location', function($location, $route) {

    var factory  = {};

    factory.change = function(loc) {
    	$location.path(loc);
    };

    factory.current = function() {
    	return $location.path();
    };

    factory.reload = function() {
        $route.reload();
    };

    return factory;
});
