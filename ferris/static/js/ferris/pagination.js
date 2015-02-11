
$(function(){

    // Set-up

    //adds params to a link
    var add_params = function(link, params){
        glue = link.indexOf('?') === -1 ? '?':'&';
        return link + glue + $.param(params);
    };

    // Check if we have localStorage, if not, return, otherwise hide the single paginator.
    if (typeof(localStorage) == 'undefined') return;
    $('.paging-container .single-pager').hide(); //hide the single pager, we don't need it  anymore.
    $('.paging-container .pagination').show();

    var cursors_list = [];

    //get cursor list
    if(paging_config.cursor){
        var stored_val = localStorage.getItem(paging_config.storage_key);
        if(stored_val){
            cursors_list = stored_val.split(',');
        }

        //something is wrong so reset to page 1
        if(!cursors_list){
            document.location.replace(paging_config.uri);
            return;
        }
    }

    //configure next link
    if(!paging_config.next_cursor){
        $('.pagination .next').addClass('disabled');
    } else {
        $('.paging-next-link').attr('href',
            add_params(paging_config.uri, {'cursor': paging_config.next_cursor, 'limit': paging_config.limit})
        );
    }
    $('.paging-next-link').click(function(e){
        if(paging_config.next_cursor){
            cursors_list.push(paging_config.next_cursor);
            localStorage.setItem(paging_config.storage_key, cursors_list.join(','));
        } else {
            e.stopPropagation();
            e.preventDefault();
        }
    });

    //configure prev link
    if(!cursors_list.length){
        $('.pagination .previous').addClass('disabled');
    } else {
        var prev_link_params = (cursors_list.length>1) ?
                {cursor: cursors_list[cursors_list.length-2], limit: paging_config.limit}
                : {limit: paging_config.limit};
        var prev_link = add_params(paging_config.uri, prev_link_params);
        $('.paging-previous-link').attr('href', prev_link );
    }
    $('.paging-previous-link').click(function(e){
        if(cursors_list){
            cursors_list.pop();
            localStorage.setItem(paging_config.storage_key, cursors_list.join(','));
        } else {
            e.stopPropagation();
            e.preventDefault();
        }
    });

    //display result count text
    if(paging_config.results > 0){
    	
    	var start_index = ((cursors_list.length * paging_config.limit) + paging_config.results) / paging_config.limit;
    	var start_page  = Math.floor(start_index);
        var end_index   = paging_config.current / paging_config.limit;
        var end_page    = Math.floor(end_index);
        		
        if	(start_page < start_index)
        {
        	start_page++;	
        }
        
        if	(end_page < end_index)
        {
        	end_page++;	
        }
        
        
        $('.paging_text').text(start_page + ' of ' + end_page);
    }
        
});