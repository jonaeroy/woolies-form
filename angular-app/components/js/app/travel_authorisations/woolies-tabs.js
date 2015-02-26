var wooliesTabs = {

    init : function()   {
        this.bindDom();
        // activate first tab
        $('.tabbable ul li[tabs=1]').find('a').click();
    },

    trigger_count : 0,

    ns : {
        tabBtn : '.tabbable ul li a',
        wooliestabs : '.woolies-tab',
        mainSubmitBtn : '#main-submit-btn',
        mainUpdateBtn : '#main-update-btn',
        nextBtn : '#next-btn'
    },

    bindDom : function()    {
        var parent = this;
        $(this.ns.tabBtn).on('click', function(e)    {
            e.preventDefault();
            parent.btnClicked(this);
        });

        $(this.ns.wooliestabs).find('input[type=submit]').css('visibility', 'hidden');
        $('#formtodetails').find('input[type=submit]')
        .css({
            'visibility' : 'hidden',
            height: 0
        });

        $('#formtodetailsupdate').find('input[type=submit]')
        .css({
            'visibility' : 'hidden',
            height: 0
        });

        $(this.ns.nextBtn).click(function() {
            parent.nextBtnClicked(this);
        });

        $(this.ns.mainSubmitBtn).click(function() {
            parent.validateAll();
        });

        $(this.ns.mainUpdateBtn).click(function() {
            parent.validateUpdateAll();
        });
    },

    nextBtnClicked : function(obj) {
        var activeTab = $('.nav-tabs li[class=active]')
        activeTab.next().find('a').click();
    },

    btnClicked : function(obj) {
        var li = $(obj).parent();

        var activeBefore = $('.tabbable ul li[class=active]');
        var activeTabBefore = (activeBefore.attr('tabs'));
        var tabNumberSelected = li.attr('tabs');
        
        /*if(!this.validateForm(activeTabBefore) && activeTabBefore) {
           return;
        }*/

        //reset active btn
        $(this.ns.tabBtn).parent().removeClass('active');
        li.addClass('active');

        // hide /show next btn
        if(li.is(':last-child'))    {
            $(this.ns.nextBtn).hide();
        }   else    {
            $(this.ns.nextBtn).show();
        }
        
        $(this.ns.wooliestabs).hide();
        $(this.ns.wooliestabs + '[tab='+ tabNumberSelected +']').show();
        return false;
    },

    validateForm : function(tabNumber)   {

        var tabContainer = $(this.ns.wooliestabs + '[tab='+ tabNumber +']');
        var tabForm = tabContainer.find('form');

        tabForm.on('submit', function(e) {
            e.preventDefault();
        })

        tabForm.find('input[type=submit]').click();
        try {
            if(document.getElementById('formtab-' + tabNumber).checkValidity()) {
                return true;
            }   else {
                return false;
            }
        } catch(e)  {
            return false;
        }
    },

    validateAll : function()    {
        var hasError = false;
        var parent = this;
        var formPostItems = '';

        if(!document.getElementById('formtodetails').checkValidity()) {
            hasError = true;
            $('#formtodetails').find('input[type=submit]').click();
            return;
        }

        $.each($(this.ns.wooliestabs), function() {

            var tabNumber = $(this).attr('tab');
            if(!parent.validateForm(tabNumber)) {
                hasError = true; // flag has error
                $('.tabbable ul li[tabs='+ tabNumber +']').find('a').click();
                $(parent.ns.wooliestabs + '[tab=' + tabNumber + ']').find('input[type=submit]').click();
                return false;
            }
            var postItem = $('#formtab-' + tabNumber).serialize();
            formPostItems += '&' + postItem;
        });

        if(!hasError)   {
            // SUBMIT ALL!!
            formPostItems += '&' + $("#formtodetails").serialize() + '&' + $('#form_credentials').serialize();
            this._send(formPostItems);
        }

    },

    validateUpdateAll : function()    {
        var hasError = false;
        var parent = this;
        var formPostItems = '';

        if(!document.getElementById('formtodetailsupdate').checkValidity()) {
            hasError = true;
            $('#formtodetailsupdate').find('input[type=submit]').click();
            return;
        }

        $.each($(this.ns.wooliestabs), function() {

            var tabNumber = $(this).attr('tab');
            if(!parent.validateForm(tabNumber)) {
                hasError = true; // flag has error
                $('.tabbable ul li[tabs='+ tabNumber +']').find('a').click();
                $(parent.ns.wooliestabs + '[tab=' + tabNumber + ']').find('input[type=submit]').click();
                return false;
            }
            var postItem = $('#formtab-' + tabNumber).serialize();
            formPostItems += '&' + postItem;
        });


        if(!hasError)   {
            // Edit ALL!!
            formPostItems += '&' + $("#formtodetailsupdate").serialize() + '&' + $('#form_credentials').serialize();
            this._edit(formPostItems);
        }
    },

    _send : function(data)  {
        if(this.trigger_count == 0) {
            this.trigger_count = 1;
            var parent = this;
            $.ajax({
                type: "POST",
                data : data,
                url: $('#APP_DOMAIN').val() + 'travel_authorisations/save_form' ,
                success: function(data) {
                    // if successfully save. redirect to listing
                    parent.trigger_count = 0;
                    window.location.href = $('#APP_DOMAIN').val() + 'travel_authorisations?key=' + $('#FORM_KEY').val();
                }
            });
        }
    },

    _edit : function(data)  {
        if(this.trigger_count == 0) {
            this.trigger_count = 1;
            var parent = this;

            $.ajax({
                url: '/travel_authorisations/fetch_request_status/' + $('#entity_key').val()
            }).done(function(response){
                if(response == 1){
                    $.ajax({
                        type: "POST",
                        data : data,
                        url: $('#APP_DOMAIN').val() + 'travel_authorisations/edit_data',
                        success: function(data) {
                            // if successfully edited. redirect to listing
                            parent.trigger_count = 0;
                            window.location.href = $('#APP_DOMAIN').val() + 'travel_authorisations?key=' + $('#FORM_KEY').val();
                        }
                    });
                }else{
                    window.location.href = '/travel_authorisations/edit_locked?frmkey=' + $('#FORM_KEY').val();
                }
            });
        }
    }
}
$(document).ready(function() {
    wooliesTabs.init();
});