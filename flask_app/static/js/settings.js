function switchMode(currentMode){
    let newMode;
    if (currentMode == "automatic") {
        newMode = "manual"
    } else {
        newMode = "automatic"
    }
    setUIMode(newMode)
    return newMode
}

function setUIMode(mode){
    let otherContainer;
    let otherSwitch;
    console.log("Mode in set ui mode ",mode)
    if (mode == "automatic") {
        otherContainer = document.querySelector('#manual-container');
        otherSwitch =  document.querySelector('#switchmanual');
    } else {
        otherContainer = document.querySelector('#automatic-container');
        otherSwitch =  document.querySelector('#switchautomatic');
    }
    const currentSwitch =  document.querySelector('#switch'+mode);
    const selectedMode = document.querySelector('#'+mode+'-container');
    selectedMode.classList.add('highlighted');
    otherContainer.classList.remove('highlighted')
    currentSwitch.style.display = "block";
    otherSwitch.style.display = "none";
}

function loadSettingsTable(settings) {
    console.log("Settings in function ->", settings);
    const settingsBody = document.querySelector('#settingsTableBody');
    settings.manual_settings.forEach((element, index) => {
        const row = `
        <tr>
          <td>${element.hour}</td>
          <td>${element.amount}</td>
          <td><button onclick="deleteRow(this, ${index})">Delete</button></td>
        </tr>
        `;
        settingsBody.insertAdjacentHTML('beforeend', row);
    });
}

async function addManualSetting(){
    const timeInputField = document.querySelector('#timeInput');
    const amountInputField = document.querySelector('#amountInput');
    if (timeInput.value <0 && timeInput.value>24){

        return
    }
    if (amountInputField.value <0.5 && amountInputField.value>10){
        
        return
    }
    amount = amountInputField.value
    time = timeInput.value
    try {
        const response = await fetch('/add_manual_setting', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json', 
          },
          body: JSON.stringify({amount,time})
        });
        if (response.ok) {
            timeInputField.value= 0;
            amountInputField.value= 0.5;
            console.log("Successful add")
        } else {
            console.log("Fail add setting")
        }
      } catch (error) {
        console.log("Error in add setting ,", error)
      }
}

async function deleteRow(button,index) {
    try {
        const response = await fetch('/delete_manual_setting', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json', 
          },
          body: JSON.stringify({ index})
        });
        if (response.ok) {
          console.log("Successful delete")
          const row = button.parentNode.parentNode;
          row.parentNode.removeChild(row);
        } else {
            console.log("Fail delete")
        }
      } catch (error) {
        console.log("Error in delete ,", error)
      }
}