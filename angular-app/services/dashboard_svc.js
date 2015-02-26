angular.module('app.services').
    service('DashboardSvc', function($http) {

	this.load_settings = function(){
	    return $http.get('/api/dashboard');
	}
	
    });
