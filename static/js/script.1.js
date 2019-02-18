$(document).ready(function(){
    var sendInfo = {}
    // Initiate the wowjs
  new WOW().init();

    $('#login-container-div').show(1000);
  $('#findlawyer').fadeIn(1000);
  $('#card-result-container').fadeIn(1000);
    $('#btnClientSignin').click(function(e){
        e.preventDefault()
        var email = $('#client_login_email').val();
        var password = $('#client_login_password').val();
        sendInfo = { email : email, password : password }

        $.post("/client/signin", JSON.stringify(sendInfo) ,function(response){
            if(response['error'] == false){
                window.location.replace('/client/dashboard');
            }else if (response['error'] == true){
                window.location.replace('/lawyer/signin?err='+err+"&m="+m+"&email"+email)
            }
        }, "json")
    });
    
    $('#btnClientSignUp').click(function(e){
        e.preventDefault();
        var first_name = $('#csu_first_name').val();
        var last_name = $('#csu_last_name').val();
        var email = $('#csu_email').val();
        var sex =$("[name='csex']:checked").val();
        var phone = $('#csu_phone').val();
        var address = $('#csu_address').val();
        var password = $('#csu_the-password').val();
        var confirm = $('#csu_confirm-password').val();
        sendInfo = {
            first_name : first_name,
            last_name : last_name,
            email : email,
            phone : phone,
            address : address,
            sex : sex,
            password : password,
            confirm : confirm
        }
        $.post("/client/signup",JSON.stringify(sendInfo),function(response){
            var succ = 1;
            var err = 1;
            var m = response['message']
            if(response['error'] == false){
                window.location.replace('/client/signup?succ='+succ+"&m="+m);
            }else if(response['error'] == true){
                window.location.replace('/client/signup?err='+err+"&m="+m);
            }
        });
    });

    // ---------------------------------------------------------------------------------------------------------------------------------------------
    // for lawyers below
    $('#btnAddCase').click(function(e){
        e.preventDefault();
        var id = $('#lawyer_id').val();
        var case_title = $('#add-case').val();
        var client_id = $('#client-id').val();
        var case_description = $('#case-description').val();
        alert(client_id);
        sendInfo = { 
            case_title : case_title,
            client_id : client_id,
            case_description : case_description
        }
        $.post("/lawyer/"+id+"/newcase", JSON.stringify(sendInfo) ,function(response){
            if(response['error'] == false){
                alert('Case has been added!');
            }
            else if(response['error'] == true){
                alert('Creating case failed!');
            }
        }, "json")
    });

    // find a lawyer button
    // $('#btnFindLawyer').click(function(e){
    //     e.preventDefault();
    //     var law_practice = $('#lawpractice').val();
    //     var cityOrMunicipality = $('#cityOrMunicipality').val();
    //     sendInfo = {
    //         law_practice : law_practice,
    //         cityOrMunicipality : cityOrMunicipality
    //     }

    //     console.log(sendInfo);
    //     // console.log(JSON.stringify(sendInfo))
    //     $.post("/lawyer/found", JSON.stringify(sendInfo), function(response){
    //         var content = $();
    //         if(response['error'] == false){
    //             var lawyers = response['lawyers']
    //             // looping through all found layers and displaying the info
    //             for(var key in lawyers){
    //                 if(lawyers.hasOwnProperty(key)){
    //                     // setting the default info for about me
    //                     if(lawyers[key].lawyer.aboutme == null){
    //                         lawyers[key].lawyer.aboutme = "No overview found";
    //                     }
    //                     // setting default image if there is no image foundd
    //                     if(lawyers[key].lawyer.profile_pic == null){
    //                         lawyers[key].lawyer.profile_pic = "../static/images/default_lawyer_pic.png";
    //                     }
    //                     // var stateObj = { practice : law_practice, cityOrMunicipality : cityOrMunicipality }
    //                     // window.history.pushState( stateObj, 'Find Lawyer', '/law-pactice='+law_practice+'&city-or-municipality='+cityOrMunicipality);
    //                     content = content.add(`
    //                                 <div class="col-md-2">&nbsp;</div>
    //                                     <div class="col-md-8">
    //                                         <div class="row space-16">&nbsp;</div>
    //                                         <div class="row">
    //                                             <div class="col-sm-4">
    //                                                 <div class="thumbnail">
    //                                                     <div class="caption text-center" onclick="location.href='localhost:8080/#'">
    //                                                         <div class="position-relative">
    //                                                             <img src="${lawyers[key].lawyer.profile_pic}" alt="profile" style="width:160px;height:160px;" />
    //                                                         </div>
    //                                                         <h4 id="thumbnail-label"><a href="#" target="_blank">${lawyers[key].lawyer.first_name} ${lawyers[key].lawyer.last_name}</a></h4>
    //                                                         <p><i class="glyphicon glyphicon-envelope  light-red lighter bigger-120"></i>&nbsp;${lawyers[key].lawyer.email}</p>
    //                                                         <div class="thumbnail-description smaller">${lawyers[key].lawyer.aboutme}</div>
    //                                                     </div>
    //                                                     <div class="caption card-footer text-center">
    //                                                         <a class="btn btn-primary btn-block" href="#">View More</a>
    //                                                     </div>
    //                                                 </div>
    //                                             </div>
    //                                         </div>
    //                                     <div class="col-md-2">&nbsp;</div>
    //                                 </div>
    //                             `);
    //                 }
    //             }
    //             // displaying to the found-lawyer div in home.html
    //             $('#found-lawyer').html(content)
                
    //         } else if(response['error'] == true){
    //             console.log(response['message']);
    //         }
    //     } , "json" );
    // });

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

    $('#deactivateLawyer').click(function(e){
        e.preventDefault();
        var id = $(".lawyer_id").val();

        sendInfo = {
            id : id
        }

        $.post("/lawyer/"+id+"/deactivate", JSON.stringify(sendInfo), function(response){
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

        $.post("/lawyer/signin",JSON.stringify(sendInfo),function(response){
            var err = 1;
            var m = response['message'];
            var email = response['email'];
            if(response['error'] == false){
                window.location.replace('/lawyer/'+response['lawyer']+'/dashboard');
            }
            else if(response['error'] == true){
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
        var sex = $('#sex').val().trim();
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
            sex : sex,
            first_name : first_name,
            last_name : last_name,
            email : email,
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

    $('#PA-client-accept').click(function(e){
        e.preventDefault();
        var client_id = $("#PA-request-client-id").val();
        var lawyer_id = $('#PA-request-lawyer-id').val();
        var relation_id = $('#PA-request-relation-id').val();
        var status = "Accepted";
        alert(relation_id);
        sendInfo = { lawyer_id : lawyer_id ,
                     relation_id  : relation_id,
                     status : status   }
        $('#'+client_id).fadeOut();
        $.post('/lawyer/'+client_id+'/pre-appoint-response', JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                
            }else if(response['error'] == true){
                console.log(response);
            }
        });
    })
    $('#PA-client-decline').click(function(e){
        e.preventDefault();
        var client_id = $("#PA-request-client-id").val();
        var lawyer_id = $('#PA-request-lawyer-id').val();
        var relation_id = $('#PA-request-relation-id').val();
        var status = "declined";
        alert(relation_id);
        sendInfo = { lawyer_id : lawyer_id ,
                     relation_id  : relation_id,
                     status : status   }
        $('#'+client_id).fadeOut();
        $.post('/lawyer/'+client_id+'/pre-appoint-response', JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                
            }else if(response['error'] == true){
                console.log(response);
            }
        });
    })

    $('#btnResetPassword').click(function(e){
        e.preventDefault();
        var token = $("#token").val();
        var password = $('#password').val();
        var confirm = $('#confirm-password').val();
        sendInfo = { password : password , confirm : confirm }
        $.post('/lawyer/reset-password/'+token, JSON.stringify(sendInfo), function(response){
            console.log(response)
        });
    })

    $("#btnForgotPass").click(function(e){
        var email = $('#email').val();
        sendInfo = { email : email }
        $.post('/lawyer/reset-password', JSON.stringify(sendInfo), function(response){
            console.log(response)
        });
        e.preventDefault()
    });
    // FOR THE ACCOUNT SETTINGS CLIENT

    $('#btnClientSavePicture').click(function(e){
        e.preventDefault();
        var id = $(".client_id").val();
        var file_data = $('#image').prop('files')[0];
        var form_data = new FormData();
        form_data.append('image', file_data);
        $.ajax({
            url: "/client/"+id+"/account-setting/profile-picture", // point to server-side controller method
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

    $('#btnClientSaveEmail').click(function(e){
        e.preventDefault();
        var id = $(".client_id").val();
        var current = $('#uc_current_email').val().trim();
        var new_email = $('#uc_new_email').val().trim();
        var password = $('#uc_e_current_password').val().trim();
        sendInfo = {
            current : current,
            new_email : new_email,
            password : password
        }
        $.post("/client/"+id+"/account-setting/change-email", JSON.stringify(sendInfo) ,function(response){
            console.log(response)
        })
    });

    $('#btnClientSavePassword').click(function(e){
        e.preventDefault();
        var id = $(".client_id").val();
        var current_pass = $('#uc_current_password').val();
        var new_pass = $('#uc_new_password').val();
        var confirm_pass = $('#uc_confirm_password').val();
        sendInfo = {
            current : current_pass,
            newpass : new_pass,
            confirm : confirm_pass
        }
        $.post("/client/"+id+"/account-setting/change-password", JSON.stringify(sendInfo) ,function(response){
            console.log(response['error'])
        })
    });
    $('#btnEditCase').click(function(e){
        e.preventDefault();
        var lawyer_id = $('#lawyer_id').val();
        var case_title=$("#case-title").val().trim();
        var case_id=$("#case_id").val();
        var case_status=$('#status').val();
        var case_description=$('#case-description').val().trim();
        alert(lawyer_id);
        sendInfo = {
            case_title : case_title,
            case_id : case_id,
            case_status : case_status,
            case_description : case_description
        }
        alert(sendInfo['case_title']);
        $.post("/lawyer/"+lawyer_id+"/edit-case", JSON.stringify(sendInfo) ,function(response){
            if(response['error'] == false){
                alert('Case Updated');
            }else if(response['error'] == true){
                alert('Case failed to Update');
            }
        })
    });

    $('#btnClientSaveInfo').click(function(e){
        e.preventDefault();
        var id = $(".client_id").val();
        var first_name = $('#uc_first_name').val().trim();
        var last_name = $('#uc_last_name').val().trim();
        var phone = $('#uc_phone').val().trim();
        var address= $('#uc_Address').val().trim();

        sendInfo = {
            first_name : first_name,
            last_name : last_name,
            phone : phone,
            address : address,
        }
        $.post("/client/"+id+"/account-setting/profile-information", JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                window.location.replace('/client/client-account-setting?succ='+succ+"&m="+m);
            }else if(response['error'] == true){
                window.location.replace('/client/client-account-setting?err='+err+"&m="+m);
            }
        } ,"json" );
    });

    $('#preAppointLawyer').click(function(e){

        e.preventDefault();
        var id = $("#seeLawyerId").val();
        var client = $('#clientCheck').val();
        

        sendInfo = { 
            id : id
        }
        if(client){
            $.post("/lawyer/"+client+"/pre-appoint", JSON.stringify(sendInfo) ,function(response){
                
                if(response['error'] == false){
                    alert('Appointment Requeset Sent');
                }
                else if(response['error'] == true){
                    console.log(response);
                }                
            }, "json")
        }
        else{
            window.location.replace('/client/signin');
        }
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

    $("#success-alert").fadeTo(2000, 500).slideUp(500, function(){
        $("#success-alert").slideUp(500);
    });
    $("#danger-alert").fadeTo(2000, 500).slideUp(500, function(){
        $("#danger-alert").slideUp(500);
    });
});