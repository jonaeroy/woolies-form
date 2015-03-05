angular.module('app.services').
    service('CourierbookSvc', function($http) {

    this.list_all = function(){
        return $http.get('/api/courierbooks');
    }

    this.create = function(params){
        return $http.post('/api/courierbooks', params);
    }

    this.get = function(key){
        return $http.get('/api/courierbooks:' + key);
    }

    this.get_store_details = function(store_num){
        return $http.get('/api/courierbooks/get_store_details/' + store_num);
    }

    this.costcentres = function(){
        return $http.get('api/courierbooks/costcentres');
    }

    this.all_list = function(){
        return $http.get('api/stores/list_all');
    }

    this.update = function(params){
        return $http.post('/api/courierbooks/edit/:' + params.key.urlsafe, params);
    }
});
