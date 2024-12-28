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