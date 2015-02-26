$(document).ready(function(){
    
    //Hides all divs except the first one
    for (var i=1 ; i<=10 ; i++) { 
        $('.d'+[i]).hide();
    };
    $('.d1').show();

    //Hides all Previous button of Unsuccessful application
    for (x=2 ; x<=8 ; x++) { 
        $('#unsuc-prev'+[x]).hide();
    };
    
    $('.unsuc').hide();

    //Checks the Agree/Disagree fields if checked
    function setButton() {
    for (var i=1; i<=8;i++) {
            if ($("input[name=question_"+[i]+"]:checked").length > 0)
                $("#next"+[i]).attr("disabled", false);
            else
                $("#next"+[i]).attr("disabled", true);
        }
    }

    for (var y=1; y<=8; y++) {
       $("input[name=question_"+[y]+"]").click(function() { setButton(); }); 
    }
    setButton();
    //End of check


    //1
    $("#next1").click(function(){
    var selValue = $('.form-container input[class="radio1"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev1').show();
                $('.d1').hide();
            
                 $('#unsuc-prev1').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev1').hide();
                    $('.d1').show();
                    $('#submit_response').show();
                });
            }
        
        else {
                                
                $('.d2').show();
                $('.d1').hide(); 
        }
    });
    //1

    //2
   $("#next2").click(function(){
   var selValue = $('.form-container input[class="radio2"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev2').show();
                $('#unsuc-prev1').hide();
                $('.d2').hide();
            
                 $('#unsuc-prev2').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev2').hide();
                    $('.d2').show();
                });
            }
        
        else {
                                
                $('.d3').show();
                $('.d2').hide();
        } 
    });
    
    $("#prev2").click(function(){ 
         $('.d2').hide();
         $('.d1').show();

    });
    //2
    

    //3         
    $("#next3").click(function(){
    var selValue = $('.form-container input[class="radio3"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev3').show();
                $('#unsuc-prev2').hide();
                $('#unsuc-prev1').hide();
                $('.d3').hide();
            
                 $('#unsuc-prev3').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev3').hide();
                    $('.d3').show();
                });
            }
        
        else {
                $('.d4').show();
                $('.d3').hide();
        } 
    });
    
    $("#prev3").click(function(){ 
         $('.d3').hide();
         $('.d2').show();  
    });
    //3
    

    //4
    $("#next4").click(function(){
    var selValue = $('.form-container input[class="radio4"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev4').show();
                $('#unsuc-prev3').hide();
                $('#unsuc-prev1').hide();
                $('.d4').hide();
            
                 $('#unsuc-prev4').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev4').hide();
                    $('.d4').show();
                });
            }
        
        else {
                $('.d5').show();
                $('.d4').hide();
        } 
    });
    
    $("#prev4").click(function(){ 
         $('.d4').hide();
         $('.d3').show();  
    });
    //4
    
    
    //5
    $("#next5").click(function(){
    var selValue = $('.form-container input[class="radio5"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev5').show();
                $('#unsuc-prev4').hide();
                $('#unsuc-prev1').hide();
                $('.d5').hide();
            
                 $('#unsuc-prev5').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev5').hide();
                    $('.d5').show();
                });
            }
        
        else {                   
                $('.d6').show();
                $('.d5').hide();
             
        } 
    });
    
    $("#prev5").click(function(){ 
         $('.d5').hide();
         $('.d4').show();  
    });
    //5
    
    //6
    $("#next6").click(function(){
    var selValue = $('.form-container input[class="radio6"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev6').show();
                $('#unsuc-prev5').hide();
                $('#unsuc-prev1').hide();
                $('.d6').hide();
            
                 $('#unsuc-prev6').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev6').hide();
                    $('.d6').show();
                });
            }
        
        else {
                $('.d7').show();
                $('.d6').hide();
        
        } 
    });
    
    $("#prev6").click(function(){ 
         $('.d6').hide();
         $('.d5').show();  
    });
    //6
    
    //7
    $("#next7").click(function(){
    var selValue = $('.form-container input[class="radio7"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev7').show();
                $('#unsuc-prev6').hide();
                $('#unsuc-prev1').hide();
                $('.d7').hide();
            
                 $('#unsuc-prev7').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev7').hide();
                    $('.d7').show();
                });
            }
        
        else {
                $('.d8').show();
                $('.d7').hide();
        } 
    });
    
    $("#prev7").click(function(){ 
         $('.d7').hide();
         $('.d6').show();  
    });
    //7
    
    //8
    $("#next8").click(function(){
    var selValue = $('.form-container input[class="radio8"]:checked').val();
        
        if (selValue == 'Disagree') {
                $('.unsuc').show();
                $('#unsuc-prev8').show();
                $('#unsuc-prev7').hide();
                $('#unsuc-prev1').hide();
                $('.d8').hide();
            
                 $('#unsuc-prev8').click(function(){  
                    $('.unsuc').hide();
                    $('#unsuc-prev8').hide();
                    $('.d8').show();
                });
            }
        
        else {
                $('.d9').show();
                $('#next9').attr("disabled", true);
                $('.d8').hide();
        } 
    });

    $("#full_name").on('change',function(){ 
        check_fields();
    });

    $("#payroll_number").on('change',function(){ 
        check_fields();
    });

    $("#cost_centre").on('change',function(){ 
        check_fields();
    });

    $("#location_name").on('change',function(){ 
        check_fields();
    });

    $("#purchase_amount").on('change',function(){ 
        check_fields();
    });

    $("#device_description").on('change',function(){ 
        check_fields();
    });

    $("#purchase_date").on('change',function(){ 
        check_fields();
    });

    $("#gst_amount").on('change',function(){ 
        check_fields();
    });

    $("#device_purchase_type").on('change',function(){ 
        check_fields();
    });

    function check_fields(){

        full_name = $('#full_name').val();
        payroll_number = $('#payroll_number').val();
        cost_centre = $('#cost_centre').val();
        location_name = $('#location_name').val();
        device_purchase_type = $('#device_purchase_type').val();
        purchase_amount = $('#purchase_amount').val();
        device_description = $('#device_description').val();
        purchase_date = $('#purchase_date').val();
        gst_amount = $('#gst_amount').val();
        
        if (full_name == ''){ $('#next9').attr("disabled", true); }
        else if (payroll_number == ''){ $('#next9').attr("disabled", true); }
        else if (cost_centre == ''){ $('#next9').attr("disabled", true); }
        else if (location_name == ''){ $('#next9').attr("disabled", true); }
        else if (device_purchase_type == ''){ $('#next9').attr("disabled", true);  }
        else if (purchase_amount == ''){ $('#next9').attr("disabled", true); }
        else if (device_description == ''){ $('#next9').attr("disabled", true);  }
        else if (purchase_date == ''){ $('#next9').attr("disabled", true); }
        else if (gst_amount == ''){ $('#next9').attr("disabled", true); }
        else{$('#next9').attr("disabled", false);}
    }
    
    $("#prev8").click(function(){ 
         $('.d8').hide();
         $('.d7').show();  
    });
    //8
    
    //9
    $("#next9").click(function(){

        $('.d10').show();
        $('.d9').hide();
    });
    
    $("#prev9").click(function(){ 
         $('.d9').hide();
         $('.d8').show();  
    });
    //9
    
    //10
    $("#prev10").click(function(){ 
         $('.d10').hide();
         $('.d9').show();  
    });
    //10

    // Purchase details validator
    $('#black').h5Validate({
        errorClass:'black'
    });
});
