/*view form controller*/
angular.module('app.controllers').controller('viewBnldsCtrl', function($scope, $location,  $log, $routeParams, BnldsSvc){
    "use.strict"
    $scope.choices=["Yes","No","N/A"];
    $scope.mode = "view";
    $scope.bnlds_details = {};

    BnldsSvc.get($routeParams.key)
        .success(function(data, status){
            $scope.bnlds_details = data;
            console.log(data);
        })
        .error(function(data,status){

        });

    

});

