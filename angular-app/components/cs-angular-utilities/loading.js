angular.module('cs.loading', []).
directive('loading', ['$compile', function ($compile) {
  'use strict';
  return {
    restrict: 'EA',
    scope: {
      'instance': '=loading'
    },
    link: function($scope, elem, attrs){
      var $elem = $(elem);
      $elem.html('<div class="loader"><div class="spinner"><div class="spinner-container container1"><div class="circle1"></div><div class="circle2"></div><div class="circle3"></div><div class="circle4"></div></div><div class="spinner-container container2"><div class="circle1"></div><div class="circle2"></div><div class="circle3"></div><div class="circle4"></div></div><div class="spinner-container container3"><div class="circle1"></div><div class="circle2"></div><div class="circle3"></div><div class="circle4"></div></div></div></div>');
      $elem.addClass('loading');
      $elem.addClass('hidden');
      $scope.$watch('instance.is_loading', function(v){
          if(v){
              $elem.removeClass('hidden');
          } else {
              $elem.addClass('hidden');
          }
      });
    }
  };
}]).
service('loading', function(){
  var complete = function(instance, q){
    return function(){
      instance._futures.splice(instance._futures.indexOf(q), 1);
      check(instance);
    };
  };

  var check = function(instance){
    instance.is_loading = !!instance._futures.length;
  };

  return {'new': function(){
    return {
      is_loading: false,
      _futures: [],
      watch: function($q){
        this._futures.push($q);
        $q.then(complete(this, $q), complete(this, $q));
        check(this);
        return $q;
      }
    };
  }};
});

