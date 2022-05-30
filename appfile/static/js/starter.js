var clicks = 0;
var loc_clicks = localStorage.getItem("loc_clicks", 0);

function p_counter() {
    const act_counter = document.activeElement.id;

    if(act_counter == 'upbtn') {
        clicks += 1;
        document.getElementById("clicks").innerHTML = clicks;
        loc_clicks = localStorage.setItem("loc_clicks", clicks);
    }
    
    else if(act_counter == 'downbtn') {
        clicks -= 1;
        if(clicks <= 0){
            clicks = 0;
        }
        document.getElementById("clicks").innerHTML = clicks;
        loc_clicks = localStorage.setItem("loc_clicks", clicks);
    }
};
 

function startFunc(){
    var selected = new Array();
    var elem = document.getElementById("cktab");
    var chks = elem.getElementsByTagName("INPUT"); 

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
                location.replace('video');
            }
            else if(element.includes('quest')){
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

};

// function getActiveElem() {
//     var quest_ck = (parseInt(localStorage.getItem('quest_ck'))+1);
//     if(quest_ck == null) {
//         localStorage.setItem('quest_ck', 0);
//     }
//     localStorage.setItem("quest_ck", (quest_ck).toString());

//     const act_elem = document.activeElement.id;
//     var questid = document.getElementById("questbtn").id;
//     //alert(act_elem + " , " + questid + " , " + quest_ck + " , " + loc_clicks);

//     var quest1 = document.querySelector('input[name="q1"]:checked').value;
//     var quest2 = document.querySelector('input[name="q2"]:checked').value;
//     var quest3 = document.querySelector('input[name="q3"]:checked').value;
//     if(!quest1 && !quest2 && !quest3){
//         alert("No score was selected. Try again.");
//         return false;
//     }
//     else{
//         alert(quest1 + ' was selected for q1, ' + quest2 + ' was selected for q2, ' + quest3 + ' was selected for q3');
//     }

//     if(quest_ck < loc_clicks && act_elem == questid) {
//         location.reload('questionnaire');
//     }
//     else {
//         alert(act_elem + " , " + questid + " , " + quest_ck + " , " + loc_clicks);
//         localStorage.setItem('quest_ck', 0);
//         location.replace('dashboard');
//         return false;
//     }
//     //return act_elem;
// };
