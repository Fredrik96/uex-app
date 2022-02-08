document.getElementsById("startbtn").addEventListener('click', startFunc);

function startFunc(bool){

    var selected = new Array();
    var elem = document.getElementById("cktab");
    var chks = elem.getElementsByTagName("INPUT");
    var clicks =  document.getElementById("clicks").innerHTML; 

    for(var i = 0; i < chks.length; i++){
        if(chks[i].checked){
            selected.push(chks[i].value);
        }
    }

    if(selected.length > 0){
        selected_items = selected.join(",");
        const match = selected.find(element => {
            if(element.includes('vid')){
                alert(element + " was found in :" + selected_items + " with " + clicks + " participants");
            }
        })
        //alert("Selected :" + selected.join(","));
    }
    
    if (bool==true)
    {
        var dimdash = document.getElementById('dashdim');
        dimdash.classList.add("dashdim"); 
    }
    
    //setting the name of the experiment
    // var table = document.getElementById("DataTab");
    // var row = table.insertRow(0);
    // var cell = row.insertCell(0);
    // cell.innerHTML = document.getElementById('cellOne').value;
};