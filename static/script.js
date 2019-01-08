var sendInfo = {}

$('#btnLogin').click(function(e){
    var email = $('#email').val();
    var password = $('#password').val();

    sendInfo = {
        email : email,
        password : password
    }

    $.post("/signin/lawyer",JSON.stringify(sendInfo),function(result){
        if(result['code'] == 200){
            window.location.replace('/mypage/dashboard');
        }
        
    });
    e.preventDefault();
});

$('#btnRegister').click(function(e) {
    var first_name = $('#first_name').val();
    var last_name = $('#last_name').val();
    var email = $('#email').val();
    var phone = $('#phone').val();
    var office = $('#office').val();
    var law_practice = $('#law_practice').val();
    var bar_number = $('#bar_number').val();

    sendInfo = {
        first_name : first_name,
        last_name : last_name,
        email : email,
        phone : phone,
        office : office,
        law_practice : law_practice,
        bar_number : bar_number
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