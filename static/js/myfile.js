document.getElementsById("startbtn").addEventListener('click', startFunc);

function startFunc(){

    var selected = new Array();
    var elem = document.getElementById("cktab");
    var chks = elem.getElementsByTagName("INPUT");

    for(var i = 0; i < chks.length; i++){
        if(chks[i].checked){
            selected.push(chks[i].value);
        }
    }

    if(selected.length > 0){
        alert("Selected :" + selected.join(","));
    }  
};