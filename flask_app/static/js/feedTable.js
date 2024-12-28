let incrementCount = 0;

function filterTable(increment, data) {
    incrementCount += increment
    const dayStarting = getIncrementedDay(incrementCount);
    data = data.filter(entry => {
        const entryDate = new Date(entry.timestamp); 
        return isSameDay(entryDate, dayStarting);
    });
    const whenstring = document.querySelector('#whenstring')
    const nextButton = document.querySelector('#nextButton')
    if (incrementCount === 0) {
        whenstring.innerHTML = "Today"
        nextButton.style.display = "none"
    } else {
        whenstring.innerHTML = `${Math.abs(incrementCount)} Days Ago `
        nextButton.style.display = "block"
    } 
    const dispenseTable = document.querySelector('#dispenseTable tbody');
    const dayString = document.querySelector('#dayString');
    dayString.innerHTML = dayStarting.toISOString()
    const formattedDate = new Date(dayStarting).toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
    dayString.innerHTML = formattedDate
    dispenseTable.innerHTML = '';
    const dataMessage = document.querySelector('#dataMessage');
    data.length == 0 ? dataMessage.style.display = "block" : dataMessage.style.display = "none"
    data.forEach(entry => {
        console.log(data);
        const row = document.createElement('tr');
        const formattedDate = new Date(entry.timestamp).toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });

        row.innerHTML = `
            <td class="longtd">${formattedDate}</td>
            <td>${entry.dispensed_amount_kg}</td>
            <td>${entry.eaten_amount_kg}</td>
            <td>${entry.dispenser_status}</td>
        `;
        dispenseTable.appendChild(row);
    });
}


function getIncrementedDay(increment) {
    const currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0); 
    if (increment !== 0) {
        currentDate.setDate(currentDate.getDate() + (increment * 1)); 
    }
    return currentDate;
}

function isSameDay(date1, date2) {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
}
