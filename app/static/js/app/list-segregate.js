var ListSegregate = {

    show_unload: false,

    init : function()   {
        
        this.create_buttons();
        /*this.bindDOM();

        this.load_default();*/
    },
    
    removeURLParameter : function(url, parameter) {
        //prefer to use l.search if you have a location/link object
        var urlparts= url.split('?');   
        if (urlparts.length>=2) {

            var prefix= encodeURIComponent(parameter)+'=';
            var pars= urlparts[1].split(/[&;]/g);

            //reverse iteration as may be destructive
            for (var i= pars.length; i-- > 0;) {    
                //idiom for string.startsWith
                if (pars[i].lastIndexOf(prefix, 0) !== -1) {  
                    pars.splice(i, 1);
                }
            }

            url= urlparts[0]+'?'+pars.join('&');
            return url;
        } else {
            return url;
        }
    },

    create_buttons : function() {


        if($('#new_req').is(':visible'))    {
            
            var options = decodeURIComponent(window.location.search.slice(1))
                      .split('&')
                      .reduce(function _reduce (/*Object*/ a, /*String*/ b) {
                        b = b.split('=');
                        a[b[0]] = b[1];
                        return a;
                      }, {});

            
            var key = options.key;
            var new_url = FULL_URL.split('?')[0] + '?key=' + key;

            var buttons = '<div id="list_segregate_buttons" style="z-index:10000">'
                            + '<ul>'
                                +'<li id=list_inprocess><a href='+new_url+'>In Process</a></li>'
                                +'<li id=list_temp_approved><a href='+new_url+'&status=2>Temporarily Approved</a></li>'
                                +'<li id=list_approved><a href='+new_url+'&status=3>Approved</a></li>'
                                +'<li id=list_rejected><a href='+new_url+'&status=4>Rejected</a></li>'
                                +'<li id=list_all><a href='+new_url+'&status=all>Show All</a></li>'
                            +'</ul>'
                            +'<div style="clear:both"></div>'
                        +'</div>';
            //$('#list').parent().css('position', 'relative');
            $('.well').first().before(buttons);

            // hotfix! hide the temporary list tab 
            if (CONTROLLER_NAME == 'bws_stores' || 
                CONTROLLER_NAME == 'courierbooks' || 
                CONTROLLER_NAME == 'replenishments' || 
                CONTROLLER_NAME == 'travel_authorisations' ||
                CONTROLLER_NAME == 'leaveapps') {
                
                    $('#list_temp_approved').hide();
            }

            

            switch(options.status) {
                case 'all':
                    $('#list_all').addClass('active');
                    break;
                case '4':
                    $('#list_rejected').addClass('active');
                    break;
                case '3':
                    $('#list_approved').addClass('active');
                    break;
                case '2':
                    $('#list_temp_approved').addClass('active');
                    break;
                default:
                    $('#list_inprocess').addClass('active');
                    break;

            }

            var interval = setInterval(function()   {
                $.each($('.table-striped th a'), function() {
                    console.log($(this).text());

                    var old_url = $(this).attr('href');
                    var params = old_url.split('&');
                    var new_url = params[0] + '&' + 'key=' + key;
                    //alert(old_url);
                    if (options.status) {
                        $(this).attr('href', new_url + '&status=' + options.status)
                    }   else {
                        $(this).attr('href', new_url);
                    }

                    if($(this).text().trim() == 'Status')  {
                        if (options.status != 'all')    $(this).parent().html('Status');
                    }  
                });

                clearInterval(interval);
            }, 200)

            
        }
    }


}
$(document).ready(function() {
    ListSegregate.init();
});