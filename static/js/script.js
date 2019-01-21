$(document).ready(function(){
    var sendInfo = {}

    // find a lawyer button
    $('#btnFindLawyer').click(function(e){
        e.preventDefault();
        var law_practice = $('#practice').val();
        var cityOrMunicipality = $('#cityOrMunicipality').val();
        sendInfo = {
            law_practice : law_practice,
            cityOrMunicipality : cityOrMunicipality
        }
        // console.log(JSON.stringify(sendInfo))
        $.post("/lawyer/find", JSON.stringify(sendInfo), function(response){
            var content = $();
            if(response['error'] == false){
                var lawyers = response['lawyers']
                // looping through all found layers and displaying the info
                for(var key in lawyers){
                    if(lawyers.hasOwnProperty(key)){
                        // setting the default info for about me
                        if(lawyers[key].lawyer.aboutme == null){
                            lawyers[key].lawyer.aboutme = "No overview found";
                        }
                        // setting default image if there is no image foundd
                        if(lawyers[key].lawyer.profile_pic == null){
                            lawyers[key].lawyer.profile_pic = "../static/images/default_lawyer_pic.png";
                        }
                        // var stateObj = { practice : law_practice, cityOrMunicipality : cityOrMunicipality }
                        // window.history.pushState( stateObj, 'Find Lawyer', '/law-pactice='+law_practice+'&city-or-municipality='+cityOrMunicipality);
                        content = content.add(`
                                    <div class="col-md-2">&nbsp;</div>
                                        <div class="col-md-8">
                                            <div class="row space-16">&nbsp;</div>
                                            <div class="row">
                                                <div class="col-sm-4">
                                                    <div class="thumbnail">
                                                        <div class="caption text-center" onclick="location.href='localhost:8080/#'">
                                                            <div class="position-relative">
                                                                <img src="${lawyers[key].lawyer.profile_pic}" alt="profile" style="width:160px;height:160px;" />
                                                            </div>
                                                            <h4 id="thumbnail-label"><a href="#" target="_blank">${lawyers[key].lawyer.first_name} ${lawyers[key].lawyer.last_name}</a></h4>
                                                            <p><i class="glyphicon glyphicon-envelope  light-red lighter bigger-120"></i>&nbsp;${lawyers[key].lawyer.email}</p>
                                                            <div class="thumbnail-description smaller">${lawyers[key].lawyer.aboutme}</div>
                                                        </div>
                                                        <div class="caption card-footer text-center">
                                                            <a class="btn btn-primary btn-block" href="#">View More</a>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        <div class="col-md-2">&nbsp;</div>
                                    </div>
                                `);
                    }
                }
                // displaying to the found-lawyer div in home.html
                $('#found-lawyer').html(content)
                
            } else if(response['error'] == true){
                console.log(response['message']);
            }
        } , "json" );
    });

    // profile picture update
    $('#btnLawyerSavePicture').click(function(e){
        e.preventDefault();
        var id = $(".lawyer_id").val();
        var file_data = $('#image').prop('files')[0];
        var form_data = new FormData();
        form_data.append('image', file_data);
        $.ajax({
            url: "/lawyer/"+id+"/account-setting/profile-picture", // point to server-side controller method
            dataType: 'json', // what to expect back from the server
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post',
            success: function (response) {
                console.log(response) // display success response from the server
            },
            error: function (response) {
                console.log(response) // display error response from the server
            }
        });
    });

    // profile information update
    $('#btnLawyerSaveInfo').click(function(e){
        e.preventDefault();
        var id = $(".lawyer_id").val();
        var first_name = $('#ufirst_name').val().trim();
        var last_name = $('#ulast_name').val().trim();
        var phone = $('#uphone').val().trim();
        var cityOrMunicipality= $('#ucityOrMunicipality').val().trim();
        var office = $('#uoffice').val().trim();
        var aboutme = $('#uaboutme').val().trim();
        var practice = [];
        $.each($("input[class='practice']:checked"), function(){            
            practice.push($(this).val());
        });

        sendInfo = {
            first_name : first_name,
            last_name : last_name,
            phone : phone,
            cityOrMunicipality : cityOrMunicipality,
            office : office,
            aboutme : aboutme,
            law_practice : practice
        }
        $.post("/lawyer/"+id+"/account-setting/profile-information", JSON.stringify(sendInfo), function(response){
            console.log(response)
        } ,"json" );
    });

    $('#btnLawyerSaveEmail').click(function(e){
        e.preventDefault();
        var id = $(".lawyer_id").val();
        var current = $('#current_email').val().trim();
        var new_email = $('#new_email').val().trim();
        var password = $('#e_current_password').val().trim();
        sendInfo = {
            current : current,
            new_email : new_email,
            password : password
        }
        $.post("/lawyer/"+id+"/account-setting/change-email", JSON.stringify(sendInfo) ,function(response){
            console.log(response)
        })
    });

    $('#btnLawyerSavePassword').click(function(e){
        e.preventDefault();
        var id = $(".lawyer_id").val();
        var current_pass = $('#current_password').val();
        var new_pass = $('#new_password').val();
        var confirm_pass = $('#confirm_password').val();
        sendInfo = {
            current : current_pass,
            newpass : new_pass,
            confirm : confirm_pass
        }
        $.post("/lawyer/"+id+"/account-setting/change-password", JSON.stringify(sendInfo) ,function(response){
            console.log(response)
        })
    });

    // lawyer sign in
    $('#btnLawyerSignin').click(function(e){
        var email = $('#lawyer_email').val();
        var password = $('#lawyer_password').val();
        
        sendInfo = {
            email : email,
            password : password
        }

        $.post("/lawyer/signin",JSON.stringify(sendInfo),function(result){
            var err = 1;
            var m = result['message'];
            var email = result['email'];
            if(result['error'] == false){
                window.location.replace('/lawyer/dashboard');
            }
            else if(result['error'] == true){
                window.location.replace('/lawyer/signin?err='+err+"&m="+m+"&email="+email)
            }
            
        }, "json");
        e.preventDefault();
    });

    // lawyer sign up
    $('#btnLawyerSignup').click(function(e) {
        e.preventDefault();
        var first_name = $('#first_name').val().trim();
        var last_name = $('#last_name').val().trim();
        var email = $('#email').val().trim();
        var phone = $('#phone').val().trim();
        var cityOrMunicipality = $('#cityOrMunicipality').val().trim();
        var office = $('#office').val().trim();
        // var law_practice = $('#law_practice').val();
        var practice = [];
        $.each($("input[class='practice']:checked"), function(){            
            practice.push($(this).val());
        });
        
        sendInfo = {
            first_name : first_name,
            last_name : last_name,
            email : email,
            phone : phone,
            cityOrMunicipality : cityOrMunicipality,
            office : office,
            law_practice : practice
        }

        $.post("/lawyer/signup",JSON.stringify(sendInfo),function(result){
            var succ = 1;
            var err = 1;
            var m = result['message']
            if(result['error'] == false){
                window.location.replace('/lawyer/signup?succ='+succ+"&m="+m);
            }else if(result['error'] == true){
                window.location.replace('/lawyer/signup?err='+err+"&m="+m);
            }
        });
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

    // function getBase64(file) {
    //     return new Promise((resolve, reject) => {
    //     const reader = new FileReader();
    //     reader.readAsDataURL(file);
    //     reader.onload = () => resolve(reader.result.substr(reader.result.indexOf(',') + 1));
    //     reader.onerror = error => reject(error);
    //     });
    // }
        
    $( function() {
        // var province = ["Abra","Agusan del Norte","Agusan del Sur","Aklan","Albay","Antique","Apayao","Aurora","Basilan",
        // "Bataan","Batanes","Batangas","Benguet","Biliran","Bohol","Bukidnon","Bulacan","Camarines Norte","Camarines Sur",
        // "Camiguin","Capiz","Catandunes","Cavite","Cebu","Compostela Valley","Cotabato","Davao del Norte","Davao del Sur",
        // "Davao Occidental","Davao Oriental","Dinagat Island","Estern Samar","Guimaras","Ifugao","Ilocos Norte","Ilocos Sur",
        // "Iloilo","Isabela","Kalinga","La Union","Laguna","Lanao del Norte","Lanao del Sur","Leyte","Maguindanao","Manila",
        // "Marinduque","Masbate","Misamis Occidental","Misamis Oriental","Mountain Province","Negros Occidental","Negros Oriental"
        // ,"Northern Samar","Nueva Ecija","Occidental Mindoro","Oriental Mindoro","Palawan","Pampanga","Pangasinan","Quezon",
        // "Quirino","Rizal","Romblon","Samar","Sarangani","Siquijor","Sorsogon","South Cotabato","Southern Leyte","Sultan Kudarat",
        // "Sulu","Surigao del Norte","Surigao del Sur","Tarlac","Tawi-Tawi","Zambales","Zamboanga del Norte","Zamboanga del Sur",
        // "Zamboanga Sibugay"]
        var city = ["Alcantara","Alcoy","Alegria","Aloguinsan","Argao","Asturias","Badian","Balamban","Bantayan","Barili","Bogo","Boljoon","Borbon",
        "Carcar","Carmen","Catmon","Cebu City","Compostela","Consolacion","Cordova","Daanbantayan","Dalaguete","Danao","Dumanjug","Ginatilan",
        "Lapu-Lapu","Liloan","Madridejos","Malabuyoc","Mandaue","Medellin","Minglanilla","Moalboal","Naga","Oslob","Pilar","Pinamungajan",
        "Poro","Ronda","Samboan","San Fernando","San Francisco","San Remigio","Santa Fe","Santander","Sibonga","Sogod","Tabogon","Tabuelan",
        "Talisay","Toledo","Tuburan","Tudela"]
        $("#cityOrMunicipality , #ucityOrMunicipality" ).autocomplete({
        source: city
        });
    } );
});