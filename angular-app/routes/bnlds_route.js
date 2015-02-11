App.config(['$routeProvider',
	    function($routeProvider){
		$routeProvider.
		    when('/add_form', {
			templateUrl: '/ngtemplates/bnlds/bnlds_form.html'
		    }).
		    when('/bnlds_list', {
			templateUrl: '/ng/templates/bnlds/bnlds_list.html',
			controller : 'BnldsList'
		    }).
		    otherwise({
			redirectTo: '/add_form'
		    });
	    }]);
