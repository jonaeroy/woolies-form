angular.module('app.controllers').controller('UsersCtrl', function($log, $scope, $timeout, UserREST, pubsub, loading){
    "use strict";

    $scope.app.section = 'admin';

    $scope.showSaveFlash = false;
    $scope.users = [];

    $scope.list = function(url) {
        $scope.page_loading = loading.new();
        $scope.page_loading.watch(UserREST.listAll()).success(function(d){
            if (d.items) $scope.users = d.items;
            else $scope.users = [];
        });
    };

    $scope.list();
});
