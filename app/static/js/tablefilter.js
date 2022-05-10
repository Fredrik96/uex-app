function SortByName() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("filtersearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("DataTab");
    tr = table.getElementsByTagName("tr");
  
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
  }

function SortByTools(newId){
    var table, tr, td, i, txtValue;
    var id_vid = document.getElementById("drop-vid");
    var id_analyt = document.getElementById("drop-analyt");
    var id_time = document.getElementById("drop-time");
    
    var filter1 = id_vid.value.toUpperCase();
    var filter2 = id_analyt.value.toUpperCase();
    var filter3 = id_time.value.toUpperCase();

    table = document.getElementById("DataTab");
    tr = table.getElementsByTagName("tr");

    $(document).one('click', '.dropdown-menu button', function() {
        newId = $(this).text().toUpperCase();
        for (i = 0; i < tr.length; i++) 
        {
            td = tr[i].getElementsByTagName("td")[1];
            //alert(newId +","+ filter4 +","+ td);
            if (td && newId == filter1) 
            {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter1) > -1) {
                    tr[i].style.display = "";
                }
                else 
                {
                    tr[i].style.display = "none";
                }
            }
            if (td && newId == filter2) 
            {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter2) > -1) {
                    tr[i].style.display = "";
                }
                else 
                {
                    tr[i].style.display = "none";
                }
            }
            if (td && newId == filter3) 
            {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter3) > -1) {
                    tr[i].style.display = "";
                }
                else 
                {
                    tr[i].style.display = "none";
                }
            }
        }
        
    });
}

function ClearTools(){
    var table, filterC, id_clear, tr, td, i;
    id_clear = document.getElementById("drop-clear");
    filterC = id_clear.value.toUpperCase();
    table = document.getElementById("DataTab");
    tr = table.getElementsByTagName("tr");
    
    for (i = 0; i < tr.length; i++) 
    {
        td = tr[i].getElementsByTagName("td")[1];
        if (td) 
        {
            tr[i].style.display = "";
        }
    }
}

function SortByTitle() {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("DataTab");
    switching = true;
    dir = "asc"; 
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("td")[0];
        y = rows[i + 1].getElementsByTagName("td")[0];
        if (dir == "asc") {
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            shouldSwitch= true;
            break;
            }
        } else if (dir == "desc") {
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            shouldSwitch = true;
            break;
            }
        }
        }
        if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;      
        } else {
        if (switchcount == 0 && dir == "asc") {
            dir = "desc";
            switching = true;
        }
        }
    }
}

var toggle = true;

function ConvertDate(y) {
    var first = y.split(" ")
    var date = first[0].split('-')
    var time = first[1].split(':')
    return +(date[2]+date[1]+date[0]+time[0]+time[1]+time[2]);
  }

function SortByDateAsc() {
    var tbody = document.querySelector("#DataTab tbody");
    var rows = [].slice.call(tbody.querySelectorAll("tr"));

    rows.sort(function(a,b) {
        var asc = ConvertDate(b.cells[0].innerHTML) - ConvertDate(a.cells[0].innerHTML);
        return asc;
    });
    

    rows.forEach(function(v) {
        tbody.appendChild(v);
    });
    toggle = false;
}

function SortByDateDesc() {
    var tbody = document.querySelector("#DataTab tbody");
    var rows = [].slice.call(tbody.querySelectorAll("tr"));
    
    rows.sort(function(a,b) {
        var desc = ConvertDate(a.cells[0].innerHTML) - ConvertDate(b.cells[0].innerHTML);
        return desc;
    });
    
    rows.forEach(function(v) {
        tbody.appendChild(v);
    });
    toggle = true;
}

function toggleSort() {
    toggle ? SortByDateAsc() : SortByDateDesc();
}


var toggleR = true;

function ShowRecent() {
    var tbody = document.querySelector("#DataTab tbody");
    var rows = [].slice.call(tbody.querySelectorAll("tr"));
    
    rows.sort(function(a,b) {
        var asc = ConvertDate(b.cells[0].innerHTML) - ConvertDate(a.cells[0].innerHTML);
        return asc;
    });

    rows.forEach(function(v) {
        tbody.appendChild(v);
    });

    for (i = 1; i < rows.length; i++) 
    {
        if (i < 3) 
        {
            rows[i].style.display = "";
        }
        else {
            rows[i].style.display = "none";
        }
    }
    toggleR = true;
}

function DisableRecent() {
    table = document.getElementById("DataTab");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) 
    {
        td = tr[i].getElementsByTagName("th")[0];
        if (td) 
        {
            tr[i].style.display = "";
        }
    }
    toggleR = false;
}

function toggleRecent() {
    toggleR ? DisableRecent() : ShowRecent();
}
