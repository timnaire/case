var sendInfo = {}

$('#btnLoginLawyer').click(function(e){
    var email = $('#lawyer_email').val();
    var password = $('#lawyer_password').val();
    
    sendInfo = {
        email : email,
        password : password
    }

    $.post("/signin/lawyer",JSON.stringify(sendInfo),function(result){
        var err = 1;
        var m = result['message'];
        var email = result['email'];
        if(result['code'] == 200){
            window.location.replace('/mypage/dashboard');
        }
        else if(result['code'] == 401){
            window.location.replace('/signin/lawyer?err='+err+"&m="+m+"&email="+email)
        }else if(result['code'] == 406){
            window.location.replace('/signin/lawyer?err='+err+"&m="+m+"&email="+email)
        }
    }, "json");
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
});

$('#btnUpdateLawyer').click(function(e) {
    var id = $("#lawyer_id").val();
    var first_name = $('#first_name').val();
    var last_name = $('#last_name').val();
    var email = $('#email').val();
    var phone = $('#phone').val();
    var city= $('#city').val();
    var office = $('#office').val();
    var law_practice = $('#law_practice').val();
    var image = document.querySelector('input[type="file"]').files[0];

    sendInfo = {
        first_name : first_name,
        last_name : last_name,
        email : email,
        phone : phone,
        city : city,
        office : office,
        law_practice : law_practice 
    }

    $.post("/mypage/myaccount/"+id, JSON.stringify(sendInfo) ,function(result){
       console.log(result);
    }, "json");
    e.preventDefault();
});

 // if(image){
    //     getBase64(image).then(
    //     data => {
    //         // sendInfo['profile_pic'] = data;
    //         $.post("/mypage/myaccount/"+id, JSON.stringify({"profile_pic":data}) ,function(result){
    //             console.log(result);
    //          }, "json");
    //     }
    //     );
    // }

// const url = result['profile_pic'];
        // fetch(url)
        // .then(res => res.blob())
        // .then(blob => {
        //     const file = new File([blob], "File name")
        //     console.log(file);
        // });

// functions here >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#lawyerpic').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
$("#image").change(function() {
    readURL(this);
});

function getBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.substr(reader.result.indexOf(',') + 1));
      reader.onerror = error => reject(error);
    });
  }
    
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