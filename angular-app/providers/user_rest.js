angular.module('app.services').
factory('UserREST', function($http) {

    var service = {};

    service.listAll = function(){
        return $http.get('/api/accounts');
    };

    return service;
});
