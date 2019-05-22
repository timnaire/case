$(document).ready(function(){
    $("#btnAddAdmin").click(function () {
        var option = "add"
        var username = $("#username").val();
        var password = $("#password").val();
        var confirm = $("#confirm").val();
        sendInfo = {
            option: option,
            username : username,
            password : password,
            confirm : confirm
        }
        $.post("/admin",JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                alert(response['message']);
            }
        });
    });

    $("#btnLoginAdmin").click(function (e) {
        e.preventDefault();
        var option = "login"
        var username = $("#loginusername").val();
        var password = $("#loginpassword").val();
        sendInfo = {
            option: option,
            username : username,
            password : password
        }
        $.post("/admin",JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                window.location.replace("/admin-dashboard")
            } else {
                alert(response['error']);
            }
        });
    });

    $("#btnAddPractice").click(function(e){
        e.preventDefault();
        var practice = $("#newPractice").val();
        sendInfo = {
            practice: practice
        }
        $.post("/admin-practices",JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                alert(response['message']);
                location.reload();
            } else {
                alert(response['error']);
            }
        });
    });

    $("#btnAddSubPractice").click(function(e){
        e.preventDefault();
        var practice = $("#law_practice").val();
        var subpractice = $("#newSubPractice").val();
        sendInfo = {
            practice: practice,
            subpractice:subpractice
        }
        console.log(sendInfo);
        $.post("/admin-subpractices",JSON.stringify(sendInfo), function(response){
            if(response['error'] == false){
                alert(response['message']);
                location.reload();
            } else {
                alert(response['error']);
            }
        });
    });
});