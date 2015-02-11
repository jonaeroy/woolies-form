App.config(['$routeProvider',
	    function($routeProvider){
		$routeProvider.
		    when('/add_form', {
			templateUrl: '/ng/bnlds/bnlds_form.html'
		    }).
		    when('/bnlds_list', {
			templateUrl: '/ng/bnlds/bnlds_list.html',
			controller : 'BnldsList'
		    }).
		    otherwise({
			redirectTo: '/add_form'
		    });
	    }]);
