/*view form controller*/
angular.module('app.controllers').controller('viewBnldsCtrl', function($scope, $location,  $log, $routeParams, BnldsSvc){
    "use.strict"
    $scope.choices=["Yes","No","N/A"];
    $scope.mode = "view";
    $scope.bnlds = {};
        BnldsSvc.get($routeParams.key)
            .success(function(data, status){
         $scope.bnlds = data;
                console.log(data);
            })
            .error(function(data,status){

            });

    $scope.view = function(){
        BnldsSvc.update($scope.bnlds)
            .success(function(data, status){
                console.log(data);
                $location.path('#view');
            })
            .error(function(data,status){

            });

    };

