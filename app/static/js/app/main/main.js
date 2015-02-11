$(document).ready(function()	{

	$('#manage_users_btn').click(function()	{

		document.location = '/users';

	});

	$('#logout_btn').click(function()	{

		document.location = $('#logout_url').val();
		
	});

	$('#manage_groups_btn').click(function()	{

		document.location = '/groups';
		
	});
	$('#manage_forms_btn').click(function()	{

		document.location = '/woolies_forms';
		
	});

	
});
