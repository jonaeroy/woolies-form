angular.module('app.services').
service('BnldsSvc', function($http) {
    this.list = function(){
	return $http.get('/api/bnlds');
    }

    this.create = function(params){
	return $http.post('/api/bnlds', params);
    }

});
