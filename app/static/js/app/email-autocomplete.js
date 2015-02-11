/**
Javascript Class for email autocomplete w/ support on HTML5 native client validation.
* @dependencies jQuery 1.9+
* @class globalAddress
* @constructor
* @author Sugar Ray Tenorio ray@hotmail.ph; sugarray.tenorio@cloudsherpas.com
=========================================================
INITIAL SETUP:
=========================================================
    # its advisable to initialize the plugin on document ready then specify a URL and initialize script
    $(document).ready(function() {
        globalAddress.ns.CONNECT_URL = 'http://where/your/email/list/will/be/fetch';
        globalAddress.init();
    });

    NOTE : the return should be JSON and has 'fullName' and 'email' property MANDATORY for now.
=========================================================
USAGE:
=========================================================
    # to enable email autcomplete, just add 'global-address' in class
    <input type='email' class='global-address' />

    # to validate as required field
    <input type='email' class='global-address' required />

    # to show MODAL type search of email, specify 'modal=true' attribute
    <input type='email' class='global-address' modal='true' />

    # to only allow single email address on the text field, specify single-select='true'
    <input type='email' class='global-address' single-select='true' />

*/

var globalAddress = {

    init : function()   {
        this.bindDom();
        //this.connect();
        var parent = this;

        var interval = setInterval(function()   {
            parent.load_exist();
            clearInterval(interval);
        }, 500);

    },

    ns : {
        PLUGIN_CLASS: '.global-address',
        CONNECT_URL : '',

        MODAL : '#global-address-modal',
        EMAIL_LIST_CONTAINER : '.global-address-list-container',
        SEARCH_TXTBOX: '.global-address-input-search',
        DONE_BTN : '#modal-done-button',
        TEMP_MODAL_TRIGGER : null,
        MODAL_SEARCH_TXTBOX : '#global-address-search-txt',
        INPUT_CONTAINER : '#global-address-list-for-'
    },

    CONTACTS : null,

    bindDom : function()    {
        var parent = this;

        $(parent.ns.MODAL).on('show', function (obj) {

            // connect modal to inpu text
            var contacts_for = $(parent.ns.TEMP_MODAL_TRIGGER).attr('contacts-for-input');

            if ($(parent.ns.TEMP_MODAL_TRIGGER).attr('single-select'))  {
                $(parent.ns.MODAL).attr('single-select', 'true');
            }   else {
                $(parent.ns.MODAL).removeAttr('single-select');
            }

            $(parent.ns.MODAL).attr('contacts-for-input', contacts_for);

            parent.ns.TEMP_MODAL_TRIGGER = null;
            parent._modal.onShow(this, parent);

        });

        // search the list with this bindings
        $(parent.ns.MODAL_SEARCH_TXTBOX).keyup(function(e)    {
            $('.global-user-tr').hide();
            $('.global-user-span:contains("' + $(this).val().toLowerCase() +'")').parent().parent().show();

        });

        $(parent.ns.DONE_BTN).on('click', function()    {
            parent.selectionDone(parent);
        });

        // get all inputs that needed the contacts list
        $.each($(parent.ns.PLUGIN_CLASS), function()    {
            if($(this).attr('modal'))   {
                parent._modal.createButton(this, parent);
            } else {
                parent.changeInput(this);
            }
        });

        $(parent.ns.PLUGIN_CLASS).on('click', function() {
            $(this).hide();
            $(this).next().show();
            var _for = $(this).attr('id');
            $(parent.ns.INPUT_CONTAINER + _for + ' input').focus();
        });

        $(parent.ns.PLUGIN_CLASS).on('keydown', function() {
            $(this).hide();
            $(this).next().show();
            var _for = $(this).attr('id');
            $(parent.ns.INPUT_CONTAINER + _for + ' input').focus();
        });

        $(parent.ns.SEARCH_TXTBOX).keyup(function(e)  {
            var length = $(this).val().length;
            if(length > 1) {
                parent.suggestionBox.show(e, this);
            }   else {
                parent.suggestionBox.hide(e, this);
            }
        });

        $(parent.ns.SEARCH_TXTBOX).blur(function(e)  {

            var _for = $(this).attr('for'),
                listContainerVisible = $('#gal_container_for_' + _for).is(':visible'),
                inputobj = $(this),
                thiss = this;

            (function() {

                var interval = setInterval(function(e)  {
                    var email = inputobj.val();
                    if(email !== '') {
                        parent.suggestionBox.createEmailInput(email, inputobj, _for);
                    }   else {
                        var origInputBox = $('#' + _for);
                        if(origInputBox.val() === '')    {
                            origInputBox.show();
                            $(thiss).parent().hide();
                        }
                    }

                    parent.suggestionBox.hide(e, thiss);
                    clearInterval(interval);
                }, 200);
            })();
        });

        $('.global-address-email-container').click(function()   {
            $(this).find(parent.ns.SEARCH_TXTBOX).focus();
        });

    },

    suggestionBox : {
        show : function(e, obj)    {
            var obj = $(obj);

            // show list
            var pos = obj.position();
            var listObj = obj.parent().find(globalAddress.ns.EMAIL_LIST_CONTAINER);
            listObj.css('left', pos.left + 5);
            listObj.css('top', pos.top + 20);

            // do search
            this.search(e, obj);
            this.cursor(e, obj);
        },

        hide : function(e, obj) {
            $(obj).parent().find(globalAddress.ns.EMAIL_LIST_CONTAINER).hide();
        },

        fill : function(data)   {
            var html ='<ul>';
            $.each(data, function() {
                var lower_fullname = this.fullName;
                lower_fullname = lower_fullname.toLowerCase()
                html += '<li class=global-user-search-li>'
                    + lower_fullname + '<br /><em>'
                    + this.email + '</em></li>';
            });
            html += '</ul>';
            $(globalAddress.ns.EMAIL_LIST_CONTAINER).html(html);
/*
            $('.global-user-search-li').on('click', function()   {
                var obj =  $(this);
                globalAddress.suggestionBox.onSelectedEmail(obj);
            });*/
        },

        insert_contacts : function(contact, obj_container) {
            console.log(contact);
            var lower_fullname = contact.fullName;
            lower_fullname = lower_fullname;
            var html = '<li id="li-'+contact.email+'" class=global-user-search-li>'
                + lower_fullname + '<br /><em>'
                + contact.email + '</em></li>';

            obj_container.append(html);
            obj_container.find('.global-user-search-li').click(function()   {
                var obj =  $(this);
                globalAddress.suggestionBox.onSelectedEmail(obj);
            });
        },

        search : function(e, obj) {
            var obj_id = obj.attr('for');
            var listContainer = $('#gal_container_for_' + obj_id + ' .ul-container');
            listContainer.html('');
            var search_string = obj.val().toLowerCase();
            var counter = 0;

            delay(function(){

                $.ajax('/api/google/directory/users?q=' + search_string, {
                    type: 'GET'
                }).done(function(data) {

                    data = eval(data);
                    $.each(data, function() {
                        v = {
                            'fullName' : this.name['fullName'],
                            'email': this.primaryEmail
                        };
                        globalAddress.suggestionBox.insert_contacts(v, listContainer);
                    });

                    // if not on the list
                    if(listContainer.find('li').length == 0)    {
                        listContainer.parent().hide();
                        // if semicolon
                        if(e.which == 186)  {
                            var val = obj.val();
                            var length = val.length;
                            var email = val.substring(0,length-1);
                            var insertBefore = $(globalAddress.ns.INPUT_CONTAINER + obj_id + ' input');
                            this.createEmailInput(email, insertBefore, obj_id);
                        }
                    }   else {
                        listContainer.parent().show();
                    }
                });

/*
                $.each(globalAddress.CONTACTS, function(i, v) {
                    if(counter < 20)    {
                        var strRegExPattern = new RegExp('\\b' + search_string + '\\b');
                        console.log(v.fullName.toLowerCase().match(strRegExPattern, 'g'));
                        if (v.fullName.toLowerCase().match(strRegExPattern) || v.email.toLowerCase().match(strRegExPattern)) {
                            globalAddress.suggestionBox.insert_contacts(v, listContainer);
                            counter++;
                        }

                    }   else {
                        return;
                    }
                });*/


            }, 500 );
        },

        cursor : function(e, obj)   {
            var obj = $(obj);
            // TODO : selection using up down arrow keys here
        },

        onSelectedEmail : function(obj) {
            /* on selected email */
            // add email div
            var email = obj.find('em').text();
            var id = obj.parent().parent().attr('for');

            var insertInto = $(globalAddress.ns.INPUT_CONTAINER + id + ' input');
            this.createEmailInput(email, insertInto, id);

            obj.parent().parent().hide();

        },

        createEmailInput : function(email, insertInto, container_id)  {

            var pattern = "[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}";
			//	For some reason this previous condition failed failed at times - AAP 15/01/14
            // reverted back - RT 3/2/2013
            if(email.match(pattern) && $('.global-address-emailInput:contains("'+email+'")').length < 1)  {
            //if(email.match(pattern))  {

                //var encoded_email = base64.encode(email)

                // Prevents TypeError: e is undefined mumbo jumbo
                email = String(email);

                var encoded_email = CryptoJS.MD5(email);

                //var decrypted = CryptoJS.RC4.decrypt(encrypted, "Secret Passphrase");

                if ($('#email-input-' + encoded_email).length > 0){
                    // Already Exist
                }
                else{
                    var emailInput = $('<div id="email-input-'+encoded_email+'"></div>');
                    emailInput.addClass('global-address-emailInput');
                    emailInput.html('<span>'+email+'</span>');
                    insertInto.before(emailInput);

                    // add close button
                    var closeEmailSelected = $('<div>x</div>');
                    closeEmailSelected.addClass('global-address-closeEmailSelected');
                    emailInput.append(closeEmailSelected);

                    var PARENT = this;
                    closeEmailSelected.on('click', function()    {
                        PARENT.removeEmail(this, container_id);
                    });

                    insertInto.val('');
                    var emailaddressInput = $('#' + container_id);
                    var eaddress = emailaddressInput.val();
                    var delimiter = (eaddress == '') ? '' : ';';
                    emailaddressInput.val(eaddress + delimiter + email);

                    if(insertInto.attr('single-select'))    {
                        insertInto.hide();
                    }
                }


            }else{
                insertInto.val('');
            }
        },

        removeEmail : function(obj, container_id)    {
            var obj = $(obj);

            var email = obj.parent().find('span').text();
            var emailaddressInput = $('#' + container_id);

            // remove email with semicolon
            var eaddress = emailaddressInput.val();
            var remove = eaddress.replace(email + ';', "");
            emailaddressInput.val(remove);

            // find and remove email without semicolon
            var eaddress = emailaddressInput.val();
            var remove = eaddress.replace(email, "");
            emailaddressInput.val(remove);

            obj.parent().remove();

            var insertInto = $(globalAddress.ns.INPUT_CONTAINER + container_id + ' input');
            if(insertInto.attr('single-select'))    {
                insertInto.show();
            }


        },

        adjustHeight : function(id)   {
            var container = $(globalAddress.ns.INPUT_CONTAINER  + id)
            var count = container.find('.global-address-emailInput').length;
            if(count % 3 == 0) {
                container.height(container.height() + 25);
            }

        }
    },


    load_exist : function()   {
        // get all inputs that needed the contacts list
        var parent = this;

        $.each($(this.ns.PLUGIN_CLASS), function()    {
            var emails = $(this).val().split(';');
            var inputfield = $(this).next().find('input');
            var _for = inputfield.attr('for');
            var _this = this;
            if(emails.length > 0)   {

                $(this).val("");
                $.each(emails, function() {
                    if(this != '')    {

                        parent.suggestionBox.createEmailInput(this, inputfield, _for);


                    }
                });
                $(_this).click();
            }
            else{
                var infield = $(this).val();
                if(infield != ''){
                    $(this).val("");
                    parent.suggestionBox.createEmailInput(infield, inputfield, _for);
                }
            }
        });
    },

    changeInput : function(obj)    {
        var obj = $(obj);
        var obj_id = obj.attr('id');
        var obj_width = obj.outerWidth();
        var obj_height = obj.height();
        var obj_border = obj.css('border')
        var name = 'global-address-list-for-';
        var is_single_select = (obj.attr('single-select')) ? ' single-select=true ' : '';

        obj.attr('type','text');

        // create new DOM containers and style
        var div = $('<div></div>');
        div.css({
            'width': obj_width,
            'min-height': obj_height,
            background : obj.css('background'),
            border: obj_border
        });
        div.addClass('global-address-email-container')
        div.attr('id', name + obj_id);
        div.attr('for', obj_id);
        obj.after(div);

        // add input
        var is_leave_app_lm = (obj.attr('leave-app-lm')) ? true : false;
        var is_leave_app_hr = (obj.attr('leave-app-hr')) ? true : false;
        var placeholder;
        if (is_leave_app_lm){
            placeholder = "Search for Line Manager";
        }
        else if(is_leave_app_hr){
            placeholder = "Search for HR Manager";
        }
        else{
            placeholder = "Search for email address";
        }

        //var placeholder = "Type the full email address";
        var input = $('<input type=text placeholder="' + placeholder + '" for="' + obj_id + '" ' + is_single_select + ' />');
        input.addClass('global-address-input-search');
        div.append(input);


        var listContainer = '<div class="global-address-list-container" id="gal_container_for_'+obj_id+'" for="'+obj_id+'">' +
                            '   <ul class="ul-container"></ul>' +
                            '</div>';
        div.append(listContainer);

        var clearFloat = $('<div></div>');
        clearFloat.css('clear', 'both');
        div.append(clearFloat);

        obj.attr('placeholder', placeholder);
        //obj.css('visibility', 'hidden');
        //obj.css('display', 'none');

    },

    _modal : {

        onShow : function(_modal, parent)  {
            var modal = $(_modal);
            if(!modal.attr('data'))    {

                //#TODO : 'save to localStorage for global access'
                if(localStorage)    {
                    data = localStorage.getItem(parent.getListName());
                }

                if (data)   {
                    parent.connectResponse(data);
                }   else {
                    parent.connect();
                }
            }
        },

        createButton : function(obj, parent)   {
            var obj = $(obj);
            var id = obj.attr('id');
            var is_single_select = (obj.attr('single-select')) ? ' single-select=true ' : '';

            var html = ' <a id="modal-trigger-btn-' + id + '" href="' + parent.ns.MODAL
                        + '" role="button" class="open-modal btn btn-primary" data-toggle="modal" ' + is_single_select + ' contacts-for-input="' + id + '">...</a>';
            obj.after(html);

            $('#modal-trigger-btn-' + id).click(function()  {
                parent.ns.TEMP_MODAL_TRIGGER = this;
            });
        }

    },
    connect : function()    {
        var parent = this;

        //#TODO : 'save to localStorage for global access'
        if(localStorage)    {
            var data = localStorage.getItem(parent.getListName());
            if(data && data != '[]' )    {
                parent.connectResponse(data);
                return;
            }
        }

        $.ajax(parent.ns.CONNECT_URL, {
            type: 'GET'
        }).done(function(data) {
            parent.connectResponse(data);
            if(localStorage)    {
                localStorage.clear();
                localStorage.setItem(parent.getListName(), data);
            }
        });
    },

    connectResponse : function(data)    {

        var data = $.parseJSON(data);
        this.CONTACTS = data;
        //this.withModalResponseAction(data);
        //this.suggestionBox.fill(data);

    },

    withModalResponseAction : function(data)    {
        // render list
        this.renderList(data);
        parent = this;

        // prevent input box default function
        $('.global-user-tr input[type=checkbox]').on('click', function(e)    {
            e.preventDefault();
        });


        // set on click event of the list
        $('.global-user-tr').on('mouseup', function()   {

            var is_single_select = parent.isSingleSelect();
            var chk = $(this).find('input[type=checkbox]');

            if(is_single_select)    {
                $('#global-users-list input[type=checkbox]').removeAttr('checked');
                if(!chk.attr('checked'))    chk.attr('checked', 'checked');
            }   else {
                if (chk.attr('checked'))    {
                    chk.removeAttr('checked');
                }   else {
                    chk.attr('checked', 'checked');
                }
            }
        });
    },

    renderList : function(data)   {
        var html ='';
        $.each(data, function() {
            var lower_fullname = this.fullName;
            lower_fullname = lower_fullname.toLowerCase()
            html+= '<tr class=global-user-tr><td><input type="checkbox" value="'+ this.email +'"> </td>'
                + '<td><span class="global-user-span" style="display:none">' + lower_fullname
                + '</span><span>'
                + this.fullName + '</span></td><td>'
                + this.email + '</td></tr>';
        });

        // hide the preloading and show the list
        $('#global-users-list').html(html);
        $('#global-directory-fetch-tr').hide();
        $('#global-directory-message-tr').show();

        $(this.ns.MODAL_SEARCH_TXTBOX).val('');
        // set focus after a second.
        var parent = this;
        (function() {
            var interval = setInterval(function()    {
                $(parent.ns.MODAL_SEARCH_TXTBOX).focus();
                clearInterval(interval);
            }, 1000);
        })();

    },

    isSingleSelect : function() {
        var is_single_select = ($(this.ns.MODAL).attr('single-select')) ? true : false;
        return is_single_select;
    },

    selectionDone : function(parent)  {
        var cc_list = new Array();

        $('#global-users-list td').find(':checked').each(function(){
            cc_list.push($(this).val());
        });

        var is_single_select = parent.isSingleSelect();

        var contacts = '';
        if(cc_list.length > 0)
            contacts = cc_list.join('; ');
        else
            contacts = '';

        var inputID = $(parent.ns.MODAL).attr('contacts-for-input');
        var oldVal = $('#' + inputID).val();
        var allContacts = (oldVal) ? oldVal + '; ' + contacts: contacts;
        $('#' + inputID).val(allContacts);
    },

    getListName : function()   {

        var resourceName = 'GAL_';
        var currentdate = new Date();
        var datetime = String(currentdate.getDate() + "_" + (currentdate.getMonth()+1));
        var name = resourceName + datetime;
        //console.log("name ===> " + name);
        return name;
    }
};

// added delay func 9/27/2013. used on typing on email search
var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

$(document).ready(function() {
    globalAddress.ns.CONNECT_URL = '/api/google/directory/users';
    globalAddress.init();
});
