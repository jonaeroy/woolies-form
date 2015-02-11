/**
* This contains the global configuration of Woolies Forms overall Javascript variables and access to other extended object properties, methods and events.
* @class Forms
* @constructor  
* @author Sugar Ray Tenorio ray@hotmail.ph
*/

var Forms = {
    init : function()   {
       
        this.bindDom();       
        /*
        (function() {

            var interval = setInterval(function() {
                $('.alert').animate({
                    opacity: 0, height: 0
                  }, 500, function() {
                    $(this).hide();
                  });
                clearInterval(interval);
            }, 5000);
        })();*/
        this.checkIfHasItems();
        this.autoHeight();
    },

    autoHeight : function() {
        $('body').css('overflow', 'hidden');
        function _resizeWindow() {
            var height = $(window).height();
            $('#sidebar-nav').height(height-85);
            $('.content').height(height-90);
            $('.well').height(height-270);
            $('.dashboard-menu-container').height(height-185)
        }
        $(window).resize(function() {
            _resizeWindow();
        });
        _resizeWindow();
    },

    checkIfHasItems : function()    {

        if($('#ROUTE').val() == 'list' && $('#ADD_URL').val()) {
            
            if($('#page-container table.table-striped tr').length < 2 && $('#ADD_URL').val() != 'poolcarbooks/form')   {
                //var url = $('#ADD_URL').val() + '?key=' + $('#FORM_KEY').val();
                var url = $('#ADD_URL').val();
                
                
                //For Enhancement
                /*var message = 'You have no active forms, <br/><a href="' + url + '">click here</a> to create a new form.';
                var html = '<div class=" " style="font-size: 30px; text-align:center; padding-top: 55px; color: #999; line-height:45px; font-weight: bold">' +
                              message +
                            '</div>';
                if($('#First_approver_group_key').val())    {
                    $('#alert_container').append(html);
                }  
                $('#page-container').hide();*/

                var message = '<em>No Results Found.<br/> Click <a href="../'+url+'">here</a> to add new form.<em>';
                var html = '<div class=" " style="font-size: 30px; text-align:center; padding-top: 55px; color: #999; line-height:45px; font-weight: bold">' +
                              message +
                            '</div>';

                /*$('#form_title').hide();
                $('#alert_container').html(html);
                $('#new_req').hide();
                $('#page-container').hide();
                */
                //document.location.href=url;
                var interval = setInterval(function()   {
                    $('.well .table-striped').hide();
                    $('.well').append(html);
                    $('.pagination').hide();
                    clearInterval(interval);
                },100);
                
            }
        }
    },

    ns : { 
        add_new_admin_btn : '#add_new_admin_btn',
        add_new_manager_btn  : '#add_new_manager_btn',
        add_new_second_manager_btn : '#add_new_second_manager_btn',
        add_new_member_btn : '#add_new_member_btn',
        user_select_modal : '#template_user_select_modal',
        select_group_admin : '#select_group_admin',
        select_group_one : '#select_group_one',
        select_group_two : '#select_group_two',
        select_group_admin_list : '#select_group_admin_list',
        select_group_one_list : '#select_group_one_list',
        select_group_two_list : '#select_group_two_list',
        save_managers_btn : '#save_managers_btn',
        FORM_KEY : '#FORM_KEY',
        group_name_class : '.group_name_class',
        template_user_add_modal : '#template_user_add_modal',
        save_member_btn : '#save_member_btn',

        ADD_LEVEL : null
    },

    bindDom : function()    {
        var PARENT = this;

        $(this.ns.add_new_admin_btn).on('click', function()    {
            PARENT.setLevels('Admin', PARENT);
        });

        $(this.ns.add_new_manager_btn).on('click', function()    {
            PARENT.setLevels('First', PARENT);
        });

       $(this.ns.add_new_second_manager_btn).on('click', function()    {
            PARENT.setLevels('Second', PARENT);
        });

        $(this.ns.select_group_admin).on('change', function()    {
            PARENT.group_members._show($(this).val(), $(Forms.ns.select_group_admin_list), PARENT);
        });

        $(this.ns.select_group_one).on('change', function()    {
            PARENT.group_members._show($(this).val(), $(Forms.ns.select_group_one_list), PARENT);
        });

        $(this.ns.select_group_two).on('change', function()    {
            PARENT.group_members._show($(this).val(), $(Forms.ns.select_group_two_list), PARENT);
        });

        $(this.ns.save_managers_btn).on('click', function()    {
            PARENT.manager._save(PARENT);
        });

        $(this.ns.group_name_class).hover(function()    {
            Forms.group_members.list(this);
        });

        $(this.ns.add_new_member_btn).on('click', function()    {
            PARENT.members._add();
        });
        $(this.ns.save_member_btn).on('click', function()    {
            PARENT.members._save(this);
        });

        $(Forms.ns.template_user_add_modal).on('hide', function()   {
            $(Forms.ns.user_select_modal).modal({backdrop : true, show:true})
        });


        try {
            $('.selectpicker').addClass('span10');
        }   catch(e) {}

        var url = window.location.search;
        
        if(window.location.href.search('print=true') != -1 ){

            $(".navbar-inner").hide();
            $("#sidebar-nav").hide();
            $(".alert").hide();
            $(".btn").hide();
            $(".btn-flat").hide();
            $(".content").css('margin-left', 0);
            $(".content").css('background', '#fff');
            var anchor = $(".download_link").text();
            var span = $('<span></span>').text(anchor);
            $(".download_link").after(span);
            $(".download_link").remove();
            $('.well').removeClass('well');
            $('.content').removeClass('content');
            $('body').css('bacckground', '#fff');

            alert("NOTE: Chrome is the suggested Web Browser for printing and saving of the request. \n\t 1. Just press (CTRL + 'P') to open the printing dialog page.\n\t 2. Click on the 'Save' button for saving to PDF format.\n\t 3. Make sure that the destination is set to 'Save as PDF'\n\t 4. Under Options, no checkbox is checked. ");
            (function() {
                var interval = setInterval(function()   {
                    window.print();   
                    clearInterval(interval);
                }, 500);
            })();

        }

        window._window =null;

        $('#savePDF').on('click', function() {
            if(!window._window){
                window._window = window.open(window.location + "&print=true", "_blank", "fullscreen=yes");
                window._window.addEventListener('unload',function(){
                    window._window =null;
                });
            }
            else{
                window._window.focus();
            }
            

        });

    },

    setLevels : function(LEVEL, PARENT)  {
        PARENT.ns.ADD_LEVEL = LEVEL;

        //reset first
        $('.group_selector_div').hide();
        $('.group_list_div').hide();

        //show select dropdown of chosen level
        $('#div_container_select_' + LEVEL).show();

        var modal_title = '',
            dropdown_select_caption = '';
            group_key = null,
            list_container = null;

        switch(LEVEL)   {
            case 'First':
                list_container = $(PARENT.ns.select_group_one_list)
                modal_title = 'Assign First level Group Approver ';
                dropdown_select_caption = 'Please select the First Level Group Approver : '
                group_key = $(PARENT.ns.select_group_one +' option:selected').val();
                break;
            case 'Second':
                list_container = $(PARENT.ns.select_group_two_list)
                modal_title = 'Assign Second level Group Approver';
                dropdown_select_caption = 'Please select the Second Level Group Approver : '
                group_key = $(PARENT.ns.select_group_two +' option:selected').val();
                break;
            case 'Admin':
                list_container = $(PARENT.ns.select_group_admin_list)
                modal_title = 'Assign Form Administrator';
                dropdown_select_caption = 'Please select the Form Administrator Group'
                group_key = $(PARENT.ns.select_group_admin +' option:selected').val();
                break;
        }
        $('#form_modal_span_title').text(modal_title);
        $('#drop_down_modal_select_caption').text(dropdown_select_caption);
        list_container.show();
        PARENT.manager.show_select(PARENT, group_key, list_container);
        
    },

    manager : {

        show_select: function(PARENT, group_key, list_container) {
            $(PARENT.ns.user_select_modal).modal({backdrop : true, show:true});
            PARENT.group_members._show(group_key, list_container, PARENT);
        },

        _save : function(PARENT)  {
            var url = '',
                group_key = '',
                message = '',
                form_key = $(PARENT.ns.FORM_KEY).val();

            switch(PARENT.ns.ADD_LEVEL)   {
                case 'First':
                    group_key = $(PARENT.ns.select_group_one).val();
                    url = "/form/approver/1/save/" + group_key + "/" + form_key;
                    message = 'First Approver Group has been Saved Successfully.'
                    break;
                case 'Second':
                    group_key = $(PARENT.ns.select_group_two).val();
                    url = "/form/approver/2/save/" + group_key + "/" + form_key;
                    message = 'Second Approver Group has been Saved Successfully.'
                    break;
                case 'Admin':
                    group_key = $(PARENT.ns.select_group_admin).val();
                    url = "/form/admin/save/" + group_key + "/" + form_key;
                    message = 'Form Administrator has been assigned Successfully.'
                    break;
            }

            if(group_key)    {
                
                var ask = confirm("Are you sure you want to assign this group on this form?")
                if(!ask)    {
                    return;
                }
                
                $.ajax({
                    type: "GET",
                    url: url,
                    success: function(data) {

                        data = jQuery.parseJSON(data);                    
                        if(data.success) {
                            $(Forms.ns.user_select_modal).modal('hide')
                            alert(message)
                            window.location.href = document.URL + "&save_form=success";
                            window.location.reload();
                        }                    
                    }
                });

            }   else {
                alert('Please select a Group before saving.');
            }
        }

    },

    group_members : {

        _show : function(group_key, $container, PARENT)   {   
            var preloader = '<img src="/static/images/search-loader.gif" width=40 height=40 align=absmid /> Searching groups ...'
            $container.html(preloader);
            
            $.ajax({
                type: "GET",
                url: "/users/get/" + group_key,
                timeout: 1000,
                success: function(data) {
                    //alert(data.length);                    
                    
                    data = jQuery.parseJSON(data);
                    //console.log(data);
                    var html = '';
                   
                    if (data.length)   {
                        $.each(data, function() {
                            var alreadyAdmin = false;
                  
                            alreadyAdmin = alreadyAdmin ? 'checked=checked' : ''; 
                            //html += '<li><input type=checkbox name=group_approver_one value='+ this.email + ' '+ alreadyAdmin +' />' + this.email + '</li>'
                            html += '<div class=row-fluid><span class=span7 style="color:#666"><strong>' + this.email + '</strong></span><span class=span4>' 
                                + this.fullname + '</span></div>'
                        });

                    }   else {
                        html = '<li>No users on this group.</li>';
                    }
                    $container.html('<ul class="list-unstyled">' + html + '</ul>');
                    PARENT.group_members.toggleLevelContainer(PARENT);                    
                },
                error : function(data)  {
                    //console.log(data);
                    $('#add_new_member_modal_div').hide();
                    $container.html('<ul class="list-unstyled">Group not Found.</ul>');
                    $('.group_list_div').hide();
                }
            });
           
           
        },

        toggleLevelContainer : function(PARENT)   {

            $('.group_list_div').hide();
            $('#add_new_member_modal_div').hide();

            var group_name = '',
                group_key = '',
                list_container = null;
            switch(PARENT.ns.ADD_LEVEL)   {
                case 'First':
                    list_container = $(Forms.ns.select_group_one_list)
                    group_name = $(PARENT.ns.select_group_one +' option:selected').text();
                    group_key =  $(PARENT.ns.select_group_one +' option:selected').val();
                    break;
                case 'Second':
                    list_container = $(Forms.ns.select_group_two_list)
                    group_name = $(PARENT.ns.select_group_two +' option:selected').text();
                    group_key =  $(PARENT.ns.select_group_two +' option:selected').val();
                    break;
                case 'Admin':
                    list_container = $(Forms.ns.select_group_admin_list)
                    group_name = $(PARENT.ns.select_group_admin +' option:selected').text();
                    group_key =  $(PARENT.ns.select_group_admin +' option:selected').val();
                    break;
            }

            if(group_name) {
                list_container.show();
                $('#add_new_member_modal_div').show();                
                $('#span_modal_selected_group_name').text(group_name);
                $('#user_add_modal_group_name').text(group_name);
                $('#GROUP_KEY_FOR_ADD_USER').val(group_key);
            }
        },

        list : function(obj)   {
            
            if(!$(obj).attr('title'))   {
              
                var group_key = $(obj).attr('group_key');
                var PARENT = obj;
                $.ajax({
                    type: "GET",
                    url: "/users/get/" + group_key,
                    success: function(data) {
                        data = jQuery.parseJSON(data);
                        //console.log(data);
                        var html = '';

                        if (data.length)   {
                            $.each(data, function() {
       
                                html += '' + this.email + '; '
                            });
                        }   else {
                            html = 'No users on this group.'
                        }
                        console.log(html);
                        $(PARENT).parent().attr('data-content', html).popover({ title: '', placement: 'bottom', trigger: 'click' });
                    
                        //$(PARENT).attr('title', html);
                    }
                });
                
            }
        }
    },

    members : {

        _add : function()   {
            $(Forms.ns.template_user_add_modal).modal({backdrop : true, show:true})
            $(Forms.ns.user_select_modal).modal('hide');
            $('#add_member_name_modal').val('');
            $('#add_member_email_modal').val('');
           
        },
        _save : function(obj)  {
            var obj = $(obj)
            if(!obj.attr('disabled'))   {
                                
                var _name = $('#add_member_name_modal').val();
                var _email = $('#add_member_email_modal').val();
                var _group = $('#GROUP_KEY_FOR_ADD_USER').val();
                var _group_name = $('#user_add_modal_group_name').text();

                if(_name && _email) {
                    obj.attr('disabled', 'disabled');
                    
                    var ask = confirm('Are you sure you want to add ' + _name + ' as a member of '+ _group_name + '?');
                    if (!ask) {
                        obj.removeAttr('disabled');
                        return;
                    }
                   
                    this.connect(_email, _name, _group, obj);
                }   else {
                    alert('Please complete all fields.')
                }
            }
        },
        connect : function(_email, _name, _group, obj)    {
            var obj = $(obj);
            $.ajax({
                type: "GET",
                url: '/users/group/add/' + _email + '/' + _name + '/' + _group,
                success: function(data) {
                    data = jQuery.parseJSON(data);                    
                    if(data.success== 'true') {
                        $(Forms.ns.template_user_add_modal).modal('hide')
                        alert('New member added successfully.')
                        window.location.href = document.URL + "&save_member=success";
                        window.location.reload();
                    }   else {
                        alert(data.message)
                        $('#add_member_name_modal').val('');
                        $('#add_member_email_modal').val('');

                        $('#template_user_add_modal .global-address-closeEmailSelected').click();
                    }

                    obj.removeAttr('disabled');
                },

                error : function()  {
                    alert('Somethings not right.');
                    obj.removeAttr('disabled');
                }
            });
        }
    }
}
$(document).ready(function() {
    Forms.init();
});
    

