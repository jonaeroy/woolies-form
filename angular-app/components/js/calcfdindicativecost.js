var checkFDto = function(obj){

    var obj =$(obj);

    var to;
    var from;
    var ftype;
    var indCost = 0.00;

    to = obj.val();
    from = obj.parent().prev().find('.FD_From').val();
    ftype = obj.parent().next().next().next().next().next().find('.FD_Fare_Type').val();

    indCost = checkIndCost(from,to,ftype);

    obj.parent(indCost).next().next().next().next().next().next().find('.FD_Indicative_Cost').val(indCost);

    calcFDtotal();

}

var checkFDfrom = function(obj){

    var obj =$(obj);

    var to;
    var from;
    var ftype;
    var indCost = 0.00;

    to = obj.parent().next().find('.FD_To').val();
    from = obj.val(); 
    ftype = obj.parent().next().next().next().next().next().next().find('.FD_Fare_Type').val();

    indCost = checkIndCost(from,to,ftype);

    obj.parent(indCost).next().next().next().next().next().next().next().find('.FD_Indicative_Cost').val(indCost);

    calcFDtotal();

}

var checkFDftype = function(obj){

    var obj =$(obj);

    var to;
    var from;
    var ftype;
    var indCost = 0.00;

    to = obj.parent().prev().prev().prev().prev().prev().find('.FD_To').val();
    from = obj.parent().prev().prev().prev().prev().prev().prev().find('.FD_From').val();
    ftype = obj.val();

    indCost = checkIndCost(from,to,ftype);

    obj.parent(indCost).next().find('.FD_Indicative_Cost').val(indCost);

    calcFDtotal();

}

