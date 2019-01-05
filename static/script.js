$('#btnRegister').click(function(e) {
    var first_name = $('#first_name').val();
    var last_name = $('#last_name').val();
    var email = $('#email').val();
    var phone = $('#phone').val();
    var office = $('#office').val();
    var specialize = $('#specialize').val();
    var bar_number = $('#bar_number').val();

    var sendInfo = {
        first_name : first_name,
        last_name : last_name,
        email : email,
        phone : phone,
        office : office,
        specialize : specialize,
        bar_number : bar_number
    }

    $.ajax({
        url: '/attorneys',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(sendInfo),
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
});