angular.module('app.controllers').controller('ModalController', function($scope, $modal){
    
    $scope.items = {};

    $scope.openmodal = function (size){
	
	var modal = $modal.open({
	    templateUrl: 'ng/templates/bnlds/bnldform.html',
	    controller: 'BnldsCtrl',
	    size:size,
	    resolve: {
		items: function(){
		    return $scope.items;
		}
	    }

	})

    }



});
