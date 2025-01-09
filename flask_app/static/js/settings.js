function switchMode(currentMode){
    let newMode;
    if (currentMode == "automatic") {
        newMode = "manual"
    } else {
        newMode = "automatic"
    }
    setUIMode(newMode,true)
    return newMode
}

function setUIMode(mode,updateDB){
    let otherContainer;
    let otherSwitch;
    console.log("Mode in set ui mode ",mode)
    if (mode == "automatic") {
        otherContainer = document.querySelector('#manual-container');
        otherSwitch =  document.querySelector('#switchmanual');
        otherCover = document.querySelector('#manualCover');
    } else {
        otherContainer = document.querySelector('#automatic-container');
        otherSwitch =  document.querySelector('#switchautomatic');
        otherCover = document.querySelector('#automaticCover');
    }
    const currentSwitch =  document.querySelector('#switch'+mode);
    const selectedMode = document.querySelector('#'+mode+'-container');
    const selectedCover = document.querySelector('#'+mode+'Cover');
    selectedMode.classList.add('highlighted');
    otherContainer.classList.remove('highlighted')
    currentSwitch.style.display = "block";
    otherSwitch.style.display = "none";
    otherCover.style.display="flex";
    selectedCover.style.display = "none";
    if (updateDB==true){
      setMode(mode)
    }

}

async function setMode(mode) {
  try {
    const response = await fetch('/change_settings_mode', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json', 
      },
      body: JSON.stringify({mode})
    });
    if (response.ok) {
        console.log("set mode in db")
    } else {
        console.log("Fail add setting")
    }
  } catch (error) {
    console.log("Error in add setting ,", error)
  }
}


function loadSettingsTable(settings) {
    console.log("Settings in function ->", settings);
    settings.manual_settings.forEach((element, index) => {
      addSettingsTableRow(element,index)
    });
    settings.automatic_settings.feedTimes.forEach((element) => {
      addAutomaticSettingsTableRow(element)
    });
    const startTimeInput = document.querySelector('#startTime');
    const endTimeInput = document.querySelector('#endTime');
    const  amountInput = document.querySelector('#amountInputManual');
    const  freqInput = document.querySelector('#frequency');
    startTimeInput.value = settings.automatic_settings.startTime
    endTimeInput.value = settings.automatic_settings.endTime
    amountInput.value =  parseInt(settings.automatic_settings.amount,10);
    freqInput.value = parseInt(settings.automatic_settings.dispenseFreqVal, 10);
}


function addSettingsTableRow(element,index){
  const settingsBody = document.querySelector('#settingsTableBodyManual');
  const row = `
  <tr>
    <td>${element.time}</td>
    <td>${element.amount}</td>
    <td><button onclick="deleteRow(this, ${index})">Delete</button></td>
  </tr>
  `;
  settingsBody.insertAdjacentHTML('beforeend', row);
}

function addAutomaticSettingsTableRow(element){
  const settingsBody = document.querySelector('#settingsTableBodyAutomatic');
  const row = `
  <tr>
    <td>${element.time}</td>
    <td>${element.amount}</td>
  </tr>
  `;
  settingsBody.insertAdjacentHTML('beforeend', row);
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
          const settingsBody = document.querySelector('#settingsTableBodyManual');
          const lastRow = settingsBody.lastElementChild;
          const newIndex = settingsBody.rows ? settingsBody.rows.length : settingsBody.children.length;
          console.log("Last row:", lastRow);
          let element = {};
          element['time'] = time;
          element['amount'] = amount;
          addSettingsTableRow(element, newIndex);
            timeInputField.value= '00:00';
            amountInputField.value= 0.5;
            console.log("Successful add")
        } else {
            console.log("Fail add setting")
        }
      } catch (error) {
        console.log("Error in add setting ,", error)
      }
}

async function addAutomaticSetting(){
  const startInput = document.querySelector('#startTime');
  const endInput = document.querySelector('#endTime');
  const amountInputField = document.querySelector('#amountInputManual');
  const dispenseFreq = document.querySelector('#frequency');
  const startTimeComp = new Date(`1970-01-01T${startInput.value}:00`);
  const endTimeComp = new Date(`1970-01-01T${endInput.value}:00`);
  if (!startInput.value || !endInput.value) {
    alert("Start Time and End Time are required!");
    return;
}
  if (startTimeComp >= endTimeComp) {
      return;
  }
  if (!amountInputField.value || amountInputField.value < 0.5 || amountInputField.value > 10) {
      return;
  }
  if (!dispenseFreq.value || isNaN(dispenseFreq.value) || dispenseFreq.value <= 0) {
      return;
  }
  const amount = amountInputField.value
  const startTime = startInput.value
  const endTime = endInput.value
  const dispenseFreqVal = dispenseFreq.value
  const feedTimes = generateTabledData(amount,startTime,endTime,dispenseFreqVal)
  try {
      const response = await fetch('/set_automatic_setting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify({amount,startTime,endTime,dispenseFreqVal,feedTimes})
      });
      if (response.ok) {
        const settingsBody = document.querySelector('#settingsTableBodyAutomatic');
        settingsBody.innerHTML = ""
        feedTimes.forEach(row => {
          addAutomaticSettingsTableRow(row)
        })
        
          console.log("Successful add")
      } else {
          console.log("Fail add setting")
      }
    } catch (error) {
      console.log("Error in add setting ,", error)
    }
}

function generateTabledData(amount,start,end,freq){
  const startTime = new Date(`1970-01-01T${start}:00`);
  const endTime = new Date(`1970-01-01T${end}:00`);
  const durationMinutes = (endTime - startTime) / (1000 * 60);
  const amountPerInterval = amount / freq;
  const feedTimes = [];
  const intervalMinutes = durationMinutes / (freq - 1); 
  for (let i = 0; i < freq; i++) {
    const feedTime = new Date(startTime.getTime() + i* intervalMinutes * 60 * 1000);
    feedTimes.push({
      time: feedTime.toTimeString().substring(0, 5),
      amount: parseFloat(amountPerInterval.toFixed(2)),
    });
  }
  console.log("Feed times:", feedTimes);
  return feedTimes;
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
          console.log("row")
          row.parentNode.removeChild(row);
        } else {
            console.log("Fail delete")
        }
      } catch (error) {
        console.log("Error in delete ,", error)
      }
}