var Drafts = {

    show_unload: false,

    init : function()   {
        this.bindControls();
        this.loadValues();
        this.ask_before_unload();
        this.check_changes();

    },

    ns : {

        'drafts_url' : DRAFT_ACTION_URL,
        'clear_url' : CLEAR_DRAFT_ACTION_URL
    },

    bindControls : function()   {
        var parent = this
        $('#save_as_draft_btn').click(function()    {
            parent.upload_data(this);
        });

        $('#clear_draft_btn').click(function()    {
            parent.clear_data(this);
        });

        $('#page-container input[type=submit]').click(function()    {
            parent.show_unload = false;
        });

        $('#page-container form').on("submit", function()    {
            parent.show_unload = false;
        });

        var e = $.Event( "change", { which: 1 } );
        $('select').trigger(e);
    },

    loadValues : function() {
        var parent = this;
        if (DRAFT_DATA != '' && DRAFT_DATA!='null') {
            data = $.parseJSON(DRAFT_DATA);
            var interval = setInterval(function() {

                $.each(data, function(v, i) {
                    console.log(v + " = " + this);
                    var obj = $("[name='" + v + "']");

                    // check if the current field has multiple values
                    var field_is_array = false;
                    try {
                        if (this.split('::::').length > 1) {
                            //console.log('im an array ==> ' + v);
                            field_is_array = true;
                        }
                    } catch(e) {}


                    // special cases
                    // for stock reject form 'To' checkbox field
                    if (v == 'To')  {
                        //special cases
                        switch(CONTROLLER_NAME) {                            
                            case 'stockrejects':
                                var values = i.split(',')
                                $.each(values, function()   {
                                    $('input[value="'+this+'"]').attr('checked', 'checked');
                                });
                                break;
                        }
                    }

                    if(obj.attr('type') == 'radio' || obj.attr('type') == 'checkbox')    {
                        // this handles all radio and checkbox
                        // special cases for replenishment checkbox
                        if (obj.attr('name') == 'toCheck')   {
                            var cb_int = setInterval(function() {
                                var checked_values = $('#Change_Type_cbox').val();
                                checked_values = checked_values.split(',');
                                console.log(checked_values)
                                $.each(checked_values, function()   {
                                    var cval = String(this);
                                    $.each(obj, function() {
                                        var checkbox = $(this);
                                        if(" " + checkbox.val() == cval)  {
                                            checkbox.attr('checked', 'checked');
                                        }
                                    });
                                });
        
                                clearInterval(cb_int);
                            }, 500);
                            
                        }   else {
                            $.each(obj, function() {
                                var _obj = $(this);
                                console.log(_obj.val() + "  === " + i)
                            
                                if (_obj.val() == i) {
                                    
                                    _obj.attr('checked', 'checked');

                                    if(v=='issue_raised_in_pct')    {
                                        _obj.val('Yes')
                                    }   else    {    
                                        _obj.click();
                                    }

                                    return false;
                                }
                            });

                        }
                        
                    }   else {
                        // this else handles all texboxes and input text

                        // dieffrent style of input population if the values is array or not
                        if (field_is_array) {
                            // special cases
                            switch(CONTROLLER_NAME) {
                                case 'director_requests':
                                case 'travel_authorisations':
                                case 'multiple_changes':
                                case 'pack_sizes':

                                    var array_values = this.split("::::")
                                    //console.log(array_values)
                                    var counter = 0;
                                    $.each(array_values, function() {
                                        var new_obj = $(obj[counter]);
                                        //alert(new_obj);
                                        // check if textfield is already displayed
                                        

                                        if (new_obj.length > 0) {
                                            
                                            if(new_obj.prop("tagName") == 'SELECT') {
                                                //alert(new_obj.html());
                                                new_obj.find('option[value="'+ this +'"]').attr('selected', 'selected');
                                            }   else    {
                                                //alert('pause1');
                                                new_obj.val(this);    
                                            }
                                        }   else {
                                            //else addrow
                                            $('#addRow').click();

                                            if (CONTROLLER_NAME == 'travel_authorisations') {
                                                var check_tab = v.split('_')[0];
                                                $('#addrow' + check_tab).click();
                                                //alert('pause2');
                                            }   else if(CONTROLLER_NAME == 'director_requests') {

                                            }

                                            // re create array since we added new row
                                            var renew_obj = $("[name='" + v + "']");
                                            var new_obj = $(renew_obj[counter]);

                                            if(new_obj.prop("tagName") == 'SELECT') {
                                                //alert(new_obj.html());
                                                new_obj.find('option[value="'+ this +'"]').attr('selected', 'selected');
                                            }   else    {
                                                //alert('pause3');
                                                new_obj.val(this);    
                                            }
                                        }
                                        
                                        //console.log(new_obj)
                                        counter++;
                                        // click the addrow button
                                        
                                    });

                                    break;
                            }

                        }   else {
                            //alert('pause4');
                            // ordinary fields here
                            obj.val(i);
                            obj.attr('draft-val',i);

                            if(!obj.hasClass('ui-timepicker-input')) {
                                obj.click();
                            }
                        }
                    }

                });
                
                clearInterval(interval);
                globalAddress.load_exist();
                //parent.editChecker();
            }, 1000);
        }
        
    },

    upload_data : function(obj)    {
        var parent = this;
        $(obj).html('<i class="icon-save"></i> SAVING ...');
        $(obj).attr('disabled', 'disabled');

        data = 'save_as_draft=true';

        $.each($('#page-container form'), function()    {
            data = data + "&" + $(this).serialize();
        });

        //alert(data);

        $.ajax({
            method: 'POST',
            url: this.ns.drafts_url,
            data: data,
            statusCode: {
                404: function() {}
            }
        })
        .done(function( html ) {
            //console.log(html);
            parent.show_unload = false;
            window.location = LIST_ACTION_URL
        });       
    },

    clear_data : function(obj)    {
        var parent = this;
        $(obj).attr('disabled', 'disabled');

        $.ajax({
            url: this.ns.clear_url,
            statusCode: {
                404: function() {}
            }
        })
        .done(function( html ) {
            //console.log(html);
            parent.show_unload = false;
            window.location = LIST_ACTION_URL
        });       
    },

    check_changes : function()  {
        var parent = this;

        var interval = setInterval(function() {
            /*$('input[type=text], textarea').on('blur', function()  {
                parent.editChecker();
            });
*/ 
            // for time pickers
            $('.ui-timepicker-list li').click(function()   {
                parent.editChecker();
            });

            $('input[type=radio], input[type=checkbox]').on('change', function()  {
                parent.editChecker();
            });

            $('input[type=text], textarea').on('keyup', function(e)  {
                parent.editChecker();
            });

            $('select').on('change', function()  {
                parent.editChecker();
            });

            clearInterval(interval);
        }, 2000);
        
        if(DRAFT_DATA == 'null')    {
            $('#clear_draft_btn').hide();
        }
        
    },

    editChecker : function()    {
        var parent = this;

        hasEdit = false;
        totalTextBox = $('#page-container input:text:enabled:visible:not([readonly="readonly"])').length;
        totalTextEdited = $('#page-container input:text:enabled:visible:not([readonly="readonly"]):textboxEmpty').length;

        if(totalTextBox != totalTextEdited)    {
            hasEdit=true;
        }

        totalTextArea = $('#page-container textarea:enabled:visible:not([readonly="readonly"])').length;
        totalTextAreaEdited = $('#page-container textarea:enabled:visible:not([readonly="readonly"]):textboxEmpty').length;

        if(totalTextArea != totalTextAreaEdited)    {
            hasEdit=true;
        }

        totalSelect = $('#page-container select:enabled:visible:not([readonly="readonly"])').length;
        totalSelectEdited = $('#page-container select:enabled:visible:not([readonly="readonly"]):textboxEmpty').length;

        if(totalSelect != totalSelectEdited)    {
            hasEdit=true;
        }

        if(!hasEdit)    {
            parent.show_unload = false;
            $('#save_as_draft_btn').attr('disabled', 'disabled');
        }   else {
            parent.show_unload = true;
            $('#save_as_draft_btn').removeAttr('disabled');

        }     
    },

    ask_before_unload : function()  {
        var parent = this;
        window.onbeforeunload = function(e) {
            if (parent.show_unload) {
                return 'You can save this form by using the "Save as Draft" button.\n\nLeaving this page will discard the changes you made in this form.';
            }
        };
    }
}
$(document).ready(function() {
    Drafts.init();
});

// custom selecter for none values input,select, textarea fields
$.extend($.expr[':'],{
    textboxEmpty: function(el){
        return $(el).val() === "";
    }
});
