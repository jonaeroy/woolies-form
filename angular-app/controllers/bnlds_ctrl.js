angular.module('app.controllers').controller('newBnldsRequestCtrl', function($scope, $location,  $log, BnldsSvc){
    "use.strict"

    $scope.bnlds={};
    $scope.items = ["dsd"];

    //list pagination variables
    $scope.max_size = 5;
    $scope.total_items = 0;
    $scope.current_page = 1;
    $scope.items_per_page = 8;

     $scope.mode = 'add';


    $scope.choices=["Yes","No","N/A"];


    $scope.create = function(){
        BnldsSvc.create($scope.bnlds)
            .success(function(data, status){
                console.log(data);
                $location.path('#list');
                $scope.list_all();
            })
            .error(function(data,status){

            });


    };

      BnldsSvc.get_user()
        .success(function(data, status){
             $scope.bnlds['Buyer_or_BAA_Name'] = data.email;
            $log.log(data);
        })
        .error(function(data, status){
    });



    $scope.bnlds_list = [];
    $scope.sliced_bnlds_list

    $scope.list_all = function(){
	BnldsSvc.list_all()
	    .success(function(data, status){
		$scope.bnlds_list = data.items;
        $scope.sliced_bnlds_list=data.items;
        // if (Object.keys(data.items).length === 0){
		  //$scope.total_items = data.items.length;
		 // $scope.pageChange();
       // }
        //console.log(data);
		console.log($scope.total_items);
	    })
	    .error(function(data, status){
		alert('Error Accessing BNLDS Request Lists!');
	    });
    };

    $scope.delete = function(key){
	BnldsSvc.delete(key)
	    .success(function(data, status){
		if(status==200){
      alert('success');
      $scope.list_all();
		}

	    })
	    .error(function(data, status){

	    });
    };

    //request list pagination
    $scope.pageChange = function(){
	var start = ($scope.current_page-1)*$scope.items_per_page;
	var end = start + $scope.items_per_page;
	$scope.sliced_bnlds_list = $scope.bnlds_list.slice(start, end);
	$log.log(start + " : " + end);}

  });


/*edit form controller*/
angular.module('app.controllers').controller('editBnldsCtrl', function($scope, $location,  $log, $routeParams, BnldsSvc){
    "use.strict"
    $scope.choices=["Yes","No","N/A"];
    $scope.mode = "edit";
    $scope.bnlds = {};
        BnldsSvc.get($routeParams.key)
            .success(function(data, status){
         $scope.bnlds = data;
                console.log(data);
            })
            .error(function(data,status){

            });

    $scope.edit = function(){
        BnldsSvc.update($scope.bnlds)
            .success(function(data, status){
                console.log(data);
                $location.path('#list');
            })
            .error(function(data,status){

            });

    };



});


