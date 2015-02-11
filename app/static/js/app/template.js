var template = {
    init : function()   {
       
        this.bindDom();
        $('.selectpicker').selectpicker();
    },

    ns : { 
        add_new_manager_btn  : '#add_new_manager_btn',
        user_select_modal : '#template_user_select_modal',
        select_group_one : '#select_group_one',
        select_group_one_list : '#select_group_one_list'
    },

    bindDom : function()    {
        var PARENT = this;
        
        $(this.ns.add_new_manager_btn).live('click', function()    {
            PARENT.manager.add();
        });

        $(this.ns.select_group_one).live('change', function()    {
            PARENT.group_members._show($(this).val());
        });
    },

    manager : {

        add: function() {
            $(template.ns.user_select_modal).modal({backdrop : true, show:true})
        }

    },

    group_members : {

        _show : function(key)   {
            
            $.ajax({
                type: "GET",
                url: "/users/get/"+key,
                success: function(data) {
                    //alert(data.length);
                    
                    var data = $.parseJSON(data);
                    var html = '';
                    console.log(data);
                    if (data.length)   {
                        $.each(data, function() {
                            html += '<li><input type=checkbox name=group_approver_one value='+ this.email +' />' + this.email + '</li>'
                        });
                    }   else {
                        html = '<li class=warning>No users on this group.</li>'
                    }

                    $(template.ns.select_group_one_list).html(html);
                }
            });
            
           
        }
    }
}

$(document).ready(function() {
    template.init()
});
    

