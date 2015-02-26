angular.module('app.controllers').controller('newBnldsRequestCtrl', function($scope, $location, BnldsSvc){
    "use.strict"

    $scope.bnlds={};
    $scope.choices=["Yes","No","N/A"];

    
    $scope.create = function(){
        BnldsSvc.create($scope.bnlds)
            .success(function(data, status){
                console.log(data.items);
            })
            .error(function(data,status){

            })

    };
    
    
    $scope.bnlds_list = [];
    
    $scope.list_all = function(){
	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
		console.log(data.items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    })
    };
});


// angular.module('app.controllers').controller('BnldsListCtrl', function($scope, BnldsSvc){
//     $scope.bnlds_items = [];
//     BnldsSvc.list()
// 	.success(function(data, status){
//             $scope.bnlds_items = data.items;
// 	})
// 	.error(function(data, status)){
//             alert("Error Occured!");
// 	}
// });
