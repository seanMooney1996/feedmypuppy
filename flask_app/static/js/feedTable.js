let incrementCount = 0;

function filterTable(increment, data) {
    incrementCount += increment
    const dayStarting = getIncrementedDay(incrementCount);
    data = data.filter(entry => {
        const entryDate = new Date(entry.timestamp); 
        return isSameDay(entryDate, dayStarting);
    });
    setStats(data)
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
        let statusMessage = ""
        entry.dispenser_status ? statusMessage = "Yes" : statusMessage = "No"
        row.innerHTML = `
            <td class="longtd">${formattedDate}</td>
            <td>${entry.dispensed_grams}</td>
            <td>${entry.eaten_grams}</td>
            <td>${entry.total_not_dispensed}</td>
            <td>${statusMessage}</td>
        `;
        dispenseTable.appendChild(row);
    });
}

function setStats(data) {
    let totalEaten = 0
    let totalDispensed= 0
    let totalNotDispensed = 0
    let peekEating = 0
    let latestEating = 0
    let earliestEating = 24
    let hourMap = {}
    for (let i=0;i<=23; i++){
        hourMap[i] = 0;
    }
    data.forEach(entry => {
        totalEaten += entry.eaten_grams
        totalDispensed += entry.dispensed_grams
        totalNotDispensed += entry.total_not_dispensed
        timestamp = entry.timestamp
        const date = new Date(timestamp); 
        hour = date.getUTCHours();
        hourMap[hour] += entry.eaten_grams
        if (entry.eaten_grams > 1){
            latestEating = Math.max(hour,latestEating)
            earliestEating = Math.min(hour,earliestEating) 
        }
    })
    let highestEatingHour = -1
    let maxEatenGrams = 0
    for (const [hour, grams] of Object.entries(hourMap)) {
        if (grams > maxEatenGrams) {
            maxEatenGrams = grams
            highestEatingHour = hour
        }
    }
    const totalEatenStat = document.querySelector('#totalEatenStat');
    totalEatenStat.innerHTML = Math.round(totalEaten)+ ' g'
    const totalDispensedStat = document.querySelector('#totalDispensedStat');
    totalDispensedStat.innerHTML = Math.round(totalDispensed) + ' g'
    const totalNotDispensedStat = document.querySelector('#totalNotDispensedStat');
    totalNotDispensedStat.innerHTML = totalNotDispensed
    const peekEatingHourStat = document.querySelector('#peekEatingHourStat');
    const latestEatingHourStat = document.querySelector('#latestEatingHourStat');
    const earliestEatingStat = document.querySelector('#earliestEatingStat');
    if (totalEaten != 0){
        peekEatingHourStat.innerHTML = latestEating + ':00'
        latestEatingHourStat.innerHTML = latestEating + ':00'
        earliestEatingStat.innerHTML = earliestEating + ':00'
    } else {
        peekEatingHourStat.innerHTML = '-'
        latestEatingHourStat.innerHTML = '-'
        earliestEatingStat.innerHTML = '-'
    }
    
    console.log(" Dispenser Statistics")
    console.log(`Total eaten: ${totalEaten} grams`)
    console.log(`Total dispensed: ${totalDispensed} grams`)
    console.log(`Total not dispensed: ${totalNotDispensed} grams`)
    console.log(`Earliest eating hour: ${earliestEating}:00`)
    console.log(`Latest eating hour: ${latestEating}:00`)
    console.log(`Highest eating hour: ${highestEatingHour}:00 with ${maxEatenGrams} grams eaten`)
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
