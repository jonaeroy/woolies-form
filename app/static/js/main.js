var app = angular.module('myApp', []);

app.directive('numbersOnly', function(){
   return {
     require: 'ngModel',
     link: function(scope, element, attrs, modelCtrl) {
         modelCtrl.$parsers.push(function (inputValue) {
             var transformedInput = inputValue.replace(/[^0-9]/g, ''); 
             if (transformedInput != inputValue) {
                modelCtrl.$setViewValue(transformedInput);
                modelCtrl.$render();
             }
             return transformedInput;   
         });
     }
   };
});

function DRFCtrl($scope){
	$scope.counter = 1;

	$scope.items = [
		{}
	];

	$scope.addRow = function(item) {
		$scope.items.push(item);
		$scope.item = {};
		$scope.counter++;
	}

	$scope.removeRow = function(index){
		$scope.items.splice(index, 1);
		$scope.counter--;
	}

	/*
	$scope.globalFunc = function(someGlobalFuncReference){
        $scope.funcRef = eval(someGlobalFuncReference);        
        assemble();
    };
    */
}