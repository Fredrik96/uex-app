function startFunc(){
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
                alert(element + " was found in : " + selected_items + " with " + clicks + " participants");
                location.replace('dashboard');
            }
            else if(element.includes('quest')){
                location.replace('questionnaire');
            }
        })
        //alert("Selected :" + selected.join(","));
    }
    
    
    //setting the name of the experiment and updating the table
    //var exp_name = document.getElementById("expname").value;
    //alert(exp_name);
    
};

function addRow() 
{
    alert("add row runs!");
    var exp_name = document.getElementById("expname");
    var newRow = document.getElementById("DataTab").insertRow( -1 );
    var newCell = newRow.insertCell( -1 );
    newCell.innerHTML = "Time";

    newCell = newRow.insertCell( -1 );
    newCell.innerHTML = "Name";

    newCell = newRow.insertCell( -1 );
    newCell.innerHTML = "Tools";

    newCell = newRow.insertCell( -1 );
    newCell.innerHTML = "Data";

}