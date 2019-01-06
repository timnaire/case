// $('#btnRegister').click(function(e) {
//     var first_name = $('#first_name').val();
//     var last_name = $('#last_name').val();
//     var email = $('#email').val();
//     var phone = $('#phone').val();
//     var office = $('#office').val();
//     var law_practice = $('#law_practice').val();
//     var bar_number = $('#bar_number').val();

//     var sendInfo = {
//         first_name : first_name,
//         last_name : last_name,
//         email : email,
//         phone : phone,
//         office : office,
//         law_practice : law_practice,
//         bar_number : bar_number
//     }

//     $.post("/signup/attorneys",JSON.stringify(sendInfo),function(result){
//         console.log(result);
//     });
    
    // $.ajax({
    //     url: '/signup/attorneys',
    //     type: 'POST',
    //     dataType: 'json',
    //     contentType: 'application/json; charset-utf-8',
    //     data: JSON.stringify(sendInfo),
    //     success: function(response) {
    //         console.log(response);
    //     },
    //     error: function(error) {
    //         console.log(error);
    //     }
    // });
    // e.preventDefault();
// });