(function(window,document,undefined){

    var bind_update_field = function(win, field_name){
        return function(val){
            win.document.getElementById(field_name).value = val;
            // are we an image browser
            if (typeof(win.ImageDialog) != "undefined") {
                // we are, so update image dimensions...
                if (win.ImageDialog.getImageData) win.ImageDialog.getImageData();
                // ... and preview if necessary
                if (win.ImageDialog.showPreviewImage) win.ImageDialog.showPreviewImage(val);
            }
        };
    };


    var hide_popups = function(){
        var wm = window.tinymce.activeEditor.windowManager;
        this._hidden_windows = [];
        for(var winx in wm.windows){
            var win = wm.windows[winx];
            if(win._visible) win.hide();
            this._hidden_windows.push(win);
        }
    };

    var show_popups = function(){
        var wm = window.tinymce.activeEditor.windowManager;
        for(var winx in this._hidden_windows){
            this._hidden_windows[winx].show();
        }
    };

    var file_browser_callback = function(field_name, url, type, win){
        if(type == 'image'){
            create_photo_picker(bind_update_field(win, field_name));
        } else {
            create_media_picker(bind_update_field(win, field_name));
        }
    };

    var create_photo_picker = function(update_field){
        var view = new google.picker.PhotosView();
        var upload_view = new google.picker.View(google.picker.ViewId.PHOTO_UPLOAD);
        var search_view = new google.picker.ImageSearchView();

        var picker = new google.picker.PickerBuilder().
        addView(view).addView(upload_view).addView(search_view).
        addView(google.picker.ViewId.RECENTLY_PICKED).
        setCallback(function(data){
            if (data.action == google.picker.Action.PICKED) {
                var doc = data.docs[0];
                if(doc.thumbnails){
                    update_field(doc.thumbnails.pop().url);
                } else {
                    update_field(doc.url);
                }
            }
            if(data.action == google.picker.Action.PICKED || data.action == google.picker.Action.CANCEL){
                show_popups();
            }
        }).
        build();

        hide_popups();
        picker.setVisible(true);
    };


    var create_media_picker = function(update_field){

        var docs_view_group = new google.picker.ViewGroup(google.picker.ViewId.DOCS);
        docs_view_group.addView(new google.picker.DocsUploadView());

        var image_view_group = new google.picker.ViewGroup(new google.picker.PhotosView());
        image_view_group.addView(google.picker.ViewId.PHOTO_UPLOAD);
        image_view_group.addView(new google.picker.ImageSearchView());
        image_view_group.addView(google.picker.ViewId.DOCS_IMAGES);

        var picker = new google.picker.PickerBuilder().
        addViewGroup(docs_view_group).
        addViewGroup(image_view_group).
        addView(google.picker.ViewId.YOUTUBE).
        addView(google.picker.ViewId.RECENTLY_PICKED).
        setCallback(function(data){
            if (data.action == google.picker.Action.PICKED) {
                var doc = data.docs[0];
                update_field(doc.url);
            }
            if(data.action == google.picker.Action.PICKED || data.action == google.picker.Action.CANCEL){
                show_popups();
            }
        }).
        build();

        hide_popups();
        picker.setVisible(true);
    };


    window.google.load('picker', '1');
    window.tinymce_file_browser = file_browser_callback;
})(window, document);