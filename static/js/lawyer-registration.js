$(function(){
	$("#wizard").steps({
        headerTag: "h2",
        bodyTag: "section",
        transitionEffect: "fade",
        enableAllSteps: true,
        transitionEffectSpeed: 500,
        labels: {
            finish: "Submit",
            next: "Forward",
            previous: "Backward"
        }
    });
    $('.wizard > .steps li a').click(function(){
    	$(this).parent().addClass('checked');
		$(this).parent().prevAll().addClass('checked');
		$(this).parent().nextAll().removeClass('checked');
    });
    // Custome Jquery Step Button
    $('.forward').click(function(){
    	$("#wizard").steps('next');
    })
    $('.backward').click(function(){
        $("#wizard").steps('previous');
    })
    
    $("a[href='#finish']").click(function(e) {
        e.preventDefault();
        var first_name = $('#first_name').val().trim();
        var last_name = $('#last_name').val().trim();
        var rollno = $('#rollno').val();
        var email = $('#email').val().trim();
        var phone = $('#phone').val().trim();
        var firm = $('#firm').val().trim();
        var sex = $('#sex').val();
        var password = $('#the-password').val().trim();
        var confirm = $('#confirm-password').val().trim();
        var cityOrMunicipality = $('#cityOrMunicipality').val().trim();
        var office = $('#office').val().trim();
        // var law_practice = $('#law_practice').val();
        var practice = [];
        $.each($("input[class='practice']:checked"), function(){            
            practice.push($(this).val());
        });
        
        alert(first_name);
        sendInfo = {
            first_name : first_name,
            last_name : last_name,
            email : email,
            sex : sex,
            firm : firm,
            password : password,
            confirm : confirm,
            rollno : rollno,
            phone : phone,
            cityOrMunicipality : cityOrMunicipality,
            office : office,
            law_practice : practice
        }

        $.post("/lawyer/signup",JSON.stringify(sendInfo),function(response){
            var succ = 1;
            var err = 1;
            var m = response['message']
            if(response['error'] == false){
                window.location.replace('/lawyer/signup?succ='+succ+"&m="+m);
            }else if(response['error'] == true){
                window.location.replace('/lawyer/signup?err='+err+"&m="+m);
            }
        });
    });

    // Select Dropdown
    $('html').click(function() {
        $('.select .dropdown').hide(); 
    });
    $('.select').click(function(event){
        event.stopPropagation();
    });
    $('.select .select-control').click(function(){
        $(this).parent().next().toggle();
    })    
    $('.select .dropdown li').click(function(){
        $(this).parent().toggle();
        var text = $(this).attr('rel');
        $(this).parent().prev().find('div').text(text);
    })


})