function checkIndCost(from,to,ftype){

    var indCost = 0.00;

    if(from == 'Adelaide' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 244
    }
    else if(from == 'Brisbane' && to == 'Adelaide' && ftype == 'Fixed'){
        indCost = 244
    }
    else if(from == 'Adelaide' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 531
    }
    else if(from == 'Brisbane' && to == 'Adelaide' && ftype == 'Flexible'){
        indCost = 531
    }
    else if(from == 'Canberra' && to == 'Adelaide' && ftype == 'Fixed'){
        indCost = 220
    }
    else if(from == 'Adelaide' && to == 'Canberra' && ftype == 'Fixed'){
        indCost = 220
    }
    else if(from == 'Canberra' && to == 'Adelaide' && ftype == 'Flexible'){
        indCost = 440
    }
    else if(from == 'Adelaide' && to == 'Canberra' && ftype == 'Flexible'){
        indCost = 440
    }
    else if(from == 'Adelaide' && to == 'Darwin' && ftype == 'Fixed'){
        indCost = 392
    }
    else if(from == 'Adelaide' && to == 'Darwin' && ftype == 'Flexible'){
        indCost = 741
    }
    else if(from == 'Darwin' && to == 'Adelaide' && ftype == 'Fixed'){
        indCost = 392
    }
    else if(from == 'Darwin' && to == 'Adelaide' && ftype == 'Flexible'){
        indCost = 741
    }
    else if(from == 'Adelaide' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 282
    }
    else if(from == 'Adelaide' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 642
    }
    else if(from == 'Perth' && to == 'Adelaide' && ftype == 'Fixed'){
        indCost = 282
    }
    else if(from == 'Perth' && to == 'Adelaide' && ftype == 'Flexible'){
        indCost = 642
    }
    else if(from == 'Brisbane' && to == 'Canberra' && ftype == 'Fixed'){
        indCost = 196
    }
    else if(from == 'Brisbane' && to == 'Canberra' && ftype == 'Flexible'){
        indCost = 380
    }
    else if(from == 'Canberra' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 196
    }
    else if(from == 'Canberra' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 380
    }
    else if(from == 'Brisbane' && to == 'Cairns' && ftype == 'Fixed'){
        indCost = 202
    }
    else if(from == 'Brisbane' && to == 'Cairns' && ftype == 'Flexible'){
        indCost = 461
    }
    else if(from == 'Cairns' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 461
    }
    else if(from == 'Cairns' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 202
    }
    else if(from == 'Brisbane' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 335
    }
    else if(from == 'Brisbane' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 780
    }
    else if(from == 'Perth' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 335
    }
    else if(from == 'Perth' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 780
    }
    else if(from == 'Brisbane' && to == 'Rockhampton' && ftype == 'Fixed'){
        indCost = 147
    }
    else if(from == 'Brisbane' && to == 'Rockhampton' && ftype == 'Flexible'){
        indCost = 406
    }
    else if(from == 'Rockhampton' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 147
    }
    else if(from == 'Rockhampton' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 406
    }
    else if(from == 'Brisbane' && to == 'Townsville' && ftype == 'Fixed'){
        indCost = 219
    }
    else if(from == 'Brisbane' && to == 'Townsville' && ftype == 'Flexible'){
        indCost = 420
    }
    else if(from == 'Townsville' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 219
    }
    else if(from == 'Townsville' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 420
    }
    else if(from == 'Canberra' && to == 'Darwin' && ftype == 'Fixed'){
        indCost = 701
    }
    else if(from == 'Canberra' && to == 'Darwin' && ftype == 'Flexible'){
        indCost = 1061
    }
    else if(from == 'Darwin' && to == 'Canberra' && ftype == 'Fixed'){
        indCost = 701
    }
    else if(from == 'Darwin' && to == 'Canberra' && ftype == 'Flexible'){
        indCost = 1061
    }
    else if(from == 'Melbourne' && to == 'Adelaide' && ftype == 'Flexible'){
        indCost = 344
    }
    else if(from == 'Melbourne' && to == 'Adelaide' && ftype == 'Fixed'){
        indCost = 152
    }
    else if(from == 'Adelaide' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 344
    }
    else if(from == 'Adelaide' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 152
    }
    else if(from == 'Brisbane' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 217
    }
    else if(from == 'Brisbane' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 496
    }
    else if(from == 'Melbourne' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 217
    }
    else if(from == 'Melbourne' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 496
    }
    else if(from == 'Canberra' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 172
    }
    else if(from == 'Canberra' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 334
    }
    else if(from == 'Melbourne' && to == 'Canberra' && ftype == 'Fixed'){
        indCost = 172
    }
    else if(from == 'Melbourne' && to == 'Canberra' && ftype == 'Flexible'){
        indCost = 334
    }
    else if(from == 'Darwin' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 266
    }
    else if(from == 'Darwin' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 639
    }
    else if(from == 'Melbourne' && to == 'Darwin' && ftype == 'Fixed'){
        indCost = 266
    }
    else if(from == 'Melbourne' && to == 'Darwin' && ftype == 'Flexible'){
        indCost = 639
    }
    else if(from == 'Hobart' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 154
    }
    else if(from == 'Hobart' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 329
    }
    else if(from == 'Melbourne' && to == 'Hobart' && ftype == 'Fixed'){
        indCost = 154
    }
    else if(from == 'Melbourne' && to == 'Hobart' && ftype == 'Flexible'){
        indCost = 329
    }
    else if(from == 'Melbourne' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 308
    }
    else if(from == 'Melbourne' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 690
    }
    else if(from == 'Perth' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 308
    }
    else if(from == 'Perth' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 690
    }
    else if(from == 'Canberra' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 381
    }
    else if(from == 'Canberra' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 744
    }
    else if(from == 'Perth' && to == 'Canberra' && ftype == 'Fixed'){
        indCost = 381
    }
    else if(from == 'Perth' && to == 'Canberra' && ftype == 'Flexible'){
        indCost = 744
    }
    else if(from == 'Darwin' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 305
    }
    else if(from == 'Darwin' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 697
    }
    else if(from == 'Perth' && to == 'Darwin' && ftype == 'Fixed'){
        indCost = 305
    }
    else if(from == 'Perth' && to == 'Darwin' && ftype == 'Flexible'){
        indCost = 697
    }
    else if(from == 'Hobart' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 439
    }
    else if(from == 'Hobart' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 823
    }
    else if(from == 'Perth' && to == 'Hobart' && ftype == 'Fixed'){
        indCost = 439
    }
    else if(from == 'Perth' && to == 'Hobart' && ftype == 'Flexible'){
        indCost = 823
    }
    else if(from == 'Karratha' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 377
    }
    else if(from == 'Karratha' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 583
    }
    else if(from == 'Perth' && to == 'Karratha' && ftype == 'Fixed'){
        indCost = 377
    }
    else if(from == 'Perth' && to == 'Karratha' && ftype == 'Flexible'){
        indCost = 583
    }
    else if(from == 'Albury' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 141
    }
    else if(from == 'Albury' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 383
    }
    else if(from == 'Sydney' && to == 'Albury' && ftype == 'Fixed'){
        indCost = 141
    }
    else if(from == 'Sydney' && to == 'Albury' && ftype == 'Flexible'){
        indCost = 383
    }
    else if(from == 'Armidale' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 162
    }
    else if(from == 'Armidale' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 399
    }
    else if(from == 'Sydney' && to == 'Armidale' && ftype == 'Fixed'){
        indCost = 162
    }
    else if(from == 'Sydney' && to == 'Armidale' && ftype == 'Flexible'){
        indCost = 399
    }
    else if(from == 'Coffs Harbour' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 150
    }
    else if(from == 'Coffs Harbour' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 396
    }
    else if(from == 'Sydney' && to == 'Coffs Harbour' && ftype == 'Fixed'){
        indCost = 150
    }
    else if(from == 'Sydney' && to == 'Coffs Harbour' && ftype == 'Flexible'){
        indCost = 396
    }
    else if(from == 'Dubbo' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 183
    }
    else if(from == 'Dubbo' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 373
    }
    else if(from == 'Sydney' && to == 'Dubbo' && ftype == 'Fixed'){
        indCost = 183
    }
    else if(from == 'Sydney' && to == 'Dubbo' && ftype == 'Flexible'){
        indCost = 373
    }
    else if(from == 'Port Macquarie' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 143
    }
    else if(from == 'Port Macquarie' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 372
    }
    else if(from == 'Sydney' && to == 'Port Macquarie' && ftype == 'Fixed'){
        indCost = 143
    }
    else if(from == 'Sydney' && to == 'Port Macquarie' && ftype == 'Flexible'){
        indCost = 372
    }
    else if(from == 'Sydney' && to == 'Wagga Wagga' && ftype == 'Fixed'){
        indCost = 160
    }
    else if(from == 'Sydney' && to == 'Wagga Wagga' && ftype == 'Flexible'){
        indCost = 363
    }
    else if(from == 'Wagga Wagga' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 160
    }
    else if(from == 'Wagga Wagga' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 363
    }
    else if(from == 'Adelaide' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 186
    }
    else if(from == 'Adelaide' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 413
    }
    else if(from == 'Sydney' && to == 'Adelaide' && ftype == 'Fixed'){
        indCost = 186
    }
    else if(from == 'Sydney' && to == 'Adelaide' && ftype == 'Flexible'){
        indCost = 413
    }
    else if(from == 'Brisbane' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 172
    }
    else if(from == 'Brisbane' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 370
    }
    else if(from == 'Sydney' && to == 'Brisbane' && ftype == 'Fixed'){
        indCost = 172
    }
    else if(from == 'Sydney' && to == 'Brisbane' && ftype == 'Flexible'){
        indCost = 370
    }
    else if(from == 'Canberra' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 154
    }
    else if(from == 'Canberra' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 263
    }
    else if(from == 'Sydney' && to == 'Canberra' && ftype == 'Fixed'){
        indCost = 154
    }
    else if(from == 'Sydney' && to == 'Canberra' && ftype == 'Flexible'){
        indCost = 263
    }
    else if(from == 'Darwin' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 338
    }
    else if(from == 'Darwin' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 748
    }
    else if(from == 'Sydney' && to == 'Darwin' && ftype == 'Fixed'){
        indCost = 338
    }
    else if(from == 'Sydney' && to == 'Darwin' && ftype == 'Flexible'){
        indCost = 748
    }
    else if(from == 'Hobart' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 221
    }
    else if(from == 'Hobart' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 449
    }
    else if(from == 'Sydney' && to == 'Hobart' && ftype == 'Fixed'){
        indCost = 221
    }
    else if(from == 'Sydney' && to == 'Hobart' && ftype == 'Flexible'){
        indCost = 449
    }
    else if(from == 'Melbourne' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 173
    }
    else if(from == 'Melbourne' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 362
    }
    else if(from == 'Sydney' && to == 'Melbourne' && ftype == 'Fixed'){
        indCost = 173
    }
    else if(from == 'Sydney' && to == 'Melbourne' && ftype == 'Flexible'){
        indCost = 362
    }
    else if(from == 'Auckland' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 691
    }
    else if(from == 'Sydney' && to == 'Auckland' && ftype == 'Flexible'){
        indCost = 691
    }
    else if(from == 'Frankfurt' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 10352
    }
    else if(from == 'Sydney' && to == 'Frankfurt' && ftype == 'Flexible'){
        indCost = 10352
    }
    else if(from == 'Hong Kong' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 3186
    }
    else if(from == 'Sydney' && to == 'Hong Kong' && ftype == 'Flexible'){
        indCost = 3186
    }
    else if(from == 'London' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 10352
    }
    else if(from == 'Sydney' && to == 'London' && ftype == 'Flexible'){
        indCost = 10352
    }
    else if(from == 'Los Angeles' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 10740
    }
    else if(from == 'Sydney' && to == 'Los Angeles' && ftype == 'Flexible'){
        indCost = 10740
    }
    else if(from == 'Mumbai' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 8245
    }
    else if(from == 'Sydney' && to == 'Mumbai' && ftype == 'Flexible'){
        indCost = 8245
    }
    else if(from == 'San Francisco' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 11346
    }
    else if(from == 'Sydney' && to == 'San Francisco' && ftype == 'Flexible'){
        indCost = 11346
    }
    else if(from == 'Shanghai' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 5093
    }
    else if(from == 'Sydney' && to == 'Shanghai' && ftype == 'Flexible'){
        indCost = 5093
    }
    else if(from == 'Perth' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 321
    }
    else if(from == 'Perth' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 725
    }
    else if(from == 'Sydney' && to == 'Perth' && ftype == 'Fixed'){
        indCost = 321
    }
    else if(from == 'Sydney' && to == 'Perth' && ftype == 'Flexible'){
        indCost = 725
    }
    else if(from == 'Sydney' && to == 'Townsville' && ftype == 'Fixed'){
        indCost = 231
    }
    else if(from == 'Sydney' && to == 'Townsville' && ftype == 'Flexible'){
        indCost = 551
    }
    else if(from == 'Townsville' && to == 'Sydney' && ftype == 'Fixed'){
        indCost = 231
    }
    else if(from == 'Townsville' && to == 'Sydney' && ftype == 'Flexible'){
        indCost = 551
    }
    else{
        indCost = 0.00
    }

    return indCost;
}

var calcFDtotal = function(){
        var total = 0.00;
        $.each($('.FD_Indicative_Cost'), function() {
            total = parseFloat(total) + parseFloat($(this).val());
        });
        total = parseFloat(total).toFixed(2);
        total = (isNaN(total)) ? 0.0 : total;

        $('#FD_Total').val(total);
}