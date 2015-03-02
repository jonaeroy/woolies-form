angular.module('app.services').
    service('BnldsSvc', function($http) {

    this.list_all = function(){
        return $http.get('/api/bnlds');
    }

    this.create = function(params){
        return $http.post('/api/bnlds', params);
    }

    this.get = function(key){
        return $http.get('/api/bnlds:' + key);
    }

    this.update = function(params){
        return $http.post('/api/bnlds/:' + params.key.urlsafe, params);
    }

    this.delete = function(key){
        return $http.delete('/api/bnlds/:' + key);
    }
});
