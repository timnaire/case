var sendInfo = {}

$('#btnLoginLawyer').click(function(e){
    var email = $('#login_email').val();
    var password = $('#login_password').val();

    sendInfo = {
        email : email,
        password : password
    }

    $.post("/signin/lawyer",JSON.stringify(sendInfo),function(result){
        if(result['code'] == 200){
            window.location.replace('/mypage/dashboard');
        }
        else{
            alert("Wrong Input!");
        }
    });
    e.preventDefault();
});

$('#btnRegisterLawyer').click(function(e) {
    var first_name = $('#first_name').val();
    var last_name = $('#last_name').val();
    var email = $('#email').val();
    var phone = $('#phone').val();
    var city = $('#city').val();
    var office = $('#office').val();
    var law_practice = $('#law_practice').val();

    sendInfo = {
        first_name : first_name,
        last_name : last_name,
        email : email,
        phone : phone,
        city : city,
        office : office,
        law_practice : law_practice
    }

    $.post("/signup/lawyer",JSON.stringify(sendInfo),function(result){
        if(result['code'] == 200){
            var succ = 1;
            var m = result['message']
            window.location.replace('/signup/lawyer?succ='+succ+"&m="+m);
        }else if(result['code'] == 400){
            var err = 1;
            var m = result['message']
            window.location.replace('/signup/lawyer?err='+err+"&m="+m);
        }
    });
    e.preventDefault();
});

// $('#btnLawyerUpdate').click(function(e) {
//     var first_name = $('#first_name').val();
//     var last_name = $('#last_name').val();
//     var email = $('#email').val();
//     var phone = $('#phone').val();
//     var province= $('#province').val();
//     var office = $('#office').val();
//     var law_practice = $('#law_practice').val();
//     var bar_number = $('#bar_number').val();

//     sendInfo = {
//         first_name : first_name,
//         last_name : last_name,
//         email : email,
//         phone : phone,
//         province : province,
//         office : office,
//         law_practice : law_practice,
//         bar_number : bar_number
//     }

//     $.post("/update/lawyer",JSON.stringify(sendInfo),function(result){
//         if(result['code'] == 200){
//             var succ = 1;
//             var m = result['message']
//             window.location.replace('/update/lawyer?succ='+succ+"&m="+m);
//         }else if(result['code'] == 400){
//             var err = 1;
//             var m = result['message']
//             window.location.replace('/update/lawyer?err='+err+"&m="+m);
//         }
//     });
//     e.preventDefault();
// });
    
$( function() {
    var availableCity = ["Abra","Agusan del Norte","Agusan del Sur","Aklan","Albay","Antique","Apayao","Aurora","Basilan",
    "Bataan","Batanes","Batangas","Benguet","Biliran","Bohol","Bukidnon","Bulacan","Camarines Norte","Camarines Sur",
    "Camiguin","Capiz","Catandunes","Cavite","Cebu","Compostela Valley","Cotabato","Davao del Norte","Davao del Sur",
    "Davao Occidental","Davao Oriental","Dinagat Island","Estern Samar","Guimaras","Ifugao","Ilocos Norte","Ilocos Sur",
    "Iloilo","Isabela","Kalinga","La Union","Laguna","Lanao del Norte","Lanao del Sur","Leyte","Maguindanao","Manila",
    "Marinduque","Masbate","Misamis Occidental","Misamis Oriental","Mountain Province","Negros Occidental","Negros Oriental"
    ,"Northern Samar","Nueva Ecija","Occidental Mindoro","Oriental Mindoro","Palawan","Pampanga","Pangasinan","Quezon",
    "Quirino","Rizal","Romblon","Samar","Sarangani","Siquijor","Sorsogon","South Cotabato","Southern Leyte","Sultan Kudarat",
    "Sulu","Surigao del Norte","Surigao del Sur","Tarlac","Tawi-Tawi","Zambales","Zamboanga del Norte","Zamboanga del Sur",
    "Zamboanga Sibugay"]
    $( "#city" ).autocomplete({
      source: availableCity
    });
  } );