angular.module('app.directives')
.directive('editInPlace', function() {
    return {
        restrict: 'E',
        scope: {value: '='},
        template: '<span ng-click="edit()" ng-bind-template="{{value*100}}%"></span><input ng-model="value"></input>',
        link: function ($scope, element, attrs) {
            var inputElement = angular.element(element.children()[1]);
            element.addClass('edit-in-place');
            $scope.editing = false;
            $scope.edit = function () {
                $scope.editing = true;
                element.addClass('active');
                inputElement[0].focus();
            };
            inputElement.blur(function() {
                $scope.editing = false;
                element.removeClass('active');
            });
        }
    };
}).directive('editInPlace2', function() {
    return {
        restrict: 'E',
        scope: {bind: '=', value: '='},
        template: '<span ng-click="edit()" ng-bind="bind"></span><input ng-model="value"></input>',
        link: function ($scope, element, attrs) {
            var inputElement = angular.element(element.children()[1]);
            element.addClass('edit-in-place');
            $scope.editing = false;
            $scope.edit = function () {
                $scope.editing = true;
                element.addClass('active');
                inputElement[0].focus();
            };
            inputElement.blur(function() {
                $scope.editing = false;
                element.removeClass('active');
            });
        }
    };
});
