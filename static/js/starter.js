var clicks = 0;
var loc_clicks = localStorage.getItem("loc_clicks", 0);
function upcounter() {
    clicks += 1;
    document.getElementById("clicks").innerHTML = clicks;
    loc_clicks = localStorage.setItem("loc_clicks", clicks);
};

function downcounter() {
    clicks -= 1;
    if(clicks <= 0){
        clicks = 0;
    }
    document.getElementById("clicks").innerHTML = clicks;
    loc_clicks = localStorage.setItem("loc_clicks", clicks);
};

function startFunc(){
    var selected = new Array();
    var elem = document.getElementById("cktab");
    var chks = elem.getElementsByTagName("INPUT");
    var ck = 0; 

    for(var i = 0; i < chks.length; i++){
        if(chks[i].checked){
            selected.push(chks[i].value);
        }
    }
    if(selected.length > 0 && clicks > 0){
        selected_items = selected.join(",");
        const match = selected.find(element => {
            if(element.includes('vid')){
                alert(element + " was found in : " + selected_items + " with " + clicks + " participants");
                location.replace('dashboard');
            }
            if(element.includes('quest')){
                alert(element + " was found in : " + selected_items + " with " + clicks + " participants");
                location.replace('questionnaire');
            }
        })
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

function getActiveElem() {
    var quest_ck = (parseInt(localStorage.getItem('quest_ck'))+1);
    localStorage.setItem("quest_ck", quest_ck.toString());
    
    const act_elem = document.activeElement.id;
    var questid = document.getElementById("questbtn").id;
    //console.log(act_elem + " , " + questid + " , " + quest_ck);
    alert(act_elem + " , " + questid + " , " + quest_ck + " , " + loc_clicks);
    if(quest_ck < loc_clicks && act_elem == questid) {
        location.replace('questionnaire');
    }
    else {
        localStorage.setItem('quest_ck', 0);
        location.replace('dashboard');
    }
    //return act_elem;
}